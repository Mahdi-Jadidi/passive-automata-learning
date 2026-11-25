"""Independent P3 region/frontier certificate verifier.

This module deliberately has no dependency on the EDR-BB producer, its DSU,
cache, ranking, or pruning implementation. It independently replays the exact
journal/2 bytes and binds the frontier to the frozen selector-v2 schema scope.
"""
from __future__ import annotations

import hashlib
import json
import time
import argparse
from pathlib import Path

from selector_v2.schema import canonical as _schema_canonical
from independent_replay import sample_data
from journal_v2_replay import verify_journal


class _Invalid(Exception):
    pass


class _Censored(Exception):
    pass


def _need(ok, message):
    if not ok:
        raise _Invalid(message)


def _exact_keys(value, keys, where):
    _need(type(value) is dict, where + ": object required")
    _need(set(value) == set(keys), where + ": fields")


def _json_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise _Invalid("duplicate JSON key: " + str(key))
        out[key] = value
    return out


def _parse(value, where):
    if type(value) is dict:
        return value
    if type(value) is str:
        raw = value
    elif type(value) is bytes:
        try:
            raw = value.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise _Invalid(where + ": UTF-8") from exc
    else:
        raise _Invalid(where + ": object or JSON text required")
    try:
        result = json.loads(raw, object_pairs_hook=_json_pairs)
    except _Invalid:
        raise
    except (ValueError, TypeError) as exc:
        raise _Invalid(where + ": JSON") from exc
    _need(type(result) is dict, where + ": top-level object")
    return result


def _canonical_json(value):
    """Use the frozen selector-v2 schema canonical byte encoding."""
    return _schema_canonical(value)


def _sha256_bytes(value):
    _need(type(value) is bytes, "SHA-256 input must be exact bytes")
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value):
    _need(type(value) is str, "SHA-256 text input")
    return _sha256_bytes(value.encode("utf-8"))


def scope_digest(scope):
    """Digest the entire trusted envelope with selector_v2.schema.canonical()."""
    return _sha256_bytes(_canonical_json(scope))


def _hex_digest(value, where):
    _need(type(value) is str and len(value) == 64 and
          all(ch in "0123456789abcdef" for ch in value), where + ": SHA-256 hex")


def _owner(owner, n, where):
    _need(type(owner) is list and len(owner) == n, where + ": owner length")
    for i, value in enumerate(owner):
        _need(type(value) is int and 0 <= value <= i, where + ": owner range/canonical order")
        _need(owner[value] == value, where + ": owner is not a canonical minimum representative")
    return tuple(owner)


def _pairs(pairs, n, where):
    _need(type(pairs) is list, where + ": pair list")
    result = []
    previous = None
    for pair in pairs:
        _need(type(pair) is list and len(pair) == 2, where + ": pair shape")
        a, b = pair
        _need(type(a) is int and type(b) is int and 0 <= a < b < n, where + ": pair endpoints/order")
        item = (a, b)
        _need(previous is None or previous < item, where + ": pairs must be sorted and unique")
        result.append(item)
        previous = item
    return tuple(result)


def _owner_from_equalities(n, pairs):
    """Reconstruct E0 by graph traversal, not by the producer's DSU."""
    adjacency = [[] for _ in range(n)]
    for a, b in pairs:
        adjacency[a].append(b)
        adjacency[b].append(a)
    owner = [-1] * n
    for start in range(n):
        if owner[start] != -1:
            continue
        stack = [start]
        component = []
        owner[start] = start
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in adjacency[current]:
                if owner[neighbor] == -1:
                    owner[neighbor] = start
                    stack.append(neighbor)
        representative = min(component)
        for member in component:
            owner[member] = representative
    return tuple(owner)


