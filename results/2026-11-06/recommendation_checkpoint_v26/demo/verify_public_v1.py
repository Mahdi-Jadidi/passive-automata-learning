"""Bounded public dispatch integration checks, not a timing comparison."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIXTURE = HERE / 'ambiguous_unique_recommendation.json'


def main():
    cases = [
        ('legacy', [], 0, 'ambiguous', 'C024-integrated-exact-search'),
        ('legacy_K2', ['--known-k','2'], 0, 'certified_unique', 'C024-integrated-exact-search'),
        ('legacy_expired', ['--seconds','0'], 3, 'unresolved', 'C024-integrated-exact-search'),
        ('recommend', ['--recommend','max-blocks'], 0, 'ambiguous', 'C026-max-blocks-v1'),
        ('recommend_equals', ['--recommend=max-blocks'], 0, 'ambiguous', 'C026-max-blocks-v1'),
        ('recommend_expired', ['--recommend','max-blocks','--seconds','0'], 3, 'unresolved', 'C026-max-blocks-v1'),
        ('exclusive', ['--recommend','max-blocks','--known-k','2'], 2, None, None),
        ('invalid_mode', ['--recommend','other'], 2, None, None),
        ('invalid_quota', ['--recommend','max-blocks','--memo-limit','0'], 2, None, None),
    ]
    rows=[]
    for name,args,exitcode,status,method in cases:
        argv=[sys.executable,str(ROOT/'partition.py'),str(FIXTURE),*args]
        p=subprocess.run(argv,cwd=ROOT,capture_output=True,timeout=25)
        (HERE/(name+'.stdout.txt')).write_bytes(p.stdout)
        (HERE/(name+'.stderr.txt')).write_bytes(p.stderr)
        out=json.loads(p.stdout) if status else None
        passed=p.returncode==exitcode and (not status or out['status']==status and out['method']==method)
        if name in ('recommend','recommend_equals'):
            rec=out['recommendation']
            passed=passed and rec['partition']==[['a','b'],['c','d']] and rec['optimality_proved'] is True and rec['tie_status']=='unique' and rec['block_count']==2
        if name=='recommend_expired':passed=passed and out['recommendation'] is None
        rows.append(dict(name=name,argv=argv,exitcode=p.returncode,status=out.get('status') if out else None,passed=passed))
    result=dict(passed=all(r['passed'] for r in rows),calls=len(rows),rows=rows,
                public_sha256=hashlib.sha256((ROOT/'partition.py').read_bytes()).hexdigest())
    (HERE/'PUBLIC_VERIFICATION_V1.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'],calls=len(rows))))
    return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
