# M2 profile — small_choice, all optima

## Artifact and reproduction

This profile uses run [45593819618](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45593819618), job [139134561473](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45593819618/job/139134561473), and [artifact 15013931205](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45593819618/artifacts/15013931205). The archived ZIP was downloaded and SHA-256 checked against ebbdf7655c7dd6b8935783c12f3d1f2165c00c88f1afc15a366654f45af9dd11. The streamed normal.json is 1,399,367,871 bytes, SHA-256 9fb5f5bbc1c64e90bc955f73d2325a1d159224e91258e8a8758a34595102e2a7, Git blob e2f00717be846336b1f3287a8dd58070272434fd. The job compared optimized and resumed outputs by exact bytes and retained the normal output in the ZIP. The job's verifier logged VERIFIED, optimum cost 4 and 16 optima. Operational status is INCOMPLETE.

The workflow head is f8de4b6b14b3840d699d3c47ccc06a71eb5e04ae. The job checked out producer 391abf97df3b67661082c907d9ce20b4f69636c2 and independent verifier e1d022496f98bf50fd57d5ef3a7a0bc8194c817c. At both producer commits edr_search.py is blob 73da7bea551df73a8676b0adf0401cd7f2d307b5 and edr_bb.py is blob 657c4e0e4059b32cd9e6477e61c7a3673290f36d. The job's verifier file is blob a35281492e2677f0c57d8955227bc233d95492ea. The trusted scope has 12 declared symbols, identity root_owner, four positives and four negatives of length three, original positional IDs and an empty journal/2 event list. Input raw SHA-256 is 10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b.

From the repository root, with read access to the run:

~~~sh
gh run download 45593819618 -R Mahdi-Jadidi/passive-automata-learning \
  -n p3-m2-small_choice-all-expanded -D m2-evidence
python -B implementation/partition_feedback_final/research/p3-m3/profile_m2.py \
  m2-evidence > small_choice_all.profile.json
python -B -m unittest discover -s implementation/partition_feedback_final/research/p3-m3
python -B -O -m unittest discover -s implementation/partition_feedback_final/research/p3-m3
~~~

The scanner also accepts the original ZIP in place of the directory. It streams canonical node records, reconstructs owners as needed from the lexical node table and projects original tokens with the two versions' loop orders and early exits. It caches counts by exact owner and charges each call to its original source. Projection counters are a deterministic reconstruction of the recorded run. Verifier acceptance and runtime are from the archived run. The scanner handles this canonical format for diagnostics. It completed in 401.545 s on Windows with CPython 3.14 and was also checked against the tracked tiny_choice/all certificate (461 nodes, matching Git blob eafd651d28fc1f06f60bdbc4c0a4095a04dc390b). All nine offline tests passed in both normal and optimized modes.

To reproduce the expanded Actions validation on Linux, use separate checkouts of the exact producer and verifier commits above and run the workflow command from the producer checkout with a fresh output directory and CPython 3.13.5:

~~~sh
python -B implementation/partition_feedback_final/research/p3-m2/run_case.py \
  --case small_choice --mode all --proof-root /path/to/pinned-proof \
  --output m2-fresh --seconds 600 --memory-mib 13312 --entries 6000000
~~~

## Region and projection profile

| Disposition | Regions |
|---|---:|
| SPLIT | 199,257 |
| EMPTY | 4,275,365 |
| COST | 762,796 |
| EXACT_NO | 258,906 |
| FEASIBLE_MIN | 346 |
| **Total** | **5,496,670** |

The root accounts for one node. There are 5,297,412 pair children and 199,257 explicit residuals. Fanout excluding the residual ranges from 3 to 66, with mean 26.586. The modal split has 28 alternatives (123,235 splits). Depth 5 contains 3,573,815 nodes. The maximum edge depth is 10, consistent with the reported peak stack depth of 11. EMPTY children account for 77.78% of all records. Under the frozen rule, even a child known to violate an ancestor prefix is emitted and closed. The initial incumbent can improve during DFS, so the observed tree includes splits at base costs above the final optimum. See [the full per-depth and fanout histograms](small_choice_all.profile.json).

| Structural quantity | Producer | Independent verifier |
|---|---:|---:|
| Full compatibility calls | 259,252 | 259,253 |
| Distinct checked owners | 259,252 | 259,252 |
| Positive projection calls | 8,014,340 | 4,460,579 |
| Negative projection calls | 7,026,517 | 2,214,760 |
| Original tokens visited in projection loops | 45,122,571 | 20,026,017 |
| Negative membership lookups in positive projection set | 7,026,517 | — |
| Positive-negative projection pair comparisons | — | 4,460,579 |
| Reported total work units | 156,682,400 | 1,095,600,376 |

