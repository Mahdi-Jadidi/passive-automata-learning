"""Exact known-k regular-factor partition search (stdlib only).

Positive complete words are accepted iff each block's local language contains
their projection. Negative words must have at least one projection outside the
corresponding finite positive projection language. A cap q bounds the number
of distinct positive projections in each block; q=None is unrestricted.
"""
from collections import defaultdict
import time

_HASH_MOD = 1_000_000_007
_HASH_BASE = 257


class _Deadline(Exception):
    pass


def _check(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise _Deadline


def _validate(data, k):
    if not isinstance(data, dict):
        raise ValueError("input must be an object")
    alphabet = data.get("alphabet")
    if (not isinstance(alphabet, list) or len(alphabet) < 2
            or any(not isinstance(a, str) or len(a) != 1 for a in alphabet)
            or len(set(alphabet)) != len(alphabet)):
        raise ValueError("alphabet must contain at least two distinct one-character strings")
    alphabet = sorted(alphabet)
    if k is None:
        k = data.get("k", 2)
    if isinstance(k, bool) or not isinstance(k, int) or not 2 <= k <= len(alphabet):
        raise ValueError("k must be an integer between 2 and alphabet size")
    samples = []
    sigma = set(alphabet)
    for key in ("positive", "negative"):
        words = data.get(key)
        if not isinstance(words, list) or any(not isinstance(w, str) for w in words):
            raise ValueError(key + " must be a list of strings")
        if any(set(w) - sigma for w in words):
            raise ValueError(key + " contains an unknown symbol")
        samples.append(sorted(set(words)))
    positive, negative = samples
    if set(positive) & set(negative):
        raise ValueError("contradictory labels")
    return alphabet, positive, negative, k


def _project(word, block, deadline=None):
    out = []
    for index, ch in enumerate(word):
        if index % 1024 == 0:
            _check(deadline)
        if ch in block:
            out.append(ch)
    return "".join(out)


def _hash_word(word, deadline=None):
    value = 0
    for index, ch in enumerate(word):
        if index % 1024 == 0:
            _check(deadline)
        value = (value * _HASH_BASE + ord(ch) + 1) % _HASH_MOD
    return value


def _prefix_hashes(word, deadline=None):
    prefix = [0]
    for index, ch in enumerate(word):
        if index % 1024 == 0:
            _check(deadline)
        prefix.append((prefix[-1] * _HASH_BASE + ord(ch) + 1) % _HASH_MOD)
    return prefix


def _components(alphabet, positive, negative, deadline):
    """Sound must-link pairs from swap and insertion-rescue witnesses."""
    pos, neg = set(positive), set(negative)
    edges = {}

    def add(a, b, witness):
        if a != b:
            edges.setdefault(tuple(sorted((a, b))), witness)

    negative_hashes = defaultdict(list)
    for word in negative:
        _check(deadline)
        negative_hashes[(len(word), _hash_word(word, deadline))].append(word)
    for word in positive:
        _check(deadline)
        powers = [1] * (len(word) + 1)
        for i in range(1, len(powers)):
            if i % 1024 == 0:
                _check(deadline)
            powers[i] = powers[i - 1] * _HASH_BASE % _HASH_MOD
        prefix_hash = _prefix_hashes(word, deadline)
        for i in range(len(word) - 1):
            _check(deadline)
            a, b = word[i], word[i + 1]
            if a != b:
                left_power = powers[len(word) - i - 1]
                right_power = powers[len(word) - i - 2]
                swapped_hash = (prefix_hash[-1] + (ord(b) - ord(a)) * left_power
                                + (ord(a) - ord(b)) * right_power) % _HASH_MOD
                for swapped in negative_hashes.get((len(word), swapped_hash), ()):
                    # Hashes only select candidates; exact string equality
                    # guards against collisions before adding an implication.
                    if (word[:i] + b + a + word[i + 2:]) == swapped:
                        add(a, b, {"rule": "adjacent_swap", "positive": word,
                                   "negative": swapped, "position": i})
    # Index positives by one-symbol deletions. A valid rescue consists of a
    # positive base x*y and another positive obtained by inserting b adjacent
    # to a in the negative x*a*y (the rescued positive has length |n|+1).
    deletion_index = defaultdict(list)
    for word in positive:
        _check(deadline)
        powers = [1] * (len(word) + 1)
        for i in range(1, len(powers)):
            if i % 1024 == 0:
                _check(deadline)
            powers[i] = powers[i - 1] * _HASH_BASE % _HASH_MOD
        prefix_hash = _prefix_hashes(word, deadline)
        for i, ch in enumerate(word):
            _check(deadline)
            suffix_length = len(word) - i - 1
            suffix_hash = (prefix_hash[-1] - prefix_hash[i + 1] * powers[suffix_length]) % _HASH_MOD
            deleted_hash = (prefix_hash[i] * powers[suffix_length] + suffix_hash) % _HASH_MOD
            deletion_index[(len(word) - 1, deleted_hash)].append((ch, i, word))
    for word in negative:
        _check(deadline)
        candidates = deletion_index.get((len(word), _hash_word(word, deadline)), ())
        by_position = defaultdict(list)
        for b, j, rescued in candidates:
            by_position[j].append((b, rescued))
        for i, a in enumerate(word):
            _check(deadline)
            base = word[:i] + word[i + 1:]
            if base not in pos:
                continue
            for j in (i, i + 1):
                for b, rescued in by_position.get(j, ()):
                    _check(deadline)
                    if (b != a and rescued[:j] == word[:j]
                            and rescued[j + 1:] == word[j:]):
                        add(a, b, {"rule": "insertion_rescue", "positive": [base, rescued],
                                   "negative": word, "position": i})
    neighbors = {a: set() for a in alphabet}
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    components, seen = [], set()
    for symbol in alphabet:
        if symbol in seen:
            continue
        stack, component = [symbol], set()
        while stack:
            _check(deadline)
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            stack.extend(neighbors[current] - component)
        seen.update(component)
        components.append(sorted(component))
    return components, [dict(symbols=list(pair), witness=edges[pair])
                        for pair in sorted(edges)]


def _positive_projection_sets(components, positive, prefix, deadline):
    """Return projection sets for already assigned atoms; None means cap fail."""
    k = max(prefix) + 1
    languages = [set() for _ in range(k)]
    # At a DFS node, symbols in unassigned atoms are absent from these partial
    # words; extension can only add projection words, so cap violation is final.
    blocks = [set() for _ in range(k)]
    for atom_i, side in enumerate(prefix):
        for ch in components[atom_i]:
            blocks[side].add(ch)
    for side, block in enumerate(blocks):
        for word in positive:
            _check(deadline)
            languages[side].add(_project(word, block, deadline))
    return languages


def _direct(blocks, positive, negative, deadline):
    languages = []
    for block in blocks:
        lang = set()
        for word in positive:
            _check(deadline)
            lang.add(_project(word, block, deadline))
        languages.append(lang)
    witnesses = []
    for word in negative:
        _check(deadline)
        unseen = []
        projections = []
        for side, block in enumerate(blocks):
            _check(deadline)
            projection = _project(word, block, deadline)
            projections.append(projection)
            if projection not in languages[side]:
                unseen.append(side)
        if not unseen:
            return None, {"negative": word, "projections": projections,
                          "matching_positive": [next(p for p in positive
                                                     if _project(p, blocks[i], deadline) == projections[i])
                                                for i in range(len(blocks))]}
        witnesses.append({"negative": word, "block_index": unseen[0],
                          "projection": projections[unseen[0]],
                          "all_unseen_block_indices": unseen})
    return {"blocks": [sorted(block) for block in blocks],
            "positive_projection_languages": [sorted(lang) for lang in languages],
            "negative_witnesses": witnesses}, None


def solve(data, *, k=None, deadline=None, max_solutions=1, local_word_cap=None):
    """Search exact canonical unordered k-way partitions.

    `max_solutions` is a positive integer or None (enumerate all). `deadline`
    is an absolute `time.perf_counter()` timestamp. `local_word_cap` is None
    or an integer >=1 bounding each block's distinct positive projections.
    A capped result describes the bounded finite-language class only.
    """
    started = time.perf_counter()
    alphabet, positive, negative, k = _validate(data, k)
    if max_solutions is not None and (isinstance(max_solutions, bool)
            or not isinstance(max_solutions, int) or max_solutions < 1):
        raise ValueError("max_solutions must be a positive integer or None")
    if local_word_cap is not None and (isinstance(local_word_cap, bool)
            or not isinstance(local_word_cap, int) or local_word_cap < 1):
        raise ValueError("local_word_cap must be a positive integer or None")

    metrics = {"graph_components": None, "nodes": 0, "leaves": 0,
               "cap_pruned_nodes": 0, "preprocessing_seconds": 0.0}
    components, edges, solutions = [], [], []
    stack = []
    exhausted = interrupted = False
    try:
        _check(deadline)
        components, edges = _components(alphabet, positive, negative, deadline)
        metrics["graph_components"] = len(components)
        if len(components) >= k:
            # Restricted-growth strings: first atom has owner 0, and each
            # later atom may use an existing side or introduce the next side.
            stack = [(0,)]
        metrics["preprocessing_seconds"] = time.perf_counter() - started
        while stack:
            _check(deadline)
            prefix = stack.pop()
            metrics["nodes"] += 1
            used = max(prefix) + 1
            remaining = len(components) - len(prefix)
            if used + remaining < k:
                continue
            if local_word_cap is not None:
                partial_languages = _positive_projection_sets(components, positive,
                                                               prefix, deadline)
                if any(len(lang) > local_word_cap for lang in partial_languages):
                    metrics["cap_pruned_nodes"] += 1
                    continue
            if len(prefix) < len(components):
                high = min(used, k - 1)
                for side in range(high, -1, -1):
                    stack.append(prefix + (side,))
                continue
            if used != k:
                continue
            metrics["leaves"] += 1
            blocks = [set() for _ in range(k)]
            for atom_i, side in enumerate(prefix):
                blocks[side].update(components[atom_i])
            record, offending = _direct(blocks, positive, negative, deadline)
            if record is not None:
                solutions.append(record)
                if max_solutions is not None and len(solutions) >= max_solutions:
                    exhausted = not stack
                    break
    except (_Deadline, KeyboardInterrupt):
        interrupted = True
    if not interrupted and not stack:
        exhausted = True
    if not metrics["preprocessing_seconds"]:
        metrics["preprocessing_seconds"] = time.perf_counter() - started
    metrics["provider_seconds"] = time.perf_counter() - started
    complete = bool(solutions) or exhausted
    if interrupted:
        status = "incomplete"
    elif solutions:
        status = "found"
    else:
        status = "infeasible"
    uniqueness = ("ambiguous" if len(solutions) >= 2 else
                  "unique" if exhausted and len(solutions) == 1 else "unknown")
    return {"method": "known-k-direct", "model_class":
            "bounded_finite_projection_languages" if local_word_cap is not None
            else "general_regular_product", "k": k, "status": status,
            "solutions": solutions, "search_exhausted": exhausted,
            "decision_complete": complete, "uniqueness": uniqueness,
            "uniqueness_scope": "sample_feasible_unordered_k_partitions_in_declared_model_class",
            "assumptions": ["exact labels", "known alphabet", "known k nonempty disjoint blocks",
                            "unrestricted regular local factors" if local_word_cap is None else
                            "each factor has at most local_word_cap distinct positive projections"],
            "alphabet": alphabet, "graph": {"components": components, "edges": edges},
            "max_solutions": max_solutions, "local_word_cap": local_word_cap,
            "metrics": metrics}
