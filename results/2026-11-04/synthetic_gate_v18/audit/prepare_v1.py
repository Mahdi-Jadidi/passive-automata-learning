"""Post-GO deterministic additions and held manifest bindings; no providers."""
import hashlib,json,random
from pathlib import Path
from oracle_data_v1 import full_family
A=Path(__file__).resolve().parent
ROOT=A.parents[3]
OLD=ROOT/'results/2026-11-04/partition_gate_v15/audit'
HELD=ROOT/'results/2026-11-03/partition_random_dfa_v13/audit'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:json.dump(x,f,ensure_ascii=False,sort_keys=True)
def main():
    held=json.loads((OLD/'CASE_MANIFEST_V1.json').read_text());jobs=held['jobs']
    assert len(jobs)==1638
    oracles={j['job_id']:j for j in json.loads((OLD/'ORACLES_V1.json').read_text())['jobs']}
    for j in jobs:assert sha(j['input'])==j['input_sha256']
    def add(cid,data,k=None,expected=None,deadline=None,all_partitions=False):
        p=A/'data'/f'{cid}.json';save(p,data)
        allowed=None if k is None else [k]
        j=dict(job_id='c018_'+cid,case_id=cid,input=str(p),input_sha256=sha(p),allowed_k=allowed)
        if expected is None:
            if all_partitions:
                from oracle_data_v1 import rgs
                family=list(rgs(len(data['alphabet'])))
            else:family=full_family(data)
            family=[x for x in family if k is None or max(x)+1==k]
            expected='unique' if len(family)==1 else 'ambiguous' if family else 'incompatible'
            oracles[j['job_id']]=dict(job_id=j['job_id'],compatible_rgs=family,count=len(family),method='all-partition unary parity proof' if all_partitions else 'independent direct full RGS')
        j['expectation']=expected
        if deadline is not None:j['deadline_seconds']=deadline
        jobs.append(j)
    c=16384
    for q in sorted({0,1,1023,1024,1025,4095,4096,4097,65535,65536,65537,c-1,c,c+1,2*c-1,2*c,2*c+1}):
        w='a'*q
        add(f'count_boundary_{q}',dict(alphabet=['a','b'],positive=[w],negative=[w+'b']),2)
        add(f'late_unknown_{q}',dict(alphabet=['a','b'],positive=[w+'z'],negative=[]),expected='invalid')
    fixtures=[
      ('unary_failed_then_invalid',dict(alphabet=['a','b'],positive=['ab'],negative=['ba','a'*32768+'z']),None,'invalid'),
      ('contradiction_then_invalid',dict(alphabet=['a','b'],positive=['a'],negative=['a','a'*16384+'z']),1,'invalid'),
      ('contradiction_long_K1',dict(alphabet=['a','b'],positive=['a'*32769]*2,negative=['a'*32769]*2),1,None),
      ('late_malformed_int',dict(alphabet=['a','b'],positive=['a'*32768,7],negative=[]),None,'invalid'),
      ('late_malformed_none',dict(alphabet=['a','b'],positive=['a'],negative=['a',None]),None,'invalid'),
      ('late_malformed_list',dict(alphabet=['a','b'],positive=['a'],negative=[[]]),1,'invalid'),
      ('duplicate_presence',dict(alphabet=['a','b'],positive=['a','a'],negative=['','']),None,None),
      ('zero_absent',dict(alphabet=['a','b'],positive=['a'],negative=['']),None,None),
      ('zero_mixed',dict(alphabet=['a','b'],positive=['','a'],negative=['b']),None,None),
      ('mixed_support',dict(alphabet=['a','b'],positive=['ab','aabb'],negative=['aab']),None,None),
      ('unicode_atomic',dict(alphabet=['é','😀','\u0301','e','\x00',' '],positive=['é😀'*8193,'e\u0301','\x00 '],negative=['😀é'*8193]),None,None),
      ('unicode_not_normalized',dict(alphabet=['é'],positive=['e\u0301'],negative=[]),None,'invalid'),
      ('invalid_unhashable_alphabet',dict(alphabet=[[]],positive=[],negative=[]),None,'invalid'),
      ('invalid_extra_truth',dict(alphabet=['a'],positive=[],negative=[],ownership={'a':0}),None,'invalid'),
      ('graph_empty_unique_noK',dict(alphabet=['a','b'],positive=['aabb'],negative=['bbaa']),None,None),
      ('graph_connected_unique_noK',dict(alphabet=['a','b'],positive=['ab'],negative=['ba']),None,None),
      ('hard_K3_zero',dict(alphabet=list('abcd'),positive=['','aabb','ccdd'],negative=['bbaa','ddcc']),3,None),
      ('parity_K2_ambiguous',dict(alphabet=list('abcd'),positive=['','aa','bb','cc','dd'],negative=list('abcd')),2,None),
      ('no_positive_epsilon',dict(alphabet=['a','b'],positive=[],negative=['']),None,None)]
    for cid,data,k,expect in fixtures:add(cid,data,k,expect)
    add('expired_before_validation',dict(alphabet=['a'],positive=['z'],negative=[]),expected='timeout',deadline=0)
    add('expired_valid',dict(alphabet=['a','b'],positive=[],negative=[]),expected='timeout',deadline=0)
    for seed in [2026110418,2026110419]:
        rng=random.Random(seed);words={True:set(),False:set()}
        while any(len(v)<2048 for v in words.values()):
            w=''.join(rng.choice('abcdefgh') for _ in range(16));label=w.count('a')%2==0
            if len(words[label])<2048:words[label].add(w)
        data=dict(alphabet=list('abcdefgh'),positive=sorted(words[True]),negative=sorted(words[False]))
        assert {w.count('a')%2 for w in data['positive']}=={0} and {w.count('a')%2 for w in data['negative']}=={1}
        add(f'many_short_parity_{seed}',data,all_partitions=True)
    grid=json.loads((HELD/'GRID_INPUT_MAP_V4.json').read_text());perf=[]
    for k,L in [(1,1000000),(20,1000000),(4,4096),(10,4096)]:
        g=grid['entries'][f'{k}:{L}'];d=Path(g['directory'])
        for n in [2,8]:
            p=d/f'input{n}.json';w=d/'world.json'
            assert sha(p)==g[f'input{n}_sha256'] and sha(w)==g['world_sha256']
            perf.append(dict(case_id=f'K{k}_L{L}_N{n}',input=str(p),input_sha256=sha(p),world=str(w),world_sha256=sha(w),generator_k=k,max_length=L,samples_per_label=n,solver_known_k=None))
    save(A/'CASE_MANIFEST_V1.json',dict(jobs=jobs,performance=perf,held_jobs=1638,added_jobs=len(jobs)-1638,scope='synthetic_only',source_manifests={str(OLD/'CASE_MANIFEST_V1.json'):sha(OLD/'CASE_MANIFEST_V1.json'),str(OLD/'ORACLES_V1.json'):sha(OLD/'ORACLES_V1.json'),str(HELD/'GRID_INPUT_MAP_V4.json'):sha(HELD/'GRID_INPUT_MAP_V4.json')}))
    save(A/'ORACLES_V1.json',dict(jobs=list(oracles.values())))
    print(json.dumps(dict(status='prepared',jobs=len(jobs),performance_cells=len(perf))))
if __name__=='__main__':main()
