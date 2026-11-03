"""Run the C011 optimized no-K CLI. Historical versions stay unchanged."""
from pathlib import Path
import runpy
import sys
if __name__ == '__main__':
    implementation = Path(__file__).parent / 'implementation'
    sys.path.insert(0, str(implementation))
    runpy.run_path(str(implementation / 'unrestricted_cli_v3.py'), run_name='__main__')
