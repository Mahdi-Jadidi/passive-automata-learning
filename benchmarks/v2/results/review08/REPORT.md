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

## Authoritative RAW journal pipeline

All eight jobs in [Actions run 45832542233](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45832542233) succeeded. They ran 32 fresh and 32 checkpoint/resume routes on the four original large inputs. Each route started with the pinned component closure and exported its RAW records through RegisteredLedger. A separately staged verifier rebuilt the trusted scope from the original input and journal bytes. M3 searched from that scope, and independent replay consumed the resulting proof. The pipeline used producer 9a361f6fa59414cc0ac262154d87c37f5aed0403, adapter 122844ee5668f1c898f85b08133a562f31719718 and verifier 5a10e649a91f8c5b159b818de7e71d4028b8170d with dense exact replay. [Phase and total CSV](pipeline.csv) · [CI, commands, counters and retained hashes](pipeline.json)

All 64 RAW closures reached the rule's fixpoint. Independent scope construction succeeded on all routes. Medium and huge each contracted original symbol ID 1 into the class represented by ID 0. Both HDFS roots remained identity. The new journal exports for medium and huge were 126,364 and 3,333,809 bytes respectively. The exact journal and independent scope bytes for these nonidentity roots are [retained as gzip archives](trusted-roots/). The frozen input manifest supplies the expected raw SHA-256. The historical P2 huge journal is still missing.

| Original fixture | Fresh nodes | Resumed nodes | Fresh proof bytes | Resumed proof bytes | Fresh total wall s | Restart total wall s | Peak RSS KiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| medium_choice | 1 | 1 | 4,189 | 4,189 | 3.76–4.99 | 6.82–8.91 | 28,160 |
| huge_choice_active | 1 | 1 | 589,189 | 589,189 | 16.74–22.16 | 25.76–30.05 | 148,336 |
| hdfs_1024 | 29 | 35 | 8,485 | 10,758 | 3.78–7.01 | 4.77–9.06 | 27,512 |
| hdfs_holdout_1024_uncapped | 33 | 39 | 9,980 | 12,377 | 3.76–6.08 | 4.77–7.82 | 27,452 |

All 32 checkpoints independently replayed as unresolved. All resume invocations produced a partial proof. Fresh replay and 28 resumed replays returned unresolved frontier. The four huge 1536 MiB resumed replays used up the shared deadline. Reported wall time includes process cleanup and reached 30.05 s. No completed fresh or resumed proof was available to establish completion or completed-resume byte equality. The HDFS resume counts reflect renewed per-invocation work within the shared wall budget.

The first CI attempt stopped at source staging because the checkout paths were relative. The second executed scope and search, but the pinned verifier CLI rejected the expected-format and expected-mode flags. Its green job status did not establish proof replay. The final run used the published verifier revision with those guards and checked that each replay exit code agreed with its verdict. [Staging failure](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45831207308) · [Superseded smoke run](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45831411364)
