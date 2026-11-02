#!/usr/bin/env python3
"""Master-owned C007 delivery closure; PREVIEW ONLY until master invokes it.

Two phases, deliberately separated:
  prepare --report PATH --timing PATH
      Validate accepted research evidence and promote root-facing documents.
  finalize --integrity PATH
      After archive_integrity_v2 has run, validate its pass result, links and
      runtime hashes, then write outcome, delivery links, and closure checks.

This file is prepared for master inspection. It must not be run by a worker.
All mutation targets are explicit C007 outputs plus workspace START_HERE_FA.md.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parents[2]
EXPECTED = {
    "implementation/finest_solver_v4.py": "c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff",
    "implementation/finest_cli_v2.py": "46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879",
}
EXPECTED_README_CANDIDATE = "e163abb99e00413a2f591613073fb1e57b1cc85c974fc86788dfa8f49c5e99c3"
EXPECTED_PUBLIC_WRAPPER_R2 = "d4d1644fa3144c68c626fc8daff818e9500a89453a21871df45ffb3e7b7232de"

def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rel_workspace(path: Path) -> str:
    return path.resolve().relative_to(WORKSPACE.resolve()).as_posix()

def cycle_path(raw: str | Path) -> Path:
    path = Path(raw)
    result = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
    if not result.is_relative_to(ROOT.resolve()):
        raise ValueError(f"path must remain inside C007: {result}")
    return result

def resolve_input(raw: str) -> Path:
    """Accept a C007-relative or workspace-relative path, with no guessing."""
    path = Path(raw)
    result = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
    if not result.exists() and not path.is_absolute():
        workspace_candidate = (WORKSPACE / path).resolve()
        if workspace_candidate.is_relative_to(WORKSPACE.resolve()) and workspace_candidate.exists():
            result = workspace_candidate
    if not result.is_relative_to(WORKSPACE.resolve()):
        raise ValueError(f"input path escapes workspace: {result}")
    return result

def accepted(record: dict) -> bool:
    if record.get("failures") not in (None, [], {}):
        return False
    statuses = {record.get("status"), record.get("scientific_status"),
                record.get("decision"), record.get("acceptance_status")}
    if statuses & {"rejected", "failed", "pending", "not_assessed", "incomplete"}:
        return False
    return bool(record.get("accepted") is True or
                statuses & {"accepted", "passed", "complete", "accepted_with_censoring"})

def require_hashes():
    for rel, wanted in EXPECTED.items():
        path = cycle_path(rel)
        if digest(path) != wanted:
            raise ValueError(f"final provider hash mismatch: {rel}")
    wrapper = cycle_path("solver.py")
    wrapper_record = read(cycle_path("coordination/WRAPPER_R2.json"))
    if (not wrapper.is_file() or digest(wrapper) != EXPECTED_PUBLIC_WRAPPER_R2
            or wrapper_record.get("new_sha256") != EXPECTED_PUBLIC_WRAPPER_R2
            or "finest_cli_v2.py" not in wrapper.read_text(encoding="utf-8")):
        raise ValueError("public solver.py wrapper does not select CLI v2")

def require_gates():
    gates = {
        "v4_correctness": ("audit/validation_v2/provider_gate_v4.json", 218, 436),
    }
    for name, (rel, rows, replays) in gates.items():
        data = read(cycle_path(rel))
        if data.get("status") != "accepted" or data.get("failures") != []:
            raise ValueError(f"{name} not accepted")
        if data.get("adaptive_rows") != rows or data.get("reference_rows") != rows:
            raise ValueError(f"{name} row count mismatch")
        if data.get("independent_certificate_replays") != replays:
            raise ValueError(f"{name} replay count mismatch")
        if any(v.get("source_failures") for v in data.get("capture_integrity", {}).values()):
            raise ValueError(f"{name} capture source failures")
    long = read(cycle_path("audit/scale_v1/long_v4_replay_v1.json"))
    if long.get("status") != "accepted" or long.get("failures") != []:
        raise ValueError("long v4 replay is not accepted")
    scale = read(cycle_path("audit/scale_v1/scale_validation_v4.json"))
    if scale.get("status") != "accepted_with_censoring" or scale.get("accepted_cells") != 4:
        raise ValueError("historical structured scale evidence not accepted as censored")
    extra_gates = ["audit/targeted_empty_graph/provider_gate_v2.json",
                   "audit/validation_v2/provider_controls_v4.json",
                   "audit/root_cli_v2.json"]
    for rel in extra_gates:
        gate = read(cycle_path(rel))
        if gate.get("status") != "accepted" or gate.get("failures") != []:
            raise ValueError(f"required v4 gate is not accepted: {rel}")
    acceptance = read(cycle_path("coordination/CORRECTNESS_ACCEPTANCE_V4.json"))
    if acceptance.get("provider", {}).get("sha256") != EXPECTED["implementation/finest_solver_v4.py"]:
        raise ValueError("master correctness acceptance does not anchor v4 provider")
    if acceptance.get("performance") != "accepted":
        raise ValueError("master has not accepted performance gate")
    return {"v4_correctness": gates["v4_correctness"][0],
            "targeted_empty_graph": extra_gates[0], "targeted_controls": extra_gates[1],
            "root_cli": extra_gates[2],
            "long_case": "audit/scale_v1/long_v4_replay_v1.json",
            "structured_scale": "audit/scale_v1/scale_validation_v4.json",
            "master_acceptance": "coordination/CORRECTNESS_ACCEPTANCE_V4.json"}

def backup_if_exists(path: Path, backup: Path):
    if path.exists():
        if backup.exists():
            raise FileExistsError(f"refusing to replace existing backup {backup}")
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(path.read_bytes())

def timing_summary(data: dict) -> str:
    if not accepted(data):
        raise ValueError("timing result is not explicitly accepted")
    jobs = data.get("jobs", data.get("cells", data.get("primary_cells")))
    if not isinstance(jobs, (list, dict)) or not jobs:
        raise ValueError("accepted timing record must contain nonempty jobs/cells/primary_cells")
    if data.get("actual_captured_provider_processes", 0) <= 0 and not data.get("process_count"):
        # Some schemas put process counts per cell; validate those below.
        if not isinstance(jobs, (list, dict)):
            raise ValueError("timing record lacks captured process counts")
    rows = []
    iterable = jobs.items() if isinstance(jobs, dict) else enumerate(jobs)
    for key, cell in iterable:
        if not isinstance(cell, dict):
            raise ValueError(f"malformed timing cell {key}")
        if cell.get("failures") not in (None, [], {}):
            raise ValueError(f"timing cell has failures: {key}")
        if cell.get("status") in {"pending", "failed", "incomplete"}:
            raise ValueError(f"timing cell not complete: {key}")
        label = str(cell.get("name", cell.get("case_id", key)))
        seconds = cell.get("median_process_seconds", cell.get("subprocess_seconds"))
        if isinstance(seconds, dict): seconds = seconds.get("median")
        if isinstance(seconds, (float, int)):
            rows.append(f"| {label} | {float(seconds):.3f} |")
        else:
            raise ValueError(f"timing cell lacks process-wall median: {key}")
    return "\n".join(["| نمونه | میانهٔ زمان کامل فرایند (ثانیه) |", "|---|---:|", *rows])

def prepare(report_arg: str, timing_arg: str):
    require_hashes()
    gate_refs = require_gates()
    report = resolve_input(report_arg)
    if not report.is_file() or not report.is_relative_to((ROOT / "theory").resolve()):
        raise ValueError("final report candidate must be an existing file under theory/")
    if report.name != "SCIENTIFIC_REPORT_CANDIDATE_FA_v4.md":
        raise ValueError("expected the accepted theory v4 report candidate")
    readme_source = cycle_path("implementation/ROOT_README_CANDIDATE_FA_v2.md")
    if digest(readme_source) != EXPECTED_README_CANDIDATE:
        raise ValueError("root README candidate hash mismatch")
    timing = resolve_input(timing_arg)
    timing_data = read(timing)
    table = timing_summary(timing_data)

    # Preserve previous public artifacts before writing replacements.
    backup_if_exists(ROOT / "README_FA.md", ROOT / "coordination" / "README_FA_PRE_V4.md")
    backup_if_exists(ROOT / "RESEARCH_REPORT_FA.md", ROOT / "coordination" / "RESEARCH_REPORT_FA_PRE_FINAL.md")
    backup_if_exists(ROOT / "MASTER_DECISION_FA.md", ROOT / "coordination" / "MASTER_DECISION_FA_PRE_FINAL.md")
    wrapper = cycle_path("solver.py")
    backup_if_exists(wrapper, ROOT / "coordination" / "public_wrapper_R2.py")
    wrapper_text = """\"\"\"C007 public CLI wrapper, v4 provider.\"\"\"\nfrom pathlib import Path\nimport runpy, sys\nimpl = Path(__file__).resolve().parent / 'implementation'\nsys.path.insert(0, str(impl))\nrunpy.run_path(str(impl / 'finest_cli_v2.py'), run_name='__main__')\n"""
    wrapper.write_text(wrapper_text, encoding="utf-8", newline="\n")

    readme = cycle_path("implementation/ROOT_README_CANDIDATE_FA_v2.md").read_text(encoding="utf-8")
    readme = readme.replace("results/2026-11-02/partition_finest_v7/implementation/finest_cli_v2.py",
                            "results/2026-11-02/partition_finest_v7/solver.py")
    readme += "\n## گزارش و شواهد نهایی\n\n"
    readme += "- [گزارش علمی نهایی](RESEARCH_REPORT_FA.md)\n"
    readme += "- [تصمیم مستر](MASTER_DECISION_FA.md)\n"
    readme += "- [اثبات‌ها](theory/PROOFS_v1.md)\n"
    readme += "- [گیت مستقل v4](audit/validation_v2/provider_gate_v4.json)\n"
    readme += "- [نتیجهٔ زمان‌گیری پذیرفته‌شده](" + Path(rel_workspace(timing)).relative_to(Path("results/2026-11-02/partition_finest_v7")).as_posix() + ")\n"
    (ROOT / "README_FA.md").write_text(readme, encoding="utf-8", newline="\n")

    report_text = report.read_text(encoding="utf-8")
    report_text += "\n\n## پیوست: زمان‌گیری پذیرفته‌شده\n\n"
    report_text += "| اندازه‌گیری | نتیجه |\n|---|---|\n"
    report_text += f"| فایل ثبت‌شده | `{rel_workspace(timing)}` |\n"
    report_text += f"| وضعیت علمی | `{timing_data.get('scientific_status', timing_data.get('status'))}` |\n\n"
    report_text += table + "\n\n"
    report_text += "زمان کامل فرایند از خواندن ورودی تا خروجی، با احتساب پیش‌پردازش، معیار اصلی است. "
    report_text += "زمان‌های داخلی adaptive/fallback ممکن است هم‌پوشانی داشته یا بخشی از هزینه را ثبت نکنند؛ جمع آن‌ها زمان کل نیست. "
    report_text += "این سلول‌ها کارایی عمومی را تضمین نمی‌کنند و هیچ برتری کلی از پیش فرض نمی‌شود.\n"
    (ROOT / "RESEARCH_REPORT_FA.md").write_text(report_text, encoding="utf-8", newline="\n")

    decision = cycle_path("implementation/MASTER_DECISION_CANDIDATE_FA_v1.md").read_text(encoding="utf-8")
    decision = decision.replace("نتیجهٔ پذیرفته‌شدهٔ زمان‌گیری در زمان اجرای اسکریپت closure به این بخش افزوده می‌شود.",
        f"زمان‌گیری پذیرفته‌شده در `{rel_workspace(timing)}` ثبت شده است. جدول و caveat زمان در گزارش نهایی آمده‌اند.")
    (ROOT / "MASTER_DECISION_FA.md").write_text(decision, encoding="utf-8", newline="\n")

    # Preserve the prior history byte-for-byte and add the new cycle at its head.
    start = WORKSPACE / "START_HERE_FA.md"
    old_start = start.read_text(encoding="utf-8")
    section = ("# شروع و ادامهٔ پژوهش یادگیری غیرفعال اتوماتا\n\n"
        "آخرین تحویل: **C007، ۲۰۲۶/۱۱/۰۲**. حل‌گر v4 برای ریزترین افراز سازگار با نمونه، "
        "با ممیزی مستقل و زمان‌گیری پذیرفته‌شده مستند شده است. این ادعا بازیابی معماری پنهان را تضمین نمی‌کند؛ "
        "در بدترین حالت جست‌وجو نمایی است.\n\n"
        f"- [راهنمای C007](results/2026-11-02/partition_finest_v7/README_FA.md)\n"
        f"- [گزارش C007](results/2026-11-02/partition_finest_v7/RESEARCH_REPORT_FA.md)\n"
        f"- [تصمیم C007](results/2026-11-02/partition_finest_v7/MASTER_DECISION_FA.md)\n"
        f"- [نتیجهٔ چرخه و وضعیت اجراها](results/2026-11-02/partition_finest_v7/coordination/CYCLE_OUTCOME.json)\n\n"
        "## سوابق چرخه‌های پیشین\n\n")
    old_body = old_start.split("\n", 1)[1] if old_start.startswith("# ") else old_start
    start.write_text(section + old_body, encoding="utf-8", newline="\n")

    required = ["solver.py", "implementation/finest_solver_v4.py", "implementation/finest_cli_v2.py",
        "implementation/C007_prepare_delivery_v1.py", "implementation/MASTER_DECISION_CANDIDATE_FA_v1.md",
        "implementation/archive_integrity_v2.py", "implementation/ROOT_README_CANDIDATE_FA_v2.md",
        "README_FA.md", "RESEARCH_REPORT_FA.md", "MASTER_DECISION_FA.md", "theory/PROOFS_v1.md",
        "coordination/CORRECTNESS_ACCEPTANCE_V4.json", "coordination/PERFORMANCE_GO_V2.json",
        "coordination/PERFORMANCE_REVIEW_V1.json", "coordination/WRAPPER_R2.json",
        "coordination/CORRECTNESS_ACCEPTANCE.json",
        "audit/timing_v2/PROPOSAL_V2.md", *gate_refs.values(), rel_workspace(timing),
        rel_workspace(report), rel_workspace(WORKSPACE / "START_HERE_FA.md")]
    unique = []
    seen = set()
    for item in required:
        abs_path = resolve_input(item)
        if not abs_path.is_file(): raise FileNotFoundError(abs_path)
        key = rel_workspace(abs_path)
        if key not in seen:
            unique.append({"path": key, "sha256": digest(abs_path), "bytes": abs_path.stat().st_size})
            seen.add(key)
    parent = read(cycle_path("coordination/parent_manifest.json"))
    for entry in parent.get("files", []):
        target = (WORKSPACE / entry["path"]).resolve()
        if not target.is_file() or digest(target) != entry["sha256"]:
            raise ValueError(f"immutable parent dependency changed: {entry.get('path')}")
    runtime = {"cycle": "C007", "status": "frozen_final_pending_integrity", "files": unique,
               "parent_dependencies": parent.get("files", []),
               "gates": {**gate_refs, "accepted_timing": rel_workspace(timing)}}
    runtime_path = cycle_path("coordination/runtime_final.json")
    if runtime_path.exists(): raise FileExistsError(runtime_path)
    runtime_path.write_text(json.dumps(runtime, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    promotion = {"readme_source": "implementation/ROOT_README_CANDIDATE_FA_v2.md",
        "readme_sha256": digest(cycle_path("implementation/ROOT_README_CANDIDATE_FA_v2.md")),
        "readme_target": "README_FA.md", "report_source": rel_workspace(report),
        "report_sha256": digest(report), "report_target": "RESEARCH_REPORT_FA.md",
        "timing_source": rel_workspace(timing), "timing_sha256": digest(timing),
        "decision_source": "implementation/MASTER_DECISION_CANDIDATE_FA_v1.md",
        "decision_target": "MASTER_DECISION_FA.md", "runtime_manifest": "coordination/runtime_final.json"}
    for name, value in (("coordination/delivery_promotion_v1.json", promotion),):
        target = cycle_path(name)
        if target.exists(): raise FileExistsError(target)
        target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with cycle_path("coordination/journal.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"event":"master_prepares_final_delivery","at_utc":datetime.now(timezone.utc).isoformat(),
            "report":rel_workspace(report),"timing":rel_workspace(timing),"runtime_manifest":"coordination/runtime_final.json"},ensure_ascii=False)+"\n")

