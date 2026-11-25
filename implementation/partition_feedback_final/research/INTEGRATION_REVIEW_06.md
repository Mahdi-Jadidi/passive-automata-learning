# Integration Review 06 — P3 M1 audit and M2 execution plan

Date: 2026-11-25. Integration lead audit of all four latest agent branches, committed code/reports, GitHub Actions, and original exact-search research. This supersedes prior "M1 complete" interpretations: M1 components are accepted, but P3 EDR-BB exact search is NOT YET IMPLEMENTED.

## 1. Executive disposition

| Gate | Status | Evidence |
|---|---|---|
| P2.1 hardened narrow structural gate | VERIFIED | Actions 45562082178; Review05 |
| P3 core M1 region algebra | PASS | Actions 45572670465, 9/9 normal and 9/9 -O |
| P3 RGS oracle | PASS | Actions 45563857327 |
| P3 interface boundary readiness | PASS | Actions 45565081120, 17/17 normal and 17/17 -O |
| P3 independent frontier verifier | BLOCKED | Actions 45571609270 FAILED |
| P3 producer serialization/full search | NOT IMPLEMENTED | Core M1 has only region/DSU/split/budget primitives |
| P3 producer -> independent verifier replay | NOT RUN | No native producer certificate |
| P3 integrated benchmark | NOT RUN | Harness used fake adapters only |
| Operational acceptance | INCOMPLETE | No live learner/evaluator evidence; no external calls |

P2.1 is not reopened. P3 is authorized structurally only, B=0, but M2 cannot pass until the proof verifier is corrected and an actual producer certificate is independently replayed.

## 2. Exact branch / PR state

- Core #2: branch research/v2-implementation-core, HEAD fa12fdcca0a8d7a9a697bb617ed09453cb56c3d5, PR #7 OPEN/DRAFT/UNMERGED.
- Proof #3: branch research/v2-proof-audit, HEAD 4c4543775b7e2700ad0505da49023e24b2e5e9ab, PR #8 OPEN/DRAFT/UNMERGED.
- Benchmark #4: branch research/v2-benchmarks, HEAD d9f49cd4b459103bebbecb8b6ba16d3b43193d83, PR #9 OPEN/DRAFT/UNMERGED.
- Interface #5: branch research/v2-interface-audit, HEAD 98bc69dcc013d28a74e2035fd417dbe66ba74e00, PR #6 OPEN/DRAFT/UNMERGED.
- Integration branch research/selector-v2 HEAD: 1cf4fb9fc935729b9ba021b3e26f791192b76578.

All four PR branches have diverged from current integration branch: core 19 ahead/13 behind; proof 57 ahead/11 behind; benchmark 49 ahead/13 behind; interface 15 ahead/13 behind. Do not merge yet. Rebase/merge-base reconciliation is a later controlled integration step after M2 commits stabilize; do not discard agent history or cherry-pick overlapping files blindly.

## 3. Core M1 independent audit

Core M1 source blobs:
- edr_bb.py: 657c4e0e4059b32cd9e6477e61c7a3673290f36d.
- test_edr_bb.py: b45a34b223b6d294373bd45b4f59c0059b5a983e.

The code implements canonical owner/region validation, branch-local disequalities, rollback DSU without path compression, deterministic union tie-break, first-true split construction, generic all-pairs fallback, base LB and SearchBudget tickets. I reviewed the mathematical state transitions:
- Region membership correctly requires candidate owner to coarsen E and respect D.
- A child adds equality for its selected pair and disequalities for every preceding alternative.
- The residual enforces all alternatives false.
- The all-pairs fallback covers every strict coarsening; residual is exactly E.
- LB n - number_of_E_classes is valid because every completion is a coarsening.
- One-optimum LB>=U and all-optima LB>U are the correct cutoffs.
- Rollback and budget ticket identity/release corrections are covered.

Actual clean CI run 45572670465 (Ubuntu 24.04 / CPython 3.13.5) verified exact source blobs, ran 9/9 tests normal and 9/9 optimized, and compiled selector sources in both modes. Each mode: 21,195 literal first-true membership checks, 157 ordered lists, 3,834 child records and 1,413 residual records. M1 is ACCEPTED.

