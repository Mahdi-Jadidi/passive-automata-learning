"""Every pair assignment and threshold on 100 seeded small instances."""
import sys,json,itertools,random,contextlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'results/2026-11-16/exact_optimizer_v43'))
import encoding as E
from optimizer import Solver
def main():
    rng=random.Random(4416);checks=0
    detailed='--detailed' in sys.argv
    target='encoding_replay_instances.jsonl' if detailed else 'encoding_audit.jsonl'
    detail_context=(HERE/'encoding_checks.jsonl').open('x',encoding='utf8') if detailed else contextlib.nullcontext(None)
    with (HERE/target).open('x',encoding='utf8') as f, detail_context as detail:
        for case in range(100):
            Sigma=['a','b','c','d'][:3+case%2]
            words=[list(w) for size in range(3) for w in itertools.product(Sigma,repeat=size)];rng.shuffle(words)
            S_plus=words[:rng.randrange(4)];S_minus=words[4:4+rng.randrange(1,4)]
            a,p,n=E.normalize({'alphabet':Sigma,'positive':S_plus,'negative':S_minus});enc=E.build(a,p,n,E.budget(None));q=enc['q'];pairs=list(enc['pairs'])
            with Solver(name='g3',bootstrap_with=enc['clauses']) as solver:
                for bits in itertools.product((False,True),repeat=len(pairs)):
                    relation=dict(zip(pairs,bits))
                    def equal(i,j):return i==j or relation[tuple(sorted((i,j)))]
                    valid=all(not(equal(i,j) and equal(j,k)) or equal(i,k) for i in range(q) for j in range(q) for k in range(q))
                    blocks=[];used=set()
                    if valid:
                        for i in range(q):
                            if i in used:continue
                            atom_ids=[j for j in range(q) if equal(i,j)];used.update(atom_ids)
                            blocks.append({a[x] for j in atom_ids for x in enc['groups'][j]})
                    def project(word,B):return tuple(x for x in word if x in B)
                    compatible=valid and all(any(project(w,B) not in {project(v,B) for v in p} for B in blocks) for w in n)
                    fixed=[enc['pairs'][pair] if value else -enc['pairs'][pair] for pair,value in relation.items()]
                    for t in range(q+1):
                        actual=solver.solve(assumptions=fixed+[enc['thresholds'][t]])
                        expected=compatible and len(blocks)>=t
                        if detail is not None:
                            detail.write(json.dumps({'case':case,'pairs':pairs,'assignment':bits,'threshold':t,
                                                     'actual':actual,'expected':expected})+'\n')
                        assert actual==expected,(case,relation,t,actual,expected)
                        checks+=1
            f.write(json.dumps({'case':case,'Sigma':Sigma,'S_plus':S_plus,'S_minus':S_minus,'atoms':q,'pass':True})+'\n');f.flush()
    print(json.dumps({'instances':100,'pair_assignment_threshold_checks':checks}))
if __name__=='__main__':main()
