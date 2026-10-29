# Context family: distinguish a star tree from a mandatory prefix

Master's static review of audit/generate_stage2_corpus_v1.py found a model-interpretation pitfall before independent acceptance. The generator makes C by cycling the alphabet and uses center–leaf star edges inside each block. Its projected C need not be a concatenation of these star-edge tiles. For example, with block abcd and tiles {ab,ac,ad}, C=abcd has chunks ab,cd, and cd is not an allowed tile. The bare language (ab|ac|ad)* is therefore the wrong declared target for this C.

No observation input needs to be altered to obtain a valid, more general target. Define, for every planted block B_i,

    u_i = projection_B_i(C)
    E_i = {center_i leaf : leaf is a different symbol of B_i}
    L_i = {u_i} · E_i*

This is a regular infinite language with a fixed mandatory prefix. The chosen cells give every u_i nonempty. Base C projects to u_i in every factor and is accepted. Rescue C+ab for an edge in B_i projects to u_i ab in that factor and unchanged u_j elsewhere, hence is accepted. Negative C+a has suffix a after u_i in its own factor; its suffix length is one, whereas every string in E_i* has even length. It is rejected. Independent membership checking must test the fixed prefix, even suffix length, and every two-character suffix tile, rather than just arbitrary parity of the whole word.

If edge endpoints a,b had different owners in ANY sample-compatible regular product, C+a would project like C+ab on a's owner and like C on every other owner. It would be accepted, a contradiction. Every declared tree edge is therefore a sound must-link independent of the particular target grammar. The trees connect the blocks; exactly k components plus direct feasibility certify the known-k partition uniquely. All observed traces are long and nonempty; the proof does not require an epsilon positive or acceptance of epsilon by the target.

Auditor was informed before accepting the family and will preserve a separate frozen target-interpretation/proof record plus independent grammar-membership checks. The original generator, inputs and sidecars remain unchanged. This corrects a target-description attempt, not the general insertion-rescue theorem or the provider's projection-feasibility criterion. No new runtime or benchmark was executed by the master for this review.

## Distinct labeled-word count

For n symbols in k blocks of size at least two, the center–leaf stars have n-k edges. The base and each edge rescue give n-k+1 distinct positives. All leaves in a block share the same negative C+center; after deduplication there are exactly k distinct negatives, even though the generator's raw list repeats them once per leaf. The three word lengths |C|, |C|+1 and |C|+2 separate the labels. Total distinct labeled observations are n+1, with no short whole-word requirement. Thus the proposed four cells use 33 distinct observations for n=32 and 129 for n=128. The auditor must check these actual normalized counts independently before adopting the numeric claim.
