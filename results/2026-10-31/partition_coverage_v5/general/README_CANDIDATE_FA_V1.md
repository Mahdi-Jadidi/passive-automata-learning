# جست‌وجوی دقیق و گواهی تنک C005

## اجرا از ریشهٔ workspace

پس از قرارگرفتن wrapper ریشه‌ای `solver.py`، فایل را از ریشهٔ workspace اجرا کنید. wrapper باید آرگومان‌ها را به `results/2026-10-31/partition_coverage_v5/general/public_cli_v1.py` منتقل کند. برای نمونه:

```powershell
$PythonExe = 'C:\Users\Mahdi\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $PythonExe -B -X utf8 solver.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode exact --q 2 --max-solutions all
& $PythonExe -B -X utf8 solver.py results/2026-10-31/partition_coverage_v5/general/examples/certificate_unique_q2.json --mode certificate --q 2
& $PythonExe -B -X utf8 solver.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode hybrid --q 2
```

برای اجرای مستقیم همین CLI در شاخهٔ چرخه:

```powershell
& $PythonExe -B -X utf8 results/2026-10-31/partition_coverage_v5/general/public_cli_v1.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode exact --q 2 --max-solutions all
```

## انتخاب حالت

- `exact` حالت پیش‌فرض است. اگر `--q` حذف شود، مدلِ عوامل منظمِ نامحدود اجرا می‌شود. اگر `--q N` داده شود، زبان محلی هر عامل حداکثر N رشته دارد. بدون `--max-solutions` حداکثر دو جواب برای تشخیص ابهام برگردانده می‌شود؛ `--max-solutions all` همهٔ افرازهای سازگار را می‌شمارد.
- `certificate` به `--q` نیاز دارد. فقط وقتی گواهی رنگ‌آمیزی یکتای گراف q-opposition را دارد، جواب یکتا می‌دهد. اگر پوشش کافی نباشد، `insufficient_coverage` برمی‌گرداند؛ این وضعیت به معنی ناسازگاری داده نیست.
- `hybrid` ابتدا گواهی تنک را امتحان می‌کند و فقط برای `insufficient_coverage` جست‌وجوی دقیق همان مدل q را اجرا می‌کند. هر دو مرحله از یک مهلت مطلق مشترک استفاده می‌کنند. اگر مرحلهٔ گواهی `incomplete` شود، جست‌وجوی دوم شروع نمی‌شود.
- `--no-q-opposition` فقط در حالت دقیق پذیرفته می‌شود و برای مقایسهٔ همان ورودی با و بدون قیود q-opposition است.

## خروجی و وضعیت‌ها

هر جواب شامل بلوک‌های الفبا، تصویر مثبت‌های هر بلوک و برای هر منفی یک شاهد مستقیم از تصویری است که در تصویرهای مثبت همان بلوک وجود ندارد. فهرست جواب‌ها افرازهای بدون ترتیب را گزارش می‌کند.

`complete` و `enumeration_complete` نشان می‌دهند جست‌وجو تمام شده است. `decision_complete` می‌تواند با یافتن یک جواب درست باشد، حتی اگر برای شمارش همهٔ جواب‌ها هنوز کار مانده باشد. بنابراین با `--max-solutions 1` ممکن است `status=found`، `complete=false` و `uniqueness=unknown` باشد. وضعیت `unique` تنها پس از پایان جست‌وجو با دقیقاً یک افراز داده می‌شود؛ دو افراز برای اثبات `ambiguous` کافی است.

کدهای خروج:

- `0`: جواب یا ناسازگاریِ اثبات‌شده در مدل انتخاب‌شده
- `2`: ورودی یا گزینهٔ نامعتبر
- `3`: جست‌وجوی ناقص یا مهلت تمام‌شده
- `4`: گواهی تنک در حالت `certificate` پوشش کافی نداشته است

## نمونهٔ جبههٔ q

برای مقایسهٔ qهای مختلف روی یک ورودی ثابت، همین فایل را جداگانه با qهای 1، 2، 3 و 4 اجرا کنید و سپس `--q` را حذف کنید:

```powershell
& $PythonExe -B -X utf8 solver.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode exact --q 1 --max-solutions all
& $PythonExe -B -X utf8 solver.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode exact --q 2 --max-solutions all
& $PythonExe -B -X utf8 solver.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode exact --q 3 --max-solutions all
& $PythonExe -B -X utf8 solver.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode exact --q 4 --max-solutions all
& $PythonExe -B -X utf8 solver.py results/2026-10-31/partition_coverage_v5/general/examples/q_frontier_sample.json --mode exact --max-solutions all
```

خروجی ثبت‌شده برای همین نمونه: q=1 بدون افراز سازگار و کامل؛ q=2 یک افراز یکتا؛ q=3 و q=4 هرکدام شش افراز و مبهم؛ مدل نامحدود نیز شش افراز و مبهم. این‌ها نتایج کلاس‌های اعلام‌شده برای نمونه‌اند و q پنهان را حدس نمی‌زنند.

نمونهٔ `certificate_unique_q2.json` گواهی موفق q=2 را نشان می‌دهد. `empty_positive_with_unseen_symbol.json` قراردادِ نمونهٔ مثبت خالی و نمادِ دیده‌نشده در حالت جست‌وجوی دقیق را نشان می‌دهد.

## فرض‌ها و مرزها

الفبا باید معلوم و نمادها بین عوامل جدا باشند؛ k معلوم است و بلوک‌ها ناتهی‌اند. برچسب‌ها دقیق‌اند و واژه‌ها کامل هستند. نمادها نویزدار، مشترک بین عوامل یا پیشوندی نیستند. k ناشناخته یا تعیین مولد پنهان ادعا نمی‌شود. حالت q محدود دربارهٔ زبان‌های متناهیِ محلی با سقف اندازه است؛ حالت نامحدود سازگاری نمونه‌ای با عوامل منظم را می‌سنجد و شناسایی یکتای DFAهای پنهان را تضمین نمی‌کند.

اثبات قیود و رابط در [EXACT_SEARCH_QOPPOSITION_PROOF_V2.md](EXACT_SEARCH_QOPPOSITION_PROOF_V2.md) و منطق fallback در [PUBLIC_CLI_FALLBACK_PROOF_V1.md](PUBLIC_CLI_FALLBACK_PROOF_V1.md) آمده است. کد provider برای جست‌وجوی دقیق در [known_k_qexact_v2.py](known_k_qexact_v2.py) است.
