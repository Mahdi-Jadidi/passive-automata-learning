# Review 05 — hardened P2 large-case recovery and P3 benchmark preparation

**Branch:** `research/v2-benchmarks`  
**Parent head:** `635bc6cc182f2215d6cd354b894c8a0eb6a831a0`  
**Scope:** original-byte recovery and benchmark infrastructure only. No learner, baseline, proof implementation, or production interface changes.

## A. Hardened P2 large cases

The exact hardened checker pins remain:

- `bounded_deletion.py`: Git blob `e1fc61b6f03484d4428642ca157e2dac43f0572d`.
- `test_bounded_deletion.py`: Git blob `6de549b9b4d208be99a419c88fd903a1ce1a6dcc`.

`REVIEW04_HARDENED_UNIT.md` records 6/6 unit tests in normal mode and 6/6 in optimized mode. This checkpoint does not transfer those unit results to a large-case replay.

### Recovered original raw inputs

The root Library copy of `partition-planted-benchmark.zip` was raw-materializable. Its SHA-256 matches `recover_inputs.py` exactly: `5d2dae2ca718cc65d48e5fbcb62480baeae0da35d37edb9184ba2b61d91e1dc4`. The original planted archive also contains the historical `PLANTED_REPORT_FA.md`, `ALL_MEASUREMENTS.csv/json`, four planted summary CSVs and `root_replay_results.json`; these were extracted and SHA-256 inventoried. They remain evaluation/history only and are not transferred to the hardened checker or solver.

| Case | Exact source member | Raw bytes | SHA-256 |
|---|---|---:|---|
| `huge_choice_active` | `planted_results/huge_choice_active/input.json` | 2,920,040 | `0be60da81326bcd8974da1df07e018e60dcd62714123b884c873ed3be782beba` |
| `huge_long_active` | `planted_results/huge_long_active/input.json` | 3,240,040 | `0ed5834c91b82a00ec8be5ba27c7f36b12f47d0d5e39911cf05fe6a5ce6f3e0c` |

Both raw JSONs have exactly the three input keys and 100,000 ordered alphabet symbols, 10,000 positives and 10,000 negatives. The two files are preserved separately in Library at `/Passive learning research/p2-huge-inputs-recovered.zip` (ZIP SHA-256 `7a51787974c056247f9413e5bb30bf58b556eb43940432e7a1146f579d652a18`).

### Original journal/2 bytes still unavailable

The exact original journal/2 artifact bytes were not recovered. The Project Library copy of `review03-benchmark-evidence.zip` still has no authorized raw-byte materialization path; the full planted source archive contains the raw inputs and historical references but no journal/2 artifacts. Historical report members recovered from `partition-planted-benchmark.zip`: `PLANTED_REPORT_FA.md` SHA-256 `6383fbf976eaf115a41e29e2b8c3f4689db366198ce57c23d6f0255ba047fcb6`; `ALL_MEASUREMENTS.csv` `f5c575eeee868a6d4d68c966c22cbbd29517781fd0eb2222e7770d9ff0826343`; `ALL_MEASUREMENTS.json` `413e91caa53b137ccbeb0f6f84327e71cb01ebf6fc73d9951c8d858f4f218eb2`; `planted_results/summary.csv` `fb198bc1dd480bf468798d7b33040c618f655e99448eaa6cc102c755b6a6a5de`; `planted_30s/summary.csv` `17a83ecaaf3a5361de0d7378e5200796224ea0d875b08dd338a057b888d71f15`; `planted_extra/summary.csv` `a8285d4566bb20e5f007534cb6af90e29c101f5f48fe157dea324b854667de3a`; `planted_high_memory/summary.csv` `e6755c2beeef16e64f508d858dd14b1612183e0089362739cf3d4ed8469670a4`; `root_replay_results.json` `55326a93324b7939ee19c5f3e51922ee48961172af27e7afb288bb63727091ca`. Their old solver outcomes are historical and were not reused as hardened verifier results. The earlier `REVIEW03.md` records these expected journal SHA-256 values:

