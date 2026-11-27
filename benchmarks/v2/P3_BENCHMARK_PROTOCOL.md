# P3 benchmark adapter protocol (measurement-only)

## Native M2 execution

`p3_native.py` uses the existing harness fixture validator and capped process worker with the native CLI config in `p3/native.json`. It checks both checkout commits and the Git blob of each staged Python source. The producer and verifier load separate staged source trees. The runner stages the exact raw bytes, constructs a canonical empty journal/2 via the independent sample digest, and calls the pinned verifier's trusted-scope builder. The scope builder replays the journal and derives the root owner; the harness checks for an identity root on these raw-only fixtures. The producer receives `{input}` and `{scope}`. The verifier receives `{input}`, `{journal}`, `{scope}`, and `{certificate}`. The producer receives `--resume` and the path to its own partial certificate only for the resume phase.

Each case/profile runs one/all, normal/-O, two fresh trials and a one-entry checkpoint probe. Every usable certificate, including a partial certificate, is independently replayed. Each phase has a 30 s wall limit and its own 1536 or 512 MiB `RLIMIT_AS`. The config records the cooperative and logical caps inside those phase limits. The runner records native status/counters, exact artifact hashes, independent verdicts and per-phase process observations. Only a repeatable EXHAUSTED certificate accepted in both independent replays yields a certified result. A producer incumbent is a provisional upper bound; the identity root contributes a base lower bound of zero. Checkpoint equality compares certificate bytes and status, while fresh equality additionally compares native counters.

The Actions job sparsely checks out raw fixtures, the manifest, and source files. Evaluation references are absent from the worktree and the staged inputs. The processes share the runner filesystem, so this is input and import isolation. No filesystem sandbox is applied. See the workflow for the reproduction command and uploaded evidence.

## Legacy measurement adapter

The sections below document the measurement-only fake-adapter infrastructure. Native measurements use the pinned CLI config above.

## Isolation boundary

The solver receives one exact raw JSON file with exactly three keys: `alphabet`, `positive`, and `negative`. Alphabet order, trace order, duplicate traces, empty words, and original token strings are preserved. The harness verifies the raw file SHA-256 against `review03/p3/input-manifest.json` and copies only those bytes into a fresh run directory.

The harness never reads `review03/p3/evaluation/index.json` or any file below `review03/p3/evaluation/`; it does not pass an evaluation path, planted optimum, reference partition, expected cost, or generator metadata to either child. The input-only and evaluation-only ZIPs are stored separately in the Library. This is process/logical isolation, not an adversarial OS sandbox: the solver runs on the same host filesystem and must not be given or discover the evaluation directory.

## Adapter config

A JSON config uses schema `p3-benchmark-adapter/1` and contains `solver.argv`, `verifier.argv`, and optional `source_pins`. Command arrays are executed directly (no shell). Supported substitutions are:

- `{python}`, `{input}`, `{certificate}`, `{checkpoint}`, `{result}`
- `{work_cap}`, `{entry_cap}`, `{seconds}`, `{memory_mib}`, `{resume_flag}`

`{resume_flag}` is removed from argv when the run is not a resume. The solver config may declare a literal `resume_flag` (for example `--resume`). Do not add an evaluation/reference placeholder. Pin the producer and verifier commit/blob identities under `source_pins`.

