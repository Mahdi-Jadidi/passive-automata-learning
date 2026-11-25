"""Independent flat P3 frontier verifier, frozen v1 (ff61b1c).
No producer imports. Path replay uses literal owner relabeling and prefix
constraints from previously checked parent records; no full alternatives list.
"""
import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

from independent_replay import sample_data
from journal_v2_replay import verify_journal
from bounded_deletion import DeletionBudget

class Invalid(ValueError):
    pass

class Incomplete(Exception):
    pass

def need(ok, msg):
    if not ok:
        raise Invalid(msg)

def fields(obj, names):
    need(type(obj) is dict and set(obj) == set(names.split()), "fields: " + names)

def canonical(obj):
    return json.dumps(obj, ensure_ascii=True, separators=(",", ":"),
                      sort_keys=True, allow_nan=False).encode("utf-8")

def sha(data):
    return hashlib.sha256(data).hexdigest()

def scope_digest(obj):
    return sha(canonical(obj))

def parse(obj, cap):
    if type(obj) is dict:
        if len(canonical(obj)) > cap:
            raise Incomplete("object byte cap")
        return obj
    if type(obj) is str:
        obj = obj.encode("utf-8")
    need(type(obj) is bytes, "expected JSON bytes or object")
    if len(obj) > cap:
        raise Incomplete("JSON byte cap")
    def pairs(items):
        out = {}
        for k, v in items:
            need(k not in out, "duplicate JSON key")
            out[k] = v
        return out
    def reject(s):
        raise Invalid("nonfinite JSON number")
    def finite(s):
        v = float(s)
        need(math.isfinite(v), "nonfinite JSON number")
        return v
    out = json.loads(obj.decode("utf-8"), object_pairs_hook=pairs,
                     parse_constant=reject, parse_float=finite)
    need(type(out) is dict, "JSON top-level object")
    return out

class Budget:
    def __init__(self, *, seconds=30, max_work=200_000_000,
                 max_exact_checks=20_000_000, max_nodes=100_000,
                 max_depth=10_000, max_entries=2_000_000,
                 max_journal_bytes=64*1024*1024,
                 max_proof_bytes=64*1024*1024,
                 max_raw_bytes=64*1024*1024):
        for v in (max_work, max_exact_checks, max_nodes, max_depth, max_entries,
                  max_journal_bytes, max_proof_bytes, max_raw_bytes):
            need(type(v) is int and v >= 0, "invalid integer budget")
        need(type(seconds) in (int, float) and 0 <= seconds <= 3600,
             "invalid time budget")
        self.deadline = time.monotonic() + seconds
        self.max_work, self.max_exact = max_work, max_exact_checks
        self.max_nodes, self.max_depth, self.max_entries = max_nodes, max_depth, max_entries
        self.max_journal_bytes, self.max_proof_bytes, self.max_raw_bytes = (
            max_journal_bytes, max_proof_bytes, max_raw_bytes)
        self.work = self.exact = self.nodes = 0
    def debit(self, amount=1):
        self.work += amount
        if self.work > self.max_work or time.monotonic() >= self.deadline:
            raise Incomplete("work/deadline cap")
    def check_exact(self):
        self.exact += 1
        if self.exact > self.max_exact:
            raise Incomplete("exact projection cap")
        self.debit()
    def entries(self, count):
        self.debit(0)
        if count > self.max_entries:
            raise Incomplete("entry cap")

def owner(value, n, b):
    need(type(value) is list and len(value) == n, "owner length")
    for i, x in enumerate(value):
        b.debit()
        need(type(x) is int and 0 <= x <= i, "owner range/type")
        need(type(value[x]) is int and value[x] == x, "owner not canonical")
    return tuple(value)

