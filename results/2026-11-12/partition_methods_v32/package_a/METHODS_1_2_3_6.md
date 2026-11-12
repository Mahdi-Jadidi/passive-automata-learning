# Dossiers 1, 2, 3, 6: exact partition methods

Status: mathematical formulations and review targets, not new implementations or experiments. The goal is exact sample-compatible partitioning, not physical-device identification. Biggest overlooked issue? A method returning a maximum block count does not automatically provide the all-compatible count C, optimal count O, lexicographically first witnesses, or interruption guarantees.

## Shared definitions and proof obligations

Let Σ be an explicitly declared ordered finite set of m atomic IDs and P,N finite full-word sample sets, with ε allowed. For B⊆Σ, π_B erases other symbols. A partition has nonempty disjoint blocks covering Σ; for Σ=∅ use the unique empty partition and empty conjunction true. Local factors are arbitrary regular languages, with no state bound or known K. Let H(B)={π_B(p):p∈P} and R(B)={n∈N:π_B(n)∉H(B)}.

**Criterion.** Π is compatible iff every n∈N belongs to R(B) for some B∈Π. Necessity: factors must accept H(B), so every rejected n needs one factor excluding its projection from all H(B). Sufficiency: each finite regular factor H(B) accepts the positive projections and each n is rejected by its witnessing block. Thus the condition is ∀n∃B∀p, not ∀n∀p∃B. If B⊆D, R(B)⊆R(D), because equality on D would imply equality on B; merging preserves compatibility. Duplicate words within a label do not change the mathematical sets; P∩N≠∅ is inconsistent. If Σ=∅, the empty partition fits exactly when N=∅. For nonempty Σ and P∩N=∅, oneblock fits. Model behavior on malformed IDs and caught resource interruptions must be specified independently; a partial run must not certify exact results.

Let C be the number of compatible partitions; k* the maximum block count when C>0; O the number achieving it. When C=0, O=0 and k* is undefined. Declared IDs unused in all words remain partition elements: although they do not change projections, they change partition counts and canonical order. The full C028 contract also returns the lexicographically first optimal RGS in DECLARED alphabet order, up to the first two all-compatible and first two optimal RGSs, first-occurrence normalized finite-factor witnesses and first rejecting block per normalized negative. A method limited to k* is marked as such. C,O and intermediate counts require arbitrary precision: they are at most Bell(m), hence use O(1+log Bell(m)) bits. Let L denote full encoded input length, including all IDs and trace occurrences; individual identifier comparisons and representation are not unit cost by assumption.

## 1. Exhaustive canonical enumeration

**Status: PROVED** for the finite full-contract procedure below, subject to completed execution.

**Formulation.** Enumerate every restricted-growth string s of length m with s[0]=0 and s[i]≤1+max(s[0..i−1]); for m=0 enumerate exactly the empty string. Decode equal labels to blocks, test the criterion, increment C, and maintain k*, O and the first two compatible/optimal RGSs; reset O and its list on a strictly higher block count, increment on equality. Construct and replay the actual H(B) factors and first normalized rejection indices after enumeration.

**Proof.** First-occurrence block labels and nonempty label preimages are inverse maps, so every partition is represented once. Each negative is checked against ALL positive projections on one block; the criterion makes each acceptance decision exact. Induction over the lexicographic generation prefix establishes the counters and retained-first-two invariants, hence at exhaustion all full-contract values are exact. Deduplication of graph paths is unnecessary because each RGS is unique. The empty RGS passes iff N is empty. An explicit contradiction check may return infeasible early after complete validation.

**Cost and failure.** A completed non-short-circuit search has Bell(m) candidates; each direct test and replay is polynomial in the explicit encoded input and emitted witness length, up to ordinary bigint bit-cost factors. This is not polynomial in variable m. Finite termination assumes sufficient resources; finite-budget or caught interruption is INCOMPLETE with null exact fields. The existing C028 implementation is independently audited against a separate oracle; this dossier adds no new benchmark evidence. Fixed m yields polynomial work in the remaining explicit input, but the bound is not uniform polynomial in m.

**Counterexample boundary.** Σ={a,b}, P={a,b}, N={ab}: each positive separately differs on some singleton but neither singleton distinguishes ab from both; the singleton partition is incompatible. It is unsound to change the quantifier order in the inner test. Biggest overlooked issue: a feasibility witness is not an exact count or an optimality certificate unless the rest of the search is exhausted or soundly summarized.

