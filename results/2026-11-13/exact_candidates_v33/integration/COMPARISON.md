# V33 comparison: same full-output contract

**Release candidate; independent final integration review pending.** All timings are synthetic, seconds, median of three; no memory was measured. The original four solvers ran in a cyclically interleaved matrix. The hybrid ran in a **later, separate** round, so its comparison to earlier medians is descriptive and subject to host/time variation. For interpretation and full proof/contract references see [REPORT_EN.md](REPORT_EN.md).

| Solver | Full-contract route | Measured strength and limitation |
|---|---|---|
| C028 | Exhaustive canonical enumeration, unchanged public baseline. | Baseline includes all counts and witnesses; Bell-number search can dominate. |
| C030 combined | Singleton-compatible Bell certificate, otherwise memoized enumeration. | Very fast on singleton-compatible cases; can remain enumeration-bound. |
| Subset DP | Coverage-state count plus exact RGS-prefix feasibility and reconstruction. | Strong on tied/reverse/overlap cases; exponential memory/time and large regressions versus C030's singleton certificate are possible. |
| Graph | Forced-pair components; Bell certificate when the component partition passes, otherwise exhaustive component enumeration. | Strong when components prove a compact family; preprocessing and fallback can be slower than C028. |
| Hybrid | Singleton certificate → compatible-component certificate → full DP fallback. | Same exact contract; extra validation/preprocessing and import hashes can cost time. Separate-round timings, no universal win. |

## Original interleaved comparison: solve medians

| Case | C028 | C030 | DP | Graph |
|---|---:|---:|---:|---:|
| empty_all_8 | 0.058389 | 0.000258 | 0.020709 | 0.000317 |
| all_compatible_10 | 1.674077 | 0.000271 | 0.115293 | 0.000345 |
| oneblock_8 | 0.130337 | 0.069321 | 0.021027 | 0.000776 |
| ties_8 | 0.141113 | 0.052832 | 0.018720 | 0.110290 |
| reverse_9 | 0.677949 | 0.380697 | 0.059851 | 0.788208 |
| reverse_10 | 4.428326 | 2.042634 | 0.133426 | 4.382762 |
| overlap_8 | 0.169095 | 0.085920 | 0.026334 | 0.210609 |
| repeated_projections_9 | 1.805809 | 0.001523 | 0.077093 | 0.000890 |
| long_words_4 | 0.010494 | 0.005283 | 0.011857 | 0.008545 |
| many_words_3 | 0.008903 | 0.010060 | 0.009175 | 0.008107 |

## Later hybrid-only round

| Case | Route | Solve | Startup-inclusive |
|---|---|---:|---:|
| empty_all_8 | singleton | 0.000377 | 0.532513 |
| all_compatible_10 | singleton | 0.000316 | 0.399042 |
| oneblock_8 | component | 0.001072 | 0.399125 |
| ties_8 | DP fallback | 0.024445 | 0.390750 |
| reverse_9 | DP fallback | 0.073849 | 0.426905 |
| reverse_10 | DP fallback | 0.210756 | 0.637503 |
| overlap_8 | DP fallback | 0.040375 | 0.436272 |
| repeated_projections_9 | singleton | 0.001907 | 0.436702 |
| long_words_4 | singleton | 0.008098 | 0.399478 |
| many_words_3 | component | 0.009387 | 0.413561 |

The original startup-inclusive medians are in the [English report](REPORT_EN.md#measured-medians). Every full serialized result matched within each case across 120 original and 30 later completed trials. The later hybrid solve medians were below the earlier C030 medians on 6/10 and C028 on 9/10; these counts are descriptions of separate rounds, not controlled paired outcomes. The C030 and hybrid singleton differences can be sub-millisecond and should not be promoted into a universal ranking. All solvers were separately checked against the independent insertion oracle on 2,275 cases and against the reference for 17 budget/schema cases each. Correctness tests and measured performance have different evidentiary scope.

Recompute from frozen raw files, without running solvers: `py results/2026-11-13/exact_candidates_v33/integration/recompute_medians.py`. Raw records and source hashes are in [manifest](MANIFEST.md). Keep C028 default unchanged; evaluate the hybrid experimentally and assess representative workloads, memory and deployment requirements before any promotion.
