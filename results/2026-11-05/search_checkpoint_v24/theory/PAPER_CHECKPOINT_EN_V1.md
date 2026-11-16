# C024 paper checkpoint: exact partition search

## Model and scope

Let A be a finite nonempty declared alphabet, P and N finite samples of complete words over A, with noiseless disjoint labels. An architecture is an unordered partition π of A into nonempty blocks. Each block B has an arbitrary regular language L_B over B. A word is accepted exactly when its projection onto every block belongs to that block’s language. No state bound, finite-factor assumption, generator ownership, or physical truth enters inference. Optional K is an externally trusted exact block count. Uniqueness below concerns the compatible partition, not factor languages or automaton states.

Write P_B={projection_B(p):p∈P}, and R(B)={n∈N:projection_B(n)∉P_B}. A partition is feasible exactly when its block rejection sets cover N. Necessity follows because every positive forces acceptance of every local projection. Sufficiency follows by choosing the finite regular languages P_B. The quantifiers are essential: each negative needs one block separating it from **all** positives; different negatives may use different blocks.

An adjacent distinct-symbol swap between a positive and negative forces the two symbols into the same block, since separate ownership preserves every projection. Connected components of these sound constraints form forced atoms. Every feasible partition groups whole atoms. This quotient is sound even though the swap graph is incomplete. Let r denote the number of atoms, m=|A|, and T the total input characters.

## Candidate A: unknown-K bipartitions

For S⊆C, R(S)⊆R(C): equality of a negative and positive projection on C implies equality on S. Hence feasibility survives coarsening. Every feasible partition with at least two blocks coarsens to a feasible bipartition. Meanwhile oneblock is always feasible because full-alphabet projection is identity and labels are disjoint. Thus finding one feasible split proves ambiguity, while rejecting every split proves oneblock unique.

A changes only the unknown-K fallback after the forced-atom partition fails; validation and existing shortcuts remain intact. Number atoms from zero, fix atom zero on the first side, and exclude the full first side:

```text
F := (1 << r) - 1
for tail := 0,...,2^(r-1)-2:
    poll()
    S := 1 | (tail << 1)
    W := exact_witness([S, F xor S])
    if W exists: return ambiguous(oneblock_witness(), W)
return certified_unique(oneblock_witness(), exhausted=True)
```

Each unordered nonempty split occurs exactly once. The first split suffices because oneblock supplies a distinct second witness. Only complete rejection permits uniqueness; interruption returns unresolved. Sound atom constraints exclude splits through atoms. These are reintegrations of C006 T1–T4/T7–T9, not new theorem claims.

General atom partitions number Bell(r); A tests at most 2^(r−1)−1 bipartitions. This is a candidate-family bound, not a total-time formula. Projection, validation, graph construction, caching, witness creation and output remain. On this route search_nodes counts split iterations rather than RGS tree nodes. complete_candidates includes the preliminary atom witness attempt; direct oneblock construction is not counted.

## Candidate B: known-K envelope

B separately modifies the C020 restricted-growth-string DFS. At a prefix with growing blocks B_i and unassigned union U, every final existing block lies within B_i∪U; every new block lies within U. By rejection monotonicity, all negatives rejectable by any valid completion lie in the envelope below:

```text
DFS(pos, blocks):
    poll(); apply exact-K count bounds
    if terminal: evaluate exact witness; return
    E := union_i R(B_i union U)
    if number_of_blocks < K: E := E union R(U)
    if E != N: prune
    otherwise continue ordinary RGS children, stopping after two solutions
```

When the current block count equals K, no valid completion can create another block, so omitting R(U) is safe. Envelope coverage is only necessary; overlapping optimistic uses of U cannot certify a completion. Leaves still use exact witnesses. For A={a,b,c}, P={aaccbb}, N={ccaabb}, K=2, prefix a|b rejects nothing, but extending to ac|b succeeds. Pruning on current coverage alone would therefore be unsound. B implements the C020 envelope argument.

B retains worst-case enumeration of S(r,K) fixed-K partitions, where S is a Stirling number of the second kind, plus DFS-prefix overhead. A checked prefix adds up to j+1 rejection requests for j growing blocks, or j when no new block is allowed. Cache misses scan full traces for exact projections, and envelope work can evict useful cached masks. Neither soundness nor fewer nodes guarantees faster execution.

## Evaluation protocol and correctness

Frozen protocols are [PROTOCOL_V1.md](../audit/PROTOCOL_V1.md) and [PROTOCOL_B_V1.md](../audit/PROTOCOL_B_V1.md). Each matrix uses six cells, five fresh-process repetitions with rotating provider order, a 20-second cooperative deadline, 25-second outer cap, and 600 process-seconds per provider. Main time includes startup, reading, solving and output; hashing and independent replay are excluded. No memory measurements were performed. Medians below are seconds and appear only for five completed validated runs; censored durations are not solved runtimes.

