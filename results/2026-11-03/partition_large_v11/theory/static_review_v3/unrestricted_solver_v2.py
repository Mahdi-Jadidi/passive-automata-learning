"""Exact no-K sample-compatible ownership analysis (C011 candidate)."""
from __future__ import annotations

from collections import OrderedDict
from functools import lru_cache
from itertools import combinations
import math
import time

METHOD = "C011-rle-binary-interval-v1"
FINGERPRINT_BASE = 1_000_003
FINGERPRINT_MASK = (1 << 64) - 1
PROJECTION_CACHE_LIMIT = 4096


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


def _fingerprint_range(prefix_hash, powers, start, end):
    """Deterministic 64-bit polynomial fingerprint; exact checks prove equality.

    Auditors may monkeypatch this helper to return a constant and force all
    fingerprint keys to collide. The index must remain complete in that case.
    """
    return (prefix_hash[end] - prefix_hash[start] * powers[end - start]) & FINGERPRINT_MASK


def _rolling_data(word, deadline, counters):
    prefix = [0] * (len(word) + 1)
    powers = [1] * (len(word) + 1)
    for i, ch in enumerate(word):
        if i % 1024 == 0:
            _check(deadline)
        prefix[i + 1] = (prefix[i] * FINGERPRINT_BASE + ord(ch) + 1) & FINGERPRINT_MASK
        powers[i + 1] = (powers[i] * FINGERPRINT_BASE) & FINGERPRINT_MASK
    counters["fingerprint_characters"] += len(word)
    return prefix, powers


class _ProjectionCache:
    """Small exact LRU; prevents a cache growing with all masks × all words."""
    def __init__(self, capacity, metrics):
        self.capacity = capacity
        self.metrics = metrics
        self.values = OrderedDict()

    def project(self, word, symbols, deadline=None):
        _check(deadline)
        canonical = tuple(sorted(symbols))
        if not canonical:
            return ""
        key = (word, canonical)
        if key in self.values:
            self.metrics["projection_cache_hits"] += 1
            self.values.move_to_end(key)
            return self.values[key]
        self.metrics["projection_cache_misses"] += 1
        allowed = set(canonical)
        out = []
        for i, ch in enumerate(word):
            if i % 1024 == 0:
                _check(deadline)
            self.metrics["projection_characters_scanned"] += 1
            if ch in allowed:
                out.append(ch)
        value = "".join(out)
        if self.capacity:
            self.values[key] = value
            if len(self.values) > self.capacity:
                self.values.popitem(last=False)
                self.metrics["projection_cache_evictions"] += 1
        return value


def _stirling_bell(r, deadline=None):
    row = [1] + [0] * r
    result = {0: 1}
    stirling = {0: [1]}
    for n in range(1, r + 1):
        _check(deadline)
        nxt = [0] * (r + 1)
        for k in range(1, n + 1):
            _check(deadline)
            nxt[k] = row[k - 1] + k * row[k]
        row = nxt
        stirling[n] = row[:n + 1]
        result[n] = sum(row)
    return result, stirling


def _partition_from_masks(masks, atoms, deadline=None):
    partition = []
    for mask in masks:
        _check(deadline)
        block = []
        for i in range(len(atoms)):
            _check(deadline)
            if mask >> i & 1:
                block.extend(atoms[i])
        partition.append(sorted(block))
    return partition


def _partition_key(partition, deadline=None):
    canonical = []
    for block in partition:
        _check(deadline)
        canonical.append(tuple(block))
    return tuple(canonical)


def _context_text(word, start, end, deadline, metrics):
    chars = []
    for i in range(start, end):
        if (i - start) % 1024 == 0:
            _check(deadline)
        metrics["certificate_context_characters"] += 1
        chars.append(word[i])
    return "".join(chars)


def _interval_key(word, window, rolling, deadline):
    lo, hi, x, y, cx, cy = window
    prefix, powers = rolling
    return (len(word), lo, hi, x, y, cx, cy,
            _fingerprint_range(prefix, powers, 0, lo),
            _fingerprint_range(prefix, powers, hi, len(word)))


