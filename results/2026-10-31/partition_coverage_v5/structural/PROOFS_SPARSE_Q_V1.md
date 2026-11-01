# C005 sparse finite-q certificate, proof v1

Provider: sparse_certificate_v1.py, SHA256 035b19e917f20fb28c678843a5fa7231276652649e90d26709778877265558f4. Status: own sanity passed; independent acceptance pending. No novelty claim.

## Model and necessary opposition

Known alphabet Sigma is partitioned into exactly k nonempty disjoint blocks. Complete noise-free words are labeled positive/negative. Each local language has at most finite integer q>=1 words (including the possibility of empty languages). For a fixed partition, let O_B be all distinct positive projections to B. A compatible model exists exactly when every |O_B|<=q and each negative has at least one block projection outside O_B. Necessity follows because every O_B is contained in its factor language; if a negative's projections all occur then every accepting product accepts it. Sufficiency chooses the finite languages O_B. These witnesses are regular, but a finite q constraint is strictly stronger than unrestricted regular semantics.

If a,b belong to one block B, projection from O_B to {a,b} is a function, hence its image has at most q elements. Therefore >q observed binary projections implies a cannot-link. >q distinct unary projections (equivalently counts) proves global infeasibility. Threshold >1 is unsound when q>1. Graph edges are only necessary constraints: checking full block cardinality and ALL negatives is mandatory.

## Sparse coloring theorem

Let G be any simple undirected sound cannot-link graph, with k known. Suppose it contains a k-clique A. Label its vertices with distinct colors 0,...,k-1. Repeatedly color an uncolored vertex v when its colored neighbors contain exactly k-1 distinct colors, assigning the remaining color. Record one already colored neighbor for each excluded color. Suppose every vertex becomes colored and final coloring is proper on EVERY edge. Then G has exactly one proper k-color partition up to permuting colors.

Proof: any proper k-coloring assigns all k distinct colors on A; a unique permutation aligns it with our anchor. Induct on the recorded propagation steps. Every excluded color is forbidden by a neighbor already forced by induction, leaving exactly the recorded color. At termination every vertex is forced, and the final edge check establishes existence. The clique ensures all k colors occur. Thus all graph-compatible partitions coincide with the recorded partition.

Because every sample-compatible q-bounded partition colors G properly, direct cap and negative checks of that sole partition have two sound outcomes: passing certifies a unique compatible partition; failing proves no compatible partition in this model. Without a complete valid coloring certificate we only abstain. A graph with a coloring conflict or a clique missed by the heuristic need not receive an infeasibility conclusion. The provider may also abstain on uniquely colorable graphs with no k-clique. Known k is essential.

Implementation searches for an anchor by bounded greedy extension rooted at each vertex, in degree order. This is intentionally incomplete, rather than an exhaustive clique search. Correctness of an accepted certificate does not depend on completeness of this heuristic. For k=1 the one-vertex anchor and zero-neighbor rule color the graph only when final edge checks pass. Missing symbols usually remain unforced and cause abstention; no blanket impossibility is claimed. Empty positives cause deliberate abstention. Immediate deadline yields incomplete with unknown uniqueness.

Recorded anchor/steps use anchor-relative color numbers; output blocks are canonically sorted independently. A replay checker should reconstruct anchor-relative colors then compare their unordered block sets to output blocks.

## Construction with q+1 positives, all q>=1

Let k>=2 nonempty blocks B_i have arbitrary, possibly unequal sizes. Let s_i list each block symbol exactly once in fixed order. First take P0 = s_1^2 ... s_k^2 and P1 = s_k^2 ... s_1^2. For each r=3,...,q+1 add P_r = s_1^r ... s_k^r (none if q=1). There are exactly q+1 distinct positives. Each block has exactly q observed words s_i^2,...,s_i^(q+1). Any cross pair a in B_i,b in B_j has two distinct binary projections aabb and bbaa (in either order), plus one count-r projection for each r>=3. Those q+1 projections are distinct by order or length. Within-block pairs have at most q values. Thus the opposition graph is complete k-partite, and the partition and observed finite languages are certified.