def _scope(raw, journal, b):
    b.debit(0)
    raw = parse(raw, b.max_raw_bytes)
    need(type(journal) is bytes, "exact journal bytes required")
    if len(journal) > b.max_journal_bytes:
        raise Incomplete("journal byte cap")
    # Precharge parsing/encoding work; exact journal replay uses its own
    # deletion budget. Line tracing also bounds the legacy Python replay loops
    # without modifying any P2 kernel or its pinned source.
    b.debit(len(canonical(raw)) + len(journal))
    modules = {"independent_replay", "journal_v2_replay", "production_replay",
               "ledger_replay", "interface_artifact_replay", "bounded_deletion"}
    def tracer(frame, event, arg):
        if event == "call":
            return tracer if frame.f_globals.get("__name__") in modules else None
        if event == "line":
            b.debit()
        return tracer
    db = DeletionBudget(work=max(0, b.max_work-b.work), entries=b.max_entries,
                        word_length=b.max_raw_bytes,
                        seconds=max(0, b.deadline-time.monotonic()))
    old_trace = sys.gettrace()
    try:
        sys.settrace(tracer)
        n, X, Y, sd = sample_data(raw)
        selector = dict(version="selector-v2/1", sample_digest=sd,
                        regime="UNRESTRICTED", family="ALL_PARTITIONS", capacity_digest=None)
        replay = verify_journal(raw, selector, journal, deletion_budget=db,
                                max_journal_bytes=b.max_journal_bytes)
    finally:
        sys.settrace(old_trace)
    b.debit(db.used)
    b.exact += db.exact_checks
    if b.exact > b.max_exact:
        raise Incomplete("journal exact-check cap")
    if replay.get("status") == "INVALID":
        raise Invalid("journal replay: " + str(replay.get("reason")))
    if replay.get("status") != "VERIFIED":
        raise Incomplete("journal replay: " + str(replay.get("reason")))
    root = owner(list(replay["result"]["proof"]["mandatory_owner"]), n, b)
    def rows(words, prefix):
        out = []
        for i, w in enumerate(words):
            b.debit(len(w)+1)
            out.append(dict(id=prefix+str(i), tokens=list(w)))
        return out
    scope = dict(format="p3-trusted-scope/v1", selector_scope=selector,
                 journal2_digest=sha(journal), alphabet=raw["alphabet"],
                 positive=rows(X, "P"), negative=rows(Y, "N"), root_owner=list(root))
    b.debit(0)
    return scope, root, X, Y

def build_trusted_scope(raw, exact_journal2_bytes, *, budgets=None):
    """Return scope or raise Invalid/Incomplete; never accept producer E0."""
    try:
        return _scope(raw, exact_journal2_bytes, Budget(**(budgets or {})))[0]
    except (MemoryError, RecursionError, TimeoutError) as e:
        raise Incomplete(type(e).__name__) from e

