"""Sufficient passive ownership certificates; optional explicitly trusted K."""
import argparse,json
from pathlib import Path
def solve(data,known_k=None):
    if not isinstance(data,dict) or set(data)!={'alphabet','positive','negative'}:raise ValueError('input must contain exactly alphabet/positive/negative')
    alphabet=data['alphabet']
    if not isinstance(alphabet,list) or not alphabet or any(not isinstance(x,str) or len(x)!=1 for x in alphabet) or len(set(alphabet))!=len(alphabet):raise ValueError('invalid alphabet')
    alphabet=sorted(alphabet);symbols=set(alphabet)
    if any(not isinstance(data[l],list) or any(not isinstance(w,str) or set(w)-symbols for w in data[l]) for l in ['positive','negative']):raise ValueError('invalid words')
    P=sorted(set(data['positive']));N=sorted(set(data['negative']))
    if set(P)&set(N):raise ValueError('contradictory labels')
    if known_k is not None and (type(known_k)is not int or not 1<=known_k<=len(alphabet)):raise ValueError('known_k must be an explicit integer in1..m')
    parent={x:x for x in alphabet}
    def root(x):
        while parent[x]!=x:x=parent[x]
        return x
    edges=[]
    for p in P:
        for n in N:
            if len(p)!=len(n):continue
            diff=[i for i,(x,y) in enumerate(zip(p,n)) if x!=y]
            if len(diff)!=2 or diff[1]!=diff[0]+1:continue
            i,j=diff
            if p[i]==p[j] or p[i]!=n[j] or p[j]!=n[i]:continue
            a,b=root(p[i]),root(p[j]);parent[max(a,b)]=min(a,b)
            edges.append({'positive':p,'negative':n,'positions':[i,j],'symbols':[p[i],p[j]]})
    groups={}
    for x in alphabet:groups.setdefault(root(x),[]).append(x)
    components=sorted(groups.values());owners={x:i for i,g in enumerate(components) for x in g}
    def project(word):
        out=[[] for _ in components]
        for x in word:out[owners[x]].append(x)
        return [''.join(w) for w in out]
    languages=[set() for _ in components]
    for p in P:
        for i,value in enumerate(project(p)):languages[i].add(value)
    witnesses=[];compatible=True
    for n in N:
        projections=project(n);reject=[i for i,value in enumerate(projections) if value not in languages[i]]
        compatible=compatible and bool(reject);witnesses.append({'word':n,'projections':projections,'rejected_by_blocks':reject})
    r=len(components);status='certificate_not_established';unique=None
    if compatible:
        if known_k is None:
            status='certified_finest_compatible_partition';unique=components if r==1 else None
        elif r==known_k:status='certified_unique_partition_under_trusted_k';unique=components
    return {'status':status,'complete_certificate_check':True,'alphabet':alphabet,'forced_same_components':components,'swap_witnesses':edges,'component_partition_sample_compatible':compatible,'component_projection_witness':{'partition':components,'positive_projection_languages':[sorted(x) for x in languages],'negative_witnesses':witnesses},'compatible_family':{'kind':'all_coarsenings_of_components','atoms':components} if compatible else None,'finest_compatible_partition':components if compatible else None,'unique_partition':unique,'known_k_explicit_argument':known_k,'physical_truth_read':False,'assumptions':['independent regular factors on disjoint known alphabets','exact labels']+(['trusted exact component count supplied explicitly'] if known_k is not None else []),'coverage_claim':'Not verified from data; no unobserved edge is interpreted as separation.','failure_meaning':'certificate_not_established does not mean no compatible model'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('input',type=Path);ap.add_argument('--known-k',type=int);args=ap.parse_args()
    try:result=solve(json.loads(args.input.read_text(encoding='utf-8-sig')),args.known_k)
    except (ValueError,TypeError,KeyError) as e:print(json.dumps({'status':'invalid_input','error':str(e)}));return 2
    print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0
if __name__=='__main__':raise SystemExit(main())
