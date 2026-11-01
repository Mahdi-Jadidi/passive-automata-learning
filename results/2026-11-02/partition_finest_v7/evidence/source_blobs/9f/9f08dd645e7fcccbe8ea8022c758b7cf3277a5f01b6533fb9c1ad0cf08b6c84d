"""Exact known-k regular-factor partition search (stdlib only).

Positive complete words are accepted iff each block's local language contains
their projection. Negative words must have at least one projection outside the
corresponding finite positive projection language. A cap q bounds the number
of distinct positive projections in each block; q=None is unrestricted.
"""
from collections import defaultdict
import math
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


def _q_opposition(alphabet, positive, q, deadline):
    """Necessary separation constraints for finite local languages of size q."""
    if q is None:
        return [], []
    unary = {a: set() for a in alphabet}
    pairwise = {}
    for word in positive:
        _check(deadline)
        for a in alphabet:
            unary[a].add(_project(word, {a}, deadline))
        for i, a in enumerate(alphabet):
            for b in alphabet[i + 1:]:
                pairwise.setdefault((a, b), set()).add(_project(word, {a, b}, deadline))
    unary_conflicts = [{"symbol": a, "distinct_positive_unary_projections": len(words),
                        "projections": sorted(words)}
                       for a, words in unary.items() if len(words) > q]
    edges = [{"symbols": [a, b], "distinct_positive_pair_projections": len(words),
              "projections": sorted(words), "rule": "pair_projection_count_gt_q"}
             for (a, b), words in sorted(pairwise.items()) if len(words) > q]
    return unary_conflicts, edges


