# V47 handoff: exact compatibility without DFA enumeration

## What changed

V47 replaces the exhaustive teacher only for this decision: **given a fixed event-alphabet partition, can some tuple of regular local languages classify the finite labeled traces under conjunctive acceptance?** It returns `ACCEPT` or `REJECT`. The outer SAT search, witnessed cuts and optimum certificate checker keep their existing semantics. The exhaustive teacher remains available for its broader tasks.

## Model and exact criterion

Let D = (S⁺, S⁻) be a finite sample over declared alphabet Σ. Let P be a valid partition of Σ, and let π_B(w) retain the events of w in B, in order. The overall classifier accepts a trace if every block accepts its projection. Define H_B = {π_B(x) : x ∈ S⁺}.

**Decision rule.** Accept P exactly when for every y ∈ S⁻ there is a block B ∈ P such that π_B(y) ∉ H_B.

**Why it is exact.**

1. Every local language K_B that accepts the positives must contain H_B. If a negative y has π_B(y) ∈ H_B on every block, then every possible tuple of such K_B accepts y. This proves rejection.
2. Conversely, choose K_B = H_B on all blocks simultaneously. Every positive passes. The decision rule guarantees that each negative fails at least one block. Each H_B is finite and therefore regular. This proves acceptance.
3. The old V46 decision calls use a sufficient state bound on each block: one state for empty H_B, otherwise the number of distinct prefixes of H_B, including ε, plus a rejecting sink. The complete trie for H_B fits that bound. Hence the direct test supplies bounded witnesses whenever it accepts. Conversely, any accepted tuple of bounded DFAs defines regular languages and must satisfy the same rule. This establishes equality of the completed verdicts on the actual optimizer calls.

## How to integrate

```text
U := all negative indices
for each block B:
    if U is empty: return ACCEPT
    H := set of exact positive projections on B
    U := [i in U such that projected_negative[B][i] is in H]
return ACCEPT if U is empty, else REJECT
```

After each block, U is exactly the negative indices whose projections matched positives on every processed block. Filtering on the next block establishes the invariant by induction. Each set membership test is a test of the whole projected word, including order, repetitions and ε.

- Use the same original negative-index order across blocks. Two negatives may project to the same word and must still retain their own indices.
- Validate the partition and sample at the caller. The implementation reads the negative count from a block's projection list, so the optimizer handles Σ = ∅ before calling it. With zero blocks, the empty conjunction accepts every trace over the empty alphabet. Compatibility then requires S⁻ = ∅.
- In V47 the public checker returns the verdict. On a completed rejection, the outer solver still finds an uncovered negative and constructs the existing witnessed cover cut from the original projections. Optionally exposing an index from U would give a rejection witness, but that is not a change made in V47.
- An interrupted check must propagate its interruption. It must not return `REJECT` or trigger a cut based on unfinished work.

For k blocks, p positives, r negatives and L total event occurrences, the already materialized images have at most k(p+r) rows and exactly L event occurrences across all blocks. The decision takes O(k(p+r)+L) under standard expected hash-table costs on constant-size event IDs. Even scanning all stored positive projections for each lookup gives a polynomial worst-case algorithm. Direct projection from the original input is also polynomial for one specified partition.

## Applicability boundary

This is an exact substitute for the fixed-partition existential decision with unrestricted local state counts, or with per-block bounds that admit the canonical finite languages above. It does not compute the full relation of bounded DFA behaviors. Independently tighter state bounds or additional required local behaviors can invalidate the canonical witness and need their own decision procedure.

The polynomial teacher does not imply a polynomial algorithm for finding the maximum number of compatible blocks over arbitrary alphabets. For a graph with at least one edge, use one positive two-event word per edge and ε as the sole negative. A block rejects ε exactly when it is a vertex cover. Thus the optimum is n−τ+1, where τ is the minimum vertex-cover size. The outer search and certificate checking can still dominate.

## Evidence and source pointers

- All 4,374 direct teacher comparisons passed over both partitions of a two-symbol alphabet and all disjoint labelings of its seven words of length at most two. An injected interruption propagated without a verdict. [Independent checks](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/799d1aa3154044534321d5f3855dd512c7238e63/results/2026-11-19/polynomial_teacher_v47/checks/summary.json)
- In a matched ten-case test at 2 s, the projection version completed 10/10 and the exhaustive version 3/10. On one ordinary interactive fixture, two matched runs per version gave median solver times of 7.528 ms and 4.137 s respectively. These are workload-specific, end-to-end timings. [Experiment summary](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/799d1aa3154044534321d5f3855dd512c7238e63/results/2026-11-19/polynomial_teacher_v47/README.md)
- Code and formal argument. [Projection teacher](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/799d1aa3154044534321d5f3855dd512c7238e63/results/2026-11-19/polynomial_teacher_v47/projection_teacher.py) · [Proof ledger](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/799d1aa3154044534321d5f3855dd512c7238e63/results/2026-11-19/polynomial_teacher_v47/PROOF.md)
