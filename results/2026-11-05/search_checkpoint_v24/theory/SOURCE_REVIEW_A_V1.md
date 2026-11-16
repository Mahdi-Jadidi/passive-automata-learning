# Actual-source review of C024-A v1

Verdict: no blocking correctness issue found by independent mathematical/source inspection. This is not an experimental audit or promotion decision.

## Read ledger
R5: results/2026-11-05/search_checkpoint_v24/implementation/candidate_c024a_v1/gate_v1.py
SHA256: 9725a263266f4e131019936e771b5df1cb100cd5715ec85c7dae90040f7e33f4 (locally verified).
The complete source was read. Earlier R1–R4 and their hashes are in INPUT_LEDGER_V1.md. Initial absence notes there refer to the earlier snapshot and the earlier proposed candidate_a_v1 path; R5 supersedes the pending-source status for the actual candidate_c024a_v1 path.

## Proof-to-code check
- The added branch occurs after full validation, unary and atom shortcuts and atom-witness failure; it is guarded by known_k is None. Existing known-K DFS remains below it.
- r≥1 follows from a validated nonempty alphabet and nonempty connected components. On disjoint labels r=1 cannot reach this branch, because the atom partition is then oneblock and passes the exact witness test. Even if considered algebraically, range(0) for r=1 is safe.
- tail ranges from 0 to 2^(r−1)−2 inclusive. Therefore side0=1|(tail<<1) contains atom zero, is contained in full_mask, and never equals full_mask. side1=full_mask^side0 is its nonempty complement. The mapping is injective and covers every split whose first side contains atom zero exactly once: 2^(r−1)−1 candidates.
- witness([side0,side1]) uses the existing exact full-sample reject masks and all-negative coverage. No current-coverage pruning or quantifier relaxation is introduced. Atom expansion and swap-forest proof are retained.
- First success returns oneblock plus the split. Disjoint validated labels justify oneblock without another projection pass; a two-block witness differs from oneblock. Stop1 is consequently sufficient for ambiguous.
- Only normal completion of the complete loop returns certified_unique. Coarsening plus the sound atom quotient excludes all other partitions. Exhaustion route is explicit; search_exhausted=False on early success is appropriate.
- Each iteration polls; exact projection/witness helpers poll; oneblock construction and final emit poll. Existing Halt/KeyboardInterrupt/RecursionError/MemoryError handling returns unresolved. The branch introduces no recursive enumeration.
- search_nodes now counts split iterations on this route, rather than RGS tree nodes. bipartitions_tested is explicit. complete_candidates includes the earlier atom test and each witness attempt; direct oneblock helper construction does not increment it. Report these metric meanings when comparing methods. reject-cache hits include preceding shortcut/witness work.

No independently replayable collision-cover certificate is added: search_exhausted is solver metadata, not an independent exhaustion proof. Small exhaustive reference checks and witness replay remain required. No tests or timing were run by this reviewer.

## B implementation obligations (separate candidate only)
Manager-reported cProfile cumulative DFS costs D .441/.444 seconds and obstruction_m8 .634/.637 seconds support bounded exploration of B. These figures were supplied by the manager, not independently inspected here; they are instrumented attribution, not speed evidence or necessarily known-K coverage.

1. Fork the frozen C020 baseline separately from A; enable the envelope only on the intended known-K DFS path, preserving count bounds and stop2 semantics. Freeze and hash source before audit/timing.
2. At a well-defined RGS prefix with assigned positions [0,pos), derive U exactly as the remaining atom mask. Compute OR_i reject(B_i|U), and reject(U) only when U is nonempty. Use immutable full P/N and the existing exact negative-index semantics. Prune only if this optimistic envelope misses a negative. Never accept a completion from envelope coverage.
3. Check count feasibility before expensive envelope work. Poll envelope mask requests/union work. Preserve restore/pop discipline, exact leaves, timeout-to-unresolved and complete-validation behavior. Keep existing bounded cache; no eager exponential table or adaptive invocation policy in this version.
4. Record checked/pruned nodes, added reject requests, cache hits/misses and projection work. Attribute cache eviction/recomputation and instrument overhead separately. Keep counters semantically explicit; smaller node counts alone do not establish benefit.
5. Retain aaccbb/ccaabb with alphabet abc, K=2: prefix a|b, U=c has zero current coverage yet compatible extension ac|b. Include full-family known-K unique/ambiguous/incompatible controls, zero remaining atoms and block-count boundaries; independently replay all returned witnesses.
6. Establish correctness before same-input end-to-end timing, using the frozen protocol and keeping regressions/timeouts. If the envelope overhead outweighs saved DFS work, retain baseline and report the negative result. Source review of B is still required once it exists.
