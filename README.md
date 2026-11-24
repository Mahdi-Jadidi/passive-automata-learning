# Passive Automata Learning — research archive

## Latest delivery · 23 November 2026

The exact hybrid algorithm returns one compatible alphabet partition with a maximum number of blocks and an independently replayable certificate.

- [Current research status, results, and reproduction](implementation/partition_feedback_final/README.md)
- [English decision rules, proofs and evidence](output/pdf/Partition_Decision_Rules_Final_EN.pdf)
- [HDFS-1024 certificate](implementation/partition_feedback_final/evidence/hdfs_1024.json) and [eight-vertex path certificate](implementation/partition_feedback_final/evidence/cover_path_8.json)

```text
python -B implementation/partition_feedback_final/staged.py implementation/partition_feedback_final/example.json --transcript
python -B implementation/partition_feedback_final/verify.py implementation/partition_feedback_final/evidence/hdfs_1024.json
```

**Earlier checkpoint — 19 November 2026:** [V46 validation, claim ledger and reproduction](results/2026-11-19/teacher_v46/README.md) and the [standalone English paper](output/pdf/Certified_Maximum_Alphabet_Partitioning_Interactive_Teacher_V46_EN.pdf). The executable method remains [V45 interactive search with the unchanged manuscript teacher](results/2026-11-16/interactive_teacher_v45/README.md). The [16 November handoff](HANDOFF_NEXT_AGENT_2026-11-16.md) and its [execution plan](docs/CONTINUATION_PLAN_V46.md) document the input checkpoint for this work. Delivery branch `codex/teacher-handoff-v46`.

آخرین تحویل (۲۰۲۶/۱۱/۰۶): [C025: خروجی رویداد و ارزیابی تریس‌های ثبت‌شده](results/2026-11-05/real_trace_checkpoint_v25/RESEARCH_REPORT_FA.md) و [متن جلسه با استاد و دمو](results/2026-11-05/real_trace_checkpoint_v25/ADVISOR_BRIEF_FA.md). مدلِ آخرین خروجی و حل‌گر آزمایشی دقیق اضافه شد؛ ۴۲ حالت خارجی با مرجع مستقل تطبیق داشتند: ۳۲ مبهم، ۱۰ ناسازگار، هیچ‌کدام یکتا. نمونهٔ عملیاتی BGL و نمونه‌های شبیه‌ساز CAGE2/Baby جدا گزارش شده‌اند؛ استنتاج به الفبای حداکثر هشت‌نوعی محدود است.

`partition_events.py` ورودی آزمایشی C025 برای خروجی هر رویداد است. `partition.py` نسخهٔ عمومی C024 برای پذیرش AND کل کلمه باقی مانده است. [نتیجهٔ کارایی و ممیزی C024](results/2026-11-05/search_checkpoint_v24/RESEARCH_REPORT_FA.md) برای همان مدل معتبر است؛ کارایی این دو مدل مقایسه نشده است.

آرشیو خصوصیِ پژوهش یادگیری غیرفعال اتوماتا، کشف افراز الفبا، شناسایی‌پذیری، اثبات‌ها و مثال‌های نقض.

اجرای فعلی از ریشه: `python partition.py INPUT.json --seconds 5`؛ فقط اگر تعداد دستگاه‌ها معتبر و معلوم است، `--known-k 2` اضافه کنید.

