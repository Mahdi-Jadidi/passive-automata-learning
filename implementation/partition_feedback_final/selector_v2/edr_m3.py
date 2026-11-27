"""Opt-in P3 M3 producer with a frozen v1 fallback entry point."""
import argparse
import json
import sys

from .edr_bb import RegionState, RollbackDSU, SearchBudget, SearchCaps, SearchCapExceeded
from .edr_search import (REASONS, canonical, close, compatible, digest, load, open_node,
                         pair_at, raw_conflict, solve as solve_v1, validate_scope, write_atomic)
from .edr_cross import ALL_PAIRS, CROSS_SUPPORT, AllPairsPrefix, CrossPairs, CrossPrefix, discover

FORMAT_V2 = "p3-region-frontier/v2"


class RetainedBudget(SearchBudget):
    def restore_retained_payload(self, encoded_bytes, entries):
        """Restore checkpoint payload without consuming new-entry allowance."""
        self.memory_bytes = self.peak_memory_bytes = encoded_bytes
        self.frontier_entries = entries
        self._check_time()
        if self.caps.memory_bytes is not None and encoded_bytes > self.caps.memory_bytes:
            raise SearchCapExceeded("memory_bytes")


def split_fields(t, rid, witness):
    fields = dict(kind="SPLIT", rule=ALL_PAIRS, alternative_count=t, cursor=0,
                  children=[], cursor_log=[], residual_id=rid,
                  suffix=dict(rule="FIRST_TRUE_SUFFIX_V1", start=0, stop=t))
    if witness is not None:
        fields.update(rule=CROSS_SUPPORT, witness=witness)
    return fields


def child_payload(child, record):
    # OPEN is the fixed admission representation, regardless of later closure.
    size = len(canonical(child)) + len(canonical(record))
    return size + len(canonical(child["id"]))


def retained_payload(table, budget):
    size = entries = 0
    for q in table.values():
        budget.charge_work()
        if q["kind"] != "SPLIT":
            continue
        residual = table[q["residual_id"]]
        size += len(canonical(residual)) + len(canonical(split_fields(
            q["alternative_count"], q["residual_id"], q.get("witness"))))
        entries += 1
        for record in q["cursor_log"]:
            budget.charge_work()
            child = table[record["child_id"]]
            size += child_payload(open_node(child["id"], q["id"], child["edge"]), record)
            entries += 1
    return size, entries


