"""Independent saved-table label/minimality/coverage audit; imports no generator."""
from pathlib import Path
import hashlib,json,time
from collections import deque
A=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def rgs(n):
    def rec(p,mx):
        if len(p)==n:yield p;return
        for x in range(mx+2):yield from rec(p+(x,),max(mx,x))
    yield from rec((0,),0)
def stirling(n):
    row=[1]+[0]*n
    for i in range(1,n+1):row=[0]+[row[j-1]+j*row[j] for j in range(1,n+1)]
    return row
def main():
    began=time.perf_counter();manifest=read(A/'FIXTURE_MANIFEST_V1.json');results=[]
    for item in manifest['inputs']:
        assert sha(item['input'])==item['input_sha256'] and sha(item['world'])==item['world_sha256'] and sha(item['generation'])==item['generation_sha256'];d=read(item['input']);w=read(item['world']);meta=read(item['generation']);dev=w['devices'];k=len(dev);owner=w['ownership'];assert set(owner)==set(d['alphabet']) and k==item['generator_K']
        observed=[set() for _ in dev];base_visited=[set() for _ in dev];base_a=[set() for _ in dev];base_b=[set() for _ in dev];terminal=[dict(accept=0,reject=0,base_accept=0,base_reject=0) for _ in dev];lengths=[[] for _ in dev];states=[];minimal=[];seen=set()
        for i,v in enumerate(dev):
            s=len(v['states']);assert v['id']==i and v['states']==list(range(s)) and v['start'] in v['states'] and set(v['accepting'])<=set(v['states']);assert len(v['transitions'])==s and v['alphabet'] and not seen.intersection(v['alphabet']);seen.update(v['alphabet']);assert all(owner[a]==i for a in v['alphabet'])
            for row in v['transitions']:assert set(row)==set(v['alphabet']) and all(type(q)is int and 0<=q<s for q in row.values())
            visited={v['start']};pending=deque(visited)
            while pending:
                q=pending.popleft()
                for nxt in v['transitions'][q].values():
                    if nxt not in visited:visited.add(nxt);pending.append(nxt)
            assert len(visited)==s
            if w['kind']=='cycle_random_permutation':
                aa,bb=v['cycle_symbol'],v['permutation_symbol'];assert set([aa,bb])==set(v['alphabet']) and v['start']==0 and v['accepting']==[0]
                assert all(v['transitions'][q][aa]==(q+1)%s for q in range(s));assert {row[bb] for row in v['transitions']}==set(range(s));assert any(v['transitions'][(q+1)%s][bb]!=(v['transitions'][q][bb]+1)%s for q in range(s));proof='single_accepting_state_on_complete_a_cycle_distinguishes_all_states'
            else:
                r=v['run'];aa,bb=v['first_symbol'],v['second_symbol'];sink=2*r+1;assert s==2*r+2 and v['start']==0 and v['accepting']==[0,2*r]
                for q in range(s):
                    expected={aa:sink,bb:sink}
                    if q<2*r:expected[aa if q<r else bb]=q+1
                    assert v['transitions'][q]==expected
                proof='distinct_single_suffix_prefix_residuals_plus_accepting_start_and_rejecting_sink'
            minimal.append(dict(declared=s,structurally_reachable=s,certified_minimal=s,minimality_proof=proof));states.append(s)
        assert seen==set(d['alphabet']);assert set(d['positive']).isdisjoint(d['negative']) and all(len(set(d[label]))==len(d[label]) for label in ['positive','negative'])
        if item['case_id']!='D':assert len(d['positive'])==item['base_per_label']+1 and len(d['negative'])==item['base_per_label']+k
        for label in ['positive','negative']:
            for wi,word in enumerate(d[label]):
                assert len(word)<=item['max_length'];qs=[v['start'] for v in dev];counts=[0]*k;is_base=item['case_id']!='D' and wi<item['base_per_label']
                for i,q in enumerate(qs):observed[i].add(q)
                if is_base:
                    for i,q in enumerate(qs):base_visited[i].add(q)
                for ch in word:
                    i=owner[ch];v=dev[i];q=qs[i]
                    if is_base:(base_a[i] if ch==v['cycle_symbol'] else base_b[i]).add(q)
                    q=v['transitions'][q][ch];qs[i]=q;counts[i]+=1;observed[i].add(q)
                    if is_base:base_visited[i].add(q)
                accepted=[]
                for i,q in enumerate(qs):
                    ok=q in dev[i]['accepting'];accepted.append(ok);terminal[i]['accept' if ok else 'reject']+=1
                    if is_base:terminal[i]['base_accept' if ok else 'base_reject']+=1
                    lengths[i].append(counts[i])
                assert all(accepted)==(label=='positive')
                if wi%16==0:print(json.dumps(dict(progress='label_replay',case_id=item['case_id'],label=label,index=wi)),flush=True)
        oracle={}
        if item['case_id']!='D':
            pi=meta['positive_anchor_index'];p=d['positive'][pi];assert len(meta['negative_anchor_indices'])==len(meta['anchor_adjacent_positions'])==k
            for i,(ni,pos) in enumerate(zip(meta['negative_anchor_indices'],meta['anchor_adjacent_positions'])):
                n=d['negative'][ni];assert pos+1<len(p) and p[pos]!=p[pos+1] and set([p[pos],p[pos+1]])==set(dev[i]['alphabet']);assert n==p[:pos]+p[pos+1]+p[pos]+p[pos+2:]
            oracle=dict(method='K disjoint sound adjacent_swap_edges plus independently_verified_truth_model',forced_groups=[v['alphabet'] for v in dev],counts_by_k=stirling(k),unknown_status='ambiguous',trusted_K_status='certified_unique')
        else:
            alpha=sorted(d['alphabet']);families={str(q):[] for q in range(len(alpha)+1)}
            for key in rgs(len(alpha)):
                groups=[[] for _ in range(max(key)+1)]
                for a,gi in zip(alpha,key):groups[gi].append(a)
                positive_images=[{''.join(a for a in p if a in group) for p in d['positive']} for group in groups]
                if all(any(''.join(a for a in n if a in group) not in positive_images[gi] for gi,group in enumerate(groups)) for n in d['negative']):families[str(max(key)+1)].append(list(key))
            assert [len(families[str(q)]) for q in range(9)]==stirling(k)+[0]*(8-k)
            for p in d['positive']:
                for n in d['negative']:
                    diff=[i for i,(a,b) in enumerate(zip(p,n)) if a!=b] if len(p)==len(n) else []
                    assert not (len(diff)==2 and diff[1]==diff[0]+1 and p[diff[0]]==n[diff[1]] and p[diff[1]]==n[diff[0]])
            oracle=dict(method='direct_full_Bell8_projection_enumeration',families_by_k=families,trusted_K_status='certified_unique',unknown_status='ambiguous',adjacent_swap_graph_edges=0)
        coverage=[]
        for i,v in enumerate(dev):
            assert len(observed[i])==states[i];coverage.append(dict(device=i,**minimal[i],observed_visited=len(observed[i]),base_observed_visited=len(base_visited[i]),base_used_cycle_transition_states=len(base_a[i]),base_used_permutation_transition_states=len(base_b[i]),terminal_outcomes=terminal[i],projection_lengths=dict(min=min(lengths[i]),max=max(lengths[i]),mean=sum(lengths[i])/len(lengths[i]),zero_count=lengths[i].count(0))))
        results.append(dict(case_id=item['case_id'],status='accepted_labels_minimality_and_scope',T=sum(map(len,d['positive']+d['negative'])),class_counts={label:len(d[label]) for label in ['positive','negative']},actual_word_lengths={label:dict(min=min(map(len,d[label])),max=max(map(len,d[label])))) for label in ['positive','negative']},coverage=coverage,oracle=oracle,input_sha256=item['input_sha256'],world_sha256=item['world_sha256']))
        print(json.dumps(dict(progress='fixture_audit_complete',case_id=item['case_id'],elapsed=time.perf_counter()-began)),flush=True)
    report=dict(status='accepted',fixtures=results,elapsed_seconds=time.perf_counter()-began,solver_imports=False,notes=['conditional base sampling and planted informative anchors explicitly separated','minimality proven from independently checked transition structure, not declarations','world metadata must never be supplied to solver'])
    with (A/'FIXTURE_AUDIT_V1.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(status='accepted',fixtures=len(results),elapsed_seconds=report['elapsed_seconds'])),flush=True)
if __name__=='__main__':main()
