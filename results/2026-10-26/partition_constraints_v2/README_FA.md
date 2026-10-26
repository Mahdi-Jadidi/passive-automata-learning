# اجرای دور دوم افراز الفبا

این بسته سه روش دقیق `baseline`، `eager` و `lazy` را برای شمارش تمام افرازهای سازگارِ الفبای معلوم به دو بلوک ناتهی فراهم می‌کند. برچسب‌ها بدون نویز و زبان‌های محلی منظم و بدون کران حالت‌اند. نسخهٔ مبنا و کدهای اجرای C002-R1 ثابت‌اند؛ مرجع هش در `coordination/runtime_manifest.json` است.

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
| طرح و مسئولیت‌ها | [PLAN_FA.md](coordination/PLAN_FA.md)، [forks.json](coordination/forks.json) |
| ثبت مرکزی، رخدادها و شکست‌های تاریخی | [journal.jsonl](coordination/journal.jsonl) |
| مبنای ثابت و نسخهٔ اصلی | [baseline/](baseline/)، [baseline_manifest.json](coordination/baseline_manifest.json) |
| کد و تلاش‌های اولیهٔ روش A | [approaches/eager/](approaches/eager/) |
| کد و تلاش‌های اولیهٔ روش B | [approaches/lazy/](approaches/lazy/) |
| بازبینی متقابل | [REVIEW_A.md](approaches/lazy/REVIEW_A.md)، [REVIEW_B.md](approaches/eager/REVIEW_B.md) |
| ساده‌سازی ردشده با مثال نقض | [REJECTED_IDEAS.md](approaches/lazy/REJECTED_IDEAS.md) |
| ممیزی موتور مشترک | [ENGINE_REVIEW.md](audit/ENGINE_REVIEW.md)، [engine-review.json](audit/engine-review.json) |
| مجموعهٔ اصلی ثابت و منشأ تولید | [CORPUS_REPORT.md](audit/CORPUS_REPORT.md)، [manifest.json](audit/corpus/frozen_v1/manifest.json) |
| تلاش‌های مستقل و نسخه‌های محتوامحور | [audit/attempts/](audit/attempts/)، [audit/source_blobs/](audit/source_blobs/) |

تلاش‌های ناموفق و نسخه‌های پیش از اصلاح حذف نمی‌شوند. وضعیت علمی و وضعیت اجرای هر تلاش جدا ثبت می‌شوند. جزئیات تحویل و تصمیم مستر پس از تکمیل ممیزی در گزارش نهایی درج می‌شود.
