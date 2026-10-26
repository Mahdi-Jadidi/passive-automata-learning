# B: exact lazy constraints

Scientific status: derivation under the fixed C002 assumptions; independent audit pending.

For a block B let P_B be the set of positive projections. A partition is feasible
exactly when each negative n has some block B with pi_B(n) absent from P_B.
Necessity follows from positive acceptance; sufficiency uses the finite regular
local languages P_B. This is the existing baseline criterion, not a novelty claim.

The A reconstruction lemma implies that unequal B-projections have a distinguishing
singleton or pair contained in B. Thus T_s(n,p), defined by the shared distinguisher
family, is equivalent to inequality of the side-s projections. Removing pairs
containing an already distinguishing singleton preserves this equivalence.

For an infeasible candidate choose one negative n supported by positive projections
on both sides, with matching positives p0 and p1. The cut is

    T_0(n,p0) OR T_1(n,p1).

Both disjuncts are false in the current candidate, so it is removed. For any
feasible partition, n has a rejecting side s whose projection differs from EVERY
positive projection; in particular it differs from p_s. Therefore that partition
satisfies the cut. The positive matches need not be the same word. Using a
different rejecting side per positive would not express the full feasibility
criterion; this implementation adds only the proved two-match cut.

Equivalently the eager constraint for n expands by distributivity into all clauses
T_0(n,p) OR T_1(n,q) for p,q positive. Lazy selects a violated clause of this
expansion. No stronger unproved generalization is enabled.

The shared engine fixes the first ownership variable to zero and requires at
least one one, giving one representative per unordered nonempty bipartition.
Graph equalities are the baseline's proved necessary conditions. A feasible model
is emitted with a direct projection witness, then only its exact assignment is
blocked by OR_i[x_i != assignment_i]. This removes no other model. Every infeasible
candidate receives a sound cut excluding itself. No candidate recurs; at most
2^(m-1)-1 candidates are processed before a final unsatisfiable search. Since cuts
preserve every unreported feasible model, termination enumerates exactly F2(S).
An identical cached cut cannot be violated by a model satisfying all accumulated
constraints; that situation is an implementation assertion failure, not a reason
to silently skip an iteration.

Empty positive samples make every negative rejectable by empty local languages;
the separator has no matches and all partitions are feasible. Empty negative
samples also allow all partitions. Contradictory labels are rejected by shared
baseline validation. Absent symbols remain variables. Lexicographic order follows
the shared validated sorted words and symbol order. Matches use first insertion,
so the first matching positive per side and the first offending negative are
deterministic.

All engine statistics accumulate across restarts. Timing includes graph building,
direct checks, cut generation and search; preprocessing_seconds measures the
initial graph phase, while cut_generation_seconds and separation_seconds expose
additional lazy overhead. Repeated searches and answer blockers can make lazy
slower than baseline or eager, especially when output is large. No efficiency or
novelty claim is made. The reconstruction and feasibility literature is documented
in ../eager/SOURCES.md and the frozen baseline literature review.

An interrupted run retains already constructed witness records, reports
complete=false, status=incomplete, feasible_partition_count=null, and a lower-bound
found count. It makes no uniqueness or infeasibility claim. Deadlines are cooperative
between operations; the auditor must enforce the hard subprocess limit because a
single baseline graph/projection operation is not preemptible.
