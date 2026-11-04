"""Tiny independent partition oracle; no solver or prior feasibility imports."""
import hashlib,json,time
from pathlib import Path
from collections import Counter
A=Path(__file__).resolve().parent
def rgs(n):
    def walk(prefix,maximum):
        if len(prefix)==n:yield tuple(prefix);return
        for x in range(maximum+2):yield from walk(prefix+(x,),max(maximum,x))
    if n==0:yield ()
    else:yield from walk((0,),0)
def blocks(key,alphabet):
    answer=[[] for _ in range(max(key)+1)]
    for x,b in zip(alphabet,key):answer[b].append(x)
    return answer
def witness(data,key):
    groups=blocks(key,data['alphabet']);languages=[]
    for group in groups:
        allowed=set(group);languages.append({''.join(x for x in p if x in allowed) for p in data['positive']})
    refs=[]
    for ni,word in enumerate(data['negative']):
        reject=[]
        for bi,group in enumerate(groups):
            allowed=set(group);value=''.join(x for x in word if x in allowed)
            if value not in languages[bi]:reject.append(bi)
        if not reject:return None
        refs.append(dict(negative_index=ni,rejecting_blocks=reject))
    return dict(rgs=key,blocks=groups,negative_rejections=refs)
def inspect(case_id,data,claim):
    assert set(data)=={'alphabet','positive','negative'}
    assert len(set(data['alphabet']))==len(data['alphabet']) and set(data['positive']).isdisjoint(data['negative'])
    m=len(data['alphabet']);families={str(k):[] for k in range(m+1)}
    for key in rgs(m):
        w=witness(data,key)
        if w is not None:families[str(max(key)+1)].append(w)
    return dict(case_id=case_id,input=data,claim=claim,word_lengths={label:list(map(len,data[label])) for label in ['positive','negative']},word_counts={label:[dict(Counter(w)) for w in data[label]] for label in ['positive','negative']},families_by_k=families,counts_by_k={k:len(v) for k,v in families.items()})
def stirling(n,k):
    table=[[0]*(n+1) for _ in range(n+1)];table[0][0]=1
    for i in range(1,n+1):
        for j in range(1,i+1):table[i][j]=table[i-1][j-1]+j*table[i-1][j]
    return table[n][k] if k<=n else 0
def main():
    began=time.perf_counter();out=[]
    unique=inspect('unique_matched',dict(alphabet=list('abcd'),positive=['abcd'],negative=['bacd','abdc']),'exactly ab|cd under K2')
    assert [w['blocks'] for w in unique['families_by_k']['2']]==[[['a','b'],['c','d']]];out.append(unique)
    ambiguous=inspect('ambiguous_unary_literal',dict(alphabet=list('abcd'),positive=['aabcd'],negative=['abcd','aaabcd']),'all set partitions compatible; a-counts 2 versus1,3')
    assert ambiguous['counts_by_k']=={'0':0,'1':1,'2':7,'3':6,'4':1};out.append(ambiguous)
    strong=inspect('ambiguous_matched',dict(alphabet=list('abcd'),positive=['abcd'],negative=['bacd','badc']),'three K2 partitions despite matched counts,lengths,Parikh vectors')
    assert strong['counts_by_k']['2']==3;assert unique['word_lengths']==strong['word_lengths'];assert unique['word_counts']==strong['word_counts'];out.append(strong)
    for np,nn in [(1,2),(2,1),(3,4),(8,9)]:
        data=dict(alphabet=list('abcd'),positive=['a'*(2*i+2)+'bcd' for i in range(np)],negative=['a'*(2*j+1)+'bcd' for j in range(nn)])
        case=inspect(f'no_count_threshold_P{np}_N{nn}',data,'all partitions: positive even a-count, negative odd a-count')
        assert case['counts_by_k']=={'0':0,'1':1,'2':7,'3':6,'4':1};out.append(case)
    general=[]
    for m in range(2,7):
        alphabet=list('abcdef'[:m]);p=''.join(alphabet)
        for k in range(1,m+1):
            negatives=[];edges=[]
            for i in range(m-k):
                word=list(p);word[i],word[i+1]=word[i+1],word[i];negatives.append(''.join(word));edges.append([alphabet[i],alphabet[i+1]])
            case=inspect(f'forest_m{m}_K{k}',dict(alphabet=alphabet,positive=[p],negative=negatives),'all coarsenings of forest components; unique at target K')
            assert case['counts_by_k']=={str(q):stirling(k,q) for q in range(m+1)}
            target=[alphabet[:m-k+1]]+[[a] for a in alphabet[m-k+1:]]
            assert [w['blocks'] for w in case['families_by_k'][str(k)]]==[target]
            case.update(target_k=k,forest_edges=edges,forest_edge_count=m-k,target_blocks=target)
            general.append(case)
    report=dict(status='passed',independent=True,provider_imports=False,case_count=len(out)+len(general),targeted=out,general=general,checks=dict(unique_example=True,literal_all7_K2=True,strong_matched_lengths_and_counts_ambiguous=True,forest_instances=len(general),all_k_families_saved=True,forest_lower_bound_scope='must-link forest rank only, not necessary negative sample count for arbitrary data'),elapsed_seconds=time.perf_counter()-began)
    dest=A/'ENUMERATION_RESULTS_V1.json'
    with dest.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(status=report['status'],cases=report['case_count'],general_instances=len(general),report_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),elapsed_seconds=report['elapsed_seconds']),sort_keys=True))
if __name__=='__main__':main()