Critical scope limitation: there is no DFS/search loop, structural candidate evaluator, flat serializer, restartable checkpoint, or certificate output. Thus no P3 optimum has been computed. The M1 CI does not constitute an exact-search gate.

## 4. Proof M1 audit and blockers

Proof branch adds:
- p3_frontier_verifier.py blob 50f2749bec56cf73eaa69d297bd6b88f2ca9dfa1.
- test_p3_frontier_verifier.py blob 43077d65cb4f24cd1f59856935e5a581d56bb301.
- P3 region contract and RGS oracle.

Actual RGS run 45563857327 passed normal/-O; Bell counts B(0..8)=1,1,2,5,15,52,203,877,4140; independent label enumeration through n=5; 7,065 region-membership checks.

The new frontier verifier is NOT accepted. Actions 45571609270 failed in normal mode before running tests: `ModuleNotFoundError: No module named selector_v2`. The proof PR merge checkout does not contain the separate core branch, and the verifier imports `selector_v2.schema.canonical`. The test also imports that producer module. This is an avoidable dependency and blocks independent CI.

Further correctness/scalability findings:
1. `root_equalities` serializes the complete pair closure of root_owner. One component of size m requires m(m-1)/2 pairs; this is O(n²) and can destroy the 100k-symbol objective. Root owner array plus independent journal replay is sufficient; remove pair closure.
2. The proof tree is recursively nested and the verifier recursively visits it. A long merge path can exceed JSON/Python recursion depth. M2 must use a flat node table and iterative verifier traversal.
3. Current EXACT_FEASIBLE only closes singleton regions. The mathematically stronger and sound `FEASIBLE_MIN` closure is required: if E itself is structurally compatible and R(E,D) is nonempty, E is the unique minimum-cost member, so the entire region closes.
4. Work/time checks are not consistently inside long projection loops; pass explicit DeletionBudget to journal replay and charge raw structural/projection work.
5. CLI currently parses with plain json.loads before duplicate-key rejecting parser; fix.
6. CI currently requests generic Python 3.13 rather than exact 3.13.5 and fails before optimized mode.

The lead froze the corrected flat v1 contract at:
`implementation/partition_feedback_final/research/P3_SERIALIZATION_V1.md`
commit 1cf4fb9fc935729b9ba021b3e26f791192b76578.
This contract is authoritative over the proof branch's nested prototype and prior draft.

## 5. Benchmark M1 audit

Benchmark #4 committed Review05 and P3 harness. Seven raw-only fixtures and exact SHA-256 manifest are recovered:
- tiny_choice (6 symbols, 2 positives, 2 negatives)
- small_choice (12, 4, 4)
- medium_choice (1,000, 1,000, 1,000)
- huge_choice_active (100,000, 10,000, 10,000)
- hdfs_1024 (29, 1,024, 1,024)
- hdfs_holdout_1024_uncapped (29, 1,024, 1,024)
- cover_path_8 (16, 8, 7)

Harness tests 9/9 normal and 9/9 optimized use fake adapters only. They validate process isolation, result envelopes, hashing, repeat/resume probes and metrics; they are not algorithm results.

P2 huge raw input recovery:
- huge_choice_active SHA256 0be60da81326bcd8974da1df07e018e60dcd62714123b884c873ed3be782beba.
- huge_long_active SHA256 0ed5834c91b82a00ec8be5ba27c7f36b12f47d0d5e39911cf05fe6a5ce6f3e0c.

Producer raw closure only (old core pin 796a83a; not hardened checker):
- huge_choice_active reached producer rule-class FIXPOINT at 1536 and 512 MiB in both modes; producer raw structural check false.
- huge_long_active reached producer rule-class FIXPOINT at 1536 MiB; producer raw structural check true. At 512 MiB, producer raw-closure processes raised MEMORY_ERROR.
- These are not hardened proof replay, not independent journal replay, not P3 solver outcomes.

Original huge journal/2 bytes are still unavailable. Expected historical SHA identifiers are huge_choice dfbc8c72bdecb316fe72dafdb8130b97887c8e7b81cc129bd41eb2eab63463d5 and huge_long 779cc7dd5f9198f5e4a5f1460e3ef2f869a2c45e509e0b41daaae016bf8ac3fe, but hashes are not bytes. Ledger ingestion and hardened full replay remain NOT RUN. Do not classify them as verifier failures.

