#!/usr/bin/env python3
"""Read-only closure audit and report builder for the frozen C007 timing V2 run."""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "audit"
EVIDENCE = ROOT / "evidence"
TIMING = AUDIT / "timing_v2"
MANIFEST_PATH = TIMING / "input_manifest_v2.json"
LEDGER_PATH = TIMING / "run_ledger_v1.jsonl"
SUMMARY_PATH = TIMING / "suite_summary_v1.json"
GO_PATH = ROOT / "coordination" / "PERFORMANCE_GO_V2.json"
CAPTURE_PATH = EVIDENCE / "capture.py"
RUNNER_PATH = AUDIT / "run_v4_timing_suite_v2.py"
PER_RUN_VALIDATOR = AUDIT / "validate_v4_timing_capture_v2.py"
REPORT_JSON = TIMING / "final_audit_v1.json"
REPORT_MD = TIMING / "TIMING_REPORT_FA.md"

EXPECTED = {
    "go": "d7b51ff312396599255c0b0ca0dc69d720d7567e6769b2e3d20b23351d75ded6",
    "manifest": "e07b0a15559becc5b13a44a5baee978b7ccefb86f06a0a4034aaa668b4625737",
    "proposal": "fcf908fd7b32d445d256b3cd75d20be970001c86a4c1a6a3bf75e9cf0b6b3f89",
    "provider": "c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff",
    "cli": "46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879",
    "wrapper": "d4d1644fa3144c68c626fc8daff818e9500a89453a21871df45ffb3e7b7232de",
    "protocol": "74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd",
    "readiness": "cff6e5e5156d1c8abe8069cde7182195742762a387817ea465ccdb66adbe5ef9",
    "capture": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
    "per_run_validator": "b85467c83b28752286711f653c079187ff1163bc70810c9adb04548d4579668e",
    "replay_helper": "f49e4822ed1f6c50a603024c42989792e2deb2b0669d3bf3a82858edbb61e4e6",
    "c006": "e83c8d13e8eac248415160f6d29fb3309f19b5d447c932e00b69e24e7cb60792",
    "c005": "9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d",
    "corpus": "906152be7d6830fac80b722da24873195687ca257650b30a02ec8ace2025c39b",
}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def expected_schedule() -> list[dict[str, object]]:
    pairs = (
        ("c007_gen_m04_013", (("adaptive", "reference"), ("reference", "adaptive"), ("adaptive", "reference"))),
        ("ctrl_empty_must_link_unique_3", (("reference", "adaptive"), ("adaptive", "reference"), ("reference", "adaptive"))),
        ("c007_gen_m08_000", (("adaptive", "reference"), ("reference", "adaptive"), ("adaptive", "reference"))),
    )
    rows = []
    for case_id, repetitions in pairs:
        for repetition, modes in enumerate(repetitions, start=1):
            for mode in modes:
                rows.append({"case_id": case_id, "repetition": repetition, "mode": mode})
    return rows


def audit_source_snapshots(attempt_dir: Path) -> dict[str, dict[str, str]]:
    manifest = read_json(attempt_dir / "manifest.json")
    require(manifest.get("attempt_id") == attempt_dir.name, f"manifest attempt id mismatch: {attempt_dir.name}")
    entries: dict[str, dict[str, str]] = {}
    for entry in manifest.get("sources", []):
        path = str(Path(entry["path"]).resolve())
        require(path not in entries, f"duplicate source path in {attempt_dir.name}: {path}")
        blob = EVIDENCE / entry["snapshot"]
        require(blob.is_file(), f"missing snapshot blob in {attempt_dir.name}: {entry['snapshot']}")
        require(sha_file(blob) == entry["sha256"], f"snapshot blob hash mismatch in {attempt_dir.name}: {path}")
        require(str(blob.stat().st_size) == entry["bytes"], f"snapshot byte count mismatch in {attempt_dir.name}: {path}")
        entries[path] = entry
    return entries


def metric_median(records: list[dict], key: str):
    values = [r["internal_metrics"][key] for r in records if isinstance(r.get("internal_metrics"), dict) and isinstance(r["internal_metrics"].get(key), (int, float))]
    return statistics.median(values) if values else None


