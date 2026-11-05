# C022 proof boundaries and attempted counterexamples

These are mathematical checks, not executed tests or a new dataset. They specify what the independent auditor should exercise.

## 1. Dropping the validated-atom premise is invalid

Take alphabet abcd, P={bacd,abdc}, N={abcd}. The swap graph forces atoms ab|cd, but they are incompatible:

    H(ab)={ba,ab}, pi_ab(n)=ab
    H(cd)={cd,dc}, pi_cd(n)=cd.

There is no negative rejection record to transfer. Inventing one from a difference with an individual positive is the false quantifier exchange. It would certify a block that accepts the negative. A later coarsening can nevertheless be compatible: the single block abcd has H=P and rejects abcd. Thus incompatible atoms do not prove all coarsenings invalid; they require the unchanged exact fallback. Candidate transfer is inside `if atom_witness is not None` only.

Existing source: `results/2026-11-04/preflight_certificates_v19/theory/GRAPH_CERTIFICATE_LIMITS_v1.md`.

## 2. Splitting a rejecting atom invalidates the argument

Take P={abcd}, N={bacd,abdc}. Atoms ab|cd are compatible. Splitting them into a|b|c|d makes every local projection of both negatives equal its positive projection; the singleton partition accepts both negatives. There is no containing output block for either rejecting two-symbol atom. Mapping an atom to a block containing only one of its symbols is unsound. The candidate checks whole-atom containment before transferring any certificate for that alternative. Its internal constructor already produces actual coarsenings.

Existing source for the compatible starting example: `results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md`, T2.

## 3. Could merging introduce a new positive match?

Attempt: after merging, the negative might match the projection of a different positive, even though the old atom rejected it. This fails: the old rejection is against **all** positives, not one paired positive. Any full merged-block match projects to a match on the rejecting atom, a contradiction. No independence of the finite positive projections is assumed here, and H(C) need not be a Cartesian product of the atom projection languages.

## 4. Could output-block ordering invalidate the rejection index?

Attempt: `coarsenings` sorts its output blocks, so an atom index is not generally an output-block index. Directly copying `rejected_by_block` would be wrong. Candidate builds symbol-to-output-block ownership in the actual returned block order, then maps every atom to that index. It transfers the negative index unchanged and uses the mapped block index. The two alternatives may therefore select a different valid rejecting block from baseline replay, which is allowed by the contract.

## 5. Unknown K, absent symbols, and empty words

Without K, the constructor returns the one-block partition and the atom partition. Transfer applies to both when r>1 and W exists. The alphabet includes unseen symbols; atoms remain nonempty and the containment map covers them. Projection onto a subset is still a compositional deletion operation for empty words. No new exception to the theorem arises. If time or memory is exhausted, the unchanged interruption mechanism may return unresolved; it does not turn a partial transfer into a completed witness.
