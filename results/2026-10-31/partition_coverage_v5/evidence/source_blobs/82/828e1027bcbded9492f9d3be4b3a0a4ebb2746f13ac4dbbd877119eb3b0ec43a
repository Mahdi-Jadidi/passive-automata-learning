import itertools,json
from pathlib import Path
from sparse_certificate_v1 import solve
P=Path(__file__).parent
protocol=json.loads((P/'minimization_protocol_v1.json').read_text(encoding='utf-8-sig'))
records=[]
for total in range(2,protocol['sizes_total_at_most']+1):
    for n in range(1,total):
        blocks=['abcdef'[:n],'abcdef'[n:total]]
        u=[b*2 for b in blocks]; v=[w+b[0] for w,b in zip(u,blocks)]
        third=''.join(w[t] for t in range(max(map(len,v))) for w in v if t<len(w))
        data={'alphabet':list(''.join(blocks)),'positive':[''.join(u),''.join(reversed(u)),third],'negative':[],'k':2}
        print(json.dumps({'input':data,'q':2}),flush=True)
        out=solve(data,local_word_cap=2)
        if len(out['graph']['edges']) != n*(total-n):
            missing=[]
            actual={tuple(p) for p in out['graph']['edges']}
            for a in blocks[0]:
                for b in blocks[1]:
                    if (a,b) not in actual:
                        missing.append({'pair':[a,b],'projections':sorted({''.join(c for c in w if c in (a,b)) for w in data['positive']})})
            records.append({'input':data,'sizes':[n,total-n],'missing':missing,'result':out})
# Minimize the fixed poset's positive subset while retaining all seven edges.
perms=[''.join(p) for p in itertools.permutations('abcde') if all(p.index(a)<p.index(b) for a,b in ['ac','ad','bd'])]
goal=set(protocol['sparse_goal_edges'])
best=None
for count in range(1,4):
    for subset in itertools.combinations(perms,count):
        edges={a+b for a,b in itertools.combinations('abcde',2) if len({''.join(c for c in w if c in (a,b)) for w in subset})>1}
        if edges==goal: best=list(subset);break
    if best:break
print(json.dumps({'minimized_unequal_failures':records,'sparse_minimum_positive_base':best}),flush=True)
