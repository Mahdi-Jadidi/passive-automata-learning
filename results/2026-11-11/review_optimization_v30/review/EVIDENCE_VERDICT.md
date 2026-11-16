# C030 independent audit evidence review

Biggest overlooked point: timing includes a fresh Python process startup in every measurement and cannot establish a general solver speedup. The proof concerns exact sample results; bounded tests do not prove absolute implementation correctness or physical ownership.

Frozen manifest V2 SHA-256 F5BBA25C2A620057975DC42F88C4DAB44B0A93A056D622B5BA93EA7EB648E659: all 20 referenced on-disk file hashes independently recomputed and matched. Its argv names approved `verify_v28_oracle_v2.py --go`; original V1 harness and failing stdout/stderr are preserved, and 8 timing fixtures remain unchanged from V1. Candidate SHA 7501901C6DE5D7BB78FFC60F152B818733E3BD4460C9A655B8D783F384E8FC2B; baseline SHA 5F60B27447B37EC07F1FD6BCE75BE6199B898573D4B32E90413E900E3A615A94. The original pre-GO log is superseded after harness edits, and the V1 diagnostic fixture assertion failure is not represented as a successful full gate.

Correctness stdout SHA 247AB8EDCD70A758B26335A67425798380AD39B860A6C059EA40433CADC36BEA records 2,271 complete comparisons for EACH of A, B and combined, plus 8 budget and 9 invalid cases per variant; LRU 366 evictions, 111 reinsertions; corrected valid fixture early failure 6 vs 10 projections. Raw JSON field `candidate_calls: 0` is an invalid stale baseline-only counter initialized and never updated in the harness; do not use it as an actual execution count. Per-variant counters and source loops record actual candidate comparisons. Five synthetic mutations checked are narrowly reported as such.

Timing raw results SHA 293BCF3F28FFF57AF23AD8696877891E7724A18A7E2797783A167D499B33D442: independently recomputed all eight independent-oracle expected complete outputs and checked all 48 stored full results, zero mismatches, all PASS; independently recomputed all 16 displayed medians from three observations each. Process wall time includes startup and input/output, not just solver execution. No memory metric and no A-only/B-only timing was measured.

| Frozen timing case | Baseline median ms | Combined median ms |
|---|---:|---:|
| singleton_no_observations_m8 | 439.404 | 432.257 |
| singleton_compatible_m5 | 341.864 | 448.983 |
| forced_nonadjacent | 380.250 | 392.920 |
| tied_nontrivial_optimum | 398.191 | 365.890 |
| memo_repeated_masks | 403.224 | 407.596 |
| memo_early_failure | 464.284 | 370.816 |
| long_many_words | 406.641 | 387.091 |
| general_no_shortcut_m7 | 382.877 | 361.366 |

These values are observations from three repetitions and are noisy; slower medians occur as well as faster ones. The evidence does not establish a uniform speedup, attribution to A vs B, general runtime bound, or measured memory reduction. AUDIT_REPORT_V2.md SHA C9B13DE714998751B65937DE277E8BCC3D6F345F7695A96A3014F3CA8240098E correctly preserves the V1 failure, source and timing scope and stale counter disclosure. This independent evidence check is by a coordinated AI agent, not a formal proof assistant or human reviewer.
