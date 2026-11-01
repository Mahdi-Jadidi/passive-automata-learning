# جست‌وجوی دقیق و گواهی تنک C005

## اجرا از ریشهٔ workspace

wrapper اجرایی در ریشهٔ چرخهٔ C005 است: `results/2026-10-31/partition_coverage_v5/solver.py`؛ این فایل در ریشهٔ کل workspace نیست. فرمان‌های زیر را از ریشهٔ workspace اجرا کنید:

```powershell
$PythonExe = 'C:\Users\Mahdi\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $PythonExe -B -X utf8 results/2026-10-31/partition_coverage_v5/solver.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode exact --q 2 --max-solutions all
& $PythonExe -B -X utf8 results/2026-10-31/partition_coverage_v5/solver.py results/2026-10-31/partition_coverage_v5/general/examples/certificate_unique_q2.json --mode certificate --q 2
& $PythonExe -B -X utf8 results/2026-10-31/partition_coverage_v5/solver.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode hybrid --q 2
```

اجرای مستقیم CLI عمومی، بدون wrapper:

```powershell
& $PythonExe -B -X utf8 results/2026-10-31/partition_coverage_v5/general/public_cli_v1.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode exact --q 2 --max-solutions all
```

## انتخاب حالت و تفسیر خروجی

- `exact` حالت پیش‌فرض است. حذف `--q` مدل عوامل منظم نامحدود را می‌سنجد؛ `--q N` اندازهٔ زبان محلی هر عامل را به N محدود می‌کند. بدون `--max-solutions` حداکثر دو پاسخ برای تشخیص ابهام گزارش می‌شود؛ `all` همهٔ افرازهای سازگار را می‌شمارد.
- `certificate` به `--q` نیاز دارد و فقط در صورت اثبات یکتایی رنگ‌آمیزی گراف q-opposition پاسخ یکتا می‌دهد. `insufficient_coverage` یعنی گواهی کافی نیست، نه اینکه داده ناسازگار باشد.
- `hybrid` پس از `insufficient_coverage` جست‌وجوی دقیق همان مدل q را اجرا می‌کند. مهلت مطلق میان دو مرحله مشترک است؛ اگر گواهی ناقص بماند، fallback آغاز نمی‌شود.
- `--no-q-opposition` در حالت دقیق امکان مقایسهٔ همان ورودی با/بدون این قیود را می‌دهد.

هر پاسخ بلوک‌های الفبا، تصویر مثبت هر بلوک و برای هر منفی شاهد تصویری را دارد که در مثبت‌های همان بلوک نیست. `complete` و `enumeration_complete` تکمیل جست‌وجو را نشان می‌دهند؛ یافتن یک پاسخ برای تصمیم مثبت کافی است ولی یکتایی را ثابت نمی‌کند. `unique` فقط با پایان شمارش و یک افراز، و `ambiguous` با دو افراز ثابت می‌شود.

کدهای خروج: 0 پاسخ یا ناسازگاری اثبات‌شده؛ 2 ورودی/گزینهٔ نامعتبر؛ 3 جست‌وجوی ناقص یا پایان مهلت؛ 4 پوشش ناکافی در حالت صرفاً `certificate`.

## نمونهٔ جبههٔ q

ورودی ثابت `results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json` را با qهای 1، 2، 3 و 4 و نیز بدون `--q` اجرا کنید. نتایج ثبت‌شدهٔ نمونه: q=1 ناسازگار و کامل؛ q=2 یک افراز یکتا؛ q=3 و q=4 شش افراز مبهم؛ مدل نامحدود نیز شش افراز مبهم. این نتایج فقط به همین نمونه مربوط‌اند و q پنهان را تخمین نمی‌زنند. مثال `certificate_unique_q2.json` مسیر گواهی موفق و `empty_positive_with_unseen_symbol.json` حالت مثبت خالی و نماد دیده‌نشده را نشان می‌دهد.

## فرض‌ها، شواهد و وضعیت ممیزی

الفبا معلوم و نمادها بین عوامل جدا، k معلوم، بلوک‌ها ناتهی، برچسب‌ها دقیق و واژه‌ها کامل‌اند. نویز، نماد مشترک، معناشناسی پیشوندی و k ناشناخته پشتیبانی نمی‌شوند. مدل q محدود، زبان‌های محلی متناهی با سقف اندازه را می‌سنجد؛ مدل نامحدود سازگاری نمونه‌ای با عوامل منظم را می‌سنجد، نه شناسایی یکتای DFA مولد.

اثبات جست‌وجو در [EXACT_SEARCH_QOPPOSITION_PROOF_V2.md](general/EXACT_SEARCH_QOPPOSITION_PROOF_V2.md)، منطق fallback در [PUBLIC_CLI_FALLBACK_PROOF_V1.md](general/PUBLIC_CLI_FALLBACK_PROOF_V1.md)، و استدلال ساختاری در [PROOFS_SPARSE_Q_V2.md](structural/PROOFS_SPARSE_Q_V2.md) است. کدها: [public_cli_v1.py](general/public_cli_v1.py)، [known_k_qexact_v2.py](general/known_k_qexact_v2.py) و [sparse_certificate_v2.py](structural/sparse_certificate_v2.py). آزمون مستقل مجموعهٔ کامل جواب‌ها هنوز در حال اجراست؛ تا انتشار گزارش gate، این نامزد README ادعای تأیید مستقل یا آمادگی نهایی نمی‌کند.
