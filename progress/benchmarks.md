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
