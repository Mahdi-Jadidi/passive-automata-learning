"""Validate the paired rank artifacts and export independent matrices."""
import argparse
import json
from pathlib import Path

from review08_export import CONFIG, MANIFEST, artifact, write_tables

FIELDS = ("nodes", "expanded", "work", "compatibility_work", "discovery_work",
          "discovery_seconds", "rank_work", "rank_calls", "resumed_nodes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("download", "ci", "output"):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    config = json.loads(CONFIG.with_name("review09-rank.json").read_bytes())
    originals = {r["case"]: r["input_sha256"] for r in json.loads(MANIFEST.read_bytes())}
    ci = json.loads(args.ci.read_bytes())
    if ci["conclusion"] != "success" or len(ci["jobs"]) != 20:
        raise ValueError("rank CI matrix did not succeed")
    for group, inputs in (("original", originals), ("targeted", config["targets"])):
        cases, rows = [], []
        for case, digest in inputs.items():
            for memory in (512, 1536):
                root = args.download / f"review09-rank-{case}-{memory}"
                summary = json.loads((root / "summary.json").read_bytes())
                if (summary["case"], summary["memory_mib"], summary["sources"],
                    summary["raw"]["sha256"], summary["targeted"]) != (
                        case, memory, config["sources"], digest, group == "targeted"):
                    raise ValueError(f"wrong rank case evidence: {root}")
                for name in ("raw", "journal", "scope"):
                    if summary[name] != artifact(root / f"{name}.json"):
                        raise ValueError(f"root artifact differs: {root}/{name}")
                runs = {(r["mode"], r["python_mode"], r["arm"], r["restart"]): r
                        for r in summary["runs"]}
                expected = {(m, p, a, r) for m in ("one", "all")
                            for p in ("normal", "optimized") for a in ("sparse-v2", "rank-v3")
                            for r in (False, True)}
                if set(runs) != expected or len(summary["runs"]) != len(expected):
                    raise ValueError(f"wrong rank variants: {root}")
                cases.append(summary)
                for (mode, runtime, arm, restart), row in runs.items():
                    directory = root / f"{mode}-{runtime}-{arm}-{'restart' if restart else 'fresh'}"
                    version = "v3" if arm == "rank-v3" else "v2"
                    for name in ("journal", "scope"):
                        if row[name] != summary[name] or row[name] != artifact(directory / f"{name}.json"):
                            raise ValueError(f"rank route has different trusted bytes: {directory}/{name}")
                    for name in ("proof", "checkpoint"):
                        path = directory / f"{name}.json"
                        if row[name] != artifact(path):
                            raise ValueError(f"rank proof fingerprint differs: {path}")
                        if row[name]:
                            doc = json.loads(path.read_bytes())
                            if (doc["format"], doc["mode"]) != (f"p3-region-frontier/{version}", mode):
                                raise ValueError(f"rank proof format or mode differs: {path}")
                            closures = sum(n.get("closure", {}).get("reason") == "RANK_COST"
                                           for n in doc["nodes"])
                            if closures != row[f"{name}_rank_leaves"] or (arm == "sparse-v2" and closures):
                                raise ValueError(f"rank closure count differs: {path}")
                    metrics = row.get("search_metrics") or {}
                    baseline = runs[mode, runtime, "sparse-v2", restart]
                    avoided = None
                    if arm == "rank-v3" and row["status"] == baseline["status"] == "VERIFIED":
                        avoided = baseline["search_metrics"]["nodes"] - metrics["nodes"]
                    replay = row.get("replay", {})
                    checkpoint = row.get("checkpoint_replay", {})
                    rows.append(dict(case=case, memory_mib=memory, mode=mode, runtime=runtime,
                                     arm=arm, restart=restart, status=row["status"],
                                     stop_reason=metrics.get("stop_reason"),
                                     replay_status=replay.get("status"), replay_reason=replay.get("reason"),
                                     checkpoint_replay_status=checkpoint.get("status"),
                                     checkpoint_replay_reason=checkpoint.get("reason"),
                                     rank_leaves=row.get("proof_rank_leaves"),
                                     checkpoint_rank_leaves=row.get("checkpoint_rank_leaves"),
                                     verified_rank_leaves=(row.get("proof_rank_leaves")
                                                           if row["status"] == "VERIFIED" else None),
                                     nodes_avoided_completed=avoided,
                                     proof_bytes=(row["proof"] or {}).get("bytes"),
                                     proof_sha256=(row["proof"] or {}).get("sha256"),
                                     peak_rss_kib=row["peak_rss_kib"],
                                     completed_resume_match=row["completed_resume_match"],
                                     wall_seconds=row["elapsed_seconds"],
                                     **{f"{name}_seconds": row["phases"].get(name, {}).get("wall_seconds")
                                        for name in ("scope", "search", "replay", "checkpoint",
                                                     "checkpoint-replay")},
                                     **{f"{name}_peak_rss_kib": row["phases"].get(name, {}).get("peak_rss_kib")
                                        for name in ("search", "replay", "checkpoint", "checkpoint-replay")},
                                     **{field: metrics.get(field) for field in FIELDS}))
        if group == "targeted":
            write_tables(args.output, "rank-targeted", ci, cases, rows)
            continue
        for status, stem in (("VERIFIED", "rank-original"), ("INCOMPLETE", "rank-censored")):
            selected = [row for row in rows if row["status"] == status]
            if selected:
                filtered = [case | {"runs": [r for r in case["runs"] if r["status"] == status]}
                            for case in cases]
                write_tables(args.output, stem, ci, [c for c in filtered if c["runs"]], selected)


if __name__ == "__main__":
    main()