## 2. Subset DP with a coverage state

**Status: PROVED** for the recurrence and exhaustive witness reconstruction. The word polynomial in counting-generating polynomial describes its algebraic form, not polynomial runtime.

**Formulation.** Index normalized N and represent it as a mask. For R⊆Σ of unassigned symbols and U⊆N of negatives not yet rejected by finalized blocks, let D(R,U;z) be a polynomial whose coefficient of z^k counts partitions of R into k blocks whose rejection masks cover U. Precompute R(B) for all nonempty B. Set

    D(∅,∅;z)=1;   D(∅,U;z)=0 if U≠∅;
    D(R,U;z)= Σ_{B⊆R, min(R)∈B} z · D(R\B, U\R(B);z),  R≠∅.

The ordering min(R) is the declared symbol order. Root D(Σ,N;z) provides C as the sum of coefficients, k* as the largest nonzero exponent, and O as that coefficient. If all coefficients vanish, C=0 and k* is undefined. Empty Σ follows directly from the two base cases. P=∅ and N=∅ are also covered by the same recurrence and finite projection criterion.

**Proof.** Every partition of nonempty R has exactly one block containing its least symbol. Choosing that B leaves a unique partition of R\B; it must cover precisely the still-uncovered requirement U\R(B). Conversely every such completion with B covers U. The anchored choice makes the decomposition one-to-one, including when several blocks reject the same negative; multiplying by z counts the chosen block and summing adds distinct partitions. Induction on |R| proves every coefficient. This supplies C, k* and O, not automatically the correct first two full-alphabet RGSs.

**Canonical witnesses.** Store enough exact DP values/child choices and traverse all feasible completions represented by the DAG, form each full partition, compute its original-alphabet RGS, and take the two smallest in each requested family, with replayed H factors. This is correct by the bijection and coefficient proof; the additional traversal can be Bell(m) in the worst case. Alternatively a faster reconstruction is a separate algorithm requiring its own lex-order proof; anchored submask iteration alone does not prove the first RGS. Counts may be generated without materializing every partition, but the simple witness reconstruction described here may revisit many DAG paths.

**Bounds.** With n=|N|, at most 2^(m+n) states and O(3^m·2^n) anchored submask transitions, plus a polynomial factor in m for polynomial coefficients, bigint operations, masks, and projection precomputation; storing all state polynomials adds an O(m) coefficient factor. A coefficient is at most Bell(m), requiring O(1+log Bell(m)) bits. Precomputing every R(B) takes 2^m times a polynomial in L and uses O(2^m n) bits for rejection masks apart from object overhead. These are conservative exponential bounds; no polynomial claim in variable m or n follows. Further truncation to saturated counts loses exact C/O.

**Safe rule.** If U is not a subset of R(R), no remaining block B⊆R can reject an uncovered n, by monotonicity, so the state has zero completions. Do not prune a partial block merely because it presently rejects no negative: P={ab}, N={ba} has no singleton rejection but the full block rejects ba. Biggest overlooked issue: state multiplicities and full-RGS witness ordering are different tasks from computing one maximum.

## 3. Exact-cover block selection

**Status: PROVED** for the augmented formulation and exhaustive full-contract extraction; a standalone optimization solve has the narrower guarantees below.

**Formulation.** Enumerate every nonempty B⊆Σ; introduce a Boolean x_B. Require

    Σ_{B∋a} x_B = 1                       for each a∈Σ,
    Σ_{B:n∈R(B)} x_B ≥ 1                 for each n∈N,
    maximize Σ_B x_B.

The first group is exact cover of symbols; the second is an additional negative-coverage constraint, not an ordinary exact-cover column. A selected block may cover zero negatives. With Σ=∅ there are no variables or symbol constraints; each negative constraint is 0≥1, so the empty family is feasible iff N=∅ and its objective is zero.

**Proof.** A feasible Boolean assignment selects pairwise disjoint nonempty subsets covering each symbol exactly once; these selected blocks form a partition. Negative constraints assert exactly that their R masks cover N, equivalent to compatibility. Conversely every compatible partition sets precisely its block variables to one and satisfies all constraints. The maps are inverse, so assignment count is partition count C; objective value is block count, its maximizers count O. This is an exact representation regardless of the algorithm used to solve it.