## 6. Interface M1 audit

Interface P3 contract and gateway tests pass 17/17 normal and 17/17 optimized (Actions 45565081120). open_gateway still delegates to the single authoritative core RegisteredLedger/journal/2. Canonical owner arrays, original positional IDs, scope binding and UNKNOWN semantics are covered. No second ledger or schema fork.

No actual producer certificate has been passed through the independent verifier. Interface integration remains NOT RUN pending #2/#3 native CLI and exact certificate.

## 7. Frozen P3 v1 contract and M2 acceptance

Read the authoritative contract before code:
`research/P3_SERIALIZATION_V1.md` at integration commit 1cf4fb9.

Key choices:
- Trusted scope binds exact selector-v2/1 unrestricted scope, exact journal bytes, ordered alphabet/traces, positional trace IDs and replay-derived root_owner.
- No O(n²) root_equalities.
- Flat node table, iterative proof replay.
- ALL_PAIRS_LEX_V1 first-true split with explicit residual and lazy suffix/cursor log.
- FEASIBLE_MIN closes a whole nonempty region when E is compatible.
- EXACT_NO only singleton; EMPTY; RAW_LABEL_CONFLICT; COST; OPEN/UNKNOWN incomplete.
- Only base equality-class LB. One-optimum >=U; all-optima >U.
- Explicit resource budgets; operational status always INCOMPLETE.
- CROSS_SUPPORT_LEX_V1 is M3 only, after M2 verifier approval.

### M2 Gate A — independent verifier
Must have green CI normal/-O at Python 3.13.5, no selector_v2 import, no quadratic root closure, flat iterative traversal, FEASIBLE_MIN, strict parsing and inside-loop budgets. Exhaustive RGS n<=8 plus corruption mutations and large-n linear root binding.

### M2 Gate B — producer exact search
Core must implement the full solver loop and flat serializer. Produce complete certificates for tiny_choice and small_choice, in one/all mode, normal/-O, repeated deterministically. No unproved pruning. Checkpoint/resume must preserve exact frontier suffix and node identity.

### M2 Gate C — independent actual certificate replay
Agent #3 must verify the exact producer-generated tiny/small certificate bytes from #2, not synthetic hand-built proof fixtures. Both modes and normal/-O. Any mismatch is INVALID or a documented blocker; no claim of search completion.

### M2 Gate D — interface integration
Offline producer -> certificate verifier -> open_gateway boundary. Proof artifact remains outside journal/2; candidate registration and request/attempt identities remain separate. No live transport.

### M2 Gate E — native benchmark
Agent #4 maps native producer/verifier CLI into existing harness after exact source pins. Run seven raw-only fixtures, fresh repeats, resume equivalence, 30s/1536MiB and separate 512MiB; solver and verifier measurements distinct. No fake adapter as algorithm result.

## 8. Control decisions

- P2.1 remains VERIFIED; operational INCOMPLETE.
- P3 M1 algebra and readiness artifacts are accepted as subcomponents only.
- P3 exact search, independent certificate, and integration remain NOT IMPLEMENTED / NOT RUN.
- No PR merge until M2 Gate A-C pass and integration branch reconciliation is planned.
- Branches are diverged from current integration base; preserve histories and reconcile only after M2 source stabilizes.
- No external learner or baseline edits, no live calls, no bounded optimization/CDAQ/P4-P7, no operational acceptance.


## 9. Final v1 contract refinement (supersedes earlier wording above)

The authoritative contract is now updated at integration commit `3411794ec013e5f7929d3e23960e80632a3e40c5`. The all-pairs alternative family is lazy/symbolic: `t=k*(k-1)//2`, `pair_at(j)` derives each emitted pair, `cursor_log` records only emitted prefix, suffix is `[cursor,t)`, and residual is an explicit symbolic all-false marker. Certificates have a flat node table with no per-node owner or full D arrays; the verifier reconstructs state iteratively from root and path. This prevents O(k²) alternative materialization/hash and O(n*nodes) repeated state storage. Earlier nested/per-node-state drafts and the prior flat-but-materialized draft are superseded. The proof verifier and core producer must follow this latest contract exactly.