def main() -> int:
    manifest = read_json(MANIFEST_PATH)
    summary = read_json(SUMMARY_PATH)
    go = read_json(GO_PATH)
    ledger_bytes = LEDGER_PATH.read_bytes()
    ledger = [json.loads(line) for line in ledger_bytes.decode("utf-8").splitlines() if line.strip()]

    require(sha_file(GO_PATH) == EXPECTED["go"], "GO record hash mismatch")
    require(sha_file(MANIFEST_PATH) == EXPECTED["manifest"], "input manifest hash mismatch")
    require(sha_file(AUDIT / "timing_v2" / "PROPOSAL_V2.md") == EXPECTED["proposal"], "proposal hash mismatch")
    require(manifest.get("status") == "frozen_inputs_prepared_no_timing_run", "input manifest status mismatch")
    require(go.get("decision") == "GO" and go.get("source_changes") == "not authorized", "GO record does not match approved scope")
    require(summary.get("status") == "complete", "suite summary is not complete")
    require(summary.get("proposal_sha256") == EXPECTED["proposal"], "summary proposal anchor mismatch")
    require(summary.get("input_manifest_sha256") == EXPECTED["manifest"], "summary input anchor mismatch")
    require(summary.get("master_go_sha256") == EXPECTED["go"], "summary GO anchor mismatch")
    require(summary.get("run_ledger_sha256") == sha_bytes(ledger_bytes), "summary ledger hash mismatch")
    require(summary.get("provider_jobs_run") == 18 and len(ledger) == 18, "expected exactly 18 provider jobs")
    require(summary.get("execution_rows") == ledger, "summary rows differ from durable JSONL ledger")
    expected = expected_schedule()
    require(len(expected) == len(ledger), "frozen schedule size mismatch")

    fixed_sources = {
        ROOT / "implementation" / "finest_solver_v4.py": EXPECTED["provider"],
        ROOT / "implementation" / "finest_cli_v2.py": EXPECTED["cli"],
        ROOT / "solver.py": EXPECTED["wrapper"],
        ROOT / "implementation" / "PROTOCOL_V5.md": EXPECTED["protocol"],
        ROOT / "implementation" / "READINESS_V4.json": EXPECTED["readiness"],
        CAPTURE_PATH: EXPECTED["capture"],
        PER_RUN_VALIDATOR: EXPECTED["per_run_validator"],
        AUDIT / "validate_provider_gate_v3.py": EXPECTED["replay_helper"],
        ROOT.parents[1] / "2026-11-01" / "partition_identifiability_v6" / "implementation" / "solver_v5.py": EXPECTED["c006"],
        ROOT.parents[1] / "2026-10-31" / "partition_coverage_v5" / "general" / "known_k_qexact_v2.py": EXPECTED["c005"],
        MANIFEST_PATH: EXPECTED["manifest"],
        AUDIT / "timing_v2" / "PROPOSAL_V2.md": EXPECTED["proposal"],
        GO_PATH: EXPECTED["go"],
        AUDIT / "corpus_v1" / "all_valid_inputs.jsonl": EXPECTED["corpus"],
    }
    for path, digest in fixed_sources.items():
        require(path.is_file() and sha_file(path) == digest, f"frozen source drift: {path}")

    time_by_mode = defaultdict(float)
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    reports = []
    validator_attempts = set()
    all_snapshot_count = 0
    runner_hashes = set()
    for index, (row, schedule_row) in enumerate(zip(ledger, expected), start=1):
        for field, value in schedule_row.items():
            require(row.get(field) == value, f"schedule mismatch at row {index}: {field}")
        require(row.get("schedule_index") == index, f"schedule index mismatch at row {index}")
        require(row.get("validation_status") == "accepted", f"validation not accepted at row {index}")
        require(row.get("scientific_status") == "accepted_complete_result", f"scientific status not complete at row {index}")
        require(row.get("provider_execution_status") == "success" and row.get("provider_exit_code") == 0, f"provider execution failure at row {index}")
        require(row.get("provider_child_reaped") is True, f"provider child not reaped at row {index}")
        attempt_id = row["provider_attempt_id"]
        provider_dir = EVIDENCE / "attempts" / attempt_id
        provider_manifest = read_json(provider_dir / "manifest.json")
        provider_result = read_json(provider_dir / "result.json")
        provider_sources = audit_source_snapshots(provider_dir)
        all_snapshot_count += len(provider_sources)
        require(provider_result.get("attempt_id") == attempt_id and provider_manifest.get("attempt_id") == attempt_id, f"provider attempt id mismatch: {attempt_id}")
        require(provider_result.get("execution_status") == "success" and provider_result.get("exit_code") == 0 and provider_result.get("child_reaped") is True, f"provider capture metadata mismatch: {attempt_id}")
        require(provider_result.get("subprocess_seconds") == row["provider_subprocess_seconds"], f"provider time mismatch: {attempt_id}")
        require(provider_result.get("stdout_bytes") == row["provider_stdout_bytes"], f"provider stdout length mismatch: {attempt_id}")
        stdout = (provider_dir / "stdout.bin").read_bytes()
        stderr = (provider_dir / "stderr.bin").read_bytes()
        require(sha_bytes(stdout) == provider_result.get("stdout_sha256") == row["provider_stdout_sha256"], f"provider stdout hash mismatch: {attempt_id}")
        require(sha_bytes(stderr) == provider_result.get("stderr_sha256"), f"provider stderr hash mismatch: {attempt_id}")
        output = json.loads(stdout.decode("utf-8").strip())
        case_info = manifest["cases"][row["case_id"]]
        require(output.get("status") == case_info["all_k_expected_status"], f"provider decision mismatch: {attempt_id}")
        require(provider_manifest.get("timeout_seconds") == 30.0, f"hard timeout mismatch: {attempt_id}")
        argv = provider_manifest.get("command_argv", [])
        require(any(a.endswith("solver.py") for a in argv), f"root wrapper not used: {attempt_id}")
        require(any(a.endswith(Path(case_info["path"]).name) for a in argv), f"wrong input in provider command: {attempt_id}")
        require("--mode" in argv and row["mode"] in argv and "--seconds" in argv and "28" in argv, f"provider command parameters mismatch: {attempt_id}")

        required = dict(fixed_sources)
        required[TIMING / case_info["path"]] = case_info["sha256"]
        required[AUDIT / case_info["rgs_oracle_path"]] = case_info["rgs_oracle_sha256"]
        required[AUDIT / case_info["independent_oracle_path"]] = case_info["independent_oracle_sha256"]
        for path, digest in required.items():
            entry = provider_sources.get(str(path.resolve()))
            require(entry is not None and entry["sha256"] == digest, f"required frozen source missing from provider capture {attempt_id}: {path}")
        runner_entry = provider_sources.get(str(RUNNER_PATH.resolve()))
        require(runner_entry is not None, f"runner source missing from provider capture: {attempt_id}")
        runner_hashes.add(runner_entry["sha256"])

        report_path = TIMING / "validations" / f"{attempt_id}.json"
        report = read_json(report_path)
        require(sha_file(report_path) == row["validation_report_sha256"], f"validator report hash mismatch: {attempt_id}")
        require(report.get("status") == "accepted" and report.get("scientific_status") == "accepted_complete_result", f"per-run independent validation failed: {attempt_id}")
        require(report.get("attempt_id") == attempt_id and report.get("case_id") == row["case_id"] and report.get("mode") == row["mode"], f"per-run validation identity mismatch: {attempt_id}")
        require(report.get("stdout_sha256") == provider_result.get("stdout_sha256"), f"per-run validation output anchor mismatch: {attempt_id}")
        validator_id = row["validator_attempt_id"]
        require(validator_id not in validator_attempts, f"duplicate validator capture: {validator_id}")
        validator_attempts.add(validator_id)
        validator_dir = EVIDENCE / "attempts" / validator_id
        validator_manifest = read_json(validator_dir / "manifest.json")
        validator_result = read_json(validator_dir / "result.json")
        validator_sources = audit_source_snapshots(validator_dir)
        all_snapshot_count += len(validator_sources)
        require(validator_result.get("execution_status") == "success" and validator_result.get("exit_code") == 0 and validator_result.get("child_reaped") is True, f"validator capture failed: {validator_id}")
        validator_out = json.loads((validator_dir / "stdout.bin").read_text(encoding="utf-8").strip())
        require(validator_out == report, f"validator stdout differs from durable report: {attempt_id}")
        for path in (provider_dir / "manifest.json", provider_dir / "result.json", provider_dir / "stdout.bin", provider_dir / "stderr.bin"):
            entry = validator_sources.get(str(path.resolve()))
            require(entry is not None and entry["sha256"] == sha_file(path), f"validator did not capture provider evidence: {attempt_id} {path.name}")

        row["stderr_bytes"] = len(stderr)
        groups[(row["case_id"], row["mode"])].append(row)
        time_by_mode[row["mode"]] += float(row["provider_subprocess_seconds"])
        reports.append({"attempt_id": attempt_id, "sha256": sha_file(report_path), "path": str(report_path.relative_to(ROOT))})

    require(len(runner_hashes) == 1, "captured runner source changed within timing suite")
    require(all(time_by_mode[mode] <= 300.0 for mode in ("adaptive", "reference")), "method subprocess budget exceeded")
    require(abs(time_by_mode["adaptive"] - summary["subprocess_seconds_by_mode"]["adaptive"]) < 1e-9, "adaptive budget sum mismatch")
    require(abs(time_by_mode["reference"] - summary["subprocess_seconds_by_mode"]["reference"]) < 1e-9, "reference budget sum mismatch")
    require(len(validator_attempts) == 18, "expected 18 distinct validator captures")

    statistics_rows = []
    for case_id in manifest["cases"]:
        for mode in ("adaptive", "reference"):
            items = groups[(case_id, mode)]
            require(len(items) == 3, f"expected three complete repetitions: {case_id} {mode}")
            times = [float(item["provider_subprocess_seconds"]) for item in items]
            sizes = [int(item["provider_stdout_bytes"]) for item in items]
            statistics_rows.append({
                "case_id": case_id,
                "mode": mode,
                "repetitions": 3,
                "subprocess_seconds": {"median": statistics.median(times), "min": min(times), "max": max(times), "raw": times},
                "stdout_bytes": {"median": statistics.median(sizes), "min": min(sizes), "max": max(sizes), "raw": sizes},
                "median_oracle_calls": metric_median(items, "oracle_calls"),
                "median_binary_cuts_checked": metric_median(items, "binary_cuts_checked"),
                "median_successful_refinements": metric_median(items, "successful_refinements"),
                "median_swap_pair_comparisons": metric_median(items, "swap_pair_comparisons"),
            })

    report = {
        "schema_version": 1,
        "status": "accepted",
        "audit_scope": "source/evidence closure, frozen schedule, capture/result/report hashes, and summary statistics; semantic certificates were independently replayed by the per-run V2 validator",
        "provider_jobs": 18,
        "independent_validation_reports_accepted": 18,
        "complete_uncensored_provider_results": 18,
        "provider_execution_failures": 0,
        "output_mismatches": 0,
        "provider_subprocess_seconds_by_mode": dict(time_by_mode),
        "provider_budgets_seconds": {"per_mode_limit": 300.0, "adaptive_used": time_by_mode["adaptive"], "reference_used": time_by_mode["reference"]},
        "source_snapshot_entries_verified": all_snapshot_count,
        "captured_runner_sha256": next(iter(runner_hashes)),
        "suite_summary_sha256": sha_file(SUMMARY_PATH),
        "run_ledger_sha256": sha_bytes(ledger_bytes),
        "per_run_reports": reports,
        "cell_statistics": statistics_rows,
        "timing_interpretation_limit": "Fresh subprocess wall time includes Python startup, input parsing, solving, and output serialization. Adaptive and reference return proofs of different sizes; these timings do not isolate a search stage or establish general superiority.",
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    REPORT_MD.write_text(render_markdown(report, ledger), encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "jobs": report["provider_jobs"], "reports": report["independent_validation_reports_accepted"], "time_by_mode": dict(time_by_mode), "json": str(REPORT_JSON), "markdown": str(REPORT_MD)}, ensure_ascii=False, sort_keys=True))
    return 0