Independent full-family oracles and certificate replay do not import solver code. This independence concerns checking/execution, while reused checker authorship is disclosed. The initial A audit made 689 calls per provider over 196 content-distinct inputs; the latest FINAL_SUMMARY_V2.json corrects the earlier 20-repeat disclosure to 21 repeated job IDs (20 random-m2 plus one obstruction-m2), leaving 668 distinct job IDs. Ten supplemental calls per provider are recorded separately. B uses 680 calls per provider and 202 input contents after deduplication and supplemental controls. These overlapping calls must not be summed as distinct datasets. Reports record zero correctness errors. Both validated timing summaries report semantic/certificate acceptance and preregistered gates passing, with no errors.

At this writing, the newer [FINAL_SUMMARY_V2.json](../audit/FINAL_SUMMARY_V2.json) also reports integrated correctness complete: 680 independently replayed calls and four CLI checks, zero errors. The CLI checks include midsearch interruption returning unresolved after 131 nodes. Integrated official timing remains unmeasured. This updates the earlier in-progress status without transferring separate-candidate timings to the integration.

[RESULTS_V1.md](../audit/RESULTS_V1.md) preserves the final disclosures: all 120 official timing attempts were retained; capture-integrity checking covered 41 attempts with no errors. Manager harness review arrived after A launch. Post-timing status-aware validation corrected the raw distributions, which included unresolved durations; no timing was discarded or restarted. A supplemental preparation KeyError is retained as C024-SUPP-PREP-001 and was fixed in a new script before supplemental provider execution. These provenance details qualify the evaluation record without changing the completed-run tables.

## Separate A timing matrix

Source: [C024-TIMING-01/VALIDATED_SUMMARY_V1.json](../audit/runs/C024-TIMING-01/VALIDATED_SUMMARY_V1.json).

| Cell | C020 completed | C020 median | A completed | A median |
|---|---:|---:|---:|---:|
| obstruction_m8_noK | 5/5 | 0.664551 | 5/5 | 0.300405 |
| obstruction_m10_noK | 5/5 | 4.782940 | 5/5 | 0.463004 |
| obstruction_m12_noK | 0/5 | — | 5/5 | 0.764873 |
| ambiguous_noK | 5/5 | 0.314259 | 5/5 | 0.360716 |
| D_K4 | 5/5 | 0.603013 | 5/5 | 0.657833 |
| A_K4 | 5/5 | 1.140300 | 5/5 | 1.290725 |

A improves the designed unique stress cells but regresses 14.78% on ambiguous_noK despite fewer counted search nodes. Known-K guards D and A increase 9.09% and 13.19%, respectively, within the preregistered 15% guardrail; their algorithmic work counts are unchanged. No finite solved-time ratio is assigned to m12 baseline’s five unresolved runs.

## Separate B timing matrix

Source: [C024-B-TIMING-01/VALIDATED_SUMMARY_V1.json](../audit/runs/C024-B-TIMING-01/VALIDATED_SUMMARY_V1.json).

| Cell | C020 completed | C020 median | B completed | B median |
|---|---:|---:|---:|---:|
| D_K4 | 5/5 | 0.453818 | 5/5 | 0.406504 |
| obstruction_m8_K4 | 5/5 | 0.676667 | 5/5 | 0.288680 |
| obstruction_m12_K4 | 2/5 | — | 5/5 | 0.441941 |
| unsafe_K2 | 5/5 | 0.557873 | 5/5 | 0.499358 |
| ambiguous_K3 | 5/5 | 0.867945 | 5/5 | 0.582029 |
| A_K4 | 5/5 | 1.965532 | 5/5 | 1.920181 |

D nodes fall from 4005 to 207 and complete-candidate calls from 1702 to 11, but median process time improves only about 10.4%. In ambiguous_K3, search nodes and candidate calls remain 15 and 3; no envelope prune occurs, while projection work increases. Its observed time decrease is therefore not causal evidence of pruning benefit. B’s m12 baseline has mixed completion, so neither its completed-only median nor a speedup ratio is reported. A and B baselines belong to separate rounds and must not be pooled or cross-divided.

## Limits and provenance

For the deletion obstruction n=a1...am, positives delete one symbol each, giving T=m², an empty swap graph and r=m. Every proper block matches a positive deleting an outside symbol, so only oneblock is feasible; valid K≥2 is incompatible. This intentionally stresses search. It does not represent natural logs. The historical A control is planted and largely exercises shortcuts. No natural-log recovery or RPNI comparison is established.

Proof details and actual-source correspondence are in C024_A_PROOFS_V1.md, OBSTRUCTION_AND_B_REVIEW_V1.md, SOURCE_REVIEW_A_V1.md and SOURCE_REVIEW_B_V1.md. Local provenance is C006/C020; external novelty review remains pending. Exhaustion metadata alone is not an independently replayable general proof. Public promotion remains the manager’s decision; this checkpoint does not announce it.

