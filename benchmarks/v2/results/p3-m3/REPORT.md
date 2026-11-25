# P3 M3 benchmark evaluation

The seven original raw fixtures, their SHA-256 manifest, and the M2 standard and expanded reports are frozen at `76bed1ed5964519db409148faebea88dad891ef3`. This report follows assignment #4 in [Integration Review 07](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/2ddf8b89d01dec5b3eb321d166de29360ebd93c0/implementation/partition_feedback_final/research/INTEGRATION_REVIEW_07.md). See the [reproduction commands](COMMANDS.md).

## Audit of the 24 frozen M2 differences

| Cases | Differences | Fresh → renewed resume nodes | Accounting |
|---|---:|---:|---|
| `hdfs_1024`, one/all | 8 | 29 → 35 | Per-invocation work cap renewed |
| `hdfs_holdout_1024_uncapped`, one/all | 8 | 33 → 39 | Per-invocation work cap renewed |
| `cover_path_8`, one | 4 | 311,557 → 311,579 | Per-invocation work cap renewed |
| `small_choice`, one | 4 | 316,730 → 316,731 | Retained checkpoint bytes omitted from the resumed live frontier charge |

Each difference appears at both address-space profiles and with both interpreters. The exact original proof hashes, caps, counters and verdicts are in [CSV](m2-frozen-differences.csv) and [JSON](m2-frozen-differences.json). The original measurement run completed all 14 jobs successfully. [Actions 45627999119](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45627999119)

**Renewed work.** The M2 budget reports work from the current invocation. Summing checkpoint and resume work exceeds 10 million units by 978,602 on HDFS, 937,327 on the holdout, and 810 on cover/one. These cases never reach the retained frontier cap. Equal cumulative charged work deducts the checkpoint's work from the resume allocation. Resume repeats some checks and reconstructs the path, while skipping already completed checks. Equal cumulative charged work therefore need not place the algorithm at the same DFS operation as a fresh run.

**Retained frontier.** M2 restores the checkpoint node table but initializes a zeroed budget. A fresh split charges its closed residual. A fresh child charges its OPEN encoding plus cursor record. The restored split and old cursor entries bypass both admissions. With a one-entry checkpoint, the omitted charge is the 107-byte root residual. Small/one reports 67,108,842 resumed bytes, but the retained sum is 67,108,949, which exceeds the 67,108,864 cap by 85 bytes. Fresh stopped at 67,108,731. The identical invocation entry counts reflect new entries only. The resumed live-byte limit is undercounted even in some byte-identical variants, where the omitted charge fits within the unused margin. This accounting concerns admitted frontier entries. Total serialized proof size and process memory are separate measurements. [Frozen search source](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/391abf97df3b67661082c907d9ce20b4f69636c2/implementation/partition_feedback_final/selector_v2/edr_search.py)

**Replay and semantic coverage.** Twenty of the 24 different original resumed proofs replayed every emitted node and ended with unresolved coverage. Four 512 MiB replays reached `MemoryError` before checking any nodes, two in each of small/one and cover/one. All 24 stayed `INCOMPLETE`. Byte divergence is a checkpoint observation. The independent replay outcome determines whether the emitted claims were checked and whether an optimum was certified. The original tiny runs completed byte-identically after resume in all eight combinations. Medium and huge matched at a single OPEN root.

## Equal cumulative controls

The 1536 MiB rerun exercises the four affected fixtures in one/all and normal/-O. The fresh and renewed arms reproduce the M2 native protocol. The cumulative-frontier control deducts prior admissions from the resume frontier and entry caps and leaves the work budget renewed. The cumulative-work control additionally deducts prior work. Both retain the same per-phase wall limits. The original 512 MiB records are included in the frozen 24-row audit. These new cumulative experiments target deterministic counters and were run at 1536 MiB where the verifier can parse the larger certificates.

All six CI jobs passed, including the matrix setup and the separate journal case. The pairs below gave the same results in normal and optimized Python. The full [restart audit CSV](audit.csv) and [JSON](audit.json) include per-phase resource measurements and independent verifier verdicts. [Actions 45634969027](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45634969027)

| Case / mode | Fresh nodes | Renewed nodes | Adjusted frontier nodes | Equal cumulative work nodes | Equal-work proof bytes vs fresh |
|---|---:|---:|---:|---:|---|
| HDFS / one and all | 29 | 35 | 35 | 29 | Match |
| Holdout HDFS / one and all | 33 | 39 | 39 | 33 | Match |
| Cover / one | 311,557 | 311,579 | 311,579 | 311,555 | Differ |
| Cover / all | 290,607 | 290,607 | 290,607 | 290,607 | Match |
| Small / one | 316,730 | 316,731 | 316,730 | 316,730 | Match |
| Small / all | 301,818 | 301,818 | 301,818 | 301,818 | Match |

Adjusting the retained cap alone restored the small/one fresh SHA-256. Its adjusted resume charged 67,108,624 new bytes and retained 107 old bytes, exactly the fresh 67,108,731. Cover/one's equal-work continuation spent 9,999,171 units in addition to 816 from the checkpoint, totaling 9,999,987. The fresh arm spent 9,999,994. Both reached the deterministic work cap before the next charge. The restart's replay and repeated setup work prevent using equal charged totals as a guarantee of byte equality. Independent replay checked the emitted nodes of these 1536 MiB proofs and returned `INCOMPLETE` with unresolved coverage.

## Separate nonempty-journal experiment

A four-symbol sample supplies only raw positive and negative traces. The experiment enumerates exact single-class deletion matches from those traces, writes a single canonical RAW component epoch to journal/2, and sends the exact raw and journal bytes to the independent scope builder. The builder independently checked the epoch and derived `[0,0,2,3]`, giving base lower bound 1. The producer received that scope and the independent verifier replayed the exact journal again against each proof. No answer metadata entered the pipeline.

At 30 seconds and 1536 MiB, M2 verified all four one/all and normal/-O combinations at cost 2. All-mode returned two optima. The four resumed proofs matched the complete fresh proofs byte-for-byte and independently verified. Normal/-O parity held in both modes. The experiment is separate from the original seven-fixture matrix. [Actions job 139277981224](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45634969027/job/139277981224)

## Paired standard and expanded evidence

The paired workflow uses the exact seven original raw fixtures, empty journal/2, identical scope bytes and the frozen 30-second / 1536 MiB and 30-second / 512 MiB limits. It records two fresh trials and checkpoint/restart phases per mode and interpreter. M3 execution depends on the published producer and verifier pins and the producer's opt-in flags. Expanded M2 validation stays in the [frozen expanded report](../p3-m2/REPORT.md#expanded-budget-acceptance-evidence). Operational status remains `INCOMPLETE`.
