# A's static mathematical/code review of B

Date: 2026-10-26. Scope: approaches/lazy/lazy_solver.py and PROOFS.md as read
for this review; shared candidate API from A. No new experiment was run for
this follow-up. This is not the independent empirical audit.

## Decision

No substantive mathematical or algorithmic correctness defect was found in the
lazy cut, enumeration logic, ownership blocking, or declared incomplete-result
fields. The two reporting clarifications below should be preserved in the final
report. Acceptance of measured correctness/performance remains with the auditor.

## 1. Cut soundness and progress

The separator selects a negative n and positives p0,p1 whose projections match
n on the current side zero and side one, respectively. The two-match cut is
T_0(n,p0) OR T_1(n,p1). Both terms are false at the selected current assignment.
For any feasible partition, n differs from EVERY positive on at least one side
s, so it differs from p_s and satisfies this cut. The code constructs the same
expression from the shared deterministic distinguisher function. It does not
replace the full feasibility condition by independent per-positive choices of
rejecting side. Thus the selected candidate is excluded and no feasible
partition is excluded.

The syntactic cut cache assertion is justified: a candidate returned by the
shared engine satisfies every already stored cut. It cannot violate the same
cut again if the engine and distinguisher equivalence are correct. An assertion
failure here should remain an archived implementation failure, not be hidden.

## 2. Complete enumeration and answer uniqueness

The shared engine canonicalizes ownership by fixing x_0=0 and excluding the
all-zero assignment. A completed feasible record is followed by the exact
ownership blocker OR_i[x_i != value_i]. This clause excludes exactly one
assignment, even though its anchor literal is always false. There are no
auxiliary witness variables to generate duplicate ownership answers.

Every assignment RETURNED by find_model either receives its answer blocker or
a sound cut excluding that assignment. Hence no returned candidate repeats.
There are at most 2^(m-1)-1 such candidates. When find_model reports no remaining
model, every feasible assignment has been emitted: cuts preserve feasible
unreported assignments, and answer blockers exclude only reported ones.

## 3. Determinism and boundaries

validate returns sorted unique positive/negative words and sorted symbols.
The separator's setdefault therefore stores the lexicographically first
matching positive, and its negative loop picks the first offending negative.
Both empty-class cases yield every canonical partition; absent symbols remain
variables. Contradictory labels are rejected by baseline validation.

The main try block catches cooperative SearchInterrupted and KeyboardInterrupt.
The shared result builder then returns complete=false, status=incomplete,
feasible_partition_count=null and a lower-bound found_partition_count. The
code does not infer a unique/infeasible result from a partial answer set.
Validation precedes this try block and final result construction follows it;
an uncaught process interruption or hard subprocess kill need not produce a
solver JSON object. Its incomplete/error state must be preserved by the external
runner. The branch documentation already distinguishes cooperative checks from
the hard subprocess limit; final prose must keep that distinction.

## Non-blocking reporting clarification R-B1

The proof phrase "No candidate recurs" is correct for assignments RETURNED to
the outer lazy loop, not for internal DFS states. find_model restarts from the
root after each cut/blocker and can revisit partial states or full assignments
that are then rejected by stored constraints. Therefore the bound on returned
candidates is NOT a bound on nodes_visited, constraint_evaluations, or cumulative
complete_assignments. These counters intentionally accumulate all restarted
work and may exceed 2^(m-1)-1. Suggested wording: "No outer-loop proposed ownership
assignment recurs; internal restarted search work is counted separately."

## Non-blocking reporting clarification R-B2

preprocessing_seconds in lazy records only the initial graph phase, whereas
eager preprocessing_seconds includes its complete formula construction.
Lazy's cut generation and separation occur later and are separately recorded.
Comparing those two preprocessing fields alone would omit lazy work. Use the
external end-to-end time (including parse, all preprocessing, search and output)
for method comparisons; phase fields are explanatory, not interchangeable
total costs. No performance result is inferred from this static review.
