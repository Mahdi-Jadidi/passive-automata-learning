# C026 proofs v1

Date: 2026-11-06. Direct mathematical derivations; independent manager audit pending. No experimental or external-novelty claim. Contract: ../CONTRACT_V1.md. Alphabet Sigma is finite, nonempty, of size m. A block is nonempty. Pi is an unordered partition. Projection pi_B erases symbols outside B. The AND product of factors F_B is {w: pi_B(w) belongs to F_B for every B in Pi}. All factors are regular; no state bound is imposed. S=(P,N) is finite with disjoint labels. Named devices and K are not input.

## 1. Finite compatibility and prime completion

For B define H_B={pi_B(p):p in P} and r(B)={n in N:pi_B(n) not in H_B}. A partition is compatible iff the union of r(B) over its blocks is N. Necessity: every consistent factor must accept H_B. Sufficiency: factors H_B accept P and reject each negative through a rejecting block. This reuses C008 T10 and C009 T1, without changing semantics. Empty P is allowed.

A nonempty language over B is alphabet-prime when it has no AND-product representation over any proper partition of B. Unary languages are prime by convention.

**Theorem 1 (prime completion for every finite compatible partition).** Every compatible Pi has a consistent realization whose factors are nonempty, infinite, regular, cofinite and alphabet-prime.

Proof. Assign each n in N to one block B with n in r(B). Let D_B contain the projections of negatives assigned to B. None belongs to H_B. Since B is nonempty, B* is infinite; choose t_B outside the finite H_B and add it to D_B. Set F_B=B* minus D_B. Its finite excluded set is nonempty and disjoint from H_B. Thus F_B is nonempty, infinite and regular, all positives are accepted and every negative is rejected by its assigned block.

For every proper nonempty C subset B, pi_C(F_B)=C*: given v in C*, choose a in B minus C. The infinitely many distinct words v a^j have the same C-projection v, and at least one avoids finite D_B. Suppose F_B decomposed over a proper partition Q of B. Every factor of this nonempty product equals the corresponding projection of F_B: any accepted local word extends by interleaving arbitrary accepted words from the other nonempty factors. These projections are all universal, so the product would be B*. This contradicts D_B nonempty. Therefore F_B is prime. Unary B needs no further argument. QED.

**Corollary 1.** The finite partition version space is exactly unchanged by requiring nonempty infinite prime regular factors. In particular every finite consistent S has a prime oneblock completion. A nontrivial true ownership partition cannot be certified from finite labels under that unbounded prime class with unknown K. This does not prohibit the oneblock partition from being certified when all splits are incompatible. It does not apply to bounded-state, prefix-closed-only, or other restricted factor classes without a new proof.

## 2. Coarsening and the complete nonempty-language factorization

For B subset C, r(B) subset r(C): if a negative C-projection equals some positive C-projection, projecting further gives equality on B. Hence compatibility survives merging blocks. Oneblock is compatible for disjoint P,N. Thus unrestricted finite partition uniqueness is equivalent to every nontrivial partition being incompatible; the sole answer is then oneblock.

For a complete nonempty regular language L, call Pi valid if L is the AND product of pi_B(L) over B in Pi. Every nonempty product's factors equal these projections, so this captures every decomposition. Write Pi <= Q when Pi refines Q.

**Lemma 2 (projection of independent products).** If L is a nonempty product over Q with factors G_C, then for B subset Sigma,

    pi_B(L) = product over nonempty B intersection C of pi_(B intersection C)(G_C).

Proof. Inclusion from left to right follows by projection. For the reverse, start with any word w in the right side. For each C meeting B choose u_C in G_C whose intersection projection is that of w; for disjoint C choose any accepted u_C. These choices exist by membership and nonemptiness. Read w in order and, before its next letter owned by C, emit the unconsumed prefix of u_C preceding that letter. Those extra letters are outside B. Emit the letter and continue; finally emit the remaining suffixes. The resulting shuffle has each C-projection u_C and B-projection w. QED.

**Lemma 3 (meet closure).** If Pi and Q are valid decompositions of nonempty L, their common refinement {B intersection C: nonempty} is valid.

Proof. Apply Lemma 2 to each factor pi_B(L) using decomposition Q. Each resulting factor is pi_(B intersection C)(L). Substitute into the product over Pi. Regularity survives projection. QED.

