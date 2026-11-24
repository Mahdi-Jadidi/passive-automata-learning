# Benchmark provenance inventory

Baseline commit: `7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6`. All paths below relative to `implementation/partition_feedback_final/`. Git blob SHA-1 identifies the exact committed bytes (including Git blob framing); these are connector-verified blob IDs, not raw-file SHA-256. Compute raw SHA-256 on checkout and extracted input bytes at run time. No benchmark archive has been fabricated.

## Pinned baseline source (read through GitHub)

| File | Git blob |
|---|---|
| sample.py | 8a31d44903256ff5faff6e6724124e854efda474 |
| model.py | ea78e9300efd121ae79441cc46c7062dfee5af9f |
| hybrid.py | 2b02597633f3fda707144029385f6aef09d8cede |
| staged.py | 51f044a907f7d0d9e4cc3d70b4cca89ac5c5b7a0 |
| search.py | c61b84623ded7325fc7ff154db131d09115120e7 |
| verify.py | dd376cae9ba57d75a69d9a1b48c9e2337ce8a40b |
| audit.py | a50d903aae68f7e2699ec507262a149f905b9369 |
| compact.py | 2885cea5cc1dd1f37209a1a08aa93359fbd01a13 |
| experiments.py | 0ebd29767156e62e930cee90447d3234037dac71 |
| stress_10000.py | a50077da8abe3b9dca03047ab608cbe0bcc98c3e |

## Available committed fixtures and historical records

| Path | Git blob | Content |
|---|---|---|
| evidence/hdfs_cases.json | 94674b572b943638c79b39f8d071f78612a12541 | Eight raw input objects: hdfs_16/64/128/512/1024, hdfs_holdout_128/512/1024 |
| evidence/hdfs_1024.json | d34d4dd85b751d716fcabc5a66a1150a6784770d | Bundle, 29 symbols, 1024 positive + 1024 negative |
| evidence/hdfs_holdout_1024_uncapped.json | 13af0aef0bd603a287f5246f2dbe1170b6862895 | Input/result bundle |
| evidence/cover_path_8.json | 6d273e2e7874a4470bf1f0f5874c44cfd1dc3d25 | Bundle, 16 symbols, 8 positive + 7 negative |
| evidence/rank_order.json | ccf9c7a9cf0eb03f3d07897e78270bab8801364c | Bundle, 2 symbols; input identical to smoke order |
| evidence/rank_triple.json | f9dbc4b8f4f14f489e2452a8a1f03f4fbf780592 | Bundle, 3 symbols; input identical to smoke triple |
| evidence/exam_multi.json | 997b07574504781a4f4c796c35e41960208240c | Bundle, 3 symbols, duplicate negatives |
| evidence/synthetic_10000_traces_1000_symbols.json | 33b1210e495db29b22333053fe5ad077e345b8e1 | Raw input, 1000 symbols, 9014 positives + 986 negatives |
| evidence/synthetic_10000_traces_1000_symbols_run.json | 8c4d8329fd371457ecc6cb885de59e2c22bddcec | Historical 30-second INCOMPLETE trial |
| evidence/timing.json | f53311505f88c5ff68d8e24788e37fa414b6b554 | Historical timings, not paired with current host |
| evidence/hybrid_checks.json | b78c6fb9281b5f027a72433c2cae4b88ba428391 | Historical regression counts |

Historical unrestricted structural costs: HDFS-1024 and holdout 2, cover-path-8 4, synthetic 986. The synthetic cost is a construction/reference result, not a completed pinned producer result. The enhanced scale archive has a different implementation (reverse contractions); do not mix its 0.109s/0.319s measurements with this pin.

## Planted and enhanced archives — not recovered here

The master handoff and R01/R03/R04 mention `partition-scale-improved.zip` (numbered variants), `partition-benchmark-lite.zip`, two full planted benchmark parts, `ALL_MEASUREMENTS.csv/json`, `PLANTED_REPORT_FA.md`, `planted_30s/summary.csv`, `planted_extra/summary.csv`, `planted_high_memory/summary.csv`, `representation_probe.json`, and `root_replay_results.json`. Raw archive bytes, complete file inventory and checksums unavailable in this runtime. The historical collection had 33 distinct samples / 41 runs: 19 OPTIMAL, 14 INCOMPLETE, 8 MEMORY_LIMIT; 17 VERIFIED. These counts are historical and not re-executed.

Named fixtures reported in R01 include huge_long_active, huge_reverse_unused, huge_sparse_small, huge_singleton_active, large_reverse_dense, large_reverse_pairs, small_count, extra_interleaved, extra_long_1024, extra_imbalanced_negative, extra_imbalanced_positive. This is a partial list, not the full suite manifest. Never recreate a missing original by guessing a generator or assign guessed checksums. Once archives are restored, hash each original archive, each raw input, and each reference independently; store source archive/member path and generator seed/version if provided.

## Isolation policy

Only exact three-key raw sample JSON enters a selector process. Ordered positive and negative arrays preserve row identities, duplicates, empty words and original token strings. Bundle input and result are extracted into separate directories. Planted groups, specs, expected costs, old certificates, generator construction state and reference labels must remain evaluation-only, never arguments or features of a selector. This is logical input isolation, not an adversarial OS filesystem sandbox. Keep benchmark source and results outside the immutable baseline checkout.
