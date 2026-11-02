"""Exact no-K sample-compatible ownership analysis (C010 candidate)."""
from __future__ import annotations

from functools import lru_cache
from itertools import combinations
import math
import time

METHOD = "C010-unrestricted-ownership-v1"


class _Stop(Exception):
    pass


def _check(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise _Stop


def _validate(data):
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    if "allowed_k" in data or "k" in data:
        raise ValueError("C010 accepts no external k constraint")
    alphabet = data.get("alphabet")
    if (not isinstance(alphabet, list) or not alphabet
            or any(not isinstance(a, str) or len(a) != 1 for a in alphabet)
            or len(set(alphabet)) != len(alphabet)):
        raise ValueError("alphabet must be a nonempty list of distinct one-character strings")
    alphabet = sorted(alphabet)
    symbols = set(alphabet)
    labels = []
    for name in ("positive", "negative"):
        words = data.get(name)
        if not isinstance(words, list) or any(not isinstance(w, str) for w in words):
            raise ValueError(f"{name} must be a list of strings")
        if any(set(w) - symbols for w in words):
            raise ValueError(f"{name} contains symbols outside alphabet")
        labels.append(sorted(set(words)))
    positive, negative = labels
    if set(positive) & set(negative):
        raise ValueError("contradictory_labels")
    return alphabet, positive, negative


def _project(word, symbols, deadline=None):
    out = []
    for index, ch in enumerate(word):
        if index % 1024 == 0:
            _check(deadline)
        if ch in symbols:
            out.append(ch)
    return "".join(out)


def _stirling_bell(r):
    row = [1] + [0] * r
    result = {0: 1}
    for n in range(1, r + 1):
        nxt = [0] * (r + 1)
        for k in range(1, n + 1):
            nxt[k] = row[k - 1] + k * row[k]
        row = nxt
        result[n] = sum(row)
    return result


def _partition_from_masks(masks, atoms):
    return [sorted(ch for i in range(len(atoms)) if mask >> i & 1 for ch in atoms[i])
            for mask in masks]


def _witness(partition, positive, negative, deadline=None):
    blocks = [set(b) for b in partition]
    languages = [{_project(p, b, deadline) for p in positive} for b in blocks]
    negative_witnesses = []
    for word in negative:
        projections = [_project(word, b, deadline) for b in blocks]
        rejected = [i for i, value in enumerate(projections) if value not in languages[i]]
        if not rejected:
            raise AssertionError("incompatible witness partition")
        negative_witnesses.append({"word": word, "projections": projections,
                                   "rejected_by_blocks": rejected})
    return {"partition": partition,
            "positive_projection_languages": [sorted(x) for x in languages],
            "negative_witnesses": negative_witnesses}


def solve(data, *, deadline=None, enumerate_partitions=False):
    started = time.perf_counter()
    metrics = {"swap_pairs_tested": 0, "swap_edges": 0, "atoms": 0,
               "atom_projection_checks": 0, "block_masks_computed": 0,
               "dp_states": 0, "dp_branches": 0,
               "enumerated_partitions": 0, "preprocessing_seconds": 0.0,
               "search_seconds": 0.0, "provider_seconds": 0.0}
    try:
        alphabet, positive, negative = _validate(data)
    except (ValueError, TypeError) as exc:
        return {"method": METHOD, "status": "invalid_input", "complete": True,
                "error": str(exc), "metrics": metrics}
    if deadline is not None and (isinstance(deadline, bool)
            or not isinstance(deadline, (int, float)) or not math.isfinite(deadline)):
        return {"method": METHOD, "status": "invalid_input", "complete": True,
                "error": "deadline must be a finite absolute perf_counter value or None",
                "metrics": metrics}
    if not isinstance(enumerate_partitions, bool):
        return {"method": METHOD, "status": "invalid_input", "complete": True,
                "error": "enumerate_partitions must be boolean", "metrics": metrics}

    m = len(alphabet)
    index = {ch: i for i, ch in enumerate(alphabet)}
    parent = list(range(m))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        x, y = find(x), find(y)
        if x != y:
            parent[max(x, y)] = min(x, y)

    edge_witnesses = []
    prep_start = time.perf_counter()
    for p in positive:
        for n in negative:
            metrics["swap_pairs_tested"] += 1
            if len(p) != len(n):
                continue
            mismatch = -1
            for pos, (a, b) in enumerate(zip(p, n)):
                if a == b:
                    continue
                if mismatch < 0:
                    mismatch = pos
                elif pos != mismatch + 1:
                    mismatch = -2
                    break
            if mismatch < 0 or mismatch + 1 >= len(p):
                continue
            i = mismatch
            if p[i] == n[i + 1] and p[i + 1] == n[i]:
                a, b = p[i], p[i + 1]
                if a != b:
                    union(index[a], index[b])
                    edge_witnesses.append({"positive": p, "negative": n,
                                           "positions": [i, i + 1],
                                           "symbols": [a, b]})

    groups = {}
    for i, ch in enumerate(alphabet):
        groups.setdefault(find(i), []).append(ch)
    atoms = sorted((tuple(v) for v in groups.values()), key=lambda v: v[0])
    r = len(atoms)
    metrics["swap_edges"] = len(edge_witnesses)
    metrics["atoms"] = r
    atom_sets = [set(a) for a in atoms]
    all_neg = (1 << len(negative)) - 1

    def atom_partition_feasible():
        langs = [{_project(p, block, deadline) for p in positive} for block in atom_sets]
        for ni, word in enumerate(negative):
            _check(deadline)
            projections = [_project(word, block, deadline) for block in atom_sets]
            metrics["atom_projection_checks"] += 1
            if not any(value not in langs[i] for i, value in enumerate(projections)):
                return False
        return True

    try:
        _check(deadline)
        atom_ok = atom_partition_feasible()
        metrics["preprocessing_seconds"] = time.perf_counter() - prep_start
        bell = _stirling_bell(r)
        if atom_ok:
            total = bell[r]
            count_by_k = {str(k): (bell[k] if k <= r else 0) for k in range(1, m + 1)}
            enumerated = None
            if enumerate_partitions:
                enumerated = []
                def grow(pos, masks):
                    _check(deadline)
                    if pos == r:
                        part = _partition_from_masks(masks, atoms)
                        enumerated.append(_witness(part, positive, negative, deadline))
                        return
                    bit = 1 << pos
                    for bi in range(len(masks)):
                        masks[bi] |= bit
                        grow(pos + 1, masks)
                        masks[bi] ^= bit
                    masks.append(bit)
                    grow(pos + 1, masks)
                    masks.pop()
                grow(0, [])
                metrics["enumerated_partitions"] = len(enumerated)
                if len(enumerated) != total:
                    raise AssertionError("coarsening enumeration disagrees with Bell count")
            pair_rows = []
            pair_same = bell[r - 1] if r > 1 else 1
            for i, a in enumerate(alphabet):
                for b in alphabet[i + 1:]:
                    same_atom = find(index[a]) == find(index[b])
                    same = total if same_atom else pair_same
                    diff = total - same
                    pair_rows.append({"symbols": [a, b],
                                      "relation": "forced_same" if same_atom else "ambiguous",
                                      "same_partition_count": same,
                                      "different_partition_count": diff,
                                      "same_partition_witness": [[x for x in alphabet]] if same_atom else
                                          _partition_from_masks([(1 << r) - 1], atoms),
                                      "different_partition_witness": None if same_atom else
                                          _partition_from_masks([1 << j for j in range(r)], atoms)})
            representative = _partition_from_masks([(1 << r) - 1], atoms)
            metrics["provider_seconds"] = time.perf_counter() - started
            return {"method": METHOD, "status": "identified_unique_partition" if total == 1 else "partial_ownership_identification",
                    "complete": True, "alphabet": alphabet, "atom_partition": [list(a) for a in atoms],
                    "swap_edge_witnesses": edge_witnesses, "atom_projection_feasible": True,
                    "partition_count": total, "partition_count_by_k": count_by_k,
                    "k_max_upper_bound": r, "pair_relations": pair_rows,
                    "representative": _witness(representative, positive, negative, deadline),
                    "enumerated_partitions": enumerated, "metrics": metrics}

        # Atom blocks fail the direct test; search all coarsenings exactly.
        search_start = time.perf_counter()
        pair_list = list(combinations(range(r), 2))
        pair_index = {pair: i for i, pair in enumerate(pair_list)}
        pair_count = len(pair_list)
        zero_pairs = (0,) * pair_count
        full_atoms = (1 << r) - 1

        @lru_cache(maxsize=None)
        def reject(blockmask):
            _check(deadline)
            symbols = set(ch for i, atom in enumerate(atoms) if blockmask >> i & 1 for ch in atom)
            positives = {_project(p, symbols, deadline) for p in positive}
            mask = 0
            for ni, word in enumerate(negative):
                if _project(word, symbols, deadline) not in positives:
                    mask |= 1 << ni
            metrics["block_masks_computed"] += 1
            return mask

        @lru_cache(maxsize=None)
        def dp(rem, covered, left):
            _check(deadline)
            metrics["dp_states"] += 1
            if (covered | reject(rem)) != all_neg:
                return 0, zero_pairs
            if rem == 0:
                return (1, zero_pairs) if left == 0 else (0, zero_pairs)
            if left <= 0 or left > rem.bit_count():
                return 0, zero_pairs
            anchor = rem & -rem
            total = 0
            same = [0] * pair_count
            sub = rem
            while sub:
                if sub & anchor:
                    metrics["dp_branches"] += 1
                    child_count, child_same = dp(rem ^ sub, covered | reject(sub), left - 1)
                    total += child_count
                    for pi, value in enumerate(child_same):
                        same[pi] += value
                    if child_count:
                        members = [i for i in range(r) if sub >> i & 1]
                        for ii, jj in combinations(members, 2):
                            same[pair_index[(ii, jj)]] += child_count
                sub = (sub - 1) & rem
            return total, tuple(same)

        totals = [0] * (m + 1)
        same_atoms = [0] * pair_count
        for k in range(1, r + 1):
            count, same = dp(full_atoms, 0, k)
            totals[k] = count
            for pi, value in enumerate(same):
                same_atoms[pi] += value
        total = sum(totals)
        metrics["search_seconds"] = time.perf_counter() - search_start
        if total == 0:
            return {"method": METHOD, "status": "model_inconsistent", "complete": True,
                    "alphabet": alphabet, "atom_partition": [list(a) for a in atoms],
                    "swap_edge_witnesses": edge_witnesses, "atom_projection_feasible": False,
                    "partition_count": 0, "partition_count_by_k": {str(k): totals[k] for k in range(1, m + 1)},
                    "k_max_upper_bound": r, "pair_relations": None, "representative": None,
                    "enumerated_partitions": None, "metrics": metrics}

        def find_partition(k, atom_i=None, atom_j=None, want_same=None):
            def rec(rem, covered, left, decided, prefix):
                _check(deadline)
                if rem == 0:
                    return prefix if covered == all_neg and left == 0 and decided else None
                anchor = rem & -rem
                sub = rem
                while sub:
                    if sub & anchor:
                        in_i = atom_i is not None and bool(sub >> atom_i & 1)
                        in_j = atom_j is not None and bool(sub >> atom_j & 1)
                        now = decided
                        if atom_i is not None and not decided:
                            if want_same and in_i != in_j:
                                sub = (sub - 1) & rem
                                continue
                            if not want_same and in_i and in_j:
                                sub = (sub - 1) & rem
                                continue
                            if (want_same and in_i and in_j) or (not want_same and in_i != in_j):
                                now = True
                        new_rem = rem ^ sub
                        new_cov = covered | reject(sub)
                        new_left = left - 1
                        if dp(new_rem, new_cov, new_left)[0]:
                            found = rec(new_rem, new_cov, new_left, now, prefix + [sub])
                            if found is not None:
                                return found
                    sub = (sub - 1) & rem
                return None
            masks = rec(full_atoms, 0, k, atom_i is None, [])
            return None if masks is None else _partition_from_masks(masks, atoms)

        rep = None
        for k in range(1, r + 1):
            if totals[k]:
                rep = find_partition(k)
                break
        pair_rows = []
        atom_for_symbol = {ch: ai for ai, atom in enumerate(atoms) for ch in atom}
        for i, a in enumerate(alphabet):
            for b in alphabet[i + 1:]:
                ai, aj = atom_for_symbol[a], atom_for_symbol[b]
                if ai == aj:
                    same, diff = total, 0
                    same_w = rep
                    diff_w = None
                    relation = "forced_same"
                else:
                    same = same_atoms[pair_index[tuple(sorted((ai, aj)))]]
                    diff = total - same
                    same_w = diff_w = None
                    for k in range(1, r + 1):
                        if totals[k] and same and same_w is None:
                            same_w = find_partition(k, ai, aj, True)
                        if totals[k] and diff and diff_w is None:
                            diff_w = find_partition(k, ai, aj, False)
                    relation = "ambiguous" if same and diff else "forced_same" if same else "forced_different"
                pair_rows.append({"symbols": [a, b], "relation": relation,
                                  "same_partition_count": same, "different_partition_count": diff,
                                  "same_partition_witness": same_w,
                                  "different_partition_witness": diff_w})
        if any(row["relation"] == "forced_different" for row in pair_rows):
            raise AssertionError("unrestricted consistent model cannot force different")
        enumerated = None
        if enumerate_partitions:
            enumerated = []
            for k in range(1, r + 1):
                def walk(rem, covered, left, prefix):
                    _check(deadline)
                    if rem == 0:
                        if covered == all_neg and left == 0:
                            p = _partition_from_masks(prefix, atoms)
                            enumerated.append(_witness(p, positive, negative, deadline))
                        return
                    anchor = rem & -rem
                    sub = rem
                    while sub:
                        if sub & anchor:
                            nr = rem ^ sub
                            nc = covered | reject(sub)
                            if dp(nr, nc, left - 1)[0]:
                                walk(nr, nc, left - 1, prefix + [sub])
                        sub = (sub - 1) & rem
                if totals[k]:
                    walk(full_atoms, 0, k, [])
            metrics["enumerated_partitions"] = len(enumerated)
            if len(enumerated) != total:
                raise AssertionError("enumeration count disagrees with DP")
        metrics["provider_seconds"] = time.perf_counter() - started
        return {"method": METHOD, "status": "identified_unique_partition" if total == 1 else "partial_ownership_identification",
                "complete": True, "alphabet": alphabet, "atom_partition": [list(a) for a in atoms],
                "swap_edge_witnesses": edge_witnesses, "atom_projection_feasible": False,
                "partition_count": total,
                "partition_count_by_k": {str(k): totals[k] for k in range(1, m + 1)},
                "k_max_upper_bound": r, "pair_relations": pair_rows,
                "representative": _witness(rep, positive, negative, deadline),
                "enumerated_partitions": enumerated, "metrics": metrics}
    except (KeyboardInterrupt, _Stop):
        metrics["provider_seconds"] = time.perf_counter() - started
        return {"method": METHOD, "status": "unknown", "complete": False,
                "reason": "deadline_or_interruption", "partition_count": None,
                "partition_count_by_k": None, "pair_relations": None,
                "representative": None, "enumerated_partitions": None,
                "metrics": metrics}
