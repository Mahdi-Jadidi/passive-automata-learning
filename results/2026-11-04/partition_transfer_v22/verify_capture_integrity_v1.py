import hashlib,json
from pathlib import Path
A=Path(__file__).resolve().parent/'audit'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
errors=[];counts={'captures':0,'streams':0,'source_references':0};historical_changes=[]
for directory in sorted((A/'attempts').iterdir()):
 if not (directory/'result.json').exists():continue
 cap=json.loads((directory/'result.json').read_text(encoding='utf-8-sig'));counts['captures']+=1
 for stream in ('stdout','stderr'):
  p=directory/(stream+'.bin');counts['streams']+=1
  if sha(p)!=cap[stream+'_sha256']:errors.append(str(p))
 for source in json.loads((directory/'manifest.json').read_text(encoding='utf-8-sig'))['sources']:
  counts['source_references']+=1
  if sha(A/source['snapshot'])!=source['sha256']:errors.append(source['snapshot'])
  if sha(source['path'])!=source['sha256']:historical_changes.append({'path':source['path'],'snapshot_sha256':source['sha256'],'current_sha256':sha(source['path'])})
report={'status':'accepted' if not errors else 'rejected','counts':counts,'errors':errors,'changed_originals_with_preserved_snapshots':historical_changes}
out=A.parent/'coordination'/'MASTER_CAPTURE_INTEGRITY_V1.json'
with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
print(json.dumps({'status':report['status'],'counts':counts,'errors':len(errors),'changed_originals':len(historical_changes)}))
