"""Independent producer and verifier tests; no MainTeacher is used."""
import copy
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '2026-11-14' / 'sat_candidate_v37' / 'vendor'))
from pysat.solvers import Solver
from master import Master
from verify import verify_optimal


def partitions(n):
    out = []
    def rec(i, groups):
        if i == n:
            out.append(groups)
            return
        for j in range(len(groups)):
            rec(i + 1, groups[:j] + [groups[j] | (1 << i)] + groups[j + 1:])
        rec(i + 1, groups + [1 << i])
    rec(0, [])
    return out


def monotone_cut_test():
    parts = partitions(4)
    functions = []
    for f in range(1, 1 << 16):
        if all(not (f >> u & 1) or f >> v & 1
               for u in range(16) for v in range(16) if u & v == u):
            functions.append(f)
    cuts = checks = 0
    for f in functions:
        for partition in parts:
            if any(f >> b & 1 for b in partition):
                continue
            regions = []
            for b in partition:
                u = b
                for j in range(4):
                    if not (f >> (u | (1 << j)) & 1):
                        u |= 1 << j
                regions.append(u)
            regions = sorted(set(regions))
            # The failed partition is eliminated; every satisfying partition survives.
            predicate = lambda p: any(all(b & ~u for u in regions) for b in p)
            assert not predicate(partition)
            cuts += 1
            for other in parts:
                if any(f >> b & 1 for b in other):
                    assert predicate(other)
                    checks += 1
    assert (len(functions), cuts, checks) == (167, 758, 5218)
    print('167 monotone functions, 758 cuts, 5218 soundness checks passed')


def test_certificate():
    # Two negatives yield intersecting necessary cuts, with a nontrivial DRUP proof.
    D = {'alphabet': list('abcd'), 'positive': [list(x) for x in ('abcd', 'dcba', 'bdca', 'cabd')],
         'negative': [list(x) for x in ('dbac', 'cdab')]}
    cuts = [
        {'negative_index': 0, 'regions': [5, 6, 11, 12], 'positive_indices': [0, 0, 1, 1]},
        {'negative_index': 1, 'regions': [7, 9, 10, 12], 'positive_indices': [3, 1, 1, 0]},
    ]
    master = Master(4)
    for cut in cuts:
        master.add_cover(cut['regions'])
    with Solver(name='g3', bootstrap_with=master.threshold(3), with_proof=True) as solver:
        assert not solver.solve()
        proof = solver.get_proof()
    assert len(proof) > 1 and any(line.strip() == '0' for line in proof)
    result = {'status': 'OPTIMAL', 'blocks': [['a', 'c', 'd'], ['b']],
              'max_devices': 2,
              'certificate': {'type': 'teacher_cut_drup', 'cuts': cuts, 'proof': proof}}
    assert verify_optimal(D, result)['status'] == 'ACCEPT'
    mutations = []
    def mutate(fn):
        r = copy.deepcopy(result); fn(r); mutations.append(r)
    mutate(lambda r: r['certificate']['cuts'][0]['regions'].__setitem__(0, 3))
    mutate(lambda r: r['certificate']['cuts'][0]['positive_indices'].__setitem__(0, 2))
    mutate(lambda r: r['certificate']['cuts'][0].__setitem__('negative_index', 99))
    mutate(lambda r: r['certificate']['cuts'][0]['positive_indices'].__setitem__(0, 99))
    mutate(lambda r: r['certificate'].__setitem__('proof', ['999 0']))
    mutate(lambda r: r['certificate'].__setitem__('proof', []))
    mutate(lambda r: r['blocks'][0].__setitem__(0, 'unknown'))
    for r in mutations:
        assert verify_optimal(D, r)['status'] == 'REJECT', r
    assert verify_optimal(D, result, {'timeout_seconds': 0})['status'] == 'INCOMPLETE'
    contradiction = {'alphabet': ['a'], 'positive': [['a']], 'negative': [['a']]}
    infeasible = {'status': 'INFEASIBLE', 'blocks': None, 'max_devices': None,
                  'certificate': {'type': 'direct_infeasible'}}
    assert verify_optimal(contradiction, infeasible)['status'] == 'ACCEPT'
    empty = {'alphabet': [], 'positive': [[]], 'negative': []}
    zero = {'status': 'OPTIMAL', 'blocks': [], 'max_devices': 0,
            'certificate': {'type': 'symbol_bound'}}
    assert verify_optimal(empty, zero)['status'] == 'ACCEPT'
    bad = copy.deepcopy(D); bad['negative'][0].append('unknown')
    assert verify_optimal(bad, result)['status'] == 'REJECT'
    print(f'Directly generated DRUP accepted ({len(proof)} lines); tampering and edge cases passed')


if __name__ == '__main__':
    monotone_cut_test()
    test_certificate()
