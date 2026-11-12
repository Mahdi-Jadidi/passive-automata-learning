# Exact full-contract candidates: bounded V33 evaluation

**Release candidate — independent final integration review pending. The hybrid was audited in a separate later round.**

**Result:** the audited subset-DP and forced-pair graph methods preserve the specified full sample-consistency contract by the cited mathematical arguments, and both were faster on some measured synthetic cases. A separately audited hybrid combines their structural strengths with the C030 singleton certificate; it has the same exact guarantee, not greater mathematical certainty. No method wins universally against C030. Evaluate the hybrid as an experimental structural dispatcher; keep C028 as the existing public default pending broader workloads, production engineering and independently measured resource behavior. No public default was changed.

## What was solved and proved

For declared ordered finite opaque IDs, finite positive and negative complete words (including ε), independent unbounded regular factors and AND acceptance, the requirement is the entire C028 result: compatible count C, maximum block count k*, optimal count O, uniqueness statuses, up to the first two lexicographic original-alphabet RGSs in both families, factors and first-rejecting-block indices. Empty alphabet, duplicates, unused IDs, contradictory labels, input validation, interrupted status and witness replay matter. These are properties of sample-compatible models, not physical truth.

The [DP candidate](../candidate_dp/candidate.py) uses anchored subset/negative-coverage DP: its coefficient for k counts k-block partitions exactly, because every partition has one block containing the least remaining ID. For witness order it tests RGS prefixes by assigning future IDs to already-open blocks before applying the DP to new blocks; exact feasible-prefix tests and lexicographic traversal give the first two full RGSs. [Proof and complexity](../candidate_dp/PROOF.md). It uses exponential state/transition resources, and repeated prefix queries may be expensive; Python recursion exhaustion is INCOMPLETE.

The [graph candidate](../candidate_graph/candidate.py) contracts proven must-link components. If their partition itself passes the compatibility test, all and only its coarsenings are compatible, giving C=Bell(q), k*=q, O=1; otherwise it enumerates all component partitions. Ordering components by first symbol appearance makes expansion preserve full-RGS lexicographic order even for interleaved components. [Proof](../candidate_graph/PROOF.md), [independent review](../candidate_dp/REVIEW_GRAPH.md). Fallback can still require Bell(q) tests plus graph preprocessing; no general speed guarantee follows.

All three candidates delegate every explicit `max_candidates` call to frozen C028 and thus preserve its candidate-prefix budget, including invalid-budget and zero behavior. Unlimited completed calls use the same schema and witness semantics. Caught interruption is not an exact answer; an uncatchable hard stop may produce no output. DP checks the reference dependency hash at import; graph imports a local C028 copy, so its frozen dependency hash matters. Neither implementation has a new public default.

## What was independently checked

The [independent audit](../audit/AUDIT_REPORT.md) reports that C028, C030 combined, DP and graph each matched a separate set-insertion oracle's entire serialized output on **2,275 cases**, plus **17** budget/schema comparisons each. Five deliberate checker mutations were detected. These are bounded tests and source reviews, not a proof for every input. On the separate timing cases, the twelve full result objects per case agree across all four solvers and all repeats; those larger timing cases are cross-implementation comparisons, not independent oracle proofs. The [DP source review](../audit/DP_SOURCE_REVIEW.md), [graph source review](../audit/GRAPH_SOURCE_REVIEW.md), and [timing protocol review](../candidate_dp/REVIEW_BENCHMARK_PROTOCOL.md) record their exact scopes.

The original four-solver timing corpus was locked before execution and contains ten synthetic cases, not real-trace workloads. There were 120 distinct trials: ten cases × four solvers × three fresh child processes, cyclic solver order, with a 20-second outer process cap. All completed with matching full outputs. CPython 3.12.14, Windows 11, 8 logical processors and the recorded Intel64 processor were used; see [environment](../audit/timing_environment.json). No memory measurement was made. Three repetitions, short calls, scheduling, host load and synthetic case selection limit inference.

## Measured medians

Seconds, median of three. **Solve time** includes all per-call preprocessing, counting, canonical witness reconstruction and replay; imports and JSON serialization are excluded. Values are rounded to six decimals. C028 is the unchanged baseline; C030 is the prior combined optimization.

| Synthetic case | C028 | C030 | DP | Graph |
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

**Startup-inclusive wall time** covers process launch, imports, solve, JSON serialization and capture; it is subject to OS scheduling. It is not the same as per-call solve time.

