# C003-GENREVIEW-A001 — static cross-review of general candidate

Decision: **no blocking cut/quotient/traversal correctness defect identified** for
the documented valid-input, finite-deadline domain. The candidate is suitable
for the independent auditor's frozen tests, subject to the API/documentation
finding below. This is not empirical acceptance and is not a performance result.

No module was imported/executed, no test/benchmark was run, no implementation was
changed. Only this structural/general_review/REVIEW_001/ directory was written.
Exact reviewed bytes, including the read-only prior graph dependency and C003
contract, are saved under snapshots/ and hashed in MANIFEST.json. Line numbers
below refer to snapshot support.py; future revisions need a new review.

## A1 — P2 API/documentation mismatch: validation interrupt is not translated

support.py:100 calls validate(data) BEFORE the try at line 110. KeyboardInterrupt
during validation/normalization therefore propagates instead of reaching the
except (Interrupted, KeyboardInterrupt) at lines 164–165. General README's
unqualified statement that interruption returns status=incomplete is broader
than the implementation. Existing solution records cannot be lost at this point
because search has not begun, but the promised provider JSON/status is absent.

Static action for owner/auditor: either include this phase in cooperative
interruption handling in a new source revision, or explicitly qualify the API
promise and ensure the external supervisor preserves the interrupt as such.
This finding does not refute any returned partition or cut; it matters to
interruption-contract acceptance. It was not triggered experimentally here.

Deadline checking also starts only at line 111, after validation. Even an expired
deadline does not bound the amount of pre-check normalization work. PROOFS.md
already discloses nonpreemptible validation/helper operations; the supervisor
must retain the external cap rather than calling this a strict hard provider
bound. Long project()/graph/family inner operations may similarly finish after
the nominal deadline before the next cooperative check.

## A2 — P3 API hardening: nonfinite/ill-typed deadline values are not validated

check() at lines 11–13 only compares perf_counter >= deadline. A NaN compares
false, disabling that deadline; positive infinity never expires; a string causes
TypeError rather than ValueError. This follows from the comparison, without any
runtime probe. These are outside a valid absolute finite perf_counter contract,
so this is not a correctness objection for valid calls. Root/API validation
should enforce/document the same domain for both providers. The structural
provider already explicitly rejects those values. max_solutions validation,
including bool rejection, is correctly present at lines 101–103.

## Positive review: exact quotient and symmetry

The imported prior witness_graph source was read and snapshotted, not modified.
Only witness_graph is called; the old 2..10-symbol validate function is not used.
General validate independently permits arbitrary finite alphabet size >=2,
normalizes duplicate/reordered words, retains absent symbols and rejects unknown
symbols/contradictions.

Both imported edge rules are necessary same-owner constraints. If an adjacent
positive/negative swap exchanged distinct owners, neither side projection would
change and the negative could not be rejected. In insertion rescue, the side
containing inserted a sees the negative in the rescued positive, and the other
side sees it in the base positive whenever a,b have different owners. Thus any
feasible partition must place a,b together. Connected components are consequently
valid indivisible variables; no feasible ownership is removed by quotienting.

The actual graph routine traverses sorted alphabet, starts each new component
at its first unseen symbol and sorts its contents. Component zero therefore
contains the smallest alphabet symbol. Fixing prefix=(0,) (117) removes exactly
global side-swap symmetry; requiring a one in the full assignment (135–136)
enforces nonempty second side. If there is only one component, that sole leaf is
discarded and complete exhaustion correctly proves general infeasibility.

## Positive review: distinguisher mapping and partial cut soundness

family() first collects count-differing singletons. Pairs containing such a
singleton can be omitted: owning the pair implies owning that singleton, already
a distinguishing term. Other unequal pair projections contribute their owner
component indices; collapsing equal indices preserves conjunction because all
symbols of a component have identical ownership. This remains true with repeated
symbols and singleton blocks. The known singleton/pair reconstruction argument
therefore gives the required T_s(n,p) equivalence on quotient assignments.

