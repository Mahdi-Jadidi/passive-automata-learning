"""Read-only verification of the complete presentation snapshot and final file."""
from pathlib import Path
import hashlib,json,sys
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
presentation=root.parent/'presentation_v1'
manifest=json.loads((presentation/'bundle_manifest.json').read_text(encoding='utf-8'))
errors=[]
for row in manifest['files']:
    p=(presentation/row['path']).resolve()
    if not p.is_relative_to(presentation.resolve()):
        errors.append('Path escaped presentation root: '+row['path']);continue
    if not p.is_file() or p.stat().st_size!=row['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:
        errors.append('Hash/size mismatch: '+row['path'])
qa=json.loads((presentation/'DELIVERY_QA.json').read_text(encoding='utf-8'))
f=presentation/'output/Alphabet_Partition_Research_FA_v2.pptx'
if hashlib.sha256(f.read_bytes()).hexdigest()!=qa['sha256']:errors.append('Final deck differs from QA receipt')
receipt=json.loads((presentation/'private/final_validation_v2.json').read_text(encoding='utf-8'))
if receipt['finalSha256']!=qa['sha256']:errors.append('Final deck differs from first-party finalizer receipt')
print(json.dumps({'status':'pass' if not errors else 'fail','checked_utc':datetime.now(timezone.utc).isoformat(),'presentation_files_checked':len(manifest['files']),'errors':errors,'final_pptx_sha256':qa['sha256'],'command':'python -B -X utf8 coordination/verify_delivery_v1.py'},indent=2))
sys.exit(bool(errors))
