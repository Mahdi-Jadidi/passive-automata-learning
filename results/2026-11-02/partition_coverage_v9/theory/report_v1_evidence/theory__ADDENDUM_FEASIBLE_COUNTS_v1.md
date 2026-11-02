# C009 short corollary — sample upper bounds on the number of blocks

Direct proof; no experiments or implementation changes. Original proof,
ledger and reviewed provider snapshots remain unchanged.

## Assumptions

Use exactly the unrestricted independent regular-factor model of PROOFS_v1.md:
known disjoint nonempty alphabet, exact finite complete-word labels, no prime
or state restriction. First ignore trusted K and examine every k=1,...,m.
Assume the full sample version space is nonempty. With contradictory labels
or another inconsistency there is no kmax and no vacuous bound on a true model.

## Corollary C1: the unrestricted feasible counts form an initial interval

Let c_k count feasible partitions with k blocks and

    kmax = max{k: c_k>0}.

Then c_k>0 exactly for k∈{1,...,kmax}.

Proof. The maximum exists because there are finitely many partitions and
at least one is feasible. Merge any two blocks B,C of a feasible model and
give the merged block the regular language

    H={u∈(B∪C)*: π_Bu∈F_B and π_Cu∈F_C}.

Its global language is unchanged, so the merged partition remains feasible
with one fewer block. Starting at a kmax-block witness and repeatedly
merging realizes every count down to one. Counts above kmax are infeasible
by definition. ∎

Consequently exact completed per-k counts at default K certify a **sample
upper bound** k_true≤kmax, conditional on the true system belonging to this
model class. They never establish k_true=kmax without extra information:
the same observations also permit the one-block merge. No data-derived
lower bound greater than one is possible in this unrestricted class.

## Corollary C2: trusted count information can meet the upper bound

For any trusted allowed set K, the feasible counts are exactly

    K ∩ {1,...,kmax}.

This does not make them contiguous when K is noncontiguous. If a separately
verified lower bound says k_true≥h, then h>kmax is model/assumption
inconsistency; h=kmax forces k_true=kmax. If h<kmax and that lower bound
is the only count restriction, multiple counts remain feasible. These are
conditional conclusions, not validation of the supplied lower bound.

The doubled-pairs sample in PROOFS_v1.md T7 has kmax=3; trusted k≥3 thus
identifies the count. In that particular sample it also identifies the
partition because c_3=1. Identification of the count alone generally does
**not** identify ownership. For example on Σ={a,b,c}, let

    P={ε,abc},   N={a}.

The singleton partition is infeasible: every projection of a appears among
positive projections on its block. The partitions ab|c and ac|b are both
feasible, since on the respective a-containing block the negative projects
to a whereas positives project to ε and ab, or ε and ac. The third two-block
partition a|bc is infeasible: a and ε are forced locally by positives and
therefore accept the negative. Thus kmax=2, c_2=2. Trusted k≥2 fixes the
count at two but leaves these two ownerships. The one-block merge remains
feasible in the absence of that trusted lower bound.

## Scope and rejected inference

Coarsening may violate primeness, a fixed local-state budget, or a different
restricted model class. The interval theorem and upper-bound inference are
not automatically transferable to such classes. Under default K they also
require complete per-k feasibility evidence; a timed-out search cannot
certify that no larger count exists. Merely selecting the largest found k
is neither an exact kmax computation nor recovery of nature's declared k.

Decision: direct corollaries confirmed under these stated assumptions;
independent review pending. Scientific status is not an executable gate.
