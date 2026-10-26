# B static harness review

Decision: this reviewed version is not acceptable as a completed audit harness.
No experiment was run and no audit/runtime source was edited. Exact byte snapshots
and hashes are in manifest.json beside this report. Changes made by the auditor
after this snapshot may resolve these findings; this report does not assess them.

Reviewed run_correctness.py SHA256:
ebb457f740b7e13ac4778c6322d4ee2009a74a17b84bbadcaa95d47a430b105a

Reviewed capture.py SHA256:
c764c2a06a65414e0fa1d45fa92631246423192d54aa28a3f6f3e08a9b0c58a9

## H1 — blocking final-summary program error

run_correctness.py line 321 stores result_paths[method] = path.name, a string.
Line 456 calls path.read_bytes() on those values when computing result_file_sha256.
This necessarily raises AttributeError for the nonempty four-entry mapping.
Even a fully passing batch therefore cannot write summary.json or return success.
Resolve file names relative to run_dir, or keep a separate actual Path mapping.
Preserve the failed run and fix as a new source version. This is a harness bug,
not a solver or mathematical refutation.

## H2 — blocking discrepancy-evidence loss

In the provider loop, check_complete_contract runs before case_results assignment
and output_handles[method].write. An incorrect or incomplete result raises before
its payload is saved. An elapsed-time failure also raises before saving it.
The exception record includes input/error/traceback but not the returned result,
method variable or expected set as structured fields. The comment claiming all
returned provider results were already saved is false. Save the raw returned
result before validating it, then attach validation outcomes. Preserve the
offending full output and original case before any minimization. No minimizer
exists in this script; mismatch shrinkage must be supplied separately rather than
claimed complete from this batch.

The same validate-before-save issue affects failing invalid/CLI-deadline checks:
outcomes are written only after their assertions pass. A surrounding capture can
save a traceback but not the redirected local stdout payload on such a failure.

## H3 — normalization coverage is incomplete

check_witnesses compares witness count/order directly against the raw negative
list. The providers correctly return witnesses for sorted unique negatives.
Consequently a valid input with reordered or duplicated negatives can produce a
false failure whenever a feasible record exists. Normalize expected observations
independently with sorted(set(...)), while still delivering the original input to
providers. Add explicit permutation/duplicate metamorphic controls; current
invalid-input cases test malformed inputs rather than accepted normalization.
This is a coverage gap even if the frozen corpus happens to be sorted/unique.

## H4 — interruption capture is incomplete

capture.py catches Exception but not KeyboardInterrupt. stdout/stderr are collected
in subprocess.PIPE and persisted only after subprocess.run returns or a caught
exception. A KeyboardInterrupt in the capture process can therefore leave only a
started manifest, no final interrupted status and no available partial output.
This falls short of the plan's preserved interrupted attempts. Use a finally path
and durable output streams with explicit interruption classification. Abrupt
unrecoverable kills still require supervisor reconciliation; do not promise a
final JSON result for every possible kill. Ordinary TimeoutExpired is handled
and preserves the bytes supplied by that exception.

## H5 — frozen-corpus integrity needs an explicit gate

The main frozen_v1 dataset/sidecar hashes are computed before and after the run,
but are not compared to the expected hash fields of their dataset specs here.
Per-case input_sha256 is mostly accepted from the record without recomputing it;
only the legacy extension receives explicit hash checks. A pre-run content change
with unchanged counts can pass before/after stability. A trusted frozen-manifest
anchor must also be checked before loading labels; before/after equality alone
is not evidence that these are the previously frozen samples. The legacy extension
does compare files against its own manifest, but a trusted external anchor is
still required to detect coordinated manifest/data changes.

## H6 — incomplete-result and progress coverage

status_result checks the incomplete flag/status/count shape, but does not validate
partial partition sets or their witnesses. The expired-deadline checks exercise
immediate empty partial results only, not interruption after some answers. This
cannot establish correctness of nonempty partial outputs. Validate those outputs
as a duplicate-free subset of the reference, with every witness checked.

The explicit mismatch early break is fail-closed: mismatch_count increments and
complete becomes false. I found no acceptance on that explicit break. However,
counters['cases'] is the planned dataset length, not completed cases, and
provider_error_count is initialized but never incremented; all exceptions are
merged into mismatch_count. Add processed/validated case counters and distinct
execution-error versus semantic-mismatch classifications. A killed process can
leave output files without a summary; their presence alone must never imply pass.

## Checks that are structurally sound within scope

normalize_partitions compares complete canonical partition sets and rejects
duplicate ownership records, empty blocks, missing/duplicated alphabet symbols.
Complete contracts check exact count, status, found count and complete=true.
check_witnesses independently recomputes positive projection languages and every
listed negative witness/all-unseen-side set, subject to the normalization flaw.

The independent project/direct_oracle implementations do not call provider helper
functions or Boolean engines. The small Boolean oracle enumerates local acceptance
values, while larger cases compare unpruned baseline with this independent direct
oracle before provider comparison. Comparing baseline wrapper to the immutable
baseline alone would be self-confirming; the additional direct oracle avoids
that sole dependency. Both oracles still use the same mathematical model, so they
are implementation checks, not independent proofs of the problem formulation.

Prior binary/abc/targeted tiers get the Boolean oracle when their dataset names
match. The legacy 3072 cases are loaded and label consistency checked using audit
truth metadata; providers receive only record['input']. This script does not by
itself enforce all named frozen_v1 tier sizes/seeds, uniqueness or the presence
of every old control/theory example: these need a reviewed corpus-validation gate.
No omitted tier can be inferred present merely from successful iteration.

capture.py uses unique attempt directories, content-addressed source bytes,
argument-list shell=False execution, and byte-preserving stdout/stderr on normal,
timed-out and caught-error paths. Only explicitly supplied sources plus capture.py
are snapshotted; the caller must include imported runtime/input dependencies.
duration_seconds includes source snapshot and manifest-writing overhead as well
as subprocess execution, so it is not a pure process/end-to-end solver timing
without a separate clock. This review does not inspect the performance runner.

All assertions require ordinary Python execution: -O/PYTHONOPTIMIZE would disable
most checks. Enforce that execution precondition or use explicit validation errors.
