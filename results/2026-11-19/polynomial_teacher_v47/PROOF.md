# V47 proof ledger

## 1. Contract

Input is a finite labeled sample D=(S⁺,S⁻) over declared ordered Σ. A compatible alphabet partition P has one regular factor K_B over each block B. The conjunction of membership in the projected factors accepts all positives and rejects all negatives. The exact objective returns one compatible P maximizing |P|, with a checked optimum certificate. There is no bound on local states in the objective. The V47 teacher is the decision service for a specified P under this contract.

## 2. The polynomial teacher is exact

**Lemma 1.** Put H_B=π_B(S⁺). The compatibility condition is

> For every y_i in S⁻ there exists B in P such that π_B(y_i) is absent from H_B.

Every compatible family must contain H_B in K_B to accept the positives. If every block's projection of y_i belongs to H_B, all blocks must accept that y_i. Conversely, choose K_B=H_B for every block. These languages meet all positives simultaneously. The stated condition ensures that each negative fails at least one of them. Each H_B is finite and regular. A complete DFA consists of its distinct prefixes including ε and a rejecting sink, with a transition to the next prefix when one exists and otherwise to the sink. The final states are the complete H_B words. If H_B is empty, a single rejecting state suffices.

**Lemma 2.** In `ProjectionTeacher.check`, after processing blocks B₁ through B_j, `uncovered` is exactly the indices i for which π_B(y_i) belongs to H_B on every processed block.

Before processing any blocks all i satisfy the empty conjunction. Processing a new block builds exactly its H_B and retains an index precisely when its projected negative is in that set. This intersects the previous set of indices with the indices accepted by the new factor. Induction proves the invariant. Once empty, the set stays empty and returning ACCEPT is sound. At exhaustion an index remains exactly when Lemma 1 fails, so REJECT is sound and complete. All projected negative lists use the same original order. Equal projections of different negative words have separate indices. The solver handles the empty alphabet explicitly because zero block images alone cannot carry a negative count.

**Theorem 1.** The V47 teacher has identical completed ACCEPT/REJECT answers to V45 on the optimizer interface.

The V45 caller's bound is the prefix-and-sink size above, or one for empty H_B. If the V47 teacher accepts, the very H_B witnesses fit V45's bounds, and the complete V45 bounded decision must accept. If V45 accepts, its witnesses are regular languages, so Lemma 1 makes V47 accept. V47 does not enumerate the full bounded relation R_B, return all possible local behaviors, or implement prescribed partial-assignment queries. Those interfaces are outside the fixed-partition decision used by the outer solver and remain available through the original manuscript implementation where supported.

**Time.** Let k=|P|, p=|S⁺|, r=|S⁻|, and L be the total length of the sample words in symbols. In a partition, the sum of all projected lengths equals L, since each original event goes to exactly one block. There are at most k(p+r) projected word rows, including ε rows. The decision processes at most kp positive insertions and kr negative membership tests. With ordinary hash-table behavior and bounded-size interned IDs this costs O(k(p+r)+L) time on materialized images. A direct construction of the images is polynomial in the original input, for example by scanning the sample once per block with direct block membership. Worst-case hash collisions in the given implementation can make each set operation compare at most p stored tuples and cost up to O(p) times a bound on tuple comparison and hashing, which is polynomial in the encoded sample length. The space used by the decision beyond the existing images is O(p+r) references and indices. The optimizer keeps its V45 projection cache separately. A cache miss may scan previously stored keys, whose total number can grow with the number of queried masks.

There is an asymptotic separation on the unary family with S⁺={a repeated ℓ times} and S⁻={ε}, ℓ≥1. The V45 table must visit at least 2^(ℓ+2) × (ℓ+2)^(ℓ+2) named DFAs at the top sufficient bound for its single block. V47 uses only membership in the finite projected positive set. This establishes removal of the enumeration cost, independent of timings.

## 3. Composition with the exact outer algorithm

V47 shares the frozen V45 sample normalization, mandatory groups, projection store, pair/count/cut CNF and verifier. The separately versioned outer entry point retains the V45 control flow, SAT threshold search and result format. Only the fixed-partition decision class and profiling instrumentation differ. The caller cross-checks the decision against the cached rejection-mask union and derives a cut only after completed rejection.

The [V46 outer proof](../teacher_v46_outer_audit/OUTER_PROOF.md) applies with Theorem 1. In brief, upward monotonicity of rejection ensures safe mandatory contraction. A witnessed false-region cut removes its rejected candidate and keeps every compatible partition. Each round maximizes the exact master relaxation, so its first accepted maximum is globally optimal. The finite candidate domain strictly shrinks after a rejection and never loses a compatible partition. Timeouts still return null mathematical fields and never convert an unfinished teacher query into a rejection. Verification stays independent of the replacement teacher and checks an attained structural bound or a regenerated threshold refutation.

## 4. General end-to-end polynomial time would imply P=NP

Consider the decision problem asking whether some compatible P has at least K blocks. It lies in NP. A candidate partition has polynomial representation and both the block-count test and Lemma 1 can be checked in polynomial time. This NP membership uses the partition as its witness. It does not presume a polynomial-size optimum certificate.

Reduce **Vertex Cover** on a simple undirected graph G=(V,E) with at least one edge. Instances with no edges can be answered immediately, so this restriction does not weaken the hardness argument. Use Σ=V, S⁻={ε}, and one length-two positive word uv for every edge {u,v}, in declared vertex order. This produces a valid sample with disjoint labels, including any isolated vertices.

For any block B, π_B(ε)=ε. An edge word projects to ε exactly when neither endpoint lies in B. Therefore a block rejects ε exactly when it meets every edge, i.e. B is a vertex cover. By Lemma 1 the partition is compatible exactly when at least one of its blocks is a vertex cover.

Let τ be the minimum cover size and n=|V|. Every compatible partition contains a block of size at least τ, so it has at most 1+n−τ blocks. Conversely a minimum vertex cover as one block and every other vertex as a singleton attains 1+n−τ. Thus

> max |P| = n−τ+1.

For a Vertex Cover threshold t with 1≤t≤n, use K=n−t+1. A cover of size at most t exists exactly when the partition maximum is at least K. The reduction has polynomial size and uses only one negative of length zero and positives of length two. Vertex Cover is the NP-complete Node Cover problem of [Karp (1972)](https://doi.org/10.1007/978-1-4684-2001-2_9). The decision version is consequently NP-complete, and computing an exact optimizer would solve it. Therefore a worst-case polynomial end-to-end algorithm for arbitrary Σ under the current contract would imply P=NP. This does not rule out polynomial special cases.

**A proved tractable regime.** For a fixed bound on |Σ|, the actual outer instance has a bounded number of atoms, possible cuts, candidate partitions, SAT variables and clause sequences. Each rejected candidate is eliminated, so the number of rounds is bounded solely by that alphabet bound. Proof generation over the bounded CNF is also bounded independently of trace lengths for the fixed exact SAT backend. Each projection, witness calculation and witness replay is polynomial in the sample encoding, and there are boundedly many masks. Thus with fixed alphabet bound the combined exact method is polynomial in the sample encoding length. The constant can be large. When |Σ| grows, the number of atom partitions can grow as a Bell number and the fixed-bound argument no longer applies.
