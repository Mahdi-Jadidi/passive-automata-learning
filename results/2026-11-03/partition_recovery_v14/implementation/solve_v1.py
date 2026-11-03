"""C014 exact unary precheck + frozen C010 fallback, compact fast-family CLI."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import exact_partition_v1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--seconds', type=float, default=None, help='cooperative time budget including input reading')
    args = parser.parse_args(argv)
    if args.seconds is not None and (not math.isfinite(args.seconds) or args.seconds < 0):
        parser.error('seconds must be finite and nonnegative')
    started = time.perf_counter()
    deadline = None if args.seconds is None else started + args.seconds
    try:
        raw = args.input.read_bytes()
        data = json.loads(raw.decode('utf-8-sig'))
        result = exact_partition_v1.solve(data, deadline=deadline)
        result['input_sha256'] = hashlib.sha256(raw).hexdigest()
        result['input_read_and_solver_seconds'] = time.perf_counter() - started
    except (ValueError, OSError) as exc:
        result = {'status': 'invalid_input', 'complete': False, 'error': str(exc)}
    except KeyboardInterrupt:
        result = {'status': 'incomplete', 'complete': False, 'reason': 'interruption_during_input'}
    except Exception as exc:
        result = {'status': 'environment_or_program_error', 'complete': False,
                  'error': f'{type(exc).__name__}: {exc}'}
    # Exact Bell integers must not be truncated by a decimal-digit safety cap.
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(0)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {'incomplete': 3, 'invalid_input': 2, 'environment_or_program_error': 1}.get(result['status'], 0)


if __name__ == '__main__':
    raise SystemExit(main())