**Theorem 2 (unique finest complete-language decomposition).** There is a unique finest valid partition Pi_star, and all valid partitions are exactly its coarsenings. Its factors are prime. If physical factors are nonempty and prime under these exact semantics, their partition equals Pi_star.

Proof. There are finitely many partitions, and oneblock is valid. Their iterated meet is valid by Lemma 3 and refines every valid partition; call it Pi_star. Merging preserves a product, giving exactly all its coarsenings. A decomposable Pi_star factor would give a finer decomposition, impossible. Conversely Pi_star refines the physical partition; if it split a physical block, projecting the finer decomposition by Lemma 2 would decompose that factor, contradicting primeness. QED.

These lemmas explicitly reproduce C008 OPTIONAL_COMPLETE_LANGUAGE_PROOF_v1 L1/T6/T7. They are a dependency, not a new C026 result. Nonempty L is essential: arbitrary empty factors destroy the argument. Prime factorization identifies abstract behavioral ownership under its assumptions, never device names.

## 3. A bounded partition-characteristic sample

A cut is an unordered bipartition B|C of Sigma. There are t=2^(m-1)-1 cuts. A cut is invalid for L iff there exists n outside L with pi_B(n) in pi_B(L) and pi_C(n) in pi_C(L). Indeed L is always contained in its cut-product, and invalidity means strict containment. Select accepted lifts p_B,p_C in L matching these respective projections. The sample positives {p_B,p_C} and negative {n} make this cut incompatible under the finite criterion.

**Lemma 4 (short cut-certificate triple).** Suppose a complete DFA A with Q states recognizes L. Every invalid cut has a certificate (n,p_B,p_C) with each word's length strictly less than Q^3.

Proof. Construct a directed epsilon-NFA on Q^3 triples (q_n,q_B,q_C), initialized at (q0,q0,q0). Its accepting triples have q_n rejecting and q_B,q_C accepting. A visible a in B advances q_n and q_B on a; a visible a in C advances q_n and q_C on a. Additionally, an epsilon transition can advance q_B alone on any c in C, and another can advance q_C alone on any b in B. Record visible letters in n and in the positive word whose coordinate advanced; record epsilon-transition letters only in the corresponding positive lift.

Each accepting run yields exactly the required triple. Conversely a triple determines a run by reading n in order and emitting, before each retained positive letter, the positive lift's erased letters; remaining erased suffixes are emitted last. The negative DFA run and the two positive DFA runs reach the prescribed accepting/rejecting states. Thus invalidity is equivalent to an accepting path.

Choose a shortest accepting path measured in ALL transitions, including epsilon transitions. Repeated states would permit deletion of a cycle, so it has at most Q^3-1 transitions. Each transition contributes at most one symbol to any one recorded word. Therefore each of n,p_B,p_C has length at most Q^3-1. This proof uses the complete DFA so complement acceptance needs no extra sink state. QED.

**Theorem 3 (finite partition-characteristic sample).** Every fixed nonempty regular L has a finite correctly labelled sample S_star of at most 3t distinct words, each of length less than Q^3, such that its compatible partitions are exactly the valid decompositions of L, namely all coarsenings of Pi_star.

Proof. For every invalid cut include a Lemma 4 triple. Deduplication only reduces size and labels cannot conflict because each word is labelled by L. Every valid decomposition stays compatible with any correct finite sample, using its true regular factors as witnesses. Conversely suppose sample-compatible Pi were not valid for L. At least one bipartition coarsening of Pi must be invalid for L: otherwise all such cuts are valid, and their meet, which is Pi, is valid by Lemma 3. (For two blocks it is the cut itself; oneblock is always valid.) That invalid cut is ruled out by its triple, whereas sample compatibility survives coarsening, a contradiction. QED.

For m=1 there are no cuts; the empty sample has the one available partition and the statement is vacuous. If there are no invalid cuts, the empty S_star is likewise allowed. Q need not be minimal. It is only an existential proof parameter for the actual target, never an input, resource quota, or inferred certificate of coverage. The sample-size bound is exponential in m and the proof supplies no uniform Q-free word-length bound.

