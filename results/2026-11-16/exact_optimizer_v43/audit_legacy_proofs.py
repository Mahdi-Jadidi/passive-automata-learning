"""Replay new DRUP traces using frozen V42's separate scanning checker/encoder."""
import json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
LEGACY=ROOT/'results/2026-11-15/exact_optimizer_v42'
def main():
    rows=[json.loads(x) for x in (HERE/'audit_raw.jsonl').read_text().splitlines()]
    examples=[r for r in rows if r['result']['certificate']['type']=='drup']
    command="import sys,json;sys.path.insert(0,sys.argv[1]);from verify import verify_optimal;request=json.load(sys.stdin);print(json.dumps(verify_optimal(request['input'],request['result'],{'timeout_seconds':30})))"
    with (HERE/'legacy_proof_audit.jsonl').open('x',encoding='utf8') as stream:
        for row in examples:
            proc=subprocess.run([sys.executable,'-c',command,str(LEGACY)],input=json.dumps(row),text=True,capture_output=True,timeout=35)
            accepted=proc.returncode==0 and json.loads(proc.stdout)=={'status':'ACCEPT'}
            stream.write(json.dumps({'audit_i':row['i'],'accepted':accepted,'stdout':proc.stdout,'stderr':proc.stderr})+'\n');stream.flush()
            assert accepted,(row['i'],proc.stdout,proc.stderr)
    print({'drup_replayed_by_legacy_checker':len(examples)})
if __name__=='__main__':main()
