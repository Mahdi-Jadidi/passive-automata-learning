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
