# Benchmark workstream — issue #4

Status: PARTIAL CHECKPOINT, ready for review of reference harness; full legacy and planted replay still blocked. No integration merge or deployment. Branch: research/v2-benchmarks; base: research/selector-v2.

## 2026-11-25 — milestone log

Read issue #4, PROJECT_HANDOFF.md and SELECTOR_V2_INDEX.md under implementation/partition_feedback_final, and benchmark-relevant sections of four research reports. Verified pinned baseline commit 7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6. Repository connector reads/writes succeeded; local git ls-remote failed with 'Could not resolve host: github.com'. No local checkout or enhanced/planted archives available. No live external protocol or service. Work restricted to benchmarks/v2 and this file.

| Checkpoint | Commit | Evidence |
|---|---|---|
| Isolated harness | fafd2a9c17f125e7df6d9e5deb84fcd8efa756f6 | Separate producer/replay workers; strict raw schema; pinned checkout gate; RSS/AS/time, local simulator instrumentation, bounds and censored outcomes |
| Regression tests | 777097c122e68ff8e3769ae6c03993e479c58b7a | python -B -m unittest -v test_harness: 4 tests PASS (0.055 s), 250 seeded + 8 targeted, Bell counts and rejection cases |
| Smoke command | 3f7212f15af605513f51b9633c6dacf6234dd94d | Generates input-only samples and saves summaries |
| Measured smoke | 76f8236c691938f759cf3e302c49652b9ac336ca | 6 OPTIMAL, 2 INFEASIBLE; all 8 independently VERIFIED, 1 censored TIMEOUT |
| Inventory | 10324c516249c40b920f480e08184968358222e5 | Git-verified source and fixture blob IDs; archive provenance and missing checksums explicitly flagged |
| Reproduction docs | ad31a3c9790a726f3654a73c127cc295fd5db94b | Linux commands, resource definitions, extraction isolation and limitations |
| Exact runner repeat | 2ab383ad4c7fa14c93002297944a4d78198e80be | python -B smoke.py smoke-repeat: 8 VERIFIED, 1 TIMEOUT, same costs/statuses; repeat CSV |

Remote Git blob hashes matched locally executed harness.py (2fe8790651e357ebb124f5abfd53d2c1c2ab230e), test_harness.py (99ad6c03ec3b25f9d1798306b26761325138d70e), smoke.py (edc0aeb57412fb0e2123af0ab1799df77aa7a983). Local SHA-256 harness c2adf934e1f2e5444a74d96c4bff82b1dde65adb872d907a9be8d703f3de576f; tests 28991f53fd7022a24822e972fee7b0d7708b8d052973c2c3de5895155f94a644. CSVs are measured reference experiments, not timings of staged.py or v2. On both repetitions, all local simulator counters and external counters were zero. No ACCEPT from external service; operational status INCOMPLETE. Reference path4 compute 0.00328/0.00418 s; independent replay 0.03259/0.03599 s. Other details in CSVs; wall time and RSS reported separately. No memory-limit run or full legacy query telemetry validation yet.

## Open gates

1. On a clean local pinned Git checkout, run legacy adapter and compare its observed query counts to producer transcript and test interrupted attempts. Run HDFS, holdout, cover path, 1000-symbol scale at explicit 5/30 s and 1536 MiB AS caps. Preserve historical records and newly measured results separately.
2. Restore raw planted and enhanced archives; inventory all inputs, checksums and references separately. No reconstructed data masquerading as original.
3. Extend telemetry to shared v2 schemas after core/interface integration (certified partial bounds/gaps, frontier, receipts, actual wire sizes). Current runner deliberately does not claim partial bounds for legacy INCOMPLETE.
4. Controlled repeats and ablations after integration and proof gate. External service and bounded mode remain owner-confirmed contract dependencies.

Review limitation: local source simulator runtime instrumentation is not tested end-to-end in this runtime. Reference smoke verifies the harness subprocess/replay and logical isolation only; it is not a security sandbox. No claim of production-scale benchmark completion. Timeout smoke depends on host speed and one-second startup allowance; censored worker RSS is null. No changes to baseline source, external black box, main, or other streams.


## Issue #10 / integration review 01 — validated follow-up

