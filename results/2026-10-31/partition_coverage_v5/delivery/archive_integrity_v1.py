#!/usr/bin/env python3
"""Read-only integrity audit for a C005 archive; writes a unique JSON report."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('output', help='new report filename, relative to delivery/ or absolute')
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    cycle = here.parent
    root = cycle.parents[2]
    out = Path(args.output)
    if not out.is_absolute(): out = here / out
    if out.exists(): ap.error(f'refusing to overwrite existing report: {out}')
    errors, counts = [], {'parent_manifest_files': 0, 'readiness_files': 0,
                          'readiness_runtime_hashes': 0, 'attempts': 0,
                          'raw_capture_files': 0, 'completion_records': 0,
                          'source_blobs': 0}
    def check(path: Path, expected: str, label: str):
        if not path.is_file(): errors.append(f'{label}: missing {path}'); return
        actual = sha(path)
        if actual.lower() != str(expected).lower(): errors.append(f'{label}: sha256 mismatch {path}')
    manifest = cycle / 'coordination' / 'parent_manifest.json'
    if manifest.is_file():
        for entry in json.loads(manifest.read_text(encoding='utf-8')).get('files', []):
            counts['parent_manifest_files'] += 1
            path = root / Path(entry['path'])
            check(path, entry.get('sha256', ''), 'parent manifest')
            if path.is_file() and entry.get('bytes') != path.stat().st_size:
                errors.append(f'parent manifest: byte count mismatch {path}')
    else: errors.append(f'missing parent manifest: {manifest}')
    for p in cycle.rglob('READINESS*.json'):
        counts['readiness_files'] += 1
        try: data = json.loads(p.read_text(encoding='utf-8'))
        except Exception as e: errors.append(f'invalid readiness JSON {p}: {e}'); continue
        for key in ('artifact', 'provider'):
            rel, digest = data.get(key), data.get('sha256')
            if rel and digest:
                counts['readiness_runtime_hashes'] += 1
                check(cycle / rel, digest, 'runtime readiness')
        for dep in data.get('dependencies', []):
            if dep.get('path') and dep.get('sha256'):
                counts['readiness_runtime_hashes'] += 1
                check(cycle / dep['path'], dep['sha256'], 'runtime dependency readiness')
    blobs = cycle / 'evidence' / 'source_blobs'
    for b in blobs.rglob('*') if blobs.exists() else []:
        if not b.is_file(): continue
        counts['source_blobs'] += 1
        digest = b.name
        if len(digest) != 64 or sha(b) != digest: errors.append(f'content-addressed source blob mismatch: {b}')
        elif b.parent.name != digest[:2]: errors.append(f'source blob shard mismatch: {b}')
    attempts = cycle / 'evidence' / 'attempts'
    if attempts.exists():
        for d in sorted(p for p in attempts.iterdir() if p.is_dir()):
            counts['attempts'] += 1
            mp, rp = d/'manifest.json', d/'result.json'
            if not mp.is_file(): errors.append(f'attempt lacks manifest: {d}'); continue
            try: m = json.loads(mp.read_text(encoding='utf-8'))
            except Exception as e: errors.append(f'invalid attempt manifest {mp}: {e}'); continue
            for name in ('stdout.bin', 'stderr.bin'):
                raw = d/name
                counts['raw_capture_files'] += 1
                if not raw.is_file(): errors.append(f'attempt lacks raw capture {raw}'); continue
                counts['completion_records'] += 1
                # Compare hashes when a capture record provides one.
                for key in (name, name.replace('.bin','_sha256'), 'raw_'+name.replace('.bin','_sha256')):
                    val = m.get(key)
                    if isinstance(val, str) and len(val) == 64 and sha(raw) != val:
                        errors.append(f'attempt raw hash mismatch {raw}')
            if not rp.is_file(): errors.append(f'attempt lacks completion result record: {rp}')
            else:
                try:
                    result = json.loads(rp.read_text(encoding='utf-8'))
                    if 'exit_code' not in result: errors.append(f'attempt result lacks exit_code: {rp}')
                except Exception as e: errors.append(f'invalid attempt result {rp}: {e}')
    else: errors.append(f'missing attempts directory: {attempts}')
    # Include the exact script bytes in the report so the report snapshots its checker.
    report = {'schema_version': 1, 'created_utc': datetime.now(timezone.utc).isoformat(),
              'checker': {'path': str(Path(__file__).relative_to(cycle)), 'sha256': sha(Path(__file__))},
              'cycle': str(cycle), 'counts': counts, 'error_count': len(errors), 'errors': errors,
              'status': 'pass' if not errors else 'fail',
              'scope_note': 'Archive integrity only; no solver tests or performance runs.'}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(report, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'status': report['status'], 'counts': counts, 'error_count': len(errors), 'report': str(out)}, ensure_ascii=False))
    return 0 if not errors else 1

if __name__ == '__main__': raise SystemExit(main())
