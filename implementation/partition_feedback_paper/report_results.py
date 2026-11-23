
"""Audit benchmark completeness and generate the mentor-facing results table."""
from collections import Counter
import json
from statistics import median

from benchmark import EVIDENCE, VARIANTS


def paid(row):
    metrics = row.get("selection", {})
    return metrics.get("regular_calls", 0) + metrics.get("diagnostic_calls", 0)


def report():
    counts = {}
    all_records = {}
    for profile, expected in (("main", 1215), ("scale", 108), ("memory", 45)):
        path = EVIDENCE / f"trials_{profile}.jsonl"
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        keys = {(r["case"], r["variant"], r["budget"], r["limit"], r["memory"], r["repeat"]) for r in records}
        assert len(records) == len(keys) == expected, (profile, len(records), len(keys), expected)
        counts[profile] = {"trials": expected, "verified": sum(r["verdict"] == "VERIFIED" for r in records)}
        all_records[profile] = records

    staged = json.loads((EVIDENCE / "trials_staged.json").read_text(encoding="utf-8"))["trials"]
    stage_keys = {(r["case"], r["repeat"], r["variant"]) for r in staged}
    assert len(stage_keys) == len(staged) == 24
    counts["staged"] = {"trials": len(staged), "verified": sum(r["verdict"] == "VERIFIED" for r in staged)}
    main = all_records["main"]
    hdfs = json.loads((EVIDENCE / "hdfs_cases.json").read_text(encoding="utf-8"))
    hdfs_root = {}
    for name, D in hdfs.items():
        positive_counts = [Counter(x) for x in D["positive"]]
        observed_counts = {a: {count[a] for count in positive_counts} for a in D["alphabet"]}
        negative_counts = [Counter(y) for y in D["negative"]]
        hdfs_root[name] = {
            "singleton_failed": sum(all(count[a] in observed_counts[a] for a in D["alphabet"])
                                   for count in negative_counts),
            "opposite_label_words": len({tuple(x) for x in D["positive"]} & {tuple(y) for y in D["negative"]}),
        }

    holdout = {(r["case"], r["budget"], r["limit"], r["repeat"], r["variant"]): r for r in main
               if "holdout" in r["case"] and r["variant"] in ("full", "full_diagnostics")}
    pairs = [(a, holdout[(*key[:-1], "full_diagnostics")]) for key, a in holdout.items() if key[-1] == "full"]
    shared = [(a, b) for a, b in pairs if a["verdict"] == b["verdict"] == "VERIFIED"]
    med_base = median(a["elapsed_seconds"] for a, b in shared) if shared else None
    med_diag = median(b["elapsed_seconds"] for a, b in shared) if shared else None
    gate = {
        "pairs": len(pairs), "common_verified": len(shared),
        "base_total_queries": sum(paid(a) for a, _ in pairs),
        "diagnostic_total_queries": sum(paid(b) for _, b in pairs),
        "base_verified": sum(a["verdict"] == "VERIFIED" for a, _ in pairs),
        "diagnostic_verified": sum(b["verdict"] == "VERIFIED" for _, b in pairs),
        "base_median_common_seconds": med_base, "diagnostic_median_common_seconds": med_diag,
    }
    gate["enable_default"] = (gate["diagnostic_total_queries"] < gate["base_total_queries"]
                              and gate["diagnostic_verified"] >= gate["base_verified"]
                              and bool(shared) and med_diag <= 1.05 * med_base)

    at_five = [r for r in main if r["budget"] == 5 and r["variant"] in ("pairs", "passive", "full", "full_diagnostics")]
    cases = dict.fromkeys(r["case"] for r in at_five)
    lines = ["# مشاهده‌های اجرای قابل‌بازتولید", "",
             "هر خانهٔ موفقیت تعداد خروجی‌های تأییدشده از سه تکرار ترتیبی با بودجهٔ ۵ ثانیه تا پایان بازپخش است. "
             "میانهٔ زمان فقط روی ردیف‌های تأییدشده محاسبه می‌شود. خط تیره به معنی فقدان اجرای تأییدشده است.", "",
             "| ورودی | منفی ناکام در تک‌نمادی | همهٔ جفت‌ها | جدول منفعل | کامل | کامل و تشخیصی | بلوک تأییدشده | میانهٔ کامل (ms) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for case in cases:
        rows = [r for r in at_five if r["case"] == case]
        verified = [r for r in rows if r["verdict"] == "VERIFIED"]
        results = {r["blocks"] for r in verified}
        assert len(results) <= 1, (case, results)
        full = [r for r in verified if r["variant"] == "full"]
        cells = [str(sum(r["variant"] == k for r in verified))+"/3"
                 for k in ("pairs", "passive", "full", "full_diagnostics")]
        failed = hdfs_root.get(case, {}).get("singleton_failed", "—")
        blocks = next(iter(results), "—")
        elapsed = f"{1000*median(r['elapsed_seconds'] for r in full):.2f}" if full else "—"
        lines.append(f"| {case} | {failed} | {' | '.join(cells)} | {blocks} | {elapsed} |")

    totals = Counter(r["variant"] for r in main if r["verdict"] == "VERIFIED")
    lines += ["", "### مقایسهٔ تفکیک‌شده", "",
              "| روش | تأیید در همهٔ بودجه‌ها | استعلام عادی | استعلام تشخیصی |",
              "|---|---:|---:|---:|"]
    for arm in VARIANTS:
        arm_rows = [r for r in main if r["variant"] == arm]
        regular = sum(r.get("selection", {}).get("regular_calls", 0) for r in arm_rows)
        diagnostic = sum(r.get("selection", {}).get("diagnostic_calls", 0) for r in arm_rows)
        lines.append(f"| {arm} | {totals[arm]}/{len(arm_rows)} | {regular} | {diagnostic} |")
    lines += ["", "برای استعلام‌های تجمعی، افزایش یا کاهش تعداد اجرای ناتمام نیز بر مقدار اثر دارد. "
              "تحلیل استعلام در مجموعهٔ جدا باید تعداد تأیید و زمان مشترک را هم همراه داشته باشد.", "",
              f"- آزمون اصلی {counts['main']['verified']} تأیید از {counts['main']['trials']} اجرا داشت.",
              f"- آزمون مقیاس {counts['scale']['verified']} تأیید از {counts['scale']['trials']} اجرا داشت.",
              f"- اندازه‌گیری جداگانهٔ حافظه {counts['memory']['verified']} تأیید از {counts['memory']['trials']} اجرا داشت.",
              f"- در مجموعهٔ جدا، نسخهٔ کامل به {gate['base_verified']}/{gate['pairs']} تأیید و "
              f"{gate['base_total_queries']} استعلام رسید. با استعلام تشخیصی این اعداد به "
              f"{gate['diagnostic_verified']}/{gate['pairs']} و {gate['diagnostic_total_queries']} رسیدند.",
              f"- شمار مقایسه‌های زمانی روی اجراهای مشترک {gate['common_verified']} است. "
              f"میانهٔ خام تا تأیید به ثانیه، به‌ترتیب {med_base} و {med_diag} است.",
              "- پیش‌فرض این بسته استعلام تشخیصیِ غیرفعال است. "
              + ("شرط آزمایشی برای فعال‌سازی برقرار شد." if gate["enable_default"] else
                 "شرط آزمایشی برای فعال‌سازی برقرار نشد.")]
    lines += ["", "### اثر پیش‌بررسیِ تک‌نمادی", "",
              "| داده | هسته / تأیید | مرحله‌ای / تأیید | میانهٔ هسته (ms) | میانهٔ مرحله‌ای (ms) |",
              "|---|---:|---:|---:|---:|"]
    for name in dict.fromkeys(r["case"] for r in staged):
        variants = [[r for r in staged if r["case"] == name and r["variant"] == v and r["verdict"] == "VERIFIED"]
                    for v in ("core", "staged")]
        trials = [f"{len(rows)}/3" for rows in variants]
        times = [f"{1000*median(r['seconds'] for r in rows):.2f}" if rows else "—" for rows in variants]
        lines.append(f"| {name} | {' | '.join(trials + times)} |")
    overrun = max(row["elapsed_seconds"] - row["budget"] for row in main)
    lines += ["", f"بیشترین عبورِ ثبت‌شده از بودجه در اجرای اصلی {overrun:.3f} ثانیه بود. "
              "کنترل موعد تعاونی است و چنین خروجی‌هایی ناتمام شمرده شده‌اند."]
    (EVIDENCE / "RESULTS_FA.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    (EVIDENCE / "summary_gate.json").write_text(json.dumps({"counts": counts, "diagnostic_gate": gate,
        "hdfs_root": hdfs_root}, indent=2), encoding="utf-8")
    print(json.dumps({"counts": counts, "gate": gate}))


if __name__ == "__main__":
    report()
