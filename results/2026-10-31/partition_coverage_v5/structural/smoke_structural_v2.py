import json,time
from pathlib import Path
from sparse_certificate_v2 import solve
p=json.loads((Path(__file__).parent/'v2_protocol_v1.json').read_text(encoding='utf-8-sig'))
for q in p['q']:
    data={'alphabet':list('abcde'),'positive':[''.join(c*r for c in w) for w in p['positive_base'] for r in range(1,q+1)],'negative':['','aa'],'k':3}
    print(json.dumps({'input':data,'q':q}),flush=True)
    out=solve(data,local_word_cap=q)
    print(json.dumps(out),flush=True)
    assert out['complete'] and out['uniqueness']=='unique'
    assert out['solutions'][0]['blocks']==[['a','c'],['b','d'],['e']]
    assert len(out['graph']['edges'])==7
for data,kwargs in [({'alphabet':list('abc'),'positive':['abc'],'negative':[],'k':2},{}),({'alphabet':['a'],'positive':['a'],'negative':[],'k':1},{'deadline':time.perf_counter()-1})]:
    print(json.dumps({'input':data,'kwargs':kwargs}),flush=True)
    out=solve(data,**kwargs)
    print(json.dumps(out),flush=True)
    assert out['complete'] is False
