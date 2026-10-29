"""C004 Stage2 correctness only: independent RGS oracle, full raw first."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import random
import time
from singleton_solver_v2 import solve as exact
from singleton_solver_v3 import solve as inference
from bounded_certificate_v1 import solve as bounded


ROOT = Path(__file__).resolve().parents[1]


def partitions(alphabet,k):
    def visit(labels,highest):
        if len(labels) == len(alphabet):
            if highest+1 == k:
                yield [[a for a,c in zip(alphabet,labels) if c==i] for i in range(k)]
            return
        for c in range(min(highest+1,k-1)+1):
            yield from visit(labels+[c],max(highest,c))
    yield from visit([0],0)


def oracle(data,k,q):
    answers=[]
    for blocks in partitions(sorted(data['alphabet']),k):
        langs=[{''.join(a for a in word if a in block) for word in data['positive']} for block in blocks]
        if any(len(lang)>q for lang in langs):
            continue
        if any(all(''.join(a for a in word if a in block) in lang for block,lang in zip(blocks,langs))
               for word in data['negative']):
            continue
        answers.append(blocks)
    return answers


def canonical(blocks):
    return tuple(tuple(block) for block in blocks)


def main():
    rng=random.Random(44002)
    failures=[]
    count=0
    def record(name,data,kind,k=None,q=1):
        nonlocal count
        if kind=='exact':
            truth=oracle(data,k,1)
            result=exact(data,k=k,max_solutions=None)
        elif kind=='bounded':
            truth=oracle(data,k,q)
            result=bounded(data,k=k,local_word_cap=q,max_solutions=None)
        else:
            truth=[p for possible in range(1,len(data['alphabet'])+1) for p in oracle(data,possible,1)]
            result=inference(data,infer_k=True,max_solutions=None)
        print(json.dumps({'name':name,'kind':kind,'data':data,'k':k,'q':q,'oracle':truth,'result':result},
                         ensure_ascii=False),flush=True)
        count+=1
        got=[s['blocks'] for s in result['solutions']]
        if kind=='exact':
            okay=sorted(map(canonical,got))==sorted(map(canonical,truth)) and result['search_exhausted']
        else:
            okay=(result['status']=='insufficient_coverage' or
                  (result['status']=='found' and got==truth and len(truth)==1) or
                  (result['status']=='infeasible' and not truth))
        if not okay:
            failures.append(name)
        return result,truth

    path={'alphabet':list('abcd'),'positive':['abcd','bacd','acbd','abdc'],'negative':[]}
    r,t=record('path_three_solutions',path,'exact',3)
    if len(t)!=3: failures.append('path_expected_three')
    pathn=dict(path,negative=['bdac'])
    r,t=record('path_negative_unique',pathn,'exact',3)
    if len(t)!=1: failures.append('path_expected_one')
    infer={'alphabet':list('abcd'),'positive':['abcd','cdab'],'negative':['bacd','abdc']}
    r,t=record('unknown_k_unique',infer,'infer')
    if r['status']!='found' or r['k']!=2: failures.append('unknown_expected_k2')
    record('unknown_naive_min_colors',{'alphabet':list('abc'),'positive':['ab','ba'],'negative':[]},'infer')
    for m in range(2,7):
        alphabet=list('abcdef'[:m])
        for sample in range(12):
            positive=[''.join(alphabet)]
            for _ in range(sample%4):
                letters=list(alphabet);rng.shuffle(letters);positive.append(''.join(letters))
            if sample%5==0: positive.append(positive[0]+alphabet[0])
            negative=[''] if sample%3 else []
            data={'alphabet':alphabet,'positive':positive,'negative':negative}
            for k in range(1,m+1):
                record(f'random_exact_{m}_{sample}_{k}',data,'exact',k)
                record(f'random_bounded_{m}_{sample}_{k}',data,'bounded',k,2)
            record(f'random_infer_{m}_{sample}',data,'infer')
    for k,width in [(2,1),(2,2),(3,1),(3,2)]:
        alphabet=list('abcdef'[:k*width]);blocks=[alphabet[i*width:(i+1)*width] for i in range(k)]
        u=[''.join(b)*2 for b in blocks]
        v=[word+b[0] for word,b in zip(u,blocks)]
        lockstep=''.join(word[j] for j in range(len(u[0])) for word in u)
        data={'alphabet':alphabet,'positive':[''.join(u),''.join(reversed(u)),lockstep,''.join(v)],'negative':['']}
        r,t=record(f'genuine_q2_{k}_{width}',data,'bounded',k,2)
        if r['status']!='found' or any(len(lang)!=2 for lang in r['solutions'][0]['positive_projection_languages']):
            failures.append(f'genuine_q2_not_recovered_{k}_{width}')
        r,t=record(f'genuine_q2_q1_refutes_{k}_{width}',data,'bounded',k,1)
        if r['status']!='infeasible': failures.append(f'genuine_q2_q1_not_refuted_{k}_{width}')
    fullcap={'alphabet':list('abcd'),'positive':['abcabcdd','ddabcabc','abcdabcd','acbacbdd','bacbacdd'],'negative':[]}
    r,t=record('pair_relaxation_fullcap_failure',fullcap,'bounded',2,2)
    if r['reason']!='forced_candidate_exceeds_q_full_block_words': failures.append('fullcap_path_not_exercised')
    for input_path in sorted((ROOT/'examples').glob('*.json')):
        data=json.loads(input_path.read_text(encoding='utf-8-sig'))
        if 'k' not in data:
            record('root_'+input_path.name,data,'infer')
        else:
            record('root_exact_'+input_path.name,data,'exact',data['k'])
            record('root_bounded_'+input_path.name,data,'bounded',data['k'],2)
    empty={'alphabet':list('ab'),'positive':[],'negative':['']}
    boundary={'exact_empty':exact(empty,k=2), 'infer_empty':inference(empty,infer_k=True),
              'bounded_empty':bounded(empty,k=2),
              'exact_expired':exact(path,k=3,deadline=time.perf_counter()-1),
              'infer_expired':inference(infer,infer_k=True,deadline=time.perf_counter()-1),
              'bounded_expired':bounded(fullcap,k=2,deadline=time.perf_counter()-1),
              'exact_limit':exact(path,k=3,max_solutions=1)}
    print(json.dumps({'boundaries':boundary},ensure_ascii=False),flush=True)
    for key,value in boundary.items():
        if key.endswith('_empty') and value['status']!='insufficient_coverage': failures.append(key)
        if key.endswith('_expired') and (value['status']!='incomplete' or value['search_exhausted']): failures.append(key)
    if boundary['exact_limit']['uniqueness']!='unknown' or boundary['exact_limit']['search_exhausted']:
        failures.append('limit_certifies_uniqueness')
    # Exercise the frozen root CLI in-process on its actual example files.
    spec=importlib.util.spec_from_file_location('root_cli_for_smoke',ROOT/'solver.py')
    cli=importlib.util.module_from_spec(spec);spec.loader.exec_module(cli)
    for name,args in [('unknown',['infer_singleton_k.json','--method','singleton-search','--infer-k']),
                      ('sparse',['sparse_three_color_ambiguous.json','--method','singleton-search','--max-solutions','all']),
                      ('disambiguated',['sparse_three_color_disambiguated.json','--method','singleton-search','--max-solutions','all']),
                      ('bounded',['three_factor_two_words.json','--method','bounded','--q','2','--max-solutions','all'])]:
        args[0]=str(ROOT/'examples'/args[0]);out=io.StringIO()
        with contextlib.redirect_stdout(out): code=cli.main(args)
        payload=json.loads(out.getvalue())
        print(json.dumps({'cli_case':name,'argv':args,'exit_code':code,'result':payload},ensure_ascii=False),flush=True)
        if code!=0 or payload['status']!='found':failures.append('cli_'+name)
    print(json.dumps({'summary':{'case_count':count,'failures':failures,'benchmark':False}},ensure_ascii=False),flush=True)
    assert not failures,failures


if __name__=='__main__':main()
