# اجرای دور دوم افراز الفبا

این بسته سه روش دقیق `baseline`، `eager` و `lazy` را برای شمارش تمام افرازهای سازگارِ الفبای معلوم به دو بلوک ناتهی فراهم می‌کند. برچسب‌ها بدون نویز و زبان‌های محلی منظم و بدون کران حالت‌اند. نسخهٔ مبنا و کدهای اجرای C002-R1 ثابت‌اند؛ مرجع هش در `coordination/runtime_manifest.json` است.

ممیزی نهایی برابری کامل baseline و eager در ۱۰٬۵۹۴ مورد و lazy در ۱۰٬۵۷۷ مورد را تأیید کرد؛ ۱۷ مورد lazy ناتمام بودند. مقایسهٔ مستقل ۱۲۰۰ کارِ برنامه‌ریزی‌شده را با ۹۹۹ خروجی کاملِ تأییدشده، ۵ پایان مهلت و ۱۹۶ کارِ انجام‌نشده به‌علت بودجه ثبت کرده است. eager جست‌وجو را کاهش داد، اما در این مجموعه بهبود عمومی زمان یا حافظه نشان نداد. [تصمیم مستر](MASTER_DECISION_FA.md) و گزارش‌های ممیزی مرجع تفسیر و محدودیت‌ها هستند.

روش پیش‌فرض `baseline` باقی می‌ماند. دو روش تازه از موتور مشترک Python با کتابخانهٔ استاندارد استفاده می‌کنند. نصب وابستگی لازم نیست. صورت‌بندی و حدود ادعا در [قرارداد](coordination/CONTRACT.md)، [اثبات A](approaches/eager/PROOFS.md) و [اثبات B](approaches/lazy/PROOFS.md) آمده‌اند.

از پوشهٔ همین بسته:

```powershell
python -B -X utf8 solver.py baseline/theory_structural_graph_gap.json --method eager --timeout-seconds 30
python -B -X utf8 solver.py baseline/theory_structural_graph_gap.json --method lazy --timeout-seconds 30
```

ورودی JSON شامل `alphabet`، `positive` و `negative` است. نمادها باید تک‌کاراکتری و تعدادشان بین ۲ و ۱۰ باشد. نمونه‌های مثبت و منفی نباید متناقض باشند. خروجی کامل همهٔ افرازها، زبان‌های متناهیِ تصویرهای مثبت و شاهدهای رد منفی‌ها را نگه می‌دارد. شاهد، محل‌های ممکنِ رد را نشان می‌دهد؛ مسئولیت واقعی عامل مولد را تعیین نمی‌کند.

کد خروج صفر یعنی شمارش کامل، ۲ یعنی ورودی نامعتبر و ۳ یعنی شمارش ناتمام. در خروجی ناتمام `complete=false`، `status=incomplete` و `feasible_partition_count=null` است؛ `found_partition_count` فقط کران پایین است. مهلت CLI تعاونی است. اجرای زیر مهلت سختِ فرایند و ثبت نسخه، دستور، محیط و خروجی خام را نیز فراهم می‌کند:

```powershell
python -B -X utf8 audit/capture.py example-eager --timeout-seconds 30 --source solver.py --source common/engine.py --source common/helpers.py --source baseline/partition_solver.py --source approaches/eager/eager_solver.py --source baseline/theory_structural_graph_gap.json -- python -B -X utf8 solver.py baseline/theory_structural_graph_gap.json --method eager --timeout-seconds 30
```

برای تکرار پژوهشی، از همان Python ثبت‌شده در manifest اجرای اصلی استفاده شود؛ دستور بالا از Python موجود در PATH استفاده می‌کند. هر فراخوانی capture شناسه و پوشهٔ تازه زیر `audit/attempts/` می‌سازد. ثبت عمومیِ فرایند ممکن است خروج ۳ را nonzero بنامد؛ تفسیر علمی باید JSON ناتمام را از خطای برنامه تفکیک کند.

## مسیر شواهد

