# C006-T002: two additional q-free contextual must-link rules

This extends, not overwrites, tested PROOFS_v1.md. Every reference there to the
incomplete graph concerns its explicitly stated adjacent-swap/insertion-rescue
rules. Adding the rules here changes which examples remain graph gaps.

## E1. Alternative insertions (A)

P contains xay and xby, N contains xy, a!=b. Suppose a,b have different owners.
The owner of a sees the negative xy's projection in positive xby, because b is
erased on that block. The owner of b sees it in xay. Every other block sees it
in either positive. Thus ALL negative projections are positively forced, which
contradicts the exact finite-sample criterion T1. Therefore a,b share an owner
in EVERY compatible partition, for arbitrary k and arbitrary regular factors.
Contexts may contain further occurrences of a,b: deleting the indicated newly
inserted occurrence is the exact relation needed; no uniqueness of symbols or
finite q assumption appears. The implementation may use the stated same-offset
rule; no need to enable a stronger different-offset insertion generalization.

## E2. Alternative deletions (B)

For one negative n, let positive p_a be obtained by deleting ONE occurrence of a,
and positive p_b by deleting ONE occurrence of b, a!=b. Positions/contexts may
differ. If owners differ, a's owner sees n's projection in p_b (deleting b has
no effect there), and b's owner sees it in p_a. Every other block sees it in
both. T1 again contradicts rejection of n. Hence a,b share an owner. Positions
must be verified against n exactly; merely a count difference or subsequence
relationship without the single-deletion check is not a certificate.

Both proofs apply to k=1 too (the constraint is vacuously respected), and all
k>=2. A replayable edge includes its rule, negative, positive pair, deleted/
inserted occurrence offsets and distinct symbols. Validate their actual labels
and exact word relations before unioning. Connectedness of ANY union of these
proved edge types remains a sufficient nontrivial obstruction. No graph-only
decomposability conclusion follows when the union is disconnected.

## E3. Preserve old/new graph meanings

For A={a,b}, P={a,b}, N={epsilon}, A immediately derives edge ab. This was an
empty-OLD-graph example, NOT an empty-enhanced-graph example.
For A={a,b,c}, P={ab,ac,bc}, N={abc}, B derives all three edges. Its old graph
gap also disappears under enhancement. These observations do not invalidate
the old counterexamples or justify silently changing their recorded graph.

Manager original A=abcd, P={acdb,cabd,bcda,dabc}, N={abcd} remains an empty graph
for the union of OLD+A+B rules: all words have length four, so A would require
length-five positives and B length-three positives, neither present. No positive
is one adjacent swap from n; old rescue would need a length-five positive as well.
The previously captured seven-split collision cover still proves no nontrivial
partition. Thus even this enhanced graph obstruction is incomplete.

The three examples are versioned rather than reclassified in place. Reduced
two-symbol example is still minimal in its original stated OLD-rule setting;
no smaller counterexample to the ENHANCED graph or automatic enhanced minimizer
is claimed. Manager's equal-length example is the preserved enhanced-gap witness.

Scientific status: proof supplied, targeted captured check to follow; independent
audit and implementation-owner versioning are separate. No novelty claim.
