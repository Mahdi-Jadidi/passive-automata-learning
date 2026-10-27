# B focused static review: C003 performance suite

Scope: exact source/plan/capture/runtime snapshots in manifest.json. No suite,
test or provider was executed by this review; no observed execution failure or
actual source drift is asserted. Findings distinguish acceptance gates from
future interruption behavior. No file outside this owned review folder changed.

## Verdict and substantive acceptance gates

The requested first/second-answer tasks and basic fresh-process timing are fair
statically. Before accepting empirical results, an independent artifact verifier
must resolve P1 and validate returned solver outputs/statuses. No broad rerun is
requested: intact saved captures may supply the evidence needed for those checks.

### P1: source/plan binding is recorded but not verified by this runner

PLAN is assigned but never read. The suite reconstructs cases/jobs from current
input files instead of consuming or comparing its schedule against plan_v2.
RUNTIME is loaded, but none of its expected file hashes are compared against
actual bytes; it is used only to construct source_paths. capture snapshots the
actual source bytes but does not compare them to trusted expected hashes either.
The runtime/corpus manifest hashes written in summary describe current files,
not a prior trusted expected-value gate. Fixed-word input source and frozen plan
files are not included in base_sources; generated per-job input files ARE saved.

This does not prove the present run used a wrong source or job. It means the
runner alone cannot establish frozen-runtime/frozen-schedule compliance. Verify
each attempt's input/provider/support/capture hashes against the frozen manifest,
bind source input files to their corpus hashes, and normalize actual semantic
job keys to frozen v2 entries. Preserve a comparison verdict separately. If these
checks pass, lack of an in-run check by itself is not a reason to rerun providers.

### P2: interrupted capture does not stop remaining scheduling

The adopted capture hash matches B_CAPTURE_R1. It retains flushed output and
terminates/reaps its own direct child on cooperative KeyboardInterrupt/timeout.
But performance_suite does not branch on execution_status='interrupted': it
appends that record, charges its subprocess time and continues scheduling.
Thus a user interrupt during capture need not stop the suite. No such interrupt
was observed in this review. Any stop/resume policy should explicitly distinguish
this from a normal completed job. A kill outside capture's controlled cleanup or
in runner metadata code can still prevent summary finalization, as documented
for capture. Process trees beyond the direct owned child are not guaranteed.

## Frozen tasks, IDs, counts and equal-work comparison

For intact frozen inputs, static loop analysis gives general and fair-reference
the SAME 100 cases, max_solutions 1 and 2, three timing reps and one separate
memory rep: 800 jobs each. The 18 fixed-word cases use those same answer limits
and repetitions: 144 jobs. Total is 1744 performance jobs, comprising 1308 timing
and 436 memory jobs, matching the performance portion of the frozen plan's
method/mode counts. This is not a repeat of C002's 1200-job task.

The fixed-word subset selection (first/middle/last within each 20-case size group)
agrees with build_plan_v2's construction by static reasoning. General/reference
compare first/second answers, not first answers against forced old full F2.
Saved C002 F2 is loaded only as audit reference; workers receive input files.

Actual job IDs differ in spelling from frozen IDs (runner method:case:limit:mode:
replicate versus plan perf:method:case:limit:timeN/memory). They require semantic
mapping, not literal-string equality. Budget-skipped records use key 'limit',
while attempted records use 'max_solutions'; a coverage verifier must normalize
that difference or it can silently lose skipped-task strata. The suite itself
does not compare expected semantic IDs or enforce equality/uniqueness against v2.

## Time/memory scope and bias limits

Timing launches the unchanged CLI in fresh Python processes. capture's
subprocess_seconds includes interpreter startup, imports, input parsing,
provider work, JSON serialization, output flushing and direct-child completion,
with source snapshots/metadata instrumentation excluded. This is a valid
end-to-end process wall boundary if declared. It is not isolated search time.

profile_one reads input, imports the root CLI and loads the provider BEFORE
tracemalloc.start. It stops tracing after solve returns and BEFORE serializing
the result. Therefore tracemalloc_peak_bytes is PROVIDER-CALL traced allocation,
excluding input parsing, provider imports and output serialization. It also
excludes RSS and untraced native memory. It must not be named full-pipeline peak
or compared directly with C002's differently scoped full-pipeline tracing. The
profile_seconds timer is similarly provider-call time; memory-mode process wall
time remains instrumented and is not a speed comparison.

All general jobs run before all fair-reference jobs, then fixed-word. This is
method-block order, unlike plan construction's interleaved method loop. Within
a method, cases are grouped by size, with timing and memory adjacent per limit.
Method blocks introduce temporal/system-load bias; a paired timing difference
on this corpus is descriptive, not a universal causal speedup. Earlier small
cases can consume budget before larger cases; report denominators by size/limit
and actual outcomes rather than only aggregate averages.

## Hard limits, statuses and preservation

Every launch uses hard_timeout=min(30, remaining budget), with a 0.001-second
floor. Spent time uses actual capture subprocess_seconds per method, including
timing and memory. Actual process creation/cleanup can overrun the remaining
budget; that is charged rather than clipped. The floor can exceed a sub-millisecond
remainder, so 'exactly no overrun ever' is not justified. All later jobs become
explicit budget_skipped after the budget is spent. The fallback to zero for a
missing subprocess_seconds would undercharge an incompatible future capture;
the captured current version supplies this field. Future adoption should validate
the field rather than silently accepting its absence/non-finite values.

The worker's cooperative deadline is 30 seconds while the hard timeout can be
smaller for a nearly exhausted method budget. Such a hard cap is censorship,
not a demonstrated solver infeasibility. Memory worker prints a wrapper containing
result and exits zero even if nested result.status is incomplete; timing CLI
instead uses exit 3 for incomplete. The generic capture raw success/program_error
must therefore NOT be used as scientific completion. Post-validation must parse
the nested memory result versus direct timing result, validate every solution
and witness, and retain incomplete/exhausted/unknown distinctions and partial
output. The suite itself does not perform that scientific check or make a
validated timing ratio.

Capture preserves raw stdout/stderr, exact command, imported runtime source list
and per-job input snapshots before returning. Ledger append is unbuffered and
fsynced per attempt. Budget skips are also explicit rows. Runtime dependencies
listed in the manifest include support.py and the read-only prior graph source.
No process is launched outside capture in these two reviewed files. Capture
source hash matches the previously tested direct-child cleanup candidate; that
is provenance evidence, not a new independent child-reaping experiment here.

run.mkdir(exist_ok=False) avoids overwriting the fixed serial_v1 directory, but
there is no top-level try/finally reconciliation or resume scheduling after a
runner crash. Existing ledger/captures survive; missing final summary must remain
incomplete evidence. The fixed directory prevents a blind rerun in place, which
is preferable to overwriting; any later attempt needs a new run artifact path.

Summary planned/attempted/skipped counts alone establish scheduling, not scientific
success or comparable-case coverage. Preserve errors/timeouts without imputing
them as 30-second timings. Any usable comparison must use matching validated
case/limit/repetition tasks and disclose censoring and temporal-order limitations.
