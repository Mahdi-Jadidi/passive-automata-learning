# P3 M2 experimental evaluation

This evaluation covers unrestricted structural search with B=0. Operational status is **INCOMPLETE**.

The standard run used benchmark commit `b34cdba663af8d6b5892d1afb027a97bbc6aca7e`. [Actions 45627999119](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45627999119)

Producer commit `391abf97df3b67661082c907d9ce20b4f69636c2` supplies the search and region blobs `73da7bea551df73a8676b0adf0401cd7f2d307b5` and `657c4e0e4059b32cd9e6477e61c7a3673290f36d`. Independent verifier commit `d89bab4c005d17c8b27d4c1e6dd291135aca649a` supplies frontier verifier blob `540a7cf9e7b048684d3ea03def744175ae629b65`. The standard JSON records all dependency pins and exact phase commands. [Standard JSON](standard.json) · [Phase CSV](standard.csv) · [Reproduction commands](COMMANDS.md)

## Experimental setup

The native harness checked the seven exact raw inputs against the committed fixture manifest (SHA-256 `b69986b320ea9f328e0c107696e6ff4d9f2c71efc0624a6859c98295f16389ba`). It built a canonical empty journal/2 for each sample using the independent sample digest and passed the exact bytes to the independent scope builder. Each scope replay yielded identity root ownership, so the base lower bound is 0. The producer receives raw input and trusted scope; the verifier receives raw input, journal, scope, and proof. Evaluation references were absent from the sparse worktrees and the staged input directories. Processes shared the Linux runner filesystem.

Every case/profile ran one/all and CPython 3.13.5 normal/-O, with two fresh runs per variant and a one-entry checkpoint probe. The external wall cap was 30 s per phase with a 25 s cooperative search/replay budget. Each phase used `RLIMIT_AS` 1536 MiB or 512 MiB, with RSS observed separately. The producer had 10M work, 2M entries and a 64 MiB internal frontier budget. The verifier had 200M work, 2,000,001 nodes and entries, 128 MiB proof bytes, 20M exact checks, depth 10,000, and 64 MiB each for raw and journal input. The internal frontier budget accounts for admitted frontier data; the final certificate includes additional serialized structure. Phase times include CLI startup, parsing and output. The parent processes are outside the child resource caps.

Fresh determinism compares exact certificate SHA-256, native status and non-time counters. Resume compares the capped resumed certificate bytes and status against the first direct run. Budgets are per invocation, so a resumed run can advance farther within a fresh work allocation. The phase CSV records both visits and replay checks with their native definitions; producer and verifier exact-check counts are implementation-specific. An incumbent cost is provisional. Certified structural results come only from independently verified EXHAUSTED certificates.

## Standard measurements

The 14 case/profile jobs completed all 56 mode/interpreter combinations. Eight combinations were `VERIFIED`, all on tiny. The other 48 were `INCOMPLETE`. Every fresh certificate matched its repeat, and normal/-O agreed for each case/profile/mode. The run produced no infeasibility claim.

The rows below summarize the first fresh trial, using the same values for normal and optimized Python where those values match. Counts in parentheses are one/all. The phase CSV carries both fresh trials, checkpoint/resume, elapsed time, peak RSS and exact artifact hashes.

| Fixture | Producer outcome at both memory caps | Fresh nodes (one/all) | Proof bytes (one/all) | Verifier at 1536 MiB | Verifier at 512 MiB |
|---|---|---:|---:|---|---|
| `tiny_choice` | `EXHAUSTED` / `EXHAUSTED` | 221 / 461 | 46,588 / 99,931 | `VERIFIED`, cost 2 and four all-mode optima | `VERIFIED`, same cost and set |
| `small_choice` | `PARTIAL / FRONTIER_CAP` in both modes | 316,730 / 301,818 | 79,579,990 / 81,080,550 | `INCOMPLETE`, unresolved frontier | `INCOMPLETE`, `MemoryError`, zero nodes checked |
| `medium_choice` | `PARTIAL / WORK_CAP` before root split | 1 / 1 | 4,189 / 4,189 | `INCOMPLETE`, unresolved frontier | `INCOMPLETE`, unresolved frontier |
| `huge_choice_active` | `PARTIAL / WORK_CAP` before root split | 1 / 1 | 589,189 / 589,189 | `INCOMPLETE`, unresolved frontier | `INCOMPLETE`, unresolved frontier |
| `hdfs_1024` | `PARTIAL / WORK_CAP` in both modes | 29 / 29 | 8,485 / 8,485 | `INCOMPLETE`, unresolved frontier | `INCOMPLETE`, unresolved frontier |
| `hdfs_holdout_1024_uncapped` | `PARTIAL / WORK_CAP` in both modes | 33 / 33 | 9,980 / 9,980 | `INCOMPLETE`, unresolved frontier | `INCOMPLETE`, unresolved frontier |
| `cover_path_8` | `PARTIAL`, `WORK_CAP` in one and `FRONTIER_CAP` in all | 311,557 / 290,607 | 78,339,509 / 79,594,130 | `INCOMPLETE`, unresolved frontier | `INCOMPLETE`, `MemoryError`, zero nodes checked |