| Synthetic case | C028 | C030 | DP | Graph |
|---|---:|---:|---:|---:|
| empty_all_8 | 0.340596 | 0.310673 | 0.321701 | 0.307924 |
| all_compatible_10 | 1.977485 | 0.268162 | 0.393561 | 0.295429 |
| oneblock_8 | 0.410830 | 0.355092 | 0.277780 | 0.282218 |
| ties_8 | 0.423691 | 0.334276 | 0.271124 | 0.354597 |
| reverse_9 | 0.957613 | 0.717374 | 0.406216 | 1.138394 |
| reverse_10 | 4.664777 | 2.408910 | 0.482329 | 4.708055 |
| overlap_8 | 0.514128 | 0.428148 | 0.376607 | 0.548160 |
| repeated_projections_9 | 2.193265 | 0.369677 | 0.497097 | 0.357190 |
| long_words_4 | 0.360541 | 0.384231 | 0.383282 | 0.382676 |
| many_words_3 | 0.381207 | 0.390741 | 0.412112 | 0.388025 |

For `reverse_10`, median C030 solve time divided by DP solve time is approximately **15.3×**; C028 divided by DP is approximately **33.2×**. For `oneblock_8`, C030 divided by graph is approximately **89.4×** and C028 divided by graph approximately **168×**. These are ratios of medians for those cases, not averages or universal speedups. Conversely, for `all_compatible_10`, DP's median solve is approximately **425×** C030's and graph is slightly slower than C030; graph is slower than C028 on `reverse_9` and `overlap_8`. Small absolute solve times and differing startup-inclusive rankings caution against overinterpreting large ratios.

## Reproduction, verification and limitations

The hybrid source review, correctness and later-round timings are described below. The exact recorded original child commands, outputs, statuses and both nanosecond timers are in [raw trials](../audit/timing_raw.jsonl); [summary](../audit/timing_summary.json) and [locked protocol](../audit/PROTOCOL.md) describe aggregation and caps. From the repository root, `py results/2026-11-13/exact_candidates_v33/integration/recompute_medians.py` **reads the frozen files only**: it verifies source, reference, corpus and raw hashes; checks the 120 original and 30 later hybrid trial identities, complete statuses and full-object equality; independently recomputes 100 medians and compares them with the recorded summaries. It does not run solvers or reproduce benchmark timings. Its captured output is [RECOMPUTED_TABLES.txt](RECOMPUTED_TABLES.txt). To repeat benchmark execution rather than recalculate these frozen measurements, preserve the original raw artifacts and follow the [audit harness and protocol](../audit/PROTOCOL.md); the raw records contain the actual child commands. The harness refuses to overwrite its raw output.

The protocol review notes that stdout/stderr capture is not byte-bounded despite the protocol's wording, and that the summary's handling of hypothetical process-OK but incomplete result statuses needs care. Neither condition affected these trials, which all returned completed matching results. The graph's imported baseline copy was independently hash-matched, although the timing harness does not itself enforce that dependency hash in each child. The exact frozen sources and evidence are bound in [the manifest](MANIFEST.md).

## Hybrid: separately executed later round

The [frozen hybrid](../candidate_dp/hybrid/candidate.py) tries C030's singleton certificate, then the graph component certificate, then the full DP. Its [composition proof](../candidate_dp/hybrid/PROOF.md) preserves the same completed result, not stronger certainty; its [independent source review and correctness gate](../audit/HYBRID_REVIEW.md) passed all 2,275 oracle cases and 17 budget/schema checks. The component shortcut is used only after the whole component partition passes compatibility. All dependency files are hash-checked at import; a missing or changed dependency prevents import. Duplicate validation and graph preprocessing are real costs on fallback.

The locked ten-case corpus was then run **later**, three fresh child processes per case, 20-second outer cap. All 30 completed and all full outputs matched the earlier C028 results. This round was not interleaved or randomized with the original four-solver run; differences in load and time mean cross-round ratios and win counts are descriptive, not controlled causal estimates. Route labels below come from a separate untimed predicate diagnostic, not timed instrumentation. Values are median seconds; startup includes launch, imports and serialization.

| Synthetic case | Route | Hybrid solve | Hybrid startup-inclusive |
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

Across these separate rounds hybrid's solve medians were lower than prior C030 on 6/10 and prior C028 on 9/10 cases, without implying that selection would replicate on another run. In `oneblock_8`, hybrid was 0.001072 s versus prior C030 0.069321 s, whereas in `repeated_projections_9` it was 0.001907 s versus prior C030 0.001523 s. On `reverse_10` the hybrid was 0.210756 s versus prior DP 0.133426 s; added work and run-to-run variation cannot be separated by these measurements. Its import costs also make startup-inclusive outcomes different. See [hybrid raw trials](../audit/hybrid_timing_raw.jsonl), [summary](../audit/hybrid_timing_summary.json), [environment](../audit/hybrid_timing_environment.json), and [route diagnostic](../audit/hybrid_routes_stdout.json).

The major unresolved issue is representativeness: the two candidates have different favorable and unfavorable structures, and the full result contract—not just the optimum—must be maintained while measuring broader realistic workloads and memory. No unique physical partition follows from a sample optimum, and NP-hardness does not rule out exact finite computation.
