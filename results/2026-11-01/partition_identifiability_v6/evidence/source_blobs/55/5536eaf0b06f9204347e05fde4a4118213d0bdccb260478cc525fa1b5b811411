"""Audit exactly the six frozen C006 timing captures and summarize them."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit"
BENCH = AUDIT / "benchmark_v1"
ATTEMPTS = ROOT / "evidence" / "attempts"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def load_auditor():
    path = AUDIT / "gate_solver_v5_v6.py"
    spec = importlib.util.spec_from_file_location("c006_frozen_independent_auditor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def grammar_accepts(grammar, word):
    kind = grammar.get("kind")
    if kind == "fixed_prefix_center_leaf_pairs_star":
        prefix, center, leaves = grammar["prefix"], grammar["center"], set(grammar["leaves"])
        if not word.startswith(prefix):
            return False
        tail = word[len(prefix):]
        return len(tail) % 2 == 0 and all(
            tail[i] == center and tail[i + 1] in leaves for i in range(0, len(tail), 2))
    if kind == "finite_words_union_unary_tail":
        return word in set(grammar["finite_words"]) or (
            len(word) >= grammar["tail_min_length"] and
            all(symbol == grammar["tail_symbol"] for symbol in word))
    return False


def canonical_json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def number_summary(values):
    if not values:
        return None
    return {"median": statistics.median(values), "min": min(values), "max": max(values)}


def main():
    batch_path = BENCH / "batch_v1.json"
    batch = json.loads(batch_path.read_text(encoding="utf-8"))
    corpus_manifest_path = BENCH / "manifest.json"
    corpus_manifest = json.loads(corpus_manifest_path.read_text(encoding="utf-8"))
    truths = {row["case_id"]: row for row in read_jsonl(BENCH / "truth_sidecars.jsonl")}
    expected = {row["case_id"]: row for row in read_jsonl(BENCH / "expected_obstructions.jsonl")}
    auditor = load_auditor()
    all_attempts = {}
    for attempt_dir in ATTEMPTS.iterdir():
        if not attempt_dir.is_dir():
            continue
        manifest_path = attempt_dir / "manifest.json"
        if not manifest_path.exists():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        label = manifest.get("label", "")
        if label.startswith("C006_BENCH_"):
            all_attempts.setdefault(label, []).append(attempt_dir)

    planned_labels = [job["label"] for job in batch["order"]]
    unplanned = sorted(set(all_attempts) - set(planned_labels))
    rows, errors = [], []
    for job in batch["order"]:
        label = job["label"]
        found = all_attempts.get(label, [])
        row = {"label": label, "rep": job["rep"], "cell": job["cell"],
               "capture_status": "missing", "independent_validation": "not_run"}
        if len(found) != 1:
            row["error"] = f"expected exactly one immutable attempt; found {len(found)}"
            errors.append({"label": label, "error": row["error"]})
            rows.append(row)
            continue
        attempt_dir = found[0]
        row["attempt_id"] = attempt_dir.name
        try:
            capture = json.loads((attempt_dir / "result.json").read_text(encoding="utf-8"))
            manifest = json.loads((attempt_dir / "manifest.json").read_text(encoding="utf-8"))
            row.update({"capture_status": capture.get("execution_status"),
                        "exit_code": capture.get("exit_code"),
                        "child_pid": capture.get("child_pid"),
                        "child_reaped": capture.get("child_reaped"),
                        "subprocess_seconds": capture.get("subprocess_seconds"),
                        "capture_duration_seconds": capture.get("duration_seconds"),
                        "stdout_bytes": capture.get("stdout_bytes"),
                        "stderr_bytes": capture.get("stderr_bytes"),
                        "stdout_sha256": capture.get("stdout_sha256"),
                        "stderr_sha256": capture.get("stderr_sha256")})
            raw = (attempt_dir / "stdout.bin").read_bytes()
            err_raw = (attempt_dir / "stderr.bin").read_bytes()
            if sha(raw) != capture.get("stdout_sha256") or len(raw) != capture.get("stdout_bytes"):
                raise ValueError("captured stdout hash/size mismatch")
            if sha(err_raw) != capture.get("stderr_sha256") or len(err_raw) != capture.get("stderr_bytes"):
                raise ValueError("captured stderr hash/size mismatch")
            if capture.get("execution_status") != "success" or capture.get("exit_code") != 0:
                raise ValueError("provider process did not complete successfully; no rerun permitted")
            if capture.get("child_reaped") is not True:
                raise ValueError("captured provider child not reaped")
            argv = manifest.get("command_argv", [])
            expected_input = str((BENCH / "inputs" / job["input"]).resolve())
            if ("--all" not in argv or "--seconds" not in argv or "28" not in argv
                    or not any(Path(arg).resolve() == Path(expected_input) for arg in argv if arg.lower().endswith(".json"))
                    or not any(Path(arg).name == "solver.py" for arg in argv)):
                raise ValueError(f"command does not match frozen CLI batch: {argv}")
            source_hashes = {entry["path"].lower(): entry["sha256"] for entry in manifest.get("sources", [])}
            expected_source_paths = {
                str((ROOT / "solver.py").resolve()).lower(): batch["root_wrapper_sha256"],
                str((ROOT / "implementation" / "cli_v4.py").resolve()).lower(): batch["cli_sha256"],
                str((ROOT / "implementation" / "solver_v5.py").resolve()).lower(): batch["provider_sha256"],
                str((BENCH / "inputs" / job["input"]).resolve()).lower(): job["input_sha256"],
                str((ROOT / "coordination" / "PERFORMANCE_GO.json").resolve()).lower(): batch["authorization"]["sha256"],
                str(batch_path.resolve()).lower(): sha(batch_path.read_bytes()),
            }
            for path, digest in expected_source_paths.items():
                if source_hashes.get(path) != digest:
                    raise ValueError(f"captured source anchor mismatch: {path}")
            input_path = BENCH / "inputs" / job["input"]
            data = json.loads(input_path.read_text(encoding="utf-8"))
            if sha(input_path.read_bytes()) != job["input_sha256"]:
                raise ValueError("input file differs from frozen hash")
            if set(data) != {"alphabet", "positive", "negative"}:
                raise ValueError("provider input contains fields outside the frozen contract")
            truth = truths[job["cell"]]
            if not all(grammar_accepts(truth["grammar"], word) for word in data["positive"]):
                raise ValueError("frozen target grammar does not accept every positive")
            if not all(not grammar_accepts(truth["grammar"], word) for word in data["negative"]):
                raise ValueError("frozen target grammar accepts a negative")
            if len(raw.splitlines()) != 1:
                raise ValueError("CLI stdout is not exactly one JSON result")
            result = json.loads(raw.decode("utf-8"))
            if (result.get("status") != "not_decomposable" or result.get("complete") is not True
                    or result.get("decision_complete") is not True or result.get("solutions") != []):
                raise ValueError(f"unexpected provider result status/shape: {result.get('status')}")
            valid, why, cut_count = auditor.replay_certificate_independently(data, result.get("certificate"))
            if not valid:
                raise ValueError(f"independent certificate replay failed: {why}")
            cert = result["certificate"]
            exp = expected[job["cell"]]
            if job["cell"] == "large_connected_m64":
                actual_edges = [sorted(edge["symbols"]) for edge in cert["must_link_edges"]]
                if (cert.get("obstruction") != "connected_must_link_graph"
                        or sorted(actual_edges) != sorted(exp["expected_edge_pairs"])
                        or len(actual_edges) != exp["expected_edge_count"]
                        or len(cert.get("components", [])) != 1 or cut_count != 0):
                    raise ValueError("large connected certificate differs from frozen edge/certificate contract")
            else:
                wanted = exp["expected_cut_rejections"]
                actual = cert.get("cut_rejections", [])
                if (cert.get("obstruction") != "complete_cut_collision_cover"
                        or cert.get("must_link_edges") != [] or cut_count != len(wanted)
                        or len(actual) != len(wanted)):
                    raise ValueError("small full-cover certificate differs from frozen contract")
                if [x.get("canonical_left_atom_mask") for x in actual] != [x["canonical_left_atom_mask"] for x in wanted]:
                    raise ValueError("small full-cover mask sequence differs from frozen canonical order")
            metrics = result.get("metrics", {})
            provider_seconds = metrics.get("provider_seconds")
            if not isinstance(provider_seconds, (int, float)) or provider_seconds < 0:
                raise ValueError("missing/invalid provider timing")
            cert_bytes = len(canonical_json_bytes(cert))
            row.update({"independent_validation": "passed", "status": result["status"],
                        "provider_seconds": provider_seconds,
                        "must_link_edges": metrics.get("must_link_edges"),
                        "contracted_components": metrics.get("contracted_components"),
                        "canonical_cuts_checked": metrics.get("canonical_cuts_checked"),
                        "certificate_kind": cert.get("obstruction"),
                        "certificate_bytes_canonical_json": cert_bytes,
                        "certificate_edge_witness_count": len(cert.get("must_link_edges", [])),
                        "certificate_cut_collision_count": len(cert.get("cut_rejections", [])),
                        "certificate_side_collision_count": 2 * len(cert.get("cut_rejections", [])),
                        "independent_cut_count": cut_count})
        except Exception as exc:
            row["independent_validation"] = "failed"
            row["error"] = repr(exc)
            errors.append({"label": label, "attempt_id": attempt_dir.name, "error": repr(exc)})
        rows.append(row)

    if unplanned:
        errors.append({"unplanned_benchmark_labels": unplanned})
    grouped = {}
    for cell in ("large_connected_m64", "small_full_cover_m4"):
        selected = [row for row in rows if row["cell"] == cell]
        grouped[cell] = {
            "planned_processes": 3,
            "captured_processes": sum(1 for row in selected if row.get("attempt_id")),
            "successful_reaped_processes": sum(1 for row in selected
                                                if row.get("capture_status") == "success" and row.get("child_reaped") is True),
            "independently_validated_processes": sum(1 for row in selected
                                                      if row.get("independent_validation") == "passed"),
            "provider_seconds": number_summary([row["provider_seconds"] for row in selected if "provider_seconds" in row]),
            "subprocess_seconds": number_summary([row["subprocess_seconds"] for row in selected if isinstance(row.get("subprocess_seconds"), (int, float))]),
            "capture_duration_seconds": number_summary([row["capture_duration_seconds"] for row in selected if isinstance(row.get("capture_duration_seconds"), (int, float))]),
            "stdout_bytes": number_summary([row["stdout_bytes"] for row in selected if isinstance(row.get("stdout_bytes"), int)]),
            "certificate_bytes_canonical_json": number_summary([row["certificate_bytes_canonical_json"] for row in selected if "certificate_bytes_canonical_json" in row]),
            "must_link_edges": number_summary([row["must_link_edges"] for row in selected if isinstance(row.get("must_link_edges"), int)]),
            "canonical_cuts_checked": number_summary([row["canonical_cuts_checked"] for row in selected if isinstance(row.get("canonical_cuts_checked"), int)]),
            "edge_witnesses": number_summary([row["certificate_edge_witness_count"] for row in selected if "certificate_edge_witness_count" in row]),
            "cut_collision_witnesses": number_summary([row["certificate_cut_collision_count"] for row in selected if "certificate_cut_collision_count" in row]),
            "side_collision_witnesses": number_summary([row["certificate_side_collision_count"] for row in selected if "certificate_side_collision_count" in row])
        }

    report = {
        "cycle": "C006",
        "scientific_status": "passed" if len(rows) == 6 and not errors and all(r.get("independent_validation") == "passed" for r in rows) else "incomplete_or_discrepancy",
        "execution_status": "success",
        "authorization_sha256": batch["authorization"]["sha256"],
        "proposal_sha256": batch["proposal_sha256"],
        "protocol_sha256": batch["protocol_sha256"],
        "corpus_manifest_sha256": batch["corpus_manifest_sha256"],
        "provider_sha256": batch["provider_sha256"],
        "cli_sha256": batch["cli_sha256"],
        "root_wrapper_sha256": batch["root_wrapper_sha256"],
        "planned_provider_processes": 6,
        "actual_captured_provider_processes": sum(1 for row in rows if row.get("attempt_id")),
        "successful_reaped_provider_processes": sum(1 for row in rows if row.get("capture_status") == "success" and row.get("child_reaped") is True),
        "independently_validated_provider_processes": sum(1 for row in rows if row.get("independent_validation") == "passed"),
        "unplanned_benchmark_labels": unplanned,
        "primary_cells": grouped,
        "jobs": rows,
        "errors": errors,
        "limitations": [
            "only two frozen cells and one solver version were measured",
            "not an old-method comparison; no speedup claim",
            "subprocess timing includes Python startup, input parsing, and full JSON output; outer capture duration includes source snapshot overhead",
            "no memory measurement",
            "the optional decomposable cell was excluded",
            "results characterize these proof paths and do not establish general scaling"
        ]
    }
    output = BENCH / "benchmark_results_v2.json"
    output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    summary = {key: value for key, value in report.items() if key not in ("jobs", "errors")}
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
