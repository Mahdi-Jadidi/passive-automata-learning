# C018 clarification: growing RGS blocks versus merging finished blocks

The original P={ab}, N={ba} example in FASTSCAN_EQUIVALENCE_v1.md and
ADVERSARIAL_SPEC_v1.md correctly shows that enlarging/merging a symbol block
can restore negative rejection. It should not be read as a literal reachable
C015 RGS node with both singleton blocks finished: RGS does not merge existing
blocks, and the swap stage would already contract a,b on that sample.

Use this precise source-relevant counterexample to unsafe partial-RGS pruning:

    alphabet=a,b,c; P={aaccbb}; N={ccaabb}; known_k=2.

Unary counts agree and there is no opposite-label single adjacent swap, so
the graph is empty. Singleton atom partition fails direct feasibility. At
RGS pos2 with current blocks {a}|{b} and remaining {c}, neither current block
rejects the negative. Nevertheless adding c to the first block yields
{a,c}|{b}, whose ac projections aacc and ccaa differ and which is compatible.
Rejecting that partial node for lack of current coverage would lose a valid
solution. This example does not ask RGS to merge already selected blocks.

This is a mathematical clarification, not an executed test or new algorithm.
The proof of the optional upper-envelope prune remains unchanged. Earlier
files/readiness are preserved; use this clarification for adversarial cases.
