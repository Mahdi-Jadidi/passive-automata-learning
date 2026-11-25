"""Run the pinned native P3 CLIs using the benchmark harness process worker."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

from p3_harness import load_manifest, run_stage, validate_raw_input


HERE = Path(__file__).resolve().parent
CONFIG = HERE / "p3/native.json"
MANIFEST = HERE / "review03/p3/input-manifest.json"
INPUTS = HERE / "p3/inputs"
VERIFIER_LIMITS = {
    "seconds": "cooperative_seconds",
    "max-nodes": "verifier_nodes",
    "max-depth": "verifier_depth",
    "max-work": "verifier_work",
    "max-exact-checks": "verifier_exact_checks",
    "max-entries": "verifier_entries",
    "max-journal-bytes": "journal_bytes",
    "max-proof-bytes": "proof_bytes",
    "max-raw-bytes": "raw_bytes",
}
LAUNCH = (
    "import runpy,sys; sys.path.insert(0,sys.argv.pop(1)); "
    "runpy.run_module(sys.argv.pop(1),run_name='__main__',alter_sys=True)"
)
MAKE_JOURNAL = """
import json
from pathlib import Path
import sys

sys.path.insert(0, sys.argv[1])
from independent_replay import sample_data
from p3_frontier_verifier import canonical

