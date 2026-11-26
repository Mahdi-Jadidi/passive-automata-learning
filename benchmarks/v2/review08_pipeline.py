"""Run a fresh or resumed RAW-to-proof pipeline with a shared wall deadline."""
import argparse
import json
from pathlib import Path
import sys
from time import monotonic

from p3_harness import load_manifest, run_stage
from p3_native import (HERE, INPUTS, MANIFEST, VERIFIER_LIMITS, artifact, cli, flags,
                       read_result, stage_sources)

CASES = ("medium_choice", "huge_choice_active", "hdfs_1024", "hdfs_holdout_1024_uncapped")
CONFIG = HERE / "p3" / "review08-pipeline.json"
MAKE = """
import json
from pathlib import Path
import sys
from time import monotonic

core, interface, raw_path, output, seconds = sys.argv[1:]
sys.path[:0] = [core, interface]
import adapter
from strict_ledger import parse
from selector_v2.core import Sample, Budget
from selector_v2.component_closure import component_closure
from selector_v2.registered_ledger import RegisteredLedger

raw = parse(Path(raw_path).read_bytes())
ledger = RegisteredLedger(raw, adapter=adapter, parse=parse)
budget = Budget(work=10000000, seconds=float(seconds))
started = monotonic()
closure = component_closure(Sample.from_input(raw), budget)
print(json.dumps(dict(phase="closure", elapsed_seconds=monotonic()-started,
                      state=closure["state"], records=len(closure["records"]),
                      owner=closure["owner"])), flush=True)
if closure["records"]:
    started = monotonic()
    ledger.append_raw(closure["records"])
    Path(output).write_bytes(ledger.export())
    print(json.dumps(dict(phase="ledger", elapsed_seconds=monotonic()-started,
                          events=len(ledger.journal))), flush=True)
"""


