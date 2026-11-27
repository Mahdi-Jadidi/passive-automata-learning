"""Validate CI pipeline artifacts and export per-phase and end-to-end observations."""
import argparse
import csv
import gzip
import hashlib
import json
from itertools import product
from pathlib import Path

CASES = ("medium_choice", "huge_choice_active", "hdfs_1024", "hdfs_holdout_1024_uncapped")
CONFIG = Path(__file__).resolve().parent / "p3/review08-pipeline.json"
MANIFEST = CONFIG.parent.parent / "review03/p3/input-manifest.json"


def artifact(path):
    if not path.is_file():
        return None
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"sha256": digest, "bytes": path.stat().st_size}


def export_ablation(download, ci, output):
    config = json.loads(CONFIG.with_name("review08-ablation.json").read_bytes())
    inputs = {r["case"]: r["input_sha256"] for r in json.loads(MANIFEST.read_bytes())}
    cases, rows = [], []
    for case, sha256 in inputs.items():
        for memory in (512, 1536):
            root = download / f"review08-ablation-{case}-{memory}"
            data = json.loads((root / "summary.json").read_bytes())
            if (data["case"], data["memory_mib"], data["sources"], data["raw"]["sha256"]) != (
                    case, memory, config["sources"], sha256):
                raise ValueError(f"wrong case or pins: {root}")
            for name in ("raw", "journal", "scope"):
                if data[name] != artifact(root / (name + ".json")):
                    raise ValueError(f"retained artifact mismatch: {root}/{name}")
            cases.append(data)
            expected = {(m, p, a) for m in ("one", "all") for p in ("normal", "optimized")
                        for a in ("dense", "sparse", "sparse-join")}
            variants = {(r["mode"], r["python_mode"], r["arm"]) for r in data["runs"]}
            if variants != expected or len(data["runs"]) != len(expected):
                raise ValueError("missing or duplicate ablation variants")
            for run in data["runs"]:
                mode, runtime, arm = (run[k] for k in ("mode", "python_mode", "arm"))
                actual = artifact(root / f"{mode}-{runtime}-{arm}" / "proof.json")
                if actual != run["proof"]:
                    raise ValueError("retained proof mismatch")
                metrics = run["metrics"] or {}
                search = run["search"]
                row = dict(case=case, memory_mib=memory, mode=mode, runtime=runtime, arm=arm,
                           status=run["status"], phase="search",
                           phase_status=metrics.get("status", search["process_status"]),
                           reason=metrics.get("stop_reason"), wall_seconds=search["wall_seconds"],
                           peak_rss_kib=search.get("peak_rss_kib"), proof_bytes=(actual or {}).get("bytes"),
                           proof_sha256=(actual or {}).get("sha256"))
                names = ("nodes", "work", "compatibility_work", "compatibility_seconds",
                         "discovery_work", "discovery_seconds", "witness_work", "witness_probes",
                         "witness_local_caps", "cross_splits", "join_work", "join_probes",
                         "join_local_caps", "join_hits", "root_check", "root_discovery")
                row.update({name: metrics.get(name) for name in names})
                rows.append(row)
                for variant, replay in run["replays"].items():
                    verdict, process = replay["verdict"], replay["process"]
                    rows.append(row | dict(
                        phase=f"replay-{variant}",
                        phase_status=verdict.get("status", process["process_status"]),
                        reason=verdict.get("reason"), wall_seconds=process.get("wall_seconds"),
                        peak_rss_kib=process.get("peak_rss_kib")) | dict.fromkeys(names))
    write_tables(output, "ablation", ci, cases, rows)


