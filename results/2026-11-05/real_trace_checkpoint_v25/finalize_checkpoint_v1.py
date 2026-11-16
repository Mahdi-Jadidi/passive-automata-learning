"""Verify frozen bindings, delivery links and completed evidence; record hashes."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOLVER_HASH = "73ff8ecae70a55525ec6a2d3f1216e721ad2f1298d973d334e6f743080358e4e"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    checks = []
    def check(name, passed):
        checks.append(dict(check=name, passed=bool(passed)))
    freeze = read(HERE / "audit/ACTUAL_FREEZE_V3.json")
    check("reviewed solver matches frozen hash", sha(HERE / "implementation/selected_output_v1/solver_v1.py") == SOLVER_HASH == freeze["solver_sha256"])
    check("evaluation harness unchanged", sha(HERE / "audit/evaluate_v3.py") == freeze["harness_sha256"])
    check("protocol unchanged", sha(HERE / "audit/PROTOCOL_V3.md") == freeze["protocol_sha256"])
    for arm in freeze["arms"]:
        check("frozen input " + arm["id"], sha(Path(arm["path"])) == arm["sha256"])
    for item in read(HERE / "audit/POSTHOC_FREEZE_V1.json"):
        check("posthoc binding " + Path(item["path"]).name, sha(Path(item["path"])) == item["sha256"])
    actual = read(HERE / "audit/ACTUAL_RESULTS_V1.json")
    check("42 audited cells, zero semantic errors", actual["cells"] == 42 and actual["semantic_certificate_errors"] == 0)
    controls = read(HERE / "audit/SMALL_CONTROLS_V1.json")
    check("independent controls 435 passed", controls["calls"] == 435 and controls["errors"] == 0)
    posthoc = read(HERE / "audit/POSTHOC_INTEGRITY_COVERAGE_V1.json")
    check("42 posthoc output checks passed without reruns", posthoc["status"] == "passed" and posthoc["cells_checked"] == 42 and posthoc["errors"] == [] and posthoc["solver_oracle_reruns"] == 0 and posthoc["original_results_modified"] is False)
    ingestion = read(HERE / "audit/INGESTION_REPLAY_V1.json")
    check("18 source ingestion replay", ingestion["status"] == "verified" and ingestion["events_checked"] == 1560 and ingestion["errors"] == [])
    captures = read(HERE / "audit/ACTUAL_LEDGER_V1.json")
    check("all seven bounded captures completed and reaped", len(captures) == 7 and all(x["execution_status"] == "success" and x["exit_code"] == 0 and x["child_reaped"] for x in captures))
    summary = read(HERE / "RESULTS_SUMMARY_V2.json")
    check("manager summary 32 ambiguous,10 incompatible,0 unique", summary["cells"] == 42 and summary["status_counts"] == {"ambiguous": 32, "incompatible": 10})
    for arm in summary["arms"]:
        check("summary output binding " + arm["arm"], sha(HERE / arm["source"]) == arm["source_sha256"])
    for filename in ["CLI_VERIFICATION_V1.json", "REAL_CLI_VERIFICATION_V1.json"]:
        check("CLI " + filename, read(HERE / "demo" / filename)["passed"] is True)
    old = read(ROOT / "results/2026-11-05/search_checkpoint_v24/RESEARCH_LEDGER_V1.json")
    check("public C024 entrypoint unchanged", sha(ROOT / "partition.py") == old["public_entry_sha256"])
    check("public C024 integrated solver unchanged", sha(ROOT / "results/2026-11-05/search_checkpoint_v24/implementation/integrated_c024_v1/gate_v1.py") == old["integrated_solver_sha256"])
    for filename in ["RESEARCH_REPORT_FA.md", "ADVISOR_BRIEF_FA.md", "demo/README_FA.md"]:
        path = HERE / filename
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" not in link and not link.startswith("#"):
                check("local link " + filename + " -> " + link, (path.parent / link.split("#", 1)[0]).exists())
    passed = all(x["passed"] for x in checks)
    verification = dict(date="2026-11-06", passed=passed, checks=checks,
                        scope="Frozen binding/link/evidence checks, not a new inference sweep",
                        remaining_limits=["1..8 selected atomic types", "No external unique partition", "No physical ownership recovery", "CLI cooperative deadline needs outer cap", "No RPNI or speed comparison"])
    (HERE / "MANAGER_VERIFICATION_V1.json").write_text(json.dumps(verification, indent=2), encoding="utf-8")
    if not passed:
        print(json.dumps(dict(passed=False, failed=[x for x in checks if not x["passed"]])))
        return 1
    coordination = dict(checkpoint="C025", completed_date="2026-11-06",
                        outcome="initial_advisor_checkpoint_completed",
                        authorization="User requested realistic trace checks, algorithm advancement and advisor-presentable stage, delegated at low effort",
                        baseline="C024 partition.py preserved under AND full-word contract",
                        experiment="selected-output exact final-block cover, explicit depth, 1..8 caller-selected types",
                        delivery="partition_events.py plus model/proofs, external-data evidence, advisor brief and runnable demos",
                        actual_sweep=dict(cells=42, ambiguous=32, incompatible=10, unique=0, unresolved=0, all_match_independent_RGS=True),
                        checks=dict(independent_controls=435, developer_controls=162, constructed_CLI_demos=5, actual_CLI_smoke=1, posthoc_cells=42),
                        workers=read(HERE / "COORDINATION_V1.json")["workers"],
                        worker_disposition="Implementation/theory/audit research delivered; correction-only audit followup interrupted, manager authored V2 reading correction. No further runs pending.",
                        methodological_independence="Separate oracle representation/code and coordinated AI chats, not independent human or blinded evaluation",
                        next_stage="Validate multi-host event abstraction/order/reset, then scale and evaluate local automata learning",
                        claims_not_established=["true multi-host recovery", "full corpus coverage", "end-to-end RPNI improvement", "new external theorem", "performance advantage"],
                        public_or_remote_mutation="No Git commit/push/PR; new local experimental entrypoint and documentation only",
                        preserved_attempts=["All audit/implementation captures and drafts", "Manager aggregation V1 KeyError, corrected V2; no inference changes", "Original misleading constancy sentence preserved with scoped V2 correction"])
    (HERE / "COORDINATION_FINAL_V1.json").write_text(json.dumps(coordination, indent=2), encoding="utf-8")
    ledger_path = HERE / "RESEARCH_LEDGER_V1.json"
    files = []
    for path in sorted(HERE.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts and path != ledger_path:
            files.append(dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size, sha256=sha(path)))
    for path in [ROOT / "README.md", ROOT / "START_HERE_FA.md", ROOT / "partition.py", ROOT / "partition_events.py"]:
        files.append(dict(path=str(path.relative_to(ROOT)), bytes=path.stat().st_size, sha256=sha(path)))
    ledger = dict(checkpoint="C025", completed_date="2026-11-06", recorded_utc=datetime.now(timezone.utc).isoformat(),
                  interpreter=sys.executable, python=sys.version, platform=platform.platform(),
                  solver_sha256=SOLVER_HASH, public_entry_sha256=sha(ROOT / "partition.py"),
                  experimental_entry_sha256=sha(ROOT / "partition_events.py"),
                  verification_passed=True, file_count=len(files), files=files,
                  exclusion="This ledger excludes itself and regenerable __pycache__; raw upstream ZIP is referenced by the preserved acquisition/manifests rather than duplicated here")
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    print(json.dumps(dict(passed=True, checks=len(checks), archived_files=len(files), actual_cells=42, independent_controls=435)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