**Scope and output.** There are 2^m−1 potential variables and at most m+n core constraints, with exponentially many incidence coefficients and exponential projection precomputation. Enumerating only selected candidate blocks changes the feasible family unless it is independently proved that every relevant block remains present; bounded block size or heuristic filtering alone does not establish exactness. An exact optimizer yielding one assignment proves at most k* if solver optimality is certified; it does not automatically provide C, O, first-two full RGSs, or valid projected-word witnesses. One full-contract route is to enumerate all satisfying block assignments uniquely, compare their full RGSs, and replay witnesses; this is exact but can be expensive. Additional counting/reconstruction algorithms require proof.

**Counterexample.** Under P={ab}, N={ba}, choosing only singleton blocks makes the representation infeasible although the oneblock assignment is compatible. Rejecting singleton blocks solely because they currently reject no negative is unsound. Biggest overlooked issue: ordinary exact cover of symbols omits the negative-coverage condition; ordinary set cover does not enforce symbol ownership exactly once.

## 6. Exact branch-and-bound (anchored finalized blocks)

**Status: PROVED** for the stated bounds and output-dependent pruning rules, conditional on resolving every relevant branch.

**Formulation.** Each search node contains j finalized pairwise-disjoint blocks, remaining symbols R, and U=N minus the union of finalized rejection sets. Branch over every nonempty B⊆R containing min(R), append B, and continue on (R\B, U\R(B)). Start from (0,Σ,N). A complete node with R=∅ is compatible iff U=∅. Maintain a replayed compatible incumbent and all unresolved frontier nodes. Any node has block-count upper bound j+|R| because every future block is nonempty. If U contains some n outside R(R), the node has no compatible completion by R monotonicity. These rules require R to mean *remaining unassigned* symbols and all earlier blocks to be final; no such coverage prune is justified for arbitrary growing RGS blocks.

**Proof.** The least-remaining anchor produces each partition once by repeatedly choosing the block containing that symbol. For a given node every remaining block uses at least one of |R| remaining symbols, so j+|R| is a valid upper bound. Every future block lies in R, hence R(B)⊆R(R); if a negative cannot be rejected by R, no completion can cover it. A feasible incumbent is a lower bound. If every unexplored node is either exhaustively searched or removed by a sound infeasibility/bound proof, the greatest feasible block count is exact.

**Different output obligations.** For *maximum value only*, a branch with upper bound ≤ incumbent may be skipped after a valid incumbent exists; for optimal tie counts or canonical first optimal witnesses, equality can contain additional required optima, so an unaggregated branch is prunable on an objective bound only when its upper bound is strictly below the incumbent. For the all-compatible count C or first two all-compatible witnesses, even a strictly lower objective bound can hide relevant compatible partitions: such a branch can be discarded only if proved infeasible or its exact count/order contribution is otherwise incorporated. Two observed equal incumbents do not exclude a better unexplored solution. Until all required branches are resolved, retain only replayed feasible lower bounds and sound upper bounds; do not label O, C, or canonicality exact.

**Cost and edge cases.** The finite anchored tree contains every set partition as a leaf, so in the worst case exponential/superpolynomial work remains; branch bookkeeping, bitsets, identifiers and arbitrary-precision counts add costs. Empty Σ is handled by the root complete-node test; contradictory labels may be rejected after validation. A finite deadline can stop before proof, in which case the state is incomplete, not incompatible. Biggest overlooked issue: an optimization prune that preserves k* can still destroy C, O or lexicographic witness guarantees.

## External primary references and scope

- Stamatelatos and Efraimidis, *Lexicographic Enumeration of Set Partitions*, https://arxiv.org/abs/2105.07472: set-partition enumeration background, not a proof of this sample criterion.
- NIST DLMF §26.7, https://dlmf.nist.gov/26.7: Bell numbers count set partitions and B(0)=1.
- Björklund, *Exact Covers via Determinants*, https://arxiv.org/abs/0910.0460: a randomized algorithm for specialized exact-cover decision problems; it does not establish this full counting/ordered-witness problem.
- Henry et al., CoALA v3, §4.1 Proposition 5 and §6.1 Corollary 12, https://arxiv.org/html/2504.16624v3: related observation-projection obstruction for active LTS learning with possibly overlapping distributions; not asserted to be identical to this disjoint passive objective.

These proofs adapt known combinatorial methods and prior C027/C028/C026 work; no novelty or general polynomial runtime claim is made. The threshold optimum is NP-complete under variable alphabet by the one-negative reduction in `../../polynomial_partition_v27/complexity/COMPLEXITY_PROOF.md`, subject to its assumptions. Complexity statements concern mathematical procedures, not measured speed.
