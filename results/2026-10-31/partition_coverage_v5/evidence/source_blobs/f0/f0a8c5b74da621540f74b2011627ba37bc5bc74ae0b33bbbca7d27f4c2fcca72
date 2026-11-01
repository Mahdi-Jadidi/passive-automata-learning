import json,time,hashlib
from pathlib import Path
from sparse_certificate_v2 import solve
P=Path(__file__).parent
protocol=json.loads((P/'sparse_scaling_protocol_v1.json').read_text(encoding='utf-8-sig'))
def build(cell,q):
    m,k,rep=cell['m'],cell['k'],cell['event_repeat']
    alphabet=[chr(0x400+i) for i in range(m)]
    anchors=alphabet[-(k-3):] if k>3 else []
    pool=alphabet[:m-len(anchors)]
    groups={};at=0
    for i,a in enumerate('abcde'):
        size=len(pool)//5+(i<len(pool)%5)
        groups[a]=pool[at:at+size];at+=size
    base=[''.join(anchors)+''.join(''.join(groups[a]) for a in 'acbde'),
          ''.join(''.join(groups[a]) for a in 'ebadc')+''.join(reversed(anchors))]
    data={'alphabet':alphabet,'positive':[''.join(c*(rep*r) for c in word) for word in base for r in range(1,q+1)],'negative':[''],'k':k}
    blocks=[sorted(groups['a']+groups['c']),sorted(groups['b']+groups['d']),groups['e']]+[[a] for a in anchors]
    blocks=sorted(blocks)
    expected_edges=sum(len(x)*len(y) for i,x in enumerate(blocks) for y in blocks[i+1:])-len(groups['a'])*len(groups['d'])
    return {'id':f"sparse_m{m}_k{k}_r{rep}_q{q}",'q':q,'data':data,'expected_blocks':blocks,'expected_edges':expected_edges,'cell':cell}
if __name__=='__main__':
    rows=[]
    for cell in protocol['cells']:
        for q in protocol['q']:
            case=build(cell,q)
            print(json.dumps({'case':case},ensure_ascii=False),flush=True)
            out=solve(case['data'],local_word_cap=q,deadline=time.perf_counter()+protocol['cooperative_seconds'])
            print(json.dumps({'id':case['id'],'output':out},ensure_ascii=False),flush=True)
            assert out['uniqueness']=='unique',out['status']
            assert out['solutions'][0]['blocks']==case['expected_blocks']
            assert len(out['graph']['edges'])==case['expected_edges']
            rows.append({'id':case['id'],'status':out['status'],'positive_lengths':list(map(len,case['data']['positive'])),'edge_count':len(out['graph']['edges']),'blocks':list(map(len,out['solutions'][0]['blocks']))})
    print(json.dumps({'summary':rows}),flush=True)