def pipeline(args, config, root, raw, producer, verifier, interface, mode, runtime, restart):
    root.mkdir()
    journal, scope = root / "journal.json", root / "scope.json"
    proof, metrics = root / "proof.json", root / "metrics.json"
    limit = 30
    started = monotonic()
    phases = {}
    summary = dict(mode=mode, python_mode=runtime, restart=restart, phases=phases,
                   wall_seconds_cap=limit, status="INCOMPLETE")

    def stage(name, command):
        remaining = limit - (monotonic() - started)
        if remaining <= 0:
            phases[name] = dict(status="NOT RUN", reason="end-to-end deadline")
            return False
        caps = config["limits"] | {"cooperative_seconds": min(25, remaining)}
        record = run_stage(command(caps), root, name, remaining, args.memory_mib, runtime,
                           extra_env={"PYTHONPATH": "", "PYTHONHOME": ""})
        phases[name] = record
        record["hard_seconds_cap"] = remaining
        return record["returncode"] == 0 and monotonic() - started <= limit

    def independent(name, values, caps, expected=False):
        argv = flags(config, name, values)
        argv += [arg for key, field in VERIFIER_LIMITS.items()
                 for arg in ("--" + key, str(caps[field]))]
        if expected:
            argv += ["--expected-format", "p3-region-frontier/v2", "--expected-mode", mode]
        return cli(runtime, verifier, "p3_frontier_verifier", argv)

    values = dict(input=raw, journal=journal, scope=scope, mode=mode,
                  certificate=proof, metrics=metrics)
    python = [sys.executable, "-B", "-P"] + (["-O"] if runtime == "optimized" else [])
    if stage("raw-ledger", lambda caps: [*python, "-c", MAKE, str(producer.parent), str(interface),
                                        str(raw), str(journal), str(caps["cooperative_seconds"])]) and artifact(journal):
        if stage("scope", lambda caps: independent("scope", values, caps)):
            trusted = read_result(scope)
            if trusted is None:
                raise ValueError("independent scope missing")
            summary["root_owner"] = trusted["root_owner"]
            summary["mandatory_merges"] = len(trusted["root_owner"]) - len(set(trusted["root_owner"]))
            checkpoint = root / "checkpoint.json"

            def produce(caps, partial=False):
                if partial:
                    caps = caps | dict(producer_entries=1)
                files = values | (dict(certificate=checkpoint, metrics=root / "checkpoint-metrics.json")
                                  if partial else {})
                command = flags(config, "producer", caps | files)
                if restart and not partial:
                    command += ["--resume", str(checkpoint)]
                return cli(runtime, producer.parent, config["producer_module"], command)

            ready = True
            if restart:
                ready = stage("checkpoint", lambda caps: produce(caps, partial=True))
                checkpoint_metrics = read_result(root / "checkpoint-metrics.json") or {}
                if ready and checkpoint_metrics.get("status") == "PARTIAL":
                    stage("checkpoint-replay", lambda caps: independent(
                        "verifier", values | dict(certificate=checkpoint), caps, expected=True))
                    verdict = read_result(root / "checkpoint-replay.stdout") or {}
                    ready = (verdict.get("status") == "INCOMPLETE"
                             and phases["checkpoint-replay"].get("returncode") == 2)
                else:
                    ready = False
            if ready and stage("search", produce) and artifact(proof):
                stage("replay", lambda caps: independent("verifier", values, caps, expected=True))
                verdict = read_result(root / "replay.stdout") or {}
                summary["replay"] = verdict
                code = phases["replay"].get("returncode")
                if verdict.get("status") == "INVALID" and code == 1:
                    summary["status"] = "INVALID"
                if verdict.get("status") == "VERIFIED" and code == 0 and monotonic()-started <= limit:
                    summary["status"] = "VERIFIED"
    summary["elapsed_seconds"] = monotonic() - started
    summary["peak_rss_kib"] = max((p.get("peak_rss_kib") or 0 for p in phases.values()), default=0)
    for file in (journal, scope, proof, root / "checkpoint.json"):
        summary[file.stem] = artifact(file)
    if metrics.exists():
        summary["search_metrics"] = read_result(metrics)
    closure_log = root / "raw-ledger.stdout"
    if closure_log.exists():
        summary["raw_ledger"] = [json.loads(line) for line in closure_log.read_text().splitlines()]
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, required=True)
    parser.add_argument("--memory-mib", type=int, choices=(512, 1536), required=True)
    for role in ("producer", "verifier", "interface", "output"):
        parser.add_argument("--" + role, type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_bytes())
    root = args.output.resolve()
    root.mkdir(parents=True)
    raw = root / "raw.json"
    raw.write_bytes((INPUTS / (args.case + ".json")).read_bytes())
    observed = artifact(raw)
    if observed["sha256"] != load_manifest(MANIFEST)[args.case]["input_sha256"]:
        raise ValueError("original input hash mismatch")
    producer = root / "producer-source" / "selector_v2"
    verifier, interface = (root / (role + "-source") for role in ("verifier", "interface"))
    for role, destination in (("producer", producer), ("verifier", verifier), ("interface", interface)):
        stage_sources(getattr(args, role), config["sources"][role], destination)
    runs = []
    for mode in ("one", "all"):
        for runtime in ("normal", "optimized"):
            for restart in (False, True):
                name = f"{mode}-{runtime}-{'restart' if restart else 'fresh'}"
                runs.append(pipeline(args, config, root / name, raw, producer, verifier,
                                     interface, mode, runtime, restart))
    roots = {tuple(run["root_owner"]) for run in runs if "root_owner" in run}
    if artifact(raw) != observed or len(roots) > 1:
        raise ValueError("input or independently replayed root disagrees")
    record = dict(case=args.case, memory_mib=args.memory_mib, raw=observed,
                  journal_origin="NEW_AUTHORITATIVE_RAW_EXPORT", sources=config["sources"], runs=runs)
    (root / "summary.json").write_text(json.dumps(record, indent=2) + "\n")
    if any(run["status"] == "INVALID" for run in runs):
        raise ValueError("independent replay rejected a proof")


if __name__ == "__main__":
    main()