**Corollary 2 (eventual recommendation convergence).** In an exhaustive passive informant for a fixed nonempty regular L, every word eventually occurs with its correct membership label. Therefore at some finite time all words of S_star have appeared. At every subsequent time the compatible partitions are exactly the coarsenings of Pi_star, and the unique maximum-block recommendation is Pi_star.

This is a statement about the exact mathematical recommendation at each finite prefix, or an implementation allowed to finish its exact optimization. A fixed computational deadline need not return a certified optimum at each time. The learner is not given the arrival time of S_star. For nontrivial Pi_star, Corollary 1 supplies prime oneblock alternative completions at every finite time, so convergence is not a finite physical-identification certificate. If physical factors may be decomposable, even the limiting behavioral partition need not be their partition.

## 4. Max-plus optimization, ties and interruptions

Sound forced atoms may contract Sigma: each atom must lie inside every compatible block, with replayable proof. Let r be the number of atoms. Atom unions represent candidate blocks; define r(B) against ALL positive projections. A DP state (R,U) has remaining atoms R and uncovered negative mask U. Define

    F(empty,empty)=0; F(empty,U!=empty)=-infinity;
    F(R,U)=max_B [1+F(R minus B,U minus r(B))],

where B ranges over submasks containing the least remaining atom. This is the max-plus adaptation of C009's canonical count recurrence, not a novelty claim. No candidate block must reject a negative by itself; coverage is a union condition.

**Proposition 4.** The recurrence returns exactly the maximum completion block count. Canonical anchoring enumerates each unordered completion once. Each feasible completion's anchored first block gives one child with its remaining coverage requirement, and conversely each feasible child gives a feasible completion. Induction on |R| proves the value. Saturated counts add only across equal-valued children; a better child resets the count and witness choices. This gives zero/one/multiple optimal partitions, not a count of machines or of all compatible partitions.

If U is empty, all remaining atoms as singleton blocks give the unique optimum |R|. If U is not a subset of r(union R), no completion exists, by rejection monotonicity. The forced-atom partition, when feasible, uniquely attains the universal upper bound r. An inconsistent partial growing block is not a safe rejection rule; only final coverage/completion conditions apply here.

Canonical recommendation is the lexicographically least restricted-growth string in sorted original-symbol order among optimal partitions. Compare full canonical partitions: bitmask traversal order alone does not prove this tie break. Two distinct optimal reconstructions must be verified as distinct partitions.

Memoized worst-case state count is O(2^r 2^n), n=|N|; summed transition count is O(3^r 2^n), before projection work, multiword mask operations, witness output and storage constants. Lazy search, forced atoms and reachable-mask sparsity can help but prove no polynomial guarantee. A memo quota is a computation limit, not a target state bound.

Any completed, replayed feasible incumbent of k blocks proves k<=k_max. Initially k_max<=r. A live branch with j finalized blocks and R remaining has upper bound j+|R|. The maximum bound across all unresolved branches and the incumbent gives a sound global upper bound. Without a fully accounted frontier retain r. An interrupted partial memo value is never an exact F value. Keep only validated completed witnesses as incumbents. A feasible candidate can establish optimality if its count equals a sound global upper bound; tie uniqueness needs a separate exhaustive argument. Two equal incumbents do not justify stopping while a larger value remains possible. Branches bounded at the incumbent value cannot be pruned when proving unique optimality or the canonical least optimum unless their tie contribution and ordering are already resolved.

Status is about ALL-K compatibility. A replayed nontrivial partition and oneblock prove ambiguity even if max-block optimization is interrupted. If completed optimum is one, oneblock is the unique compatible partition. A unique optimal nontrivial recommendation still has coarser compatible alternatives. Failed validation, contradictory labels and interrupted validation must follow the frozen contract; zero/one discovered answers under interruption do not prove uniqueness or incompatibility.

## 5. Incremental behavior

For extending correctly labelled samples, compatible families shrink and their maximum block counts are nonincreasing. A recommended partition need not move by merging: multiple old maxima can resolve in favor of an incomparable one. See COUNTEREXAMPLES_V1.md. New positives can remove rejection witnesses, so rejection masks and caches are valid only for their exact solve input; monotonicity in block inclusion is not permission to reuse stale masks across sample extension.
