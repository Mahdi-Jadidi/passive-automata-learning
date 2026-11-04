"""C020 deterministic large-minimal DFA fixtures; no solver imports. Post-GO."""
from pathlib import Path
import hashlib,json,random,time
A=Path(__file__).resolve().parent
SPECS=[('A',64,4,512,4096,202611042001),('B',256,8,128,65536,202611042002),('C',1024,20,16,1000000,202611042003)]
def rng(seed,purpose):return random.Random(int.from_bytes(hashlib.sha256(f'{seed}:{purpose}'.encode()).digest(),'big'))
def save(path,value):
    with path.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def world(seed,s,k):
    alpha=list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'[:2*k]);order=alpha.copy();rng(seed,'ownership').shuffle(order);devices=[];owner={};attempts=[]
    for i in range(k):
        aa,bb=sorted(order[2*i:2*i+2]);permutation=None
        for trial in range(1,11):
            p=list(range(s));rng(seed,f'permutation:{i}:{trial}').shuffle(p)
            if any(p[(q+1)%s]!=(p[q]+1)%s for q in range(s)):permutation=p;break
        if permutation is None:raise RuntimeError('noncommuting permutation generation exhausted10attempts')
        devices.append(dict(id=i,states=list(range(s)),start=0,accepting=[0],alphabet=[aa,bb],transitions=[{aa:(q+1)%s,bb:permutation[q]} for q in range(s)],kind='cycle_random_permutation',cycle_symbol=aa,permutation_symbol=bb))
        owner.update({aa:i,bb:i});attempts.append(trial)
    return dict(alphabet=alpha,devices=devices,ownership=owner,seed=seed,kind='cycle_random_permutation',permutation_attempts=attempts)
def replay(word,w):
    states=[d['start'] for d in w['devices']];owner=w['ownership'];tables=[d['transitions'] for d in w['devices']]
    for ch in word:
        i=owner[ch];states[i]=tables[i][states[i]][ch]
    return all(q in d['accepting'] for q,d in zip(states,w['devices'])),states
def conditional(w,n,limit):
    k=len(w['devices']);s=len(w['devices'][0]['states']);prefix_size=limit-k*(s-1);assert prefix_size>0;words={True:[],False:[]};records=[];seen=set();attempt_total=0;duplicates=0
    for label in [True,False]:
        for index in range(n):
            for attempt in range(1,4):
                attempt_total+=1;r=rng(w['seed'],f'word:{label}:{index}:{attempt}');prefix=''.join(r.choices(w['alphabet'],k=prefix_size));_,states=replay(prefix,w);reject=None if label else index%k;tails=[];repairs=[]
                for i,d in enumerate(w['devices']):
                    target=1 if i==reject else 0;count=(target-states[i])%s;tails.append(d['cycle_symbol']*count);repairs.append(count)
                word=prefix+''.join(tails);assert len(word)<=limit
                actual,terminal=replay(word,w);assert actual==label
                if word in seen:duplicates+=1;continue
                seen.add(word);words[label].append(word);records.append(dict(label='positive' if label else 'negative',index=index,attempt=attempt,prefix_length=prefix_size,repair_lengths=repairs,repair_length=sum(repairs),actual_length=len(word),reject_device=reject,terminal_states=terminal,word_sha256=hashlib.sha256(word.encode()).hexdigest()));break
            else:raise RuntimeError('unique conditional observation exhausted3attempts')
        print(json.dumps(dict(progress='base_class_generated',label=label,count=n,cap=limit,seed=w['seed'])),flush=True)
    return words,records,dict(attempts=attempt_total,duplicate_attempts=duplicates,wrong_label_rejections=0,requested_per_label=n,distribution='uniform iid symbol prefix; deterministic cycle-symbol target-state repair; label-conditioned, not passive iid words')
def anchors(w):
    pieces=[];positions=[];offset=0
    for d in w['devices']:
        s=len(d['states']);aa=d['cycle_symbol'];bb=d['permutation_symbol'];table=d['transitions'];q=next(q for q in range(s) if table[(q+1)%s][bb]!=(table[q][bb]+1)%s);after=table[(q+1)%s][bb];piece=aa*(s+q)+aa+bb+aa*((-after)%s);positions.append(offset+s+q);pieces.append(piece);offset+=len(piece)
    p=''.join(pieces);assert replay(p,w)[0];neg=[]
    for pos in positions:
        chars=list(p);chars[pos],chars[pos+1]=chars[pos+1],chars[pos];n=''.join(chars);assert not replay(n,w)[0];neg.append(n)
    return p,neg,positions
