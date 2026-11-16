"""Opt-in C026 maximum-block recommendation CLI."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time
import recommend_v1


def fallback(status, reason):
    return {'schema_version': 1, 'method': recommend_v1.METHOD, 'status': status,
            'physical_truth_read': False, 'recommendation': None,
            'findings': {'data_insufficient': None, 'computation_incomplete': status == 'unresolved'},
            'error' if status == 'invalid_input' else 'reason': reason}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--recommend', choices=['max-blocks'])
    mode.add_argument('--known-k', type=int)
    parser.add_argument('--seconds', type=float, default=5)
    parser.add_argument('--memo-limit', type=int, default=100000)
    args = parser.parse_args(argv)
    if args.known_k is not None:
        parser.error('this opt-in CLI implements --recommend max-blocks; use the existing gate for --known-k')
    if not math.isfinite(args.seconds) or args.seconds < 0:
        parser.error('seconds must be finite and nonnegative')
    if args.memo_limit <= 0:
        parser.error('memo-limit must be a positive integer')
    started = time.perf_counter()
    try:
        raw = args.input.read_bytes()
        data = json.loads(raw.decode('utf-8-sig'))
        result = recommend_v1.solve(data, deadline=started + args.seconds, memo_limit=args.memo_limit)
        result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    except (ValueError, OSError) as exc:
        result = fallback('invalid_input', str(exc))
    except (KeyboardInterrupt, RecursionError, MemoryError):
        result = fallback('unresolved', 'input_or_resource_interruption')
    except Exception as exc:
        result = fallback('unresolved', 'program_or_environment_error: ' + str(exc))
    try:
        encoded = json.dumps(result, ensure_ascii=True, sort_keys=True)
    except (Exception, KeyboardInterrupt):
        result = fallback('unresolved', 'serialization_interruption')
        encoded = json.dumps(result)
    try:
        sys.stdout.write(encoded + '\n')
    except (OSError, UnicodeError, MemoryError, KeyboardInterrupt):
        return 3
    return {'certified_unique': 0, 'ambiguous': 0, 'incompatible': 0,
            'unresolved': 3, 'invalid_input': 2}[result['status']]


if __name__ == '__main__':
    raise SystemExit(main())
