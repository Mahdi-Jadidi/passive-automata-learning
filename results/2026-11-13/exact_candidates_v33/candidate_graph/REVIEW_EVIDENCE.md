# Independent validation of V33 timing evidence

Verdict: **PASS for raw-file integrity, trial completeness, full-output agreement, and recomputed per-case medians**, subject to the scope and limitations below. This is read-only analysis of recorded evidence, not another benchmark and not a proof of universal correctness or performance.

Independently parsed all 120 raw rows: exactly 10 cases × 4 solvers × 3 distinct repeats, every recorded status OK and exit code 0. Every case's 12 complete serialized result objects are identical, including factors and ordered witnesses; each parsed child stdout agrees with its stored result and timing. All 40 solve medians and 40 startup-inclusive wall medians match the summary. Each raw row's recorded source hash matches `source_hashes.json`, the current four source files, and the environment record. The timing corpus hash matches the protocol and environment. These checks establish internal consistency of retained evidence, not independent replay of the measurements or external authenticity of files.

Raw SHA-256 `65A69BC5CD07A2D897E2171FAEDE6EC9EE9DD50774276BBA3970DDCE10E480EE`; timing corpus `013E2B60DC1D5740D766A9B0F77C458C4FBB92F203EE67977F3FE7104B48215B`; timing summary `4729BB0E024AE793D5D00E821F52092BEF42701985EBF97E724317E60BCD66A1`; environment `4dbcdea6dbcf7dcd31fc52f923075ababdedc35208766da017f0b876aebc38f6`.

The following are median **solve seconds**, not process-startup seconds; order is fastest to slowest by median. Baseline columns permit direct comparison; a ratio is C028 or C030 median divided by the candidate median, so >1 favors the candidate. Three trials are insufficient to establish statistical significance, especially for close or sub-millisecond timings.

| Case | C028 | C030 | DP | Graph | Median order |
|---|---:|---:|---:|---:|---|
| empty_all_8 | 0.0583894 | 0.0002580 | 0.0207092 | 0.0003174 | C030, Graph, DP, C028 |
| all_compatible_10 | 1.6740766 | 0.0002715 | 0.1152929 | 0.0003455 | C030, Graph, DP, C028 |
| oneblock_8 | 0.1303368 | 0.0693214 | 0.0210267 | 0.0007756 | Graph, DP, C030, C028 |
| ties_8 | 0.1411126 | 0.0528318 | 0.0187203 | 0.1102902 | DP, C030, Graph, C028 |
| reverse_9 | 0.6779491 | 0.3806970 | 0.0598513 | 0.7882083 | DP, C030, C028, Graph |
| reverse_10 | 4.4283258 | 2.0426338 | 0.1334259 | 4.3827617 | DP, C030, Graph, C028 |
| overlap_8 | 0.1690945 | 0.0859204 | 0.0263338 | 0.2106090 | DP, C030, C028, Graph |
| repeated_projections_9 | 1.8058092 | 0.0015227 | 0.0770932 | 0.0008897 | Graph, C030, DP, C028 |
| long_words_4 | 0.0104944 | 0.0052834 | 0.0118575 | 0.0085450 | C030, Graph, C028, DP |
| many_words_3 | 0.0089026 | 0.0100601 | 0.0091750 | 0.0081074 | Graph, C028, DP, C030 |

DP median was lower than C028 on 8/10 cases and C030 on 6/10; Graph was lower than C028 on 8/10 and C030 on 3/10. These are descriptive case counts, not significance tests or a distribution-wide conclusion. For example, DP is 33.19× faster than C028 and 15.31× faster than C030 on `reverse_10` by the ratio of medians; Graph is 168.05× and 89.38× faster on `oneblock_8`, respectively. Conversely, Graph is 0.80× C028 and 0.41× C030 on `overlap_8`, i.e. slower by those inverse ratios. On the two empty/all-compatible cases C030 already has its singleton Bell shortcut, so large ratios against C028 should not be framed as a novel general graph advantage.

The child clock surrounds the complete `solve` call: normalization, graph/DP preprocessing, factor construction and replay are included; module imports and JSON serialization are outside it. The separately recorded startup-inclusive parent wall interval includes process launch, imports, solve, JSON serialization, scheduling and teardown; it is not startup overhead alone. All trials use an outer 20-second cap, with no timeout or error recorded. Source inspection and the retained logs do not independently establish machine idleness, randomization, peak memory, or environmental reproducibility. The fixed synthetic corpus is small and purposive, three trials per cell were used, and startup/load noise is material for very short solves. No result here supports a real-world or universal speedup claim. Finite full-output agreement is not a correctness proof; the separate audit supplies the bounded oracle checks.

Biggest overlooked issue: compare the full contract and preprocessing-inclusive solves against both C028 and the existing optimized C030, rather than reporting large baseline-only ratios or treating sub-millisecond ranks as stable.

