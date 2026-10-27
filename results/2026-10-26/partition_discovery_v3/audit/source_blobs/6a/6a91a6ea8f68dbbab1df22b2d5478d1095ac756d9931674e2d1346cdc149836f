"""Nine independent structural boundary calls; no performance measurements."""
import argparse
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import time
import traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def project(word, block):
    return ''.join(a for a in word if a in block)


def canonical(blocks):
    return tuple(sorted(tuple(sorted(b)) for b in blocks))


def oracle(data):
    alphabet=sorted(data['alphabet'])
    positives=sorted(set(data['positive']))
    negatives=sorted(set(data['negative']))
    models=set()
    for suffix in itertools.product((0,1),repeat=len(alphabet)-1):
        owners=(0,)+suffix
        if 1 not in owners:
            continue
        blocks=[{a for a,s in zip(alphabet,owners) if s==side} for side in (0,1)]
        if not positives:
            # Choose each nonempty local word longer than ANY observed negative.
            # Then every negative differs on both sides; every partition is possible.
            models.add(canonical(blocks))
            continue
        factors=[project(positives[0],b) for b in blocks]
        if any([project(p,b) for b in blocks]!=factors for p in positives):
            continue
        if all(any(project(n,blocks[s])!=factors[s] for s in (0,1)) for n in negatives):
            models.add(canonical(blocks))
    return models