def finite_world(seed,k=4,r=128):
    alpha=list('abcdefgh');order=alpha.copy();rng(seed,'ownership').shuffle(order);devices=[];owner={};sink=2*r+1
    for i in range(k):
        aa,bb=sorted(order[2*i:2*i+2]);tables=[{aa:sink,bb:sink} for _ in range(sink+1)]
        for q in range(2*r):tables[q][aa if q<r else bb]=q+1
        devices.append(dict(id=i,states=list(range(sink+1)),start=0,accepting=[0,2*r],alphabet=[aa,bb],transitions=tables,kind='epsilon_or_fixed_runword',run=r,first_symbol=aa,second_symbol=bb));owner.update({aa:i,bb:i})
    return dict(alphabet=alpha,devices=devices,ownership=owner,seed=seed,kind='epsilon_or_fixed_runword')
def main():
    start=time.perf_counter();root=A/'fixtures_v1';root.mkdir(exist_ok=False);items=[]
    for name,s,k,n,L,seed in SPECS:
        began=time.perf_counter();directory=root/name;directory.mkdir();w=world(seed,s,k);samples,records,attempts=conditional(w,n,L);p,neg,positions=anchors(w)
        assert len(p)<=L and p not in samples[True] and not set(neg).intersection(samples[False]);P=samples[True]+[p];N=samples[False]+neg;assert len(set(P))==len(P) and len(set(N))==len(N) and set(P).isdisjoint(N)
        data=dict(alphabet=w['alphabet'],positive=P,negative=N);meta=dict(base_per_label=n,positive_base_indices=list(range(n)),negative_base_indices=list(range(n)),positive_anchor_index=n,negative_anchor_indices=list(range(n,n+k)),anchor_adjacent_positions=positions,anchor_length=len(p),records=records,attempts=attempts,actual_lengths={'positive':list(map(len,P)),'negative':list(map(len,N))},generation_seconds=time.perf_counter()-began)
        for filename,x in [('solver_input.json',data),('world.json',w),('generation.json',meta)]:save(directory/filename,x)
        items.append(dict(case_id=name,source_seed=seed,states=s,generator_K=k,alphabet_size=2*k,base_per_label=n,max_length=L,input=str(directory/'solver_input.json'),input_sha256=sha(directory/'solver_input.json'),world=str(directory/'world.json'),world_sha256=sha(directory/'world.json'),generation=str(directory/'generation.json'),generation_sha256=sha(directory/'generation.json')))
        print(json.dumps(dict(progress='fixture_saved',case_id=name,seconds=time.perf_counter()-began)),flush=True)
    directory=root/'D';directory.mkdir();w=finite_world(202611042004);P=['']+[d['first_symbol']*128+d['second_symbol']*128 for d in w['devices']];N=[d['second_symbol']*128+d['first_symbol']*128 for d in w['devices']];assert all(replay(p,w)[0] for p in P) and all(not replay(n,w)[0] for n in N)
    save(directory/'solver_input.json',dict(alphabet=w['alphabet'],positive=P,negative=N));save(directory/'world.json',w);save(directory/'generation.json',dict(kind='finite_graph_empty_certified',run=128,positive_count=5,negative_count=4,conditioning='exact finite language construction'))
    items.append(dict(case_id='D',source_seed=202611042004,states=258,generator_K=4,alphabet_size=8,max_length=256,input=str(directory/'solver_input.json'),input_sha256=sha(directory/'solver_input.json'),world=str(directory/'world.json'),world_sha256=sha(directory/'world.json'),generation=str(directory/'generation.json'),generation_sha256=sha(directory/'generation.json')))
    cells=[dict(case_id=name,known_k=k,cell_id=name+('_unknown' if k is None else '_K'+str(k))) for name,k in [('A',None),('A',4),('B',None),('B',8),('C',None),('D',4)]]
    save(A/'FIXTURE_MANIFEST_V1.json',dict(inputs=items,cells=cells,elapsed_seconds=time.perf_counter()-start,hidden_metadata_not_solver_input=True))
    print(json.dumps(dict(status='fixtures_generated',unique_inputs=4,timing_cells=6,total_seconds=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