def _validate_scope(raw_value, journal_bytes, value):
    """Bind raw sample, exact journal bytes, schema scope and replayed root E0.

    The journal is replayed by the previously committed independent journal/2
    kernel. No EDR-BB producer state is consulted. Trace IDs are stable original
    positions (P0.. and N0..) because selector-v2/1 stores ordered trace arrays.
    """
    raw = _parse(raw_value, "raw sample")
    scope = _parse(value, "trusted scope")
    _exact_keys(raw, {"alphabet", "positive", "negative"}, "raw sample")
    _exact_keys(scope, {"format", "selector_scope", "journal2_digest", "alphabet",
                        "positive", "negative", "root_equalities", "root_owner"}, "scope")
    _need(scope["format"] == "p3-trusted-scope/v1", "scope format")
    _need(type(journal_bytes) is bytes, "exact journal/2 bytes required")
    _hex_digest(scope["journal2_digest"], "journal2_digest")
    _need(scope["journal2_digest"] == _sha256_bytes(journal_bytes),
          "journal2 digest is not SHA-256 of the exact supplied bytes")

    n, positive_words, negative_words, sample_digest = sample_data(raw)
    selector_scope = _parse(scope["selector_scope"], "selector_scope")
    _exact_keys(selector_scope, {"version", "sample_digest", "regime", "family", "capacity_digest"},
                "selector_scope")
    expected_selector_scope = {
        "version": "selector-v2/1", "sample_digest": sample_digest,
        "regime": "UNRESTRICTED", "family": "ALL_PARTITIONS", "capacity_digest": None,
    }
    _need(selector_scope == expected_selector_scope, "selector scope/sample identity mismatch")

    alphabet = raw["alphabet"]
    _need(scope["alphabet"] == alphabet, "ordered original alphabet mismatch")
    expected_positive = [{"id": "P" + str(i), "tokens": list(tokens)}
                         for i, tokens in enumerate(positive_words)]
    expected_negative = [{"id": "N" + str(i), "tokens": list(tokens)}
                         for i, tokens in enumerate(negative_words)]
    _need(scope["positive"] == expected_positive, "positive original trace IDs/tokens mismatch")
    _need(scope["negative"] == expected_negative, "negative original trace IDs/tokens mismatch")

    # Replay the exact immutable journal/2 bytes. VERIFIED here means all supplied
    # events and records replay; operational_status remains INCOMPLETE by design.
    journal_result = verify_journal(raw, selector_scope, journal_bytes, max_journal_bytes=len(journal_bytes))
    if journal_result.get("status") == "INVALID":
        raise _Invalid("journal/2 replay INVALID: " + str(journal_result.get("reason", "invalid")))
    if journal_result.get("status") != "VERIFIED":
        raise _Censored("journal/2 replay INCOMPLETE: " + str(journal_result.get("reason", "censored")))
    replayed = journal_result["result"]["proof"]["mandatory_owner"]
    replayed_owner = _owner(list(replayed), n, "independently replayed journal/2 root owner")
    root_owner = _owner(scope["root_owner"], n, "trusted root E0 owner")
    _need(root_owner == replayed_owner, "root_owner is not reconstructed from independent journal/2 replay")

    root_equalities = _pairs(scope["root_equalities"], n, "trusted root equalities")
    expected_equalities = tuple((i, j) for i in range(n) for j in range(i + 1, n)
                                if replayed_owner[i] == replayed_owner[j])
    _need(root_equalities == expected_equalities, "root equalities do not encode replayed E0")
    _need(_owner_from_equalities(n, root_equalities) == replayed_owner,
          "root E0 owner is not equality closure")

    traces = {}
    for tid, tokens in [(row["id"], row["tokens"]) for row in expected_positive]:
        _need(tid not in traces, "duplicate positive trace ID")
        traces[tid] = ("positive", tuple(tokens))
    for tid, tokens in [(row["id"], row["tokens"]) for row in expected_negative]:
        _need(tid not in traces, "duplicate negative trace ID")
        traces[tid] = ("negative", tuple(tokens))
    return scope, n, replayed_owner, traces, scope_digest(scope)


def _class_representatives(owner):
    return tuple(sorted(set(owner)))


def _alternatives(owner):
    reps = _class_representatives(owner)
    return tuple((reps[i], reps[j]) for i in range(len(reps)) for j in range(i + 1, len(reps)))


def _merge_owner(owner, pair):
    a, b = pair
    ra, rb = owner[a], owner[b]
    if ra == rb:
        raise _Invalid("fallback alternative does not join distinct E-classes")
    keep, drop = (ra, rb) if ra < rb else (rb, ra)
    return tuple(keep if x == drop else x for x in owner)


