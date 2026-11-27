"""Pair the frozen sparse route with a published native compact-v2 CLI configuration."""
import argparse
import csv
import json
from pathlib import Path
import sys

BASELINE = Path(__file__).resolve().parent / "p3/review09-pipeline.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact-config", type=Path, required=True)
    parser.add_argument("--baseline-producer", required=True)
    parser.add_argument("--compact-producer", required=True)
    parser.add_argument("--verifier", required=True)
    parser.add_argument("--interface", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", choices=("medium_choice", "huge_choice_active", "hdfs_1024", "hdfs_holdout_1024_uncapped"), required=True)
    parser.add_argument("--memory-mib", choices=("512", "1536"), required=True)
    parser.add_argument("--journal-origin", choices=("retained", "fresh"), required=True)
    args = parser.parse_args()
    from review08_pipeline import main as pipeline_main
    baseline = json.loads(BASELINE.read_bytes())
    compact = json.loads(args.compact_config.read_bytes())
    for key in ("limits", "scope", "verifier", "replay_flags"):
        if baseline[key] != compact[key]:
            raise ValueError(f"paired setting differs: {key}")
    for role in ("interface", "verifier"):
        if baseline["sources"][role] != compact["sources"][role]:
            raise ValueError(f"paired source differs: {role}")
    if compact.get("expected_format", "p3-region-frontier/v2") != "p3-region-frontier/v2":
        raise ValueError("expected native v2 format")
    args.output.mkdir(parents=True)
    reports = {}
    for variant, config, producer in (
        ("sparse", BASELINE, args.baseline_producer),
        ("compact", args.compact_config, args.compact_producer),
    ):
        destination = args.output / variant
        sys.argv = [sys.argv[0], "--case", args.case, "--memory-mib", args.memory_mib,
                    "--journal-origin", args.journal_origin, "--producer", producer,
                    "--verifier", args.verifier, "--interface", args.interface,
                    "--output", str(destination)]
        pipeline_main(config)
        reports[variant] = json.loads((destination / "summary.json").read_bytes())
    sparse, compact = reports.values()
    if sparse["raw"] != compact["raw"]:
        raise ValueError("paired raw input differs")
    for old, new in zip(sparse["runs"], compact["runs"], strict=True):
        for key in ("journal", "scope"):
            if old[key] and new[key] and old[key] != new[key]:
                raise ValueError(f"paired {key} bytes differ")
        for run in (old, new):
            if args.case in ("medium_choice", "huge_choice_active") and "root_owner" in run:
                if run["mandatory_merges"] < 1:
                    raise ValueError("expected a genuine contracted choice root")
    columns = ("variant", "mode", "python_mode", "restart", "phase", "status",
               "elapsed_seconds", "peak_rss_kib", "mandatory_merges")
    with (args.output / "paired.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for variant, report in reports.items():
            for run in report["runs"]:
                scope = run["phases"].get("scope", {})
                writer.writerow(run | scope | dict(variant=variant, phase="trusted_scope",
                    status="READY" if "root_owner" in run else "UNAVAILABLE",
                    elapsed_seconds=scope.get("elapsed_seconds"),
                    peak_rss_kib=scope.get("peak_rss_kib")))
                writer.writerow(run | dict(variant=variant, phase="end_to_end_search"))
    (args.output / "paired.json").write_text(json.dumps(reports, indent=2) + "\n",
                                             encoding="utf-8")


if __name__ == "__main__":
    main()
