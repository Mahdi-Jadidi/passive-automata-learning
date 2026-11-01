"""C006 exact existential test for a nontrivial two-factor decomposition.

Exact complete-word labels, known alphabet, two nonempty disjoint blocks, and
unrestricted regular factors. Finite positive projections are witnesses, not a
restriction on the target languages. Uses only a frozen C005 must-link helper.
"""
from __future__ import annotations
import hashlib
import importlib.util
import math
import time
from pathlib import Path

METHOD = "c006-unknown-k-general-regular-v1"
PARENT_HELPER = (Path(__file__).resolve().parents[3] / "2026-10-31"
                 / "partition_coverage_v5" / "general" / "known_k_qexact_v2.py")
PARENT_HELPER_SHA256 = "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d"


class _Stop(Exception):
    pass


def _check(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise _Stop


def _load_parent_helper():
    raw = PARENT_HELPER.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != PARENT_HELPER_SHA256:
        raise RuntimeError("frozen C005 helper hash mismatch: " + digest)
    spec = importlib.util.spec_from_file_location("c006_frozen_c005_qexact_v2", PARENT_HELPER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen C005 helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate(data):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    forbidden = {"k", "q", "local_word_cap"} & set(data)
    if forbidden:
        raise ValueError("C006 input must not specify " + ", ".join(sorted(forbidden)))
    alphabet = data.get("alphabet")
    if (not isinstance(alphabet, list) or not alphabet
            or any(not isinstance(a, str) or len(a) != 1 for a in alphabet)
            or len(set(alphabet)) != len(alphabet)):
        raise ValueError("alphabet must be a nonempty list of distinct one-character strings")
    alphabet = sorted(alphabet)
    sigma = set(alphabet)
    classes = []
    for key in ("positive", "negative"):
        words = data.get(key)
        if not isinstance(words, list) or any(not isinstance(w, str) for w in words):
            raise ValueError(key + " must be a list of strings")
        if any(set(w) - sigma for w in words):
            raise ValueError(key + " contains a symbol outside alphabet")
        classes.append(sorted(set(words)))
    positive, negative = classes
    if set(positive) & set(negative):
        raise ValueError("contradictory labels")
    return alphabet, positive, negative


def _project(word, block, deadline=None):
    out = []
    for i, symbol in enumerate(word):
        if i % 256 == 0:
            _check(deadline)
        if symbol in block:
            out.append(symbol)
    return "".join(out)


def _blocks_from_mask(atoms, mask):
    left, right = set(), set()
    for i, atom in enumerate(atoms):
        (left if (mask >> i) & 1 else right).update(atom)
    return [sorted(left), sorted(right)]


def _compatibility(blocks, positive, negative, deadline=None):
    languages = []
    for block in blocks:
        _check(deadline)
        languages.append({_project(word, set(block), deadline) for word in positive})
    positive_witnesses = [
        {"word": word, "projections": [_project(word, set(b), deadline) for b in blocks]}
        for word in positive]
    negative_witnesses = []
    for word in negative:
        _check(deadline)
        projections = [_project(word, set(b), deadline) for b in blocks]
        unseen = [i for i in range(2) if projections[i] not in languages[i]]
        if not unseen:
            matches = [next(p for p in positive if
                            _project(p, set(blocks[i]), deadline) == projections[i])
                       for i in range(2)]
            return None, {"negative": word, "projections": projections,
                          "matching_positive_by_side": matches}
        negative_witnesses.append({"word": word, "projections": projections,
                                   "rejected_by_side": unseen[0]})
    return {"blocks": blocks,
            "positive_projection_languages": [sorted(x) for x in languages],
            "positive_witnesses": positive_witnesses,
            "negative_witnesses": negative_witnesses}, None


def _canonical_masks(atom_count):
    # Atom zero is fixed on side zero, removing block-swap duplicates.
    for tail in range((1 << (atom_count - 1)) - 1):
        yield (tail << 1) | 1


def _replay_must_link_edge(edge, positive, negative, alphabet):
    pair, w = edge.get("symbols"), edge.get("witness")
    if (not isinstance(pair, list) or len(pair) != 2 or pair[0] == pair[1]
            or any(not isinstance(a, str) or a not in alphabet for a in pair)
            or not isinstance(w, dict) or w.get("rule") not in ("adjacent_swap", "insertion_rescue")
            or not isinstance(w.get("negative"), str)):
        return False
    a, b = pair
    if w.get("negative") not in negative:
        return False
    if w["rule"] == "adjacent_swap":
        p, i = w.get("positive"), w.get("position")
        return (p in positive and isinstance(i, int) and not isinstance(i, bool)
                and 0 <= i < len(p)-1 and p[i:i+2] in (a+b, b+a)
                and p[:i] + p[i+1] + p[i] + p[i+2:] == w["negative"])
    if w["rule"] == "insertion_rescue":
        ps = w.get("positive")
        if not isinstance(ps, list) or len(ps) != 2 or any(p not in positive for p in ps):
            return False
        base, rescued = ps
        # The C005 edge stores its symbol pair sorted, while the deleted and
        # inserted roles are contextual. Try both role orientations.
        claimed_i = w.get("position")
        if isinstance(claimed_i, bool) or not isinstance(claimed_i, int):
            return False
        for i, symbol in enumerate(w["negative"]):
            if i != claimed_i or symbol not in pair or w["negative"][:i] + w["negative"][i+1:] != base:
                continue
            inserted = pair[1] if symbol == pair[0] else pair[0]
            if rescued in (w["negative"][:i] + inserted + w["negative"][i:],
                           w["negative"][:i+1] + inserted + w["negative"][i+1:]):
                return True
        return False
    return False


def _union_components(alphabet, edges):
    parent = {a: a for a in alphabet}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for edge in edges:
        a, b = edge["symbols"]
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    out = {}
    for a in alphabet:
        out.setdefault(find(a), []).append(a)
    return sorted((sorted(x) for x in out.values()), key=lambda x: x[0])


def verify_certificate(data, certificate):
    """Replay a no-decomposition certificate without invoking the solver."""
    try:
        alphabet, positive, negative = _validate(data)
    except (ValueError, TypeError):
        return {"valid": False, "reason": "invalid_input"}
    if not isinstance(certificate, dict) or certificate.get("kind") != "no_nontrivial_bipartition":
        return {"valid": False, "reason": "wrong_certificate_kind"}
    if len(alphabet) == 1:
        valid = (certificate.get("obstruction") == "singleton_alphabet"
                 and certificate.get("alphabet") == alphabet
                 and certificate.get("components") == [alphabet]
                 and certificate.get("must_link_edges") == [])
        return {"valid": valid, "kind": "singleton_alphabet"}
    edges = certificate.get("must_link_edges")
    if not isinstance(edges, list):
        return {"valid": False, "reason": "missing_must_link_edges"}
    for edge in edges:
        if not isinstance(edge, dict) or not _replay_must_link_edge(edge, positive, negative, set(alphabet)):
            return {"valid": False, "reason": "invalid_must_link_witness", "edge": edge}
    if certificate.get("alphabet") != alphabet:
        return {"valid": False, "reason": "alphabet_mismatch"}
    components = _union_components(alphabet, edges)
    if certificate.get("components") != components:
        return {"valid": False, "reason": "component_partition_mismatch",
                "expected_components": components}
    if len(components) == 1:
        if certificate.get("obstruction") != "connected_must_link_graph":
            return {"valid": False, "reason": "wrong_connected_obstruction"}
        return {"valid": True, "kind": "connected_must_link_graph", "checked_cuts": 0}
    if certificate.get("obstruction") != "complete_cut_collision_cover":
        return {"valid": False, "reason": "wrong_cut_obstruction"}
    records = certificate.get("cut_rejections")
    if not isinstance(records, list):
        return {"valid": False, "reason": "missing_cut_rejections"}
    expected = [(tail << 1) | 1 for tail in range((1 << (len(components)-1))-1)]
    by_mask = {}
    for record in records:
        mask = record.get("canonical_left_atom_mask") if isinstance(record, dict) else None
        if isinstance(mask, bool) or not isinstance(mask, int) or mask in by_mask:
            return {"valid": False, "reason": "duplicate_or_invalid_cut"}
        by_mask[mask] = record
    if set(by_mask) != set(expected):
        return {"valid": False, "reason": "cut_cover_incomplete",
                "expected_cut_count": len(expected), "actual_cut_count": len(by_mask)}
    for mask in expected:
        blocks = _blocks_from_mask(components, mask)
        record = by_mask[mask]
        collision = record.get("collision")
        if not isinstance(collision, dict) or collision.get("negative") not in negative:
            return {"valid": False, "reason": "missing_collision_negative", "mask": mask}
        witnesses = collision.get("matching_positive_by_side")
        if not isinstance(witnesses, list) or len(witnesses) != 2:
            return {"valid": False, "reason": "missing_side_collisions", "mask": mask}
        for side, p in enumerate(witnesses):
            n = collision["negative"]
            if p not in positive or _project(p, set(blocks[side])) != _project(n, set(blocks[side])):
                return {"valid": False, "reason": "invalid_side_collision", "mask": mask,
                        "side": side}
    return {"valid": True, "kind": "complete_cut_collision_cover", "checked_cuts": len(expected)}


def verify_solution(data, solution):
    """Replay direct projection witnesses for one compatible partition."""
    try:
        alphabet, positive, negative = _validate(data)
    except (ValueError, TypeError):
        return {"valid": False, "reason": "invalid_input"}
    if not isinstance(solution, dict):
        return {"valid": False, "reason": "solution_not_object"}
    blocks = solution.get("blocks")
    if not isinstance(blocks, list) or len(blocks) != 2 or any(not isinstance(b, list) or not b for b in blocks):
        return {"valid": False, "reason": "not_two_nonempty_blocks"}
    left, right = map(set, blocks)
    if left & right or left | right != set(alphabet):
        return {"valid": False, "reason": "blocks_not_partition"}
    langs = [{_project(p, b) for p in positive} for b in (left, right)]
    if solution.get("positive_projection_languages") != [sorted(x) for x in langs]:
        return {"valid": False, "reason": "positive_projection_language_mismatch"}
    expected_positive = [{"word": p, "projections": [_project(p, b) for b in (left, right)]}
                         for p in positive]
    if solution.get("positive_witnesses") != expected_positive:
        return {"valid": False, "reason": "positive_witness_mismatch"}
    expected_negative = []
    for n in negative:
        projections = [_project(n, b) for b in (left, right)]
        unseen = [i for i in range(2) if projections[i] not in langs[i]]
        if not unseen:
            return {"valid": False, "reason": "negative_not_rejected", "negative": n}
        expected_negative.append({"word": n, "projections": projections, "rejected_by_side": unseen[0]})
    if solution.get("negative_witnesses") != expected_negative:
        return {"valid": False, "reason": "negative_witness_mismatch"}
    return {"valid": True, "positive_count": len(positive), "negative_count": len(negative)}


def solve(data, *, deadline=None, max_solutions=1):
    """Find compatible bipartitions or return a complete replayable obstruction.

    deadline is an absolute perf_counter timestamp. max_solutions defaults to
    one; None returns all. A truncated result has complete=False. A single
    early answer proves existence but does not establish uniqueness.
    """
    started = time.perf_counter()
    if max_solutions is not None and (isinstance(max_solutions, bool)
            or not isinstance(max_solutions, int) or max_solutions < 1):
        raise ValueError("max_solutions must be a positive integer or None")
    if deadline is not None and (isinstance(deadline, bool)
            or not isinstance(deadline, (int, float)) or not math.isfinite(deadline)):
        raise ValueError("deadline must be a finite absolute perf_counter value or None")
    metrics = {"canonical_cuts_checked": 0, "must_link_edges": 0,
               "contracted_components": None, "provider_seconds": 0.0}
    try:
        alphabet, positive, negative = _validate(data)
    except (ValueError, TypeError) as exc:
        return {"method": METHOD, "status": "invalid_input", "complete": True,
                "decision_complete": True, "uniqueness": "unknown", "solutions": [],
                "certificate": None, "error": str(exc), "metrics": metrics}
    metrics.update(alphabet_size=len(alphabet), positive_count=len(positive), negative_count=len(negative))
    if len(alphabet) == 1:
        cert = {"kind": "no_nontrivial_bipartition", "obstruction": "singleton_alphabet",
                "alphabet": alphabet, "components": [alphabet], "must_link_edges": []}
        check = verify_certificate(data, cert)
        return {"method": METHOD, "status": "not_decomposable", "complete": True,
                "decision_complete": True, "uniqueness": "none",
                "uniqueness_scope": "sample_compatible_nontrivial_two_block_partitions",
                "solutions": [], "certificate": cert, "certificate_check": check,
                "assumptions": ["exact labels", "known alphabet", "two nonempty disjoint blocks",
                                "unrestricted regular local factors"],
                "metrics": dict(metrics, contracted_components=1,
                                 provider_seconds=time.perf_counter()-started)}
    try:
        _check(deadline)
        helper = _load_parent_helper()
        components, raw_edges = helper._components(alphabet, positive, negative, deadline)
    except KeyboardInterrupt:
        return {"method": METHOD, "status": "incomplete", "complete": False,
                "decision_complete": False, "uniqueness": "unknown", "solutions": [],
                "certificate": None, "reason": "interrupted",
                "metrics": dict(metrics, provider_seconds=time.perf_counter()-started)}
    except Exception as exc:
        if exc.__class__.__name__ in ("_Stop", "_Deadline"):
            return {"method": METHOD, "status": "incomplete", "complete": False,
                    "decision_complete": False, "uniqueness": "unknown", "solutions": [],
                    "certificate": None, "reason": "deadline_or_interruption",
                    "metrics": dict(metrics, provider_seconds=time.perf_counter()-started)}
        return {"method": METHOD, "status": "runtime_error", "complete": False,
                "decision_complete": False, "uniqueness": "unknown", "solutions": [],
                "certificate": None, "error": repr(exc),
                "metrics": dict(metrics, provider_seconds=time.perf_counter()-started)}
    components = sorted((sorted(c) for c in components), key=lambda c: c[0])
    edges = [{"symbols": sorted(e["symbols"]), "witness": e["witness"]} for e in raw_edges]
    metrics.update(must_link_edges=len(edges), contracted_components=len(components))
    if len(components) == 1:
        cert = {"kind": "no_nontrivial_bipartition", "obstruction": "connected_must_link_graph",
                "alphabet": alphabet, "components": components, "must_link_edges": edges}
        check = verify_certificate(data, cert)
        if not check["valid"]:
            return {"method": METHOD, "status": "runtime_error", "complete": False,
                    "decision_complete": False, "uniqueness": "unknown", "solutions": [],
                    "certificate": None, "error": "connected certificate replay failed: " + str(check),
                    "metrics": metrics}
        return {"method": METHOD, "status": "not_decomposable", "complete": True,
                "decision_complete": True, "uniqueness": "none",
                "uniqueness_scope": "sample_compatible_nontrivial_two_block_partitions",
                "solutions": [], "certificate": cert, "certificate_check": check,
                "assumptions": ["exact labels", "known alphabet", "two nonempty disjoint blocks",
                                "unrestricted regular local factors"],
                "metrics": dict(metrics, provider_seconds=time.perf_counter()-started)}
    rejections, solutions, exhausted = [], [], False
    total_cuts = (1 << (len(components)-1)) - 1
    try:
        for mask in _canonical_masks(len(components)):
            _check(deadline)
            metrics["canonical_cuts_checked"] += 1
            solution, collision = _compatibility(_blocks_from_mask(components, mask),
                                                  positive, negative, deadline)
            if solution is not None:
                solutions.append(solution)
                if max_solutions is not None and len(solutions) >= max_solutions:
                    exhausted = metrics["canonical_cuts_checked"] == total_cuts
                    break
            else:
                rejections.append({"canonical_left_atom_mask": mask, "collision": collision})
        else:
            exhausted = True
    except KeyboardInterrupt:
        exhausted = False
    except Exception as exc:
        if exc.__class__.__name__ not in ("_Stop", "_Deadline"):
            return {"method": METHOD, "status": "runtime_error", "complete": False,
                    "decision_complete": False, "uniqueness": "unknown", "solutions": solutions,
                    "certificate": None, "error": repr(exc),
                    "metrics": dict(metrics, provider_seconds=time.perf_counter()-started)}
        exhausted = False
    cert = None
    if exhausted and not solutions:
        cert = {"kind": "no_nontrivial_bipartition", "obstruction": "complete_cut_collision_cover",
                "alphabet": alphabet, "components": components, "must_link_edges": edges,
                "cut_rejections": rejections}
        check = verify_certificate(data, cert)
        if not check["valid"]:
            return {"method": METHOD, "status": "runtime_error", "complete": False,
                    "decision_complete": False, "uniqueness": "unknown", "solutions": [],
                    "certificate": None, "error": "cut-cover replay failed: " + str(check),
                    "metrics": metrics}
    status = "incomplete" if not exhausted and not solutions else ("found" if solutions else "not_decomposable")
    uniqueness = ("ambiguous" if len(solutions) >= 2 else
                  "unique" if exhausted and len(solutions) == 1 else
                  "none" if exhausted else "unknown")
    return {"method": METHOD, "model_class": "general_regular_product", "status": status,
            "complete": exhausted, "enumeration_complete": exhausted,
            "decision_complete": bool(solutions) or exhausted, "uniqueness": uniqueness,
            "uniqueness_scope": "sample_compatible_nontrivial_two_block_partitions",
            "solutions": solutions, "certificate": cert,
            "certificate_check": verify_certificate(data, cert) if cert is not None else None,
            "assumptions": ["exact labels", "known alphabet", "two nonempty disjoint blocks",
                            "unrestricted regular local factors"],
            "max_solutions": max_solutions,
            "metrics": dict(metrics, provider_seconds=time.perf_counter()-started)}


