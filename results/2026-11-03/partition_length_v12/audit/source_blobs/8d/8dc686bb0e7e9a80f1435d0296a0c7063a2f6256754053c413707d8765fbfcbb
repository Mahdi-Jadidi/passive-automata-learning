import hashlib,json
from pathlib import Path
A=Path(__file__).resolve().parent
groups=[list(x) for x in ['ab','cd','ef','gh']]
def sha(b): return hashlib.sha256(b).hexdigest()
def save(path,obj):
    raw=(json.dumps(obj,ensure_ascii=False,sort_keys=True)+'\n').encode()
    with path.open('xb') as f:f.write(raw)
    return sha(raw)
def proj(w,g):return ''.join(x for x in w if x in g)
def main():
    cells=[]; certs=[]; (A/'cases').mkdir()
    for family,lengths in [('lowrun',[100000,300000,1000000]),('highrun',[10000,30000,100000])]:
        for L in lengths:
            context='a'*(L-2) if family=='lowrun' else ('abcdefgh'*((L+5)//8))[:L-2]
            d={'alphabet':list('abcdefgh'),'positive':[x+y+context for x,y in groups],'negative':[y+x+context for x,y in groups]}
            assert len(set(d['positive']))==len(set(d['negative']))==4 and not set(d['positive'])&set(d['negative'])
            assert all(len(w)==L for w in d['positive']+d['negative'])
            edges=set()
            for p in d['positive']:
                for n in d['negative']:
                    diff=[i for i,(x,y) in enumerate(zip(p,n)) if x!=y]
                    if len(diff)==2 and diff[1]==diff[0]+1:
                        i,j=diff
                        if p[i]==n[j] and p[j]==n[i]: edges.add(tuple(sorted((p[i],p[j]))))
            assert edges=={tuple(g) for g in groups}
            langs=[{proj(p,set(g)) for p in d['positive']} for g in groups]
            assert all(any(proj(n,set(g)) not in lang for g,lang in zip(groups,langs)) for n in d['negative'])
            if family=='lowrun' and L==100000:
                previous=A.parent.parent/'partition_large_v11/audit/cases/performance_v2/scale_long_word_100000_m8.json'
                assert d==json.loads(previous.read_text())
            cid=f'{family}_L{L}'; path=A/'cases'/f'{cid}.json'; h=save(path,d)
            runs=[sum(i==0 or w[i]!=w[i-1] for i in range(len(w))) for w in d['positive']+d['negative']]
            cells.append({'case_id':cid,'family':family,'length':L,'actual_lengths':[len(w) for w in d['positive']+d['negative']],'run_counts':runs,'total_characters':8*L,'path':str(path.relative_to(A)),'input_sha256':h,'memory_probe':L==lengths[-1]})
            certs.append({'case_id':cid,'input_sha256':h,'atoms':groups,'atom_count':4,'expected_partition_count':15,'expected_partition_count_by_k':{'1':1,'2':7,'3':6,'4':1,'5':0,'6':0,'7':0,'8':0},'same_count_across_atoms':5,'proof':'All four chain edges independently replayed from opposite-label adjacent swaps; atom partition independently rejects each negative. Sound must-links plus coarsening closure imply exactly all coarsenings of four atoms.','adjacent_edges':sorted(edges),'atom_partition_feasible':True})
    save(A/'PERFORMANCE_MANIFEST_V2.json',{'cells':cells})
    save(A/'PERFORMANCE_FAMILY_CERTIFICATES_V3.json',{'certificates':certs})
    print(json.dumps({'status':'independent_family_certificates_passed','cells':6,'partition_count_each':15,'run_counts':[c['run_counts'] for c in cells]}))
if __name__=='__main__':main()
