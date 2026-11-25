"""Reproducible, input-only P3 EDR-BB benchmark harness (Linux/Python 3.10+).

This is an experimental runner, not a solver, proof checker, or production schema.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
from typing import Any

SOLVER_SCHEMA = "p3-benchmark-solver/1"
VERIFIER_SCHEMA = "p3-benchmark-verifier/1"
SOLVER_STATUSES = {"COMPLETE_CANDIDATE", "COMPLETE_INFEASIBLE", "INCOMPLETE", "INVALID"}
VERIFIER_STATUSES = {"VERIFIED", "INCOMPLETE", "INVALID"}
SOLVER_COUNTERS = (
    "generated_regions", "expanded_regions", "exact_checks", "pruned_regions",
    "frontier_size", "work_units", "entry_count",
)
VERIFIER_COUNTERS = ("regions_replayed", "exact_checks", "frontier_size")
PLACEHOLDERS = {
    "python", "input", "certificate", "checkpoint", "result", "work_cap",
    "entry_cap", "seconds", "memory_mib", "resume_flag",
}


class HarnessError(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise HarnessError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json_bytes(raw: bytes) -> Any:
    try:
        return json.loads(raw, object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HarnessError(f"invalid JSON: {exc}") from exc


def validate_raw_input(raw: bytes) -> dict[str, Any]:
    data = load_json_bytes(raw)
    if type(data) is not dict or set(data) != {"alphabet", "positive", "negative"}:
        raise HarnessError("solver input must contain exactly alphabet, positive, negative")
    alphabet = data["alphabet"]
    if (type(alphabet) is not list or
            any(type(symbol) is not str or not symbol for symbol in alphabet) or
            len(set(alphabet)) != len(alphabet)):
        raise HarnessError("invalid ordered alphabet")
    allowed = set(alphabet)
    for field in ("positive", "negative"):
        traces = data[field]
        if type(traces) is not list:
            raise HarnessError(f"{field} must be an ordered list")
        for trace in traces:
            if type(trace) is not list or any(type(token) is not str or token not in allowed for token in trace):
                raise HarnessError(f"invalid ordered trace in {field}")
    return data


def load_manifest(path: Path) -> dict[str, dict[str, Any]]:
    raw = path.read_bytes()
    manifest = load_json_bytes(raw)
    if type(manifest) is not list:
        raise HarnessError("fixture manifest must be a JSON array")
    result: dict[str, dict[str, Any]] = {}
    for row in manifest:
        if type(row) is not dict:
            raise HarnessError("manifest row must be an object")
        case = row.get("case")
        digest = row.get("input_sha256")
        if type(case) is not str or not case or type(digest) is not str or len(digest) != 64:
            raise HarnessError("manifest row requires case and input_sha256")
        if case in result:
            raise HarnessError(f"duplicate fixture case: {case}")
        result[case] = row
    return result


def _counter_object(value: Any, required: tuple[str, ...], label: str) -> dict[str, int]:
    if type(value) is not dict:
        raise HarnessError(f"{label}.counters must be an object")
    counters: dict[str, int] = {}
    for name in required:
        number = value.get(name)
        if type(number) is not int or number < 0:
            raise HarnessError(f"{label}.counters.{name} must be a non-negative integer")
        counters[name] = number
    return counters


def validate_solver_result(path: Path) -> dict[str, Any]:
    data = load_json_bytes(path.read_bytes())
    if type(data) is not dict or data.get("schema") != SOLVER_SCHEMA:
        raise HarnessError(f"solver result schema must be {SOLVER_SCHEMA}")
    status = data.get("status")
    if status not in SOLVER_STATUSES:
        raise HarnessError("unknown solver search status")
    counters = _counter_object(data.get("counters"), SOLVER_COUNTERS, "solver")
    return {"schema": SOLVER_SCHEMA, "status": status, "counters": counters}


def validate_verifier_result(path: Path) -> dict[str, Any]:
    data = load_json_bytes(path.read_bytes())
    if type(data) is not dict or data.get("schema") != VERIFIER_SCHEMA:
        raise HarnessError(f"verifier result schema must be {VERIFIER_SCHEMA}")
    status = data.get("status")
    if status not in VERIFIER_STATUSES:
        raise HarnessError("unknown verifier status")
    counters = _counter_object(data.get("counters"), VERIFIER_COUNTERS, "verifier")
    return {"schema": VERIFIER_SCHEMA, "status": status, "counters": counters}


def load_config(path: Path) -> dict[str, Any]:
    config = load_json_bytes(path.read_bytes())
    if type(config) is not dict or config.get("schema") != "p3-benchmark-adapter/1":
        raise HarnessError("config schema must be p3-benchmark-adapter/1")
    if set(config) - {"schema", "solver", "verifier", "source_pins"}:
        raise HarnessError("unsupported adapter config fields")
    if "source_pins" in config and type(config["source_pins"]) is not dict:
        raise HarnessError("source_pins must be an object")
    for stage in ("solver", "verifier"):
        spec = config.get(stage)
        allowed_keys = {"argv", "resume_flag"} if stage == "solver" else {"argv"}
        if type(spec) is not dict or set(spec) - allowed_keys or type(spec.get("argv")) is not list or not spec["argv"]:
            raise HarnessError(f"config.{stage}.argv must be a non-empty string array with supported keys only")
        if any(type(arg) is not str or not arg for arg in spec["argv"]):
            raise HarnessError(f"config.{stage}.argv entries must be non-empty strings")
        for arg in spec["argv"]:
            # Reject unknown placeholders and prevent accidental evaluation-path injection.
            import string
            for _, field, _, _ in string.Formatter().parse(arg):
                if field is not None and field not in PLACEHOLDERS:
                    raise HarnessError(f"unsupported command placeholder: {{{field}}}")
    return config


def render_argv(spec: dict[str, Any], values: dict[str, str]) -> list[str]:
    argv: list[str] = []
    for token in spec["argv"]:
        if token == "{resume_flag}" and not values.get("resume_flag"):
            continue
        rendered = token.format_map(values)
        if "\x00" in rendered:
            raise HarnessError("NUL in command argument")
        argv.append(rendered)
    return argv


def _worker(spec_path: Path) -> int:
    spec = load_json_bytes(spec_path.read_bytes())
    argv = spec["argv"]
    memory_mib = spec["memory_mib"]
    seconds = spec["seconds"]
    env = {**os.environ, **spec["env"], "PYTHONHASHSEED": "0"}

    def limit_address_space() -> None:
        cap = int(memory_mib) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    status = "PROCESS_ERROR"
    returncode: int | None = None
    started = time.perf_counter()
    try:
        with Path(spec["stdout_path"]).open("wb") as stdout, Path(spec["stderr_path"]).open("wb") as stderr:
            completed = subprocess.run(
                argv, cwd=spec["cwd"], env=env, stdin=subprocess.DEVNULL,
                stdout=stdout, stderr=stderr, timeout=seconds,
                preexec_fn=limit_address_space, check=False,
            )
        returncode = completed.returncode
        if returncode == 0:
            status = "OK"
        elif b"MemoryError" in Path(spec["stderr_path"]).read_bytes():
            status = "MEMORY_ERROR"
    except subprocess.TimeoutExpired:
        status = "TIMEOUT"
    except OSError as exc:
        Path(spec["stderr_path"]).write_text(f"worker OSError: {exc}\n")
        status = "PROCESS_ERROR"
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    print(json.dumps({
        "process_status": status,
        "returncode": returncode,
        "elapsed_seconds": time.perf_counter() - started,
        "peak_rss_kib": int(usage.ru_maxrss),
    }, sort_keys=True))
    return 0


def run_stage(
    argv: list[str], run_dir: Path, stage: str, seconds: float, memory_mib: int,
    python_mode: str,
) -> dict[str, Any]:
    stdout_path = run_dir / f"{stage}.stdout"
    stderr_path = run_dir / f"{stage}.stderr"
    spec_path = run_dir / f"{stage}.worker.json"
    env = {"PYTHONOPTIMIZE": "1" if python_mode == "optimized" else "0"}
    spec = {
        "argv": argv, "cwd": str(run_dir), "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path), "seconds": seconds, "memory_mib": memory_mib,
        "env": env,
    }
    spec_path.write_text(json.dumps(spec, sort_keys=True) + "\n")
    started = time.perf_counter()
    try:
        worker = subprocess.run(
            [sys.executable, "-B", str(Path(__file__).resolve()), "--worker", str(spec_path)],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=seconds + 3.0, check=False,
            env={**os.environ, "PYTHONHASHSEED": "0", "PYTHONOPTIMIZE": "0"},
        )
        if worker.returncode != 0:
            raise HarnessError(f"stage worker failed: {worker.stderr.decode(errors='replace')}")
        measured = load_json_bytes(worker.stdout)
    except subprocess.TimeoutExpired:
        measured = {"process_status": "TIMEOUT", "returncode": None,
                    "elapsed_seconds": time.perf_counter() - started, "peak_rss_kib": None}
    except (OSError, ValueError) as exc:
        measured = {"process_status": "PROCESS_ERROR", "returncode": None,
                    "elapsed_seconds": time.perf_counter() - started, "peak_rss_kib": None,
                    "worker_error": str(exc)}
    stdout = stdout_path.read_bytes() if stdout_path.exists() else b""
    stderr = stderr_path.read_bytes() if stderr_path.exists() else b""
    return {
        **measured,
        "command_argv": argv,
        "command_sha256": sha256(json.dumps(argv, separators=(",", ":")).encode()),
        "wall_seconds": time.perf_counter() - started,
        "stdout_sha256": sha256(stdout),
        "stderr_sha256": sha256(stderr),
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
    }


def _stage_values(
    *, input_path: Path, certificate: Path, checkpoint: Path, result: Path,
    work_cap: int, entry_cap: int, seconds: float, memory_mib: int,
    resume_flag: str = "",
) -> dict[str, str]:
    return {
        "python": sys.executable,
        "input": str(input_path.resolve()),
        "certificate": str(certificate.resolve()),
        "checkpoint": str(checkpoint.resolve()),
        "result": str(result.resolve()),
        "work_cap": str(work_cap),
        "entry_cap": str(entry_cap),
        "seconds": str(seconds),
        "memory_mib": str(memory_mib),
        "resume_flag": resume_flag,
    }


def _solver_once(
    config: dict[str, Any], input_path: Path, run_dir: Path, *,
    work_cap: int, entry_cap: int, seconds: float, memory_mib: int,
    python_mode: str, resume: bool = False, checkpoint: Path | None = None,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=False)
    cert = run_dir / "certificate.json"
    checkpoint_path = checkpoint or (run_dir / "checkpoint.json")
    result_path = run_dir / "solver-result.json"
    spec = config["solver"]
    values = _stage_values(
        input_path=input_path, certificate=cert, checkpoint=checkpoint_path,
        result=result_path, work_cap=work_cap, entry_cap=entry_cap,
        seconds=seconds, memory_mib=memory_mib,
        resume_flag=str(spec.get("resume_flag", "")) if resume else "",
    )
    argv = render_argv(spec, values)
    measured = run_stage(argv, run_dir, "solver", seconds, memory_mib, python_mode)
    out: dict[str, Any] = {"process": measured, "result": None, "certificate_sha256": None,
                           "certificate_bytes": None, "checkpoint_exists": checkpoint_path.exists(),
                           "checkpoint_sha256": None, "checkpoint_bytes": None}
    if measured["process_status"] != "OK":
        return out
    if not result_path.is_file():
        out["adapter_error"] = "solver result file missing"
        return out
    try:
        parsed = validate_solver_result(result_path)
    except (HarnessError, OSError) as exc:
        out["adapter_error"] = str(exc)
        return out
    out["result"] = parsed
    result_bytes = result_path.read_bytes()
    out["solver_result_sha256"] = sha256(result_bytes)
    out["solver_result_bytes"] = len(result_bytes)
    if cert.is_file():
        raw_cert = cert.read_bytes()
        out["certificate_sha256"] = sha256(raw_cert)
        out["certificate_bytes"] = len(raw_cert)
    if parsed["status"] in ("COMPLETE_CANDIDATE", "COMPLETE_INFEASIBLE") and not cert.is_file():
        out["adapter_error"] = "complete solver result without certificate artifact"
    out["checkpoint_exists"] = checkpoint_path.is_file()
    if checkpoint_path.is_file():
        checkpoint_bytes = checkpoint_path.read_bytes()
        out["checkpoint_sha256"] = sha256(checkpoint_bytes)
        out["checkpoint_bytes"] = len(checkpoint_bytes)
    return out


def _verify_once(
    config: dict[str, Any], input_path: Path, certificate: Path, run_dir: Path, *,
    work_cap: int, entry_cap: int, seconds: float, memory_mib: int, python_mode: str,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=False)
    result_path = run_dir / "verifier-result.json"
    values = _stage_values(
        input_path=input_path, certificate=certificate, checkpoint=run_dir / "unused-checkpoint.json",
        result=result_path, work_cap=work_cap, entry_cap=entry_cap, seconds=seconds, memory_mib=memory_mib,
    )
    argv = render_argv(config["verifier"], values)
    measured = run_stage(argv, run_dir, "verifier", seconds, memory_mib, python_mode)
    out: dict[str, Any] = {"process": measured, "result": None}
    if measured["process_status"] != "OK":
        return out
    if not result_path.is_file():
        out["adapter_error"] = "verifier result file missing"
        return out
    try:
        result_bytes = result_path.read_bytes()
        out["result"] = validate_verifier_result(result_path)
        out["verifier_result_sha256"] = sha256(result_bytes)
        out["verifier_result_bytes"] = len(result_bytes)
    except (HarnessError, OSError) as exc:
        out["adapter_error"] = str(exc)
    return out


def _case_status(solver_runs: list[dict[str, Any]], verifier_runs: list[dict[str, Any]], deterministic: str) -> str:
    for run in solver_runs:
        if run.get("adapter_error"):
            return "INVALID"
        if (run.get("result") or {}).get("status") == "INVALID":
            return "INVALID"
        if run.get("process", {}).get("process_status") == "MEMORY_ERROR":
            return "INCOMPLETE"
        if run.get("process", {}).get("process_status") != "OK":
            return "INCOMPLETE"
        if (run.get("result") or {}).get("status") != "COMPLETE_CANDIDATE" and (run.get("result") or {}).get("status") != "COMPLETE_INFEASIBLE":
            return "INCOMPLETE"
    for run in verifier_runs:
        if run.get("status") == "NOT RUN":
            return "INCOMPLETE"
        if run.get("adapter_error"):
            return "INVALID"
        status = (run.get("result") or {}).get("status")
        if status == "INVALID":
            return "INVALID"
        if run.get("process", {}).get("process_status") != "OK" or status != "VERIFIED":
            return "INCOMPLETE"
    if deterministic == "FAIL":
        return "INCOMPLETE"
    return "VERIFIED"


def run_case(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    summary: dict[str, Any] = {
        "schema": "p3-benchmark-run/1", "case": args.case,
        "python_mode": args.python_mode, "seconds_cap": args.seconds,
        "address_space_cap_mib": args.memory_mib, "work_cap": args.work_cap,
        "entry_cap": args.entry_cap, "operational_status": "INCOMPLETE",
        "status": "NOT RUN", "solver_runs": [], "verifier_runs": [],
        "deterministic_replay_status": "NOT RUN", "restartability_status": "NOT RUN",
    }
    try:
        manifest = load_manifest(args.manifest)
        if args.case not in manifest:
            raise HarnessError("case is not present in fixture manifest")
        row = manifest[args.case]
        input_path = args.input_dir / f"{args.case}.json"
        if not input_path.is_file():
            summary["not_run_reason"] = "raw input file unavailable"
            return summary
        raw = input_path.read_bytes()
        actual_hash = sha256(raw)
        summary["input_sha256"] = actual_hash
        summary["input_bytes"] = len(raw)
        if actual_hash != row["input_sha256"]:
            raise HarnessError("raw input SHA-256 does not match committed fixture manifest")
        data = validate_raw_input(raw)
        summary["input_dimensions"] = {
            "alphabet": len(data["alphabet"]), "positives": len(data["positive"]),
            "negatives": len(data["negative"]),
            "occurrences": sum(map(len, data["positive"] + data["negative"])),
            "max_word_length": max(map(len, data["positive"] + data["negative"]), default=0),
        }
        if not args.config.is_file():
            summary["not_run_reason"] = "producer/verifier adapter config unavailable"
            return summary
        config = load_config(args.config)
    except (HarnessError, OSError) as exc:
        summary["status"] = "INVALID"
        summary["input_error"] = str(exc)
        return summary

    # Copy only raw input into the run workspace. Evaluation directory is never read or passed.
    isolated_input = output / "input.json"
    isolated_input.write_bytes(raw)
    config_hash = sha256(args.config.read_bytes())
    summary["adapter_config_sha256"] = config_hash
    summary["host"] = platform.platform()
    summary["python"] = sys.version
    summary["python_hash_seed"] = 0
    summary["evaluation_references_read"] = False
    summary["solver_commands_receive_only"] = ["input", "certificate", "checkpoint", "result", "work_cap", "entry_cap", "seconds", "memory_mib"]

    for i in range(args.repeat):
        run_dir = output / f"solver-{i+1}"
        solver = _solver_once(
            config, isolated_input, run_dir, work_cap=args.work_cap, entry_cap=args.entry_cap,
            seconds=args.seconds, memory_mib=args.memory_mib, python_mode=args.python_mode,
        )
        summary["solver_runs"].append(solver)
        if (solver.get("result") or {}).get("status") in ("COMPLETE_CANDIDATE", "COMPLETE_INFEASIBLE") and not solver.get("adapter_error"):
            verify_dir = output / f"verifier-{i+1}"
            verifier = _verify_once(
                config, isolated_input, run_dir / "certificate.json", verify_dir,
                work_cap=args.work_cap, entry_cap=args.entry_cap, seconds=args.seconds,
                memory_mib=args.memory_mib, python_mode=args.python_mode,
            )
            summary["verifier_runs"].append(verifier)
        else:
            summary["verifier_runs"].append({"status": "NOT RUN", "reason": "solver did not emit a complete certificate"})

    cert_hashes = [r.get("certificate_sha256") for r in summary["solver_runs"]]
    run_signatures = [(r.get("certificate_sha256"), (r.get("result") or {}).get("status"), (r.get("result") or {}).get("counters")) for r in summary["solver_runs"]]
    if args.repeat >= 2 and all(cert_hashes) and len(set(map(repr, run_signatures))) == 1:
        summary["deterministic_replay_status"] = "PASS"
    elif args.repeat >= 2 and all(cert_hashes):
        summary["deterministic_replay_status"] = "FAIL"
    else:
        summary["deterministic_replay_status"] = "NOT RUN"

    if args.restart_probe:
        solver_spec = config["solver"]
        if not solver_spec.get("resume_flag"):
            summary["restartability_status"] = "NOT RUN"
            summary["restartability_reason"] = "adapter does not declare a resume flag"
        else:
            restart_dir = output / "restart-initial"
            initial_cap = min(args.restart_work_cap, args.work_cap)
            initial = _solver_once(
                config, isolated_input, restart_dir, work_cap=initial_cap, entry_cap=args.entry_cap,
                seconds=args.seconds, memory_mib=args.memory_mib, python_mode=args.python_mode,
            )
            summary["restart_initial"] = initial
            if (initial.get("result") or {}).get("status") in ("COMPLETE_CANDIDATE", "COMPLETE_INFEASIBLE"):
                summary["restartability_status"] = "NOT NEEDED (completed before restart cap)"
            elif ((initial.get("result") or {}).get("status") == "INCOMPLETE" and
                  initial.get("checkpoint_exists")):
                resumed = _solver_once(
                    config, isolated_input, output / "restart-resumed", work_cap=args.work_cap,
                    entry_cap=args.entry_cap, seconds=args.seconds, memory_mib=args.memory_mib,
                    python_mode=args.python_mode, resume=True,
                    checkpoint=restart_dir / "checkpoint.json",
                )
                summary["restart_resumed"] = resumed
                direct_hash = cert_hashes[0] if cert_hashes else None
                if ((resumed.get("result") or {}).get("status") in ("COMPLETE_CANDIDATE", "COMPLETE_INFEASIBLE") and
                    resumed.get("certificate_sha256") and resumed.get("certificate_sha256") == direct_hash):
                    summary["restartability_status"] = "PASS"
                else:
                    summary["restartability_status"] = "FAIL"
            else:
                summary["restartability_status"] = "FAIL"

    summary["status"] = _case_status(
        summary["solver_runs"],
        summary["verifier_runs"],
        summary["deterministic_replay_status"],
    )
    summary["solver_elapsed_seconds"] = sum(r.get("process", {}).get("wall_seconds", 0.0) for r in summary["solver_runs"])
    summary["verifier_elapsed_seconds"] = sum(r.get("process", {}).get("wall_seconds", 0.0) for r in summary["verifier_runs"] if r.get("process"))
    summary["solver_peak_rss_kib_max"] = max((r.get("process", {}).get("peak_rss_kib") or 0 for r in summary["solver_runs"]), default=0) or None
    summary["verifier_peak_rss_kib_max"] = max((r.get("process", {}).get("peak_rss_kib") or 0 for r in summary["verifier_runs"] if r.get("process")), default=0) or None
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=False)
    parser.add_argument("--input-dir", type=Path, required=False)
    parser.add_argument("--config", type=Path, required=False)
    parser.add_argument("--case")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--python-mode", choices=("normal", "optimized"), default="normal")
    parser.add_argument("--seconds", type=float, default=30.0)
    parser.add_argument("--memory-mib", type=int, default=1536)
    parser.add_argument("--work-cap", type=int, default=10_000_000)
    parser.add_argument("--entry-cap", type=int, default=2_000_000)
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--restart-probe", action="store_true")
    parser.add_argument("--restart-work-cap", type=int, default=100)
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return _worker(args.worker)
    required = (args.manifest, args.input_dir, args.config, args.case, args.output)
    if any(x is None for x in required):
        parser.error("--manifest, --input-dir, --config, --case and --output are required")
    if (not 0 < args.seconds < float("inf") or args.memory_mib <= 0 or
        args.work_cap <= 0 or args.entry_cap <= 0 or args.repeat <= 0 or args.restart_work_cap <= 0):
        parser.error("time, memory, work, entry and repeat caps must be positive")
    summary = run_case(args)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["status"] in ("VERIFIED", "NOT RUN") else 1


if __name__ == "__main__":
    raise SystemExit(main())
