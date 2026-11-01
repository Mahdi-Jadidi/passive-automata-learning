"""C006 unknown-k unrestricted-regular decomposition decision CLI."""
from pathlib import Path
import runpy
import sys

if __name__ == '__main__':
    implementation = Path(__file__).resolve().parent / 'implementation'
    sys.path.insert(0, str(implementation))
    runpy.run_path(str(implementation / 'cli_v4.py'), run_name='__main__')
