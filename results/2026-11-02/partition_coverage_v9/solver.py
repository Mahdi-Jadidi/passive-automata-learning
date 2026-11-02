"""Public C009 CLI, selecting the immutable v1 ownership provider."""
from pathlib import Path
import runpy
import sys

implementation = Path(__file__).resolve().parent / 'implementation'
sys.path.insert(0, str(implementation))
runpy.run_path(str(implementation / 'ownership_cli_v1.py'), run_name='__main__')
