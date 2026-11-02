# C007-T002 static review of stable finest_solver_v3

SHA256 c783929cc75b0979cab679f82c0e43e3aceab014db0b2d063628d0302b33477a
matches master's stable hash and READINESS_V1. Snapshot/hashes in MANIFEST.json.
This review imports/runs no provider and executes no tests. The six theoretical
smokes and implementation's seven-case smoke are NOT independent acceptance.

Decision: no blocking mathematical error identified in COMPLETE cheap/adaptive/
reference/early-ambiguity certificates. Partial-result preservation findings P1/P2
below need independent-gate attention. This is not blanket acceptance of all
interrupt timings or malformed verifier inputs.

## P1: reference interrupts discard discovered compatible answers

_solve_reference stores feasible cuts and witness records (400), but its catch
at 410 returns _incomplete(..., [], None,...). A deadline/KeyboardInterrupt after
valid answers therefore drops ALL of them, their meet and their history from
the returned result. Complete=false/status=incomplete is conservative and makes
no false finest claim, but partial discoveries are not preserved in that output.
By contrast, deliberate reference truncation at 402 retains cut lists only in a
dict put into successful_separators; it returns partial_meet=[] and has no witness
records there. This differs from the adaptive list-of-step history schema.

The independent gate should distinguish safe lack of a final decision from the
requested preservation/replay of partial answers. If fixing, use a new source
version and preserve the tested V3 bytes; this reviewer implements no change.

## P2: adaptive asynchronous-interrupt snapshot can have mismatched history

At 427 append a new valid separator step, then at 428 assign current=_meet(...).
An actual KeyboardInterrupt between these actions or inside _meet can enter the
catch at 445 with the NEW history but OLD current. Returned partial_meet then
need not equal the meet reconstructed from successful_separators. Normal
cooperative _Stop from subsequent _direct happens AFTER current assignment and
does not have this particular race. The concern is static control flow, not an
experiment or observed counterexample. No complete/unique assertion is created,
but the returned partial proof state may fail replay. A consistent committed
snapshot or reconstructible history needs explicit gate coverage if arbitrary
interrupts are claimed. No correction is activated here.

## Proof review: cheap forcing certificate

solve uses graph components as current ONLY for a direct compatibility shortcut
(338–355). If incompatible, it starts adaptive state at [alphabet], not atoms.
This matches the sandwich bounds: graph coownership is a LOWER equivalence bound;
the meet of found feasible cuts is an UPPER equivalence bound. These are not
interchangeable. verify_result replays exact old swap/rescue labels and occurrence
roles, rebuilds components over every declared symbol, requires claimed components
AND witness partition equal those components, and recomputes direct compatibility.
Thus cheap success proves unique finest, not merely a compatible candidate.
Connected components=one block yields one_block_only with trivial feasibility.

## Proof review: adaptive and complete cover

Only validated graph atoms define the binary search space; current meet is NOT
used as a forced ownership restriction. _refines_cut returns true iff no current
block crosses the cut. Such compatible cuts are nonseparators, not discarded as
invalid. Any other feasible cut strictly refines current by intersection, with
history containing its full independently recomputable direct witness. No active
meet block is assumed inseparable. Successful count is <=m-1 by block increase;
the actual oracle rescans binary masks each round, potentially exponential.

Final cover is stronger/larger than the minimal theoretical constrained cover:
it covers ALL canonical atom bipartitions, not just those splitting current.
Verifier requires unique integer/nonbool masks, exact expected cardinality and
membership for every canonical mask. Each mask either has a genuine negative
collision with both positively labeled matching sides, OR an exactly validated
compatible witness which does NOT split the claimed meet. Graph witnesses justify
the excluded symbol cuts splitting atoms. No searched prefix/count substitutes
for coverage. Full feasible binary answers can never be silently omitted.

_verify_no_separator starts computed=[alphabet], validates every history cut as
a full alphabet bipartition, recomputes its witness and requires strict progress.
It THEN intersects ALL feasible cuts in the final complete cover. Equality with
the claimed meet is required. This handles reference certificates with empty
history correctly: final feasible cuts reconstruct the actual meet from scratch.
An empty binary family yields computed=[alphabet]. When graph atom count is one,
the empty mask cover is justified by replayed graph connectivity. This does not
accept unexplained empty covers on disconnected atoms.

This reconstruction plus the nonsplit check enforces BOTH equivalence bounds.
A claimed too-fine meet fails reconstruction; a too-coarse meet is split by a
valid cut and fails the nonsplit check. Earlier history need not be re-visited
by search; verifier recomputes its compatibility directly. Each actual compatible
cut necessarily respects valid graph atoms even if not separately enforced in
the final-history loop, by the sound-edge theorem.

## Early infeasible partial meet

After each new validated separator, solve directly tests the new meet. If it
fails, early_infeasible_meet contains >=2 feasible strict-refinement steps and a
negative whose projections are seen on EVERY meet block. The verifier rebuilds
history from one-block, checks valid two-block partitions and full direct
witnesses, correct strict-refinement predicate, no split of graph atoms, and
exact equality to the claimed partial meet. It then recomputes the full collision.
By coarsening closure no feasible finest partition can refine all these feasible
cuts while their meet is infeasible. Therefore multiple maximal refinements EXIST.
No final meet or explicit frontier is claimed; meet_is_final=false is accurate.
The previous inverted predicate failure is not present in the stable branch.

## Reference reconstruction, stopping and scope

Reference enumerates all canonical graph-atom bipartitions, meets ALL compatible
answers starting at one-block and emits the full cover. Early max_solutions is
explicitly incomplete unless it actually reached the last mask. Final direct
checks distinguish finest_unique, multiple_maximal_exist and one_block_only.
Cheap success is deliberately bypassed in reference mode: this is a matched-task
finest target reference, not the old C006 first-answer task. Different proof/output
sizes remain relevant to end-to-end timing; speed cannot follow from round counts.

The parent is hash-checked, and only the old q-free graph extraction is used.
No finite q, known k, state cap, hidden target or real-system query enters solve.
Enhanced C006 A/B are inactive. Positive-only/no-positive inputs can yield
singleton finest by convention, not recovered architecture. One-block-only does
not mean invalid data or no regular model. No kmax/frontier enumeration follows.

Validation/final verification has no general deadline preemption; verify_result
expects complete results and is not itself a partial-result verifier. Malformed
witness partitions can reach _direct before _valid_partition in the finest branch
and may raise instead of returning valid=false. This is a totality/hardening
boundary; complete valid producer certificates above have no such shape issue.
These limitations must remain separate from accepted gate coverage. All exact
source versions and failed attempts remain owned/preserved by implementation.
