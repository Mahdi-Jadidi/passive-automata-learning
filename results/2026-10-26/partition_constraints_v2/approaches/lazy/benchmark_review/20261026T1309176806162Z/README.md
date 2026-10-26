# Candidate benchmark support — BMARK-A001

**Unexecuted candidate for independent auditor review.** No performance result is
claimed. This folder adds no dependency and changes no C002-R1 runtime source.
The auditor should review/adopt these files before executing them, after the
whole-set correctness audit. The harness contains **no correctness checker**.
It neither reads generator truth nor validates witnesses; the auditor must do
that independently for the captured full outputs before publishing comparisons.

## Integration

From the cycle root, using the same standard-library Python executable for all
methods (replace the output path with a new path for every attempt):

```powershell
& 'C:\Users\Mahdi\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B -X utf8 approaches/eager/benchmark_support/runner.py --output approaches/eager/benchmark_support/runs/NEW_UNIQUE_SUITE
```

Do not run this beside any other benchmark, correctness experiment or heavy job.
A local `.benchmark.lock` prevents overlapping copies of this runner, but cannot
detect unrelated programs. Existing output directories are refused. If a process
is forcibly killed, retain its directory and lock as evidence; verify its owner
has stopped before manually removing only that lock. Never reuse the old suite.

The runner imports the existing `audit/capture.py` without editing it. Execution
will write its ordinary immutable attempts under `audit/attempts/` and deduplicated
source/input blobs under `audit/source_blobs/`, plus suite files under `--output`.
The candidate's preparation did not execute it or write those audit artifacts.

## Fixed design

- Only frozen `performance_100` input objects are serialized into solver input
  files. The dataset file, all input hashes, exactly 100 cases, and the C002-R1
  manifest and six source hashes are checked. Truth sidecars are never opened.
- There are 900 timing jobs (100 × 3 methods × 3 repetitions), followed by 300
  **separate** tracemalloc jobs (100 × 3 methods). Every job is a fresh Python
  process. No benchmarks run concurrently. Sorted case IDs and rotating method
  order give each method each ordinal position once over three timing repeats.
- The worker invokes the **unchanged `solver.py` via `runpy.run_path(...,
  run_name="__main__")`**, passing the actual CLI arguments. It does not re-create
  or optimize solver logic. Full stdout is the driver's actual output.
- Each subprocess has a 30-second external timeout, reduced to the remaining
  method budget when necessary. The same value is passed as cooperative solver
  timeout. A shared 900-second budget **per method across timing and memory**
  counts actual subprocess wall time including startup, not snapshot/capture
  overhead. Explicit `budget_skipped` rows retain every unexecuted planned job.
  Memory may consequently be partly or entirely skipped after costly timings.
  OS process creation/termination scheduling can cause a small wall overrun;
  timeout caps and actual elapsed times are both retained, never rounded down.
- Runtime sources are checked before/after the suite and before/after every
  subprocess; corpus/support source manifests are retained before/after. Source
  drift aborts remaining jobs. The before/after checks cannot rule out a malicious
  transient edit restored between checks; freeze the workspace during execution.

## Measurements and interpretation

`*.worker.json` records `pipeline_seconds`: after worker bootstrap and before
`runpy`/driver imports, through input reading, preprocessing, search, JSON
serialization and stdout/stderr flush to the capture pipe. The tiny identical
`runpy` infrastructure cost is included. Python interpreter startup, worker
bootstrap imports (`sys`, `time`), and writing the metrics sidecar are excluded.
This is a repeatable measured pipeline boundary, not a claim of isolated search
time. A timed-out/forcibly killed process may have no sidecar.

`process_elapsed_seconds` times precisely the existing capture module's
`subprocess.run` call, including startup and shutdown. A module-local proxy adds
this timing without altering the global subprocess implementation or capture
source. `capture_elapsed_including_overhead_seconds` preserves capture's own
duration, which includes source snapshots and most artifact writing. It **must
not be reported as algorithm runtime**. `total_harness_seconds` also includes
input preparation, analysis and metadata I/O. Snapshot preparation is outside the
per-process timeout and method process budget.

Memory mode starts `tracemalloc` **before** importing `runpy`/driver and parsing
the input, then reads current/peak allocation immediately after output flush.
It measures allocations tracked by Python's allocator since that start; it is
not OS peak RSS, excludes already-created bootstrap objects, and need not include
native allocations. Sidecar serialization is outside the traced interval.
Memory-mode elapsed time is diagnostic only and is never compared as speed.

Each executed job retains all original provider metrics and search counters,
output byte count/hash and a reference to the complete raw JSON in the capture
attempt. Missing baseline node/constraint counts remain **missing**, not zero.
Eager `preprocessing_seconds` includes its eager formula construction; lazy's
same-named field covers initial graph setup only. Lazy `separation_seconds` and
`cut_generation_seconds` remain separate online phases. Counters for restarted
DFS include repeated internal work. No field-level equivalence of unlike phases
is implied, and no residual time is mislabeled as pure search.

## Status and evidence

`jobs.jsonl` is append/flush/fsync per job. Plans enumerate all 1200 job IDs.
Every subprocess goes through existing `audit.capture.capture`, preserving its
command, environment, source/input snapshots and raw stdout/stderr. Input and
source blob storage is content-addressed. Metrics sidecars are also snapshotted
after completion. Ordinary Ctrl-C during a capture is deferred until raw output
is saved (bounded by that job's timeout); remaining jobs get explicit abort rows.
Hard process termination, power failure or an uncatchable OS signal can leave an
open attempt: preserve it and have the auditor record that limitation rather
than reconstructing output. An active capture interrupted outside this deferral
can lack a final raw record; its started manifest still remains evidence.

The existing capture tool generically marks nonzero exits `program_error`.
The runner **does not modify that raw evidence**. It classifies exit 3 as
`incomplete` only when complete=false, status=incomplete, the feasible total is
null and a matching worker exit sidecar exists. Exit 0 needs a complete result
contract. Other failures are kept as timeout, environment_error, capture_error,
or program_error. A valid incomplete result is never called a solver bug, unique,
or conclusively infeasible. Malformed JSON/sidecars and missing sidecars are
recorded separately from genuine external timeout. Original full/partial stdout
always remains in the capture attempt.

`summary.json` reports censored/skipped/error counts separately. Preliminary
paired summaries require **all** repetitions of both methods to be complete;
per-case medians are computed before distributions/ratios. No censored run is
imputed as 30 seconds and no speed ratio is made from memory-mode times. These
summaries are explicitly pending independent full-set/witness validation.
They are descriptive of this corpus only, exclude incomplete cases with a stated
denominator, and establish no general speedup or statistical significance.

## Preparation record and limitations

This is a new support idea, not a correction to A001's mathematical method.
No runtime, common file, audit file, existing report or Git state was edited.
No subprocess benchmark, solver experiment, or memory experiment was run while
preparing it. Independent review and a recorded harness smoke run are still
required before the expensive suite. Syntax-only inspection is not evidence of
runtime correctness.

A read-only PowerShell manifest inspection first failed because
`ConvertFrom-Json` rejects an empty-string property without `-AsHashtable`;
rerunning that read with `-AsHashtable` succeeded. No solver execution was
involved. Original terminal outputs remain in the task transcript; no separate
raw shell log was saved, so one is not fabricated here.
