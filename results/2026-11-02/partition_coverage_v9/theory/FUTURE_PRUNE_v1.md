# C009 future candidate — remaining-block rejection bound

Scientific status: mathematically sound under the stated C009 model.
Implementation status: **not implemented / not activated / not measured**.
No experiments or provider edits. This is a future step, not a change to
the current report, frozen v1 gates, scale cases, or performance conclusions.

## Assumptions and notation

Use the exact fixed labelled sample and rejection masks of PROOFS_v1.md:

    R(B)={j: π_B(n_j) is absent from {π_B(p):p∈P}}.

B and S below are nonempty symbol sets with B⊆S. Mask computation uses the
same original positives and negatives on both sets; this argument does not
allow dynamically deleting positives or changing labels.

## Lemma: rejection is monotone under enlarging a symbol block

    B⊆S  implies  R(B)⊆R(S).

Proof. Fix j∈R(B). If j∉R(S), some p∈P satisfies π_S(n_j)=π_S(p).
Project both sides further onto B. Since B⊆S, projections compose as
π_B(π_S(w))=π_B(w). Therefore π_B(n_j)=π_B(p), contradicting j∈R(B).
Thus j∈R(S). The argument also covers P=∅: every mask contains every
negative index, so the inclusion is immediate. ∎

## Corollary: necessary remaining-state coverage

In a nonempty DP state let rem be the remaining symbols, covered the
negative mask already rejected, and ALL the mask of every negative. If

    covered OR R(rem) != ALL,

there is no valid completion, for any requested remaining block count.

Proof. Every future block B is a subset of rem, so the lemma gives
R(B)⊆R(rem). Hence the union of all future rejection masks is contained
in R(rem). A negative index missing from covered OR R(rem) cannot be
rejected either by the previous blocks or by any future block. It must
remain incorrectly accepted, contradicting the exact feasibility criterion.
Therefore the completion count and all coownership counts are zero. ∎

The base case rem=∅ should continue to use the existing exact empty-state
test. This candidate does not require defining or precomputing R(∅).

## Limits

Passing the bound is only necessary, not sufficient for a given block count.
For example on rem={a,b}, P={ab}, N={ba}, R(rem)=ALL, yet a request for two
remaining blocks has no completion: both unary projections are positively
forced. The one-block remainder is feasible instead. Thus the bound cannot
replace the exact DP or its count constraints.

The current v1 precomputes masks for every nonempty symbol block, so a future
implementation could reuse R(rem). Its benefit depends on state distribution,
mask sizes and overhead; no speed, memory or scale improvement has been
measured. Worst-case state and branch exploration remain exponential.
Any implementation must receive a new frozen version and appropriate
independent checks; this note authorizes no silent modification of v1.

Decision: retain as a mathematically justified future-pruning candidate.
There are no run commands, seeds or captured outputs because no execution
was performed for this documentation-only lemma.