raw = json.loads(Path(sys.argv[2]).read_bytes())
journal = dict(version="selector-v2-journal/2", sample_digest=sample_data(raw)[3], events=[])
Path(sys.argv[3]).write_bytes(canonical(journal))
"""


def artifact(path):
    if not path.is_file():
        return None
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"sha256": digest, "bytes": path.stat().st_size}


def stage_sources(checkout, spec, destination):
    def git(*argv):
        return subprocess.check_output(["git", "-C", str(checkout), *argv]).strip().decode()

    if git("rev-parse", "HEAD") != spec["commit"]:
        raise ValueError(f"unexpected source HEAD in {checkout}")
    destination.mkdir(parents=True)
    for name, expected in spec["blobs"].items():
        path = checkout / spec["directory"] / name
        if git("hash-object", "--no-filters", str(path)) != expected:
            raise ValueError(f"source blob mismatch: {path}")
        (destination / name).write_bytes(path.read_bytes())


def read_result(path):
    if path.is_file() and path.stat().st_size:
        try:
            result = json.loads(path.read_bytes())
        except (ValueError, UnicodeError):
            return None
        if isinstance(result, dict):
            return result
    return None


def cli(python_mode, source, module, argv):
    interpreter = [sys.executable, "-B", "-P"]
    if python_mode == "optimized":
        interpreter.append("-O")
    return [*interpreter, "-c", LAUNCH, str(source), module, *argv]


def flags(config, key, values):
    return [token.format_map(values) for token in config[key]]


def bench(args, config, root, raw, journal, scope, producer, verifier, python_mode, mode):
    limits = config["limits"]
    values = dict(limits, input=raw, journal=journal, scope=scope, mode=mode)
    verify_limits = [arg for key, limit in VERIFIER_LIMITS.items()
                     for arg in ("--" + key, str(limits[limit]))]
    phases = {}

    def phase(name, argv):
        workdir = root / name
        workdir.mkdir(parents=True)
        record = run_stage(argv, workdir, name, limits["wall_seconds"], args.memory_mib,
                           python_mode, extra_env={"PYTHONPATH": "", "PYTHONHOME": ""})
        phases[name] = record
        return workdir, record

    def verify(name, proof):
        if not proof:
            phases[name] = {"status": "NOT RUN", "reason": "no usable producer certificate"}
            return
        argv = flags(config, "verifier", dict(values, certificate=proof)) + verify_limits
        workdir, record = phase(name, cli(python_mode, verifier, "p3_frontier_verifier", argv))
        result = read_result(workdir / f"{name}.stdout")
        if result:
            expected = {"VERIFIED": 0, "INVALID": 1, "INCOMPLETE": 2}
            status = result.get("status")
            if status in expected and record["returncode"] == expected[status]:
                record["native"] = result
                record["status"] = status
                if status == "INCOMPLETE" and (result.get("reason") or "").startswith("MemoryError"):
                    record["process_status"] = "MEMORY_ERROR"
                elif status != "VERIFIED":
                    record["process_status"] = "OK"
                return
        record.update(status="INCOMPLETE", reason="verifier emitted no consistent verdict")

    def produce(name, entries=None, resume=None):
        proof = root / name / "certificate.json"
        metrics = proof.with_name("metrics.json")
        overrides = dict(values, certificate=proof, metrics=metrics)
        if entries is not None:
            overrides["producer_entries"] = entries
        argv = flags(config, "producer", overrides)
        if resume:
            argv += ["--resume", str(resume)]
        workdir, record = phase(name, cli(python_mode, producer.parent, "selector_v2.edr_search", argv))
        record.update(certificate=artifact(proof), metrics_file=artifact(metrics))
        native = read_result(metrics)
        if record["returncode"] == 0 and native and record["certificate"]:
            declared = native.get("status")
            if declared in ("EXHAUSTED", "PARTIAL"):
                cert = json.loads(proof.read_bytes())
                if cert["declared_status"] != declared:
                    record.update(status="INVALID", reason="certificate and metrics disagree")
                    return None
                incumbent = cert["incumbent"]
                record.update(status=declared, native=native,
                              incumbent_cost=None if incumbent is None else incumbent["cost"],
                              open_nodes=sum(node["kind"] == "OPEN" for node in cert["nodes"]),
                              unresolved_suffixes=sum(node["kind"] == "SPLIT" and
                                                       node["cursor"] < node["alternative_count"]
                                                       for node in cert["nodes"]))
                return proof
        stdout = read_result(workdir / f"{name}.stdout")
        stderr = read_result(workdir / f"{name}.stderr")
        native = stdout or stderr or {}
        reason = native.get("reason") or record["process_status"]
        if reason == "MEMORY_ERROR":
            record["process_status"] = reason
        status = "INVALID" if native.get("status") == "INVALID" else "INCOMPLETE"
        record.update(status=status, reason=reason)
        return None

    direct = []
    for i in (1, 2):
        proof = produce(f"producer-{i}")
        direct.append(phases[f"producer-{i}"])
        verify(f"verifier-{i}", proof)

    checkpoint = produce("checkpoint", entries=1)
    checkpoint_status = phases["checkpoint"]["status"]
    if checkpoint_status == "PARTIAL":
        verify("checkpoint-verifier", checkpoint)
        resumed = produce("resumed", resume=checkpoint)
        verify("resumed-verifier", resumed)
        resume_status = compare_certificates(direct[0], phases["resumed"])
    else:
        resume_status = "NOT NEEDED" if checkpoint_status == "EXHAUSTED" else "CENSORED"

    determinism = compare_certificates(*direct, compare_metrics=True)
    verdicts = [phases[name]["status"] for name in ("producer-1", "producer-2", "verifier-1", "verifier-2")]
    status = "INCOMPLETE"
    if "INVALID" in verdicts:
        status = "INVALID"
    elif verdicts == ["EXHAUSTED", "EXHAUSTED", "VERIFIED", "VERIFIED"] and determinism == "MATCH":
        status = "VERIFIED"
    certified = phases["verifier-1"]["native"]["result"] if status == "VERIFIED" else None
    return dict(mode=mode, python_mode=python_mode, status=status, phases=phases,
                certified_result=certified, determinism=determinism,
                checkpoint_resume=resume_status)


def compare_certificates(first, second, *, compare_metrics=False):
    if not first.get("certificate") or not second.get("certificate"):
        return "CENSORED"
    equal = first["certificate"] == second["certificate"] and first["status"] == second["status"]
    if compare_metrics:
        equal = equal and first.get("native") == second.get("native")
    return "MATCH" if equal else "DIFFERENT"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--producer-root", required=True, type=Path)
    parser.add_argument("--verifier-root", required=True, type=Path)
    parser.add_argument("--case", required=True, choices=load_manifest(MANIFEST))
    parser.add_argument("--memory-mib", required=True, type=int, choices=(512, 1536))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_bytes())
    limits = config["limits"]
    root = args.output.resolve()
    root.mkdir(parents=True)
    raw, journal, scope = (root / name for name in ("raw.json", "journal.json", "trusted.json"))
    data = (INPUTS / f"{args.case}.json").read_bytes()
    row = load_manifest(MANIFEST)[args.case]
    if hashlib.sha256(data).hexdigest() != row["input_sha256"]:
        raise ValueError("raw fixture differs from manifest")
    validate_raw_input(data)
    raw.write_bytes(data)
    producer = root / "producer-source/selector_v2"
    verifier = root / "verifier-source"
    stage_sources(args.producer_root.resolve(), config["sources"]["producer"], producer)
    stage_sources(args.verifier_root.resolve(), config["sources"]["verifier"], verifier)
    summary = dict(case=args.case, address_space_mib=args.memory_mib, limits=limits,
                   sources=config["sources"], config=artifact(CONFIG), manifest=artifact(MANIFEST),
                   fixture=row, raw=artifact(raw), host=platform.platform(), python=sys.version,
                   hash_seed=0, operational_status="INCOMPLETE", runs=[])
    argv = [sys.executable, "-B", "-P", "-c", MAKE_JOURNAL, str(verifier), str(raw), str(journal)]
    extra_env = {"PYTHONPATH": "", "PYTHONHOME": ""}
    summary["journal_phase"] = run_stage(argv, root, "journal", limits["wall_seconds"],
                                         args.memory_mib, "normal", extra_env=extra_env)
    summary["journal"] = artifact(journal)
    if summary["journal_phase"]["returncode"] == 0 and summary["journal"]:
        values = dict(input=raw, journal=journal, scope=scope)
        argv = flags(config, "scope", values)
        argv += [arg for key, limit in VERIFIER_LIMITS.items() for arg in ("--" + key, str(limits[limit]))]
        summary["scope_phase"] = run_stage(cli("normal", verifier, "p3_frontier_verifier", argv),
                                           root, "scope", limits["wall_seconds"], args.memory_mib,
                                           "normal", extra_env=extra_env)
    summary["scope"] = artifact(scope)
    if summary.get("scope_phase", {}).get("returncode") == 0 and summary["scope"]:
        trusted = json.loads(scope.read_bytes())
        if trusted["root_owner"] != list(range(row["alphabet"])):
            raise ValueError("empty journal did not replay to identity root")
        summary["base_lower_bound"] = row["alphabet"] - len(set(trusted["root_owner"]))
        for mode in ("one", "all"):
            pair = []
            for python_mode in ("normal", "optimized"):
                run = bench(args, config, root / f"{mode}-{python_mode}", raw, journal, scope,
                            producer, verifier, python_mode, mode)
                summary["runs"].append(run)
                pair.append(run)
            parity = compare_certificates(*(run["phases"]["producer-1"] for run in pair),
                                          compare_metrics=True)
            for run in pair:
                run["normal_optimized_parity"] = parity
    else:
        summary["status"] = "NOT RUN"
        summary["reason"] = "journal or independently replayed scope unavailable"
    (root / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    for run in summary["runs"]:
        print(args.case, args.memory_mib, run["mode"], run["python_mode"], run["status"],
              run["determinism"], run["checkpoint_resume"], run["normal_optimized_parity"], flush=True)
    if not summary["runs"]:
        print(args.case, summary["status"], summary["reason"], flush=True)


if __name__ == "__main__":
    main()
