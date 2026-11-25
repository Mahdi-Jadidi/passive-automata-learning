# Next-session handoff 06 — P3 M1 audited, M2 gates frozen

Date: 2026-11-25. Read this file and INTEGRATION_REVIEW_06.md first. GitHub is authoritative. P2.1 is closed; P3 exact search is not yet implemented.

## Current disposition
- P2.1 hardened narrow structural gate: VERIFIED at GitHub Actions run 45562082178.
- Operational acceptance: INCOMPLETE. No live learner calls, no external receipt authority, no deployment.
- P3 M1 subcomponents: core region algebra PASS; RGS oracle PASS; interface boundary readiness PASS; benchmark harness PASS with fake adapters only.
- P3 independent frontier verifier: BLOCKED; latest CI failed.
- P3 producer full search/serializer: NOT IMPLEMENTED.
- Actual producer certificate replay and native P3 benchmarks: NOT RUN.
- P3 structural exact search B=0 remains authorized, but do not claim completion.

## Latest branches
| Agent | Branch | HEAD | PR |
|---|---|---|---|
| Core #2 | research/v2-implementation-core | fa12fdcca0a8d7a9a697bb617ed09453cb56c3d5 | #7 |
| Proof #3 | research/v2-proof-audit | 4c4543775b7e2700ad0505da49023e24b2e5e9ab | #8 |
| Benchmark #4 | research/v2-benchmarks | d9f49cd4b459103bebbecb8b6ba16d3b43193d83 | #9 |
| Interface #5 | research/v2-interface-audit | 98bc69dcc013d28a74e2035fd417dbe66ba74e00 | #6 |

All PRs are OPEN/DRAFT/UNMERGED. They are diverged from current integration base: core 19 ahead/13 behind, proof 57 ahead/11 behind, benchmark 49 ahead/13 behind, interface 15 ahead/13 behind. Do not merge or force-push; reconcile histories after M2 source stabilizes.

Integration branch: research/selector-v2 (read its live HEAD; this handoff and index are maintained there).
Authoritative contract: research/P3_SERIALIZATION_V1.md at 1cf4fb9fc935729b9ba021b3e26f791192b76578.
Lead audit: research/INTEGRATION_REVIEW_06.md at 8462a6a725e1ee4a7a1a7436a00a54b7d8911ee3.

## Actual CI evidence
- P2.1 hardened gate run 45562082178: 43/43 normal, 31/31 optimized; four actual journal/2 artifacts VERIFIED/FIXPOINT; 31 mutations rejected; five caps INCOMPLETE; false EXHAUSTED INVALID; PARTIAL INCOMPLETE.
- Core M1 run 45572670465: 9/9 normal and 9/9 -O; 21,195 literal first-true memberships, 157 ordered lists, 3,834 child and 1,413 residual records; exact source blobs checked.
- RGS oracle run 45563857327: normal/-O; Bell counts B(0..8), 7,065 region-membership checks.
- Interface readiness run 45565081120: 17/17 normal and 17/17 -O.
- Proof frontier run 45571609270: FAILED in normal mode due ModuleNotFoundError for selector_v2.schema; optimized skipped. Do not call this verifier PASS.

## Frozen v1 contract — mandatory
Read research/P3_SERIALIZATION_V1.md. It supersedes nested proof prototype and earlier drafts:
- Trusted scope binds selector-v2/1 scope, exact journal bytes, ordered alphabet/traces, positional IDs and replay-derived root_owner.
- No root_equalities pair closure (O(n²)).
- No producer schema import in verifier; canonical JSON independently implemented.
- Flat node table and iterative proof traversal, not recursive nested tree.
- ALL_PAIRS_LEX_V1 only for M2.
- FEASIBLE_MIN closes any nonempty region if E itself is structurally compatible; EXACT_NO only singleton.
- Base LB only; one-optimum >=U, all-optima >U.
- Resource caps checked inside loops; cap -> INCOMPLETE/no result.
- CROSS_SUPPORT is M3 only, after independent proof review.

## Agent responsibilities / next gate

### Core #2 (M2 producer)
On existing branch implement full DFS/branch-and-bound and flat serializer. Evaluate E literally. Close with EMPTY, RAW_LABEL_CONFLICT, FEASIBLE_MIN, singleton EXACT_NO or base-LB COST; otherwise first-true all-pairs split with explicit residual and suffix. Produce actual tiny_choice and small_choice certificates, one/all mode, normal/-O, deterministic repeat and restart equivalence. No advanced pruning. Coordinate exact output bytes with #3.

### Proof #3 (M2 verifier)
Fix failing CI: remove selector_v2 import, remove root_equalities, implement independent canonical JSON, flat iterative traversal, FEASIBLE_MIN, strict duplicate-key CLI, inside-loop work/time budgets and DeletionBudget. Pin Python 3.13.5. Add large-n linear scope test and exhaustive RGS/mutations. Replay exact tiny/small certificates from #2. Do not certify synthetic fixture alone.

### Benchmark #4
Keep seven raw-only fixtures and harness. Adapt to native producer/verifier CLI only after exact pins are published. Run tiny/small first, then remaining fixtures with 30s/1536 MiB and separate 512 MiB runs; repeat and checkpoint/resume. Solver/verifier phases separate. P2 original huge journal/2 artifacts remain NOT RUN until raw bytes are supplied; raw closure numbers are producer-only.

### Interface #5
Preserve open_gateway -> sole core RegisteredLedger. Add offline actual producer certificate -> proof verifier -> candidate registration test after #2/#3 CLI stabilizes. Proof certificate remains outside journal/2; candidate owner, sample/scope, request_id and attempt_id remain distinct. No external calls.

## Required M2 acceptance order
A. Proof verifier CI green normal/-O at Python 3.13.5, independent, flat, resource-bounded.
B. Core exact search produces complete tiny/small certificates.
C. Proof independently replays those exact producer bytes and matches literal RGS optimum/all-optima.
D. Interface offline integration passes.
E. Native benchmark harness records exact runs and limitations.

Do not merge PRs until A-C pass and lead review approves. No learner/baseline modification, live calls, bounded optimization, CDAQ, P4-P7 or operational acceptance.


## Final contract correction
The current authoritative `research/P3_SERIALIZATION_V1.md` is commit `ff61b1c56138c89fc0ad9a615f0b2a587b03393a`. It requires lazy `pair_at(j)` for all-pairs alternatives, `t=k*(k-1)//2`, prefix-only cursor logs, symbolic suffix and residual, flat node table, no per-node E/D copies, iterative proof replay. This supersedes any earlier description of full alternatives hashes/lists or per-node owner/D arrays. The verifier and producer must not materialize O(k²) alternatives.
