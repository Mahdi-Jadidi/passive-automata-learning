"""Compare compatibility and discovery toggles on the same pinned native CLI."""
import argparse
import json
from pathlib import Path
import sys

from p3_harness import load_manifest, run_stage
from p3_native import (HERE, INPUTS, MAKE_JOURNAL, MANIFEST, VERIFIER_LIMITS, artifact,
                       cli, flags, read_result, stage_sources)

ARMS = {"dense": [], "sparse": ["--sparse"], "sparse-join": ["--sparse", "--join"]}


def main():
    manifest = load_manifest(MANIFEST)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--case", choices=tuple(manifest), required=True)
    p.add_argument("--memory-mib", type=int, choices=(512, 1536), required=True)
    for name in ("producer", "verifier", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    args = p.parse_args()
    config = json.loads((HERE / "p3/review08-ablation.json").read_bytes())
    limits = config["limits"]
    root = args.output.resolve()
    root.mkdir(parents=True)
    raw, journal, scope = (root / f"{name}.json" for name in ("raw", "journal", "scope"))
    raw.write_bytes((INPUTS / f"{args.case}.json").read_bytes())
    original = artifact(raw)
    if original["sha256"] != manifest[args.case]["input_sha256"]:
        raise ValueError("original raw input mismatch")
    producer = root / "producer-source" / "selector_v2"
    verifier = root / "verifier-source"
    stage_sources(args.producer.resolve(), config["sources"]["producer"], producer)
    stage_sources(args.verifier.resolve(), config["sources"]["verifier"], verifier)

    def stage(argv, directory, name, runtime="normal"):
        return run_stage(argv, directory, name, limits["wall_seconds"], args.memory_mib,
                         runtime, extra_env={"PYTHONHOME": "", "PYTHONPATH": ""})

    verify_limits = [token for flag, key in VERIFIER_LIMITS.items()
                     for token in ("--" + flag, str(limits[key]))]
    paths = dict(input=raw, journal=journal, scope=scope)
    export = stage([sys.executable, "-B", "-P", "-c", MAKE_JOURNAL,
                    str(verifier), str(raw), str(journal)], root, "journal")
    binding = stage(cli("normal", verifier, "p3_frontier_verifier",
                        flags(config, "scope", paths) + verify_limits), root, "scope")
    trusted = read_result(scope)
    if export["returncode"] != 0 or binding["returncode"] != 0 or trusted is None:
        raise ValueError("independent empty-journal scope unavailable")

    rows = []
    order = list(ARMS)
    offset = (list(manifest).index(args.case) + (args.memory_mib == 512)) % len(order)
    order = order[offset:] + order[:offset]
    for mode in ("one", "all"):
        for runtime in ("normal", "optimized"):
            current = {}
            for arm in order:
                directory = root / f"{mode}-{runtime}-{arm}"
                directory.mkdir()
                proof, metrics = (directory / f"{name}.json" for name in ("proof", "metrics"))
                values = paths | dict(mode=mode, certificate=proof, metrics=metrics)
                produce = cli(runtime, producer.parent, config["producer_module"],
                              flags(config, "producer", limits | values) + ARMS[arm])
                row = dict(arm=arm, mode=mode, python_mode=runtime, status="INCOMPLETE",
                           search=stage(produce, directory, "search", runtime),
                           proof=artifact(proof), metrics=read_result(metrics), replays={})
                rows.append(row)
                current[arm] = row
                if row["search"]["returncode"] != 0 or not row["proof"]:
                    continue
                replay = flags(config, "verifier", values) + verify_limits
                replay += ["--expected-format", "p3-region-frontier/v2", "--expected-mode", mode]
                for variant, toggle in (("dense", []), ("sparse", ["--sparse-exact"])):
                    name = f"replay-{variant}"
                    process = stage(cli(runtime, verifier, "p3_frontier_verifier", replay + toggle),
                                    directory, name, runtime)
                    verdict = read_result(directory / f"{name}.stdout") or {}
                    row["replays"][variant] = dict(process=process, verdict=verdict)
                    if verdict.get("status") == "INVALID" and process["returncode"] == 1:
                        row["status"] = "INVALID"
                    if (variant == "sparse" and row["status"] != "INVALID"
                            and verdict.get("status") == "VERIFIED" and process["returncode"] == 0):
                        row["status"] = "VERIFIED"
                left, right = (row["replays"][key]["verdict"] for key in ("dense", "sparse"))
                if left.get("status") == right.get("status") == "VERIFIED" and left["result"] != right["result"]:
                    row["status"] = "INVALID"
            completed = [r for r in current.values() if r["status"] == "VERIFIED"]
            exact = [r["replays"]["sparse"]["verdict"]["result"] for r in completed]
            keys = ("optimum", "optima") if mode == "all" else ("optimum",)
            if exact and any(any(result[k] != exact[0][k] for k in keys) for result in exact):
                raise ValueError("independently verified arms disagree")
            if (current["dense"]["status"] == current["sparse"]["status"] == "VERIFIED"
                    and current["dense"]["proof"] != current["sparse"]["proof"]):
                raise ValueError("compatibility-only toggle changed completed proof bytes")
    if artifact(raw) != original:
        raise ValueError("original raw bytes changed")
    summary = dict(case=args.case, memory_mib=args.memory_mib, sources=config["sources"],
                   raw=original, journal=artifact(journal), scope=artifact(scope), order=order,
                   scope_phase=binding, journal_phase=export, runs=rows)
    (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if any(r["status"] == "INVALID" for r in rows):
        raise ValueError("independent replay rejected an ablation proof")


if __name__ == "__main__":
    main()
