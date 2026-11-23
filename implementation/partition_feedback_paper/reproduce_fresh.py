
"""Run an independent reproduction in a new directory without touching recorded trials."""
import argparse
from pathlib import Path
from shutil import copy2
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--timed", action="store_true", help="rerun all benchmarks (several minutes)")
    args = parser.parse_args()
    output = args.destination.resolve()
    output.mkdir()
    evidence = output / "evidence"
    evidence.mkdir()
    for source in HERE.glob("*.py"):
        copy2(source, output / source.name)
    copy2(HERE / "example.json", output / "example.json")
    for name in ("hdfs_cases.json", "hdfs_provenance.json"):
        copy2(HERE / "evidence" / name, evidence / name)

    commands = [["audit.py"], ["audit_evidence.py"]]
    if args.timed:
        commands += [
            ["benchmark.py", "main"], ["benchmark.py", "scale"], ["benchmark.py", "memory"],
            ["benchmark_staged.py"], ["report_results.py"],
        ]
    for command in commands:
        subprocess.run([sys.executable, "-B", *command], cwd=output, check=True)


if __name__ == "__main__":
    main()
