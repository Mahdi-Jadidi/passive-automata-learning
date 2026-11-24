"""P2.1 final pinned research gate; no transport, operational acceptance or merge."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from selector_v2.integration.run_review03 import CORE_REVIEW, ARTIFACTS, verify_files

HEADS = dict(core='796a83a5f8f69c4dc7c0db619e1cdb130ddc0b33',
             interface='0eb1050ad103bad2f93d3b9feb732bf94184f2a2',
             proof='83762437ba05e1def9dde5edff8c7d44878f4269')
CORE = dict(CORE_REVIEW, **{
    'integration/replay_boundary.py':'ec49016283321866c9a498c2aca269cc934e6f04',
    'integration/test_replay_boundary.py':'4164a1e6060aea1d776df52cfd47b2a6da7ed633',
    'integration/run_review03.py':'195a9a93a3651ee4824dafdca556f49d1367f1ef',
})
INTERFACE = {
    'adapter.py':'c38e441c7327a44adad8a0fe1125d45c93e8ef69',
    'strict_ledger.py':'a66975de137e3ec556b8c7aacd108cf975c46344',
    'shared_gateway.py':'33ef122814c409cc7c0d201b0cb4c3127b078862',
    'gateway.py':'8b314e11c0d935122779365b08666c482697621f',
    'test_adapter.py':'bfa7dee3373da7d267c373e238b95d271a8a2669',
    'test_gateway_v2.py':'502b7c40f7776fc3bab087303e457fae149587c3',
    'export_journal2.py':'1d3a16f03171f2259427ecda8de94282ffda8cae',
}
PROOF = {
    'independent_replay.py':'aa09243fa7ccc941c37609e959aefb419075df32',
    'production_replay.py':'4666c3f1aca6189331a83ff2f00de0e376e2a710',
    'ledger_replay.py':'0b615b6c17258e621d73147baa262d791985d8d0',
    'bounded_deletion.py':'64eda7d13b3153175f09b70e41be66e1615846b2',
    'test_bounded_deletion.py':'2f59257d0ff3396417c2cedf9845f61e2fd20928',
    'interface_artifact_replay.py':'51f928ee2311ab8995f88f0e9f195ac7c659e469',
    'journal_v2_replay.py':'6c49013e809b5ac4d2b2a37850e6e6cece513072',
    'replay_published_j2.py':'d32d3bed22dc06a0d51ff7965c7f621950b16455',
}
DELEGATED = {
    'interface-journal2.json':'4c66a0f69633cf1f07bcf04e8852cd4207995b19',
    'interface-journal2.json.gz':'a61d493991c7464641c6d182929ba8c185f57421',
    'interface-journal2-epochs.json':'2e862db654dfbaaba0d6285444ba81b12c984b2b',
    'interface-journal2-epochs.json.gz':'6efdc4356b79e4368e17c59b6376d50861762c12',
}
HASHES = {
    'roundtrip':'14f0dc4cb606ca7f1b20a5cd575a937dd6471da594d983d86254e210573e5ab8',
    'adversarial':'1b78c4aefe974db58409cb186528af75b1981752ba0a3778634fe3bcb406e97c',
    'interface-journal2':'caf40422d9d3e6d0cd8257da4b757cacd71cda1e6db089493421c912515edf94',
    'interface-journal2-epochs':'adabd0b274ebaa2ce55aab7f874f6485664399d4b0df59b013d158cfb2338491',
}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('interface-dir','proof-dir','core-artifacts','output-dir'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--timeout',type=int,default=120)
    args=p.parse_args();module=Path(__file__).resolve().parents[1]
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    report=dict(status='INCOMPLETE',operational_status='INCOMPLETE',heads=HEADS,checks={},artifacts={},blockers=[])
    def finish(status,reason=None):
        report['status']=status
        if reason:report['blockers'].append(reason)
        (out/'gate.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print(json.dumps(report,sort_keys=True),flush=True)
        return {'VERIFIED':0,'INVALID':1,'INCOMPLETE':2}[status]
    try:
        verify_files(module,CORE);verify_files(args.interface_dir,INTERFACE);verify_files(args.proof_dir,PROOF);verify_files(args.core_artifacts,ARTIFACTS)
    except (OSError,SystemExit) as exc:return finish('INCOMPLETE',str(exc))
    report['checks']['source_blobs']=True
    root=module.parent;paths=[root,args.interface_dir.resolve(),args.proof_dir.resolve()]
    for mode in ('normal','optimized'):
        flags=[] if mode=='normal' else ['-O'];d=out/mode;d.mkdir()
        env=dict(os.environ,PYTHONPATH=os.pathsep.join(map(str,paths)),PYTHONNOUSERSITE='1',
                 P2_ARTIFACT=str(d/'roundtrip.json'),P2_ADVERSARIAL_ARTIFACT=str(d/'adversarial.json'),P21_GATE_ARTIFACT_DIR=str(d))
        def run(name,*argv):
            with (d/(name+'.log')).open('wb') as log:
                try:return subprocess.run([sys.executable,*flags,*argv],env=env,cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=args.timeout).returncode
                except (OSError,subprocess.TimeoutExpired):return 2
        rc=run('export','-m','export_journal2',str(d));report['checks'][mode+'_export']=rc
        if rc:return finish('INCOMPLETE',mode+' delegated export failed')
        try:verify_files(d,DELEGATED)
        except (OSError,SystemExit) as exc:return finish('INVALID',str(exc))
        modules=['selector_v2.integration.'+n for n in ('test_roundtrip','test_journal_audit','test_gateway_parity','test_replay_boundary')]+['test_gateway_v2','test_bounded_deletion']
        if mode=='normal':modules += ['selector_v2.tests.'+n for n in ('test_evidence_store','test_schema_closure','test_sparse_analysis')]
        rc=run('combined','-m','unittest','-v',*modules);report['checks'][mode+'_combined']=rc
        if rc:return finish('INCOMPLETE',mode+' combined suite failed')
        for name,expected in HASHES.items():
            try:body=(d/(name+'.json')).read_bytes()
            except OSError as exc:return finish('INCOMPLETE',str(exc))
            if hashlib.sha256(body).hexdigest()!=expected:return finish('INVALID',name+' SHA256 mismatch')
            if name in ('roundtrip','adversarial') and body!=gzip.decompress((args.core_artifacts/(name+'-v2.json.gz')).read_bytes()):return finish('INVALID',name+' committed gzip mismatch')
            if mode=='optimized' and body!=(out/'normal'/(name+'.json')).read_bytes():return finish('INVALID',name+' normal/-O mismatch')
        rc=run('independent','-m','selector_v2.integration.test_final_gate',str(d));report['checks'][mode+'_independent']=rc
        if rc:return finish('INVALID' if rc==1 else 'INCOMPLETE',mode+' independent replay not verified')
        try:result=json.loads((d/'independent.log').read_bytes())
        except (ValueError,OSError) as exc:return finish('INCOMPLETE',str(exc))
        if result.get('status')!='VERIFIED' or result.get('operational_status')!='INCOMPLETE':return finish('INCOMPLETE','unverified independent result')
        if mode=='normal':report['artifacts']=result['artifacts']
        elif report['artifacts']!=result['artifacts']:return finish('INVALID','normal/-O proof status mismatch')
        rc=run('published','-m','replay_published_j2',str(args.core_artifacts.resolve()),str(d));report['checks'][mode+'_published']=rc
        if rc:return finish('INCOMPLETE',mode+' proof-stream published artifact audit failed')
        rc=run('boundary','-m','unittest','-v','selector_v2.integration.test_final_gate');report['checks'][mode+'_boundary']=rc
        if rc:return finish('INCOMPLETE',mode+' independent mutation/boundary suite failed')
    return finish('VERIFIED')


if __name__=='__main__':raise SystemExit(main())
