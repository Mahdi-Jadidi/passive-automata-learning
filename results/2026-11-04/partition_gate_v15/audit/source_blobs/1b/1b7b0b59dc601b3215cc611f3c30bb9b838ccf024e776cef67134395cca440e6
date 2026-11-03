"""Provider-independent finite-sample oracle and deterministic audit corpus."""
import hashlib,itertools,json,random
from pathlib import Path
A=Path(__file__).resolve().parent;R=A.parent;OLD=R.parent.parent/'2026-11-03/partition_recovery_v14/audit'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(obj,ensure_ascii=False,sort_keys=True)+'\n').encode()
    with p.open('xb') as f:f.write(raw)
    return sha(raw)
def rgs(n):
    def rec(prefix,maximum):
        if len(prefix)==n:yield tuple(prefix);return
        for x in range(maximum+2):yield from rec(prefix+[x],max(maximum,x))
    yield from rec([0],0)
def blocks(key,alphabet):
    out=[[] for _ in range(max(key)+1)]
    for x,i in zip(alphabet,key):out[i].append(x)
    return out
def feasible(data,key):
    alphabet=sorted(data['alphabet']);part=blocks(key,alphabet);owner={x:i for i,g in enumerate(part) for x in g}
    def project(w):
        out=[[] for _ in part]
        for x in w:out[owner[x]].append(x)
        return [''.join(v) for v in out]
    languages=[set() for _ in part]
    for p in set(data['positive']):
        for i,value in enumerate(project(p)):languages[i].add(value)
    return all(any(value not in languages[i] for i,value in enumerate(project(n))) for n in set(data['negative']))
def full_family(data):return [x for x in rgs(len(data['alphabet'])) if feasible(data,x)]
def main():
    manifest=json.loads((OLD/'DATA_MANIFEST_V1.json').read_text());cases=[]
    def add(cid,data,kind,extra=None):
        p=A/'data'/f'{cid}.json';h=save(p,data);cases.append({'case_id':cid,'path':str(p.resolve()),'sha256':h,'kind':kind,**(extra or {})})
    for c in manifest['small_cases']:
        p=Path(c['path']);assert sha(p.read_bytes())==c['sha256'];cases.append({'case_id':'held_'+c['case_id'],'path':str(p.resolve()),'sha256':c['sha256'],'kind':'held_C014'})
    assert len(cases)==217
    for m in range(2,7):
        alphabet=list('abcdef'[:m]);words=['']+[''.join(x) for n in range(1,4) for x in itertools.product(alphabet,repeat=n)]
        for i in range(40):
            seed=2026110415+m*100+i;rng=random.Random(seed);selected=rng.sample(words,min(len(words),rng.randrange(1,17)));data={'alphabet':alphabet,'positive':[],'negative':[]}
            for word in selected:
                label=rng.randrange(3)
                if label:data['positive' if label==1 else 'negative'].append(word)
            add(f'random_m{m}_{i}',data,'random',{'seed':seed})
    targeted=[('swap_covered',list('abcd'),['','ab','cd'],['ba','dc']),('graph_failure_unique',list('abcd'),['','aabb','ccdd'],['bbaa','ddcc']),('all_Bell',list('abcd'),[''],['a','b','c','d']),('same_K_ambiguous',list('abcd'),[],[]),('empty_P',list('abc'),[],['a']),('empty_N',list('abc'),['ab'],[]),('empty_both',list('abc'),[],[])]
    for cid,alpha,P,N in targeted:add(cid,{'alphabet':alpha,'positive':P,'negative':N},'targeted')
    for m in [8,10,12]:
        alpha=list('abcdefghijkl'[:m]);pairs=[alpha[i:i+2] for i in range(0,m,2)];add(f'structured_m{m}',{'alphabet':alpha,'positive':['']+[''.join(g) for g in pairs],'negative':[''.join(reversed(g)) for g in pairs]},'structured',{'certified_atoms':pairs})
    oracles=[];jobs=[]
    for c in cases:
        data=json.loads(Path(c['path']).read_text());alphabet=sorted(data['alphabet'])
        if c['kind']=='structured':
            atoms=c['certified_atoms'];family=[]
            for g in atoms:
                p=''.join(g);n=''.join(reversed(g));assert p in data['positive'] and n in data['negative'] and len(g)==2 and g[0]!=g[1]
            atomkey=tuple(i//2 for i in range(len(alphabet)));assert feasible(data,atomkey)
            for component_key in rgs(len(atoms)):family.append(tuple(component_key[i//2] for i in range(len(alphabet))))
            restrictions=[None,[len(atoms)],[2],[len(atoms)+1]]
        else:
            assert len(alphabet)<=8;family=full_family(data);m=len(alphabet);restrictions=[None]+[[k] for k in sorted({1,m,(m+1)//2})]
        assert family and all(feasible(data,x) for x in family)
        for allowed in restrictions:
            selected=[x for x in family if allowed is None or max(x)+1 in allowed];jid=c['case_id']+('_noK' if allowed is None else '_K'+','.join(map(str,allowed)))
            jobs.append({'job_id':jid,'case_id':c['case_id'],'input':c['path'],'input_sha256':c['sha256'],'allowed_k':allowed,'expectation':'unique' if len(selected)==1 else 'ambiguous' if selected else 'incompatible'})
            oracles.append({'job_id':jid,'alphabet':alphabet,'compatible_rgs':selected,'count':len(selected),'method':'independent full RGS' if c['kind']!='structured' else 'swap forced-components + direct atom feasibility + complete component-coarsening enumeration'})
    invalid=[('contradictory',{'alphabet':['a','b'],'positive':['a'],'negative':['a']}),('empty_alphabet',{'alphabet':[],'positive':[],'negative':[]}),('duplicate_symbols',{'alphabet':['a','a'],'positive':[],'negative':[]}),('unknown_symbol',{'alphabet':['a'],'positive':['b'],'negative':[]}),('nonstring_word',{'alphabet':['a'],'positive':[1],'negative':[]}),('missing_field',{'alphabet':['a'],'positive':[]})]
    for cid,data in invalid:
        p=A/'invalid'/f'{cid}.json';h=save(p,data);jobs.append({'job_id':'invalid_'+cid,'case_id':cid,'input':str(p.resolve()),'input_sha256':h,'allowed_k':None,'expectation':'incompatible' if cid=='contradictory' else 'invalid'})
        if cid=='contradictory':
            oracles.append({'job_id':'invalid_'+cid,'alphabet':['a','b'],'compatible_rgs':[],'count':0,'method':'direct identical opposite labels'})
            jobs.append({'job_id':'contradictory_K1','case_id':cid,'input':str(p.resolve()),'input_sha256':h,'allowed_k':[1],'expectation':'incompatible'})
            oracles.append({'job_id':'contradictory_K1','alphabet':['a','b'],'compatible_rgs':[],'count':0,'method':'direct identical opposite labels'})
    valid=next(j for j in jobs if j['job_id']=='empty_both_noK')
    for tag,value in [('zero',0),('too_large',4),('boolean',True),('float',1.5),('string','2')]:jobs.append({**valid,'job_id':'invalid_known_k_'+tag,'api_known_k':value,'expectation':'invalid'})
    save(A/'CASE_MANIFEST_V1.json',{'cases':cases,'jobs':jobs,'provider_truth_inputs':False,'held_count':217,'new_random_count':200,'structured_count':3,'no_source_execution_before_GO':True})
    save(A/'ORACLES_V1.json',{'jobs':oracles});print(json.dumps({'cases':len(cases),'jobs':len(jobs),'exact_oracles':len(oracles)}))
if __name__=='__main__':main()