def _extract_contractions(alphabet, positive, negative, deadline, metrics):
    """Discover sound binary-interval and legacy swap certificates by index."""
    m = len(alphabet)
    index = {ch: i for i, ch in enumerate(alphabet)}
    parent = list(range(m))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union_pair(x, y):
        rx, ry = find(index[x]), find(index[y])
        if rx == ry:
            return False
        parent[max(rx, ry)] = min(rx, ry)
        metrics["successful_unions"] += 1
        return True

    positive_index = {}
    swap_index = {}
    for word in positive:
        _check(deadline)
        rolling = _rolling_data(word, deadline, metrics)
        windows, runs = _rle_windows(word, deadline, metrics)
        for window in windows:
            _check(deadline)
            key = _interval_key(word, window, rolling, deadline)
            positive_index.setdefault(key, []).append((word, window))
            metrics["positive_interval_records"] += 1
        for i in range(len(runs) - 1):
            _check(deadline)
            lo = runs[i][2] - 1
            hi = lo + 2
            x, y = sorted((word[lo], word[lo + 1]))
            window = (lo, hi, x, y, 1, 1)
            key = _interval_key(word, window, rolling, deadline)
            swap_index.setdefault(key, []).append((word, lo, x, y))
            metrics["legacy_swap_interval_records"] += 1

    metrics["fingerprint_buckets"] = len(positive_index)
    binary_certificates = []
    swap_witnesses = []
    seen_swap_witnesses = set()
    certified_pairs = set()
    for word in negative:
        _check(deadline)
        rolling = _rolling_data(word, deadline, metrics)
        windows, runs = _rle_windows(word, deadline, metrics)
        for window in windows:
            _check(deadline)
            lo, hi, x, y, cx, cy = window
            pair = (x, y)
            if pair in certified_pairs:
                continue
            key = _interval_key(word, window, rolling, deadline)
            bucket = positive_index.get(key, ())
            for p, p_window in bucket:
                metrics["interval_index_candidate_checks"] += 1
                metrics["exact_context_checks"] += 1
                if not _same_context(p, word, lo, hi, deadline, metrics):
                    metrics["fingerprint_collision_contexts"] += 1
                    continue
                if p_window != window or not _verify_interval(
                        p, word, lo, hi, x, y, cx, cy, deadline, metrics):
                    metrics["exact_interval_rejections"] += 1
                    continue
                # Contradictory labels were rejected by _validate; p != n is
                # checked by _verify_interval. This is a replayable T1 edge.
                certified_pairs.add(pair)
                union_pair(x, y)
                left = _context_text(p, 0, lo, deadline, metrics)
                right = _context_text(p, hi, len(p), deadline, metrics)
                binary_certificates.append({
                    "type": "binary_anagram_interval",
                    "positive": p,
                    "negative": word,
                    "interval": [lo, hi],
                    "left": left,
                    "right": right,
                    "symbols": [x, y],
                    "counts": {x: cx, y: cy},
                })
                metrics["binary_interval_certificates"] += 1
                break

        # Preserve the legacy adjacent-swap certificate field using a
        # length-two view of each RLE transition; no swapped string is built.
        for i in range(len(runs) - 1):
            _check(deadline)
            lo = runs[i][2] - 1
            hi = lo + 2
            x, y = sorted((word[lo], word[lo + 1]))
            window = (lo, hi, x, y, 1, 1)
            key = _interval_key(word, window, rolling, deadline)
            for p, _, _, _ in swap_index.get(key, ()):
                metrics["swap_pairs_tested"] += 1
                metrics["exact_context_checks"] += 1
                if not _same_context(p, word, lo, hi, deadline, metrics):
                    metrics["fingerprint_collision_contexts"] += 1
                    continue
                if p[lo] != word[lo + 1] or p[lo + 1] != word[lo] or p[lo] == p[lo + 1]:
                    metrics["exact_interval_rejections"] += 1
                    continue
                witness_key = (p, word, lo)
                if witness_key not in seen_swap_witnesses:
                    seen_swap_witnesses.add(witness_key)
                    swap_witnesses.append({"positive": p, "negative": word,
                                           "positions": [lo, lo + 1],
                                           "symbols": [p[lo], p[lo + 1]]})
                union_pair(p[lo], p[lo + 1])
                metrics["swap_edges"] += 1
                break

    groups = {}
    for i, ch in enumerate(alphabet):
        _check(deadline)
        groups.setdefault(find(i), []).append(ch)
    atoms = sorted((tuple(v) for v in groups.values()), key=lambda v: v[0])
    atom_for_symbol = {ch: ai for ai, atom in enumerate(atoms) for ch in atom}
    metrics["atoms"] = len(atoms)
    for bucket in positive_index.values():
        _check(deadline)
        metrics["non_singleton_fingerprint_buckets"] += len(bucket) > 1
    return atoms, atom_for_symbol, swap_witnesses, binary_certificates


