"""P3 M2 producer, frozen p3-region-frontier/v1. No external evaluator.

A DFS path stores prefix constraints symbolically. For two current E classes
with minima a<b, the least cross-class pair of representatives of ANY ancestor
E is (a,b): both minima were representatives there. Consequently merging these
classes violates an ancestor's first-true prefix iff (a,b) is lexicographically
less than that ancestor's selected pair. The maximum selected pair suffices
for exact D emptiness on a nonempty path. This is a representation of D,
not an additional pruning rule; even forbidden children are emitted as EMPTY.
The all-false residual is represented by its edge, never by a pair array.
"""
import argparse
import hashlib
import json
from pathlib import Path
import os
import sys

from .core import Sample
from .edr_bb import RegionState, RollbackDSU, SearchBudget, SearchCaps, SearchCapExceeded

FORMAT = "p3-region-frontier/v1"
REASONS = {"seconds":"TIME_CAP", "work":"WORK_CAP", "entries":"ENTRY_CAP",
           "memory_bytes":"FRONTIER_CAP"}


def canonical(obj):
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def load(path):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError("duplicate JSON key")
            result[k] = v
        return result
    def reject(_):
        raise ValueError("nonfinite JSON number")
    return json.loads(Path(path).read_bytes().decode("utf-8"),
                      object_pairs_hook=pairs, parse_constant=reject)


