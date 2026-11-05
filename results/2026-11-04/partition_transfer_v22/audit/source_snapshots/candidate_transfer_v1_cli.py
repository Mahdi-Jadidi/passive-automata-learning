"""One-command exact prerequisite gate for a uniquely justified partition."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import gate_v1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--known-k', type=int, default=None, help='externally trusted exact count; not inferred from data')
    parser.add_argument('--seconds', type=float, default=5, help='cooperative budget including input reading')
    args = parser.parse_args(argv)
    import math
    if not math.isfinite(args.seconds) or args.seconds < 0:
        parser.error('seconds must be finite and nonnegative')
    started = time.perf_counter()
    deadline = started + args.seconds
    try:
        raw = args.input.read_bytes()
        data = json.loads(raw.decode('utf-8-sig'))
        result = gate_v1.solve(data, known_k=args.known_k, deadline=deadline)
        result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    except (ValueError, OSError) as exc:
        result = {'status': 'invalid_input', 'error': str(exc),
                  'findings': {'data_insufficient': None, 'computation_incomplete': False}}
    except (KeyboardInterrupt, RecursionError, MemoryError):
        result = {'status': 'unresolved', 'reason': 'input_or_resource_interruption',
                  'findings': {'data_insufficient': None, 'computation_incomplete': True}}
    except Exception as exc:
        traceback.print_exc(file=sys.stderr)
        result = {'status': 'unresolved', 'reason': 'program_or_environment_error', 'error': str(exc),
                  'findings': {'data_insufficient': None, 'computation_incomplete': True}}
    explanations = {
        'certified_unique': 'Exactly one compatible partition under the stated assumptions; the certified partition is released.',
        'ambiguous': 'Two distinct compatible partitions prove that these data and assumptions do not select a unique ownership.',
        'incompatible': 'No compatible partition under the declared labels and trusted count, with a completed proof.',
        'unresolved': 'Required proof work did not complete; this does not establish observational insufficiency.',
        'invalid_input': 'The input or explicit constraint does not satisfy the declared API.'}
    result['explanation'] = explanations[result['status']]
    result['input_and_solver_seconds'] = time.perf_counter() - started
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return {'certified_unique': 0, 'ambiguous': 0, 'incompatible': 0, 'unresolved': 3, 'invalid_input': 2}[result['status']]


if __name__ == '__main__':
    raise SystemExit(main())