def render_markdown(report: dict, ledger: list[dict]) -> str:
    stats = {(item["case_id"], item["mode"]): item for item in report["cell_statistics"]}
    labels = {"adaptive": "تطبیقی", "reference": "مرجع"}
    case_labels = {
        "c007_gen_m04_013": "m=4؛ چند بیشینهٔ ماکسیمال / مسیر fallback",
        "ctrl_empty_must_link_unique_3": "m=6؛ سه بلوک یکتای نهایی، بدون یال اجباری",
        "c007_gen_m08_000": "m=8؛ مسیر سریع swap-only",
    }
    lines = [
        "# گزارش زمان‌سنجی C007، نسخهٔ ۲",
        "",
        "## نتیجهٔ ممیزی",
        "",
        "هر ۱۸ اجرای مجاز (۳ ورودی × ۲ روش × ۳ تکرار) با موفقیت کامل شدند. خروجی هر اجرا پیش از اجرای بعدی با اعتبارسنج مستقل نسخهٔ ۲ بررسی شد؛ ۱۸ از ۱۸ گزارش پذیرفته شدند. در ممیزی نهایی، ترتیب برنامه‌ریزی‌شده، هش‌های ورودی و کد، snapshotهای منبع، خروجی‌های خام و دفتر اجرا دوباره بررسی شدند. هیچ خروجی ناقص، خطای اجرا یا اختلافی ثبت نشد.",
        "",
        "## خلاصهٔ هر ورودی و روش",
        "",
        "| ورودی | روش | زمان فرایند تازه، میانه [کمینه، بیشینه] (ثانیه) | stdout میانه (بایت) | میانهٔ فراخوانی اوراکل | میانهٔ برش بررسی‌شده |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for case_id in case_labels:
        for mode in ("adaptive", "reference"):
            item = stats[(case_id, mode)]
            t = item["subprocess_seconds"]
            oracle = item["median_oracle_calls"]
            cuts = item["median_binary_cuts_checked"]
            lines.append(f"| {case_labels[case_id]} | {labels[mode]} | {t['median']:.6f} [{t['min']:.6f}, {t['max']:.6f}] | {item['stdout_bytes']['median']:.0f} | {oracle if oracle is not None else '—'} | {cuts if cuts is not None else '—'} |")
    lines.extend([
        "",
        "زمان اصلی، مدت زیر‌فرایند ثبت‌شده توسط capture است؛ این زمان راه‌اندازی Python، خواندن و تجزیهٔ ورودی، حل و سریال‌سازی خروجی را دربر می‌گیرد. اندازهٔ خروجی دو روش یکسان نیست و برای برخی ورودی‌ها تفاوت زیادی دارد، پس این مقایسه زمان رسیدن به تصمیم دارای گواهی روی این سه نمونه را می‌سنجد؛ زمان خالص جست‌وجو یا برتری کلی روش‌ها را اثبات نمی‌کند. معیار حافظه در این نوبت اندازه‌گیری نشد.",
        "",
        "## همهٔ اجراهای خام",
        "",
        "| # | ورودی | تکرار | روش | زمان (ثانیه) | stdout (بایت) | شناسهٔ capture | SHA گزارش اعتبارسنج |",
        "|---:|---|---:|---|---:|---:|---|---|",
    ])
    for row in ledger:
        lines.append(f"| {row['schedule_index']} | {row['case_id']} | {row['repetition']} | {labels[row['mode']]} | {row['provider_subprocess_seconds']:.6f} | {row['provider_stdout_bytes']} | `{row['provider_attempt_id']}` | `{row['validation_report_sha256']}` |")
    lines.extend([
        "",
        "## بازتولید و محدودیت‌ها",
        "",
        f"- مجوز ثابت: `PERFORMANCE_GO_V2.json`، SHA-256 `{EXPECTED['go']}`.",
        f"- طرح و ورودی‌ها: `PROPOSAL_V2.md`، SHA-256 `{EXPECTED['proposal']}`؛ manifest ورودی SHA-256 `{EXPECTED['manifest']}`.",
        f"- دفتر کامل اجراها: `run_ledger_v1.jsonl`، SHA-256 `{report['run_ledger_sha256']}`.",
        f"- خلاصهٔ اجرا: `suite_summary_v1.json`، SHA-256 `{report['suite_summary_sha256']}`.",
        f"- ممیزی نهایی ساختاری: `final_audit_v1.json`؛ {report['source_snapshot_entries_verified']} snapshot منبع بررسی شد.",
        f"- بودجهٔ مصرف‌شده: تطبیقی {report['provider_budgets_seconds']['adaptive_used']:.3f}s و مرجع {report['provider_budgets_seconds']['reference_used']:.3f}s، از سقف 300s برای هر روش.",
        "- گواهی‌های معنایی هر خروجی با اعتبارسنج مستقل V2 بررسی شده‌اند؛ این گزارش نهایی زنجیرهٔ ثبت، زمان‌ها و هش‌ها را می‌بندد.",
        "",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
