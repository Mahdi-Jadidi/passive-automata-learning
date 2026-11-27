"""Measure fresh RAW closure, authoritative journal/2, scope, M4, and replay."""
import argparse
from hashlib import sha256
from pathlib import Path
import subprocess
import sys
from time import monotonic

from p3_frontier_verifier import Incomplete, build_trusted_scope, verify_frontier
from profile_raw import FIXTURES
from run_native import require, write
from selector_v2.component_closure import component_closure
from selector_v2.core import Budget, Sample
from selector_v2.edr_bb import SearchCaps
from selector_v2.edr_m3 import FORMAT_V2, load
from selector_v2.edr_m4 import solve
from selector_v2.registered_ledger import RegisteredLedger


STAGES = ("raw", "scope", "search", "replay")
WALL = dict.fromkeys(STAGES, 30)
TOTAL = 120


def phase(name, source, path, mode):
    raw = load(source)
    journal = path / "journal.json"
    scope = path / "scope.json"
    proof = path / "certificate.json"
    if name == "raw":
        import adapter
        from strict_ledger import parse

        started = monotonic()
        budget = Budget(work=10_000_000, seconds=20)
        closure = component_closure(Sample.from_input(raw), budget)
        closure_seconds = monotonic() - started
        started = monotonic()
        ledger = RegisteredLedger(raw, adapter=adapter, parse=parse)
        ledger.append_raw(closure["records"])
        journal.write_bytes(ledger.export())
        return dict(state=closure["state"], closure_seconds=closure_seconds,
                    closure_work=budget.used, ledger_seconds=monotonic() - started,
                    epoch_count=len(closure["records"]),
                    quotient_classes=len(set(closure["owner"])))
    if name == "scope":
        trusted = build_trusted_scope(raw, journal.read_bytes(),
                                      budgets=dict(seconds=25, max_work=200_000_000))
        write(scope, trusted)
        return dict(status="VERIFIED", quotient_classes=len(set(trusted["root_owner"])))
    if name == "search":
        certificate, stats = solve(raw, load(scope), mode, sparse=True,
                                   caps=SearchCaps(25, 10_000_000, 2_000_000, 67_108_864))
        write(proof, certificate)
        return stats
    return verify_frontier(raw, journal.read_bytes(), load(scope), proof.read_bytes(),
                           expected_format=FORMAT_V2, expected_mode=mode, seconds=25,
                           max_work=200_000_000)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("one", "all"), required=True)
    parser.add_argument("--phase", choices=STAGES)
    parser.add_argument("--memory-mib", type=int)
    args = parser.parse_args()
    if args.memory_mib is not None:
        import resource

        limit = args.memory_mib * 1024**2
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    if args.phase:
        try:
            report = phase(args.phase, args.raw, args.output, args.mode)
        except (Incomplete, MemoryError) as exc:
            report = dict(status="INCOMPLETE", reason=str(exc))
        write(args.output / (args.phase + ".metrics.json"), report)
        return
    path = args.output
    path.mkdir(parents=True, exist_ok=False)
    python = [sys.executable, "-B"]
    if not __debug__:
        python.append("-O")
    raw_hash = sha256(args.raw.read_bytes()).hexdigest()
    require(raw_hash == FIXTURES.get(args.raw.stem), "raw fixture hash")
    rows = {}
    started = monotonic()
    for name in STAGES:
        before = monotonic()
        command = python + [__file__, "--raw", str(args.raw), "--output", str(path),
                            "--mode", args.mode, "--phase", name]
        timeout = min(WALL[name], TOTAL - (before - started))
        if timeout <= 0:
            rows[name] = dict(status="END_TO_END_CAP")
            break
        try:
            proc = subprocess.run(command, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            rows[name] = dict(status="HARD_TIMEOUT", wall_seconds=monotonic()-before)
            break
        if proc.returncode:
            rows[name] = dict(status="PROCESS_FAILURE", exit_code=proc.returncode,
                              stderr=proc.stderr.decode(errors="replace"),
                              wall_seconds=monotonic()-before)
            break
        metrics = load(path / (name + ".metrics.json"))
        rows[name] = dict(metrics=metrics, wall_seconds=monotonic()-before)
        if metrics.get("status") in ("INCOMPLETE", "INVALID"):
            break
    hashes = {f.name: dict(bytes=f.stat().st_size, sha256=sha256(f.read_bytes()).hexdigest())
              for f in sorted(path.iterdir())}
    write(path / "summary.json", dict(raw_sha256=raw_hash, stages=rows, files=hashes,
                                      memory_mib=args.memory_mib, mode=args.mode,
                                      optimized=not __debug__, stage_wall_caps=WALL,
                                      total_wall_cap=TOTAL, pipeline_seconds=monotonic()-started))
    print(args.raw.stem, args.mode, list(rows), rows.get("replay", {}).get("metrics"),
          flush=True)


if __name__ == "__main__":
    main()
