import sys,itertools,json,random
from pathlib import Path
base=Path(__file__).resolve().parents[1]/'interactive_teacher_v45'
sys.path.insert(0,str(base))
from teacher_main import MainTeacher
from spec import direct_reject,mandatory_groups,budget
from master import Master
from verify import check_drup
from pysat.solvers import Solver
rng=random.Random(46); tick=budget(None); count=0; cycles=0
for _ in range(120):
 a=('a','b','c'); blocks=[('a',),('b',),('c',)]
 words=[(),('a',),('b',),('c',),('a','b'),('b','a'),('a','c'),('c','a')]
 p=rng.sample(words,rng.randrange(3)); n=rng.sample(words,rng.randrange(1,4))
 images={B:{'positive':[tuple(x for x in w if x in B) for w in p], 'negative':[tuple(x for x in w if x in B) for w in n]} for B in blocks}
 ans=MainTeacher(tick).check(blocks,images)
 expect=all(any(tuple(x for x in w if x in B) not in images[B]['positive'] for B in blocks) for w in n)
 assert (ans['status']=='ACCEPT')==expect
 count+=1; cycles+=bool(ans['metrics']['cycle_bits'])
# Check cut CNF against the mathematical class-escape property on all partitions of four atoms.
def partitions(n):
 def go(i,bs):
  if i==n: yield [b[:] for b in bs];return
  for b in bs:
   b.append(i);yield from go(i+1,bs);b.pop()
  bs.append([i]);yield from go(i+1,bs);bs.pop()
 yield from go(0,[])
checks=0
for cover in itertools.combinations(range(1,15),2):
 m=Master(4);m.add_cover(cover)
 with Solver(name='g3',bootstrap_with=m.clauses) as s:
  for P in partitions(4):
   ass=[v if any(i in b and j in b for b in P) else -v for (i,j),v in m.pairs.items()]
   expected=any(all(any(not (u>>x&1) for x in b) for u in cover) for b in P)
   assert s.solve(assumptions=ass)==expected
   checks+=1
# DRUP test: a satisfiable formula cannot gain a RUP empty clause; contradictory units can.
m=Master(2); assert not check_drup(m,1,['0'],tick)
m.clauses += [[1],[-1]]; assert check_drup(m,1,[],tick)
out={'seed':46,'teacher_cases':count,'teacher_cases_with_cycles':cycles,'master_cut_partition_checks':checks,'drup_cases':2}
Path(__file__).with_name('review_results.json').write_text(json.dumps(out,indent=2))
print(out)
