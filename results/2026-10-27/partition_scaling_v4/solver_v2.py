"""C004 CLI R2: preserves R1; uses interruption-safe singleton inference v4."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent


def answer_limit(value):
    if value == 'all':
        return None
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError('expected a positive integer or all') from error
    if number < 1:
        raise argparse.ArgumentTypeError('expected a positive integer or all')
    return number


def load_provider(method):
    if method in ('general', 'bounded'):
        path = ROOT / 'general/known_k_v3.py'
    else:
        sys.path.insert(0, str(ROOT / 'structural'))
        if method == 'bounded-certificate':
            path = ROOT / 'structural/bounded_certificate_v1.py'
        else:
            version = 1 if method == 'singleton-certificate' else 4
            path = ROOT / f'structural/singleton_solver_v{version}.py'
    spec = importlib.util.spec_from_file_location('c004_cli_provider', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.solve


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--method', choices=['general', 'bounded', 'bounded-certificate', 'singleton-certificate',
                                            'singleton-search'], default='general')
    parser.add_argument('--k', type=int, help='known number of nonempty blocks; default input k or 2')
    parser.add_argument('--q', type=int, help='at most q words per local language; bounded method only')
    parser.add_argument('--infer-k', action='store_true', help='singleton-search conditional certificate only')
    parser.add_argument('--max-solutions', type=answer_limit, default=1)
    parser.add_argument('--timeout-seconds', type=float, default=30.0)
    args = parser.parse_args(argv)
    started = time.perf_counter()
    try:
        if not math.isfinite(args.timeout_seconds) or args.timeout_seconds < 0:
            raise ValueError('timeout-seconds must be finite and nonnegative')
        if args.infer_k and (args.method != 'singleton-search' or args.k is not None):
            raise ValueError('infer-k requires singleton-search and no explicit k')
        if args.method in ('bounded', 'bounded-certificate'):
            if args.q is None or args.q < 1:
                raise ValueError('bounded methods require a positive q')
        elif args.q is not None:
            raise ValueError('q is supported only by bounded methods')
        data = json.loads(args.input.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict):
            raise ValueError('input must be an object')
        if args.infer_k:
            if 'k' in data:
                raise ValueError('infer-k input must omit k; keep hidden k in an audit sidecar')
        else:
            k = data.get('k', 2) if args.k is None else args.k
            if isinstance(k, bool) or not isinstance(k, int) or k < 2:
                raise ValueError('common interface requires known k >= 2')
        options = dict(k=args.k, deadline=time.perf_counter()+args.timeout_seconds,
                       max_solutions=args.max_solutions)
        if args.method in ('bounded', 'bounded-certificate'):
            options['local_word_cap'] = args.q
        if args.method == 'singleton-search':
            options['infer_k'] = args.infer_k
        result = load_provider(args.method)(data, **options)
        result['interface'] = dict(method=args.method, infer_k=args.infer_k,
                                   cli_seconds_before_serialization=time.perf_counter()-started)
    except (ValueError, OSError) as error:
        print(json.dumps(dict(status='invalid_input', error=str(error)), ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {'incomplete': 3, 'insufficient_coverage': 4}.get(result['status'], 0)


if __name__ == '__main__':
    raise SystemExit(main())
