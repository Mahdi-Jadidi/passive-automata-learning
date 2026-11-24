"""Raw analysis for the singleton, pair and bounded witness-rank stages."""
from collections import Counter
from itertools import combinations

from model import merge, ordered


def singleton_analysis(sigma, positives, negatives, tick):
    values = [set() for _ in sigma]
    for word in dict.fromkeys(positives):
        tick()
        counts = Counter(word)
        for symbol, possible in enumerate(values):
            possible.add(counts[symbol])
    coverage = {}
    for i, word in enumerate(negatives):
        tick()
        counts = Counter(word)
        for symbol, possible in enumerate(values):
            if counts[symbol] not in possible:
                coverage[i] = 1 << symbol
                break
    return coverage


def pair_scan(root, positives, negatives, unresolved, tick, *, include_triples=True):
    positive_ids = {}
    for j, word in enumerate(positives):
        positive_ids.setdefault(word, j)
    negative_ids = {}
    for i in unresolved:
        negative_ids.setdefault(negatives[i], i)
    hits, failures = {}, []
    for left, right in combinations(root, 2):
        tick()
        pair = left | right
        symbols = {left.bit_length() - 1, right.bit_length() - 1}
        images = {}
        for word, j in positive_ids.items():
            tick()
            images.setdefault(tuple(a for a in word if a in symbols), j)
        rejected = set()
        failure = None
        for word, i in negative_ids.items():
            tick()
            projected = tuple(a for a in word if a in symbols)
            if projected not in images:
                rejected.add(i)
            elif failure is None:
                failure = [pair, i, images[projected]]
        if failure is None:
            return merge(root, left, right), "pair", []
        hits[pair] = rejected
        failures.append(failure)

    # A pair containing no new rejection cannot help when every single pair fails.
    useful = [pair for pair in hits if hits[pair]]
    target = set(negative_ids.values())
    for left, right in combinations(useful, 2):
        tick()
        if not left & right and hits[left] | hits[right] == target:
            answer = ordered([left, right, *(b for b in root if not b & (left | right))])
            return answer, "two-pairs", failures

    triples = combinations(root, 3) if include_triples else ()
    for atoms in triples:
        tick()
        block = atoms[0] | atoms[1] | atoms[2]
        symbols = {atom.bit_length() - 1 for atom in atoms}
        images = set()
        for word in positive_ids:
            tick()
            images.add(tuple(a for a in word if a in symbols))
        for word in negative_ids:
            tick()
            if tuple(a for a in word if a in symbols) in images:
                break
        else:
            answer = ordered([block, *(a for a in root if not a & block)])
            return answer, "triple", failures

    # Produce an optional compatible incumbent for the general search.
    remaining = target.copy()
    used, chosen = 0, []
    while remaining:
        tick()
        candidate = max((p for p in useful if not p & used),
                        key=lambda p: len(hits[p] & remaining), default=0)
        if not candidate or not hits[candidate] & remaining:
            return None, None, failures
        used |= candidate
        chosen.append(candidate)
        remaining -= hits[candidate]
    answer = ordered([*chosen, *(b for b in root if not b & used)])
    return answer, None, failures


def discrepancy_families(positives, negatives, unresolved, tick, limit):
    xs = list(dict.fromkeys(positives))
    ys = {negatives[i]: None for i in unresolved}
    # Debit at least one unit per comparison even if alternatives are forced.
    if limit is not None and len(xs) * len(ys) > limit:
        return None
    rows = {}
    size = 1
    counts = {word: Counter(word) for word in (*xs, *ys)}
    for y in ys:
        families = {}
        for x in xs:
            tick()
            differing = {a for a in counts[x].keys() | counts[y].keys()
                         if counts[x][a] != counts[y][a]}
            alternatives = [1 << a for a in sorted(differing)]
            stable = sorted(counts[x].keys() - differing)
            for a, b in combinations(stable, 2):
                tick()
                if tuple(s for s in x if s in (a, b)) != tuple(s for s in y if s in (a, b)):
                    alternatives.append((1 << a) | (1 << b))
            assert alternatives
            key = tuple(sorted(alternatives))
            if key not in families:
                if limit is not None:
                    size *= len(key)
                    if size > limit:
                        return None
                families[key] = None
        row = tuple(families)
        if row:
            rows[y] = row
    return tuple(rows.values())


def rank_answer(root, rows, tick):
    # Each state tracks the component partition and the current negative's block.
    states = {root}
    for row in rows:
        states_with_anchor = {(state, 0) for state in states}
        for alternatives in row:
            next_states = set()
            for state, anchor in states_with_anchor:
                for alternative in alternatives:
                    tick()
                    support = anchor | alternative
                    joined = 0
                    untouched = []
                    for block in state:
                        if block & support:
                            joined |= block
                        else:
                            untouched.append(block)
                    next_states.add((ordered([joined, *untouched]), joined))
            states_with_anchor = next_states
        states = {state for state, _ in states_with_anchor}
    return min(states, key=lambda state: (-len(state), state))

