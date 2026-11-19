## 6. Experimental methods and results

Trials were sequential. V43 and V45 ran in separate fresh Windows x64 CPython 3.12.14 processes for each timed trial. The pinned Glucose3 backend was supplied by python-sat 1.9.dev22. Both solver calls had 60-second cooperative limits, with independent 60-second consumer limits. First trials were run for all ten fixed V33 cases per solver. Initial completions received two further trials with alternating method order. Censored first trials were not duplicated. Solve times below exclude startup and standalone consumer time and include any in-solver proof self-check. Each group shows completed/attempted; a median is shown only with repeated completions. The corpus correctness/resource audit used one V45 process at 0.25 seconds per input and a 2-second consumer limit. This is not a representative workload timing comparison.

**Corpus.** Of 2,261 inputs, 1,245 were optimal, 2 infeasible and 1,014 incomplete. All 1,247 completed outputs matched the frozen exhaustive reference and passed the V45 checker. The corpus contains 2,187 labelings of seven small two-symbol words, four empty-alphabet boundaries, ten fixed cases, and 60 seeded small cases. The historical 0.03-second audit yielded 1,052 checked completions and 1,209 incomplete results. Its concurrent workload makes it unsuitable as a controlled timing baseline.

**Fixed cases.** First trials finished for V43 on 10/10 and V45 on 6/10 cases. All completed results passed their own consumers and matched the frozen optimum. The historical clean one-second values were 10/10 and 3/10, respectively. The case labels describe synthetic workloads and carry no population-level performance claim.

| Fixed case | Optimum | V43 finished / trials | V43 median (s) | V45 finished / trials | V45 median (s) |
|---|---|---|---|---|---|
| empty_all_8 | 8 | 3/3 | 0.00043 | 3/3 | 0.00205 |
| all_compatible_10 | 10 | 3/3 | 0.00056 | 3/3 | 0.00200 |
| oneblock_8 | 1 | 3/3 | 0.00252 | 0/1 | — |
| ties_8 | 7 | 3/3 | 0.00163 | 3/3 | 16.44911 |
| reverse_9 | 8 | 3/3 | 0.00122 | 3/3 | 13.03583 |
| reverse_10 | 9 | 3/3 | 0.00181 | 3/3 | 26.67107 |
| overlap_8 | 6 | 3/3 | 0.11028 | 0/1 | — |
| repeated_projections_9 | 9 | 3/3 | 0.00069 | 3/3 | 0.05435 |
| long_words_4 | 4 | 3/3 | 0.00343 | 0/1 | — |
| many_words_3 | 1 | 3/3 | 0.01230 | 0/1 | — |

**Fixtures.** All three outputs passed the checker and a direct partition-enumeration oracle. Every recorded cut was replayed from the input against its preceding rejected proposal. The two-cut input was selected using the solver model order and is a diagnostic.

| Fixture | k | Cuts | Proof lines | Solve (s) |
|---|---|---|---|---|
| ordinary | 2 | 1 | 0 | 14.591 |
| two_cut | 3 | 2 | 0 | 31.843 |
| ab_ba | 1 | 0 | 0 | 14.063 |

**Censoring.** The first censored V45 case in fixed order was preselected by rule for one 300-second solve escalation. Other 60-second censored cases were retained without extra runs. Named-DFA progress below counts the final teacher call only. The bound is the last reported local-table bound. A dash indicates that the recorded telemetry does not identify the active block size.

| Case | Limit (s) | Outcome | Bound | Symbols | Named DFAs in final call |
|---|---|---|---|---|---|
| oneblock_8 | 60 | INCOMPLETE | 10 | 8 | 349,336 |
| overlap_8 | 60 | INCOMPLETE | 4 | 2 | 824,132 |
| long_words_4 | 60 | INCOMPLETE | 52 | 1 | 236,108 |
| many_words_3 | 60 | INCOMPLETE | 8 | 1 | 248,314 |
| oneblock_8 | 300 | INCOMPLETE | 10 | 8 | 4,401,840 |

Complete local enumeration scales were oneblock_8 ≈ 10^83.0, overlap_8 ≈ 10^6.0, long_words_4 ≈ 10^104.9, many_words_3 ≈ 10^9.6 named representations. These sizes describe the enumeration space. The progress counts are affected by short-circuiting on positive traces, so they do not directly predict finish time.

V43 median worker startup was 1.286 s and median standalone checking time was 0.00158 s on completed trials. Process peak working sets ranged from 27.1 to 27.8 MiB. The raw records retain per-trial counters and evidence for censored runs.

V45 median worker startup was 1.441 s and median standalone checking time was 0.00879 s on completed trials. Process peak working sets ranged from 27.3 to 28.1 MiB. The raw records retain per-trial counters and evidence for censored runs.

**Projection microbenchmark.** Both methods used identical mask lists and the historical seeded corpus and checker. Each row is a median of three paired repetitions. All projection, witness and rejection digests matched. Times include build, query and digest work. The historical V45 prefix store lost all four comparisons.

| Alphabet size | Requests | Scanner (ms) | Prefix store (ms) |
|---|---|---|---|
| 4 | distinct | 130.249 | 287.374 |
| 4 | repeated | 294.679 | 556.568 |
| 8 | distinct | 285.090 | 726.276 |
| 8 | repeated | 162.442 | 190.154 |

**Independent execution checks.** {{REVIEW_RESULTS}}

The fixtures’ zero-line proof logs are valid when the reconstructed base formula at threshold k+1 already yields a unit-propagation conflict. The mutation campaign also used a nonempty, 14-line solver proof.