Example shape (replace entry points/arguments only after Agent #2 and #3 agree):

```json
{
  "schema": "p3-benchmark-adapter/1",
  "source_pins": {"producer_commit": "...", "verifier_commit": "..."},
  "solver": {
    "argv": ["{python}", "-B", "solver_adapter.py", "--input", "{input}", "--certificate", "{certificate}", "--checkpoint", "{checkpoint}", "--result", "{result}", "--work-cap", "{work_cap}", "--entry-cap", "{entry_cap}", "--seconds", "{seconds}", "--memory-mib", "{memory_mib}", "{resume_flag}"],
    "resume_flag": "--resume"
  },
  "verifier": {
    "argv": ["{python}", "-B", "verifier_adapter.py", "--input", "{input}", "--certificate", "{certificate}", "--result", "{result}"]
  }
}
```

## Measurement envelopes

These are harness-only summaries; they are not solver certificates or a production wire schema.

Solver writes `{result}` as:

```json
{
  "schema": "p3-benchmark-solver/1",
  "status": "COMPLETE_CANDIDATE | COMPLETE_INFEASIBLE | INCOMPLETE | INVALID",
  "counters": {
    "generated_regions": 0,
    "expanded_regions": 0,
    "exact_checks": 0,
    "pruned_regions": 0,
    "frontier_size": 0,
    "work_units": 0,
    "entry_count": 0
  }
}
```

The adapter writes the actual native proof/frontier bytes to `{certificate}` and a restartable checkpoint to `{checkpoint}` when incomplete. `COMPLETE_*` requires a complete search artifact, not merely an incumbent. The adapter maps native counters without synthesizing values.

The independent verifier writes `{result}` as:

```json
{
  "schema": "p3-benchmark-verifier/1",
  "status": "VERIFIED | INVALID | INCOMPLETE",
  "counters": {"regions_replayed": 0, "exact_checks": 0, "frontier_size": 0}
}
```

Agent #3's checker remains independent: no producer DSU, cache, pruning, or validation imports. `VERIFIED` must mean complete independent replay under the agreed P3 proof contract. Unknown or unresolved frontier work is `INCOMPLETE`; malformed/contradictory proof evidence is `INVALID`.

## Execution and recorded metrics

`p3_harness.py` runs solver and verifier as separate subprocess phases. Each phase gets its own hard wall timeout and `RLIMIT_AS` address-space cap; observed peak RSS is recorded separately from that cap. The harness records exact argv and argv hash, stdout/stderr hashes and byte counts, result/certificate/checkpoint hashes, elapsed wall time, peak RSS, source pins, input hash/dimensions, and all counters above. Solver and verifier elapsed time/RSS are never combined.

Deterministic replay runs the solver at least twice in fresh directories and compares certificate SHA-256, solver status, and counters. Optional `--restart-probe` runs a low-work-cap attempt, requires a checkpoint for an incomplete attempt, resumes it, and compares the resumed certificate hash to the uninterrupted result. Restartability is reported separately from mathematical verification.

Use separate normal and optimized invocations. Example:

```sh
python -B benchmarks/v2/p3_harness.py \
  --manifest benchmarks/v2/review03/p3/input-manifest.json \
  --input-dir /path/to/p3-exact-search-inputs/inputs \
  --config /path/to/p3-adapter.json --case tiny_choice \
  --output /tmp/p3-tiny-normal --python-mode normal \
  --seconds 30 --memory-mib 1536 --work-cap 10000000 --entry-cap 2000000 \
  --repeat 2 --restart-probe

python -B -O benchmarks/v2/p3_harness.py \
  --manifest benchmarks/v2/review03/p3/input-manifest.json \
  --input-dir /path/to/p3-exact-search-inputs/inputs \
  --config /path/to/p3-adapter.json --case tiny_choice \
  --output /tmp/p3-tiny-optimized --python-mode optimized \
  --seconds 30 --memory-mib 1536 --work-cap 10000000 --entry-cap 2000000 \
  --repeat 2 --restart-probe
```

Run a 512 MiB trial in a fresh output directory and report it separately; it is not a substitute for the 1536 MiB run. `RLIMIT_AS` is a virtual-address-space cap, not an RSS cap.

## Fail-closed status

- `VERIFIED`: solver reports a complete result and the independent verifier returns `VERIFIED`; deterministic replay did not fail.
- `INVALID`: raw input/hash, adapter envelope, or independently checked evidence is malformed/contradictory.
- `INCOMPLETE`: timeout, memory/process censoring, work/entry cap, incomplete search, unresolved verifier frontier, or deterministic replay mismatch. No complete result is claimed.
- `NOT RUN`: raw input or agreed adapter config is unavailable; no process was started.

`operational_status` remains `INCOMPLETE` for all local structural experiments. No external learner calls or operational acceptance are implied.
