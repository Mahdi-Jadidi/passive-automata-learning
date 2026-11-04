"""Portable dispatch to the unchanged audited C020 C2 solver."""
from pathlib import Path
import runpy
import sys
if __name__ == "__main__":
    impl = Path(__file__).resolve().parent / "algorithm"
    sys.path.insert(0, str(impl))
    runpy.run_path(str(impl / "partition_gate_v1.py"), run_name="__main__")