def verify(data, result, models, expired):
    require(result['model_class']=='fixed_word_product','wrong model scope')
    require('fixed_word' in result['uniqueness_scope'],'uniqueness not class-scoped')
    if expired:
        require(result['status']=='incomplete' and not result['search_exhausted'], 'deadline false exhaustion')
        require(result['uniqueness']=='unknown' and not result['decision_complete'] and not result['solutions'],
                'deadline false decision/uniqueness')
        return
    status=result['status']
    if status=='assumption_violation':
        require(not models,'class refutation with compatible model')
        require(result['search_exhausted'] and result['decision_complete'] and result['uniqueness']=='unknown',
                'refutation contract invalid')
        require(not result['solutions'],'refutation emitted solution')
    elif status=='insufficient_coverage':
        require(not result['decision_complete'] and not result['search_exhausted']
                and result['uniqueness']=='unknown' and not result['solutions'],
                'coverage limitation incorrectly decides class')
    elif status=='found':
        require(len(models)==1 and len(result['solutions'])==1,'found not sole class partition')
        require(result['uniqueness']=='unique' and result['search_exhausted'] and result['decision_complete'],
                'unique result contract invalid')
    else:
        raise ValueError('unexpected boundary status '+status)
    positives=sorted(set(data['positive']))
    negatives=sorted(set(data['negative']))
    for record in result['solutions']:
        require(canonical(record['blocks']) in models,'solution absent from independent oracle')
        blocks=[set(b) for b in record['blocks']]
        require(len(blocks)==2 and all(blocks) and not blocks[0]&blocks[1]
                and blocks[0]|blocks[1]==set(data['alphabet']),'bad blocks')
        langs=[sorted({project(p,b) for p in positives}) for b in blocks]
        require(record['positive_projection_languages']==langs and all(len(l)==1 for l in langs),'not singleton local languages')
        require(record['local_words']==[l[0] for l in langs],'local words mismatch')
        witnesses=record['negative_witnesses']
        require([w['negative'] for w in witnesses]==negatives,'witness coverage mismatch')
        for w in witnesses:
            unseen=[s for s in (0,1) if project(w['negative'],blocks[s]) not in langs[s]]
            require(bool(unseen) and w['all_unseen_block_indices']==unseen,'unseen sides invalid')
            require(w['block_index'] in unseen and w['projection']==project(w['negative'],blocks[w['block_index']]),'chosen witness invalid')
    certificate=result.get('certificate') or {}
    if certificate.get('kind')=='odd_opposition_cycle':
        alpha=sorted(data['alphabet'])
        independent_edges={frozenset((a,b)) for a,b in itertools.combinations(alpha,2)
                           if len({project(p,{a,b}) for p in positives})>1}
        cycle=certificate['symbols']
        require(len(cycle)>=4 and cycle[0]==cycle[-1] and (len(cycle)-1)%2==1,'not closed odd cycle')
        require(len(set(cycle[:-1]))==len(cycle)-1,'cycle not simple')
        require(all(frozenset((a,b)) in independent_edges for a,b in zip(cycle,cycle[1:])), 'odd-cycle edge unsupported')
        graph=result['graph']
        require({frozenset(e) for e in graph['edges']}==independent_edges,'opposition graph mismatch')
        for edge,index in zip(graph['edges'],graph['edge_positive_indices']):
            require(project(positives[index],set(edge))!=project(positives[0],set(edge)), 'edge index witness invalid')
    if certificate.get('kind')=='count_inconsistency':
        a=certificate['symbol']; i,j=certificate['positive_indices']
        counts=[positives[i].count(a),positives[j].count(a)]
        require(counts==certificate['counts'] and counts[0]!=counts[1],'count witness invalid')
    if result.get('reason')=='unique_structural_candidate_violates_labels':
        conflicts=certificate.get('accepted_negative_conflicts',[])
        require(bool(conflicts),'expected accepted-negative certificate')
        alpha=result['graph']['symbols']; colors=result['graph']['colors']
        blocks=[{a for a,c in zip(alpha,colors) if c==s} for s in (0,1)]
        factors=certificate['local_words']
        require(all(n in negatives and [project(n,b) for b in blocks]==factors for n in conflicts),
                'accepted-negative conflict unsupported')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    fixture=HERE/'inputs.json'
    provider_path=ROOT/'structural/fixed_word_solver.py'
    frozen_raw=provider_path.read_bytes()
    spec=importlib.util.spec_from_file_location('independent_boundary_structural',provider_path)
    provider=importlib.util.module_from_spec(spec); spec.loader.exec_module(provider)
    cases=json.loads(fixture.read_text(encoding='utf-8'))
    require(len(cases)==9,'bounded fixture changed')
    reports=[]
    for item in cases:
        cid=item['id']; data=item['input']
        try:
            result=provider.solve(data,deadline=time.perf_counter()-1 if item.get('expired') else None,max_solutions=1)
            raw=dict(case_id=cid,input=data,result=result)
            # Persist returned evidence BEFORE oracle/assertions/checks.
            with (args.output/(cid+'.raw.json')).open('x',encoding='utf-8') as handle:
                json.dump(raw,handle,ensure_ascii=False,indent=2); handle.flush(); os.fsync(handle.fileno())
            print(json.dumps(raw,ensure_ascii=False),flush=True)
            models=oracle(data)
            verify(data,result,models,bool(item.get('expired')))
            reports.append(dict(case_id=cid,accepted=True,status=result['status'],class_model_count=len(models),
                                class_partitions=[list(map(list,p)) for p in sorted(models)]))
        except BaseException as error:
            failure=dict(case_id=cid,input=data,error=repr(error),traceback=traceback.format_exc(),
                         scientific_status='acceptance_blocked_pending_diagnosis')
            (args.output/(cid+'.failure.json')).write_text(json.dumps(failure,ensure_ascii=False,indent=2),encoding='utf-8')
            raise
    require(provider_path.read_bytes()==frozen_raw,'provider source changed during checks')
    report=dict(accepted=True,cases=9,provider_calls=9,oracle='independent exhaustive fixed-word partitions, no candidate helpers',
                reports=reports,provider_sha256=sha(frozen_raw),input_sha256=sha(fixture.read_bytes()),
                checker_sha256=sha(Path(__file__).read_bytes()),
                scope='fixed_word_product exceptional branches only; no general model refutation implied',
                timing_benchmark=False)
    (args.output/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    main()
