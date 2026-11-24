# Next-session handoff 04 — P2.1 gate, final proof hardening, and P3 transition

**Date:** 2026-11-25  
**Repository:** https://github.com/Mahdi-Jadidi/passive-automata-learning  
**Integration branch:** `research/selector-v2`  
**Baseline:** `7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6`  
**Current decision:** Narrow P2.1 structural/reference gate passed on its recorded pins. A later hardening change to the independent bounded-deletion verifier is not yet included in the core combined-gate runner. Re-pin and rerun before declaring the current branch set fully closed or starting P3 implementation.

This file replaces chat memory as the continuity source. New chats must read it and the linked review reports before acting. Requested execution model is GPT-6.2 High, selected manually in each new chat; a prompt or GitHub issue cannot select the model or launch agents.

## 1. Current GitHub state (checked 2026-11-25)

Repository work remains isolated in four existing agent branches and four open draft PRs. Continue on these branches; do not create replacement branches and do not merge.

| Stream | Existing branch | Latest branch head at handoff | PR |
|---|---|---|---|
| Core / implementation | `research/v2-implementation-core` | `c5e7e170add6f92e129099bf7444f5fd7a29eb3a` | [#7](https://github.com/Mahdi-Jadidi/passive-automata-learning/pull/7) |
| Independent proof | `research/v2-proof-audit` | `cf5a007571853b6cdf6259fa2a9a95f5c1e351f8` | [#8](https://github.com/Mahdi-Jadidi/passive-automata-learning/pull/8) |
| Benchmarks | `research/v2-benchmarks` | `52d21e672b0ae6420cf677ff09c01bb2a3fd6b05` | [#9](https://github.com/Mahdi-Jadidi/passive-automata-learning/pull/9) |
| Interface | `research/v2-interface-audit` | `ae04a28304507fa16830fcb470f52103d9a588c4` | [#6](https://github.com/Mahdi-Jadidi/passive-automata-learning/pull/6) |

All four PRs were still open and Draft at handoff. No PR has been merged. Issue [#10](https://github.com/Mahdi-Jadidi/passive-automata-learning/issues/10) is the active P2 integration thread. Latest integration decision is [INTEGRATION_REVIEW_03.md](INTEGRATION_REVIEW_03.md), commit `d6daba598ba382f6c213deb12a598d60d3817b00`.

## 2. What is actually complete

### P2.1 narrow structural integration gate

Core report [REVIEW03_FINAL.md](../selector_v2/integration/REVIEW03_FINAL.md) and [final-gate.json](../selector_v2/integration/final-gate.json), at core head `c5e7e17`, report:

- Gate status `VERIFIED`, blockers empty; operational status remains `INCOMPLETE`.
- Tested core predecessor `796a83a5f8f69c4dc7c0db619e1cdb130ddc0b33`; authoritative RegisteredLedger implementation unchanged from `4e21dbf0d06c030681e774cb15f1a5cf0c802f0d`.
- Interface `0eb1050ad103bad2f93d3b9feb732bf94184f2a2`, which delegates to the exact core RegisteredLedger; no parallel production ledger.
- Independent proof executable pin `83762437ba05e1def9dde5edff8c7d44878f4269`; proof sign-off/docs `e8895a344821f7cd463823774e6bc591e064264c`.
- Normal mode: 40/40 tests; optimized `python -O`: 28/28.
- Four actual journal/2 artifacts independently replayed as VERIFIED in both modes.
- 31 counted outer/delegated mutation cases rejected per mode.
- Five resource caps return INCOMPLETE/no proof; false EXHAUSTED is INVALID; PARTIAL closure remains INCOMPLETE.
- Artifacts preserve operational status INCOMPLETE. No external service was called.

This closes the specified structural/reference integration gate for the tested pins. It does **not** establish live external acceptance, production readiness, bounded optimization, durable persistence, or clean CI. Git DNS blocked clean worktree checkout; tests used byte-verified source snapshots.

### Interface delegation

The current interface API `research/interface/p2/gateway.py:open_gateway()` returns the actual core `RegisteredLedger` journal/2 instance. It does not maintain a competing ledger or dual-write. Interface final handoff is `research/interface/p2/REVIEW03_FINAL.md` at `ae04a28`. Historical SharedGateway/RegisteredLedger paths remain regression/reference code, not a second production authority.

### Proof hardening after the successful combined gate

The proof agent subsequently hardened exact deletion replay to avoid unbounded full-word/remainder materialization. Latest proof branch head is `cf5a007571853b6cdf6259fa2a9a95f5c1e351f8`. Exact current Git blob IDs:

- `bounded_deletion.py`: `e1fc61b6f03484d4428642ca157e2dac43f0572d`
- `test_bounded_deletion.py`: `6de549b9b4d208be99a419c88fd903a1ce1a6dcc`

Its exact-blob local tests passed 6/6 normal and 6/6 optimized. Coverage: 4,374 corpus-owner cases, 13,122 forced 0/2/64-bit filter checks, 500 randomized collision cases, duplicate-positive index cap, all budget caps, and a synthetic 20,000-symbol trace (20,001 index entries, two exact comparisons, 200,010 work units). Process test-harness RSS was 109,708 KiB normal / 109,580 KiB optimized. See [bounded-deletion-test-output.txt](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/cf5a007571853b6cdf6259fa2a9a95f5c1e351f8/research/audit/bounded-deletion-test-output.txt).

**Important stale-pin issue:** core's current `run_final_gate.py` at `c5e7e17` still expects the earlier proof blobs `64eda7d13b3153175f09b70e41be66e1615846b2` and `2f59257d0ff3396417c2cedf9845f61e2fd20928`, and proof head `8376243...`. It has not yet been rerun against the hardened blobs `e1fc61b...` and `6de549b...`. The previous gate result remains valid for its exact old pins; do not misrepresent it as covering the later proof change.

## 3. Benchmark state and exact unresolved work

[Benchmark REVIEW03.md](https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/52d21e672b0ae6420cf677ff09c01bb2a3fd6b05/benchmarks/v2/REVIEW03.md) records:

- On the original 33 planted inputs, P1 sparse analysis obtained 29 independently verified structural optima and four verified lower bounds only. The four unresolved inputs are `huge_choice_active`, `medium_choice`, `small_choice`, `tiny_choice`.
- Three pinned P3 fixtures are HDFS, HDFS holdout and `cover_path_8`. P3 input-only fixtures and separate evaluation/reference manifest are prepared. Search must consume only input JSON; never expose planted reference costs, labels, or evaluation index to the solver.
- With the **previous** official bounded checker at 30 s / 1536 MiB, `huge_choice_active` replay verified mandatory floor 1 but no optimum; `huge_long_active` verified structural optimum 10,000. Both were INCOMPLETE at 512 MiB. Those large-case results do not cover the latest hardened checker blobs.
- Latest proof comment explicitly requests re-running the exact hardened proof branch against the actual `huge_choice_active` and `huge_long_active` journals, 30 s / 1536 MiB, normal and optimized, reporting raw closure and full outer journal replay separately, with exact input hashes, source blobs, work/entries/exact-check telemetry, time/RSS, and VERIFIED/INVALID/INCOMPLETE.

Do not call an old prototype filter result an official proof replay. Do not infer a lower bound from MemoryError or timeout.

## 4. Immediate next actions — finish the pin update, then begin P3

### Agent 01 — Core / integration owner

1. Continue on `research/v2-implementation-core`.
2. Update `selector_v2/integration/run_final_gate.py` to pin the latest proof branch `cf5a007571853b6cdf6259fa2a9a95f5c1e351f8` and replace the two stale PROOF blob IDs with `e1fc61b6f03484d4428642ca157e2dac43f0572d` and `6de549b9b4d208be99a419c88fd903a1ce1a6dcc`. Preserve all other verified pins unless a real source change requires updating them.
3. Rerun the full final combined gate in normal and `python -O` modes using exact pinned core/interface/proof source snapshots and fresh output directories. Publish machine-readable gate result, full logs, source blob identities, artifact hashes and limitations.
4. Keep fail-closed semantics. INVALID or INCOMPLETE must never yield a proof result or authorize pruning. Do not change journal schema/2 without a demonstrated defect.
5. Do not merge or modify the external learner/baseline.

### Agent 02 — Independent proof owner

1. Continue on `research/v2-proof-audit`; latest branch head `cf5a007...`.
2. Preserve verifier independence: no producer validation, adapter validation, or core `audit_journal.py` imports in the proof kernel.
3. Review the core runner's updated pins and combined result independently. Confirm the exact hardened checker is the one executed.
4. Coordinate with benchmark agent on actual huge-case bounded replay. Keep VERIFIED (all supplied evidence valid) distinct from FIXPOINT/LABEL_CONFLICT (closed structural proof); PARTIAL/OPEN or resource censoring must remain INCOMPLETE for closure.
5. Further proof work should prepare the independent P3 region/frontier certificate contract and exhaustive small RGS oracle, not implement producer pruning before the core P3 design is reviewed.

### Agent 03 — Benchmark owner

1. Continue on `research/v2-benchmarks`; latest head `52d21e6...`.
2. Run the exact proof-branch bounded checker blobs `e1fc61b...` / `6de549b...` on the actual recovered `huge_choice_active` and `huge_long_active` cases. Run normal and optimized modes at 30 s / 1536 MiB; also report 512 MiB fail-closed runs if feasible.
3. Separate raw closure/producer phase from full outer journal/2 verification. Report input SHA-256, raw journal SHA-256, exact core/proof source Git blobs, budgets, work, peak entries, exact checks, elapsed time, process RSS and final status. Do not mix prior prototype filters, old proof pin, or literal control with official verifier results.
4. Preserve existing planted input-only and evaluation/reference separation. Prepare P3 fixture manifests and reproducible commands; do not run solver with reference costs.
5. Independently rerun current core/interface/proof suites after the repin.

### Agent 04 — Interface owner

1. Continue on `research/v2-interface-audit`; latest head `ae04a28...`.
2. Preserve `open_gateway()` delegation to core `RegisteredLedger` / journal/2. No competing state, schema fork, or dual-write.
3. Prepare the P3 adapter/search boundary contract: submit only complete partitions over the original alphabet, preserve ordered original IDs, bind sample/scope/partition identity, distinguish PROJECTION_NO / BOUNDED_NO / ACCEPT / UNKNOWN, and keep every unauthenticated/mock outcome operationally INCOMPLETE.
4. Add selector-side contract tests only. Do not call or modify the external learner; do not claim live transport/authentication.

### After the repinned combined gate passes — P3 EDR-BB structural exact search

P3 is the next algorithmic milestone, and only the unrestricted structural/reference path is authorized initially. Use the research design in `PROJECT_HANDOFF.md` §R03 and `research/2026-11-24/03_EXACT_SEARCH(2).md`.

- A node is `R(E,D)`: complete partitions coarsening equality partition E and satisfying branch-local disequality pairs D. Root E is the independently verified mandatory quotient.
- Derive only necessary conflict disjunctions from sound same-negative dead-cover, disjoint deletion support, complete alternatives, or independently proved rank constraints.
- For ordered alternatives `e1...et`, child j forces ej equal and earlier alternatives unequal. Prove children are pairwise disjoint and cover every completion satisfying the conflict by the unique first true pair. Keep residual regions unless independently proved infeasible.
- Use rollback symbol DSU, lazy child generation and a restartable frontier/cursor. Branch-local disequalities must not leak across rollback. Generic all-pair fallback after exact-only NO excludes only the exact representative E and covers every strict coarsening.
- Base cost is `n - |E|`; add only independently justified additional quotient-rank lower bounds. Never charge mandatory unions twice.
- No canonical-merge-parent pruning combined with conflict-only branching unless separately proved; known counterexample exists in the exact-search report.
- Policy stays B=0: no CDAQ probes, no heuristic pruning, no anonymous SAT/ML. Search proposes complete original-alphabet partitions only.
- Build a literal/RGS exhaustive oracle for small alphabets. Compare every optimum and all region coverage against the oracle; test adversarial duplicate/empty/unused symbols, negative interactions, branch rollback, restart/resume, time/resource caps, UNKNOWN, and proof mutations.
- Independent verifier consumes the serialized region/frontier proof and original raw sample, never producer caches. Strict-improvement cutoff for one optimum; use strict `>` if enumerating all optima.
- Resource limits yield INCOMPLETE with preserved frontier. No unproved pruning, no operational ACCEPT claim, no bounded optimization claim.

P4 AEFC, P5 advanced/rational rank bounds, and P6 CDAQ are later isolated ablations after a stable P3 frontier and proof contract. P7 is controlled paired benchmark/ablation.

## 5. Operational and repository boundaries

The external learner/evaluator remains an immutable BLACK BOX. No endpoint calls, hidden-state inspection, code edits, or redesign. The paper specifies semantics but not the actual RPC/wire protocol. Owner-confirmed transport/authentication, cryptographic receipt trust, capacity policy, durable crash recovery, clean network-enabled CI, and scale behavior remain separate gates. Current status is operational `INCOMPLETE`.

Keep PRs #6–#9 open/Draft until a separate review explicitly authorizes integration. Commit/push each validated milestone on the existing assigned branch with exact commands, pinned source hashes, raw outputs, measured time/RSS, and limitations. Do not report an Agent as run from GitHub issue text; verify branch commits. Do not use memory summaries in place of source files.

## 6. New-chat startup checklist

Every replacement chat must:
1. Select GPT-6.2 with High thinking effort manually.
2. Join the existing Passive learning research Project.
3. Read this file, `PROJECT_HANDOFF.md`, `SELECTOR_V2_INDEX.md`, `INTEGRATION_REVIEW_03.md`, Issue #10 latest comments, and its assigned stream report.
4. Verify the current branch head before editing; preserve the exact branch above.
5. Execute the assigned task, not just write a plan; push tested milestones and record blockers.
6. Never merge, modify the external learner, or claim operational acceptance.
