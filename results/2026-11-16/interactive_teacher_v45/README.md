# V45 — interactive partition search with the unchanged manuscript teacher

This is a separate research implementation. V43 and V44 are preserved. The supplied `main.pdf` is copied unchanged in `sources/`; the new reference implements its Sections 5.1–5.3 without changing the exhaustive local-table or forest-conditioning algorithm. No fast substitute teacher, symmetry-breaking enumeration, or partial-table acceptance is activated.

## Run the API

Use a fresh Python process, putting this directory first on `sys.path` (the historical versions also use flat module names):

```python
import sys
sys.path.insert(0, 'results/2026-11-16/interactive_teacher_v45')
from optimizer import solve_optimal, solve_profiled
from verify import verify_optimal
D = {'alphabet':['a','b','c'],
     'positive':[['c','b','a']],
     'negative':[['a','b','c'],['b','a','c']]}
profile = solve_profiled(D, {'timeout_seconds':30})
result = profile['result']
if result['status'] in ('OPTIMAL','INFEASIBLE'):
    print(verify_optimal(D,result,{'timeout_seconds':5}))
print(result)
```

The result retains `status, blocks, max_devices, certificate`. New general proof type is `teacher_cut_drup`. `INCOMPLETE` has null mathematical result fields and is not a rejected candidate. Existing V43 consumers do not support this new proof type; use this version's consumer. The local pinned Windows PySAT/Glucose dependency remains `results/2026-11-14/sat_candidate_v37/vendor`. Python 3.12 is used in the recorded runs.

## Components and boundaries

- `teacher_main.py`: literal bounded fixed-partition teacher; complete original local tables are cached externally across calls, while each join uses fresh working tables. Caller parameters are the sufficient positive-trie state counts. This restriction is proved equivalent to unrestricted sample compatibility, not imposed as a true-device state ceiling.
- `projections.py`: shared exact prefix representation, cached-superset projection and per-mask labelled images; no repeated construction for an already cached mask.
- `optimizer.py`, `master.py`: maximizing candidate generation, external failure explanation, maximal false-region cover cuts and incremental SAT. No full W_i mining and no fallback to V43.
- `verify.py`: direct witness checks and deterministic CNF/DRUP checking; it imports no teacher, projection store or native solver. Shared normalization/atom/master code remains trusted.
- `PROOF.md`: correctness, projection identity, safe contraction, cut progress/soundness, optimum and certificate proofs.

## Evidence and results

`summary.json` and `EVALUATION.md` aggregate saved records. This validation checks stored results; it is not an independent rerun. Reproduce experiments only in a fresh copy/output location because scripts generally use exclusive output creation. `experiments.py` also creates the diagnostic example; preserve ALL existing evidence before rerunning. `summarize.py`, PDF building and rendering intentionally regenerate their derived outputs.

```powershell
python results/2026-11-16/interactive_teacher_v45/run_tests.py
python results/2026-11-16/interactive_teacher_v45/audit.py
python results/2026-11-16/interactive_teacher_v45/experiments.py
python results/2026-11-16/interactive_teacher_v45/memory_measurements.py
python results/2026-11-16/interactive_teacher_v45/two_cut_demo.py
python results/2026-11-16/interactive_teacher_v45/projection_benchmark.py
python results/2026-11-16/interactive_teacher_v45/summarize.py
python results/2026-11-16/interactive_teacher_v45/build_pdf.py
python results/2026-11-16/interactive_teacher_v45/render_qa.py
python results/2026-11-16/interactive_teacher_v45/freeze.py
```

- All four saved test scripts passed. Master checks cover all pair assignments and cover sets through four atoms. Region checks cover 167 monotone families, 758 cuts and 5,218 preservation checks. Teacher tests include thirty comparisons against the raw Cartesian join of local tables, cache immutability, cycles, positive-forced zeros, interruptions and DFA witness replay.
- On the frozen 2,261-case corpus with a **0.03-second** limit each: **1,050 OPTIMAL, 2 INFEASIBLE, 1,209 INCOMPLETE**. All 1,052 completed results matched the reference and were accepted by the consumer. Incomplete cases are not passes or proofs of infeasibility. This run overlapped an initial benchmark batch and supplies correctness/resource evidence, not clean timing.
- Clean comparison: 60 fresh-process trials, ten synthetic cases and three repetitions for each method, one-second solve limits. V43 completed all thirty runs; V45 completed nine, corresponding to three easy cases. The first contended batch is preserved separately and excluded from timing tables. Twenty process-peak memory measurements are separate single-trial records.
- Production examples with one and two successive rejection cuts completed with accepted optimum certificates. The two-cut input was model-dependent by design, not an unbiased benchmark. Its corrected fixture-generator issue is preserved in `history/`.
- All 24 projection microbenchmark records have matching full-result and rejection checksums. The current prefix-store implementation was **slower** than the dictionary-cached scanner in all four median workload comparisons. Sharing was implemented; general speedup was not demonstrated.
- The faithful teacher is the main bottleneck. The final ordinary example call alone enumerated over one million named DFA representations. No internal teacher optimization was made in response.

`REVIEW_CUTS.md` and `REVIEW_PROJECTIONS.md` are AI-assisted Terra reviews, not independent scientific peer review. The review's duplicate-literal proof-checker concern was fixed in the new consumer; no teacher logic changed. Original reviewer text is retained.

## Optional change is not applied

`PROPOSED_TEACHER_CHANGE_NOT_APPLIED.md` gives a concrete, proved restricted feasibility-adapter proposal. It would not preserve all the manuscript's behavior-query interfaces and requires explicit user approval before implementation. **The current production solver continues to use the exhaustive reference teacher.**

No suitable whole-trace AND-model field data are available, as confirmed by the user; valid field trials remain zero. No universal speedup, scientific-first novelty or defect-free software claim is made.

English article: `output/pdf/Interactive_Partition_Learning_Unchanged_Teacher_V45_EN.pdf` from repository root. Its source, builder, page renders and layout QA are retained here. `manifest.json` hashes source/evidence/PDF and `release_checks.json` confirms frozen V43 and user PDF integrity.

## گزارش فارسی

نسخهٔ تعاملی پیاده شد: بهترین کاندیدای افراز پیشنهاد می‌شود، تیچرِ مطابق مقاله پاسخ می‌دهد و از هر شکستِ کامل‌شده یک قید عمومی استخراج می‌شود. نمونهٔ دوم دو بار پاسخ منفی گرفت و سپس جواب بهینه با گواه تأییدشده داد. تیچر را سریع‌تر یا جایگزین نکردیم. آزمایش‌ها نشان دادند شمارش DFA در همان تیچر گلوگاه جدی است و کشِ پیشوندی فعلی نیز در ریزآزمون‌ها سریع‌تر نبود. این نسخه فعلاً جایگزین سریع‌ترِ V43 معرفی نمی‌شود. پیشنهاد تغییر محدود و نیازمند تأیید شما جداگانه مستند شده و اجرا نشده است.
