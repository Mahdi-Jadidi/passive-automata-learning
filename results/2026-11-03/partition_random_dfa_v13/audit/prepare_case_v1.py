"""Captured preparation only; generator execution requires runner approval."""
import argparse,hashlib,importlib.util,json,time
from pathlib import Path
A=Path(__file__).resolve().parent; R=A.parent
G=R/'implementation/generate_v1.py'
def save(p,v):
    raw=(json.dumps(v,ensure_ascii=False,sort_keys=True)+'\n').encode()
    with p.open('xb') as f:f.write(raw)
    return hashlib.sha256(raw).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--k',type=int,required=True);ap.add_argument('--m',type=int,required=True);ap.add_argument('--length',type=int,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--small',action='store_true');a=ap.parse_args()
    assert hashlib.sha256(G.read_bytes()).hexdigest()=='0b649344035f449b0a17cd6410dd41db67c6b1e06025b78262807740b93ba410'
    spec=importlib.util.spec_from_file_location('frozen_generator',G);gen=importlib.util.module_from_spec(spec);spec.loader.exec_module(gen)
    a.out.mkdir(parents=True,exist_ok=False);started=time.perf_counter();world=gen.build_world(20261103,a.k,a.m)
    world_seconds=time.perf_counter()-started
    data,stats=gen.generate(world,a.length,8,20261103,'near-max',800,'uniform')
    save(a.out/'world.json',world);save(a.out/'generation.json',stats)
    # Independent table/owner and label replay; no generator replay calls.
    start=time.perf_counter();devices=world['devices'];owner=world['ownership']
    assert len(devices)==a.k and len(owner)==a.m and set(owner)==set(data['alphabet'])
    for i,d in enumerate(devices):
        assert d['id']==i and d['start'] in d['states'] and set(d['accepting'])<=set(d['states'])
        assert d['start'] in d['accepting'] and set(d['states'])-set(d['accepting'])
        assert all(owner[ch]==i for ch in d['alphabet'])
        assert len(d['transitions'])==len(d['states'])
        for table in d['transitions']:assert set(table)==set(d['alphabet']) and set(table.values())<=set(d['states'])
        for state in d['states']:
            seen={state};todo=[state]
            while todo:
                for dest in d['transitions'][todo.pop()].values():
                    if dest not in seen:seen.add(dest);todo.append(dest)
            assert seen==set(d['states'])
    records={(x['label'],x['index']):x for x in stats['samples']};lengths=[];runs=[]
    for label in ['positive','negative']:
        assert len(data[label])==len(set(data[label]))
        for idx,word in enumerate(data[label]):
            states=[d['start'] for d in devices]
            for ch in word:
                device=owner[ch];states[device]=devices[device]['transitions'][states[device]][ch]
            accepted=all(states[i] in d['accepting'] for i,d in enumerate(devices))
            assert accepted==(label=='positive') and len(word)<=a.length
            record=records[label,idx];run=sum(i==0 or ch!=word[i-1] for i,ch in enumerate(word))
            assert record['final_states']==states and record['length']==len(word) and record['run_count']==run
            lengths.append(len(word));runs.append(run)
    assert not set(data['positive'])&set(data['negative'])
    replay_seconds=time.perf_counter()-start
    assert stats['complete'],'sample shortfall; saved world and generation statistics are retained'
    derived={**data,'positive':data['positive'][:2],'negative':data['negative'][:2]}
    h8=save(a.out/'input8.json',data);h2=save(a.out/'input2.json',derived)
    nesting_test='derived exact prefix; count independence statically reviewed'
    if a.small:
        direct,st=gen.generate(world,a.length,2,20261103,'near-max',200,'uniform')
        save(a.out/'direct2_generation.json',st);assert st['complete'] and direct==derived
        nesting_test='independent count2 call equals first2 of count8'
    save(a.out/'validation.json',{'status':'independent_labels_and_nesting_passed','world_generation_seconds':world_seconds,'sample_generation_seconds':stats['generation_seconds'],'independent_label_replay_seconds':replay_seconds,'input8_sha256':h8,'input2_sha256':h2,'input2_parent_sha256':h8,'nesting':nesting_test,'actual_lengths8':lengths,'run_counts8':runs,'total_characters8':sum(lengths),'wall_preparation_seconds':time.perf_counter()-started})
    print(json.dumps({'status':'prepared','path':str(a.out)}))
if __name__=='__main__':main()
