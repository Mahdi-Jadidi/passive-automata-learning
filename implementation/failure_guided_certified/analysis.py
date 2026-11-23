"""Trace indexing and certifying mandatory-component contraction."""

from itertools import combinations

from sample import read_sample


def analyze_traces(D, tick):
    Sigma, S_plus, S_minus = read_sample(D, tick)
    positives = {}
    for j, word in enumerate(S_plus):
        tick()
        positives.setdefault(word, j)
    for i, word in enumerate(S_minus):
        tick()
        if word in positives:
            return {"kind": "opposite_labels", "negative": i, "positive": positives[word]}
        if not Sigma:
            return {"kind": "empty_alphabet", "negative": i}
    root = tuple((a,) for a in range(len(Sigma)))
    return Sigma, S_plus, S_minus, root


def contract(root, matches):
    """Restart on the updated components after each certified merge."""
    alphabet = {a for block in root for a in block}
    steps = []
    while True:
        for i in range(len(matches.S_minus)):
            matches.tick()
            mandatory = []
            for block in root:
                complement = tuple(sorted(alphabet.difference(block)))
                j = matches.row(complement)[i]
                if j is not None:
                    mandatory.append({"block": block, "positive": j})
            if len(mandatory) >= 2:
                removed = {item["block"] for item in mandatory}
                joined = tuple(sorted(a for block in removed for a in block))
                root = tuple(sorted([b for b in root if b not in removed] + [joined]))
                steps.append({"negative": i, "deleted": mandatory})
                break
        else:
            return root, steps


def exact_components(root, matches):
    """Meet of compatible bipartitions for at most ten components."""
    signatures = [[] for _ in root]
    for size in range(len(root) - 1):
        for extra in combinations(range(1, len(root)), size):
            matches.tick()
            side = {0, *extra}
            left = tuple(sorted(a for j in side for a in root[j]))
            right = tuple(sorted(a for j, block in enumerate(root) if j not in side for a in block))
            if matches.first_failure((left, right)) is None:
                for j, signature in enumerate(signatures):
                    signature.append(j in side)
    groups = {}
    for block, signature in zip(root, signatures):
        groups.setdefault(tuple(signature), []).extend(block)
    return tuple(sorted(tuple(sorted(values)) for values in groups.values()))

