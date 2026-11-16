"""Acquire a small, commit-pinned operational-log sample from its maintainer."""
import hashlib
import json
from pathlib import Path
import platform
import sys
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
OUT = HERE / 'external/loghub_bgl_v1'
OUT.mkdir(parents=True, exist_ok=False)
report = {'id': 'C025-BGL-acquisition-v1', 'repository': 'https://github.com/logpai/loghub',
          'purpose': 'Research-only external operational-log sample assessment, not full-system trace recovery',
          'python': sys.version, 'platform': platform.platform(), 'files': [], 'errors': []}

def fetch(url):
    with urlopen(Request(url, headers={'User-Agent': 'C025-research-checkpoint'}), timeout=20) as response:
        payload = response.read(5 * 1024 * 1024 + 1)
        if len(payload) > 5 * 1024 * 1024:
            raise ValueError('per-file download cap exceeded')
        return payload, response.status

try:
    commit_url = 'https://api.github.com/repos/logpai/loghub/commits/master'
    commit_raw, status = fetch(commit_url)
    (OUT / 'commit.json').write_bytes(commit_raw)
    commit = json.loads(commit_raw)['sha']
    assert len(commit) == 40 and all(ch in '0123456789abcdef' for ch in commit)
    report.update(commit=commit, commit_url=commit_url)
    for source, local in [('BGL/BGL_2k.log_structured.csv', 'BGL_2k.log_structured.csv'),
                          ('BGL/BGL_2k.log', 'BGL_2k.log'), ('BGL/README.md', 'BGL_README.md'),
                          ('README.md', 'LOGHUB_README.md'), ('LICENSE', 'LICENSE')]:
        url = f'https://raw.githubusercontent.com/logpai/loghub/{commit}/{source}'
        payload, status = fetch(url)
        (OUT / local).write_bytes(payload)
        report['files'].append({'url': url, 'source_path': source, 'local': local,
                                'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest(),
                                'http_status': status})
    report['status'] = 'downloaded_pinned_original_samples'
except Exception as exc:
    report['status'] = 'incomplete'
    report['errors'].append({'type': type(exc).__name__, 'message': str(exc)})
finally:
    (OUT / 'ACQUISITION_V1.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': report['status'], 'files': len(report['files']), 'errors': report['errors']}))
if report['errors']:
    raise SystemExit(1)