- `huge_choice_active`: `dfbc8c72bdecb316fe72dafdb8130b97887c8e7b81cc129bd41eb2eab63463d5`
- `huge_long_active`: `779cc7dd5f9198f5e4a5f1460e3ef2f869a2c45e509e0b41daaae016bf8ac3fe`

Those hashes are historical identifiers only; they are not a substitute for the artifact bytes and were not recomputed in this runtime.

### Raw closure phase — executed separately from journal replay

The producer raw-closure phase was run against the recovered original raw inputs using the current core source blobs listed below. The run does **not** import `bounded_deletion.py`, `RegisteredLedger`, or any independent journal replay module. `RAW_CLOSURE_COMPLETE` means only that the producer's existing component-closure rule class reached `FIXPOINT`; it is not a structural optimum, P3 EDR-BB result, hardened proof verification, or operational acceptance. The `producer_raw_check` column is the producer's own raw structural check, not an independent verification.

| Case | Mode | Address-space cap | Process elapsed | Closure elapsed | Raw-check elapsed | Peak RSS | Work units | Exact deletion checks | Facts | Edges | Epochs | Quotient blocks | Producer raw check | Raw-records SHA-256 | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `huge_choice_active` | normal | 1536 MiB | 1.832 s | 1.300 s | 0.185 s | 205,220 KiB | 863,938 | 41,998 | 20,999 | 1 | 2 | 99,999 | false | `29b7482b71c86b96de5b06653072648d4d8f89fdd9d63af18a96d86429f611d8` | RAW_CLOSURE_COMPLETE |
| `huge_choice_active` | optimized | 1536 MiB | 1.877 s | 1.404 s | 0.176 s | 207,028 KiB | 863,938 | 41,998 | 20,999 | 1 | 2 | 99,999 | false | same | RAW_CLOSURE_COMPLETE |
| `huge_choice_active` | normal | 512 MiB | 1.796 s | 1.352 s | 0.195 s | 202,812 KiB | 863,938 | 41,998 | 20,999 | 1 | 2 | 99,999 | false | same | RAW_CLOSURE_COMPLETE |
| `huge_choice_active` | optimized | 512 MiB | 1.967 s | 1.473 s | 0.175 s | 202,472 KiB | 863,938 | 41,998 | 20,999 | 1 | 2 | 99,999 | false | same | RAW_CLOSURE_COMPLETE |
| `huge_long_active` | normal | 1536 MiB | 2.192 s | 1.657 s | 0.172 s | 208,324 KiB | 1,410,000 | 60,000 | 30,000 | 10,000 | 2 | 90,000 | true | `98d2a9825d116dab50f074e2c3f36e244be0bc38f5dc1a582d52276fb6d300eb` | RAW_CLOSURE_COMPLETE |
| `huge_long_active` | optimized | 1536 MiB | 2.234 s | 1.655 s | 0.178 s | 208,316 KiB | 1,410,000 | 60,000 | 30,000 | 10,000 | 2 | 90,000 | true | same | RAW_CLOSURE_COMPLETE |
| `huge_long_active` | normal | 512 MiB | 1.354 s | — | — | 201,296 KiB | — | — | — | — | — | — | — | — | MEMORY_ERROR |
| `huge_long_active` | optimized | 512 MiB | 1.526 s | — | — | 201,152 KiB | — | — | — | — | — | — | — | — | MEMORY_ERROR |

