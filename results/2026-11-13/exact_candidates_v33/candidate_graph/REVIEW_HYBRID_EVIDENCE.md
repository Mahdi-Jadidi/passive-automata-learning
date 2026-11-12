# Independent validation of appended hybrid evidence

Verdict: **PASS for internal consistency of recorded hashes, all 30 hybrid trials, full-output agreement, and recomputed solve and parent-wall medians.** This is read-only analysis of retained files; it is not a rerun, an external authenticity guarantee, a correctness proof or a general speed claim.

The 30 records cover the ten frozen cases with three distinct repeats each, all `OK` with exit code zero and the frozen hybrid source hash. Each stored child stdout agrees with its parsed elapsed time and full result. For each case, all three hybrid full results equal all twelve prior full results, including status, counts, recommendation, ordered witnesses and factor serialization. All ten solve and ten startup-inclusive wall medians match the summary; prior solver medians copied into that summary match the original summary. Route labels match the separately recorded untimed predicate replay; those labels are diagnostic, not instrumented observations of the timed processes.

The unchanged original raw SHA-256 is `65a69bc5cd07a2d897e2171faede6ec9ee9dd50774276bba3970ddce10e480ee`; hybrid raw is `6c369e0380eca99c4d68f0917a395b5f2d07abcee3182d5866065fcd3d4c4dd2`; hybrid summary is `ee54c41d572ce14b26ccb0de5b6cf48d10da54d6fc25419e2b7d8e5535903694`. The source is `6377ccd75281567be11af5820ae52668612a069240c31d2a5aee0cf4f1022063`, proof `27094f9595d2f04034718667712098839b8d882c970491c81e297e5c348bb219`, and frozen timing corpus `013e2b60dc1d5740d766a9b0f77c458c4fbb92f203ee67977f3fe7104b48215b`; source/corpus hashes match the environment record, and the original raw hash matches both earlier summary and hybrid environment. The retained correctness log separately reports PASS for 2,275 oracle cases and 17 budget/invalid checks; this review did not rerun those tests.

| Case | Hybrid solve median (s) | Hybrid parent wall median (s) | Earlier C028 solve (s) | Earlier C030 solve (s) | Earlier DP solve (s) | Earlier graph solve (s) |
|---|---:|---:|---:|---:|---:|---:|
| empty_all_8 | 0.0003768 | 0.5325135 | 0.0583894 | 0.0002580 | 0.0207092 | 0.0003174 |
| all_compatible_10 | 0.0003161 | 0.3990417 | 1.6740766 | 0.0002715 | 0.1152929 | 0.0003455 |
| oneblock_8 | 0.0010722 | 0.3991254 | 0.1303368 | 0.0693214 | 0.0210267 | 0.0007756 |
| ties_8 | 0.0244445 | 0.3907502 | 0.1411126 | 0.0528318 | 0.0187203 | 0.1102902 |
| reverse_9 | 0.0738486 | 0.4269048 | 0.6779491 | 0.3806970 | 0.0598513 | 0.7882083 |
| reverse_10 | 0.2107557 | 0.6375034 | 4.4283258 | 2.0426338 | 0.1334259 | 4.3827617 |
| overlap_8 | 0.0403745 | 0.4362720 | 0.1690945 | 0.0859204 | 0.0263338 | 0.2106090 |
| repeated_projections_9 | 0.0019066 | 0.4367019 | 1.8058092 | 0.0015227 | 0.0770932 | 0.0008897 |
| long_words_4 | 0.0080979 | 0.3994782 | 0.0104944 | 0.0052834 | 0.0118575 | 0.0085450 |
| many_words_3 | 0.0093874 | 0.4135610 | 0.0089026 | 0.0100601 | 0.0091750 | 0.0081074 |

Hybrid runs were **sequentially appended after** all four earlier solver runs, not interleaved or randomized against them. Host load, thermal and scheduler variation can therefore explain part of observed differences; three repeats are too few for significance claims. Solve time includes validation, certificates, preprocessing, fallback, witness generation and replay but excludes imports/hash checks and JSON serialization. The parent wall measurement includes process startup, imports/hash checks, solve, serialization, scheduling and teardown; it is not startup overhead in isolation.

For `all_compatible_10`, hybrid solve median is about 0.316 ms, yet parent wall median is about **399 ms**; the earlier C028 parent-wall median is about 1,977 ms. The roughly 5,296× ratio of solve-only medians against C028 is therefore not a 5,296× end-to-end speedup: the measured parent-wall ratio is about 5×, itself subject to the sequential-run caveat. C030's earlier solve median was about 0.272 ms, showing the singleton shortcut was already available. Very short measurements are especially sensitive to overhead and noise. These ten synthetic cases and finite checks do not establish broad performance or physical-truth recovery.

Biggest overlooked issue: solve-only ratios omit fixed process/import/serialization cost, and later sequential trials confound solver differences with host variation.
