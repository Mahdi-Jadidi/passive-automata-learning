"""Deterministic correctness data and truth-assisted calibration collector; GO only."""
import hashlib,itertools,json,random
from pathlib import Path
A=Path(__file__).resolve().parent;R=A.parent;OLD=R.parent/'partition_random_dfa_v13/audit'
def save(p,value):
    p.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(value,ensure_ascii=False,sort_keys=True)+'\n').encode()
    with p.open('xb') as f:f.write(raw)
    return hashlib.sha256(raw).hexdigest()
def accepted(word,world):
    states=[d['start'] for d in world['devices']]
    for ch in word:
        i=world['ownership'][ch];states[i]=world['devices'][i]['transitions'][states[i]][ch]
    return all(states[i] in d['accepting'] for i,d in enumerate(world['devices']))
def world(k,commutative):
    devices=[];owner={}
    for i in range(k):
        x,y=chr(97+2*i),chr(98+2*i)
        table=[{x:q^1,y:q^2} for q in range(4)] if commutative else [{x:1,y:0},{x:1,y:0}]
        d={'id':i,'alphabet':[x,y],'states':list(range(len(table))),'start':0,'accepting':[0],'transitions':table}
        devices.append(d);owner.update({x:i,y:i})
    return {'true_devices':k,'alphabet':list(owner),'ownership':owner,'devices':devices,'construction':'commutative_per_symbol_even_parity' if commutative else 'strongly_connected_set_reset'}
def main():
    cases=[];held=[]
    for k in range(1,5):
        for L in [8,64]:
            d=OLD/'data/controls'/f'K{k}_M{2*k}_L{L}';p=d/'input2.json'
            cases.append({'case_id':f'held_control_K{k}_L{L}','path':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'world':str((d/'world.json').resolve()),'kind':'held_control'})
    for m in range(2,7):
        alphabet=list('abcdef'[:m]);pool=['']+[''.join(x) for n in range(1,4) for x in itertools.product(alphabet,repeat=n)]
        for i in range(40):
            seed=2026110314+m*100+i;rng=random.Random(seed);observed=rng.sample(pool,min(len(pool),rng.randrange(1,17)));data={'alphabet':alphabet,'positive':[],'negative':[]}
            for word in observed:
                label=rng.randrange(3)
                if label:data['positive' if label==1 else 'negative'].append(word)
            p=A/'data/random'/f'm{m}_{i}.json';h=save(p,data);cases.append({'case_id':f'random_m{m}_{i}','path':str(p.resolve()),'sha256':h,'seed':seed,'kind':'random_finite_labels'})
    for k in [2,3,4]:
        for commuting in [False,True]:
            w=world(k,commuting);wp=A/'data/worlds'/f'K{k}_commuting{int(commuting)}.json';wh=save(wp,w)
            for coverage in (['full'] if commuting else ['full','missing_last']):
                queries=[];data={'alphabet':w['alphabet'],'positive':[],'negative':[]}
                for i,device in enumerate(w['devices']):
                    if coverage=='missing_last' and i==k-1:continue
                    x,y=device['alphabet']
                    for word in ([x+y,y+x,x+x,y+y,x,y,''] if commuting else [x+y,y+x]):
                        label=accepted(word,w);queries.append({'word':word,'accepted':label,'scheduled_device':i});data['positive' if label else 'negative'].append(word) if word not in data['positive']+data['negative'] else None
                cid=f'calibration_K{k}_commuting{int(commuting)}_{coverage}';p=A/'data/calibration'/f'{cid}.json';h=save(p,data)
                qp=A/'data/calibration'/f'{cid}_queries.json';save(qp,{'queries':queries,'policy':coverage,'truth_assisted_schedule':True,'passive_original_data':False,'world_sha256':wh})
                cases.append({'case_id':cid,'path':str(p.resolve()),'sha256':h,'world':str(wp.resolve()),'queries':str(qp.resolve()),'kind':'calibration','coverage_policy':coverage,'commutative_world':commuting})
    oldmap=json.loads((OLD/'GRID_INPUT_MAP_V4.json').read_text())['entries']
    for k in [1,20]:
        entry=oldmap[f'{k}:1000000'];d=Path(entry['directory'])
        for n in [2,8]:held.append({'case_id':f'held_million_K{k}_n{n}','path':str(d/f'input{n}.json'),'sha256':entry[f'input{n}_sha256'],'world':str(d/'world.json'),'world_sha256':entry['world_sha256'],'kind':'held_timing'})
    assert len(cases)==217 and len(held)==4
    save(A/'DATA_MANIFEST_V1.json',{'small_cases':cases,'timing_cases':held,'collector_is_additional_label_access':True});print(json.dumps({'small_cases':217,'timing_cases':4,'calibration_worlds':6}))
if __name__=='__main__':main()