At 1536 MiB the verifier checked every emitted node in the small and cover fresh proofs. The bounds for small were base LB 0 and provisional incumbent cost 5 in both modes. Cover reached provisional 5 in one mode and 6 in all mode. For the 512 MiB fresh runs, the verifier hit memory limits even though each certificate was about 75–77 MiB on disk. The producer and verifier memory observations are recorded separately.

At 1536 MiB, the first normal small/one producer phase took 11.730 s and peaked at 408,844 KiB, with 13,421 exact checks. Independent replay took 14.080 s and peaked at 607,632 KiB, with 214,305 exact checks. For huge/one at the same cap, the producer took 3.122 s and peaked at 80,860 KiB. The verifier took 1.418 s and peaked at 83,920 KiB. Its one checked node was the OPEN root. The huge result describes the initial work-limited frontier for 100,000 symbols; it supplies no search-completion or proof-scaling estimate.

### Checkpoint and repeat behavior

The capped resume comparison matched in 32 combinations and differed in 24.

- Tiny used a two-node `ENTRY_CAP` checkpoint and resumed byte-identically to the fresh complete result in both modes, both profiles and both interpreters.
- Small and cover all-mode resumed byte-identically at the frontier cap. Their one-mode resumed artifacts differed at the tested caps. Small one advanced from 316,730 to 316,731 nodes at the same recorded entry count, producing 79,580,244 bytes instead of 79,579,990. Cover one advanced from 311,557 to 311,579 nodes under the per-invocation work cap. These are measurements of capped frontier equality.
- Both HDFS fixtures advanced six additional nodes after the one-entry checkpoint, so the resumed partial certificates differed. The verifier replayed the emitted nodes and returned `INCOMPLETE` for each unresolved suffix. Medium and huge hit the work cap before the entry cap. Their matching single OPEN roots are restart observations without progress.

GitHub Actions retains the first direct proof and checkpoint for each variant together with phase logs and native metrics. The committed measurements retain SHA-256 and length for every emitted proof, including second fresh and resumed artifacts whose exact files were omitted from the upload.

Published SHA-256 values are `47edc893bb3c3617dd925bfcdfc53fa074cc7117e3fcb463eca1a84ff83baa3a` for the 476-row CSV, `9561605b5515721da6af00d877babc438e64c1532e007e1ebb4689ca8a006be5` for the standard JSON, and `bc3d28f6531fb2849656d228cde26a2e4b3a06c52ad3386a503b273e9bf9f6ee` for the expanded JSON.

The preliminary Actions run [45627762197](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45627762197) incorrectly included the producer's elapsed-time field in native repeat equality. The smoke gate stopped scale execution on that run. Commit `b34cdba` excluded elapsed time from the comparison and reran the measurements above. The existing fake-adapter harness tests pass 9/9 under normal and optimized Python and serve as infrastructure validation.

## Expanded-budget acceptance evidence

These two small-fixture results use expanded resources and are stored in [expanded.json](expanded.json).

| Mode | Producer run and cooperative limits | Proof bytes | Independent replay | Structural result |
|---|---|---:|---|---|
| one | [45592454384](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592454384), 240 s / 5120 MiB | 264,463,193 | [45592784988](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45592784988), normal/-O `VERIFIED` at 50.38/50.70 s and 2,026,520/2,028,720 KiB | Cost 4, 1,091,642 checked nodes, 659,914 exact checks in both modes |
| all | [45593819618](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45593819618), 600 s / 13312 MiB | 1,399,367,871 | [45628480530](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45628480530), normal/-O `VERIFIED` at 392.47/396.25 s and 10,341,036/10,343,200 KiB | Cost 4, all 16 optima, 5,496,670 checked nodes and 4,460,579 exact checks in both modes |

The expanded producer's normal, optimized, and resumed certificate bytes agree for both modes. Small/one SHA-256 is `dafa72f9e8ec4cc63330d4a7cd420cd478237dd7431c7e488267345ed810471e`. Small/all SHA-256 is `9fb5f5bbc1c64e90bc955f73d2325a1d159224e91258e8a8758a34595102e2a7`. The new small/all replay used verifier checkout `d89bab4c`, a 630 s outer wall cap, and the same 13312 MiB address-space cap. Both modes charged 2,494,969,001 verifier work units. The separately timed RGS oracle exhausted all 4,213,597 partitions and matched the complete optimum set in each Python mode.

## Boundaries

This evaluation used the exact M2 source pins with no algorithm, baseline, learner, or production-interface changes. There were zero external learner calls and no merge. The original P2 journal/2 artifacts remain unavailable. Historical P2 full replay remains **NOT RUN** under the hardened checker and is outside these P3 empty-journal trials. This report makes no performance comparison against an external learner or unrelated pin.
