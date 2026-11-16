# Actual-source review of C024-B v1

Verdict: no blocking correctness issue found by independent mathematical/source inspection. No experiments, implementation edits, timing claim or promotion decision.

## Read ledger
R6: results/2026-11-05/search_checkpoint_v24/implementation/candidate_c024b_v1/gate_v1.py
SHA256: 4e5a8e39528efadf3d2eeaab2dfa02a0d77711d7028005737fe78a42b38cb9a3 (locally verified).
R7: results/2026-11-05/search_checkpoint_v24/implementation/candidate_c024b_v1/minimal.diff
SHA256: 83f822cb2184c600a1cf977745f96bd82f3f0c9993aa55d40a950f3b9ef902e1 (locally computed).
Complete source and supplied minimal diff were read; earlier local mathematical/baseline provenance is recorded in INPUT_LEDGER_V1.md. The diff is consistent with the reviewed insertion and metadata changes; no automated diff verification was run.

## Completion invariant and safe envelope
At dfs(pos,masks), masks partition exactly atom bits [0,pos). Each recursive step either adds bit pos to one existing mask and restores it, or appends that bit as a new block and pops it. Existing blocks are never merged. Thus unassigned=((1<<r)-1)^((1<<pos)-1) is precisely the set of remaining atom bits, with no high bits, because 0≤pos≤r.

Count pruning occurs first. At every checked nonterminal node j=len(masks)≤K and pos<r, hence U is nonempty. Every final descendant block extending B_i is a subset of B_i∪U. Every newly created block is a subset of U. Exact reject masks are monotone under symbol-set inclusion: a projection collision on a superset implies a collision on its subset. Therefore each completion's rejected-negative union is contained in the implemented envelope.

The conditional term reject(U) iff j<K is safe and tighter than the unconditional proposal: if j=K, any descendant creating a new block has too many blocks and cannot be a valid K-completion. All valid final blocks then extend existing blocks, so their B_i∪U terms suffice. If j<K, reject(U) covers every possible new final block. Sharing U among envelope terms is optimistic and cannot remove a valid completion.

reject returns only bits for existing negative indices. Consequently envelope is a subset of all_rejected; envelope!=all_rejected means at least one negative is absent, not merely a different bit encoding. The return on this condition is sound. Full coverage only allows DFS to continue and never directly accepts a solution.

## Source integration and boundaries
- All envelope behavior is guarded by known_k is not None; unknown-K RGS enumeration remains logically unchanged (METHOD identifies the separate candidate).
- Leaf exact witness evaluation precedes envelope evaluation. Count bounds at pos=r enforce exactly K before a leaf is tested. No reject(0) is introduced by the envelope.
- At the root j=0, reject(U) covers the whole alphabet; disjoint labels imply full coverage. This check is sound but can add overhead without pruning.
- The existing stop2 criterion, mask restoration, exact sample-wide reject implementation, bounded 4096-entry cache and exception-to-unresolved handling remain in use. Polls occur per envelope request and inside cache-miss projection work, with final emit polling retained.
- Exhaustive unique/incompatible outputs name the envelope rule. search_exhausted now means all valid descendants were tested or soundly excluded, not every complete partition was materialized. This metadata is not a separately replayable pruning/exhaustion proof.

## Measurement and audit obligations
Existing complete_candidates counts actual witness calls, not pruned completions; search_nodes includes nodes discarded by count bounds. envelope_checks counts nonterminal count-feasible checks and envelope_prunes their failures. Counters exist only once known-K fallback is entered, so shortcut routes can omit them. The implementation does not separately count envelope reject requests or cache misses; block_masks_computed records actual misses, and reject_cache_hits is aggregate. Do not claim more granular attribution from these fields alone; instrument a separate profiling version if required.

Required independent audit remains: small complete known-K families and replayed alternatives, the aaccbb/ccaabb current-coverage counterexample, j=K nodes, j<K nodes, count-bound failures and leaves, plus interruption behavior. Same-input end-to-end timing must include additional cache misses, evictions and projection work. This review establishes the pruning argument and its source correspondence, not experimental correctness evidence or speed benefit.
