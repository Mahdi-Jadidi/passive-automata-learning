"""Bounded profiling of frozen C018 on an auditor-approved observational input."""
import argparse
import cProfile
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
import traceback

BASELINE = Path(__file__).resolve().parents[3] / '2026-11-04/synthetic_gate_v18/implementation/gate_v1.py'
EXPECTED = 'c288448f4a11849f74293b13201fdc578a79e6fbbe24165684807bd32ceeb83d'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--known-k', type=int)
    ap.add_argument('--seconds', type=float, default=5)
    args = ap.parse_args()
    if not math.isfinite(args.seconds) or not 0 <= args.seconds <= 20:
        ap.error('profiling soft budget must be finite in0..20; outer auditor uses <=25s hard')
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    profile = cProfile.Profile()
    receipt = {'schema_version': 1, 'command': sys.argv, 'python': sys.version,
               'profiling_is_not_benchmark_timing': True, 'known_k': args.known_k,
               'soft_seconds': args.seconds, 'baseline_path': str(BASELINE), 'execution_status': 'started',
               'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    result = None
    try:
        raw_source = BASELINE.read_bytes()
        receipt['baseline_sha256'] = hashlib.sha256(raw_source).hexdigest()
        if receipt['baseline_sha256'] != EXPECTED:
            raise ValueError('baseline integrity mismatch')
        raw = args.input.read_bytes()
        receipt['input_sha256'] = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw)
        spec = importlib.util.spec_from_file_location('_c020_frozen_baseline', BASELINE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = profile.runcall(module.solve, data, known_k=args.known_k, deadline=started + args.seconds)
        (args.out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, sort_keys=True), encoding='utf-8')
        receipt.update(execution_status='returned', gate_status=result['status'])
    except Exception as exc:
        receipt.update(execution_status='program_or_input_error', error=repr(exc))
        (args.out / 'traceback.txt').write_text(traceback.format_exc(), encoding='utf-8')
    except KeyboardInterrupt:
        receipt.update(execution_status='interrupted')
    finally:
        profile.dump_stats(str(args.out / 'profile.pstats'))
        rows = []
        for entry in profile.getstats():
            code = entry.code
            filename, line, name = ('<builtin>', 0, code) if isinstance(code, str) else (code.co_filename, code.co_firstlineno, code.co_name)
            rows.append({'file': filename, 'line': line, 'function': name,
                         'primitive_calls': entry.callcount - entry.reccallcount, 'calls': entry.callcount,
                         'own_seconds': entry.inlinetime, 'cumulative_seconds': entry.totaltime})
        (args.out / 'functions.json').write_text(json.dumps({
            'top_own': sorted(rows, key=lambda r: -r['own_seconds'])[:30],
            'top_cumulative': sorted(rows, key=lambda r: -r['cumulative_seconds'])[:30]}, indent=2), encoding='utf-8')
        receipt['profile_process_seconds_before_receipt'] = time.perf_counter() - started
        receipt['files'] = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                            for p in args.out.iterdir() if p.is_file()}
        (args.out / 'receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({'execution_status': receipt['execution_status'], 'gate_status': result['status'] if result else None}))
    return 0 if receipt['execution_status'] == 'returned' else 1


if __name__ == '__main__':
    raise SystemExit(main())
