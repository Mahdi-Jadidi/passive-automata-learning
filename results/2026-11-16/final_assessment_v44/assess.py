"""Read-only evidence validation followed by assessment and hash-manifest output."""
from pathlib import Path
import hashlib
import json
import os
import platform
import subprocess
import sys
from build_pdf import HERE, ROOT, OUTPUT

def records(path):
    return [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]

def main():
    frozen=HERE.parent/'exact_optimizer_v43'
    hashes={'encoding.py':'38da943c28419cb02c7b2aecff56c9ce189ed57ec51e39d2e19b74afab50727e',
            'optimizer.py':'a4dcb3f1dfa6a84d5743276a9d8d584ab6e17d79fda1da95d3aa0ba976d8da63',
            'verify.py':'e42c85a2cddb61797856114292f3577a2356c6bebcdf6bb7933ba6ca71af0dad'}
    for name,value in hashes.items():
        assert hashlib.sha256((frozen/name).read_bytes()).hexdigest()==value,name
    summary=json.loads(subprocess.check_output([sys.executable,str(frozen/'summarize.py')],text=True))
    encoding=records(HERE/'encoding_audit.jsonl')
    assert len(encoding)==100 and all(x['pass'] for x in encoding)
    checks=sum((1<<(x['atoms']*(x['atoms']-1)//2))*(x['atoms']+1) for x in encoding)
    assert checks==15664
    replay=records(HERE/'encoding_replay_instances.jsonl')
    assert replay==encoding
    detail=records(HERE/'encoding_checks.jsonl')
    assert len(detail)==checks and all(x['actual']==x['expected'] for x in detail)
    identities={(x['case'],tuple(x['assignment']),x['threshold']) for x in detail}
    assert len(identities)==checks
    for case,item in enumerate(encoding):
        assert sum(x['case']==case for x in detail)==(1<<(item['atoms']*(item['atoms']-1)//2))*(item['atoms']+1)
    family=records(HERE/'structural_family_raw.jsonl')
    assert [x['m'] for x in family]==[2,3,4,8,16,32,64,128,256]
    assert all(x['pass'] and x['checked']=={'status':'ACCEPT'} and
               x['profile']['result']['max_devices']==x['m']-1 for x in family)
    field=json.loads((HERE/'field_readiness.json').read_text())
    limitation=json.loads((HERE/'FIELD_DATA_LIMITATION.json').read_text(encoding='utf-8'))
    assert limitation['and_model_field_trials']==0
    actual=hashlib.sha256((ROOT/field['source']).read_bytes()).hexdigest()
    assert actual==field['sha256'] and field['and_model_field_tests']==0
    qa=json.loads((HERE/'pdf_layout_qa.json').read_text())
    assert all(not x['outside_safe_page_bounds'] and not x['replacement_characters'] for x in qa['checks'])
    assessment={'implementation':'V43','assessment':'V44','source_integrity':'PASS',
                'environment':{'python':sys.version,'platform':platform.platform(),
                               'processor':platform.processor(),'logical_cpus':os.cpu_count()},
                'verified_benchmark_trials':summary['verified_trials'],
                'verified_oracle_audit_cases':summary['verified_audit_cases'],
                'new_encoding_instances':100,'new_encoding_checks':checks,
                'detailed_encoding_replay_checks':len(detail),'evidence_validation':'STORED_RECORDS_AND_HASHES_NOT_FULL_HISTORICAL_REEXECUTION',
                'structural_family_instances':len(family),'largest_family_alphabet':256,
                'and_model_field_trials':0,'pdf_pages':qa['pages'],
                'field_data_availability':limitation['status'],
                'universal_superiority':'NOT_ESTABLISHED','scientific_novelty':'REQUIRES_INDEPENDENT_REVIEW',
                'formal_software_verification':'NOT_DONE','independent_peer_review':'NOT_DONE',
                'benchmark_summary':summary['summary']}
    (HERE/'assessment.json').write_text(json.dumps(assessment,indent=2)+'\n',encoding='utf-8')
    paths=set(HERE.glob('*.py'))|set(HERE.glob('*.md'))|set(HERE.glob('*.jsonl'))
    paths|={HERE/'assessment.json',HERE/'field_readiness.json',HERE/'FIELD_DATA_LIMITATION.json',HERE/'pdf_layout_qa.json',OUTPUT}
    paths|=set(frozen.glob('*.py'))|set(frozen.glob('*.md'))|set(frozen.glob('*.jsonl'))
    paths.add(ROOT/'docs/ALGORITHM_NOTATION.md')
    manifest={p.relative_to(ROOT).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                                            'bytes':p.stat().st_size} for p in sorted(paths)}
    (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in assessment.items() if k not in ('environment','benchmark_summary')}))

if __name__=='__main__':main()