def _witness(partition, positive, negative, projection_cache, deadline=None):
    blocks = []
    for b in partition:
        _check(deadline)
        blocks.append(set(b))
    languages = []
    for block in blocks:
        _check(deadline)
        language = set()
        for p in positive:
            _check(deadline)
            language.add(projection_cache.project(p, block, deadline))
        languages.append(language)
    negative_witnesses = []
    for word in negative:
        _check(deadline)
        projections = []
        for b in blocks:
            _check(deadline)
            projections.append(projection_cache.project(word, b, deadline))
        rejected = [i for i, value in enumerate(projections) if value not in languages[i]]
        if not rejected:
            raise AssertionError("incompatible witness partition")
        negative_witnesses.append({"word": word, "projections": projections,
                                   "rejected_by_blocks": rejected})
    return {"partition": partition,
            "positive_projection_languages": [sorted(x) for x in languages],
            "negative_witnesses": negative_witnesses}


def _rle_windows(word, deadline, metrics):
    """Enumerate maximal two-symbol intervals by equal adjacent RLE labels."""
    runs = []
    start = 0
    for i, ch in enumerate(word):
        if i % 1024 == 0:
            _check(deadline)
        if i and ch != word[i - 1]:
            runs.append((word[i - 1], start, i))
            start = i
    if word:
        runs.append((word[-1], start, len(word)))
    metrics["rle_runs"] += len(runs)
    if len(runs) < 2:
        return [], runs

    labels = []
    for i in range(len(runs) - 1):
        _check(deadline)
        labels.append(tuple(sorted((runs[i][0], runs[i + 1][0]))))
    windows = []
    i = 0
    while i < len(labels):
        _check(deadline)
        j = i
        while j + 1 < len(labels) and labels[j + 1] == labels[i]:
            _check(deadline)
            j += 1
        x, y = labels[i]
        lo, hi = runs[i][1], runs[j + 1][2]
        cx = cy = 0
        for ch, run_start, run_end in runs[i:j + 2]:
            _check(deadline)
            if ch == x:
                cx += run_end - run_start
            else:
                cy += run_end - run_start
        windows.append((lo, hi, x, y, cx, cy))
        i = j + 1
    metrics["binary_windows"] += len(windows)
    for l, h, *_ in windows:
        _check(deadline)
        metrics["binary_window_characters"] += h - l
    return windows, runs


def _same_context(left, right, lo, hi, deadline, metrics):
    """Exact prefix/suffix comparison without allocating long string slices."""
    if len(left) != len(right):
        return False
    for i in range(lo):
        if i % 1024 == 0:
            _check(deadline)
        metrics["exact_context_characters"] += 1
        if left[i] != right[i]:
            return False
    for i in range(hi, len(left)):
        if (i - hi) % 1024 == 0:
            _check(deadline)
        metrics["exact_context_characters"] += 1
        if left[i] != right[i]:
            return False
    return True


def _verify_interval(p, n, lo, hi, x, y, cx, cy, deadline, metrics):
    if p == n or len(p) != len(n):
        return False
    px = py = nx = ny = 0
    for i in range(lo, hi):
        if (i - lo) % 1024 == 0:
            _check(deadline)
        metrics["interval_characters_verified"] += 1
        a, b = p[i], n[i]
        if a not in (x, y) or b not in (x, y):
            return False
        px += a == x
        py += a == y
        nx += b == x
        ny += b == y
    return px == nx == cx and py == ny == cy