def solve(raw, scope, mode="one", *, caps=None, checkpoint=None, split_rule=ALL_PAIRS):
    """Return (certificate, telemetry). A checkpoint is a trusted local PARTIAL
    certificate. It is not an authority: only independent replay certifies
    the final result. Resume walks emitted DFS prefix without reevaluating
    closed leaves, reconstructs their winners, and continues at the cursor.
    Work, time and new entry limits are per invocation. V2's payload limit
    includes retained checkpoint admissions. The root placeholder is free.
    """
    if mode not in ("one","all"):
        raise ValueError("mode")
    if split_rule not in (ALL_PAIRS, CROSS_SUPPORT):
        raise ValueError("split rule")
    if split_rule == ALL_PAIRS:
        return solve_v1(raw, scope, mode, caps=caps, checkpoint=checkpoint)
    budget = RetainedBudget(caps)
    sample, root = validate_scope(raw,scope)
    sd = digest(scope)
    if checkpoint is None:
        table = {"root":open_node("root",None,dict(kind="ROOT"))}
        best = None
    else:
        if (type(checkpoint) is not dict or set(checkpoint) !=
            {"format","scope_digest","mode","declared_status","root_owner","incumbent","optima","nodes"}
            or checkpoint["format"] != FORMAT_V2 or checkpoint["scope_digest"] != sd
            or checkpoint["mode"] != mode or checkpoint["declared_status"] != "PARTIAL"
            or canonical(checkpoint["root_owner"]) != canonical(scope["root_owner"])
            or checkpoint["optima"] != []):
            raise ValueError("checkpoint header mismatch")
        nodes = checkpoint["nodes"]
        if type(nodes) is not list or not nodes:
            raise ValueError("checkpoint table")
        table = {q["id"]:q for q in nodes}
        if list(table) != sorted(table) or len(table)!=len(nodes) or "root" not in table:
            raise ValueError("checkpoint node order")
        best = checkpoint["incumbent"]
        if best is not None:
            p = RegionState(tuple(best["owner"]))
            if not root.contains(p.owner) or p.lower_bound != best["cost"]:
                raise ValueError("checkpoint incumbent")
    winners = set()
    dsu = RollbackDSU(root.alphabet_size,root.owner)
    # Frame: id, rollback mark, inherited exclusive lex prefix threshold,
    # empty flag, next child index (-1 means first visit).
    # V2 also freezes the typed ancestor prefixes and the current pair family.
    stack = [["root",dsu.mark(),None,False,-1,(),None]]
    visited = set()
    counters = dict(expanded=0,closed=0,exact_checks=0,generated=0,
                    resumed_nodes=0,peak_depth=1)
    counters.update(witness_work=0, witness_probes=0, witness_local_caps=0, cross_splits=0)
    stop = None

    def candidate(owner, cost):
        nonlocal best, winners
        if best is None or cost < best["cost"]:
            best = dict(owner=list(owner),cost=cost)
            winners = {owner}
        elif cost == best["cost"] and mode=="all":
            winners.add(owner)

    def finish():
        frame = stack.pop()
        dsu.rollback(frame[1])

    def leaf(node, why):
        close(node,why)
        counters["closed"] += 1

    try:
        if checkpoint is not None:
            budget.restore_retained_payload(*retained_payload(table, budget))
        conflict = raw_conflict(sample,budget)
        if best is not None:
            if not compatible(tuple(best["owner"]),sample.positive,sample.negative,budget):
                raise ValueError("checkpoint incumbent incompatible")
        while stack:
            budget.charge_work()
            ident, mark, threshold, empty, next_j, prefixes, family = stack[-1]
            q = table[ident]
            if next_j == -1:
                if ident in visited:
                    raise ValueError("duplicate DFS node")
                visited.add(ident)
                if q["kind"] == "LEAF":
                    counters["resumed_nodes"] += 1
                    if q["closure"]["reason"] == "FEASIBLE_MIN":
                        budget.charge_work(root.alphabet_size)
                        owner = dsu.snapshot()
                        candidate(owner,root.alphabet_size-dsu.class_count)
                    finish()
                    continue
                if q["kind"] == "OPEN":
                    if empty:
                        leaf(q,dict(reason="EMPTY"))
                        finish()
                        continue
                    if conflict is not None:
                        leaf(q,conflict)
                        finish()
                        continue
                    budget.charge_work(root.alphabet_size)
                    region = RegionState(dsu.snapshot())
                    lb = region.lower_bound
                    if best is not None and (lb > best["cost"] or
                                             (mode=="one" and lb==best["cost"])):
                        leaf(q,dict(reason="COST"))
                        finish()
                        continue
                    counters["exact_checks"] += 1
                    if compatible(region.owner,sample.positive,sample.negative,budget):
                        candidate(region.owner,lb)
                        leaf(q,dict(reason="FEASIBLE_MIN"))
                        finish()
                        continue
                    reps = sorted(set(region.owner))
                    k = len(reps)
                    # Every pair forbidden iff even the lexicographic maximum
                    # is below the inherited prefix threshold.
                    if k < 2 or (threshold is not None and (reps[-2],reps[-1]) < threshold):
                        leaf(q,dict(reason="EXACT_NO"))
                        finish()
                        continue
                    witness = discover(region.owner, sample, budget, counters)
                    if witness is not None:
                        family = CrossPairs.build(tuple(witness["support_s"]),
                                                  tuple(witness["support_t"]), budget)
                    t = family.count if family is not None else k*(k-1)//2
                    rid = ident+"/r"
                    residual = open_node(rid,ident,dict(kind="RESIDUAL"))
                    residual_reason = "CONFLICT_RESIDUAL" if family is not None else "EXACT_NO"
                    close(residual,dict(reason=residual_reason))
                    fields = split_fields(t, rid, witness)
                    # Admission before changing parent: interruption cannot lose
                    # the residual, or commit a split without a suffix.
                    payload = len(canonical(residual))
                    payload += len(canonical(fields))
                    budget.admit_frontier_entry(payload)
                    if rid in table:
                        raise ValueError("duplicate residual")
                    table[rid] = residual
                    visited.add(rid)
                    del q["reason"]
                    q.update(fields)
                    if family is not None:
                        counters["cross_splits"] += 1
                    counters["generated"] += 1
                    counters["closed"] += 1
                    counters["expanded"] += 1
                elif q["kind"] == "SPLIT":
                    rid = ident+"/r"
                    if q["rule"] == CROSS_SUPPORT:
                        witness = q["witness"]
                        family = CrossPairs.build(tuple(witness["support_s"]),
                                                  tuple(witness["support_t"]), budget)
                    elif q["rule"] != ALL_PAIRS or "witness" in q:
                        raise ValueError("invalid local checkpoint rule")
                    residual_reason = "CONFLICT_RESIDUAL" if family is not None else "EXACT_NO"
                    if empty or q["residual_id"]!=rid or table[rid] != dict(
                            id=rid,parent_id=ident,edge=dict(kind="RESIDUAL"),
                            kind="LEAF",closure=dict(reason=residual_reason)):
                        raise ValueError("invalid local checkpoint split")
                    visited.add(rid)
                    counters["resumed_nodes"] += 1
                else:
                    raise ValueError("checkpoint node kind")
                stack[-1][4] = 0
                stack[-1][6] = family
                continue
            budget.charge_work(root.alphabet_size)
            reps = dsu.representatives()
            t = family.count if family is not None else len(reps)*(len(reps)-1)//2
            cursor = q["cursor"]
            if (t!=q["alternative_count"]
                or type(cursor) is not int or not 0<=cursor<=t
                or len(q["children"])!=cursor or len(q["cursor_log"])!=cursor
                or q["suffix"]!=dict(rule="FIRST_TRUE_SUFFIX_V1",start=cursor,stop=t)):
                raise ValueError("invalid checkpoint cursor")
            if next_j == t:
                finish()
                continue
            j = next_j
            pair = family.pair_at(j,budget) if family is not None else pair_at(reps,j)
            child_id = ident+"/c"+str(j)
            edge = dict(kind="CHILD",index=j,pair=list(pair))
            record = {"from":j,"to":j+1,"child_id":child_id,"pair":list(pair)}
            if j < cursor:
                child = table[child_id]
                if (q["children"][j]!=child_id or q["cursor_log"][j]!=record
                    or child["parent_id"]!=ident or child["edge"]!=edge):
                    raise ValueError("checkpoint child mismatch")
            elif j != cursor:
                raise ValueError("DFS skipped cursor")
            child_mark = dsu.mark()
            child_threshold = threshold
            child_prefixes = prefixes
            dsu.union(*pair)
            invalid = any(prefix.violated(dsu, pair, budget) for prefix in prefixes)
            if family is not None:
                if j:
                    child_prefixes += (CrossPrefix(family, pair),)
            elif j:
                child_prefixes += (AllPairsPrefix(pair),)
                child_threshold = pair if threshold is None else max(pair, threshold)
            if j == cursor:
                child = open_node(child_id,ident,edge)
                budget.admit_frontier_entry(child_payload(child,record))
                if child_id in table:
                    raise ValueError("duplicate child")
                table[child_id] = child
                q["children"].append(child_id)
                q["cursor_log"].append(record)
                q["cursor"] = j+1
                q["suffix"]["start"] = j+1
                counters["generated"] += 1
            stack[-1][4] += 1
            stack.append([child_id,child_mark,child_threshold,invalid,-1,child_prefixes,None])
            counters["peak_depth"] = max(counters["peak_depth"],len(stack))
        if len(visited)!=len(table):
            raise ValueError("orphan checkpoint nodes")
    except SearchCapExceeded as exc:
        stop = REASONS[exc.cap]
    # A cap at the final stack unwind must not create a false PARTIAL.
    # Every unresolved region is explicitly OPEN or represented by a suffix.
    unresolved = any(q["kind"]=="OPEN" or (q["kind"]=="SPLIT" and
                     q["cursor"]<q["alternative_count"]) for q in table.values())
    if not unresolved:
        stop = None
    if stop:
        for q in table.values():
            if q["kind"]=="OPEN":
                q["reason"]=stop
    cert = dict(format=FORMAT_V2,scope_digest=sd,mode=mode,
                declared_status="PARTIAL" if stop else "EXHAUSTED",
                root_owner=list(root.owner),incumbent=best,
                optima=[list(p) for p in sorted(winners)] if not stop and mode=="all" else [],
                nodes=[table[k] for k in sorted(table)])
    counters.update(budget.counters())
    counters.update(status="PARTIAL" if stop else "EXHAUSTED",stop_reason=stop,
                    nodes=len(table),operational_status="INCOMPLETE")
    return cert,counters


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw",required=True)
    p.add_argument("--scope",required=True)
    p.add_argument("--mode",choices=("one","all"),default="one")
    p.add_argument("--out",required=True)
    p.add_argument("--metrics")
    p.add_argument("--resume")
    p.add_argument("--split-rule",choices=(ALL_PAIRS,CROSS_SUPPORT),default=ALL_PAIRS)
    p.add_argument("--seconds",type=float)
    p.add_argument("--work",type=int)
    p.add_argument("--entries",type=int)
    p.add_argument("--frontier-bytes",type=int)
    a=p.parse_args()
    try:
        cert,metrics=solve(load(a.raw),load(a.scope),a.mode,
                           caps=SearchCaps(a.seconds,a.work,a.entries,a.frontier_bytes),
                           checkpoint=load(a.resume) if a.resume else None,
                           split_rule=a.split_rule)
        write_atomic(a.out,cert)
        if a.metrics:
            write_atomic(a.metrics,metrics)
        print(canonical(metrics).decode())
    except MemoryError:
        # No false proof on hard memory failure; an existing atomic checkpoint
        # remains usable. Hard kill/OS address space are runner-level censoring.
        print('{"status":"INCOMPLETE","operational_status":"INCOMPLETE","reason":"MEMORY_ERROR"}')
        return 2
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print(json.dumps(dict(status="INVALID",operational_status="INCOMPLETE",reason=str(exc))),
              file=sys.stderr)
        return 2
    return 0


if __name__=="__main__":
    sys.exit(main())