direct() chooses a negative n whose projection appears among positives on both
sides, with lex-first matching p0/p1 because observations are sorted and setdefault
keeps the first. The new cut T0(n,p0) OR T1(n,p1) is globally valid: a feasible
assignment rejects n on one side against ALL positive projections, in particular
against the fixed selected p_s. This argument does not depend on the source
candidate's other variable values. The code checks source exclusion at 157–158.

cut_value() (86–95) computes the disjunction of ownership conjunctions. True means
one term is already fully satisfied; unknown means some term is still possible;
false means every term has a known opposite owner. In particular false is stable
under extending a prefix and cannot exclude a satisfying completion. No unknown
value is used for pruning.

## Positive review: cuts added after prefixes were pushed

The stack is initialized once (117). A popped prefix (120) is checked against
EVERY accumulated cut (123–127), before descent or direct testing. When a new
cut is appended at 159, any previously pushed sibling/ancestor frontier prefix
will be checked with that cut on its future pop. Already explored invalid leaves
do not need to be revisited, and a globally sound cut cannot invalidate an
already saved feasible leaf.

The pending stack represents disjoint frontier subtrees. Each non-root prefix
has exactly one parent; that parent is popped at most once and pushes each child
exactly once (132–133). Induction shows no prefix or complete ownership leaf can
be visited twice. No stack reinitialization or root restart occurs in the loop.
Feasible leaves need no answer blocker. Discarding a false-cut prefix removes only
infeasible leaves; exhaustion covers all remaining canonical quotient leaves.

## First/second/exhaustion semantics

- A fully validated direct record is appended before the answer-limit check
  (140–144). max_solutions=1 therefore seeks one answer; 2 continues the same
  stack to a second; None never triggers a finite answer limit.
- Reaching the limit sets exhausted only when the frontier is actually empty
  (145). A nonempty frontier that might later be pruned leaves uniqueness unknown,
  a conservative result. Finishing the while loop sets exhausted=true (162–163).
- No answer with actual exhaustion means infeasible in general_regular_product.
  One answer plus exhaustion means unique in the sample-feasible class, not
  planted-factor recovery. Two distinct answers prove ambiguous even without
  exhaustion. A first answer plus unexamined frontier decides existence only.
- A caught interruption preserves appended answers and returns incomplete.
  During an unfinished traversal exhausted remains false, so no unique/none
  conclusion follows. Already stored two answers still establish ambiguity.
  For a second-answer request, decision_complete=true with one preserved answer
  refers to existence; the caller must inspect len(solutions), search_exhausted
  and status to know the second-answer task is unfinished.

Full witness records are constructed inside direct() before appending; a partial
failed local witness construction cannot enter solutions. Zero positives/negatives
have the expected vacuous projection semantics. No unobserved target is consulted.

## Fairness, timing and limits

general_solver.py and fair_reference.py load the same support source and differ
only by learn=True/False. They have equal quotient, canonical zero-first order,
direct check and requested answer limit. Learning can skip only infeasible leaves,
so the feasible answer order matches the no-cut reference. This is a fair
find-first/second comparator, not a reference forced to enumerate all answers.
It shares code and graph assumptions and MUST NOT serve as the sole correctness
oracle; the proof explicitly makes that distinction.

The comparison isolates learned-cut overhead/benefit AFTER the same graph quotient.
It does not independently measure the quotient's benefit against symbol-level
enumeration. That is a scope limitation, not unfairness for the stated comparison.
provider_seconds includes work after entering search, not wrapper/module startup,
root input parsing or external serialization. phase timers may omit interrupted
partial phases as already documented; they must not be equated to full external
time. No timing superiority follows from this static review or from node counts.

The C002 graph source is a real runtime dependency dynamically imported by path
(42–47); it must be explicitly frozen/supplied in every capture source list. No
runtime hash guard exists inside the provider, so external manifest validation is
part of reproducibility. This review records its actual bytes and sees no old
file mutation. Relocation must preserve the declared sibling C002/C003 layout or
be handled by a separately reviewed integration change.

No claims from general's reported smoke were independently rerun or certified
here. Auditor adoption/testing and any API fix remain with their respective owners.
