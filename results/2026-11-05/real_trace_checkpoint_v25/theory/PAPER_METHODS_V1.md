# C025 paper methods v1

## Exact observation model
A finite alphabet consists of complete atomic event IDs. An unordered partition assigns every ID to one nonempty block. Each block is a deterministic finite-state Mealy transducer with the same declared initial state across traces. Only the owner of the current event consumes it, updates state and emits the observed output. Outcomes are not history inputs. Unknown-labelled events still enter local memory but impose no output constraint; empty traces impose none.

For block B, finite-depth key is (suffix_d(prior projected input history),current event). Full depth uses the complete projected history through current. Short histories retain their true length. A block is admissible iff no two known-labelled positions owned by it have equal keys and unequal outputs. A partition is compatible iff every block is admissible. Determinism proves necessity. For finite depth, assign outputs consistently on observed keys and extend arbitrarily, using suffix states. For full depth, a trie of observed local prefixes gives finite states and transition outputs; add arbitrary outputs and a fallback state for unseen extensions. This proves finite-state sufficiency without identifying a minimal or physically true machine. Current implementation supports Boolean labels or None; multiclass requires a separately versioned schema.

## Complete finalized-block search
For m≤8 cache each nonempty block check. Recursively anchor the next block at the least remaining ID and enumerate every subset of the other remaining IDs. Check this FINAL block; if admissible, recurse on its complement. Every unordered partition has exactly one path: its block containing the least remaining ID is uniquely determined at each step. Discarding an inadmissible finalized block is safe. Rejecting an inadmissible growing partial block is unsafe because expansion may add distinguishing context.

```text
cover(remaining, finalized):
    poll(); apply optional externally trusted K count bounds
    if remaining empty: record witness if count allowed; return
    for B subset of remaining containing least remaining ID:
        if admissible(B): cover(remaining minus B, finalized plus B)
        if two witnesses found: stop
```

Two distinct terminal witnesses certify ambiguity. Normal exhaustion with one solution certifies uniqueness; zero certifies incompatibility. Interruption returns unresolved, without exhaustion. Malformed schema returns invalid_input. Witness rules preserve observed outputs and explicitly leave unobserved outputs/extensions arbitrary; conflict certificates identify source positions, equal contexts and unequal labels. Exhaustion metadata alone is not an independently replayable enumeration proof.

## Complexity and identifiability
At most 2^m−1 distinct block masks are checked. A direct finite-depth scan over E events costs O(E(d+1)) per block under customary hashing assumptions, plus record/storage overhead. Full-history keys use shared (parent,event) trie IDs rather than copied complete histories. These bounds do not establish empirical speed. Memory includes context dictionaries, cached summaries and output witnesses.

Distinct block checks must not be confused with search paths. Without memoized cover-state dynamic programming, canonical partition traversal retains Bell-type worst-case cost, with prefix overhead; fixed-K complete families number S(m,K). Stop2 can terminate early but supplies no polynomial guarantee. Validation and witness output add work.

At full history, merging compatible blocks preserves compatibility: equal merged projected words have the same last ID and therefore the same old owner, and project to equal old local words. If no identical full histories carry unequal known outputs, oneblock fits. Thus a nontrivial full-history partition always has a oneblock alternative unless external K excludes it; unknown-K unique can only be oneblock. Identical-history contradictions make every partition incompatible.

For every finite depth d≥1 coarsening can fail: newly included events may evict informative older events from the suffix. No full-history bipartition shortcut or C024 swap must-link/envelope applies there. Depth0 is current-type output constancy; when it holds, every partition fits. Increasing depth relaxes consistency and may increase ambiguity. Neither compatibility nor conditional finite-depth uniqueness alone establishes physical ownership.

## Assumptions and evaluation protocol
Freeze encoding, order, boundaries, label alignment and Unknown handling. CAGE2 converter associates action i with next-record status; audit that alignment and last-record accounting. Host-target qualification is an explicit preprocessing assumption even with opaque IDs. TrueState and host truth are evaluation-only. Keep unknown selected events in context. Selecting top8 by training frequency changes the representation: labels on other current types are excluded and history is projected onto the selected block; missing same-host causal actions remain a limitation.

Fix depths0,1,2,4,8,full. Report full-alphabet known-host consistency separately from subset-compatible-family membership and truth comparison. Split source lineage before prefixes/truncations, and fix selection from training only. Report selected/excluded events, types, files and known/unknown labels. Unseen heldout contexts require abstention or a separately specified prediction rule; witness arbitrary defaults are not identified predictions.

BGL is a separate operational-log arm using template EventId input and alert output, with Node evaluation-only. Sampling does not establish complete causal history. Template sharing across nodes challenges unique-symbol node ownership, while per-template label constancy would make depth0 nondiscriminating. These are diagnostics to measure, not results asserted here.

Independent audit compares complete small families and directly replays witnesses/conflicts, unknown-event memory, finite-depth coarsening failures, malformed late input and interruptions. CLI serialization lies outside cooperative solver polling. Manager-assigned outer25/120-second wall caps cover the relevant jobs through serialization; capture process failures and censored runs explicitly. Resource limits are not solved runtimes. Actual-data audit results remain pending this writing.

## Provenance and present evidence
This method reintegrates C016 semantic obstructions and C017 selected-output proofs. External novelty is unassessed; no RPNI improvement, speed, hardware recovery or production prediction claim is made. See MODEL_CONTRACT_V1.md, COUNTEREXAMPLES_V1.md and SOURCE_REVIEW_V1.md.

Read-only inspection of smoke_v1.py and smoke_results_v1.json supports a limited developer-test statement:162 fixture/depth/K rows reportedly pass, using direct context/family controls, JSON-roundtrip witness replay, validation and expired-deadline checks. Each evaluated block is also compared with a copied C017 evaluator whose SHA256 matches the historical source. The report binds the reviewed solver hash and records zero real-data solver runs. This is developer comparison evidence on fixtures, not independent audit or a historical C017 actual-data run. This reviewer did not execute tests.