def write_tables(output, stem, ci, cases, rows):
    output.mkdir(parents=True, exist_ok=True)
    (output / f"{stem}.json").write_bytes((json.dumps(dict(ci=ci, cases=cases), indent=2)
                                          + "\n").encode())
    with (output / f"{stem}.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(config_path=CONFIG):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("download", type=Path)
    p.add_argument("ci", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--ablation", action="store_true")
    args = p.parse_args()
    config = json.loads(config_path.read_bytes())
    inputs = {r["case"]: r["input_sha256"] for r in json.loads(MANIFEST.read_bytes())}
    ci = json.loads(args.ci.read_bytes())
    if ci["status"] != "completed" or ci["conclusion"] != "success":
        raise ValueError("the CI run did not complete successfully")
    if args.ablation:
        export_ablation(args.download, ci, args.output)
        return
    cases, rows, retained = [], [], {}
    review09 = config_path != CONFIG
    origins = ("retained", "fresh") if review09 else (None,)
    historical = json.loads((CONFIG.parent.parent / "results/review08/pipeline.json").read_bytes())
    for case, memory, origin in product(CASES, (512, 1536), origins):
        name = f"review09-pipeline-{case}-{memory}-{origin}" if origin else f"review08-pipeline-{case}-{memory}"
        root = args.download / name
        data = json.loads((root / "summary.json").read_bytes())
        if (data["case"], data["memory_mib"], data["sources"], data["raw"]) != (
                case, memory, config["sources"], artifact(root / "raw.json")):
            raise ValueError(f"case manifest does not match retained bytes: {root}")
        if data["raw"]["sha256"] != inputs[case]:
            raise ValueError(f"wrong original input: {root}")
        if origin:
            label = "RETAINED_REVIEW08" if origin == "retained" else "NEW_AUTHORITATIVE_RAW_EXPORT"
            if data["journal_origin"] != label:
                raise ValueError(f"incorrect journal origin: {root}")
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
            if origin:
                for phase in ("search", "checkpoint", "replay", "checkpoint-replay"):
                    argv = run["phases"].get(phase, {}).get("command_argv")
                    if argv is None:
                        continue
                    required = ({config["producer_module"], "--sparse"} if phase in ("search", "checkpoint")
                                else {"p3_frontier_verifier", "--sparse-exact", "p3-region-frontier/v2"})
                    if not required.issubset(argv) or ("-O" in argv) != (runtime == "optimized"):
                        raise ValueError(f"unexpected sparse command: {directory}/{phase}")
                    if "--join" in argv:
                        raise ValueError(f"unexpected join arm: {directory}/{phase}")
            if origin == "retained":
                prior = next(c["runs"][0] for c in historical["cases"] if c["case"] == case)
                if any(run[kind] != prior[kind] for kind in ("journal", "scope")):
                    raise ValueError("retained input differs from Review08")
            scope = run.pop("root_owner", None)
            if scope is not None:
                trusted = json.loads((directory / "scope.json").read_bytes())
                if trusted["root_owner"] != scope:
                    raise ValueError("retained scope differs")
                run["root_size"] = len(scope)
                if not origin and run["mandatory_merges"]:
                    for name in ("journal", "scope"):
                        filename = f"{case}-{name}-{run[name]['sha256']}.json.gz"
                        retained[filename] = directory / (name + ".json")
            for observation in run.get("raw_ledger", []):
                owner = observation.pop("owner", None)
                if owner is not None:
                    observation["owner_size"] = len(owner)
                    observation["matches_independent_scope"] = owner == scope if scope is not None else None
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
                             reason=metrics.get("stop_reason"),
                             wall_seconds=run["elapsed_seconds"],
                             peak_rss_kib=run["peak_rss_kib"],
                             mandatory_merges=run.get("mandatory_merges"),
                             nodes=metrics.get("nodes"), work=metrics.get("work"),
                             witness_work=metrics.get("witness_work"),
                             witness_probes=metrics.get("witness_probes"),
                             witness_local_caps=metrics.get("witness_local_caps"),
                             proof_bytes=(run["proof"] or {}).get("bytes"),
                             completed_resume=equality, process_status="", returncode=""))
            total = rows[-1]
            sparse_fields = ("compatibility_work", "compatibility_seconds", "compatibility_peak_index_bytes",
                             "discovery_work", "discovery_seconds", "resumed_nodes")
            if origin:
                total["journal_origin"] = origin
                total.update({field: metrics.get(field) for field in sparse_fields})
                total.update(hard_seconds_cap=run["wall_seconds_cap"],
                             proof_sha256=(run["proof"] or {}).get("sha256"))
            for phase, value in run["phases"].items():
                phase_metrics = {}
                if phase == "search":
                    phase_metrics = metrics
                elif phase == "checkpoint":
                    checkpoint_metrics = directory / "checkpoint-metrics.json"
                    if checkpoint_metrics.is_file():
                        phase_metrics = json.loads(checkpoint_metrics.read_bytes())
                        run["checkpoint_metrics"] = phase_metrics
                stage_fields = {}
                if origin:
                    stage_fields = {field: phase_metrics.get(field) for field in sparse_fields}
                    proof_kind = {"search": "proof", "replay": "proof", "checkpoint": "checkpoint",
                                  "checkpoint-replay": "checkpoint"}.get(phase)
                    stage_fields.update(hard_seconds_cap=value.get("hard_seconds_cap"),
                                        proof_sha256=(run.get(proof_kind) or {}).get("sha256"))
                verdict = (run.get(phase.replace("-", "_"), {})
                           if phase in ("replay", "checkpoint-replay") else {})
                rows.append(dict(total | stage_fields | dict(
                    phase=phase, wall_seconds=value.get("wall_seconds"),
                    peak_rss_kib=value.get("peak_rss_kib"), nodes=phase_metrics.get("nodes"),
                    work=phase_metrics.get("work"), witness_work=phase_metrics.get("witness_work"),
                    witness_probes=phase_metrics.get("witness_probes"),
                    witness_local_caps=phase_metrics.get("witness_local_caps"),
                    proof_bytes=total["proof_bytes"] if phase == "search" else
                    ((run["checkpoint"] or {}).get("bytes") if phase == "checkpoint" else None),
                    reason=phase_metrics.get("stop_reason") or verdict.get("reason"),
                    process_status=verdict.get("status") or value.get("process_status", value.get("status")),
                    returncode=value.get("returncode"))))
            for phase in run.get("raw_ledger", []):
                internal = dict.fromkeys((*sparse_fields, "hard_seconds_cap", "proof_sha256")) if origin else {}
                rows.append(total | internal | dict(
                    phase=phase["phase"], wall_seconds=phase["elapsed_seconds"],
                    peak_rss_kib=None, nodes=None, work=phase.get("work"),
                    witness_work=None, witness_probes=None, witness_local_caps=None,
                    proof_bytes=None, reason=None, process_status=phase.get("state"), returncode=None))
    write_tables(args.output, "pipeline", ci, cases, rows)
    if retained:
        evidence = args.output / "trusted-roots"
        evidence.mkdir(exist_ok=True)
        for name, source in retained.items():
            (evidence / name).write_bytes(gzip.compress(source.read_bytes(), mtime=0))


if __name__ == "__main__":
    main()
