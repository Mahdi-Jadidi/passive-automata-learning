"""Export M3 evaluation evidence and audit the immutable M2 resume comparisons."""
import argparse
import csv
from hashlib import file_digest
import json
from pathlib import Path

from p3_export import MANIFEST, check_files, flatten

HERE = Path(__file__).resolve().parent
M2 = HERE / "results/p3-m2/standard.csv"
CONFIG = HERE / "p3/native.json"
VARIANTS = {(mode, interpreter) for mode in ("one", "all")
            for interpreter in ("normal", "optimized")}


def write(output, stem, payload, rows):
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{stem}.json").write_bytes(
        (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    )
    with (output / f"{stem}.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, list(dict.fromkeys(key for row in rows for key in row)),
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def historical(output):
    groups = {}
    with M2.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            if row["checkpoint_resume"] == "DIFFERENT":
                key = tuple(row[k] for k in ("case", "address_space_mib", "mode", "python_mode"))
                groups.setdefault(key, {})[row["phase"]] = row
    limits = json.loads(CONFIG.read_bytes())["limits"]
    rows = []
    for (case, memory, mode, interpreter), phases in groups.items():
        direct, checkpoint, resumed = (phases[k] for k in ("producer-1", "checkpoint", "resumed"))
        charged = {key: int(checkpoint[key]) + int(resumed[key])
                   for key in ("work_units", "frontier_bytes", "entries")}
        excess = charged["frontier_bytes"] - limits["frontier_bytes"]
        replay = phases["resumed-verifier"]
        rows.append(dict(case=case, address_space_mib=int(memory), mode=mode, python_mode=interpreter,
                         direct_cap=direct["reason"], resumed_cap=resumed["reason"],
                         direct_nodes=int(direct["nodes"]), resumed_nodes=int(resumed["nodes"]),
                         checkpoint_work=int(checkpoint["work_units"]),
                         resumed_work=int(resumed["work_units"]), cumulative_work=charged["work_units"],
                         work_over_cap=charged["work_units"] - limits["producer_work"],
                         checkpoint_frontier_bytes=int(checkpoint["frontier_bytes"]),
                         resumed_frontier_bytes=int(resumed["frontier_bytes"]),
                         retained_frontier_bytes=charged["frontier_bytes"], frontier_over_cap=excess,
                         retained_entries=charged["entries"], entry_cap=limits["producer_entries"],
                         replay_status=replay["phase_status"], replay_reason=replay["reason"],
                         replay_nodes=int(replay["nodes"]) if replay["nodes"] else None,
                         direct_sha256=direct["proof_sha256"], resumed_sha256=resumed["proof_sha256"],
                         accounting="retained_frontier_undercount" if excess > 0 else "renewed_work"))
    if len(rows) != 24 or sum(row["frontier_over_cap"] > 0 for row in rows) != 4:
        raise ValueError("unexpected frozen M2 difference counts")
    write(output, "m2-frozen-differences", dict(actions_run=45627999119, rows=rows), rows)


def phase_rows(summary, arm):
    phases = {(r["mode"], r["python_mode"], name): p
              for r in summary["runs"] for name, p in r["phases"].items()}
    for row in flatten(summary):
        phase = phases.get((row["mode"], row["python_mode"], row["phase"]), {})
        native = phase.get("native", {})
        rules = phase.get("split_rules", {})
        prefix = phases.get((row["mode"], row["python_mode"], "checkpoint"), {}).get("native", {})
        resumed = row["phase"] in ("resumed", "cumulative-frontier", "cumulative-work")
        cumulative = {key: prefix[key] + native[key] for key in ("work", "entries", "frontier_bytes")
                      if resumed and key in prefix and key in native}
        yield dict(arm=arm, **row, fresh_comparison=phase.get("fresh_comparison"),
                   checkpoint_prefix_preserved=phase.get("checkpoint_prefix_preserved"),
                   cumulative_work=cumulative.get("work"), retained_entries=cumulative.get("entries"),
                   retained_frontier_bytes=cumulative.get("frontier_bytes"),
                   proof_format=phase.get("proof_format"),
                   cross_splits=rules.get("CROSS_SUPPORT_LEX_V1", 0) if "split_rules" in phase else None,
                   all_pairs_splits=rules.get("ALL_PAIRS_LEX_V1", 0) if "split_rules" in phase else None,
                   discovery_metrics=json.dumps({k: v for k, v in native.items()
                                                  if "discover" in k or "witness" in k}, sort_keys=True))


def retained_resumes(root, summary):
    for run in summary["runs"]:
        directory = root / f"{run['mode']}-{run['python_mode']}"
        checkpoint_path = directory / "checkpoint/certificate.json"
        if not checkpoint_path.is_file():
            continue
        prefix = json.loads(checkpoint_path.read_bytes())["nodes"]
        for name in ("resumed", "cumulative-frontier", "cumulative-work"):
            phase = run["phases"].get(name, {})
            artifact = phase.get("certificate")
            if not artifact:
                continue
            path = directory / name / "certificate.json"
            if path.stat().st_size != artifact["bytes"]:
                raise ValueError(f"resumed proof length mismatch: {path}")
            with path.open("rb") as stream:
                if file_digest(stream, "sha256").hexdigest() != artifact["sha256"]:
                    raise ValueError(f"resumed proof hash mismatch: {path}")
            wanted = {node["id"] for node in prefix}
            resumed = {node["id"]: node for node in json.loads(path.read_bytes())["nodes"]
                       if node["id"] in wanted}
            preserved = True
            for node in prefix:
                actual = resumed.get(node["id"], {})
                if node["kind"] == "LEAF":
                    preserved &= node == actual
                else:
                    preserved &= all(node[k] == actual.get(k) for k in ("id", "parent_id", "edge"))
                if node["kind"] == "SPLIT":
                    preserved &= all(node.get(k) == actual.get(k) for k in (
                        "kind", "rule", "alternative_count", "residual_id", "witness"
                    ))
                    for key in ("children", "cursor_log"):
                        preserved &= node[key] == actual.get(key, [])[:node["cursor"]]
            phase["checkpoint_prefix_preserved"] = bool(preserved)


def observed(args):
    ci = json.loads(args.ci.read_bytes())
    if ci["status"] != "completed" or ci["conclusion"] != "success":
        raise ValueError("CI must have completed successfully for a complete export")
    paired = args.kind == "paired"
    fixtures = {row["case"]: row for row in json.loads(MANIFEST.read_bytes())}
    cases = list(fixtures) if paired else ["small_choice", "hdfs_1024",
                                          "hdfs_holdout_1024_uncapped", "cover_path_8"]
    profiles = (1536, 512) if paired else (1536,)
    for stem, selection in ((args.kind, cases), (args.kind + "-nonempty", ["nonempty_root"])):
        groups, rows = [], []
        for case in selection:
            for memory in profiles:
                directory = args.download / f"p3-m3-evaluation-{case}-{memory}"
                group = {}
                for arm in ("m2", "m3") if paired else ("m2",):
                    root = directory / arm
                    summary = json.loads((root / "summary.json").read_bytes())
                    if (summary["case"], summary["address_space_mib"]) != (case, memory):
                        raise ValueError(f"wrong case/profile in {root}")
                    if case in fixtures and summary["raw"]["sha256"] != fixtures[case]["input_sha256"]:
                        raise ValueError(f"wrong fixture bytes in {root}")
                    variants = {(r["mode"], r["python_mode"]) for r in summary["runs"]}
                    if len(summary["runs"]) != 4 or variants != VARIANTS:
                        raise ValueError(f"missing or duplicate variants in {root}")
                    check_files(root, summary)
                    retained_resumes(root, summary)
                    group[arm] = summary
                    rows.extend(phase_rows(summary, arm))
                if paired and any(group["m2"][key] != group["m3"][key]
                                  for key in ("raw", "journal", "scope", "limits")):
                    raise ValueError(f"unmatched conditions in {directory}")
                groups.append(group)
        write(args.output, stem, dict(ci=ci, profiles=groups), rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--kind", choices=("audit", "paired"), default="audit")
    parser.add_argument("--download", type=Path)
    parser.add_argument("--ci", type=Path)
    args = parser.parse_args()
    if args.download and args.ci:
        observed(args)
    elif args.download or args.ci:
        parser.error("--download and --ci must be supplied together")
    else:
        historical(args.output)


if __name__ == "__main__":
    main()
