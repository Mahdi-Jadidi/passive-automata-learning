"""Literal audit of verifier path_state/pair_at, independent of producer.
Run: PYTHONPATH=tests/reference python -B tests/reference/p3_path_exhaustive_audit.py
Repeat with -O. This tests region reconstruction, not complete certificate replay.
"""
from collections import Counter
from itertools import combinations
from p3_frontier_verifier import Budget, pair_at, path_state
from rgs_oracle import rgs, region, self_test


def check(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def owner(p):
    return tuple(p.index(g) for g in p)


def literal_owner(n, E):
    # Independent connected-component reachability, not owner relabeling/DSU.
    adjacency = [set() for _ in range(n)]
    for a, b in E:
        adjacency[a].add(b)
        adjacency[b].add(a)
    answer = [-1] * n
    for a in range(n):
        if answer[a] >= 0:
            continue
        pending = [a]
        answer[a] = a
        while pending:
            for b in adjacency[pending.pop()]:
                if answer[b] < 0:
                    answer[b] = a
                    pending.append(b)
    return tuple(answer)


def run():
    self_test()
    total = Counter()
    for n in range(7):
        ps = list(rgs(n))
        count = Counter()
        for root in map(owner, ps):
            root_E = tuple((i, g) for i, g in enumerate(root) if i != g)
            table = {}
            budget = Budget(seconds=30, max_work=200_000_000)
            def visit(qid, parent, edge, E, D):
                q = dict(id=qid, parent_id=parent, edge=edge)
                table[qid] = q
                literal = {p for p in ps if region(p, E, D)}
                count['membership_checks'] += len(ps)
                expected = literal_owner(n, E)
                p, reps, empty, singleton = path_state(q, table, root, budget,
                                                        singleton_check=True)
                check(p == expected, ('owner', n, root, qid, p, expected))
                check(reps == sorted(set(expected)), ('representatives', n, qid))
                check(empty == (not literal), ('empty', n, root, qid))
                if literal:
                    check(singleton == (len(literal) == 1), ('singleton', n, root, qid))
                    expected_min = min(literal, key=lambda x: n-len(set(x)))
                    check(owner(expected_min) == expected, ('minimum', n, root, qid))
                    check(sum(len(set(x)) == len(reps) for x in literal) == 1,
                          ('unique minimum', n, root, qid))
                count['nodes'] += 1
                count['empty'] += int(empty)
                count['singleton_nonempty'] += int(bool(literal) and singleton)
                if len(literal) <= 1:
                    return literal
                pairs = list(combinations(sorted(set(expected)), 2))
                count['splits'] += 1
                q['cursor_log'] = []
                for j, pair in enumerate(pairs):
                    check(pair_at(sorted(set(expected)), j) == list(pair), ('pair_at', n, qid, j))
                    q['cursor_log'].append(dict(pair=list(pair)))
                    count['pair_checks'] += 1
                hits = Counter()
                for j, pair in enumerate(pairs):
                    child = visit(qid+'/c'+str(j), qid,
                                  dict(kind='CHILD', index=j, pair=list(pair)),
                                  E+(pair,), D+tuple(pairs[:j]))
                    hits.update(child)
                residual = visit(qid+'/r', qid, dict(kind='RESIDUAL'), E, D+tuple(pairs))
                hits.update(residual)
                check(hits == Counter({x:1 for x in literal}), ('coverage/disjointness', n, root, qid))
                count['residuals'] += 1
                return literal
            visit('root', None, dict(kind='ROOT'), root_E, ())
            count['roots'] += 1
        total.update(count)
        print('n=', n, dict(sorted(count.items())))
    print('TOTAL', dict(sorted(total.items())))


if __name__ == '__main__':
    run()
