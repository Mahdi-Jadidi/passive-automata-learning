"""Validate CI pipeline artifacts and export per-phase and end-to-end observations."""
import argparse
import csv
import json
from pathlib import Path

from p3_native import artifact
from review08_pipeline import CASES, CONFIG


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("download", type=Path)
    p.add_argument("ci", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()
    config = json.loads(CONFIG.read_bytes())
    ci = json.loads(args.ci.read_bytes())
    cases, rows = [], []
    for case in CASES:
        for memory in (512, 1536):
            root = args.download / f"review08-pipeline-{case}-{memory}"
            data = json.loads((root / "summary.json").read_bytes())
            if (data["case"], data["memory_mib"], data["sources"], data["raw"]) != (
                    case, memory, config["sources"], artifact(root / "raw.json")):
                raise ValueError(f"case manifest does not match retained bytes: {root}")
            cases.append(data)
            expected = {(m, p, r) for m in ("one", "all") for p in ("normal", "optimized")
                        for r in (False, True)}
            if len(data["runs"]) != len(expected):
                raise ValueError("wrong number of variants")
            by_variant = {(r["mode"], r["python_mode"], r["restart"]): r for r in data["runs"]}
            if set(by_variant) != expected:
                raise ValueError("missing or duplicate variants")
            for (mode, runtime, restart), run in by_variant.items():
                directory = root / f"{mode}-{runtime}-{'restart' if restart else 'fresh'}"
                for name in ("proof", "checkpoint", "journal", "scope"):
                    if run[name] != artifact(directory / (name + ".json")):
                        raise ValueError(f"retained artifact mismatch: {directory}/{name}")
                scope = run.get("root_owner")
                if scope is not None:
                    trusted = json.loads((directory / "scope.json").read_bytes())
                    if trusted["root_owner"] != scope:
                        raise ValueError("retained scope differs")
                fresh = by_variant[mode, runtime, False]
                equality = ""
                if restart and run["status"] == fresh["status"] == "VERIFIED":
                    equality = "MATCH" if run["proof"] == fresh["proof"] else "DIFFERENT"
                    if equality != "MATCH":
                        raise ValueError("completed fresh and resumed bytes disagree")
                run["completed_resume"] = equality or "NOT ESTABLISHED"
                metrics = run.get("search_metrics") or {}
                rows.append(dict(case=case, memory_mib=memory, mode=mode, runtime=runtime,
                                 restart=restart, status=run["status"], phase="total",
                                 wall_seconds=run["elapsed_seconds"],
                                 peak_rss_kib=run["peak_rss_kib"],
                                 mandatory_merges=run.get("mandatory_merges"),
                                 nodes=metrics.get("nodes"), work=metrics.get("work"),
                                 witness_work=metrics.get("witness_work"),
                                 witness_probes=metrics.get("witness_probes"),
                                 witness_local_caps=metrics.get("witness_local_caps"),
                                 proof_bytes=(run["proof"] or {}).get("bytes"),
                                 completed_resume=equality, process_status="", returncode=""))
                for phase, value in run["phases"].items():
                    rows.append(dict(rows[-1] | dict(
                        phase=phase, wall_seconds=value.get("wall_seconds"),
                        peak_rss_kib=value.get("peak_rss_kib"), nodes=None, work=None,
                        witness_work=None, witness_probes=None, witness_local_caps=None,
                        proof_bytes=None, process_status=value.get("process_status", value.get("status")),
                        returncode=value.get("returncode"))))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "pipeline.json").write_text(json.dumps(dict(ci=ci, cases=cases), indent=2) + "\n")
    with (args.output / "pipeline.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
