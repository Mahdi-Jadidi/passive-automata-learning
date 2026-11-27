"""Profile the four exact Review08 raw inputs under matching search caps."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from time import monotonic

from p3_frontier_verifier import build_trusted_scope
from run_native import ARMS, replay, require, write
from selector_v2.core import Sample
from selector_v2.edr_m3 import canonical, load


FIXTURES = {
    "medium_choice": "abdce6ec6d39f21d845dabe409e6978f38f4bcb4871854cf82e55507ccb9862f",
    "huge_choice_active": "0be60da81326bcd8974da1df07e018e60dcd62714123b884c873ed3be782beba",
    "hdfs_1024": "7d076991e9ba118b98226a64d9551cd5c6df5d0797183d2e8a95ed896b057075",
    "hdfs_holdout_1024_uncapped": "238d37c4588f1a8506275859ede5cf6a5225630bb3454c016568ff7e2ae5ff6c",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", choices=FIXTURES, required=True)
    parser.add_argument("--memory-mib", type=int)
    args = parser.parse_args()
    if args.memory_mib is not None:
        import resource

        limit = args.memory_mib * 1024**2
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    path = args.output / args.case
    path.mkdir(parents=True, exist_ok=True)
    source = args.fixtures / (args.case + ".json")
    raw_bytes = source.read_bytes()
    require(sha256(raw_bytes).hexdigest() == FIXTURES[args.case], "raw fixture hash")
    raw = json.loads(raw_bytes)
    sample = Sample.from_input(raw)
    journal = canonical(dict(version="selector-v2-journal/2", sample_digest=sample.sample_digest,
                             events=[]))
    scope = build_trusted_scope(raw, journal)
    (path / "journal.json").write_bytes(journal)
    write(path / "scope.json", scope)
    rows = []
    python = [sys.executable, "-B"]
    if not __debug__:
        python.append("-O")
    for mode in ("one", "all"):
        for arm, flags in ARMS.items():
            stem = path / f"{mode}-{arm}"
            proof = stem.with_suffix(".cert.json")
            metrics = stem.with_suffix(".metrics.json")
            command = python + ["-m", "selector_v2.edr_m4", "--raw", str(source),
                                "--scope", str(path / "scope.json"), "--mode", mode,
                                "--out", str(proof), "--metrics", str(metrics),
                                "--seconds", "25", "--work", "10000000", "--entries", "2000000",
                                "--frontier-bytes", "67108864"]
            command.extend("--" + flag for flag in flags)
            row = dict(mode=mode, arm=arm, flags=flags)
            started = monotonic()
            try:
                proc = subprocess.run(command, capture_output=True, timeout=30)
                row.update(exit_code=proc.returncode, wall_seconds=monotonic() - started,
                           stderr=proc.stderr.decode(errors="replace"))
            except subprocess.TimeoutExpired:
                row.update(status="HARD_TIMEOUT", wall_seconds=monotonic() - started)
            else:
                if proc.returncode == 0:
                    blob = proof.read_bytes()
                    verdict = replay(raw, journal, scope, blob, mode)
                    require(verdict["status"] in ("VERIFIED", "INCOMPLETE"), verdict)
                    row.update(status=verdict["status"], replay=verdict, producer=load(metrics),
                               proof_bytes=len(blob), proof_sha256=sha256(blob).hexdigest())
                else:
                    row.update(status="PROCESS_CENSORED",
                               stdout=proc.stdout.decode(errors="replace"))
            rows.append(row)
            print(args.case, mode, arm, row["status"], row.get("producer", {}).get("root_check"),
                  row.get("producer", {}).get("root_discovery"), flush=True)
    write(path / "summary.json", dict(case=args.case, raw_sha256=FIXTURES[args.case],
                                      python=sys.version.split()[0], optimized=not __debug__,
                                      memory_mib=args.memory_mib, rows=rows))


if __name__ == "__main__":
    main()
