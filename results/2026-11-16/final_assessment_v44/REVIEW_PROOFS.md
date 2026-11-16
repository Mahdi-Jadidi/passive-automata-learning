# AI-assisted proof and implementation review

This is a read-only AI-assisted review of ARTICLE_EN.md and the frozen V43 encoding.py, optimizer.py, and verify.py. It is not independent scientific peer review or formal software verification.

## Finding

- **Reporting mismatch, limited to producer self-checking.** Article Algorithm 1, step 6 says “Self-check the result, then return OPTIMAL,” and section 8 describes timing as including “self-checking where implemented.” In optimizer.py, the symbol-bound, atom-bound, and single-negative shortcuts return immediately, before the general path's `E.feasible`/DRUP replay checks. The edge-size general route checks feasibility but does not invoke the consumer's edge-bound verification. The externally callable `verify_optimal` can independently check these certificates. Clarify that producer self-checking applies to the general path as implemented, and that full consumer verification is separate; do not imply every returned shortcut has been self-checked. This observation does not establish an incorrect optimum or certificate.

## Proof assessment

Theorem 1's projection criterion and monotonicity, Theorem 2's mandatory-symbol contraction, and Theorem 3's minimum-witness bound follow from the stated unrestricted finite-language model. The empty-alphabet convention is handled separately. Theorem 4's coverage argument is valid: a distinct minimal witness omits some element of a known minimal witness, so the exclusion children cover it; pruning a region contained in a pending larger region preserves coverage, and skipping an already processed region is safe because it was either false or delegated to strictly smaller children. Deletion minimization yields an inclusion-minimal witness by monotonicity. The implementation matches these operations.

Theorem 5's equivalence relation, witness gates, representative variables, and threshold recurrence express compatibility and block count as claimed. The implementation's three transitivity clauses and fully equivalent gates match the specification. Theorem 6 follows conditional on correct finite operations, complete extraction, and sound and complete SAT, with feasible incumbents and monotone threshold bounds. The stated structural and DRUP certificates supply the respective upper bounds; the consumer reconstructs the encoding rather than trusting a supplied CNF. Theorem 7's mandatory-pair argument gives m-1 blocks and polynomial preprocessing on the stated family; the Bell-number claim is expressly relative to the specified baseline.

The checker shares the deterministic encoder and extraction with the producer, as disclosed in the article, so its acceptance does not independently establish their correctness. This review found no concrete counterexample to Theorems 1–7 or the certificate logic. This is a reasoned review, not a proof that the implementation is defect-free; no conclusion here rests solely on test outcomes.
