"""Read-only byte integrity review; each invocation creates a fresh record."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import shutil
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / 'coordination/integrity_runs' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ') + '_' + uuid4().hex[:8])
RUN.mkdir(parents=True, exist_ok=False)
shutil.copyfile(__file__, RUN / 'verify_artifacts.py')
checks, validations, errors = [], [], []


def digest(path):
    h = sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def check(path, expected, kind):
    actual = digest(path) if path.is_file() else None
    checks.append(dict(path=str(path), kind=kind, expected=expected,
                       actual=actual, matches=actual == expected))


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


try:
    for name in ('parent_manifest.json', 'runtime_manifest.json'):
        manifest = load(ROOT / 'coordination' / name)
        for item in manifest['files']:
            check(ROOT / item['path'], item['sha256'], name)
    check(ROOT / 'audit/capture.py', load(ROOT / 'coordination/runtime_manifest.json')['capture_sha256'], 'capture')
    for path in (ROOT / 'audit/corpus').rglob('*manifest*.json'):
        manifest = load(path)
        files = manifest.get('files', {})
        entries = files.items() if isinstance(files, dict) else ((x['path'], x) for x in files)
        for name, item in entries:
            if isinstance(item, dict) and 'sha256' in item:
                check(path.parent / name, item['sha256'], 'corpus')
    for path in ROOT.rglob('*'):
        if path.is_file() and 'source_blobs' in path.parts and len(path.name) == 64:
            check(path, path.name, 'content_addressed_blob')
        if path.is_file() and path.name == 'result.json':
            record = load(path)
            for stream in ('stdout', 'stderr'):
                key = stream + '_sha256'
                if key in record:
                    check(path.parent / (stream + '.bin'), record[key], 'captured_stream')
    for path in (ROOT / 'audit/validation').rglob('report*.json'):
        record = load(path)
        validations.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path),
                                accepted=record.get('accepted'), status=record.get('status'),
                                historical_rejections_preserved=True))
except Exception as error:
    errors.append(repr(error))

failed = [x for x in checks if not x['matches']]
report = dict(run_id=RUN.name, at_utc=datetime.now(timezone.utc).isoformat(),
              command=[sys.executable, '-B', '-X', 'utf8', *sys.argv], cwd=str(Path.cwd()),
              python=sys.version, flags=str(sys.flags), platform=platform.platform(),
              script_sha256=digest(Path(__file__)), check_count=len(checks),
              all_match=not failed and not errors, failure_count=len(failed), errors=errors,
              checks=checks, validation_index=validations,
              scientific_status='byte_integrity_only_not_a_mathematical_proof')
(RUN / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(run_dir=str(RUN), checks=len(checks), failures=len(failed), errors=errors,
                      all_match=report['all_match']), ensure_ascii=False))
raise SystemExit(0 if report['all_match'] else 1)
