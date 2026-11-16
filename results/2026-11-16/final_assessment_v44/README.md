# Final assessment V44 / English article

The implemented optimizer is frozen in `../exact_optimizer_v43/`. This folder adds a proof-oriented English manuscript, explicit Boolean construction, a restricted-family superiority theorem, further encoding checks, real-data readiness assessment and reproducible PDF generation.

- `ARTICLE_EN.md`: full article source; seven theorems, two lemmas, operational algorithm and explicit CNF appendix.
- `CLAIM_STATUS.md`: proved statements, tested properties, trust boundaries and unmet requirements.
- `encoding_audit.jsonl`: 100 seeded samples; 15,664 pair-assignment/threshold checks.
- `encoding_checks.jsonl`, `encoding_replay_instances.jsonl`: fresh replay with all 15,664 individual actual/expected outcomes.
- `structural_family_raw.jsonl`: nine generated ab/ba-family instances, up to 256 symbols, all accepted certificates.
- `field_readiness.json`: actual BGL provenance and labels; **zero valid AND-model field experiments**.
- `FIELD_DATA_LIMITATION.json`: user confirmation that suitable field data are currently unavailable; field validation remains deferred.
- `assessment.json`: read-only evidence checks and environment metadata.
- `manifest.json`: SHA-256 digests of code, source, raw evidence and final PDF; excludes itself and image renders.
- `pdf_layout_qa.json`, `rendered/`: every page rendered and boundary-checked; final pages inspected visually.
- `REVIEW_PROOFS.md`, `REVIEW_EVIDENCE.md`: two Terra low-effort AI-assisted reviews; findings and resolutions are recorded in the claim ledger. These are not independent peer reviews.

Final PDF: `../../../output/pdf/Certified_Maximum_Component_Alphabet_Partitioning_EN.pdf`.

Rebuild using Python with ReportLab, pypdfium2, pdfplumber and Pillow installed (Windows fonts are embedded):

```powershell
python results/2026-11-16/final_assessment_v44/build_pdf.py
python results/2026-11-16/final_assessment_v44/render_qa.py
python results/2026-11-16/final_assessment_v44/assess.py
```

The experiments below use exclusive output creation to protect existing evidence. Preserve old evidence before intentionally rerunning. Structural-family timings will be new observations, rather than the frozen timings:

```powershell
python results/2026-11-16/final_assessment_v44/check_encoding.py
python results/2026-11-16/final_assessment_v44/check_encoding.py --detailed
python results/2026-11-16/final_assessment_v44/structural_family.py
python results/2026-11-16/final_assessment_v44/field_readiness.py
```

The main benchmark remains the V43 raw file: four methods, ten synthetic inputs, three fresh processes each, all 120 optimal and checked. V43 is faster on some structures and slower on others. Neither universal superiority, first-in-literature novelty, defect-free software nor successful real field validation follows from this artifact. See the claim ledger for the precise limits.

## گزارش کوتاه

نسخهٔ اجرایی دقیق و مقالهٔ انگلیسی آماده است. اثبات مراحل، بهینگی، گواه، آزمون‌های صحت و مقایسه در ریپو ثبت شده‌اند. روش همهٔ افرازها را در حلقهٔ بیرونی نمی‌شمارد و از انقباض اجباری، شاهدهای کمینه و SAT افزایشی استفاده می‌کند. برتری همگانی ثابت نشده؛ برتریِ اثبات‌شده محدود به یک خانواده در برابر خط مبنای مشخص است. دادهٔ میدانیِ دارای برچسب پذیرش/رد کل تریس هنوز موجود نیست. نوآوری نهایی و صحت بدون نقص نرم‌افزار نیازمند بررسی مستقل/تأیید رسمی‌اند.