def _union_disequalities(parent, earlier):
    return tuple(sorted(set(parent).union(earlier)))


def _empty(owner, disequalities):
    return any(owner[a] == owner[b] for a, b in disequalities)


def _singleton(owner, disequalities):
    reps = _class_representatives(owner)
    separated = set()
    for a, b in disequalities:
        ra, rb = owner[a], owner[b]
        if ra != rb:
            separated.add((min(ra, rb), max(ra, rb)))
    return all((reps[i], reps[j]) in separated
               for i in range(len(reps)) for j in range(i + 1, len(reps)))


def _compatible(owner, positives, negatives):
    groups = set(owner)
    positive_projections = {
        group: {tuple(token for token in trace if owner[token] == group)
                for trace in positives}
        for group in groups
    }
    for negative in negatives:
        separated = False
        for group in groups:
            projection = tuple(token for token in negative if owner[token] == group)
            if all(projection != candidate for candidate in positive_projections[group]):
                separated = True
                break
        if not separated:
            return False
    return True


def _coarsens(candidate, root_owner):
    mapping = {}
    for i, root_class in enumerate(root_owner):
        if root_class in mapping and mapping[root_class] != candidate[i]:
            return False
        mapping[root_class] = candidate[i]
    return True


def _cost(owner):
    return len(owner) - len(set(owner))


def _verify_leaf(node, owner, disequalities, ctx, incumbent_cost, mode, declared_status, found, where):
    closure = node["closure"]
    _need(type(closure) is dict and type(closure.get("reason")) is str, where + ": closure")
    reason = closure["reason"]
    n = ctx["n"]
    if reason == "UNKNOWN":
        _exact_keys(closure, {"reason"}, where + " UNKNOWN closure")
        if declared_status == "EXHAUSTED":
            raise _Invalid(where + ": EXHAUSTED declaration with UNKNOWN")
        raise _Censored("unresolved UNKNOWN closure")
    if reason == "EMPTY":
        _exact_keys(closure, {"reason"}, where + " EMPTY closure")
        _need(_empty(owner, disequalities), where + ": EMPTY without E-D contradiction")
        return
    if reason == "RAW_LABEL_CONFLICT":
        _exact_keys(closure, {"reason", "positive_id", "negative_id"}, where + " raw conflict")
        p = ctx["traces"].get(closure["positive_id"])
        y = ctx["traces"].get(closure["negative_id"])
        _need(type(closure["positive_id"]) is str and p is not None and p[0] == "positive",
              where + ": positive witness id")
        _need(type(closure["negative_id"]) is str and y is not None and y[0] == "negative",
              where + ": negative witness id")
        _need(p[1] == y[1], where + ": forged raw label-conflict witness")
        return
    _need(not _empty(owner, disequalities), where + ": non-EMPTY closure on empty region")
    if reason == "EXACT_NO":
        _exact_keys(closure, {"reason"}, where + " EXACT_NO closure")
        _need(_singleton(owner, disequalities), where + ": EXACT_NO region is not singleton")
        _need(not _compatible(owner, ctx["positive_tokens"], ctx["negative_tokens"]),
              where + ": EXACT_NO partition is structurally compatible")
        return
    if reason == "EXACT_FEASIBLE":
        _exact_keys(closure, {"reason", "owner", "cost"}, where + " EXACT_FEASIBLE closure")
        witness = _owner(closure["owner"], n, where + " feasible witness owner")
        _need(witness == owner, where + ": feasible witness does not equal singleton region")
        _need(_singleton(owner, disequalities), where + ": EXACT_FEASIBLE region is not singleton")
        actual_cost = _cost(owner)
        _need(type(closure["cost"]) is int and closure["cost"] == actual_cost,
              where + ": feasible witness cost")
        _need(_compatible(owner, ctx["positive_tokens"], ctx["negative_tokens"]),
              where + ": forged feasible witness")
        found.append((owner, actual_cost))
        return
    if reason == "COST":
        _exact_keys(closure, {"reason"}, where + " COST closure")
        _need(incumbent_cost is not None, where + ": COST closure without incumbent")
        lower_bound = n - len(set(owner))
        allowed = lower_bound >= incumbent_cost if mode == "one" else lower_bound > incumbent_cost
        _need(allowed, where + ": invalid base equality-class lower-bound cutoff")
        return
    raise _Invalid(where + ": unsupported closure reason " + reason)


