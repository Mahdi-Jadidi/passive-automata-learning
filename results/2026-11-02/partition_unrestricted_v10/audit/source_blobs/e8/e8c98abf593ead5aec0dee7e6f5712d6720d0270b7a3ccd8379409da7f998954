# C010 four-cell scale correctness gate — preregistration

## Frozen data and provider

The four input byte strings were frozen after the 128-case independent full-set gate passed and before any scale oracle or scale provider run.

* Scale input manifest: `audit/scale_v1/manifest.json`, SHA-256 `cd140f1e2d3b3976febd5c277c7aa3a045f94d658c9f5674084f2abd2f1eba2f`.
* Generator: `audit/generate_scale_corpus_v2.py`, SHA-256 `f62c3cc82d55c9df23822d570684b31fa2da705a99a96bcf81de665dfde01a46`.
* Provider readiness: `implementation/READINESS_V3.json`, SHA-256 `13733c49a331a05dd1b6e59dbb73cd2323d869b17d50bed88f9997ae855b420e`.
* Provider solver: `implementation/unrestricted_solver_v2.py`, SHA-256 `4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502`.
* Root CLI wrapper: `solve.py`, SHA-256 `533bcbffe39fa18648567abcaeb1fd775d75d05561f42be007c03c849f41a989`.

No source, input or expected result may change after this protocol is saved. Each cell is run **once**, in manifest order, in its own fresh root-CLI subprocess with cooperative `--seconds 28`, an outer hard capture deadline of 30 seconds, and no `--enumerate`. Complete and incomplete outputs are both retained. No timeout, `unknown`, or incomplete cell is retried. These are correctness-only scale observations; the four sequential cells are not a timing benchmark and establish no speed comparison.

## Independent oracle rules and expected cells

The oracle is separate from provider code. For the first two inputs it replays every adjacent-swap edge, reconstructs connected components, directly checks the atom partition and then enumerates only the quotient partitions: Bell(7)=877 and Bell(8)=4140. Edge soundness proves every compatible symbol partition must coarsen the components; atom feasibility proves every such coarsening is compatible. It must not enumerate Bell(14), Bell(64), or describe the quotient family as a hidden physical count.

For the m=10 graph-empty case, independently enumerate all Bell(10)=115,975 symbol partitions and apply direct projection feasibility; do not trust the provider graph to reveal semantic must-links. The resulting family is expected to be exactly the coarsenings of the five doubled pairs. For the length-4096 case, enumerate all Bell(4)=15 symbol partitions directly. Replay all positive/negative projections and pair witnesses for every completed provider cell.

| Cell | Expected result | Required structural checks |
|---|---|---|
| `m14_seven_pair_atoms` | 877; spectrum `S(7,k)`; kmax 7 | 7 replayed edges, 7 pair-atoms, atom partition feasible; within-atom pair count 877, cross-atom count Bell(6)=203 |
| `m64_eight_connected_groups` | 4,140; spectrum `S(8,k)`; kmax 8 | 56 replayed edges, 8 groups of 8, atom partition feasible; within-group count 4,140, cross-group count Bell(7)=877; never enumerate Bell(64) |
| `m10_graph_empty_five_semantic_pairs` | 52; spectrum `S(5,k)`; kmax 5 | 0 swap edges; provider retains 10 singleton graph-atoms and enters fallback; direct symbol oracle proves five semantic pairs; within-pair count 52, cross-pair count Bell(4)=15 |
| `long_word_length_4096_forced_pair` | 5; spectrum `S(3,k)`; kmax 3 | 0 swap edges; provider retains 4 singleton graph-atoms and enters fallback; direct 15-partition oracle proves `{a,b}` is one semantic atom; its pair count 5, every other pair count Bell(2)=2 |

For every result compare `complete/status`, total, all spectrum keys including zeros through `m`, both exact k bounds, all `m choose 2` pair counts/relations/witnesses, atom partition, edge records, atom feasibility, and counters. Independently replay the representative projection witness and every same/different pair witness. Default mode must not silently enumerate; `enumerated_partitions` stays null. Record `block_masks_computed`, `dp_states`, `dp_branches`, `swap_pairs_tested`, `swap_edges`, `atoms`, `atom_projection_checks`, and external capture elapsed/subprocess seconds. A complete mismatch rejects; timeout/incomplete is censored, not accepted as a count claim.

## Execution order

1. Capture the independent scale-oracle generation/check and validate its immutable output against the frozen manifest.
2. Capture the four root-CLI provider cells separately in the listed order; exactly one attempt each.
3. Capture an independent scale-output validator over the four raw attempts and exact inputs; preserve every raw stream, result and hash.

No performance benchmark, repeated timing, memory comparison, hidden-generator truth, or general speed claim is in scope.