def pair_at(reps, j):
    k = len(reps)
    t = k*(k-1)//2
    if type(j) is not int or not 0 <= j < t:
        raise ValueError("pair index")
    lo, hi = 0, k-1
    while lo+1 < hi:
        i = (lo+hi)//2
        if i*(2*k-i-1)//2 <= j:
            lo = i
        else:
            hi = i
    return reps[lo], reps[lo+1+j-lo*(2*k-lo-1)//2]


def validate_scope(raw, scope):
    sample = Sample.from_input(raw)
    expected = {"format","selector_scope","journal2_digest","alphabet",
                "positive","negative","root_owner"}
    if type(scope) is not dict or set(scope) != expected:
        raise ValueError("trusted scope fields")
    if scope["format"] != "p3-trusted-scope/v1":
        raise ValueError("trusted scope version")
    sc = dict(version="selector-v2/1", sample_digest=sample.sample_digest,
              regime="UNRESTRICTED", family="ALL_PARTITIONS", capacity_digest=None)
    if scope["selector_scope"] != sc or scope["alphabet"] != raw["alphabet"]:
        raise ValueError("scope/sample mismatch")
    for key, tag, words in (("positive","P",sample.positive),("negative","N",sample.negative)):
        actual = scope[key]
        expected = [dict(id=tag+str(i),tokens=list(w)) for i,w in enumerate(words)]
        # Canonical bytes distinguish bool from int.
        if canonical(actual) != canonical(expected):
            raise ValueError("scope trace mismatch")
    h = scope["journal2_digest"]
    if type(h) is not str or len(h)!=64 or any(c not in "0123456789abcdef" for c in h):
        raise ValueError("journal digest syntax")
    if type(scope["root_owner"]) is not list:
        raise ValueError("root owner array")
    region = RegionState(tuple(scope["root_owner"]))
    if region.alphabet_size != len(sample.alphabet):
        raise ValueError("root alphabet mismatch")
    # Trust boundary: only Agent #3's independently replayed scope authorizes E0.
    # Producer cannot certify the journal; verifier must replay it again.
    return sample, region


def compatible(owner, X, Y, budget):
    """Literal projections use original token IDs, including empty projections."""
    groups = sorted(set(owner))
    if not Y:
        return True
    remaining = set(range(len(Y)))
    def project(w, g):
        out = []
        budget.charge_work()
        for a in w:
            budget.charge_work()
            if owner[a] == g:
                out.append(a)
        return tuple(out)
    for g in groups:
        budget.charge_work()
        positives = set()
        for x in X:
            positives.add(project(x,g))
        # List of indices, not trace deduplication; stable iteration order.
        for i in sorted(remaining):
            if project(Y[i],g) not in positives:
                remaining.remove(i)
        if not remaining:
            return True
    return False


def raw_conflict(sample, budget):
    seen = {}
    for j,x in enumerate(sample.positive):
        budget.charge_work(1+len(x))
        seen.setdefault(x,j)
    for i,y in enumerate(sample.negative):
        budget.charge_work(1+len(y))
        if y in seen:
            return dict(reason="RAW_LABEL_CONFLICT",positive_id="P"+str(seen[y]),
                        negative_id="N"+str(i))
    return None


def open_node(ident, parent, edge):
    return dict(id=ident,parent_id=parent,edge=edge,kind="OPEN",reason="USER_STOP")


def close(node, reason):
    del node["reason"]
    node.update(kind="LEAF",closure=reason)


def write_atomic(path, obj):
    path = Path(path)
    tmp = path.with_name(path.name+".tmp")
    # Stream encoding; do not allocate another complete serialized proof.
    with tmp.open("w",encoding="utf-8",newline="") as f:
        json.dump(obj,f,ensure_ascii=True,sort_keys=True,separators=(",",":"),allow_nan=False)
    os.replace(tmp,path)


def solve(raw, scope, mode="one", *, caps=None, checkpoint=None):
    """Return (certificate, telemetry). A checkpoint is a trusted local PARTIAL
    certificate. It is not an authority: only independent replay certifies
    the final result. Resume walks emitted DFS prefix without reevaluating
    closed leaves, reconstructs their winners, and continues at the cursor.
    Limits are per invocation. Root placeholder is mandatory and not charged
    as a new entry. Entry cap counts newly emitted child/residual nodes.
    """
    if mode not in ("one","all"):
        raise ValueError("mode")
    sample, root = validate_scope(raw,scope)
    sd = digest(scope)
    budget = SearchBudget(caps)
    if checkpoint is None:
        table = {"root":open_node("root",None,dict(kind="ROOT"))}
        best = None
    else:
        if (type(checkpoint) is not dict or set(checkpoint) !=
            {"format","scope_digest","mode","declared_status","root_owner","incumbent","optima","nodes"}
            or checkpoint["format"] != FORMAT or checkpoint["scope_digest"] != sd
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
    stack = [["root",dsu.mark(),None,False,-1]]
    visited = set()
    counters = dict(expanded=0,closed=0,exact_checks=0,generated=0,
                    resumed_nodes=0,peak_depth=1)
    stop = None

    def candidate(owner, cost):
        nonlocal best, winners
        if best is None or cost < best["cost"]:
            best = dict(owner=list(owner),cost=cost)
            winners = {owner}
        elif cost == best["cost"]:
            winners.add(owner)

    def finish():
        frame = stack.pop()
        dsu.rollback(frame[1])

    def leaf(node, why):
        close(node,why)
        counters["closed"] += 1

    try:
        conflict = raw_conflict(sample,budget)
        if best is not None:
            if not compatible(tuple(best["owner"]),sample.positive,sample.negative,budget):
                raise ValueError("checkpoint incumbent incompatible")
        while stack:
            budget.charge_work()
            ident, mark, threshold, empty, next_j = stack[-1]
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
                    t = k*(k-1)//2
                    rid = ident+"/r"
                    residual = open_node(rid,ident,dict(kind="RESIDUAL"))
                    close(residual,dict(reason="EXACT_NO"))
                    # Admission before changing parent: interruption cannot lose
                    # the residual, or commit a split without a suffix.
                    budget.admit_frontier_entry(len(canonical(residual)))
                    if rid in table:
                        raise ValueError("duplicate residual")
                    table[rid] = residual
                    visited.add(rid)
                    del q["reason"]
                    q.update(kind="SPLIT",rule="ALL_PAIRS_LEX_V1",
                             alternative_count=t,cursor=0,children=[],cursor_log=[],
                             residual_id=rid,suffix=dict(rule="FIRST_TRUE_SUFFIX_V1",start=0,stop=t))
                    counters["generated"] += 1
                    counters["closed"] += 1
                    counters["expanded"] += 1
                elif q["kind"] == "SPLIT":
                    rid = ident+"/r"
                    if empty or q["residual_id"]!=rid or table[rid] != dict(
                            id=rid,parent_id=ident,edge=dict(kind="RESIDUAL"),
                            kind="LEAF",closure=dict(reason="EXACT_NO")):
                        raise ValueError("invalid local checkpoint split")
                    visited.add(rid)
                    counters["resumed_nodes"] += 1
                else:
                    raise ValueError("checkpoint node kind")
                stack[-1][4] = 0
                continue
            budget.charge_work(root.alphabet_size)
            reps = dsu.representatives()
            t = len(reps)*(len(reps)-1)//2
            cursor = q["cursor"]
            if (q["rule"]!="ALL_PAIRS_LEX_V1" or t!=q["alternative_count"]
                or type(cursor) is not int or not 0<=cursor<=t
                or len(q["children"])!=cursor or len(q["cursor_log"])!=cursor
                or q["suffix"]!=dict(rule="FIRST_TRUE_SUFFIX_V1",start=cursor,stop=t)):
                raise ValueError("invalid checkpoint cursor")
            if next_j == t:
                finish()
                continue
            j = next_j
            pair = pair_at(reps,j)
            child_id = ident+"/c"+str(j)
            edge = dict(kind="CHILD",index=j,pair=list(pair))
            record = {"from":j,"to":j+1,"child_id":child_id,"pair":list(pair)}
            if j < cursor:
                child = table[child_id]
                if (q["children"][j]!=child_id or q["cursor_log"][j]!=record
                    or child["parent_id"]!=ident or child["edge"]!=edge):
                    raise ValueError("checkpoint child mismatch")
            elif j == cursor:
                child = open_node(child_id,ident,edge)
                budget.admit_frontier_entry(len(canonical(child))+len(canonical(record)))
                if child_id in table:
                    raise ValueError("duplicate child")
                table[child_id] = child
                q["children"].append(child_id)
                q["cursor_log"].append(record)
                q["cursor"] = j+1
                q["suffix"]["start"] = j+1
                counters["generated"] += 1
            else:
                raise ValueError("DFS skipped cursor")
            child_mark = dsu.mark()
            dsu.union(*pair)
            invalid = threshold is not None and pair < threshold
            stack[-1][4] += 1
            stack.append([child_id,child_mark,pair if threshold is None else max(pair,threshold),invalid,-1])
            counters["peak_depth"] = max(counters["peak_depth"],len(stack))
        if len(visited)!=len(table):
            raise ValueError("orphan checkpoint nodes")
    except SearchCapExceeded as exc:
        stop = REASONS[exc.cap]
    if stop:
        for q in table.values():
            if q["kind"]=="OPEN":
                q["reason"]=stop
    cert = dict(format=FORMAT,scope_digest=sd,mode=mode,
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
    p.add_argument("--seconds",type=float)
    p.add_argument("--work",type=int)
    p.add_argument("--entries",type=int)
    p.add_argument("--frontier-bytes",type=int)
    a=p.parse_args()
    try:
        cert,metrics=solve(load(a.raw),load(a.scope),a.mode,
                           caps=SearchCaps(a.seconds,a.work,a.entries,a.frontier_bytes),
                           checkpoint=load(a.resume) if a.resume else None)
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