| موضوع | مسیر |
|---|---|
| گزارش نهایی فارسی | [RESEARCH_REPORT_FA.md](RESEARCH_REPORT_FA.md) |
| تصمیم پایان دور و پیشنهاد ادامه | [MASTER_DECISION_FA.md](MASTER_DECISION_FA.md) |
| گزارش ممیز مستقل | [AUDIT_REPORT_FA.md](audit/AUDIT_REPORT_FA.md) |
| طرح و مسئولیت‌ها | [PLAN_FA.md](coordination/PLAN_FA.md)، [forks.json](coordination/forks.json) |
| ثبت مرکزی، رخدادها و شکست‌های تاریخی | [journal.jsonl](coordination/journal.jsonl) |
| مبنای ثابت و نسخهٔ اصلی | [baseline/](baseline/)، [baseline_manifest.json](coordination/baseline_manifest.json) |
| کد و تلاش‌های اولیهٔ روش A | [approaches/eager/](approaches/eager/) |
| کد و تلاش‌های اولیهٔ روش B | [approaches/lazy/](approaches/lazy/) |
| بازبینی متقابل | [REVIEW_A.md](approaches/lazy/REVIEW_A.md)، [REVIEW_B.md](approaches/eager/REVIEW_B.md) |
| ساده‌سازی ردشده با مثال نقض | [REJECTED_IDEAS.md](approaches/lazy/REJECTED_IDEAS.md) |
| ممیزی موتور مشترک | [ENGINE_REVIEW.md](audit/ENGINE_REVIEW.md)، [engine-review.json](audit/engine-review.json) |
| مجموعهٔ اصلی ثابت و منشأ تولید | [CORPUS_REPORT.md](audit/CORPUS_REPORT.md)، [manifest.json](audit/corpus/frozen_v1/manifest.json) |
| افزونهٔ ۳۰۷۲ مولد قبلی | [manifest.json](audit/corpus/legacy_generator_extension_v1/manifest.json) |
| خروجی‌های کامل و ناقصِ ممیزی گسترده | [summary.json](audit/correctness_runs/20261026T125503.860658Z_805e5494/summary.json) |
| اعتبارسنجی مستقلِ خروجی‌های ذخیره‌شده | [validation_report.json](audit/correctness_validation/20261026T133346.038161Z_8ba0e9bf/validation_report.json) |
| دفتر ۱۲۰۰ کار و خلاصهٔ کارایی | [jobs.jsonl](audit/benchmark_adopted/runs/serial_20261026T140000Z/jobs.jsonl)، [summary.json](audit/benchmark_adopted/runs/serial_20261026T140000Z/summary.json) |
| اعتبارسنجی مستقلِ مقایسه | [validation_report.json](audit/benchmark_validation/20261026T142254.406767Z_079436eb/validation_report.json) |
| اجرای دوبارهٔ مقایسه در مسیر تازه | [README.md](audit/benchmark_adopted/README.md) |
| کنترل سلامت بایت‌ها | [verify_integrity.ps1](coordination/verify_integrity.ps1) |
| تلاش‌های مستقل و نسخه‌های محتوامحور | [audit/attempts/](audit/attempts/)، [audit/source_blobs/](audit/source_blobs/) |

تلاش‌های ناموفق و نسخه‌های پیش از اصلاح حذف نمی‌شوند. وضعیت علمی و وضعیت اجرای هر تلاش جدا ثبت می‌شوند. `audit/run_correctness.py` نسخهٔ تاریخیِ ناموفق است و همراه لاگش حفظ شده؛ ادامهٔ موفق در `audit/run_correctness_resume.py` و بازبینی مستقل در `audit/validate_saved_correctness.py` ثبت شده‌اند. اعتبارسنجی مقایسه در `audit/validate_benchmark.py` است. برای بازخوانی شواهد موجود از validatorهای موفق استفاده شود؛ ساخت دوبارهٔ داده در مسیر frozen موجود مجاز نیست.

مهلت سخت ممکن است بدون JSON پایان یابد. payload ناقصِ اولین تلاش lazy پیش از ذخیره از دست رفت؛ فقدان آن صریحاً ثبت شده و اجراهای بعدی شاهد تازه‌اند. ثبت پایدارِ پذیرفته‌شده در `audit/capture.py` خروجی را مستقیماً در فایل می‌نویسد؛ نسخهٔ قبلی و بازبینی ناسازگاری نامزدها نیز محفوظ‌اند.
