"""Test pair/count/cut encoding on finite monotone predicates, without a teacher."""
import argparse
import json
from pathlib import Path
import random

from audit import SEED, load, partitions


def trial(q, rng, Master, Solver, check_drup):
    full = (1<<q)-1
    pool = [m for m in range(1,full) if m.bit_count() in (2,3)]
    minima = [rng.sample(pool,rng.randrange(1,5)) for _ in range(rng.randrange(2,5))]
    reject = [{b for b in range(1,full+1) if any(b&w==w for w in family)} for family in minima]
    universe = partitions(q)
    def failed(p):
        return next((i for i,allowed in enumerate(reject) if not any(b in allowed for b in p)),None)
    compatible = [p for p in universe if failed(p) is None]
    master = Master(q)
    expected = set(universe)
    checks = []
    with Solver(name='g3',bootstrap_with=master.clauses) as sat:
        assumptions = {p:[var if any(block&(1<<a) and block&(1<<b) for block in p) else -var
                          for (a,b),var in master.pairs.items()] for p in universe}
        while True:
            for p,bits in assumptions.items():
                assert sat.solve(assumptions=bits)==(p in expected), (q,minima,p,checks)
            k = max(map(len,expected))
            threshold_checks = []
            for t in range(q+2):
                gate = master.thresholds[t] if t<=q else False
                actual = gate is not False and sat.solve(assumptions=[] if gate is True else [gate])
                assert actual==(t<=k), (q,minima,t,k)
                if actual:
                    decoded = tuple(sum(1<<a for a in block) for block in master.decode(sat.get_model()))
                    assert decoded in expected and len(decoded)>=t
                threshold_checks.append(dict(t=t,expected=t<=k,actual=actual))
            candidate = rng.choice(sorted(p for p in expected if len(p)==k))
            i = failed(candidate)
            check = dict(relaxation_max=k,partition_assignment_checks=len(universe),
                         thresholds=threshold_checks,candidate=candidate,failure=i)
            checks.append(check)
            if i is None:
                assert k==max(map(len,compatible))
                break
            regions = []
            for b in candidate:
                false_supersets = [u for u in range(1,full) if u&b==b and u not in reject[i]]
                largest = [u for u in false_supersets
                           if all(u&v!=u for v in false_supersets if u!=v)]
                regions.append(rng.choice(largest))
            def survives(p):
                return any(all(b&u!=b for u in regions) for b in p)
            assert not survives(candidate) and all(map(survives,compatible))
            expected = {p for p in expected if survives(p)}
            check['cover'] = sorted(set(regions))
            for clause in master.add_cover(regions):
                sat.add_clause(clause)
    with Solver(name='g3',bootstrap_with=master.threshold(k+1),with_proof=True) as producer:
        assert not producer.solve()
        proof = producer.get_proof()
    assert check_drup(master,k+1,proof,lambda:None)
    return dict(atoms=q,minimal_witness_generators=minima,oracle_optimum=k,rounds=checks,
                proof=proof,proof_checked=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('output',type=Path)
    args = ap.parse_args()
    load('v45')  # Load the committed solver package in a fresh interpreter.
    from master import Master
    from pysat.solvers import Solver
    from verify import check_drup
    rng = random.Random(SEED+1)
    records = []
    with args.output.open('x',encoding='utf-8') as stream:
        for q in (5,6,7):
            for rep in range(12):
                row = dict(trial(q,rng,Master,Solver,check_drup),repetition=rep,seed=SEED+1)
                records.append(row)
                stream.write(json.dumps(row)+'\n')
                stream.flush()
    rounds = [entry for r in records for entry in r['rounds']]
    print(json.dumps(dict(trials=len(records),rounds=len(rounds),
                          pair_assignment_checks=sum(r['partition_assignment_checks'] for r in rounds),
                          threshold_checks=sum(len(r['thresholds']) for r in rounds),
                          refutations_checked=len(records))),flush=True)


if __name__=='__main__':
    main()