def pair_at(reps, j):
    k = len(reps)
    need(type(j) is int and 0 <= j < k*(k-1)//2, "pair index")
    lo, hi = 0, k-1
    while lo+1 < hi:
        mid = (lo+hi)//2
        if mid*(2*k-mid-1)//2 <= j:
            lo = mid
        else:
            hi = mid
    start = lo*(2*k-lo-1)//2
    return [reps[lo], reps[lo+1+j-start]]

def representatives(p, b):
    b.debit(len(p))
    return [i for i, x in enumerate(p) if i == x]

def compatible(p, X, Y, b):
    # Literal original-token projections. No producer cache, no hash-only hit.
    groups = representatives(p, b)
    def proj(w, g):
        out = []
        for t in w:
            b.debit()
            if p[t] == g:
                out.append(t)
        return out
    for y in Y:
        b.debit()
        separated = False
        for g in groups:
            b.debit()
            py = proj(y, g)
            for x in X:
                b.check_exact()
                px = proj(x, g)
                b.debit(min(len(px), len(py))+1)
                if py == px:
                    break
            else:
                separated = True
                break
        if not separated:
            return False
    return True

def coarsens(p, root, b):
    for i, x in enumerate(root):
        b.debit()
        need(p[i] == p[x], "incumbent violates E0")

def exact_int(v, expected):
    return type(v) is int and v == expected

def path_state(node, table, root, b, *, singleton_check=False):
    # Reconstruct one path at a time, not one owner array per certificate node.
    chain = []
    at = node
    while at["id"] != "root":
        b.debit()
        chain.append(at)
        if len(chain) > b.max_depth:
            raise Incomplete("path depth cap")
        at = table[at["parent_id"]]
    p = root
    residual = False
    for step in reversed(chain):
        b.debit()
        edge = step["edge"]
        if edge["kind"] == "RESIDUAL":
            residual = True
            continue
        a, c = edge["pair"]
        ra, rc = p[a], p[c]
        need(ra != rc, "child equality not between distinct classes")
        keep, drop = min(ra, rc), max(ra, rc)
        b.debit(len(p))
        p = tuple(keep if x == drop else x for x in p)
    reps = representatives(p, b)
    empty = False
    separated = set()
    # All earlier false alternatives are exactly the parent's checked prefix.
    # The residual's complete all-false family is represented by a flag,
    # never materialized. It cannot create a contradiction by itself.
    for step in chain:
        edge = step["edge"]
        if edge["kind"] != "CHILD":
            continue
        log = table[step["parent_id"]]["cursor_log"]
        for j in range(edge["index"]):
            b.debit()
            a, c = log[j]["pair"]
            ra, rc = p[a], p[c]
            if ra == rc:
                empty = True
            elif singleton_check and not residual:
                separated.add((min(ra, rc), max(ra, rc)))
                b.entries(len(separated))
    singleton = residual or len(reps) <= 1 or (
        singleton_check and len(separated) == len(reps)*(len(reps)-1)//2)
    return p, reps, empty, singleton

def verify_frontier(raw, exact_journal2_bytes, trusted_scope, proof, *, budgets=None, **limits):
    """Strict result envelope. Keyword limits retained for older callers."""
    b = None
    def result(status, reason, payload=None):
        out = dict(status=status, operational_status="INCOMPLETE", reason=reason,
                   nodes_checked=0 if b is None else b.nodes,
                   work_units=0 if b is None else b.work,
                   exact_checks=0 if b is None else b.exact)
        if status == "VERIFIED":
            out["result"] = payload
        return out
    try:
        b = Budget(**dict(budgets or {}, **limits))
        trusted, root, X, Y = _scope(raw, exact_journal2_bytes, b)
        supplied = parse(trusted_scope, b.max_raw_bytes)
        need(canonical(supplied) == canonical(trusted), "trusted scope mismatch")
        cert = parse(proof, b.max_proof_bytes)
        fields(cert, "format scope_digest mode declared_status root_owner incumbent optima nodes")
        need(cert["format"] == "p3-region-frontier/v1", "format")
        need(cert["scope_digest"] == scope_digest(trusted), "scope digest")
        n = len(root)
        need(owner(cert["root_owner"], n, b) == root, "root owner mismatch")
        mode, declared = cert["mode"], cert["declared_status"]
        need(mode in ("one", "all") and declared in ("EXHAUSTED", "PARTIAL"), "mode/status")
        inc, U = None, None
        if cert["incumbent"] is not None:
            q = cert["incumbent"]
            fields(q, "owner cost")
            inc = owner(q["owner"], n, b)
            coarsens(inc, root, b)
            U = n-len(representatives(inc, b))
            need(exact_int(q["cost"], U), "incumbent cost")
            need(compatible(inc, X, Y, b), "false incumbent")
        need(type(cert["optima"]) is list, "optima list")
        winners = [owner(q, n, b) for q in cert["optima"]]
        need(winners == sorted(set(winners)), "optima order/duplicates")
        need(not winners or (mode == "all" and declared == "EXHAUSTED"), "forbidden optima")
        nodes = cert["nodes"]
        need(type(nodes) is list and bool(nodes), "nodes must be nonempty")
        if len(nodes) > b.max_nodes:
            raise Incomplete("node cap")
        b.entries(len(nodes))
        table = {}
        previous = ""
        for q in nodes:
            b.debit()
            need(type(q) is dict and type(q.get("id")) is str, "node id")
            ident = q["id"]
            need(previous < ident, "node order/duplicate")
            previous = ident
            table[ident] = q
        need("root" in table, "missing root")
        found = set()
        best_found = None
        unresolved = False
        for q in nodes:
            b.debit()
            ident = q["id"]
            kind = q.get("kind")
            base = "id parent_id edge kind"
            if kind == "OPEN":
                fields(q, base+" reason")
            elif kind == "LEAF":
                fields(q, base+" closure")
            elif kind == "SPLIT":
                fields(q, base+" rule alternative_count cursor children cursor_log residual_id suffix")
            else:
                raise Invalid("node kind")
            edge = q["edge"]
            if ident == "root":
                need(q["parent_id"] is None and edge == {"kind":"ROOT"}, "root edge")
            else:
                parent_id = q["parent_id"]
                need(type(parent_id) is str and parent_id in table and
                     parent_id < ident, "parent absent/out of order")
                parent = table[parent_id]
                need(parent["kind"] == "SPLIT", "parent not SPLIT")
                need(type(edge) is dict, "edge")
                if edge.get("kind") == "CHILD":
                    fields(edge, "kind index pair")
                    j = edge["index"]
                    need(type(j) is int and 0 <= j < parent["cursor"], "child index")
                    need(ident == parent_id+"/c"+str(j) and parent["children"][j] == ident,
                         "child path/reference")
                    need(canonical(edge["pair"]) == canonical(parent["cursor_log"][j]["pair"]),
                         "child pair")
                else:
                    need(edge == {"kind":"RESIDUAL"} and ident == parent_id+"/r" and
                         parent["residual_id"] == ident and kind != "SPLIT", "residual path")
            closure = q.get("closure")
            exact_no = type(closure) is dict and closure.get("reason") == "EXACT_NO"
            p, reps, empty, singleton = path_state(q, table, root, b, singleton_check=exact_no)
            cost = n-len(reps)
            b.nodes += 1
            if kind == "OPEN":
                need(q["reason"] in ("TIME_CAP","WORK_CAP","ENTRY_CAP","FRONTIER_CAP","USER_STOP"),
                     "OPEN reason")
                unresolved = True
                continue
            if kind == "SPLIT":
                need(not empty and not singleton and q["rule"] == "ALL_PAIRS_LEX_V1",
                     "invalid split/rule")
                t = len(reps)*(len(reps)-1)//2
                need(t > 0 and exact_int(q["alternative_count"], t), "alternative count")
                c = q["cursor"]
                need(type(c) is int and 0 <= c <= t, "cursor range")
                children, log = q["children"], q["cursor_log"]
                need(type(children) is list and type(log) is list and len(children)==len(log)==c,
                     "missing/extra emitted child or cursor record")
                need(q["residual_id"] == ident+"/r" and q["residual_id"] in table, "missing residual")
                need(canonical(q["suffix"]) == canonical(dict(rule="FIRST_TRUE_SUFFIX_V1",start=c,stop=t)),
                     "missing/forged suffix")
                for j in range(c):
                    b.debit()
                    child = ident+"/c"+str(j)
                    need(children[j] == child and child in table, "missing/duplicate child")
                    need(canonical(log[j]) == canonical({"from":j,"to":j+1,"child_id":child,
                                                        "pair":pair_at(reps,j)}), "cursor log")
                unresolved |= c < t
                continue
            need(type(closure) is dict and type(closure.get("reason")) is str, "closure")
            reason = closure["reason"]
            if reason == "RAW_LABEL_CONFLICT":
                fields(closure, "reason positive_id negative_id")
                def trace_id(s, prefix, words):
                    need(type(s) is str and s.startswith(prefix) and s[1:].isdigit(),
                         "trace ID")
                    i = int(s[1:])
                    need(s == prefix+str(i) and 0 <= i < len(words), "trace ID range")
                    return words[i]
                x, y = trace_id(closure["positive_id"], "P", X), trace_id(closure["negative_id"], "N", Y)
                b.debit(min(len(x),len(y))+1)
                need(x == y, "forged raw conflict")
                continue
            fields(closure, "reason")
            if reason == "UNKNOWN":
                unresolved = True
            elif reason == "EMPTY":
                need(empty, "false EMPTY")
            else:
                need(not empty, "nonempty closure on empty region")
                if reason == "COST":
                    need(U is not None and (cost >= U if mode=="one" else cost > U),
                         "invalid cost cutoff")
                elif reason == "EXACT_NO":
                    need(singleton and not compatible(p,X,Y,b), "false EXACT_NO")
                elif reason == "FEASIBLE_MIN":
                    need(compatible(p,X,Y,b), "false FEASIBLE_MIN")
                    if best_found is None or cost < best_found:
                        best_found = cost
                    if mode == "all" and U == cost:
                        found.add(p)
                        b.entries(len(found))
                else:
                    raise Invalid("unsupported closure")
        b.debit(0)
        need((declared == "PARTIAL") == bool(unresolved), "declared status contradicts coverage")
        if declared == "PARTIAL":
            return result("INCOMPLETE", "unresolved frontier")
        need(best_found is None or (U is not None and best_found >= U), "missing/worse incumbent")
        if mode == "all":
            need((inc is None or inc in found) and winners == sorted(found), "all-optima mismatch")
        return result("VERIFIED", None, dict(optimum=U, owner=None if inc is None else list(inc),
                                            optima=[list(p) for p in winners]))
    except (Incomplete, MemoryError, RecursionError, TimeoutError) as e:
        return result("INCOMPLETE", str(e) or type(e).__name__)
    except (ValueError, TypeError, KeyError, IndexError, OverflowError, AttributeError) as e:
        return result("INVALID", str(e) or type(e).__name__)

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--make-trusted-scope", action="store_true")
    for name in ("raw","journal","scope","proof","out"):
        p.add_argument("--"+name, required=name in ("raw","journal"))
    for name, default in (("max-nodes",100000),("max-depth",10000),
                          ("max-work",200000000),("max-exact-checks",20000000),
                          ("max-entries",2000000),("max-journal-bytes",64*1024*1024),
                          ("max-proof-bytes",64*1024*1024),("max-raw-bytes",64*1024*1024)):
        p.add_argument("--"+name, type=int, default=default)
    p.add_argument("--seconds", type=float, default=30)
    a = p.parse_args(argv)
    limits = {k:v for k,v in vars(a).items() if k.startswith("max_") or k=="seconds"}
    def read(path, cap):
        need(path is not None, "missing path")
        with open(path,"rb") as f:
            data = f.read(cap+1)
        if len(data)>cap:
            raise Incomplete("input byte cap")
        return data
    try:
        Budget(**limits)
        raw = read(a.raw,a.max_raw_bytes)
        journal = read(a.journal,a.max_journal_bytes)
        if a.make_trusted_scope:
            need(a.out is not None, "--out required")
            scope = build_trusted_scope(raw,journal,budgets=limits)
            Path(a.out).write_bytes(canonical(scope))
            return 0
        out = verify_frontier(raw,journal,read(a.scope,a.max_raw_bytes),
                              read(a.proof,a.max_proof_bytes),budgets=limits)
    except (Incomplete,MemoryError,RecursionError,TimeoutError) as e:
        out = dict(status="INCOMPLETE",reason=str(e),operational_status="INCOMPLETE",
                   nodes_checked=0,work_units=0,exact_checks=0)
    except (ValueError,TypeError,OSError) as e:
        out = dict(status="INVALID",reason=str(e),operational_status="INCOMPLETE",
                   nodes_checked=0,work_units=0,exact_checks=0)
    print(canonical(out).decode("utf-8"))
    return {"VERIFIED":0,"INVALID":1,"INCOMPLETE":2}[out["status"]]

if __name__ == "__main__":
    raise SystemExit(main())
