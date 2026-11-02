# Static review of C010 scale-oracle constructions

Reviewed source: `audit/generate_scale_corpus_v2.py` (read only). This checks
the four mathematical input/oracle constructions, not the generator's runtime,
provider behavior, or the independent oracle implementation. No script was run.

## Findings

| Cell | Construction argument | Exact family / count | Finding |
|---|---|---:|---|
| `m14_seven_pair_atoms` | Each positive `xy` and negative `yx` is an adjacent unequal swap, forcing each of the seven disjoint pairs into one atom. On its pair block, `yx` is absent from the positive pair projections, so the atom partition is feasible. Every compatible partition is exactly a coarsening of those seven atoms. | All partitions of 7 atoms: `Bell(7)=877`; spectrum `S(7,k)`. A cross-atom pair is together in `Bell(6)=203`. | Cleared |
| `m64_eight_connected_groups` | The 56 adjacent path edges are each witnessed by positive `xy` / negative `yx`, forcing every path's eight symbols into one connected atom. No reversed edge word is a positive projection on that path block, so the eight-atom partition is feasible; all coarsenings are compatible. | All partitions of 8 atoms: `Bell(8)=4140`; spectrum `S(8,k)`. A cross-group pair is together in `Bell(7)=877`. | Cleared for this structured construction |
| `m10_graph_empty_five_semantic_pairs` | Each doubled pair positive `xxyy` versus negative `yyxx` has four differing positions, so it creates no adjacent-swap edge. If its two symbols were separated, every block projection of positive and negative would agree; thus each pair is nevertheless a semantic must-link. The five pair atoms reject their corresponding negatives on the atom partition, so all coarsenings are feasible. | All partitions of 5 semantic atoms: `Bell(5)=52`; spectrum `S(5,k)`. A cross-pair coownership count is `Bell(4)=15`. | Cleared |
| `long_word_length_4096_forced_pair` | The unique positive `a^2048 b^2048` and negative `b^2048 a^2048` have no adjacent-swap witness. Separating `a,b` leaves identical local projections, so they must co-own. Their joint block rejects the negative; unused `c,d` are free atoms. | All partitions of 3 semantic atoms `{ab},{c},{d}`: `Bell(3)=5`; spectrum `S(3,k)`. Any other pair is together in `Bell(2)=2` partitions. | Cleared |

For the first two cells the swap graph's connected components are the stated
atoms. For the last two, the provider's swap graph is empty; the semantic
coownership argument does not assume that missing graph edges imply separation.
In every cell, a feasible atom partition makes the compatible family exactly
all its coarsenings, so the Bell/Stirling oracle formulas follow. These are
counts of unordered symbol partitions, not language realizations.

## Scope and conclusion

The `m64` input is deliberately structured as eight disjoint paths of eight
symbols, with a replayable must-link witness on every path edge. Its oracle
enumerates the `Bell(8)` quotient partitions and lifts them. This establishes
correctness for that constructed 64-symbol instance; it does not establish
coverage or performance for arbitrary 64-symbol inputs, nor does it enumerate
`Bell(64)` partitions.

Static construction review: **cleared; no mathematical counterexample found**
in the four claimed atom counts or their Bell/Stirling totals. Independent
oracle execution and provider acceptance remain separate checks; this review
does not certify either.
