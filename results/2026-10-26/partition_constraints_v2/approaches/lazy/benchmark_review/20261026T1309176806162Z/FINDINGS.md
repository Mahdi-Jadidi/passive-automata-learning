# B static cross-review of A benchmark support

Decision: candidate has a sound basic job/timing design for the ORIGINAL capture
API implementation, but capture-version compatibility is a pre-suite blocker
if the durable Popen candidate is adopted. Static inspection only; no benchmark,
syntax execution or harness test was run here. No A/audit/shared file was edited.
All claims apply to the exact copied files in manifest.json, not later versions.

runner.py SHA256 16876ce34ab9fe6f077e0925324770374a17964eadbb3b8bd97dfeca15b30d68
worker.py SHA256 f1bb4866244587ff02c31dccd7e23e7ba7451cdba3cdd901cab0379b5ae5b801

Both match PREPARATION_RECORD.json. The README hash also matches that record.
audit/capture.py at review is still the old run-based implementation, SHA256
c764c2a06a65414e0fa1d45fa92631246423192d54aa28a3f6f3e08a9b0c58a9;
its bytes are preserved as audit_capture_at_review.py. Therefore finding M1 is
conditional on adoption of the durable capture implementation, not a claimed
failure of the old pair. No failed execution is invented.

## M1 — blocking compatibility gate before durable capture adoption

main replaces capture.subprocess with SimpleNamespace(run=measured_run,
TimeoutExpired=...). B_CAPTURE_R1's capture_candidate.py instead needs Popen and
its cleanup uses TimeoutExpired. The injected namespace has no Popen, so that
combination fails during process launch with AttributeError. Its measured_run
never executes, process_clock remains empty, and process_seconds becomes 0.
Consequently the method budgets are not measured. The runner does not abort on
each program/capture error, so this can produce a large all-failure suite with
zero charged process time rather than useful 1200 executions.

Adoption must explicitly select compatible capture and runner versions. With the
durable API, prefer its subprocess_seconds result for budgets and process elapsed
time, without replacing capture.subprocess. Validate that this value exists and
is finite/nonnegative rather than defaulting absent timing to zero. If keeping
the old capture temporarily, retain this review's conditional status and account
for its previously reported H4 interruption limitations. A post-adoption captured
smoke is required before the expensive suite; this review does not run it.

## M2 — interrupted raw status requires explicit handling with the new API

classify explicitly handles raw timed_out, environment_error and capture_error,
but not interrupted. It falls through to JSON/sidecar/exit checks. It can label
a genuine raw interrupted attempt program_error, or even complete if a child
completed with code 0 and matching sidecar just as the parent was interrupted.
Only interrupt_requested from the runner's SIGINT handler triggers its later
reclassification/abort, which is not a general replacement for inspecting the
capture API's raw status (e.g. a direct KeyboardInterrupt). Add interrupted to
the authoritative raw-status handling when adopting that API. Do not reinterpret
the preserved raw result file. Ordinary timed_out is already authoritative and
excluded from complete summaries even if partial/complete stdout happened to
arrive before termination.

## Timing and budget checks that pass statically

worker starts its pipeline clock before runpy/driver imports and input reading,
then flushes stdout/stderr before stopping it. Formula building, graph work,
search and JSON serialization are included. Interpreter startup and sys/time
bootstrap plus sidecar writing are excluded and documented. With the old capture,
the module-local run proxy measures startup through subprocess.run completion,
without modifying the global subprocess module; snapshot/manifest work is outside
that process clock. Both phase boundaries are defensible if named accurately.

Memory mode starts tracemalloc before importing runpy/driver and reads the peak
after output flush, with sidecar serialization outside. The stated scope excludes
RSS and untraced native allocations. Memory process time is not used as a speed
metric. No pure-search runtime or universal memory claim is supported.

Spent time is accumulated separately for each method from its process elapsed
time, with hard_limit=min(30, remaining). Timing and memory share the 900-second
method budget; memory may be skipped after slow timings, explicitly documented.
The same cap is passed to the cooperative CLI timeout. A process timeout includes
startup and sidecar overhead, whereas the solver's soft timer starts later; a
hard timeout before sidecar completion is correctly retained as timeout rather
than being counted as a completed pipeline. Process creation/scheduling cannot
be strictly preempted by subprocess.run's timeout; actual time can overrun the
remaining budget slightly and is not clipped. With the old capture pair, no
unequal method-specific budget or omitted preprocessing was found.

## Job coverage and ordering

read_cases checks the fixed performance data-file hash, manifest dataset hash,
100 cases, unique IDs, record input hashes and exact learner-input fields. It
does not open generator truth. Given those 100 inputs, job_plan produces exactly
900 timing jobs (3 repetitions x 100 cases x 3 methods) and 300 separate memory
jobs (1 x 100 x 3), each launching a fresh process sequentially. Rotating method
order gives each method every position once for each timing case over its three
repetitions. There is no concurrent method advantage. The plan's fixed corpus
hash anchors size strata; the runner does not independently regenerate/check
the required 25-per-size strata or <=64-word condition.

Budget skips retain a ledger row for every planned job. Abort finalization fills
unexecuted IDs with explicit not-run states. A locally held lock prevents two
copies of this runner, not unrelated heavy work. Timing and memory phase order
is fixed, so all-method coverage should be reported from actual statuses rather
than inferred from the existence of a 1200-entry plan.

## Preservation, acceptance and remaining validation requirements

Executed jobs reference full raw stdout/stderr in immutable capture attempts;
input/runtime/corpus/worker sources and completed sidecars are snapshotted.
The ledger appends, flushes and fsyncs each row. Runtime sources are checked
before/after jobs; support/corpus drift is detected at suite finalization. Drift
aborts publication validity; already calculated paired summaries do not override
that abort. Abrupt kills can leave an unfinished active attempt/lock and need
explicit supervisor reconciliation, as documented.

classify is only a coarse execution-shape gate: it checks complete flag/status,
method/mode/exit and finite pipeline time, but not full F2, counts, witnesses or
nonempty partial output validity. This is explicitly delegated to the auditor.
Therefore even all-complete status is NOT scientific acceptance. The independent
checker must validate every benchmark output against its input/reference before
comparisons are published, including any incomplete output as a feasible subset.
Memory peak should also be validated as a finite nonnegative integer: classify
currently does not check it, and summaries accepts generic numeric values.

An uninterrupted suite with program errors or all budget skips still returns 0
when abort_reason is None. This is a harness-completion exit, not all-jobs-success;
the importer must inspect status counts and required job coverage rather than
accept exit 0 as a passing benchmark. The summary correctly states independent
validation is required. A stricter separate suite-validation verdict would reduce
misinterpretation without discarding error/censoring evidence.

Paired summaries require all repetitions of BOTH compared methods to be complete,
aggregate per-case medians first, show comparable case IDs/counts and preserve
censoring statuses. This avoids imputing a timeout as 30 seconds or treating
missing counters as measured zeros. Those distributions remain descriptive of
the selected completed cases; they do not establish general speedup. Fields
preprocessing_seconds have different method scopes, correctly explained in README.
