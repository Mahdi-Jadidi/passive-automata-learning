import itertools,json,time
from pathlib import Path
from sparse_certificate_v1 import solve,graph_certificate
P=Path(__file__).parent
protocol=json.loads((P/'smoke_protocol_v1.json').read_text(encoding='utf-8-sig'))
def dense(sizes,q):
    symbols=iter('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    blocks=[''.join(next(symbols) for _ in range(n)) for n in sizes]
    u=[b*2 for b in blocks]
    words=[''.join(u),''.join(reversed(u))]
    words+=[''.join(b*r for b in blocks) for r in range(3,q+2)]
    return {'alphabet':list(''.join(blocks)),'positive':words,'negative':[],'k':len(blocks)},[list(b) for b in blocks]
def lockstep(sizes,r):
    data,blocks=dense(sizes,2)
    u=[''.join(b)*r for b in blocks]
    v=[w+b[0] for w,b in zip(u,blocks)]
    third=''.join(w[t] for t in range(max(map(len,v))) for w in v if t<len(w))
    data['positive']=[''.join(u),''.join(reversed(u)),third]
    return data,blocks
rows=[]
for q in protocol['q']:
    for sizes in protocol['sizes']:
        data,blocks=dense(sizes,q)
        print(json.dumps({'input':data,'q':q,'kind':'dense_q_plus_one'}),flush=True)
        out=solve(data,local_word_cap=q,max_solutions=2)
        assert out['uniqueness']=='unique' and out['solutions'][0]['blocks']==blocks,out
        rows.append({'kind':'dense','q':q,'sizes':sizes,'status':out['status'],'edges':len(out['graph']['edges'])})
    positive=[]
    for perm in itertools.permutations(protocol['sparse_alphabet']):
        w=''.join(perm)
        if all(w.index(a)<w.index(b) for a,b in protocol['sparse_poset_relations']):
            positive.extend(''.join(a*r for a in w) for r in range(1,q+1))
    data={'alphabet':list('abcde'),'positive':positive,'negative':['','aa'],'k':3}
    print(json.dumps({'input':data,'q':q,'kind':'sparse_trace_realization'}),flush=True)
    out=solve(data,local_word_cap=q)
    assert out['uniqueness']=='unique',out
    assert out['solutions'][0]['blocks']==[['a','c'],['b','d'],['e']]
    assert len(out['graph']['edges'])==7
    rows.append({'kind':'sparse_trace','q':q,'output':out})
failures=[]
for sizes in protocol['sizes']:
    for r in protocol['repeats']:
        data,blocks=lockstep(sizes,r)
        print(json.dumps({'input':data,'q':2,'kind':'original_lockstep','sizes':sizes,'repeats':r}),flush=True)
        out=solve(data,local_word_cap=2)
        expected=sum(len(a)*len(b) for i,a in enumerate(blocks) for b in blocks[i+1:])
        row={'sizes':sizes,'repeats':r,'edge_count':len(out['graph']['edges']),'complete_expected':expected,'output':out}
        if row['edge_count']!=expected: failures.append({'input':data,**row})
        rows.append({'kind':'original_lockstep',**row})
# Finite cap checked directly after graph relaxation; connected/ambiguous abstentions.
for data,q in [({'alphabet':list('ab'),'positive':['','a','aa'],'negative':[],'k':2},1),({'alphabet':list('abc'),'positive':['abc'],'negative':[],'k':2},1)]:
    print(json.dumps({'input':data,'q':q,'kind':'controls'}),flush=True)
    rows.append({'kind':'control','output':solve(data,local_word_cap=q)})
expired=solve({'alphabet':['a'],'positive':['a'],'negative':[],'k':1},deadline=time.perf_counter()-1)
assert expired['status']=='incomplete'
print(json.dumps({'rows':rows,'lockstep_failures_original':failures,'expired':expired}),flush=True)
