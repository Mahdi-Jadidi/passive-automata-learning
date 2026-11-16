from itertools import combinations


def partitions(items):
    if not items:
        yield ()
        return
    x, *rest = items
    for p in partitions(rest):
        yield ((x,),) + p
        for i in range(len(p)):
            yield p[:i] + ((x,) + p[i],) + p[i+1:]


def projection(word, block):
    return tuple(x for x in word if x in block)


def test(m, edges):
    vertices = tuple(range(m))
    negative = vertices
    positives = [tuple(v for v in vertices if v not in edge) for edge in edges]
    independent = [set(c) for k in range(m+1) for c in combinations(vertices, k)
                   if all(not set(e) <= set(c) for e in edges)]
    alpha = max(map(len, independent))
    feasible = []
    for partition in partitions(vertices):
        rejects = [all(projection(negative, b) != projection(p, b) for p in positives)
                   for b in partition]
        for b, rejects_n in zip(partition, rejects):
            cover = all(set(b) & set(e) for e in edges)
            assert rejects_n == cover
        if any(rejects):
            feasible.append(partition)
    optimum = max(map(len, feasible))
    assert optimum == alpha + 1, (m, edges, optimum, alpha)
    return alpha, optimum, len(feasible)


if __name__ == '__main__':
    cases = 0
    for m in range(2, 5):
        possible_edges = list(combinations(range(m), 2))
        for mask in range(1, 1 << len(possible_edges)):
            edges = [e for i, e in enumerate(possible_edges) if mask >> i & 1]
            test(m, edges)
            cases += 1
    print(f'PASS: all {cases} nonempty simple graphs on 2, 3, or 4 labelled vertices')
    for m, edges in [(2, [(0, 1)]), (3, [(0, 1), (1, 2)]),
                     (3, [(0, 1), (0, 2), (1, 2)])]:
        print(f'm={m} edges={edges} alpha,optimum,feasible={test(m, edges)}')
