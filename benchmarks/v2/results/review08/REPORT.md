# Review 08 benchmark freeze

The manifest binds the seven original inputs, source configurations and M2/M3 reports and data to the exact Git blobs at benchmark commit 8484b8bff5b93e1be3a7924697161efc34e481d8. The original evidence remains in place. The manifest records the actual job IDs and conclusions returned by GitHub for the paired and restart workflows.

| Frozen run | Jobs successful | Result |
|---|---:|---|
| 45636792736 | 17/17 | M2 8/56 verified, M3 24/56 verified |
| 45634969027 | 6/6 | M2 restart accounting and independent nonempty-journal control |

The censored CSV and JSON select the first fresh producer invocation for each incomplete raw M3 variant from the frozen paired CSV. All 32 used 10,000,000 charged work units and stopped at WORK_CAP. Each row retains the original discovery counters, RSS and wall time.

| Original fixture | Nodes | All-pairs splits | Cross splits | Discovery work | Probes | Local caps |
|---|---:|---:|---:|---:|---:|---:|
| medium_choice | 1 | 0 | 0 | 0 | 0 | 0 |
| huge_choice_active | 1 | 0 | 0 | 0 | 0 | 0 |
| hdfs_1024 | 29 | 14 | 0 | 57,344 | 2,548 | 14 |
| hdfs_holdout_1024_uncapped | 33 | 16 | 0 | 65,536 | 2,598 | 16 |

Medium and huge ran out of work before the root split and before any charged discovery. The old producer has no separate root compatibility timing, so this evidence cannot attribute the entire pre-split budget to compatibility. HDFS and holdout fell back to all-pairs at every admitted split. Local discovery work was under 0.7% of the total charged work on these runs. These are observations of incomplete frontiers.

Reproduce the source data with the frozen [commands](../p3-m3/COMMANDS.md). Query CI with gh run view RUN --json headSha,conclusion,url,jobs and select the paired CSV rows with arm=m3, phase=producer-1 and run_status=INCOMPLETE.

The historical P2 huge journal bytes remain missing. A ledger export generated from RAW closure in this assignment would be newly generated evidence. The earlier nonempty micro-control is separate from the large-fixture pipeline.

## Controlled compatibility and discovery ablations

All 14 jobs in [Actions run 45831832220](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45831832220) succeeded. The same seven original inputs ran in one/all and normal/-O at 30 s with 512 MiB and 1536 MiB address-space caps. The producer pin is 140b4e51f89baf8c3e38e18d704d8c4d36c24f39 and the independent verifier pin is 5a10e649a91f8c5b159b818de7e71d4028b8170d. The frozen M3 run used different executable pins and remains a separate baseline.

Both verifier modes verified 72 runs, covering all three arms on tiny, small and cover. All three arms emitted the same proof bytes in each of the 24 matched completed variants. Both verifier modes returned INCOMPLETE for all 96 large-fixture runs. Per-stage timing, RSS, work, root outcome, proof size and hashes are in [CSV](ablation.csv) and [JSON](ablation.json).

| Original fixture | Dense root compatibility work | Sparse root compatibility work | Dense nodes | Sparse nodes | Sparse + join nodes |
|---|---:|---:|---:|---:|---:|
| medium_choice | 9,963,699, capped | 69,472 | 1 | 265 | 63 |
| huge_choice_active | 9,691,999, capped | 477,452, capped | 1 | 1 | 1 |
| hdfs_1024 | 939,070 | 87,509 | 29 | 2,050–8,352 | 280–840 |
| hdfs_holdout_1024_uncapped | 897,461 | 88,444 | 33 | 2,110–7,463 | 280–828 |

Dense root compatibility consumed nearly all charged work in medium and huge. Sparse gets through medium's root check. On huge, the sparse estimator reached 67,108,800 charged index bytes before the next allocation would exceed the 64 MiB cap. The native stop reason is FRONTIER_CAP and discovery never starts. HDFS and holdout both pass the root check in all arms. On medium, discovery consumed 534,972 charged units in the sparse arm and 7,680,787 with join enabled. The HDFS join arms spent roughly 6.4–6.8 million charged units in discovery. Join produced one hit on medium and zero or one per HDFS run. All these frontier counts are censored, so they do not establish time to completion or an improvement in optimum coverage.
