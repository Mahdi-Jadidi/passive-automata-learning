"""Create compact accepted Stage2 timing gate JSON and its Persian report."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def main() -> None:
    detailed_path = HERE / "stage2_timing_report_v1.json"
    detailed = read(detailed_path)
    protocol = read(HERE / "stage2_timing_protocol_v1.json")
    preservation = read(HERE / "stage2_timing_preservation_inventory_v1.json")
    refreeze = read(HERE / "stage2_timing_refreeze_erratum_01.json")
    execution = read(HERE / "stage2_timing_execution_ledger_v1.json")
    stage1 = read(HERE / "stage1_performance_report_v2.json")

    if detailed.get("acceptance") != "accepted" or detailed.get("validation_errors"):
        raise SystemExit("detailed timing report is not accepted")
    failed_aggregates = [
        {"attempt_id": "20261029T085410.908640Z_165a89ef3d", "error": "report summary field name mismatch", "provider_runs_started": 0},
        {"attempt_id": "20261029T085455.184101Z_0ff6dc9062", "error": "budget aggregation field name mismatch", "provider_runs_started": 0},
    ]
    successful_aggregate = {
        "attempt_id": "20261029T085528.010634Z_373cccb9da",
        "execution_status": "success", "exit_code": 0,
        "stdout_sha256": "f30427635905534b5dc9785cbee5ef6620985105e797d554e1cc67099df9173f",
    }
    provider_jobs = detailed["per_job_records"]
    wall = detailed["wall_results"]
    mem = detailed["memory_results"]
    cell_summary = {}
    for case, methods in wall.items():
        cell_summary[case] = {}
        for method, row in methods.items():
            cell_summary[case][method] = {
                "median_wall_seconds": row["median_wall_seconds"],
                "min_wall_seconds": row["min_wall_seconds"],
                "max_wall_seconds": row["max_wall_seconds"],
                "wall_seconds_by_rep": row["wall_seconds_by_rep"],
                "median_provider_seconds": row["median_provider_seconds"],
                "median_output_bytes": row["median_output_bytes"],
                "output_bytes_by_rep": row["output_bytes_by_rep"],
                "status_counts": row["search_statuses"],
                "uniqueness_counts": row["uniqueness_statuses"],
                "search_exhausted_by_rep": row["search_exhausted_by_rep"],
                "solutions_by_rep": row["solution_count_by_rep"],
                "search_nodes_by_rep": row["search_nodes_by_rep"],
                "pair_tests_by_rep": row["pair_tests_by_rep"],
                "attempt_ids": row["attempt_ids"],
            }

    gate = {
        "schema": "C004-stage2-matched-timing-gate-v1",
        "acceptance": "accepted",
        "validation_errors": [],
        "protocol_sha256": detailed["protocol_sha256"],
        "protocol_freeze_record_sha256": detailed["protocol_freeze_record_sha256"],
        "schedule_sha256": detailed["schedule_sha256"],
        "stage2_correctness_gate_sha256": detailed["stage2_gate_report_sha256"],
        "runtime_manifest_sha256": detailed["runtime_manifest_sha256"],
        "source_bindings": detailed["source_bindings"],
        "inputs": detailed["input_bindings"],
        "job_counts": detailed["scheduled_counts"],
        "wall_scope": {
            "metric": "capture subprocess_seconds",
            "per_job_hard_timeout_seconds": 30.0,
            "provider_soft_deadline_seconds": 29.0,
            "includes": protocol["measured_scope"]["wall_includes"],
            "source_snapshot_overhead_excluded": True,
            "serialized": "full API result inside metadata envelope, including QOP graph and witnesses",
        },
        "wall_results": cell_summary,
        "memory_results": mem,
        "qop_exact_edge_counts": detailed["qop_exact_edge_counts"],
        "provider_budget_accounting": detailed["budget_accounting"],
        "capture_source_snapshot_reconciliation": {
            "attempts_with_snapshots": len(detailed["capture_source_snapshot_reconciliation"]),
            "source_bindings_verified_per_attempt": True,
            "provider_capture_attempts": [row["attempt_id"] for row in provider_jobs],
        },
        "aggregate_capture": successful_aggregate,
        "superseded_read_only_aggregate_attempts": failed_aggregates,
        "preservation_inventory_sha256": sha(HERE / "stage2_timing_preservation_inventory_v1.json"),
        "refreeze_erratum_sha256": sha(HERE / "stage2_timing_refreeze_erratum_01.json"),
        "preservation_status": {
            "original_protocol_bytes_available": preservation["items"]["original_protocol"]["bytes_available"],
            "original_freeze_bytes_available": preservation["items"]["original_freeze_record"]["bytes_available"],
            "failed_executor_source_bytes_available": preservation["items"]["failed_executor_source"]["bytes_available"],
            "pre_refreeze_provider_children_started": refreeze["pre_executor_fix_provider_children_started"],
            "active_refrozen_protocol_used_for_all_jobs": refreeze["active_protocol_used_for_all_fifteen_jobs"],
            "historical_bytes_reconstructed": False,
            "empty_failed_ledger_snapshot_sha256": preservation["items"]["empty_failed_ledger_snapshot"]["sha256"],
        },
        "limits": detailed["limits"],
    }
    gate_path = HERE / "stage2_timing_gate_v1.json"
    gate_bytes = (json.dumps(gate, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    gate_path.write_bytes(gate_bytes)
    gate_hash = sha(gate_path)

    fa = f'''# گزارش زمان‌سنجی مرحله دوم

**وضعیت:** پذیرفته شد؛ هر ۱۵ اجرای زمان‌سنجی مستقل و پس از ثبت خروجی خام بررسی شدند و خطای اعتبارسنجی صفر بود.

پروتکل فعال با SHA-256 `{detailed["protocol_sha256"]}` پیش از اجرا تثبیت شد. هش برنامه زمان‌بندی `{detailed["schedule_sha256"]}` است. ۱۲ اجرای زمان‌سنجی و ۳ اجرای جداگانه `tracemalloc` با ۱۵ فرایند تازه و به‌صورت سریالی اجرا شدند. هر دو روش روی ورودی‌های یکسان با `k` معلوم، سقف واژگان محلی `q=2` و `max_solutions=2` اجرا شدند.

## زمان دیواری کامل

زمان‌ها از `capture subprocess_seconds` گرفته شده‌اند. این بازه راه‌اندازی مفسر فرزند، خواندن پروتکل و ورودی، واردکردن حل‌گر، حل مسئله، سریال‌سازی کل نتیجه API و نوشتن خروجی را دربرمی‌گیرد. زمان snapshot منابع توسط ابزار capture بیرون از این بازه است. مهلت نرم حل‌گر ۲۹ ثانیه و مهلت سخت هر فرایند ۳۰ ثانیه بود.

| ورودی | روش | میانه زمان دیواری | بازه سه اجرا | میانه بایت خروجی | نتیجه |
|---|---|---:|---:|---:|---|
| `m16/k4` | General v3, q2 | {wall['m16_k4']['general_v3_q2']['median_wall_seconds']:.3f} s | {wall['m16_k4']['general_v3_q2']['min_wall_seconds']:.3f}–{wall['m16_k4']['general_v3_q2']['max_wall_seconds']:.3f} s | {int(wall['m16_k4']['general_v3_q2']['median_output_bytes']):,} | ۳ از ۳ کامل و یکتا |
| `m16/k4` | QOP001, q2 | {wall['m16_k4']['qop001_q2']['median_wall_seconds']:.3f} s | {wall['m16_k4']['qop001_q2']['min_wall_seconds']:.3f}–{wall['m16_k4']['qop001_q2']['max_wall_seconds']:.3f} s | {int(wall['m16_k4']['qop001_q2']['median_output_bytes']):,} | گواهی یکتای معتبر در ۳ اجرا |
| `m128/k8` | General v3, q2 | {wall['m128_k8']['general_v3_q2']['median_wall_seconds']:.3f} s | {wall['m128_k8']['general_v3_q2']['min_wall_seconds']:.3f}–{wall['m128_k8']['general_v3_q2']['max_wall_seconds']:.3f} s | {int(wall['m128_k8']['general_v3_q2']['median_output_bytes']):,} | ۳ پاسخ معتبر؛ جست‌وجو ناقص و یکتایی نامعلوم |
| `m128/k8` | QOP001, q2 | {wall['m128_k8']['qop001_q2']['median_wall_seconds']:.3f} s | {wall['m128_k8']['qop001_q2']['min_wall_seconds']:.3f}–{wall['m128_k8']['qop001_q2']['max_wall_seconds']:.3f} s | {int(wall['m128_k8']['qop001_q2']['median_output_bytes']):,} | گواهی یکتای معتبر در ۳ اجرا |

هر شش پاسخ General v3 و هر شش پاسخ QOP با پارتیشن هدف مقایسه شدند و تصویرهای مثبت و سقف دو واژه برای هر عامل مستقلاً بررسی شد. در `m128/k8`، General v3 در هر سه اجرا یک پاسخ درست داد، ولی جست‌وجوی کامل نشد؛ این سه اجرا شاهد یکتایی نیستند. گواهی QOP در ورودی بزرگ ۷٬۱۶۸ یال تقابل دقیق را با شاهدهای قابل‌بررسی تولید کرد. خروجی کامل QOP بزرگ حدود ۸۴۵ KB بود و هزینه سریال‌سازی در زمان دیواری دیده می‌شود.

## حافظه جداگانه

مقادیر زیر اوج تخصیص‌های Python ثبت‌شده با `tracemalloc` هستند، نه RSS فرایند. این سه اجرا جدا از مقایسه زمان دیواری‌اند.

| ورودی | روش | اوج تخصیص ردیابی‌شده |
|---|---|---:|
| `m16/k4` | General v3, q2 | {mem[0]['peak_traced_python_bytes']:,} bytes |
| `m16/k4` | QOP001, q2 | {mem[1]['peak_traced_python_bytes']:,} bytes |
| `m128/k8` | QOP001, q2 | {mem[2]['peak_traced_python_bytes']:,} bytes |

مصرف زمان اندازه‌گیری‌شده General v3 در Stage 1 برابر {detailed['budget_accounting']['general_v3']['stage1_standard_and_stress_seconds']:.3f} ثانیه بود. با احتساب فراخوانی‌های دیواری و اجرای حافظه Stage 2، مجموع {detailed['budget_accounting']['general_v3']['combined_measured_invocation_seconds']:.3f} از سقف ۹۰۰ ثانیه است. QOP001 در این مرحله مجموع {detailed['budget_accounting']['qop001']['combined_measured_invocation_seconds']:.3f} ثانیه مصرف کرد.

## دامنه و سوابق حفظ‌شده

نتیجه QOP مشروط به `k` معلوم، `q=2`، برچسب‌های دقیق و گواهی تقابل است و ادعایی درباره بازیابی عامل‌های DFA نامقید نیست. ورودی‌ها مثبت‌محور و از خانواده دارای زبان محلی با حداکثر دو واژه‌اند.

پیش از شروع اجرا، یک خطای هماهنگ‌کننده تشخیص داده شد و صفر فرزند حل‌گر اجرا شده بود. پروتکل و freeze اولیه با هش‌های ثبت‌شده در inventory در content-addressed storage پیدا نشدند؛ بایت‌های تاریخی و منبع دقیق اجرای ناموفق در دسترس نیستند و بازسازی نشده‌اند. ledger خالی و رکورد خطا حفظ شده‌اند. هر ۱۵ اجرای رسمی به پروتکل refreezeشده با هش بالا متصل‌اند. دو خطای بعدی فقط در اسکریپت تجمیعِ پس از اجرا رخ دادند؛ خروجی‌های خام زمان‌سنجی را تغییر ندادند و اجرای نهایی تجمیع موفق بود.

JSON فشرده پذیرفته‌شده: `stage2_timing_gate_v1.json`، SHA-256 `{gate_hash}`.
'''
    fa_path = HERE / "STAGE2_TIMING_REPORT_FA.md"
    fa_path.write_text(fa, encoding="utf-8")
    print(json.dumps({"acceptance": gate["acceptance"], "gate_sha256": gate_hash,
                      "persian_report_sha256": sha(fa_path), "jobs": gate["job_counts"]},
                     ensure_ascii=False, sort_keys=True, separators=(",", ":")))

if __name__ == "__main__":
    main()
