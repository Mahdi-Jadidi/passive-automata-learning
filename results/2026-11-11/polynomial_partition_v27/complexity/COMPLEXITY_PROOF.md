# Complexity audit: maximum sample-compatible blocks

The biggest overlooked issue is that the requested exact polynomial-time optimum would solve an NP-complete problem, already on one negative trace and words with no repeated symbol. This is a conditional barrier (unless P = NP), not an unconditional proof that a polynomial algorithm cannot exist.

## Model and decision problem

The alphabet is an explicitly listed finite set of m distinct atomic symbol identifiers; identifiers may use O(log m) bits each, so m can grow. The total encoded input size includes that alphabet, every listed word and all labels. Empty words are allowed. Words are complete traces. A partition consists of nonempty disjoint blocks covering the alphabet. The local factors are arbitrary regular languages and the global acceptance condition is AND of the projected local acceptances; there is no factor count, ownership, state bound, or physical truth in the input.

For nonempty alphabet and disjoint P,N, define OPT as the maximum number of blocks among compatible partitions. The threshold problem takes (alphabet, P, N, t) and asks whether OPT >= t. If contradictory labels are admitted, the answer is NO for every threshold requiring a partition; alternatively reject them as invalid under a documented input contract. Our hard instances are consistent.

For a block B, let H_B={projection_B(p): p in P}. A partition is compatible iff, for every n in N, some block B has projection_B(n) outside H_B. Necessity follows because the factor over B must accept every positive projection. For sufficiency use exactly H_B as the local language: a finite language is regular, all positives pass, and each negative fails at least one factor. In particular, factor automata do not need to be guessed in a certificate. One block is always compatible on consistent data.

## Theorem: NP-complete threshold, NP-hard optimum

The threshold problem is NP-complete, even on consistent samples with exactly one negative word, and where each symbol occurs at most once in each word. Computing OPT or returning an optimal partition is NP-hard under polynomial-time reductions. Therefore a deterministic algorithm that always returns the exact optimum in polynomial combined input size would imply P=NP. Conversely, if P=NP, polynomially many threshold queries and standard self-reduction can produce the optimum and a witnessing partition, so the existence of a general polynomial exact algorithm is equivalent to P=NP. No separation is asserted.

### Proof of membership

A certificate assigns one integer block number to each alphabet symbol, using at most m numbers. Verify nonempty blocks and compute projections for each (block, trace); compare each negative projection with each positive projection. This is polynomial in the explicit input length and determines compatibility by the criterion above. Check that the number of blocks is at least t. This also applies to epsilon, empty P, empty N and arbitrary trace lengths.

### Reduction and proof

Take a simple undirected graph G=(V,E) with at least one edge. In any fixed ordering v1,...,vm of V, construct alphabet Sigma=V, one negative word n=v1...vm, and, for each edge e={u,v}, one positive word p_e obtained from n by deleting u and v. Set target t=k+1 for the independent-set threshold k. The sample is consistent: every p_e has length m-2 while n has length m. The alphabet and word lists have O(m(|E|+1)) symbol occurrences; construction and binary identifier encoding take polynomial time. E is nonempty, so m>=2. For m=2, a positive word can be epsilon; it is a valid full trace.

For any B subset V, projection_B(n)=projection_B(p_e) exactly when B is disjoint from e. The forward implication holds because every vertex of B appears once in n and a vertex deleted from p_e cannot occur in its projection; the reverse holds because deletion outside B does not change its projection. Consequently B rejects n, meaning projection_B(n) is absent from H_B, exactly when B meets every edge: B is a vertex cover. Thus a partition is compatible exactly when at least one of its blocks is a vertex cover.

Let alpha(G) be the largest independent-set size. Since E is nonempty, V minus any independent set is a nonempty vertex cover. Given a maximum independent set I, take V minus I as one block and every member of I as a singleton. This compatible partition has alpha(G)+1 blocks. Conversely, any compatible partition has a vertex-cover block C. Its complement V minus C is independent, and every other block is a nonempty subset of that complement; therefore there are at most |V minus C| other blocks, so the total is at most alpha(G)+1. Hence OPT=alpha(G)+1. In particular, OPT>=k+1 iff alpha(G)>=k, with a polynomial reduction.

The independent-set decision problem is NP-complete. Karp's original paper establishes NP-completeness of CLIQUE; a graph has a clique of size k iff its complement has an independent set of size k. The nonempty-edge restriction preserves hardness: for any graph H, add a disjoint edge and increase k by one; alpha increases by exactly one. Reference: Richard M. Karp, *Reducibility Among Combinatorial Problems* (1972), https://www2.seas.gwu.edu/~simhaweb/champalg/tsp/papers/KarpOriginal.pdf .

An exact optimization value decides the NP-complete threshold. For a returned optimal partition, counting its blocks provides the value. For the P=NP converse: threshold feasibility with some specified symbol pairs required together/apart is also in NP. Under P=NP, first find OPT with O(log m) threshold queries, then assign each symbol to existing or new block, testing whether each tentative pair-relation prefix can still be extended to a compatible partition of OPT blocks. Polynomially many decisions recover a witness. These extra constraints are internal self-reduction queries, not part of the original task input.

## Boundaries and independently checkable examples

- This hardness says nothing by itself about the special question OPT>=2. Indeed every graph in the reduction has such a partition: for any vertex v, V minus {v} is a nonempty cover and {v} is its complement. The complexity of the general nontrivial-split question remains open in this audit; do not infer NP-hardness or a polynomial algorithm from this reduction.
- If m is a fixed constant, enumerate all Bell(m) partitions and verify each using projections in polynomial time in the rest of the input. Bell(m) is not polynomial as variable m grows. The previous max-plus dynamic program is exact, but its exponential dependence on m and/or the negative count gives no combined polynomial guarantee.
- If P or N is empty and the alphabet is nonempty, all partitions are compatible: with P empty choose empty local languages, and with N empty no rejection is required. OPT=m. If m=1 and labels are consistent, OPT=1. The theorem's nonempty-edge reduction avoids the edgeless graph, where the empty minimum cover would not be an allowable block and alpha+1 would exceed m.
- The reduction concerns best sample-compatible factor count, not recovery of the physical partition or number of real devices. Unrestricted consistent finite data also admit the one-block model; an optimal nontrivial partition generally has compatible coarsenings.
- The theorem uses variable-size abstract symbols. An implementation limited to fixed-width Unicode characters has a finite maximum alphabet and is not a faithful unbounded-m asymptotic model, although large finite instances may remain computationally challenging. The proof does not rely on physical devices, prefix-closed languages, distributional assumptions or word-length/state bounds.

For an edge ab, n=ab and P={epsilon}; OPT=2. For path a-b-c, n=abc and P={c,a}; the cover {b} plus {a},{c} gives OPT=3. For triangle ab,ac,bc, n=abc and P={c,b,a}; minimum covers have size 2 and OPT=2. The companion script enumerates all 71 nonempty labelled simple graphs of sizes 2 through 4, all their set partitions, checks block rejection against vertex-cover status, and checks OPT=alpha+1. It is a finite sanity check, not a substitute for the proof. Run with a Python 3 interpreter: `python check_reduction.py`.