The 512 MiB `MEMORY_ERROR` rows are specifically raw-closure producer processes under `RLIMIT_AS`; they are not bounded-deletion verifier failures. RSS is lower than the address-space cap because virtual address-space exhaustion can occur before RSS reaches the cap. The address-space limit is applied before reading/parsing the raw input (after interpreter startup). Component closure receives a 30-second cooperative deadline; the external process safety wall was 35 seconds to allow interpreter startup. The producer raw structural check is measured as a separate subphase under the same address-space cap. The exact-deletion counter is a transparent wrapper around the pinned `_equal` predicate; it increments a counter and delegates to the unchanged function. External wall times (including interpreter startup) were 2.71/2.49/4.04/4.03 s for `huge_choice_active` normal-1536/normal-512/optimized-1536/optimized-512, and 2.93/2.07/4.17/3.66 s for `huge_long_active` in the same order. The complete per-run JSON, stdout/stderr hashes and raw-record output hashes are preserved in `p2-raw-closure-evidence.zip` (SHA-256 `bbbae722127828023260bdcc2b1e3762a0483dabf41cfee77e4a5c15138e27c4`; Library path `/Passive learning research/p2-raw-closure-evidence.zip`). Aggregated `results.json` SHA-256 is `601a5c0fad7320e1e777519b57a4092fe3536449d2d9eeb38b169e51de97d6ec`; the generated CRLF `results.csv` SHA-256 is `ace2aa9f9125acfc8f9e6d18dccbffd0657c1087d5582dbcbbfb8e758b45131e`. The committed repository CSV is LF-normalized (SHA-256 `9f5dc122a92b70b4578284b00c3258498b38feb62ae74fc2ee766ae757d1dede`; Git blob `78beacf1411b59c668c7ac0bd003c24e7bdcfd34`).

The exact core source commit `796a83a5f8f69c4dc7c0db619e1cdb130ddc0b33` (the P2.1 gate pin; same blobs at core branch head `3c5b8f42f1a268505acec3a2e871a08c6e51b22c`) was fetched and verified locally by `git hash-object`: `core.py` `997304c3adce9d3148d454b079639575f419ba0e`; `component_closure.py` `97844bc266556cc04cd54a75c0d57dc00d6709ea`; `sparse_analysis.py` `f773cc1c6b1a852193ba2afb75aa2fce4941a5c2`; `schema.py` `65a7522a8442a184c14f7a0fa74fc307ce60229f`. The runner records these same pins and the hardened proof commit `cf5a007571853b6cdf6259fa2a9a95f5c1e351f8` as not imported. It does not import the hardened verifier.

Reproduction command shape (repeat separately for both cases, both modes, and each memory cap):

```sh
timeout 35s python -B benchmarks/v2/p2_raw_closure_replay.py \
  --input /path/to/p2-inputs/huge_choice_active.json \
  --expected-input-sha256 0be60da81326bcd8974da1df07e018e60dcd62714123b884c873ed3be782beba \
  --repo-root . --output /tmp/huge-choice-normal-1536 \
  --seconds 30 --memory-mib 1536

timeout 35s python -B -O benchmarks/v2/p2_raw_closure_replay.py \
  --input /path/to/p2-inputs/huge_long_active.json \
  --expected-input-sha256 0ed5834c91b82a00ec8be5ba27c7f36b12f47d0d5e39911cf05fe6a5ce6f3e0c \
  --repo-root . --output /tmp/huge-long-optimized-512 \
  --seconds 30 --memory-mib 512
```

### Ledger and hardened replay remain NOT RUN

| Required phase | Normal | Optimized | Status / reason |
|---|---|---|---|
| Ledger ingestion of original journal/2 artifact | NOT RUN | NOT RUN | Original journal/2 envelope bytes unavailable |
| Complete independent journal/2 replay using hardened blobs | NOT RUN | NOT RUN | Original journal/2 envelope bytes unavailable |
| Hardened verifier 512 MiB replay | NOT RUN | NOT RUN | No original journal artifact was supplied to the hardened verifier |
| Hardened verifier 30 s / 1536 MiB replay | NOT RUN | NOT RUN | No original journal artifact was supplied to the hardened verifier |

