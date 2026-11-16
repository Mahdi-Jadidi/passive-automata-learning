# Independent mixed-cover hypergraph engine: design and proofs

**CHECKPOINT — PROPOSED; independent review required before implementation or benchmarking.** No solver or measured speed is claimed. Scope is finite noiseless full-word samples, unknown number and state counts of disjoint regular factors under conjunctive acceptance. IDs are explicitly declared ordered opaque nonempty strings, not characters. Normalize first-occurrence duplicate words within each label; ε is an empty ID array. Validate exactly `alphabet`, `positive`, `negative`, lists and word lists, distinct IDs and membership of all IDs before any mathematical conclusion. Contradictory labels are valid but infeasible. Unused IDs remain vertices. The model's sample uniqueness is not physical truth.

## Criterion and incidence hypergraph

For B⊆Σ let H(B)={π_B(p):p∈P} and R(B)={n∈N:π_B(n)∉H(B)}. For every nonempty B create **one** row e_B incident to every symbol in B and every negative in R(B). Symbol vertices require exactly one incident selected row; negative vertices require at least one. Multiple selected rows may cover the same negative. One selected row can cover no negatives. This is mixed exact/at-least-one cover, not ordinary exact cover of all columns.

**Lemma 1 (projection).** Π is compatible iff ⋃_{B∈Π}R(B)=N. Each factor must contain H(B), so rejection of n requires some projection outside H(B). Conversely the finite regular factors H(B) accept P and reject every n with a covering block. This also covers P=∅ and, with the empty conjunction, Σ=∅.

**Theorem 2 (bijection and objective).** Exact symbol cover gives pairwise-disjoint nonempty rows whose union is Σ, hence a partition; negative coverage gives compatibility by Lemma 1. Every compatible partition selects exactly its blocks, so the maps are inverse, including the unique empty row set when Σ=∅. Row count is the block count. The number of selected-row sets is C; the greatest row count is k*, and the number attaining it is O. If no set is feasible, C=O=0 and k* undefined. A row has no alternative rejection-witness choices: counting such choices would overcount.

## Independent search and pseudocode

Maintain selected rows Q, uncovered symbols S and uncovered negatives U. Available rows A are precisely all rows whose symbol sets are subsets of S. Choose deterministically an uncovered symbol with fewest incident rows in A, breaking ties by declared alphabet order. Branch on each row containing that symbol in a fixed subset order. Never branch on a negative coverage witness; coverage tags may overlap. Every branch removes at least the chosen symbol. Optional sound prune: if U contains a negative absent from the union of R(B) over A, no completion exists. A zero-row uncovered symbol is infeasible. No optimum-based pruning is used in the full-contract search.

```text
SEARCH(Q,S,U):
    if S is empty:
        if U is empty: EMIT(Q)
        return
    A := {B ≠ ∅ : B ⊆ S}
    if U is not subset of union(R(B) for B in A): return
    a := deterministic minimum-degree symbol of S using rows A
    for each B in A with a in B, in fixed order:
        SEARCH(Q ∪ {B}, S \ B, U \ R(B))
```

**Theorem 3 (uniqueness, completeness, termination).** Fix any target partition extending a reached node. Its unique block containing deterministically chosen a is exactly one available row, so it follows exactly one child; induction gives exactly one root-to-leaf path for that target, independent of dynamic column choice. Conversely every emitted leaf covers each symbol once and all negatives. Coverage-union pruning cannot remove a feasible completion because its future rows are a subset of A. Each step decreases |S|, branching is finite, depth ≤m, so traversal terminates with sufficient resources. Different traversal histories cannot emit the same partition; no search-order assumption about lexicographic RGS is needed.

## Exact output and witnesses

At every emitted partition compute its RGS by labeling blocks in order of first declared-symbol occurrence. Increment arbitrary-precision C; keep the two smallest RGSs seen, comparing entire strings, not traversal order. Maintain k* and O; on a strictly larger row count reset O=1 and its two-smallest list; on equality increment O and insert into that ordered list if applicable. Induction on emitted leaves proves C, k*, O and both first-two lists at exhaustion; distinct leaves ensure no ties duplicate a partition. First optimal witness is recommendation, O=1 is optimal uniqueness, C=1 is sample uniqueness. For each retained partition construct each H(B) in first-occurrence positive projection order and choose the first rejecting block in canonical label order per normalized negative; independently replay exact symbol ownership, factors and indices before returning. A replay failure is ERROR and cannot certify output. This design returns C028's schema; it deliberately strengthens its compatible witness choice to first two lexicographically, matching V32/V33. If C=0 set counts zero, witness lists empty, optimum/recommendation/optimal uniqueness null; malformed input has INVALID_INPUT and null mathematical fields; caught resource exhaustion/interruption is INCOMPLETE with null fields. Hard process termination may yield no response.

No `max_candidates` compatibility is assumed: an optional **separately named node budget** may be specified later, returning INCOMPLETE whenever exhausted; zero and termination boundaries need a separate contract review. It must not be silently called C028's candidate-prefix budget. An unlimited call searches the finite tree given adequate resources.

## Boundary cases and cost

Σ=∅ has one empty row set: it fits iff N=∅ (including P=∅); no row may reject ε in this case. For m>0 and P=∅ each nonempty row rejects every negative; for N=∅ every partition is feasible. If P∩N≠∅, reject only after validation; one block proves feasibility for nonempty Σ and disjoint labels. Equal projections compare complete sequences of atomic IDs; repeated traces are normalized but repeated IDs within words are preserved.

There are 2^m−1 rows, up to O((m+|N|)2^m) incidence entries and 2^m times polynomial encoded-input projection preprocessing, including exact ID comparison and word lengths. Tree leaves are at most Bell(m); the tree has depth at most m, at most O((m+1)Bell(m)) nodes because each node extends to at least one full partition when all rows are available. Work per node includes scanning/maintaining candidate incidences, union coverage, bigint and witness ordering; memory includes exponential row storage, search stack and counts of O(1+log Bell(m)) bits. These are upper bounds, not polynomial time in m or speed evidence. The NP-complete variable-alphabet threshold in V27 is a conditional complexity barrier, not a prohibition on finite exact solving.

**Biggest overlooked issue:** at-least-one negative coverage is not an exact-cover column. Branching directly on a negative and counting selected witnesses can enumerate the same partition repeatedly when multiple blocks reject it. Symbol-only deterministic branching avoids this; prunes or shortcuts that retain only the optimum can silently invalidate C, O or first-two witnesses.

## Related prior work and status

Knuth's [Dancing Links](https://arxiv.org/abs/cs/0011047) presents Algorithm X for exact cover; the additional at-least-one negative coverage and the bijection/uniqueness arguments above are this design's stated adaptation, not attributed to that paper and not claimed novel. V32 package B §4 and §10 supplied the mixed block-cover formulation and projection foundation. Design status PROVED subject to independent mathematical review; implementation, performance and observed correctness remain OPEN pending that review and later audit.

## توضیح کوتاه فارسی

هر بلوک ممکن یک ردیف است؛ هر نماد باید دقیقاً یک‌بار و هر نمونهٔ منفی دست‌کم یک‌بار پوشش داده شود. جست‌وجو فقط روی یک نمادِ پوشش‌نیافته شاخه می‌زند تا هر افراز دقیقاً یک‌بار دیده شود. شمارش و دو شاهد مرتب پس از پایان کل جست‌وجو دقیق‌اند؛ این طرح نمایی است و هنوز پیاده‌سازی یا آزمایش نشده است.
