"""Review 03 pinned regression runner; current outer proof/delegation gate OPEN.

This deliberately cannot grant VERIFIED on the reviewed predecessor heads.
Pin the actual new interface delegation and independent /2 proof checker in a
subsequent reviewed checkpoint, not via an arbitrary CLI verifier path.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from selector_v2.integration.run_p21 import CORE, INTERFACE, PROOF, verify_files

CORE_HEAD = '4e21dbf0d06c030681e774cb15f1a5cf0c802f0d'
INTERFACE_HEAD = 'b27850a667a55927fd3ad127dccce3956d8ead22'
PROOF_HEAD = 'ed20d9b12ea9730e07e7d2d1e0581744a266eb02'
BENCHMARK_HEAD = 'a784d2d6ecb75bc0469c0aa60e210946a2566947'
CORE_REVIEW = dict(CORE, **{
    'registered_ledger.py':'092507fc156e604be242e3100117fedc27b96d04',
    'integration/run_p21.py':'6c7dec2aa2e3c0a98d2640e9b6e3bc77b2dd23e6',
    'integration/audit_journal.py':'2485d498069564a23cd36940f7c791a678c6d8e9',
    'integration/test_roundtrip.py':'fb15567da4265aaa7f147b76bcad5921ff8f2ec2',
    'integration/test_journal_audit.py':'3b5c12b92161c83afefaa552c1252d3aadee8d7e',
    'integration/test_gateway_parity.py':'c58c25a70f6b5b94f2ff37b04b19ddc8429aa294',
})
ARTIFACTS = {
    'roundtrip-v2.json.gz':'eedb6c2fb7ad29346f91230dfc7db1df46eff716',
    'adversarial-v2.json.gz':'1f1444631ba3e1b12f95ae8ba4e362f93d5b8246',
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--interface-dir',type=Path,required=True)
    p.add_argument('--proof-dir',type=Path,required=True)
    p.add_argument('--artifact-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--timeout',type=int,default=120)
    args = p.parse_args()
    module = Path(__file__).resolve().parents[1]
    out = args.output_dir.resolve()
    out.mkdir(parents=True,exist_ok=False)
    report = dict(status='INCOMPLETE',operational_status='INCOMPLETE',
                  core=CORE_HEAD,interface=INTERFACE_HEAD,proof=PROOF_HEAD,benchmark=BENCHMARK_HEAD,
                  benchmark_executed=False,independent_journal2=False,delegated_interface=False,
                  checks={},blockers=['interface /2 delegation not published at pinned head',
                                      'independent /2 replay not published at pinned head'])
    def finish(code):
        (out/'gate.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print(json.dumps(report,sort_keys=True),flush=True)
        return code
    try:
        verify_files(module,CORE_REVIEW)
        verify_files(args.interface_dir,INTERFACE)
        verify_files(args.proof_dir,PROOF)
        verify_files(args.artifact_dir,ARTIFACTS)
        report['checks']['reviewed_blob_identity'] = True
    except (OSError,SystemExit) as exc:
        report['blockers'].append(str(exc)); return finish(2)
    # Exact pinned dependencies precede other user Python paths; execute child
    # interpreters in the module root. Ignore ambient PYTHONPATH and user site.
    env = dict(os.environ,PYTHONPATH=os.pathsep.join(map(str,[module.parent,args.interface_dir.resolve(),args.proof_dir.resolve()])),PYTHONNOUSERSITE='1')
    for mode in ('normal','optimized'):
        flags = [] if mode=='normal' else ['-O']
        argv = [sys.executable,*flags,'-m','selector_v2.integration.run_p21',
                '--interface-dir',str(args.interface_dir.resolve()),'--proof-dir',str(args.proof_dir.resolve()),
                '--artifact',str(out/(mode+'-roundtrip.json')),'--adversarial-artifact',str(out/(mode+'-adversarial.json'))]
        if mode=='normal': argv.append('--full')
        commands = [argv,[sys.executable,*flags,'-m','unittest','selector_v2.integration.test_replay_boundary','-v']]
        for i,cmd in enumerate(commands):
            key = mode+('-regression' if i==0 else '-boundary')
            with (out/(key+'.log')).open('wb') as log:
                try:
                    proc=subprocess.run(cmd,env=env,cwd=module.parent,stdout=log,stderr=subprocess.STDOUT,timeout=args.timeout)
                except (OSError,subprocess.TimeoutExpired) as exc:
                    report['checks'][key]='INCOMPLETE'; report['blockers'].append(type(exc).__name__); return finish(2)
            report['checks'][key]=proc.returncode
            if proc.returncode:
                report['blockers'].append(key+' failed; inspect log'); return finish(2)
    for name in ('roundtrip','adversarial'):
        try:
            expected=gzip.decompress((args.artifact_dir/(name+'-v2.json.gz')).read_bytes())
            normal=(out/('normal-'+name+'.json')).read_bytes()
            optimized=(out/('optimized-'+name+'.json')).read_bytes()
        except (OSError,EOFError,MemoryError) as exc:
            report['blockers'].append(type(exc).__name__); return finish(2)
        if expected!=normal or normal!=optimized:
            report['status']='INVALID'; report['blockers'].append(name+' artifact byte mismatch'); return finish(1)
        report['checks'][name+'_sha256']=hashlib.sha256(normal).hexdigest()
    # The predecessor proof stream verifies v1 records, not journal/2.
    # The predecessor interface maintains its own historical gateway, not delegation.
    # Passing regression tests therefore cannot close the gate.
    return finish(2)


if __name__=='__main__': raise SystemExit(main())
