"""Master archive integrity check; execute after all workers freeze their files."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / 'audit'
CACHE = {}


def sha(path):
    path = path.resolve()
    if path not in CACHE:
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        CACHE[path] = digest.hexdigest()
    return CACHE[path]


def main():
    attempts = streams = references = 0
    for directory in sorted((AUDIT / 'attempts').iterdir()):
        if not directory.is_dir():
            continue
        result = json.loads((directory / 'result.json').read_text(encoding='utf-8'))
        manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        assert result['child_reaped'] and not result.get('cleanup_error'), directory
        assert not manifest.get('source_snapshot_error'), directory
        for name in ('stdout', 'stderr'):
            path = directory / (name + '.bin')
            assert sha(path) == result[name + '_sha256'], path
            assert path.stat().st_size == result[name + '_bytes'], path
            streams += 1
        for source in manifest['sources']:
            snapshot = AUDIT / source['snapshot']
            assert sha(snapshot) == source['sha256'], snapshot
            assert sha(Path(source['path'])) == source['sha256'], source['path']
            references += 1
        attempts += 1
    mapping = json.loads((AUDIT / 'GRID_INPUT_MAP_V4.json').read_text())['entries']
    assert len(mapping) == 120
    for item in mapping.values():
        directory = Path(item['directory'])
        for name, key in [('world.json', 'world_sha256'), ('input2.json', 'input2_sha256'), ('input8.json', 'input8_sha256')]:
            assert sha(directory / name) == item[key], directory / name
    result = {'status': 'passed', 'capture_attempts': attempts, 'raw_streams': streams,
              'snapshot_references': references, 'unique_files_hashed': len(CACHE),
              'prepared_parents': len(mapping), 'solver_inputs': 2 * len(mapping)}
    with (ROOT / 'coordination' / 'integrity_result.json').open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
