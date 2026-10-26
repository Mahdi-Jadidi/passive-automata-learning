# A cross-review of B-CAPTURE-R1 — CAPREVIEW-A001

Decision: **blocked for direct integration with the reviewed A benchmark runner**.
The capture callable's public arguments and legacy returned fields are retained,
but A's dependency on capture internals makes the two candidates incompatible.
This is static inspection only: no imports of either module, tests, experiments,
implementation changes, adoption, or empirical certification occurred.

Reviewed exact bytes are retained in `snapshots/`; hashes and source locations
are in `REVIEW_MANIFEST.json`. Candidate capture SHA256 matches the delegated
hash `68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf`.
All line numbers below refer to these snapshots, not a future adopted revision.

## Findings requiring integration changes

### R1 — P1: A's subprocess proxy prevents B from launching any job

A `runner.py:267` assigns `capture.subprocess = SimpleNamespace(run=...,
TimeoutExpired=...)`. B `capture_candidate.py:154` calls `subprocess.Popen`.
The namespace has no `Popen`; the access raises AttributeError before spawning,
which B's outer exception handler records as `capture_error` (lines 180–187).
Therefore adopting B as `audit/capture.py` with this A runner cannot execute the
planned suite. This follows directly from the attribute lookup; it was not run.

Required integration action: remove A's old `subprocess.run` timing proxy when
using B's capture. Use B's returned `subprocess_seconds` instead. Do not add a
second child/wrapper process or modify solver logic to work around this.

### R2 — P1: removing the proxy alone silently disables the method budget

A `runner.py:304–305` obtains `process_clock.get("seconds", 0.0)` and adds that
value to `spent[method]`. B never invokes `measured_run`, so after removing or
expanding the proxy this clock remains empty and each run is charged zero. The
900-second method budget then never decreases; A also reports a misleading
zero `process_elapsed_seconds`. B's new clock is not consumed anywhere in this
version of A.

Required integration action: explicitly consume and validate a finite,
nonnegative `attempt["subprocess_seconds"]` for both the ledger and budget.
Absence/invalidity must be an instrumentation error, not a zero fallback.
Record the capture source/version so old and new clock semantics cannot be mixed.

### R3 — P2: A does not preserve B's `interrupted` status

B adds raw `execution_status="interrupted"` at lines 167/179. A's classifier
(`runner.py:117–146`) recognizes raw timeout/environment/capture errors but not
interrupted. An interrupted child generally has no matching final sidecar and
is classified as `program_error`. If a matching complete sidecar exists, A can
even classify the interrupted capture as `complete`, because it checks exit and
JSON without rejecting raw interrupted. A's later interrupt_requested override
only handles the `program_error` case when A's own SIGINT flag was set; it is not
a complete interpretation of B's return contract.

Required integration action: handle raw `interrupted` before examining exit code
or JSON. Preserve any JSON/sidecar as evidence, but keep that execution censored
and out of complete comparable pairs. Retain `primary_execution_status` when
cleanup changes the raw result to capture_error.

### R4 — P2: failed cleanup must stop the benchmark supervisor

B explicitly reports `cleanup_error`, `child_reaped=false`, and capture_error
when `_terminate_and_reap` fails (lines 172–174, 201, 211–214). It does not claim
success in that case. A currently records capture_error and proceeds to the next
job; only source drift or a requested interrupt aborts the loop. If a launched
child remains alive, subsequent measurements could overlap it, violating the
serial benchmark design.

Required integration action: a returned cleanup_error or launched-but-not-reaped
child must abort remaining jobs and require supervisor reconciliation. No
automatic claim that the child stopped is justified. This is a conditional error
path found in code, not evidence that a cleanup failure actually occurred.

### R5 — P3: HANDOFF overstates duration_seconds' final boundary

HANDOFF says duration_seconds runs through output hashing/result assembly. In
the candidate result dictionary, duration_seconds is evaluated at line 198,
before stdout_sha256/stderr_sha256 at lines 205–206 and subsequent assembly.
It includes reading the files at line 190 but excludes these later hashes and
result.json writing. Correct this wording or explicitly move the boundary in a
new implementation revision. This does not affect subprocess_seconds and must
not be used to revise stored past durations.

## Static assessment of capture behavior and stated limits

- The callable signature and legacy keys are compatible at the public API level.
  Added keys are subprocess_seconds, child_pid, child_reaped and cleanup_scope;
  `interrupted` is an added raw status. Timeout/interruption now retain actual
  terminated-child exit codes. Downstream logic must prioritize raw status over
  those nonzero codes. Valid exit-3 incomplete JSON still needs scientific
  classification by the caller; B deliberately leaves raw nonzero exits generic.
- stdout.bin/stderr.bin are created before launch (141–142), then passed as
  direct unbuffered file destinations to Popen (150–155). This removes the old
  parent-PIPE accumulation loss on capture interruption. Both file handles are
  fsynced after cleanup (176–177). Child-side unflushed bytes and power/storage
  failure are correctly excluded from the promise in HANDOFF.md. Output hashes
  are computed from retained file bytes. Startup/final metadata is not claimed
  to be atomic or power-failure durable.
- The direct child's lifecycle is tracked by its Popen object. Normal completion
  is waited again; a live child is terminated, escalated to kill after a one-second
  wait, then waited/reaped. Repeated KeyboardInterrupt during cleanup retries.
  Cleanup exceptions become capture_error rather than false success. Descendants
  are not controlled, accurately disclosed; the reviewed solver worker does not
  intentionally launch child processes. Constructor-interruption ownership gaps
  and initial/final metadata interruptions are also disclosed, not certified away.
- subprocess_seconds starts immediately before Popen and ends after cleanup,
  before fsync. It includes startup, wait, termination/reaping and failed spawn
  overhead; it excludes source snapshots, manifest/environment preparation,
  fsync, stream hashing, and result writing. These boundaries match HANDOFF.md.
  It is a parent wall interval, not solver CPU time or the worker's pipeline clock.
- The `wait(timeout=...)` clock starts **after** Popen returns (162); subsequent
  cleanup can add up to a one-second terminate wait before kill/wait, and kill
  reaping itself has no finite timeout (229). Thus a 30-second argument does not
  enforce a strict 30-second launch-to-reap ceiling. HANDOFF.md openly describes
  the post-creation timeout and cleanup clock; reports must preserve these limits.
  Auditor adoption must resolve the intended cap semantics rather than label it
  an exact end-to-end hard wall bound. This is especially material to shortened
  calls at the end of a 900-second budget.
- A's worker README currently says stdout is flushed to a capture **pipe**. With
  B adopted, flush targets the capture **file**. The pipeline still covers output
  flush, but the destination and buffering differ from the old backend; update
  that measurement description and do not pool runs across capture backends.

The seven initial checks described in B's handoff were not independently rerun
or their attempt outputs verified in this scoped static review. They remain B's
reported evidence. Final adoption and any new smoke/performance execution belong
to the independent auditor. No scientific conclusion about eager/lazy correctness
or efficiency follows from this infrastructure review.
