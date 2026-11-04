"""Public entry point for the exact synthetic-trace partition gate."""
from pathlib import Path
import runpy
import sys


if __name__ == '__main__':
    implementation = Path(__file__).resolve().parent / 'results' / '2026-11-04' / 'scaling_v20' / 'implementation' / 'candidate_c2_v1'
    sys.path.insert(0, str(implementation))
    runpy.run_path(str(implementation / 'partition_gate_v1.py'), run_name='__main__')
