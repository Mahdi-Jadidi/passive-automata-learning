# C024 obstruction and Candidate B review v1

Status: proofs and bounded recommendation; no performance experiments. Local provenance: C006 T8 and C020 Candidate B.

## Deleted-symbol obstruction
For m≥1 choose distinct symbols a1,...,am, n=a1...am, P={n with ai deleted:1≤i≤m}, N={n}, A={ai}. There are m distinct positives, each length m−1, and one negative length m, so total recorded characters are m(m−1)+m=m². Labels are disjoint.

For any proper nonempty block S choose aj outside S. The positive obtained by deleting aj projects onto S exactly as n does. Therefore n∉R(S); no proper block rejects the sole negative. Every block of a partition with at least two blocks is proper, so every such partition fails. The full block rejects n (identity projection and disjoint labels). Exactly oneblock is feasible. Any externally supplied valid K≥2 is incompatible; K>m is invalid input under the API, not an incompatibility result.

The swap graph is empty: all positives have length m−1 while the negative has length m, and swaps preserve length. Thus r=m. For m≥2, each symbol has negative count 1 and some positive count 1 (delete another symbol), as well as positive count 0 (delete itself). No unary block rejects n, so the unary-all-partitions shortcut fails. For m=1 it succeeds because P={epsilon} and N={a1}; this boundary is intentional. No empirical runtime or lower bound follows merely from this obstruction; it forces exhaustive rejection in A absent stronger shortcuts, but many algorithms may exploit its structure.

## Envelope proof
At an RGS node let current blocks be B1,...,Bj and U be the union of unassigned atoms. Every completed current block C_i⊆B_i∪U. Every newly created block C⊆U. Monotonicity R(S)⊆R(T) for S⊆T gives
E = union_i R(B_i∪U) union R(U),
omitting the last term when U is empty. All negatives rejectable by any completion belong to E. If E misses one negative, every completion fails: pruning is sound. Reusing U in several terms deliberately relaxes mutually exclusive assignments; coverage is necessary, never sufficient. Count feasibility pruning remains separate. When no new block can be created, retaining R(U) merely weakens pruning and remains safe.

Current-coverage pruning is unsound. A={a,b,c}, P={aaccbb}, N={ccaabb}, K=2. At RGS prefix a|b with c unassigned, both current projections match: aa and bb. Yet assigning c to a yields ac|b; the ac projections aacc and ccaa differ, so the negative is rejected. No adjacent-swap edge arises (four differing positions); the prefix is reachable. This counterexample needs no merging of previously separate blocks.

## Additional cost and recommendation
For a checked node with j current blocks, the simple envelope adds at most j+1 reject-mask requests (j when U empty), plus mask construction and unions. Across V checked nodes, requests are at most Σ_v(j_v+1)≤V(K+1) on count-feasible known-K nodes. Requests are not cache misses: each miss scans the full immutable sample for projections, requiring O(T) character work plus string/set operations and mask operations; include O(m) deletion-table/block setup and O(|P|+|N|) empty-word/record overhead. Negative bitsets require ceil(|N|/wordbits) machine words; Python integer costs are not constant. With arbitrary atom-sized masks include their bit-operation costs too. A 4096-entry cache can evict existing leaf masks, so recomputation may increase beyond the added calls. Peak live projection language storage, expanded cache values, and counters also matter. Avoid preallocating all 2^r masks.

Decision: a separate, tightly limited B merits implementation ONLY if current-baseline profiling shows material known-K DFS cost. Use the stated envelope at fixed invocation points, existing bounded exact cache and independent count bounds; no adaptive policies or new constraints in this version. Require the counterexample above, independent full-family correctness, cache miss/projection counters, and end-to-end same-input timing. If cost is in validation/graph/shortcuts, defer B. Mathematical soundness supplies no speed guarantee and does not authorize promotion. This conditional recommendation does not assert that the profiling precondition has been met.
