"""C003 partition construction: general, fixed-word, or fair-reference."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import sys
import time


def limit(value):
    if value == 'all':
        return None
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError('expected a positive integer or all') from error
    if number < 1:
        raise argparse.ArgumentTypeError('expected a positive integer or all')
    return number


def provider(method):
    root = Path(__file__).resolve().parent
    relative = {'general': 'general/general_solver.py',
                'fair-reference': 'general/fair_reference.py',
                'fixed-word': 'structural/fixed_word_solver.py'}[method]
    spec = importlib.util.spec_from_file_location('c003_' + method.replace('-', '_'), root / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None):
    started = time.perf_counter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--method', choices=('general', 'fixed-word', 'fair-reference'), default='general')
    parser.add_argument('--max-solutions', type=limit, default=1)
    parser.add_argument('--timeout-seconds', type=float, default=30.0)
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout_seconds) or args.timeout_seconds < 0:
        parser.error('timeout must be finite and nonnegative')
    try:
        data = json.loads(args.input.read_text(encoding='utf-8-sig'))
        result = provider(args.method).solve(data, deadline=started + args.timeout_seconds,
                                             max_solutions=args.max_solutions)
    except (ValueError, OSError) as error:
        print(json.dumps({'status': 'invalid_input', 'error': str(error)}, ensure_ascii=False))
        return 2
    result.setdefault('metrics', {})['cli_seconds_before_serialization'] = time.perf_counter() - started
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return {'incomplete': 3, 'insufficient_coverage': 4,
            'assumption_violation': 5}.get(result['status'], 0)


if __name__ == '__main__':
    sys.exit(main())
