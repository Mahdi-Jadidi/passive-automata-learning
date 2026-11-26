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

Both paired profiles also verified the journal experiment in all four variants per arm. M2 emitted five nodes per mode and M3 emitted four, including one cross split at the contracted root. M3 charged 110 discovery work units and ran 15 probes in each first trial. Both arms certified cost 2 and the same two all-mode optima, with completed resume bytes matching fresh in every variant. [Nonempty paired CSV](paired-nonempty.csv) · [Nonempty paired JSON](paired-nonempty.json)

## Paired standard results

The paired workflow used the exact seven original raw fixtures, empty journal/2, identical scope bytes and the frozen 30-second / 1536 MiB and 30-second / 512 MiB limits. Each arm ran two fresh trials plus the one-entry checkpoint and renewed resume under CPython 3.13.5, one/all and normal/-O. All 17 CI jobs succeeded, including matrix setup and the two separate journal profiles. Harness tests passed 9/9 in each interpreter. The producer and independent verifier source maps are in the [exact M3 config](../../p3/m3-native.json). [Actions 45636792736](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45636792736) · [Paired phase CSV](paired.csv) · [Paired JSON](paired.json)

Across the 56 original fixture combinations per arm, M2 verified 8 and M3 verified 24. M3 verified tiny, small and cover in both modes at both memory caps. The other 32 M3 combinations stayed work-capped. The table gives first-trial counts and bytes as one/all, with the same values in normal/-O and at both address-space caps.

| Fixture | M2 nodes | M3 nodes | M2 proof bytes | M3 proof bytes | M3 independently verified result |
|---|---:|---:|---:|---:|---|
| `tiny_choice` | 221 / 461 | 10 / 10 | 46,588 / 99,931 | 2,658 / 2,737 | Cost 2, four all-mode optima |
| `small_choice` | 316,730 / 301,818 | 46 / 46 | 79,579,990 / 81,080,550 | 12,693 / 13,244 | Cost 4, sixteen all-mode optima |
| `cover_path_8` | 311,557 / 290,607 | 641 / 3,271 | 78,339,509 / 79,594,130 | 169,343 / 871,133 | Cost 4, nine all-mode optima |
| `hdfs_1024` | 29 / 29 | 29 / 29 | 8,485 / 8,485 | 8,485 / 8,485 | INCOMPLETE |
| `hdfs_holdout_1024_uncapped` | 33 / 33 | 33 / 33 | 9,980 / 9,980 | 9,980 / 9,980 | INCOMPLETE |
| `medium_choice` | 1 / 1 | 1 / 1 | 4,189 / 4,189 | 4,189 / 4,189 | INCOMPLETE |
| `huge_choice_active` | 1 / 1 | 1 / 1 | 589,189 / 589,189 | 589,189 / 589,189 | INCOMPLETE |

At 1536 MiB, the first normal M3 small/all producer phase finished in 0.115 s at 19,668 KiB, and independent replay verified in 0.065 s at 18,468 KiB. M2 small/all stopped at the frontier cap after 12.291 s at 386,052 KiB. Its verifier checked the emitted frontier in 14.547 s at 602,640 KiB and returned `INCOMPLETE`. M2 also replayed the emitted cover frontier under this memory profile.

At 512 MiB, normal small/all reached `EXHAUSTED` in M3 in 0.065 s at 19,640 KiB, with verified replay in 0.065 s at 18,200 KiB. M2 stopped at its frontier cap after 11.097 s at 385,992 KiB. Its verifier returned `MemoryError` before checking nodes. Normal cover/all M3 completed in 0.617 s at 23,592 KiB, and replay took 0.216 s at 24,528 KiB. M2 stopped after 10.338 s at 374,468 KiB, and its replay returned `MemoryError`. These timings compare outcomes under fixed limits and give completion times only for the exhausted runs.

Discovery admitted 3 cross splits in tiny and 15 in small per first trial. Small charged 14,609 discovery units and 1,886 probes per mode. Cover charged 192,457 / 774,256 units across 33,187 / 133,579 probes and admitted 128 / 396 cross splits. HDFS and holdout incurred 14 and 16 local discovery caps respectively with zero cross splits, reproducing the M2 fresh node counts. Medium and huge exhausted work at the OPEN root before discovery. These censored cases give no completion or large-alphabet scaling estimate.

Fresh repeat and normal/-O parity held within both arms. All 24 completed M3 combinations matched the direct proof bytes after resume and independently verified. The 16 HDFS variants in each arm showed different partial bytes after renewed work. Medium and huge matched without advancing beyond the root. The exporter checks the retained resume bytes and checkpoint prefix independently of the replay verdict. In M3 the frontier metric already includes restored payload. The M2 metric requires adding the checkpoint charge. The revisions account for different admitted payload fields, so byte-limit comparisons measure each revision's defined admission proxy.

The producer and verifier run as separate capped processes. Trial time includes startup, parsing and serialization, especially for sub-100 ms cases. RSS is a separate measurement from the address-space limit. Witness discovery has native work and probe counters without a separate elapsed-time measurement. Both arms use the flat serializer lineage. v2 carries split witnesses and a conflict-residual marker, so different node counts and proof bytes reflect different search coverage and wire fields. Tiny supplies an equal-completion comparison. The paired M2 small and cover runs are censored, so their node and proof sizes describe emitted prefixes.

## Separate validation and scope

The [frozen expanded M2 report](../p3-m2/REPORT.md#expanded-budget-acceptance-evidence) provides same-task complete small proofs under larger limits. Those timings stay out of the standard paired table. The independent M3 proof-only workflow passed all eight native replay jobs, including tiny, small, mixed-path and nonempty-root cases. It is a separate correctness run. [Actions 45637001978](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45637001978)

The M2 report, original input bytes and manifest retain their exact baseline contents. The benchmark branch changes experiment code and evidence only. The pipeline made zero external learner calls. Operational status remains `INCOMPLETE`.
