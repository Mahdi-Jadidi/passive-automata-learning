"""Verify immutable capture records for both correctness runs and supplement."""
import hashlib,json
from pathlib import Path
A=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ids=set();errors=[]
 for name in ['C024-CORRECTNESS-01','C024-B-CORRECTNESS-01','C024-INTEGRATED-CORRECTNESS-01']:
  for l in (A/'runs'/name/'ledger.jsonl').read_text().splitlines():
   r=json.loads(l)
   if 'attempt_id' in r:ids.add(r['attempt_id'])
 for r in read(A/'runs/C024-SUPPLEMENT-02/REPORT_V2.json')['rows']:ids.add(r['attempt_id'])
 for r in read(A/'runs/C024-INTEGRATED-CLI-01/REPORT_V1.json')['rows']:ids.add(r['attempt_id'])
 for aid in sorted(ids):
  try:
   d=A/'attempts'/aid;c=read(d/'result.json');m=read(d/'manifest.json');assert c['child_reaped'] and not c.get('capture_error') and not c.get('cleanup_error')
   for stream in ['stdout','stderr']:assert sha(d/(stream+'.bin'))==c[stream+'_sha256']
   for s in m['sources']:assert sha(A/s['snapshot'])==s['sha256'] and sha(s['path'])==s['sha256']
  except Exception as e:errors.append({'failure_id':'C024-CAPTURE-'+aid,'error':repr(e)})
 out={'attempts_checked':len(ids),'errors':errors};(A/'CORRECTNESS_CAPTURE_INTEGRITY_V2.json').write_text(json.dumps(out,indent=2));print(out)
if __name__=='__main__':main()