The producer checks each split owner once and uses that failed check to label the residual. The verifier checks the same 199,257 owners on their residual edges. Both phases also check 59,649 singleton EXACT_NO children and 346 FEASIBLE_MIN leaves. The verifier's only repeated full owner within its own phase is the incumbent check. The producer uses a positive-projection set per block and tracks remaining negatives. The verifier loops negative-first and stops at the first matching positive per attempted block. Its logged exact_checks counter is the inner pair-comparison count, while the producer's exact_checks counts full compatibility calls. The reconstruction matches both counters exactly. There can be at most 8 × (2¹²−1) = 32,760 distinct (trace ID, symbol block) projection keys on this fixture, so repeated projection work is present even with almost no repeated full owners. Work units come from different accounting rules and are shown separately.

## Serialization and peak memory

| Phase | Whole subprocess wall s | Producer internal elapsed s | Peak RSS (KiB) |
|---|---:|---:|---:|
| Normal producer | 188.458 | 125.512 | 6,766,704 |
| Optimized producer | 179.590 | 118.674 | 6,770,452 |
| Resumed producer | 184.590 | 123.256 | 6,766,836 |
| Normal independent verifier | 251.009 | — | 10,340,880 |
| Optimized independent verifier | 251.348 | — | 10,343,252 |

Wall and RSS above are from the artifact's summary.json, metrics and GNU time logs, on Ubuntu 24.04.5 with CPython 3.13.5. The expanded address-space limit was 13,312 MiB and the verifier input-byte cap was 2 GiB. These results use the expanded acceptance envelope. Producer internal elapsed includes search, per-entry JSON sizing and final ordered-table construction. The wall-minus-internal differences are 62.946 s, 60.916 s and 61.334 s, respectively. They include streaming JSON output plus runner/CLI startup, input, metrics, and process overhead. Direct write-only timing, verifier parse versus replay timing, and per-phase RSS peaks were unmeasured.

| Encoded content | Bytes |
|---|---:|
| EMPTY leaf payloads | 670,324,335 |
| All SPLIT payloads | 566,103,539 |
| Other leaf payloads | 157,442,616 |
| Delimiters and outer document fields | 5,497,381 |
| **Total** | **1,399,367,871** |

The EMPTY leaf payloads account for 47.90% of the raw file. Inside the split payloads, 5,297,412 cursor records occupy 367,476,040 bytes including array brackets and separators, and the matching children arrays occupy 136,816,784 bytes on the same basis. Together the arrays account for 36.04% of the full certificate, excluding the field names. These bytes are already included in SPLIT payloads. The cursor log repeats each child path also present in the children array and child node, and repeats the merge pair from the edge.

The producer keeps the complete node table and visited set in memory during search, then creates a sorted list of node references and streams it with json.dump. Its reported peak frontier_bytes of 1,177,958,379 charges canonical OPEN children and cursor records at admission plus residuals. It is an accounting value distinct from retained-object memory, final proof size and process RSS. In the fresh normal run the admission path calls the small canonical encoder twice per child and once per residual (10,794,081 calls before other validation/encoding). The verifier reads the entire proof, decodes UTF-8 and parses a full object graph, builds an ID index, and reconstructs path state for each of the 5,496,670 nodes. It independently checks each emitted child and cursor record. The older 4M-entry run's verifier failed with MemoryError before checking any nodes. These source paths and the historical failure identify memory pressure points. The expanded run did not measure individual allocation contributions.

## Where reductions would come from

- **Node count and proof work.** The proposed cross-support rule has a concrete root witness on the fixture. N0=[6,7,8] and P2=[7,8,6] match after deleting {6}, and again after deleting {7,8}. With identity E, the complete cross family is [(6,7),(6,8)]. The M2 root emits all 66 pair children. A future root split with this witness would have two pair children plus its explicit conflict residual. This establishes the root fanout comparison only. Total node reduction, time and all-optima replay under M3 remain unmeasured. Compare variants on the same fixture, incumbent and caps with node and work counters separated from output and replay timings.
- **Structural work at fixed coverage.** Independently optimize verifier path reconstruction and measure the exact owner/trace-key reuse that the profile actually shows. Formally distinguish producer structural calls, verifier compatibility calls and verifier inner pair comparisons. Cached work must preserve raw scope and exact equality. Producer cache entries provide no verifier evidence.
- **Bytes and peak memory at fixed coverage.** The normal JSON member is 85,612,918 bytes compressed in the ZIP, a 16.35× ratio. Compressed transport can preserve the exact canonical bytes on decode. It leaves the current full-object memory requirement on replay. For later review, record reconstruction of redundant child paths/cursor fields and streaming or disk-backed replay as separate serialization experiments on the same node stream. Measure logical records, raw/compressed bytes, encoding and replay time, and RSS independently. Any grammar change requires a separate contract and validation. See [CROSS_SUPPORT_LEX_V1.md](CROSS_SUPPORT_LEX_V1.md) for the branching proposal.
