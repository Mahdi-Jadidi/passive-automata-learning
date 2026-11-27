"""Run matched sparse-v2 and rank-v3 RAW-only benchmark routes."""
import argparse
import json
from pathlib import Path
import sys

from p3_harness import load_manifest, run_stage
from p3_native import (HERE, INPUTS, MAKE_JOURNAL, MANIFEST, VERIFIER_LIMITS,
                       artifact, cli, flags, read_result, stage_sources)
from review08_pipeline import pipeline

CONFIG = HERE / "p3/review09-rank.json"
ARMS = {"sparse-v2": ("v2", []), "rank-v3": ("v3", ["--rank"])}
ORACLE = """
import json
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from p3_rgs12_oracle import oracle
print(json.dumps(oracle(json.loads(Path(sys.argv[2]).read_bytes()), seconds=25)))
"""


def main():
    config = json.loads(CONFIG.read_bytes())
    manifest = load_manifest(MANIFEST)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=(*manifest, *config["targets"]), required=True)
    parser.add_argument("--memory-mib", type=int, choices=(512, 1536), required=True)
    for role in ("producer", "verifier", "output"):
        parser.add_argument("--" + role, type=Path, required=True)
    args = parser.parse_args()
    limits = config["limits"]
    root = args.output.resolve()
    root.mkdir(parents=True)
    raw, journal, scope = (root / f"{name}.json" for name in ("raw", "journal", "scope"))
    producer = root / "producer-source/selector_v2"
    verifier = root / "verifier-source"
    stage_sources(args.producer.resolve(), config["sources"]["producer"], producer)
    stage_sources(args.verifier.resolve(), config["sources"]["verifier"], verifier)
    targeted = args.case in config["targets"]
    source = args.producer / config["target_directory"] if targeted else INPUTS
    raw.write_bytes((source / f"{args.case}.json").read_bytes())
    observed = artifact(raw)
    expected = config["targets"][args.case] if targeted else manifest[args.case]["input_sha256"]
    if observed["sha256"] != expected:
        raise ValueError("wrong RAW fixture bytes")

    def setup(argv, stage):
        record = run_stage(argv, root, stage, limits["wall_seconds"], args.memory_mib,
                           "normal", extra_env={"PYTHONPATH": "", "PYTHONHOME": ""})
        if record["returncode"] != 0:
            raise ValueError(f"{stage} failed")
        return record

    python = [sys.executable, "-B", "-P", "-c"]
    journal_phase = setup([*python, MAKE_JOURNAL, str(verifier), str(raw), str(journal)], "journal")
    verify_caps = [item for flag, key in VERIFIER_LIMITS.items()
                   for item in ("--" + flag, str(limits[key]))]
    values = dict(input=raw, journal=journal, scope=scope)
    scope_phase = setup(cli("normal", verifier, "p3_frontier_verifier",
                            flags(config, "scope", values) + verify_caps), "bind")
    retained = {"journal": journal.read_bytes(), "scope": scope.read_bytes()}
    truth = None
    oracle_phase = None
    if targeted:
        oracle_phase = setup([*python, ORACLE, str(verifier), str(raw)], "oracle")
        census = read_result(root / "oracle.stdout")
        if census["status"] != "VERIFIED":
            raise ValueError("targeted literal RGS did not complete")
        truth = census["result"]

    order = list(ARMS)
    if (list((*manifest, *config["targets"])).index(args.case) + (args.memory_mib == 512)) % 2:
        order.reverse()
    runs = {}
    for mode in ("one", "all"):
        for runtime in ("normal", "optimized"):
            for arm in order:
                version, toggles = ARMS[arm]
                settings = config | dict(expected_format=f"p3-region-frontier/{version}",
                                         producer_flags=config["producer_flags"] + toggles)
                for restart in (False, True):
                    route = f"{mode}-{runtime}-{arm}-{'restart' if restart else 'fresh'}"
                    directory = root / route
                    row = pipeline(args, settings, directory, raw, producer, verifier,
                                   None, mode, runtime, restart, retained)
                    row["arm"] = arm
                    row.pop("root_owner", None)
                    for kind in ("proof", "checkpoint"):
                        path = directory / f"{kind}.json"
                        if row[kind]:
                            document = read_result(path)
                            if document is None:
                                raise ValueError(f"missing proof document: {path}")
                            row[f"{kind}_rank_leaves"] = sum(
                                node.get("closure", {}).get("reason") == "RANK_COST"
                                for node in document["nodes"])
                    runs[mode, runtime, arm, restart] = row

    for (mode, runtime, arm, restart), row in runs.items():
        if row["status"] == "INVALID":
            raise ValueError("independent replay rejected a proof")
        row["completed_resume_match"] = None
        if row["status"] != "VERIFIED":
            if targeted:
                raise ValueError("targeted route did not verify")
            continue
        result = row["replay"]["result"]
        if truth and (result["optimum"] != truth["optimum"] or result["owner"] not in truth["optima"]
                      or (mode == "all" and result["optima"] != truth["optima"])):
            raise ValueError("targeted result differs from literal RGS")
        peer = runs[mode, runtime, "sparse-v2" if arm == "rank-v3" else "rank-v3", restart]
        if peer["status"] == "VERIFIED":
            other = peer["replay"]["result"]
            if result["optimum"] != other["optimum"] or (mode == "all" and result["optima"] != other["optima"]):
                raise ValueError("completed arms disagree")
        fresh = runs[mode, runtime, arm, False]
        if restart and fresh["status"] == "VERIFIED":
            row["completed_resume_match"] = row["proof"] == fresh["proof"]
            if not row["completed_resume_match"]:
                raise ValueError("completed resume proof differs")
    if targeted:
        mode = {"equality": "one", "strict": "all", "fractional": "one"}[args.case]
        if any(not runs[mode, runtime, "rank-v3", restart].get("proof_rank_leaves")
               for runtime in ("normal", "optimized") for restart in (False, True)):
            raise ValueError("targeted rank cutoff did not fire")
    summary = dict(case=args.case, targeted=targeted, memory_mib=args.memory_mib,
                   sources=config["sources"], raw=observed, journal=artifact(journal),
                   scope=artifact(scope), oracle=truth, oracle_phase=oracle_phase,
                   journal_phase=journal_phase, scope_phase=scope_phase, runs=list(runs.values()))
    (root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
