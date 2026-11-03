"""Read-only verification of frozen C010 parent and completed C011 snapshot."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[2]

def check_manifest(path, base):
    entries = json.loads(path.read_text(encoding='utf-8-sig'))['files']
    errors = []
    for row in entries:
        target = (base / row['path']).resolve()
        if not target.is_relative_to(base.resolve()):
            errors.append('path escaped root: ' + row['path'])
            continue
        if not target.is_file():
            errors.append('missing: ' + row['path'])
            continue
        if target.stat().st_size != row['bytes']:
            errors.append('size mismatch: ' + row['path'])
        if hashlib.sha256(target.read_bytes()).hexdigest() != row['sha256']:
            errors.append('hash mismatch: ' + row['path'])
    return len(entries), errors

def main():
    errors = []
    counts = {}
    for name, path, base in [
        ('parent', ROOT/'coordination/parent_manifest.json', WORKSPACE),
        ('cycle', ROOT/'coordination/bundle_manifest.json', ROOT),
    ]:
        try:
            counts[name], found = check_manifest(path, base)
            errors.extend(found)
        except Exception as exc:
            errors.append(name + ': ' + repr(exc))
    binding_path = ROOT/'audit/CANDIDATE_BINDING_V1.json'
    if binding_path.is_file():
        binding = json.loads(binding_path.read_text(encoding='utf-8-sig'))
        for key in ['solver','cli','readiness','static_review']:
            row = binding[key]
            target = (ROOT/row['path']).resolve()
            if not target.is_relative_to(ROOT.resolve()) or hashlib.sha256(target.read_bytes()).hexdigest()!=row['sha256']:
                errors.append('candidate binding mismatch: '+key)
    else:
        errors.append('candidate binding missing')
    print(json.dumps({'status':'pass' if not errors else 'fail',
        'checked_utc':datetime.now(timezone.utc).isoformat(),
        'files_checked':counts,'errors':errors,
        'scope':'SHA-256/size/path integrity only; not a scientific correctness proof',
        'interpreter':sys.executable},indent=2))
    return bool(errors)

if __name__ == '__main__':
    raise SystemExit(main())
