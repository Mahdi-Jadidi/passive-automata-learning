"""Audit retained Actions artifacts and export native measurements to JSON and CSV."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent / "review03/p3/input-manifest.json"


def flatten(summary):
    base = {
        "case": summary["case"], "address_space_mib": summary["address_space_mib"],
        "wall_seconds_cap": summary["limits"]["wall_seconds"],
        "input_sha256": summary["raw"]["sha256"],
        "journal_sha256": (summary["journal"] or {}).get("sha256"),
        "scope_sha256": (summary["scope"] or {}).get("sha256"),
        "base_lower_bound": summary.get("base_lower_bound"),
    }

    def row(name, phase, run=None):
        run = run or {}
        native = phase.get("native", {})
        proof = phase.get("certificate") or {}
        if "verifier" in name:
            producer_name = name.replace("verifier", "producer") if name.startswith("verifier") else name.removesuffix("-verifier")
            proof = run["phases"][producer_name].get("certificate") or {}
        certified = native.get("result") if run.get("status") == "VERIFIED" else None
        return {
            **base, "mode": run.get("mode"), "python_mode": run.get("python_mode"),
            "run_status": run.get("status", summary.get("status")), "phase": name,
            "phase_status": phase.get("status", phase.get("process_status")),
            "process_status": phase.get("process_status"),
            "reason": phase.get("reason") or native.get("stop_reason") or native.get("reason"),
            "returncode": phase.get("returncode"),
            "elapsed_seconds": phase.get("elapsed_seconds"),
            "peak_rss_kib": phase.get("peak_rss_kib"),
            "nodes": native.get("nodes", native.get("nodes_checked")),
            "work_units": native.get("work", native.get("work_units")),
            "exact_checks": native.get("exact_checks"), "entries": native.get("entries"),
            "generated": native.get("generated"), "expanded": native.get("expanded"),
            "closed": native.get("closed"), "frontier_bytes": native.get("frontier_bytes"),
            "resumed_nodes": native.get("resumed_nodes"), "open_nodes": phase.get("open_nodes"),
            "unresolved_suffixes": phase.get("unresolved_suffixes"),
            "proof_bytes": proof.get("bytes"), "proof_sha256": proof.get("sha256"),
            "provisional_upper_bound": phase.get("incumbent_cost"),
            "certified_optimum": (certified or {}).get("optimum"),
            "certified_optima_count": len(certified["optima"]) if certified and run["mode"] == "all" else None,
            "determinism": run.get("determinism"),
            "normal_optimized_parity": run.get("normal_optimized_parity"),
            "checkpoint_resume": run.get("checkpoint_resume"),
        }

    for name in ("journal", "scope"):
        yield row(name, summary.get(name + "_phase", {"status": "NOT RUN"}))
    for run in summary["runs"]:
        for name, phase in run["phases"].items():
            yield row(name, phase, run)


def check_files(directory, summary):
    expected = {"raw.json": summary["raw"], "journal.json": summary["journal"],
                "trusted.json": summary["scope"]}
    for name in ("journal", "scope"):
        if phase := summary.get(name + "_phase"):
            for stream in ("stdout", "stderr"):
                expected[f"{name}.{stream}"] = {
                    "bytes": phase[stream + "_bytes"], "sha256": phase[stream + "_sha256"]
                }
    for run in summary["runs"]:
        for name, phase in run["phases"].items():
            path = Path(f"{run['mode']}-{run['python_mode']}", name)
            if phase.get("metrics_file"):
                expected[path / "metrics.json"] = phase["metrics_file"]
            if phase.get("certificate") and name in ("producer-1", "checkpoint"):
                expected[path / "certificate.json"] = phase["certificate"]
            for stream in ("stdout", "stderr"):
                if stream + "_sha256" in phase:
                    expected[path / f"{name}.{stream}"] = {
                        "bytes": phase[stream + "_bytes"], "sha256": phase[stream + "_sha256"]
                    }
    for name, digest in expected.items():
        path = directory / name
        if digest is None and not path.exists():
            continue
        if digest is None or not path.is_file() or path.stat().st_size != digest["bytes"]:
            raise ValueError(f"artifact length mismatch: {path}")
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != digest["sha256"]:
            raise ValueError(f"artifact mismatch: {directory / name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("download", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--actions-run", type=int, required=True)
    parser.add_argument("--actions-head", required=True)
    args = parser.parse_args()
    reports = []
    for fixture in json.loads(MANIFEST.read_bytes()):
        case = fixture["case"]
        for memory in (1536, 512):
            directory = args.download / f"p3-m2-{case}-{memory}"
            summary = json.loads((directory / "summary.json").read_bytes())
            if (summary["case"], summary["address_space_mib"], summary["raw"]["sha256"]) != (
                case, memory, fixture["input_sha256"]
            ):
                raise ValueError(f"case/profile/fixture mismatch in {directory}")
            variants = {(r["mode"], r["python_mode"]) for r in summary["runs"]}
            expected = {(mode, py) for mode in ("one", "all") for py in ("normal", "optimized")}
            if not (len(summary["runs"]) == 4 and variants == expected) and summary.get("status") != "NOT RUN":
                raise ValueError(f"missing or duplicate modes in {directory}")
            check_files(directory, summary)
            reports.append(summary)
    args.output.mkdir(parents=True, exist_ok=True)
    json_path = args.output / "standard.json"
    json_path.write_bytes((json.dumps(dict(actions_run=args.actions_run, actions_head=args.actions_head,
                                          profiles=reports), indent=2, sort_keys=True) + "\n").encode())
    rows = [row for summary in reports for row in flatten(summary)]
    with (args.output / "standard.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, rows[0], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
