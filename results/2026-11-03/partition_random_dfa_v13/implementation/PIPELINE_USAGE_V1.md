# C013 generate-to-C010 pipeline

`run_case_v1.py` is a separate standard-library helper. It does not modify or
import the frozen generator or solver. Before starting, it checks their exact
SHA-256 values. Generator and C010 CLI each run in fresh Python subprocesses
using the calling interpreter. C011 is never selected.

The following commands are reproduction recipes; neither has been executed.
Run from the repository root after the independent static gate clears:

```powershell
python -B results/2026-11-03/partition_random_dfa_v13/implementation/run_case_v1.py --devices 3 --alphabet-size 40 --max-length 64 --samples-per-label 8 --seed 20261103 --out results/2026-11-03/partition_random_dfa_v13/audit/example_k3_l64
```

Reuse the saved observations for a new solver process without regenerating:

```powershell
python -B results/2026-11-03/partition_random_dfa_v13/implementation/run_case_v1.py --devices 3 --alphabet-size 40 --max-length 64 --samples-per-label 8 --seed 20261103 --out results/2026-11-03/partition_random_dfa_v13/audit/example_k3_l64 --reuse-input
```

`--allowed-devices 1 2 3` can replace `--devices 3`; this affects world
generation only. Generator options `--length-mode`, `--event-profile` and
`--max-attempts-per-label` are forwarded. In reuse mode generation arguments
are recorded as requested metadata only; they do not relabel, validate against
the world, or replace the saved observational file. The actual input hash and
actual sample counts are authoritative.

Generated files are `OUT/data/world.json` and `OUT/data/solver_input.json`.
Every attempt gets a new `OUT/runs/UUID/` directory containing
`generation.stdout.bin`, `generation.stderr.bin` when generation is requested,
`inference.stdout.bin`, `inference.stderr.bin`, and `manifest.json`.
The pipeline never opens world.json; the solver subprocess receives only the
observational path. The input must have exactly alphabet/positive/negative.
The pipeline refuses to regenerate into existing data; reuse is explicit.

The manifest records interpreter/version, all source hashes including the
helper, exact command arguments, input hash, process exit codes, hard-timeout
status, stream hashes/bytes, and separate generation/inference wall times.
These process wall times include startup, reading, computation and writing the
captured streams; they exclude wrapper validation, hashing and final manifest
writing. Reuse records generation time as null, not zero. Total wrapper elapsed
time is not reported as inference time.

Default cooperative inference budget is 5 seconds and hard budget 7 seconds;
configure with `--seconds` and `--hard-seconds` (hard must exceed cooperative).
Generation hard timeout defaults to 120 seconds via `--generation-seconds`.
Raw stdout/stderr are retained even when empty, malformed, or cut off. A valid
JSON result is copied byte-for-byte to `result.json`; no fabricated solver
result is written when JSON parsing fails. C010 uses unknown/complete:false
for cooperative cutoffs. An external timeout is recorded separately and never
upgraded to a complete result even if a JSON fragment happens to be parseable.

C010 default output contains exact total/per-k counts and all symbol-pair
relations with witness partitions when it completes. This does not mean every
compatible partition is listed. `--enumerate` explicitly forwards C010's full
family enumeration and can be expensive; use only for prespecified small
controls. `full_partition_listing` is true only when enumeration was requested,
the process succeeded, the result is complete, and an enumeration list exists.

Generator exit 3 means a saved uniqueness/label shortfall. The pipeline still
solves the actual retained observations and records `generation_shortfall`.
Manifest `complete` concerns inference on those observations, not fulfillment
of requested sample counts. Reused inputs have generation_shortfall=null;
inspect their generation manifest/world with the independent auditor if needed.
Generation failure or hard timeout stops inference. Exit codes of the helper:
0 for complete inference, 3 for incomplete/failed inference, 1 for generation
or environment/input failure, 2 for CLI/integrity precondition failure.

The source/protocol freeze is in PIPELINE_READINESS_V1.json. No generator or
provider was run while writing this helper. Independent static review and
captured correctness controls remain pending.