**Required next input:** upload `review03-benchmark-evidence.zip` as a raw file or provide the two exact journal/2 JSON artifact files whose SHA-256 values are listed above. Until then, the complete hardened replays remain `NOT RUN`, not `INCOMPLETE`, `INVALID`, or `MEMORY_ERROR`. The raw-closure measurements above are a separate producer-only phase and must not be presented as a hardened verifier replay.

## B. Seven P3 raw-only fixtures recovered

The exact seven raw-only inputs were reconstructed from the two verified source archives. The third archive required by the committed recovery script, `partition-scale-improved.zip`, was also recovered and hash-checked (`595f928ef085f8decc9533404eeb3a8b458ff4e82e527e80d889c20fa55946ca`); it is not used to construct the seven P3 fixtures. The resulting `input-manifest.json` raw SHA-256 is `b69986b320ea9f328e0c107696e6ff4d9f2c71efc0624a6859c98295f16389ba`, and its Git blob ID is exactly the committed `68d2414bd7e1f9294a850268369a55559d440b06`. The separate evaluation index Git blob is `289b7bf33b9d5e47eb863fb7099d1c22722f0722`. All seven individual raw hashes and dimensions are recorded in `p3/README.md` and the committed input manifest.

Recovered input-only ZIP SHA-256: `a280e093aa298af359f0e30408b633eefb0283e02471dba52f3d78f1e4059220`. Recovered evaluation-only ZIP SHA-256: `8d3da1c67975edd2209fd69f7fa9c403d613c97bf55293bb57dd2c8012a30982`. Both were uploaded to distinct Library paths. The ZIPs are newly assembled; their member input bytes are the exact original bytes. No reference or planted optimum is included in the input-only ZIP.

## C. P3 harness validation and coordination

`p3_harness.py` is a benchmark-only process runner. It validates raw-only inputs and manifest hashes; runs solver and independent verifier in separate capped subprocesses; records generated/expanded/pruned regions, exact checks, frontier size, work/entry counters, per-phase elapsed time and peak RSS; preserves artifact and log hashes; and checks deterministic replay plus optional checkpoint/resume. The adapter envelope is explicitly measurement-only and does not define or fork the production P3 proof schema.

Validation uses fake adapter programs only (no EDR-BB solver result):

```sh
python -B -m unittest -v test_p3_harness
python -B -O -m unittest -v test_p3_harness
```

Both modes: **9/9 PASS**. The mock test verifies independent-verifier phase separation, deterministic certificate replay, checkpoint/resume equality, strict raw-only schema, duplicate-key rejection, fixture hash rejection, and `NOT RUN` for a missing input. These are harness tests, not P3 algorithm benchmarks.

Coordination requests were posted to issues #2 and #3 (comments `7155478347`, `7155478894`, and follow-up `7155816807`) for the producer CLI/counters/checkpoint interface and independent verifier CLI/certificate/counters. Core #2 subsequently reported M1 and cap-accounting corrections through `99195d1a4179a46686b453919c5143e23aa1c6a8`; it is in-memory region algebra only and explicitly has no serializer/resume or certificate semantics yet. Core #2 accepts/adapts the proposed `p3-region-frontier/v1` target with scope-binding amendments, but waits for proof #3 to freeze exact grammar and verifier entry point. The proof-side region contract and interface-side P3 contract remain preparation/draft. Integrated P3 benchmarking is on hold until both agents agree on native interfaces and pinned source commits. No EDR-BB solver has been benchmarked; P3 harness tests use fake adapters only.

## Limitations and boundaries

- Raw P2 inputs and P3 input-only fixtures are recovered; original P2 journal/2 bytes are not.
- No P2 large-case closure, ledger ingestion, or hardened independent replay was run in this checkpoint.
- No 512 MiB failure is claimed.
- P3 harness mock tests do not validate EDR-BB mathematics or producer/verifier integration.
- Evaluation references remain outside the solver input directory.
- No external learner calls, baseline changes, PR merges, deployment, or operational acceptance.