- Reviewed P1 core ref 822a45084dcad4f21f09c445802d12c1312e331a; baseline pin 7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6. Exact source files verified by Git blob SHA. Clean worktree still blocked by DNS; recovered exact source snapshots used instead. Seven exact core tests PASS, 11.612 s (13.05 s full wall), peak 216560 KiB with tracemalloc. Four exact benchmark tests PASS 0.056 s; updated harness 4 PASS 0.058 s. Third smoke suite 8 VERIFIED, one censored TIMEOUT.
- Library recovery: full original planted ZIP, enhanced ZIP and handoff ZIP recovered, checksummed. 41 archive records / 33 unique byte-identical inputs; extraction repeated with identical manifest SHA-256 49d09e6632ea0af6e6db6e392459a52fb2dfc6f8d3f647d2be92c0d81b1a6381. Split upload aliases denied raw materialization; original full archive available. Legacy six required module bytes match the pin; sample.py and search.py require only line-ending normalization to attain exact Git blobs. Three bundled legacy inputs recovered with matching Git blobs and reference labels separated; scale raw fixture byte-identical.
- Same-host 5s/512 MiB AS paired tests on nine recovered raw inputs: legacy four verified optima, three INCOMPLETE, two Python MemoryError at dense singleton mask construction; P1 five independent structural optimum replays, four lower-bound-only (HDFS/holdout/path8/tiny_choice). Both 100k original planted cases have verified cost 10000/90000 blocks; not substituted synthetic cases. Also two separate synthetic 100k core test constructions independently verified. Legacy targeted tiny_choice one query, 237 JSON bytes, exact transcript reconciliation. Actual simulator interruption test 3 attempted calls, 2 replies (128+93 bytes), last attempt only. Four selected sparse replay mutations rejected. No external calls; operational INCOMPLETE.
- New code is only in benchmarks/v2; no production schema or proof-agent changes. No merge.

| Commit | Checkpoint |
|---|---|
| cf008c5 | Exact reviewed Python tests and third smoke execution |
| edc550d | Pinned sparse-core worker, scoped independent replay |
| cf37670 | Six measured sparse results including synthetic and incomplete |
| 05952d4 | Exact legacy snapshot gate and simulator telemetry reconciliation |
| 4c92f49 | Recover original archives and input/reference checksum inventory |
| 7406ad1 | Nine actual paired cases + targeted instrumentation |
| 085ba76 | Actual simulator and replay mutation checks |
| b4ca57f | Reproducible commands, archive digests, comparison limitations |

Full details: benchmarks/v2/ISSUE10.md, results/issue10-python-rerun.md, results/issue10-sparse.csv, results/issue10-paired.csv. Next gates: remaining 28 planted instances, repeated 5/30 s controlled comparisons, enhanced variant run, clean checkout CI, shared P2 schema integration and live external transport. Not a full end-to-end optimizer claim.


## Integration review 02 / issue #10 — executed follow-up

- All 33 original planted inputs, including previous 28 unrun inputs: 99 measured 5s/512 MiB runs, legacy 11 verified optima, enhanced 15, P1 29 plus four verified bounds. All finite optima agree with archived references read post-run only. Two producer-optimal but replay-censored results excluded from certification.
- 12 serial repeat runs on two tiny cases, nine selected 30s runs (small_count, large_reverse_dense, original scale-1000), explicit failure and query telemetry. Small_count now verifies in both baselines, scale-1000 enhanced/P1 verifies, legacy times out. Full 30s matrix and broad repeats not completed.
- Independently reran exact reviewed P2 core/proof/interface suites 12+14+13=39 passing methods; source blob identities verified. 13 actual raw P2 producer-ledger-independent replay runs, including 2 high-cap retries. Nine 5s roundtrips pass; huge_long_active closure memory-censored at 512 MiB but verifies cost 10000 at 1536 MiB/30s. Huge_choice_active independent proof remains MemoryError even at 1536 MiB; no verified bound from that P2 run.
- No operational ACCEPT, zero external attempts, no external learner or baseline source changes. No merge. Clean worktree CI still DNS-blocked, unified adapter transaction gate open. Exact source snapshots and archive hashes recorded in REVIEW02.md.

| Commit | Checkpoint |
|---|---|
| 751b5db | Exact P2 core tests |
| 7bd0673 | Enhanced archive runner |
| d65c9ec | Cohort/repeat runner |
| 442fe01 | Post-run result exporter |
| 71253b1 | All 99 original planted measurements |
| d790d1d | Actual P2 phase harness |
| 0a3fd4f | 11 P2 phase records |
| f64ec65 | 2 higher-cap P2 trials |
| 7106ac4 | Independent proof/interface suites |
| 41a9eaa | 12 serial repeats |
| 10a89b3 | 9 selected long-budget runs |
| 7f2897c | Input-hash/reference index |
| 25a7ab0 | Review02 reproduction and limitations |

See benchmarks/v2/REVIEW02.md and results/review02-*. Commit checkpoints are new measurements; previous review01 results retained unchanged.