def _missing_coverage(declared_status, message):
    if declared_status == "EXHAUSTED":
        raise _Invalid(message)
    raise _Censored(message)


def _visit(node, expected_id, expected_owner, expected_d, expected_via, ctx,
           incumbent_cost, mode, declared_status, found, budget, depth):
    if time.monotonic() > budget["deadline"]:
        raise _Censored("verification time cap")
    if budget["nodes"] >= budget["max_nodes"]:
        raise _Censored("verification node cap")
    if depth > budget["max_depth"]:
        raise _Censored("verification depth cap")
    budget["nodes"] += 1
    _need(type(node) is dict, expected_id + ": node object")
    kind = node.get("kind")
    base = {"id", "owner", "disequalities", "kind"}
    allowed = set(base)
    if expected_via is not None:
        allowed.add("via")
    if kind == "LEAF":
        allowed.add("closure")
    elif kind == "OPEN":
        pass
    elif kind == "SPLIT":
        allowed.update({"rule", "cursor", "suffix", "cursor_log", "children", "residual"})
    else:
        raise _Invalid(expected_id + ": unknown node kind")
    if kind == "SPLIT":
        required = {"rule", "cursor", "suffix", "cursor_log", "children", "residual"}
        missing = required.difference(node)
        if missing:
            _missing_coverage(declared_status, expected_id + ": missing frontier coverage field(s): " + ",".join(sorted(missing)))
    _exact_keys(node, allowed, expected_id)
    _need(node["id"] == expected_id, expected_id + ": duplicate/orphan/reparented node id")
    owner = _owner(node["owner"], ctx["n"], expected_id + " owner")
    _need(owner == expected_owner, expected_id + ": invalid parent-to-child E transition")
    disequalities = _pairs(node["disequalities"], ctx["n"], expected_id + " disequalities")
    _need(disequalities == expected_d, expected_id + ": invalid parent-to-child D transition")
    if expected_via is not None:
        _need(type(node["via"]) is list and len(node["via"]) == 2 and
              all(type(x) is int for x in node["via"]) and
              node["via"] == list(expected_via),
              expected_id + ": reordered/forged child alternative")
    if kind == "OPEN":
        budget["unresolved"] = True
        return
    if kind == "LEAF":
        _verify_leaf(node, owner, disequalities, ctx, incumbent_cost, mode, declared_status, found, expected_id)
        return

    _need(node["rule"] == "ALL_PAIRS_LEX_V1", expected_id + ": unsupported alternative/pruning rule")
    alternatives = _alternatives(owner)
    count = len(alternatives)
    _need(count > 0, expected_id + ": SPLIT has no alternatives")
    cursor = node["cursor"]
    _need(type(cursor) is int and 0 <= cursor <= count, expected_id + ": cursor range")
    children = node["children"]
    _need(type(children) is list, expected_id + ": children list")
    if len(children) < cursor:
        _missing_coverage(declared_status, expected_id + ": missing emitted child chunk")
    _need(len(children) == cursor, expected_id + ": children exceed cursor")
    digest = _sha256_bytes(_canonical_json([list(pair) for pair in alternatives]))
    suffix = node["suffix"]
    _exact_keys(suffix, {"rule", "start", "stop", "alternatives_sha256"}, expected_id + " suffix")
    _need(type(suffix["start"]) is int and type(suffix["stop"]) is int and
          type(suffix["alternatives_sha256"]) is str and
          suffix["rule"] == "FIRST_TRUE_SUFFIX_V1" and
          suffix["start"] == cursor and suffix["stop"] == count and
          suffix["alternatives_sha256"] == digest,
          expected_id + ": incomplete/forged lazy frontier suffix")
    log = node["cursor_log"]
    _need(type(log) is list, expected_id + ": cursor log list")
    if len(log) < cursor:
        _missing_coverage(declared_status, expected_id + ": missing cursor history chunk")
    _need(len(log) == cursor, expected_id + ": cursor log exceeds cursor")
    for i, record in enumerate(log):
        _exact_keys(record, {"from", "to", "child_id", "pair"}, expected_id + " cursor record")
        pair = alternatives[i]
        _need(type(record["from"]) is int and type(record["to"]) is int and
              type(record["child_id"]) is str and type(record["pair"]) is list and
              len(record["pair"]) == 2 and all(type(x) is int for x in record["pair"]) and
              record["from"] == i and record["to"] == i + 1 and
              record["child_id"] == expected_id + "/c" + str(i) and
              record["pair"] == list(pair), expected_id + ": cursor rollback/skip/reorder")
    for i, child in enumerate(children):
        pair = alternatives[i]
        child_owner = _merge_owner(owner, pair)
        child_d = _union_disequalities(disequalities, alternatives[:i])
        _visit(child, expected_id + "/c" + str(i), child_owner, child_d, pair,
               ctx, incumbent_cost, mode, declared_status, found, budget, depth + 1)
    residual_d = _union_disequalities(disequalities, alternatives)
    residual = node["residual"]
    _need(type(residual) is dict and residual.get("kind") in ("LEAF", "OPEN"),
          expected_id + ": residual must be an explicit singleton/empty disposition")
    _visit(residual, expected_id + "/r", owner, residual_d, None,
           ctx, incumbent_cost, mode, declared_status, found, budget, depth + 1)
    if cursor < count:
        budget["unresolved"] = True