def solve(data, *, deadline=None, enumerate_partitions=False):
    started = time.perf_counter()
    metrics = {"swap_pairs_tested": 0, "swap_edges": 0, "atoms": 0,
               "atom_projection_checks": 0, "block_masks_computed": 0,
               "dp_states": 0, "dp_branches": 0,
               "enumerated_partitions": 0, "preprocessing_seconds": 0.0,
               "search_seconds": 0.0, "provider_seconds": 0.0,
               "total_input_characters": 0, "fingerprint_characters": 0,
               "rle_runs": 0, "binary_windows": 0,
               "binary_window_characters": 0, "positive_interval_records": 0,
               "legacy_swap_interval_records": 0, "fingerprint_buckets": 0,
               "non_singleton_fingerprint_buckets": 0,
               "interval_index_candidate_checks": 0,
               "exact_context_checks": 0, "exact_context_characters": 0,
               "fingerprint_collision_contexts": 0,
               "interval_characters_verified": 0, "exact_interval_rejections": 0,
               "binary_interval_certificates": 0, "certificate_context_characters": 0,
               "successful_unions": 0,
               "projection_cache_hits": 0, "projection_cache_misses": 0,
               "projection_cache_evictions": 0, "projection_characters_scanned": 0,
               "partition_witness_cache_hits": 0, "partition_witness_cache_misses": 0,
               "projection_witness_cache_hits": 0, "projection_witness_cache_misses": 0}
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
    projection_cache = _ProjectionCache(PROJECTION_CACHE_LIMIT, metrics)
    partition_pool = {}
    projection_witness_pool = {}

    def intern_partition(partition):
        canonical = _partition_key(partition, deadline)
        if canonical in partition_pool:
            metrics["partition_witness_cache_hits"] += 1
            return partition_pool[canonical]
        metrics["partition_witness_cache_misses"] += 1
        partition_pool[canonical] = partition
        return partition

    def get_projection_witness(partition):
        key = _partition_key(partition, deadline)
        if key in projection_witness_pool:
            metrics["projection_witness_cache_hits"] += 1
            return projection_witness_pool[key]
        metrics["projection_witness_cache_misses"] += 1
        payload = _witness(partition, positive, negative, projection_cache, deadline)
        projection_witness_pool[key] = payload
        return payload

    prep_start = time.perf_counter()
    try:
        _check(deadline)
        for word in positive:
            _check(deadline)
            metrics["total_input_characters"] += len(word)
        for word in negative:
            _check(deadline)
            metrics["total_input_characters"] += len(word)
        atoms, atom_for_symbol, edge_witnesses, interval_certificates = _extract_contractions(
            alphabet, positive, negative, deadline, metrics)
    except (KeyboardInterrupt, _Stop):
        metrics["provider_seconds"] = time.perf_counter() - started
        return {"method": METHOD, "status": "incomplete", "complete": False,
                "reason": "deadline_or_interruption", "partition_count": None,
                "partition_count_by_k": None, "pair_relations": None,
                "representative": None, "enumerated_partitions": None,
                "metrics": metrics}
    r = len(atoms)
    metrics["swap_edges"] = len(edge_witnesses)
    metrics["atoms"] = r
    atom_sets = []
    all_neg = (1 << len(negative)) - 1

    def atom_partition_feasible():
        langs = []
        for block in atom_sets:
            _check(deadline)
            language = set()
            for p in positive:
                _check(deadline)
                language.add(projection_cache.project(p, block, deadline))
            langs.append(language)
        for ni, word in enumerate(negative):
            _check(deadline)
            projections = []
            for block in atom_sets:
                _check(deadline)
                projections.append(projection_cache.project(word, block, deadline))
            metrics["atom_projection_checks"] += 1
            if not any(value not in langs[i] for i, value in enumerate(projections)):
                return False
        return True

    try:
        _check(deadline)
        for atom in atoms:
            _check(deadline)
            atom_sets.append(set(atom))
        atom_ok = atom_partition_feasible()
        metrics["preprocessing_seconds"] = time.perf_counter() - prep_start
        bell, stirling = _stirling_bell(r, deadline)
        if atom_ok:
            total = bell[r]
            count_by_k = {}
            for k in range(1, m + 1):
                _check(deadline)
                count_by_k[str(k)] = stirling[r][k] if k <= r else 0
            enumerated = None
            if enumerate_partitions:
                enumerated = []
                def grow(pos, masks):
                    _check(deadline)
                    if pos == r:
                        part = _partition_from_masks(masks, atoms, deadline)
                        enumerated.append(get_projection_witness(part))
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
            one_block_witness = intern_partition([list(alphabet)])
            atom_masks = []
            for j in range(r):
                _check(deadline)
                atom_masks.append(1 << j)
            atom_partition_witness = intern_partition(_partition_from_masks(atom_masks, atoms, deadline))
            for i, a in enumerate(alphabet):
                _check(deadline)
                for b in alphabet[i + 1:]:
                    _check(deadline)
                    same_atom = atom_for_symbol[a] == atom_for_symbol[b]
                    same = total if same_atom else pair_same
                    diff = total - same
                    pair_rows.append({"symbols": [a, b],
                                      "relation": "forced_same" if same_atom else "ambiguous",
                                      "same_partition_count": same,
                                      "different_partition_count": diff,
                                      "same_partition_witness": one_block_witness,
                                      "different_partition_witness": None if same_atom else atom_partition_witness})
            representative = intern_partition(_partition_from_masks([(1 << r) - 1], atoms, deadline))
            metrics["provider_seconds"] = time.perf_counter() - started
            return {"method": METHOD, "status": "identified_unique_partition" if total == 1 else "partial_ownership_identification",
                    "complete": True, "alphabet": alphabet, "atom_partition": [list(a) for a in atoms],
                    "swap_edge_witnesses": edge_witnesses, "atom_projection_feasible": True,
                    "binary_interval_must_link_certificates": interval_certificates,
                    "partition_count": total, "partition_count_by_k": count_by_k,
                    "k_max_upper_bound": r, "k_max_compatible": r, "pair_relations": pair_rows,
                    "representative": get_projection_witness(representative),
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
            symbols = set()
            for i, atom in enumerate(atoms):
                _check(deadline)
                if blockmask >> i & 1:
                    symbols.update(atom)
            positives = set()
            for p in positive:
                _check(deadline)
                positives.add(projection_cache.project(p, symbols, deadline))
            mask = 0
            for ni, word in enumerate(negative):
                _check(deadline)
                if projection_cache.project(word, symbols, deadline) not in positives:
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
                _check(deadline)
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
                    "binary_interval_must_link_certificates": interval_certificates,
                    "partition_count": 0, "partition_count_by_k": {str(k): totals[k] for k in range(1, m + 1)},
                    "k_max_upper_bound": r, "k_max_compatible": None, "pair_relations": None, "representative": None,
                    "enumerated_partitions": None, "metrics": metrics}

        def find_partition(k, atom_i=None, atom_j=None, want_same=None):
            def rec(rem, covered, left, decided, prefix):
                _check(deadline)
                if rem == 0:
                    return prefix if covered == all_neg and left == 0 and decided else None
                anchor = rem & -rem
                sub = rem
                while sub:
                    _check(deadline)
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
            return None if masks is None else _partition_from_masks(masks, atoms, deadline)

        rep = None
        for k in range(1, r + 1):
            if totals[k]:
                rep = find_partition(k)
                break
        pair_rows = []
        for i, a in enumerate(alphabet):
            _check(deadline)
            for b in alphabet[i + 1:]:
                _check(deadline)
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
                            same_w = intern_partition(find_partition(k, ai, aj, True))
                        if totals[k] and diff and diff_w is None:
                            diff_w = intern_partition(find_partition(k, ai, aj, False))
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
                            p = _partition_from_masks(prefix, atoms, deadline)
                            enumerated.append(get_projection_witness(intern_partition(p)))
                        return
                    anchor = rem & -rem
                    sub = rem
                    while sub:
                        _check(deadline)
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
                "binary_interval_must_link_certificates": interval_certificates,
                "partition_count": total,
                "partition_count_by_k": {str(k): totals[k] for k in range(1, m + 1)},
                "k_max_upper_bound": r, "k_max_compatible": max(k for k in range(1, r + 1) if totals[k]), "pair_relations": pair_rows,
                "representative": get_projection_witness(rep),
                "enumerated_partitions": enumerated, "metrics": metrics}
    except (KeyboardInterrupt, _Stop):
        metrics["provider_seconds"] = time.perf_counter() - started
        return {"method": METHOD, "status": "incomplete", "complete": False,
                "reason": "deadline_or_interruption", "partition_count": None,
                "partition_count_by_k": None, "pair_relations": None,
                "representative": None, "enumerated_partitions": None,
                "metrics": metrics}
