"""Order-preserving trace analysis for the partition search."""

from sample import read_sample


def analyze_traces(D, tick, *, preprocess):
    Sigma, S_plus, S_minus = read_sample(D, tick)
    positives = {word: j for j, word in reversed(list(enumerate(S_plus)))}
    for i, word in enumerate(S_minus):
        tick()
        if word in positives:
            return {"kind": "opposite_labels", "negative": i, "positive": positives[word]}
        if not Sigma:
            return {"kind": "empty_alphabet", "negative": i}

    components = list(range(len(Sigma)))
    witnesses = []

    def representative(a):
        while a != components[a]:
            a = components[a]
        return a

    if preprocess:
        for i, y in enumerate(S_minus):
            for offset, (a, b) in enumerate(zip(y, y[1:])):
                tick()
                left, right = representative(a), representative(b)
                if left == right:
                    continue
                x = y[:offset] + (b, a) + y[offset + 2:]
                if x in positives:
                    components[right] = left
                    witnesses.append({"negative": i, "positive": positives[x], "offset": offset})

    blocks = {}
    for a in range(len(Sigma)):
        tick()
        blocks.setdefault(representative(a), []).append(a)
    root = tuple(sorted(tuple(block) for block in blocks.values()))
    return Sigma, S_plus, S_minus, root, witnesses