The q+1 lower bound asserted here is ONLY for obtaining >q values on any one opposition edge. It is NOT a lower bound for all possible partition-recovery methods. This family includes repeated events, unequal blocks and singleton blocks, but excludes missing symbols because s_i covers its entire block. It proves sample-count reduction for this constructive family, not arbitrary passive recovery. This dense family supplies no evidence for sparse-graph coverage.

## Original three-positive proposal and its boundary

For equal block sizes n, let u_i=s_i^r (r>=2), v_i=u_i+first(s_i). Use forward concatenation of u_i, reverse concatenation of u_i, and round-robin lockstep of v_i. For a cross pair whose two symbols are not first symbols, each occurs r times in the lockstep trace; equal n makes their occurrences alternate by rounds (possibly with fixed offset order). The result is neither a^r b^r nor b^r a^r, since r>=2. If at least one symbol is a first symbol, its count increases and the third projection already differs by length/count. Every block projects to u_i or v_i, exactly two words. Hence the original equal-size q=2 proposal is sound.

A naive unequal-size extension is false for complete opposition coverage. Original and size-minimized evidence is preserved. The smallest tested two-block failure over total size<=6 is sizes (2,4), positives `ababcdefcdef`, `cdefcdefabab`, `acbdaebfacdefc`. Pair {b,f} has only {bbff,ffbb}; expected complete bipartite graph loses that edge. This is NOT a counterexample to the original equal-size claim, nor a proof the partition cannot be recovered (the sparse provider can still certify it). Minimum is relative to the specified two-block, repeat-2 construction and tested total sizes, not global counterexample minimization over arbitrary strings.

## Actual trace-realizable sparse example

Base positives `acbde`, `ebadc`, alphabet abcde, k=3. Their opposition graph has edges ab,ae,bc,be,cd,ce,de: a path a-b-c-d joined to e. Its unique blocks are {a,c}|{b,d}|{e}; complete tripartite on these blocks would have 8 edges, but this graph has 7 (missing ad). Anchor b,c,e forces a from neighbors b,e, then d from c,e. For each q>=1 replace every event of each base trace by r copies for r=1,...,q. This gives 2q positives. A fixed-order pair has q projections; an inverted pair has 2q>q projections. Each true block has q local words; sparse graph remains exactly the same. Empty and `aa` negatives are directly rejected. Own initial smoke used all 25 linear extensions of poset a<c,a<d,b<d expanded in this way; captured minimization found the 2-positive base above. Independent audit should check the reduced base rather than assuming the initial 25-positive run tested it.

## Complexity and dependency capture

All runtime code is in sparse_certificate_v1.py (stdlib only). Validation/projection/check helpers adapted verbatim from parent C004 structural/singleton_solver_v1.py; bounded solve body adapted from C004 structural/bounded_certificate_v1.py. Those parents are provenance, not runtime imports. Capture this source, driver, every input and frozen protocol; capture.py snapshots itself. No dependency installation.

Pair extraction materializes all binary projections using per-symbol incidence: per positive O(mL+m^2) operations, with projected-string sizes retained in witnesses (not constant-byte values). Bounded greedy anchor search and repeated propagation are polynomial; a coarse O(m^3) graph-processing bound suffices, excluding sorting and output-string costs. The algorithm is not a complete uniquely-colorable-graph recognizer. Cooperative deadline checks are periodic; outer hard limits remain required. Accepted outputs include full words and all negative witnesses, so output serialization is material work.

Own captures: smoke 20261031T063843.841364Z_5656c4d7a3; minimization 20261031T063925.345240Z_431ed2410a. The failed bare `python` environment launch started no capture or solver, produced no scientific result; corrected bundled runtime was then used. No official performance runs authorized/performed by structural worker.
