# V33 independent correctness and timing report

**Gate: PASS on the frozen bounded audit; no universal empirical correctness or speed claim.** Independent source/proof reviews: [DP](DP_SOURCE_REVIEW.md) and [graph](GRAPH_SOURCE_REVIEW.md). C028, C030 combined, DP, and graph matched the separate insertion-partition oracle's entire serialized output on 2,275 inputs apiece: 2,187 exhaustive ternary labelings, 60 seeded inputs, 24 prior edge cases, four metamorphic records. Each also matched C028 on 17 finite-budget/invalid-schema cases. Five output mutations were detected; the oracle's partition generator self-tested Bell(0..8), epsilon and opaque-ID collision cases. Full output includes counts, optimum, both first-two witness families, factors and first rejecting indices. The bounded oracle tests are not proof for all inputs. Logs and all inputs are preserved here. No repair round was needed.

The pre-locked [protocol](PROTOCOL.md) and [timing cases](timing_cases.jsonl) define 10 **synthetic** workloads; no licensed real-trace evidence is claimed. 120 trials = four solvers × ten cases × three, in separately spawned processes, 20-second outer cap; all completed. For each case the 12 full serialized outputs agreed. Solver time below is the median of three `perf_counter_ns` durations around the full in-process solve, including its preprocessing and witness construction but excluding import and JSON serialization. Startup-inclusive wall timings, raw per-trial data, commands, stdout/stderr and full result objects are in [summary](timing_summary.json) and [raw JSONL](timing_raw.jsonl). Windows 11, CPython 3.12.14, Intel64 Family 6 Model 142 Stepping 10, 8 logical processors; see [environment](timing_environment.json). No measurement of memory is claimed.

| Case | C, k*, O | C028 s | C030 s | DP s | Graph s |
|---|---:|---:|---:|---:|---:|
| empty_all_8 | 4140, 8, 1 | 0.058389 | 0.000258 | 0.020709 | 0.000317 |
| all_compatible_10 | 115975, 10, 1 | 1.674077 | 0.000272 | 0.115293 | 0.000346 |
| oneblock_8 | 1, 1, 1 | 0.130337 | 0.069321 | 0.021027 | 0.000776 |
| ties_8 | 3263, 7, 7 | 0.141113 | 0.052832 | 0.018720 | 0.110290 |
| reverse_9 | 21146, 8, 36 | 0.677949 | 0.380697 | 0.059851 | 0.788208 |
| reverse_10 | 115974, 9, 45 | 4.428326 | 2.042634 | 0.133426 | 4.382762 |
| overlap_8 | 1657, 6, 3 | 0.169095 | 0.085920 | 0.026334 | 0.210609 |
| repeated_projections_9 | 21147, 9, 1 | 1.805809 | 0.001523 | 0.077093 | 0.000890 |
| long_words_4 | 15, 4, 1 | 0.010494 | 0.005283 | 0.011858 | 0.008545 |
| many_words_3 | 1, 1, 1 | 0.008903 | 0.010060 | 0.009175 | 0.008107 |

On these instances graph's atom certificate is particularly effective for oneblock_8 and repeated_projections_9; it can be slower than C028 when atom contraction does not eliminate enumeration (reverse_9 and overlap_8). DP is substantially faster on the measured tied/reverse/overlap cases, but is slower than C030 and graph on the all-compatible shortcut cases and slower than C030 on long_words_4. The small three-run sample, OS noise, data distribution, m and n, and cross-case variability preclude universal rankings or asymptotic claims. Full output equality on timing cases establishes consistency between implementations for those cases, not independent oracle verification of the largest cases.

Frozen evidence SHA-256: correctness corpus `294B48B80DF5A15AA95DEBBBD14677FB26211DDB86E81EF0EE44AA29F5282927`; timing corpus `013E2B60DC1D5740D766A9B0F77C458C4FBB92F203EE67977F3FE7104B48215B`; protocol `CB1E4BA7EA259B1F6E74D244AAFE1E9EE5DDF5FEB5654A88F86CBCDDC40BE`; correctness harness `569AD6B48C4AF981399A54A6F0FD5A42FC4AC02A4ACAB35D31369E6227006C04`; timing harness `9EF280C6C608DDDCA3E711DFD70532F8FD968FC987EC646B196FF0E653C158E0`; raw `65A69BC5CD07A2D897E2171FAEDE6EC9EE9DD50774276BBA3970DDCE10E480EE`; summary `4729BB0E024AE793D5D00E821F52092BEF42701985EBF97E724317E60BCD66A1`. Candidate and baseline source hashes and runtime command are in [environment](timing_environment.json) and per-trial raw records. Source freeze hash for graph's baseline helper matches C028.

Biggest overlooked issue: all four solvers must deliver the same full serialized contract. Selecting only favorable cases, omitting startup times, hiding timeouts, or treating a replayed optimum as a proof of C/O or physical ownership would invalidate the comparison.