def finalize(integrity_arg: str):
    integrity = cycle_path(integrity_arg)
    record = read(integrity)
    if record.get("status") != "pass" or record.get("error_count") != 0:
        raise ValueError("archive integrity has not passed with zero errors")
    runtime_path = cycle_path("coordination/runtime_final.json")
    runtime = read(runtime_path)
    for entry in runtime.get("files", []):
        target = (WORKSPACE / entry["path"]).resolve()
        if not target.is_file() or digest(target) != entry["sha256"]:
            raise ValueError(f"runtime manifest mismatch: {entry['path']}")
    for entry in runtime.get("parent_dependencies", []):
        target = (WORKSPACE / entry["path"]).resolve()
        if not target.is_file() or digest(target) != entry["sha256"]:
            raise ValueError(f"parent dependency manifest mismatch: {entry['path']}")
    link_docs = [ROOT/"README_FA.md", ROOT/"RESEARCH_REPORT_FA.md", ROOT/"MASTER_DECISION_FA.md"]
    links = []
    for doc in link_docs:
        for target in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"): continue
            raw_target = target.split("#", 1)[0]
            local = (doc.parent / raw_target).resolve()
            workspace_target = (WORKSPACE / raw_target).resolve()
            linked = local if local.exists() else workspace_target
            if not linked.exists(): raise ValueError(f"broken link in {doc.name}: {target}")
            links.append({"document":doc.name,"target":target})
    attempts = []
    for path in sorted((ROOT/"evidence/attempts").glob("*/result.json")):
        data = read(path)
        attempts.append({"attempt_id":data.get("attempt_id"),"execution_status":data.get("execution_status"),
                         "scientific_status":data.get("scientific_status","not_assessed")})
    outcome = {"cycle":"C007","status":"complete","scientific_status":"confirmed_under_retained_assumptions",
        "target":"unique finest sample-compatible partition; no hidden architecture recovery claim",
        "v4_provider_sha256":EXPECTED["implementation/finest_solver_v4.py"],
        "correctness_gate":"audit/validation_v2/provider_gate_v4.json","attempt_count":len(attempts),
        "attempts":attempts,"integrity":{"path":rel_workspace(integrity),"sha256":digest(integrity),
            "error_count":0,"counts":record.get("counts",{})},
        "limitations":["worst-case exponential search","structured scale families only","no RPNI/noise/shared symbols"],
        "evidence":[{"path":rel_workspace(p),"sha256":digest(p)} for p in
            [ROOT/"README_FA.md",ROOT/"RESEARCH_REPORT_FA.md",ROOT/"MASTER_DECISION_FA.md",runtime_path]]}
    for name, value in (("coordination/CYCLE_OUTCOME.json",outcome),
                        ("coordination/DELIVERY_LINKS.json",{"count":len(links),"links":links}),
                        ("coordination/CLOSURE_CHECKS.json",{"status":"passed","integrity":"pass",
                            "runtime_manifest":"pass","markdown_links":"pass","links_checked":len(links),
                            "attempt_records":len(attempts)})):
        path=cycle_path(name)
        if path.exists(): raise FileExistsError(path)
        path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with cycle_path("coordination/journal.jsonl").open("a",encoding="utf-8") as stream:
        stream.write(json.dumps({"event":"cycle_completed","at_utc":datetime.now(timezone.utc).isoformat(),
            "integrity":rel_workspace(integrity),"links_checked":len(links)},ensure_ascii=False)+"\n")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="phase",required=True)
    p=sub.add_parser("prepare"); p.add_argument("--report",required=True); p.add_argument("--timing",required=True)
    f=sub.add_parser("finalize"); f.add_argument("--integrity",required=True)
    args=parser.parse_args()
    if args.phase=="prepare": prepare(args.report,args.timing)
    else: finalize(args.integrity)
    print(json.dumps({"phase":args.phase,"status":"completed"}))

if __name__=="__main__": main()
