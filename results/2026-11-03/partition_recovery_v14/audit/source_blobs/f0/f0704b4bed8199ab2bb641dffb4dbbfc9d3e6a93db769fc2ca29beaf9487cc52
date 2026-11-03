"""Independent saved-world replay and complete finite-sample RGS oracle."""
import hashlib,importlib.util,itertools,json,time
from collections import Counter
from pathlib import Path
A=Path(__file__).resolve().parent;R=A.parent
C=R.parent.parent/'2026-11-02/partition_unrestricted_v10/audit/validate_provider_v2.py'
s=importlib.util.spec_from_file_location('independent',C);old=importlib.util.module_from_spec(s);s.loader.exec_module(old)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replay(data,world):
    owner=world['ownership'];devices=world['devices'];assert set(owner)==set(data['alphabet'])
    for i,d in enumerate(devices):
        assert d['id']==i and all(owner[x]==i for x in d['alphabet'])
        assert len(d['transitions'])==len(d['states']) and set(d['accepting'])<=set(d['states'])
        for table in d['transitions']:assert set(table)==set(d['alphabet']) and set(table.values())<=set(d['states'])
    for label in ['positive','negative']:
        for word in data[label]:
            states=[d['start'] for d in devices]
            for x in word:
                i=owner[x];states[i]=devices[i]['transitions'][states[i]][x]
            assert all(states[i] in d['accepting'] for i,d in enumerate(devices))==(label=='positive')
def graph(data):
    alphabet=sorted(data['alphabet']);parent={x:x for x in alphabet};edges=[]
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    for p in data['positive']:
        for n in data['negative']:
            if len(p)!=len(n):continue
            differences=[i for i in range(len(p)) if p[i]!=n[i]]
            if len(differences)!=2:continue
            i,j=differences
            if j==i+1 and p[i]!=p[j] and p[i]==n[j] and p[j]==n[i]:
                a,b=find(p[i]),find(p[j]);parent[max(a,b)]=min(a,b);edges.append([p[i],p[j]])
    groups={}
    for x in alphabet:groups.setdefault(find(x),[]).append(x)
    return sorted(groups.values()),edges
def main():
    manifest=json.loads((A/'DATA_MANIFEST_V1.json').read_text());out=[];held=[];replay_seconds=0
    for c in manifest['small_cases']+manifest['timing_cases']:
        p=Path(c['path']);assert sha(p)==c['sha256'];raw=json.loads(p.read_text());data={k:sorted(set(raw[k])) if k!='alphabet' else sorted(raw[k]) for k in ['alphabet','positive','negative']}
        assert not set(data['positive'])&set(data['negative']) and all(set(w)<=set(data['alphabet']) for w in data['positive']+data['negative'])
        world=json.loads(Path(c['world']).read_text()) if 'world' in c else None
        if world:
            t=time.perf_counter();replay(data,world);replay_seconds+=time.perf_counter()-t
        if c['kind']=='held_timing':
            pos=[Counter(w) for w in data['positive']];sets={a:{p.get(a,0) for p in pos} for a in data['alphabet']}
            predicate=all(any(counts.get(a,0) not in sets[a] for a in data['alphabet']) for counts in map(Counter,data['negative']))
            row=[1];bells=[1]
            for n in range(1,len(data['alphabet'])+1):
                row=[0]+[(row[k-1] if k-1<len(row) else 0)+(k*row[k] if k<len(row) else 0) for k in range(1,n+1)];bells.append(sum(row))
            held.append({'case_id':c['case_id'],'input_sha256':c['sha256'],'predicate':predicate,'exact_count_oracle':predicate,'partition_count':bells[-1] if predicate else None,'partition_count_by_k':{str(k):v for k,v in enumerate(row) if k>0} if predicate else None,'same_pair_count':bells[-2] if predicate else None,'alphabet':data['alphabet']})
            continue
        expected=old.direct_expected(data);m=len(data['alphabet']);spectrum={str(k):sum(max(x)+1==k for x in expected) for k in range(1,m+1)}
        pairs=[{'symbols':[data['alphabet'][i],data['alphabet'][j]],'same':sum(x[i]==x[j] for x in expected),'different':sum(x[i]!=x[j] for x in expected)} for i,j in itertools.combinations(range(m),2)]
        components,edges=graph(data);compatible=old.feasible(data,components)
        if compatible:
            component_rgs=old.partition_rgs(components,data['alphabet'])
            assert all(all(component_rgs[i]!=component_rgs[j] or x[i]==x[j] for i,j in itertools.combinations(range(m),2)) for x in expected)
        oracle={'case_id':c['case_id'],'input_sha256':c['sha256'],'compatible_rgs':sorted(expected),'partition_count':len(expected),'partition_count_by_k':spectrum,'pairs':pairs,'components':components,'component_partition_compatible':compatible}
        if c['kind']=='calibration':
            k=world['true_devices'];truth=old.partition_rgs([d['alphabet'] for d in world['devices']],data['alphabet'])
            assert truth in expected and all(world['ownership'][x]==world['ownership'][y] for x,y in edges)
            oracle.update(truth_rgs=truth,known_k_explicit_oracle_analysis=k,known_k_compatible_rgs=sorted(x for x in expected if max(x)+1==k),components_equal_truth=old.partition_rgs(components,data['alphabet'])==truth,coverage_verified_from_truth_is_external_evaluation=True)
        out.append(oracle)
    with (A/'SMALL_ORACLES_V1.json').open('x') as f:json.dump({'cases':out,'independent_label_replay_seconds':replay_seconds,'small_count':len(out),'held_timing_count':4},f,indent=2)
    with (A/'HELD_ORACLES_V1.json').open('x') as f:json.dump({'cases':held,'method':'independent Counter unary criterion + Bell/Stirling recurrence'},f,indent=2)
    print(json.dumps({'status':'data_and_full_oracles_verified','small_count':len(out),'held_timing_count':4,'independent_label_replay_seconds':replay_seconds}))
if __name__=='__main__':main()
