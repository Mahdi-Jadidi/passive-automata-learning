"""Experimental C025 partitioning for current-event outputs (1..8 event types).

This entry point uses the selected-output contract, separate from partition.py's
complete-word AND-acceptance contract. See the C025 report for data assumptions.
"""
from pathlib import Path
import runpy
import sys


if __name__ == "__main__":
    implementation = (
        Path(__file__).resolve().parent
        / "results/2026-11-05/real_trace_checkpoint_v25/implementation/selected_output_v1"
    )
    sys.path.insert(0, str(implementation))
    runpy.run_path(str(implementation / "cli_v1.py"), run_name="__main__")
