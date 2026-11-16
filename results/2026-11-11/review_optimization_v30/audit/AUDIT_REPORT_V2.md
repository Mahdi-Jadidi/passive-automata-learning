# C030 independent adversarial audit — final v2

Date: 2026-11-12. Independent audit of the proof-approved A/B implementation against frozen C028 and a separate recursive set-insertion oracle. Candidate/source files were not edited.

## Result

The corrected v2 correctness gate passed. The three candidate entry points (`solve_a`, `solve_b`, `solve_combined`) matched the independent oracle across all 2,271 unlimited records and matched the frozen C028 baseline on eight explicit-budget pairs and nine invalid-schema/budget pairs per variant. Comparisons covered the full serialized output: compatible and optimum counts, maximum, status, uniqueness, canonical recommendation, first two global and optimum witnesses, factor order, and normalized negative rejection-block references. Witnesses were replayed.

The B-only diagnostics passed: the 9-ID traversal caused 366 LRU evictions and 111 later insertions of evicted keys. Sequential disjoint-input solves remained correct. For the early-failure fixture, baseline checked 6 projections and memo B checked 10; both returned the same rejection result. The fixture has P={a,b}, N={ab,bb,abb}, partition {a}|{b}. The whole words are noncontradictory; `ab` projects to a seen positive in each block, so the baseline stops at the first negative while B computes all local rejection bits. The observed vectors were `{a}: (false,false,false)` and `{b}: (false,true,true)`.

All 48 fixed timing observations (eight inputs × baseline/combined × three repetitions) completed and matched the full oracle result, with no timeout. Each fresh process includes startup time. The cases are small; results vary by case and repetition, and the combined solver was slower on some cases. These measurements do not establish a general speedup or complexity bound.

This validates the reviewed exact optimizations on the frozen code and bounded corpus. The finite experiments do not replace the proof or establish a general runtime guarantee. The computed optimum is sample-derived; these results do not recover an unknown physical partition when the labels do not identify one.

## Preserved v1 harness failure

The first full candidate run completed its baseline, all three 2,271-case comparisons, budget checks, and invalid-input checks, then failed in the harness-only early-failure diagnostic. Its mistaken fixture used one positive `a`, negative `b` first, and one block `{a,b}`; `b` is correctly rejected there, so the diagnostic's assertion that the baseline returned `None` was wrong. No candidate defect was found. The exact v1 script, empty stdout, and raw traceback remain preserved as `verify_v28_oracle_v1_frozen.py`, `candidate_correctness_v1_stdout.txt`, and `candidate_correctness_v1_stderr.txt`. The corrected fixture was reviewed and frozen as v2 before the rerun; v1 files were not overwritten.

## Frozen sources and environment

- Candidate source SHA-256: `7501901c6de5d7bb78ffc60f152b818733e3bd4460c9a655b8d783f384e8fc2b`.
- C028 baseline SHA-256: `5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94`.
- Approved v2 harness SHA-256: `de3ff0e7e355396376b13dbc6f855edf22e995034b7ff858da04deb6efafabbb`.
- Timing fixture SHA-256 (unchanged from v1): `aced9d1a86f2498ae36be6adce72e083c43e0367cb0662a7d5b118b80a3eee9a`.
- Python 3.14.6, `C:\Users\Mahdi\AppData\Local\Python\pythoncore-3.14-64\python.exe`; Windows 11, build `10.0.26300`.

The complete pre-run hash/argv record is [FROZEN_MANIFEST_V2.json](FROZEN_MANIFEST_V2.json). It also preserves references and hashes for the reviewed proofs, source verdict, corrected diagnostic verdict, independent oracle, all fixture inputs, and v1 failure evidence.

## Commands and captured evidence

From the workspace root, with the interpreter above:

```powershell
python results/2026-11-11/review_optimization_v30/audit/freeze_manifest_v2.py
python results/2026-11-11/review_optimization_v30/audit/verify_v28_oracle_v2.py --go
python results/2026-11-11/review_optimization_v30/audit/run_timing.py
```

`freeze_manifest_v2.py` froze the v2 harness SHA and unchanged corpus before the candidate run. `candidate_correctness_v2_stdout.txt` records PASS counts; `candidate_correctness_v2_stderr.txt` is empty. `timing_results.json` contains every raw duration and full per-run result; `timing_stdout.txt` is the command summary and `timing_stderr.txt` is empty. The baseline-only oracle crosscheck is preserved in `baseline_oracle_v2_stdout.txt` (2,271 cases, PASS) and its empty stderr file.

The v2 harness stdout retains a legacy `candidate_calls: 0` field initialized for baseline-only mode; it is not an execution count. The same JSON explicitly reports `candidate_variants: 3` and per-variant case, budget, and invalid-case counts, which record the actual candidate invocations.
