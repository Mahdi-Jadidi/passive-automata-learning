## 7. Measured evaluation

All timings below are seconds. The main comparison uses ten fixed synthetic inputs, three fresh processes per method/case, a one-second solve budget and a separate one-second consumer budget. Imports and process startup are excluded. Incomplete results are censored outcomes, not slow successful solves. V43 and V45 are not equal-work internal implementations: V45 deliberately calls the exhaustive manuscript teacher.

| Case | V43 completed / 3 | V43 median | V45 completed / 3 | V45 median |
|---|---:|---:|---:|---:|
| empty_all_8 | 3 | 0.000249 | 3 | 0.001312 |
| all_compatible_10 | 3 | 0.000342 | 3 | 0.000887 |
| oneblock_8 | 3 | 0.001282 | 0 | - |
| ties_8 | 3 | 0.000816 | 0 | - |
| reverse_9 | 3 | 0.000841 | 0 | - |
| reverse_10 | 3 | 0.000990 | 0 | - |
| overlap_8 | 3 | 0.064751 | 0 | - |
| repeated_projections_9 | 3 | 0.000487 | 3 | 0.026824 |
| long_words_4 | 3 | 0.003210 | 0 | - |
| many_words_3 | 3 | 0.005322 | 0 | - |

The original concurrently run timing batch is retained but excluded from this table. Single-trial process peak working sets were measured separately for all twenty case/method pairs using Windows GetProcessMemoryInfo. They include Python/native imports and are not algorithm-only allocations; incomplete and completed runs do different work, so no memory superiority is claimed.

On the 2,261-case frozen-reference corpus, the new solver had a 0.03-second per-instance budget: 1050 OPTIMAL, 1209 INCOMPLETE, 2 INFEASIBLE. Every completed optimum/infeasibility result agreed with its reference and passed the consumer. The incomplete instances are not counted as correctness successes. This corpus run overlapped an initial benchmark batch and is not a clean timing experiment.

Four saved test-script runs passed: projection tests (three tests including all masks and 5,000-symbol words), teacher tests (six tests including thirty seeded Cartesian-join comparisons), exhaustive master tests through four atoms (16,384 covers and 64 pair assignments at four atoms), and certificate/cut tests (167 monotone families, 758 cuts, 5,218 preservation checks, an accepted fourteen-line DRUP trace, and tamper/boundary checks).

Two production interaction examples completed with accepted optimum certificates. The ordinary three-symbol example learned one cut; a separate model-dependent four-symbol diagnostic deliberately required two cuts and returned three blocks. The latter fixture is not an unbiased benchmark. Its initial generator incorrectly assumed identical SAT tie-breaking under different query sequences; that diagnostic issue and correction are preserved in history.

| Projection workload | Cached scanner median | Shared store median |
|---|---:|---:|
| 4 symbols, distinct | 0.030582 | 0.083067 |
| 4 symbols, repeated | 0.048554 | 0.080414 |
| 8 symbols, distinct | 0.081494 | 0.220631 |
| 8 symbols, repeated | 0.043687 | 0.078453 |

These twenty-four microbenchmark records include initialization and three repetitions per workload/method. Both methods cache masks; full-result and rejection checksums match. The prefix store shares representation and transformations, but Python DAG traversal and tuple materialization may cost more than direct scanning. No universal projection speedup is claimed.