- **[بستهٔ پیشین جلسه با استاد، C021](results/2026-11-04/advisor_package_v21/README_FA.md)** — ۱۹ اسلاید، متن صحبت و دموی اجراییِ مدل قبلی؛ نتایج تازه در C025 هستند.
- **[مقیاس‌پذیری با دستگاه‌های پرحالت، C020](results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md)** — نسخهٔ عمومی جدید، تا ۲۰ دستگاهِ ۱۰۲۴حالته، بهبودهای اندازه‌گیری‌شده و پسرفت کنترل کوچک.
- [آموزش نسخهٔ دارای قید تعداد](docs/ALGORITHM_TUTORIAL_FA.md) — مثال کامل، معیار تصویر، شمارش DP و روابط مالکیت.
- [پیش‌شرط‌های یکتایی با تعداد معلوم و ردِ آستانهٔ صرفِ تعداد تریس](results/2026-11-04/preflight_certificates_v19/README_FA.md)
- **[بهینه‌سازی دقیق و آزمون تریس‌های تولیدی، C018](results/2026-11-04/synthetic_gate_v18/RESEARCH_REPORT_FA.md)** — صحت مستقل، زمان‌گیری هم‌قرارداد و موارد ناتمام.
- **[سابقهٔ هدف LANCER و توقف پیشین](results/2026-11-04/lancer_case_study_v16/GOAL_FA.md)** — ارزیابی محدودِ داده و مدل به درخواست کاربر در C025 از سر گرفته شد؛ بازیابی کاملِ میزبان‌ها محقق نشده است.
- **[دروازهٔ اعلام قطعی: بررسی کفایت داده پیش از تحویل افراز](results/2026-11-04/partition_gate_v15/RESEARCH_REPORT_FA.md)** — یکتا، مبهم، ناسازگار و ناتمام با گواه مستقل.
- **[بازیابی گواهی‌شده با تعداد معلوم و بهینه‌سازی دقیق تریس بلند](results/2026-11-03/partition_recovery_v14/RESEARCH_REPORT_FA.md)** — شرایط بازیابی، سه نمونهٔ موفق و ضدنمونه‌ها.
- **[مولد دستگاه و تریس تصادفی، تعداد دستگاه ۱ تا ۲۰ و طول تا یک میلیون](results/2026-11-03/partition_random_dfa_v13/README_FA.md)** — کد، اثبات‌ها و ارزیابی حل‌گر دقیق C010.
- **[اثر طول تریس تا یک میلیون رویداد و تحلیل مرتبه](results/2026-11-03/partition_length_v12/RESEARCH_REPORT_FA.md)**
- **[بهینه‌سازی مجموعه‌های بزرگ، دور یازدهم](results/2026-11-03/partition_large_v11/RESEARCH_REPORT_FA.md)** — مقایسهٔ سه‌تکراری، بهبودها و پسرفت‌های سرعت/حافظه.
- **[حل‌گر بدون تعداد خارجی و گزارش دور دهم](results/2026-11-02/partition_unrestricted_v10/RESEARCH_REPORT_FA.md)** — اثبات امکان محاسبه، مرز ناممکنیِ بازیابی فیزیکی و کاهش جست‌وجو.
- [مثال و توضیح فارسیِ نسخهٔ بدون تعداد](results/2026-11-02/partition_unrestricted_v10/theory/USER_EXPLANATION_FA_v1.md)
- [اجرای نسخهٔ بدون تعداد](results/2026-11-02/partition_unrestricted_v10/README_FA.md)
- [پاورپوینت فارسیِ ارائه](results/2026-11-02/presentation_v1/output/Alphabet_Partition_Research_FA_v2.pptx)
- [راهنمای ادامهٔ پروژه و دورهای قبلی](START_HERE_FA.md)
- [راهنمای اجرای C009](results/2026-11-02/partition_coverage_v9/README_FA.md)
- [گزارش C009 و حدود تجربی](results/2026-11-02/partition_coverage_v9/RESEARCH_REPORT_FA.md)
- [اثبات‌های C009](results/2026-11-02/partition_coverage_v9/theory/PROOFS_v1.md)
- [مرز شناسایی مالکیت واقعی و مثال‌های نقض C008](results/2026-11-02/partition_identification_v8/RESULT_FA.md)

## چه چیزی در آرشیو است؟

آرشیو پروژه شامل `results/`، `output/`، فایل‌های ساخت و نسخه‌های میانی در `.build/`، و فایل‌های بایگانی‌شدهٔ قبلی است. وابستگی‌های نصب‌شدهٔ `node_modules/` و کش محلی `.cache/` در فضای کاری نگهداری می‌شوند. مسیرهای آزمایشیِ ناموفق، خروجی خام، کدهای نسخه‌دار، گزارش‌ها و اسلایدها حذف نشده‌اند. سند موجود در پوشهٔ دیگر پروژه با ثبت منشأ در `archive/external_sources/` آمده است. همهٔ شاخه‌های محلی Git نیز به مخزن ارسال می‌شوند. پوشهٔ داخلی `.git/` به‌صورت فایل بارگذاری نمی‌شود؛ تاریخچه از طریق خود Git منتقل می‌شود.

## دامنهٔ ادعای الگوریتم

حل‌گر فعلی افرازهای سازگار با برچسب‌های دقیقِ کلمهٔ کامل را برای عوامل مستقلِ منظم با الفباهای مجزا، بدون مجموعهٔ خارجیِ تعدادهای مجاز، محاسبه می‌کند. نسخهٔ C009 با قید تعداد نیز حفظ شده است. نتیجهٔ قطعی دربارهٔ مولد واقعی مشروط به درست‌بودن همین فرض‌هاست. مشاهده‌نشدن یک تریس، برچسب منفی نیست. شمارش افرازها، احتمال مالکیت فیزیکی نیست. پوشش همگانیِ صددرصدِ ساختار سخت‌افزاری از هر لاگ متناهی ادعا نمی‌شود.

نسخهٔ اجرایی C009 روی ۱۲۹ مجموعهٔ کامل افراز با مرجع مستقل تطبیق داشت؛ مورد ۱۴نمادیِ آزمون مقیاس ناتمام ماند. جزئیات و محدودیت‌ها در گزارش همان دور ثبت‌اند.

دور دهم: ۱۲۵ ورودی یکتا و سه کنترل، در مجموع ۱۲۸ فراخوانی، با کل خانوادهٔ مرجع برابر شدند. چهار آزمون ساختاریافته، از جمله ۶۴ نماد در هشت گروه اجباری و ورودی چهارنمادی با طول ۴۰۹۶، مستقل تأیید شدند. این دامنهٔ آزمون تضمین پوشش همهٔ داده‌های هم‌اندازه نیست. هر دادهٔ بی‌تناقض در مدل نامقید یک توضیح تک‌بلوکی دارد؛ شناسایی عمومیِ چند دستگاه واقعی بدون اطلاعات اضافه ناممکن است.
