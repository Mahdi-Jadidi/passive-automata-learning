# Current research handoff

## Contract and current state

Given ordered positive and negative words over a finite declared alphabet, return one compatible partition with the greatest number of blocks and an independent optimality certificate, or an infeasibility witness. Cost is alphabet size minus block count. The model has unbounded local states and preserves original negative IDs. A block separates a negative if its projection differs from every positive projection. With sufficient resources, the uncapped exact search terminates on finite inputs. Runtime and memory can grow combinatorially.

The current default checks singletons, pairs, two disjoint pairs, and a single triple before the exact merge search. It has no default time, query, pair-scan, or raw-witness cap. The optional --rank route runs exact witness-rank optimization after the pair checks. Use explicit budgets for controlled measurements. The solver and verifier entry points are staged.py and verify.py.

Reuse projection equalities as zero regions for the **same negative**. A witnessed incompatible coarsening lets the search retain an immediate crossing merge on at least one route to each compatible continuation. Compatibility evidence can supply a cheaper incumbent. A proven lower bound can close strict improvements. Predictions about useful queries or merges only determine their order. See [pseudocode and proofs](ALGORITHM_UNCAPPED_FA.md).

## Results to replay

| Case | Result | Evidence |
|---|---|---|
| HDFS-1024 | Verified 27 blocks, cost 2, two disjoint pairs | [Input and certificate](evidence/hdfs_1024.json) |
| HDFS holdout-1024 | Verified 27 blocks, cost 2, triple E20/E21/E4 and 26 singletons. All 406 cost-one alternatives carry a failure witness. | [Input and certificate](evidence/hdfs_holdout_1024_uncapped.json) |
| Eight-vertex path | Verified 12 blocks, cost 4, disjoint-support root bound | [Input and certificate](evidence/cover_path_8.json) |
| 10,000 distinct traces, 1,000 symbols | Reference optimum 14 blocks with minimum block size 22. Default solver was INCOMPLETE in a 30-second trial and emitted no certificate. | [Input](evidence/synthetic_10000_traces_1000_symbols.json) · [Trial](evidence/synthetic_10000_traces_1000_symbols_run.json) |

The earlier hybrid timing file is historical. In that run Holdout was incomplete at five seconds. The new triple certificate establishes the current answer and does not replace the old timing observation. The 2,529 historical inputs matched a direct reference on the uncapped default path. The uncapped rank route was tested on a focused case. Its full-suite run was stopped before completion. [Earlier timing records](evidence/timing.json) · [Earlier hybrid audit](evidence/hybrid_checks.json)

## Reproduce

Run from this directory. On Windows, py can replace python.

~~~text
python -B verify.py evidence/hdfs_1024.json
python -B verify.py evidence/hdfs_holdout_1024_uncapped.json
python -B verify.py evidence/cover_path_8.json
python -B stress_10000.py --seconds 30
~~~

The stress runner constructs the fixture in memory, validates its reference construction and prints JSON. It checks that the committed fixture matches the generator. It leaves the recorded trial untouched. Median and completion comparisons require fresh repeat runs in the same environment.

## Scale-test construction and next engineering task

The fixture has 9,014 positive and 986 negative length-two traces, all distinct. The intended groups are paths of sizes 22, twelve times 75, and 78. Each adjacent edge ab appears positive and ba appears negative. If a and b lie apart, on every block the projections of ab and ba agree. Thus each edge forces its endpoints together and all vertices of each path must be co-blocked. All positives are ascending pairs. Projecting a reverse negative onto its path block keeps both symbols in descending order and no positive projection equals that word. The 14 path blocks are therefore compatible and meet the upper bound on the number of blocks.

The single measured failure spent 27.429 seconds in pair scanning and about 2.571 seconds in singleton analysis. The solver had not reached general merge search. There are 499,500 possible pairs and the current scan recomputes projections across traces for each pair. The 30-second test establishes a practical failure at that budget. The constructed optimum is a reference proof, while the solver itself emitted no result or certificate.

**Start with a certified fast path for mandatory contractions.** Discover short projection-equality witnesses before broad pair scanning. In this fixture, the positive word ab matching ba on each of the two endpoint complements proves both endpoints must occur in a separating block for ba. Record witnesses and validated contractions using the existing certificate representation, then replay them from raw traces. Use sparse occurrence/count indexes to avoid scanning all word pairs when testing for these local witnesses. If contraction does not resolve the instance, continue the general exact route. Candidate ordering can change freely if every unexplored alternative still has a certified route or cutoff.

Acceptance criteria for that work are a replayable 14-block result on this committed input, matching the direct reference on the 2,529 historical inputs, and a new report measuring phase time, peak memory and time through independent verification. Preserve the original failed trial for comparison.

