"""Exact partition gate; opt in to a maximum-block recommendation with --recommend."""
import argparse
from pathlib import Path
import runpy
import sys


if __name__ == '__main__':
    if '--help' in sys.argv[1:] or '-h' in sys.argv[1:]:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('input', type=Path)
        modes = parser.add_mutually_exclusive_group()
        modes.add_argument('--known-k', type=int, help='externally trusted count (legacy gate)')
        modes.add_argument('--recommend', choices=['max-blocks'], help='recommend the maximum-block compatible partition without K')
        parser.add_argument('--seconds', type=float, default=5, help='cooperative budget, default 5')
        parser.add_argument('--memo-limit', type=int, default=100000, help='DP entry quota for recommendation mode')
        parser.parse_args()
    recommendation = any(arg == '--recommend' or arg.startswith('--recommend=') for arg in sys.argv[1:])
    if recommendation:
        implementation = (Path(__file__).resolve().parent / 'results' / '2026-11-06'
                          / 'recommendation_checkpoint_v26' / 'implementation')
        entrypoint = 'cli_v1.py'
    else:
        implementation = (Path(__file__).resolve().parent / 'results' / '2026-11-05'
                          / 'search_checkpoint_v24' / 'implementation' / 'integrated_c024_v1')
        entrypoint = 'partition_gate_v1.py'
    sys.path.insert(0, str(implementation))
    runpy.run_path(str(implementation / entrypoint), run_name='__main__')