def verify_frontier(raw, journal_bytes, scope, proof, *, max_nodes=100000, max_depth=200, seconds=10.0, max_journal_bytes=64*1024*1024):
    """Return VERIFIED, INVALID, or INCOMPLETE; never returns a partial result.

    Raw sample, exact journal/2 bytes, schema scope and E0 are replay-bound before
    any producer frontier record is examined. The producer cannot supply E0.
    """
    started = time.monotonic()
    try:
        _need(type(max_nodes) is int and max_nodes > 0, "max_nodes")
        _need(type(max_depth) is int and max_depth > 0, "max_depth")
        _need(type(seconds) in (int, float) and 0 <= seconds <= 3600, "seconds")
        _need(type(journal_bytes) is bytes, "exact journal/2 bytes required")
        _need(type(max_journal_bytes) is int and max_journal_bytes > 0, "max_journal_bytes")
        if len(journal_bytes) > max_journal_bytes:
            raise _Censored("journal byte cap")
        trusted, n, root_owner, traces, digest = _validate_scope(raw, journal_bytes, scope)
        if time.monotonic() - started > seconds:
            raise _Censored("verification time cap during journal/2 replay")
        cert = _parse(proof, "proof")
        _exact_keys(cert, {"format", "scope_digest", "mode", "declared_status",
                           "root_owner", "incumbent", "optima", "root"}, "proof")
        _need(cert["format"] == "p3-region-frontier/v1", "proof format")
        _need(cert["scope_digest"] == digest, "stale or mismatched scope digest")
        mode = cert["mode"]
        _need(mode in ("one", "all"), "optimum mode")
        declared = cert["declared_status"]
        _need(declared in ("EXHAUSTED", "PARTIAL"), "declared status")
        _need(_owner(cert["root_owner"], n, "proof root owner") == root_owner,
              "root E0 does not match independently replayed journal/2 scope")
        incumbent = cert["incumbent"]
        incumbent_owner = None
        incumbent_cost = None
        if incumbent is not None:
            _exact_keys(incumbent, {"owner", "cost"}, "incumbent")
            incumbent_owner = _owner(incumbent["owner"], n, "incumbent owner")
            _need(_coarsens(incumbent_owner, root_owner), "incumbent violates mandatory E0")
            incumbent_cost = _cost(incumbent_owner)
            _need(type(incumbent["cost"]) is int and incumbent["cost"] == incumbent_cost,
                  "incumbent cost")
            positives = [row["tokens"] for row in trusted["positive"]]
            negatives = [row["tokens"] for row in trusted["negative"]]
            _need(_compatible(incumbent_owner, positives, negatives), "incumbent is not structurally compatible")
        optima = cert["optima"]
        _need(type(optima) is list, "optima list")
        checked_optima = []
        for item in optima:
            checked_optima.append(_owner(item, n, "reported optimum owner"))
        _need(checked_optima == sorted(set(checked_optima)), "optima must be sorted and unique")
        if mode == "one":
            _need(not checked_optima, "one-optimum mode must not claim all optima")
        ctx = {
            "n": n,
            "traces": traces,
            "positive_tokens": [row["tokens"] for row in trusted["positive"]],
            "negative_tokens": [row["tokens"] for row in trusted["negative"]],
        }
        found = []
        budget = {"nodes": 0, "max_nodes": max_nodes, "max_depth": max_depth,
                  "deadline": started + seconds, "unresolved": False}
        _visit(cert["root"], "root", root_owner, (), None, ctx,
               incumbent_cost, mode, declared, found, budget, 0)
        if budget["unresolved"]:
            if declared == "EXHAUSTED":
                raise _Invalid("EXHAUSTED declaration with OPEN/UNKNOWN/nonempty suffix")
            raise _Censored("frontier is PARTIAL")
        if declared != "EXHAUSTED":
            raise _Censored("producer did not declare EXHAUSTED")
        if incumbent_cost is None:
            _need(not found, "feasible singleton found without final incumbent")
            _need(not checked_optima, "optima reported without incumbent")
            return {"status": "VERIFIED", "result": {"optimum": None, "owner": None,
                    "optima": []}, "nodes_checked": budget["nodes"],
                    "operational_status": "INCOMPLETE"}
        _need(all(cost >= incumbent_cost for _, cost in found),
              "a feasible singleton beats the final incumbent")
        if mode == "all":
            winners = {incumbent_owner}
            winners.update(owner for owner, cost in found if cost == incumbent_cost)
            _need(checked_optima == sorted(winners), "all-optima list is incomplete or contains a false optimum")
            result_optima = [list(owner) for owner in checked_optima]
        else:
            result_optima = []
        return {"status": "VERIFIED", "result": {"optimum": incumbent_cost,
                "owner": list(incumbent_owner), "optima": result_optima},
                "nodes_checked": budget["nodes"], "operational_status": "INCOMPLETE"}
    except _Censored:
        return {"status": "INCOMPLETE", "operational_status": "INCOMPLETE"}
    except MemoryError:
        return {"status": "INCOMPLETE", "operational_status": "INCOMPLETE"}
    except _Invalid as exc:
        return {"status": "INVALID", "reason": str(exc), "operational_status": "INCOMPLETE"}
    except (TypeError, ValueError, RecursionError):
        return {"status": "INVALID", "reason": "malformed evidence", "operational_status": "INCOMPLETE"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Independently verify a P3 EDR-BB region/frontier certificate")
    parser.add_argument("--raw", required=True, help="raw three-key sample JSON")
    parser.add_argument("--journal", required=True, help="exact canonical journal/2 bytes")
    parser.add_argument("--scope", required=True, help="p3-trusted-scope/v1 JSON")
    parser.add_argument("--proof", required=True, help="p3-region-frontier/v1 JSON")
    parser.add_argument("--max-nodes", type=int, default=100000)
    parser.add_argument("--max-depth", type=int, default=200)
    parser.add_argument("--seconds", type=float, default=10.0)
    args = parser.parse_args(argv)
    raw = json.loads(Path(args.raw).read_text(encoding="utf-8"))
    scope = json.loads(Path(args.scope).read_text(encoding="utf-8"))
    proof = json.loads(Path(args.proof).read_text(encoding="utf-8"))
    result = verify_frontier(raw, Path(args.journal).read_bytes(), scope, proof,
                             max_nodes=args.max_nodes, max_depth=args.max_depth, seconds=args.seconds)
    print(json.dumps(result, sort_keys=True, ensure_ascii=True, separators=(",", ":")))
    return 0 if result.get("status") == "VERIFIED" else (2 if result.get("status") == "INCOMPLETE" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
