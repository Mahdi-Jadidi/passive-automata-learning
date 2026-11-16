# C024-A exact delta

Source: frozen current C020 C2. Only METHOD and the unknown-K fallback immediately after atom_witness failure / known_k==r rejection change. CLI remains byte-identical. B is not implemented.

Let r be the number of forced atoms. Enumerate tail integers 0 through 2^(r-1)-2 inclusive. Set side0 = 1 | (tail << 1), side1 = ((1 << r)-1) xor side0. Thus atom zero is fixed in side0, both sides are nonempty, each unordered bipartition appears exactly once. Poll before each candidate and use the unchanged exact witness/reject helper. Return the first compatible split together with oneblock as two witnesses of ambiguity. If all splits fail, release oneblock as unique with search_exhausted=true. Exceptions retain the existing unresolved output, without speculative partitions.

Correctness uses C006 `results/2026-11-01/partition_identifiability_v6/theory/PROOFS_v1.md`, T3 (and its coarsening basis T2). Any compatible nontrivial partition respecting forced atoms merges to a compatible bipartition of atoms. Disjoint labels guarantee the oneblock witness after validation. This reuses the existing theorem; no novelty claim is made.

New routes: two_block_search_witness (search_exhausted=false), exhausted_forced_atom_bipartitions (true). Both include bipartitions_tested and proof_basis. Search_nodes counts tested splits on this fallback, not recursive states or runtime. complete_candidates still includes the failed atom precheck. The potential split count is 2^(r-1)-1; it is not a formula for full runtime. Exact projection/cache/validation, fast paths, and known-K DFS are unchanged.

Smoke: syntax compilation; known-K obstruction; unary, swap fast, contradiction, invalid input; unique m8 exhaustion; first compatible fallback split; direct independent projection replay of emitted witnesses; canonical enumeration r=2..8; already expired deadline. These are development controls, not the independent full audit. No full benchmark was run.

Review concerns: existing certificate replay tools may require the two new route names; search_nodes semantics differ on this branch; exhausted metadata is not a standalone independently replayable exhaustion certificate. Huge r still has exponential enumeration, and big-integer bound construction is not interruptible inside a single Python operation (existing code also builds integer masks); deadline polling covers each enumerated candidate and existing projection/witness loops. No public promotion is implied.