def solve(data, *, k=None, local_word_cap=None, deadline=None, max_solutions=None,
          use_q_opposition=True, use_contextual_must_links=True):
    """Enumerate compatible unordered partitions with sound graph constraints.

    `deadline` is an absolute time.perf_counter() timestamp. `max_solutions`
    is None (enumerate all) or a positive limit. `local_word_cap` declares the
    finite-projection-language class; it also activates q-opposition unless
    disabled. Both constraint switches affect pruning only, never the direct
    compatibility check. A cap means finite-language semantics, not general
    regular-factor semantics.
    """
    started = time.perf_counter()
    alphabet, positive, negative, k = _validate(data, k)
    if max_solutions is not None and (isinstance(max_solutions, bool)
            or not isinstance(max_solutions, int) or max_solutions < 1):
        raise ValueError("max_solutions must be a positive integer or None")
    if local_word_cap is not None and (isinstance(local_word_cap, bool)
            or not isinstance(local_word_cap, int) or local_word_cap < 1):
        raise ValueError("local_word_cap must be a positive integer or None")
    if not isinstance(use_q_opposition, bool) or not isinstance(use_contextual_must_links, bool):
        raise ValueError("constraint switches must be booleans")
    if deadline is not None and (isinstance(deadline, bool)
            or not isinstance(deadline, (int, float)) or not math.isfinite(deadline)):
        raise ValueError("deadline must be a finite absolute time.perf_counter() value or None")

    metrics = {"must_link_components": None, "nodes": 0, "leaves": 0,
               "cap_pruned_nodes": 0, "cannot_link_pruned_nodes": 0,
               "preprocessing_seconds": 0.0}
    components, must_edges, q_edges, solutions = [], [], [], []
    stack = []
    exhausted = interrupted = False
    contradiction = None
    unary_conflicts = []
    try:
        _check(deadline)
        if use_contextual_must_links:
            components, must_edges = _components(alphabet, positive, negative, deadline)
        else:
            components = [[a] for a in alphabet]
        q_edges = (_q_opposition(alphabet, positive, local_word_cap, deadline)
                   if use_q_opposition else ([], []))
        unary_conflicts, q_edges = q_edges
        atom_of = {a: i for i, atom in enumerate(components) for a in atom}
        cannot = set()
        for edge in q_edges:
            a, b = edge["symbols"]
            ia, ib = atom_of[a], atom_of[b]
            if ia == ib:
                contradiction = {"kind": "must_link_and_cannot_link",
                                 "must_link_component": components[ia],
                                 "cannot_link": edge}
                break
            cannot.add(tuple(sorted((ia, ib))))
        if unary_conflicts:
            contradiction = {"kind": "unary_projection_count_exceeds_q",
                             "conflicts": unary_conflicts}
        metrics["must_link_components"] = len(components)
        if contradiction is None and len(components) >= k:
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
                partial = _positive_projection_sets(components, positive, prefix, deadline)
                if any(len(lang) > local_word_cap for lang in partial):
                    metrics["cap_pruned_nodes"] += 1
                    continue
            if len(prefix) < len(components):
                atom_i = len(prefix)
                high = min(used, k - 1)
                for side in range(high, -1, -1):
                    if any((min(atom_i, prior), max(atom_i, prior)) in cannot
                           and prefix[prior] == side for prior in range(atom_i)):
                        metrics["cannot_link_pruned_nodes"] += 1
                        continue
                    stack.append(prefix + (side,))
                continue
            if used != k:
                continue
            metrics["leaves"] += 1
            blocks = [set() for _ in range(k)]
            for atom_i, side in enumerate(prefix):
                blocks[side].update(components[atom_i])
            record, _offending = _direct(blocks, positive, negative, deadline)
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
    enumeration_complete = exhausted
    decision_complete = bool(solutions) or exhausted
    if interrupted:
        status = "incomplete"
    elif contradiction is not None or (exhausted and not solutions):
        status = "infeasible"
    elif solutions:
        status = "found"
    else:
        status = "incomplete"
    uniqueness = ("ambiguous" if len(solutions) >= 2 else
                  "unique" if exhausted and len(solutions) == 1 else
                  "none" if exhausted else "unknown")
    return {"method": "known-k-q-opposition-exact-v2",
            "model_class": "bounded_finite_projection_languages" if local_word_cap is not None
            else "general_regular_product", "k": k, "status": status,
            "solutions": solutions, "search_exhausted": exhausted,
            "complete": enumeration_complete,
            "enumeration_complete": enumeration_complete,
            "decision_complete": decision_complete, "uniqueness": uniqueness,
            "uniqueness_scope": "sample_feasible_unordered_k_partitions_in_declared_model_class",
            "assumptions": ["exact labels", "known alphabet", "known k nonempty disjoint blocks",
                            "unrestricted regular local factors" if local_word_cap is None else
                            "finite local projection languages with size at most local_word_cap"],
            "alphabet": alphabet, "constraints": {
                "contextual_must_links_enabled": use_contextual_must_links,
                "must_link_edges": must_edges,
                "q_opposition_enabled": use_q_opposition and local_word_cap is not None,
                "q": local_word_cap, "cannot_link_edges": q_edges,
                "unary_conflicts": unary_conflicts, "presearch_contradiction": contradiction},
            "max_solutions": max_solutions, "local_word_cap": local_word_cap,
            "metrics": metrics}


def _main(argv=None):
    import argparse
    import json
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON object with alphabet, positive, negative, and optional k")
    parser.add_argument("--k", type=int)
    parser.add_argument("--local-word-cap", type=int, default=None,
                        help="finite local projection-language bound; omit for unrestricted regular factors")
    parser.add_argument("--max-solutions", type=int, default=None,
                        help="truncate enumeration after this many solutions")
    parser.add_argument("--deadline-seconds", type=float,
                        help="cooperative duration from start of provider call")
    parser.add_argument("--no-q-opposition", action="store_true")
    parser.add_argument("--no-contextual-must-links", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.deadline_seconds is not None and (not math.isfinite(args.deadline_seconds)
                or args.deadline_seconds < 0):
            raise ValueError("deadline-seconds must be a finite nonnegative number")
        with open(args.input, "r", encoding="utf-8-sig") as stream:
            data = json.load(stream)
        deadline = (time.perf_counter() + args.deadline_seconds
                    if args.deadline_seconds is not None else None)
        result = solve(data, k=args.k, local_word_cap=args.local_word_cap,
                       deadline=deadline, max_solutions=args.max_solutions,
                       use_q_opposition=not args.no_q_opposition,
                       use_contextual_must_links=not args.no_contextual_must_links)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 3 if result["status"] == "incomplete" else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "invalid_input", "error": str(exc)},
                         ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(_main())
