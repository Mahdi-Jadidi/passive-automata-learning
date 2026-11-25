# Selector v2 — research and implementation index

Baseline: 7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6 (codex/v47-polynomial-teacher).
Integration branch: research/selector-v2. Do not modify the external automata learner or the baseline.

## Archived research
- [Master handoff](PROJECT_HANDOFF.md)
- [01 Sparse analysis / SDJ-IDA](research/2026-11-24/01_SPARSE_ANALYZE.md)
- [02 NO implication / AEFC](research/2026-11-24/02_NO_IMPLICATION.md)
- [03 Exact search / EDR-BB](research/2026-11-24/03_EXACT_SEARCH.md)
- [04 Query policy / CDAQ](research/2026-11-24/04_QUERY_POLICY.md)
- [AEFC reference validation](research/2026-11-24/no_implication_validation.py)
- [AEFC validation output](research/2026-11-24/no_implication_validation_run.txt)

## Parallel workstreams
| Issue | Branch | Dependency |
|---|---|---|
| #2 | research/v2-implementation-core | Starts immediately; P0/P1 |
| #3 | research/v2-proof-audit | Theory audit independently; verifier integration after schema freeze |
| #4 | research/v2-benchmarks | Baseline harness independently; v2 benchmarking after integration |
| #5 | research/v2-interface-audit | Paper/interface audit independently; live adapter requires confirmed protocol |

Agent instructions are in the issues. Requested model GPT-6.2 High must be selected in the execution UI; issue creation does not launch agents. Each stream commits after each testable milestone and opens a draft PR to the integration branch. No direct main writes or automatic merges.

## Integration order
Core/schema + interface contract -> typed evidence and basic exact search -> independent replay -> AEFC and rank bounds -> guarded CDAQ -> controlled ablations.
Keep structural and external acceptance distinct, preserve UNKNOWN, and report both cost bounds and independent verification. No publication novelty or external speedup is established yet.

## Status (2026-11-24)
Four research reports and the master handoff archived. Four parallel workstreams prepared; agent execution not initiated by GitHub. Raw benchmark archives and live external protocol still need availability confirmation.


## Status (2026-11-25 — next-session handoff)
- [Next-session handoff 04](NEXT_SESSION_HANDOFF_04.md) is the current continuity source for replacement chats.
- Narrow P2.1 structural journal/2 gate passed at core checkpoint c5e7e17 against proof pin 8376243 and interface pin 0eb1050. Operational status remains INCOMPLETE.
- Proof branch subsequently hardened bounded deletion replay: latest branch cf5a007, source blobs e1fc61b / 6de549b. Core combined runner still pins the older proof blobs; repin and rerun normal/-O before starting P3 implementation.
- Benchmark #4 must execute the latest hardened checker on the actual huge_choice_active and huge_long_active inputs; prior 1536 MiB large-case results used the previous proof pin.
- All four PRs #6–#9 remain open/Draft; do not merge. External learner and baseline remain immutable.


## Status (2026-11-25 — P2.1 post-hardening closure / P3 authorization)
- [Integration review 05](research/INTEGRATION_REVIEW_05.md) and [Next-session handoff 05](NEXT_SESSION_HANDOFF_05.md) supersede the earlier pending-gate status in handoff 04.
- P2.1 narrow structural journal/2 gate is VERIFIED at proof pin cf5a007 with hardened checker/test blobs e1fc61b / 6de549b. GitHub Actions run 45562082178: 43/43 normal, 31/31 optimized, four actual artifacts VERIFIED/FIXPOINT, 31 mutations rejected, five caps INCOMPLETE, false EXHAUSTED INVALID and PARTIAL INCOMPLETE. Operational status remains INCOMPLETE.
- Independent lead review of actual proof imports, source hashes, exact artifact replay and logs passed for the reference/simulator structural path.
- P3 EDR-BB unrestricted structural exact search is AUTHORIZED, B=0, under [issue #11](https://github.com/Mahdi-Jadidi/passive-automata-learning/issues/11). Scope and agent assignments are frozen in issue #11 and Review05.
- P3 preparation CI: interface contract 17/17 normal and optimized (run 45563718490); independent RGS oracle normal/-O (run 45563857327).
- All four agent PRs #6–#9 remain open/draft/unmerged. Benchmark hardened huge_choice_active/huge_long_active raw and full journal replay remain NOT RUN because original raw bytes could not be materialized; this is not a failure or inferred memory censoring. See benchmarks/v2/REVIEW04_HARDENED_UNIT.md.
- External learner/baseline unchanged; no live calls, merge, bounded optimization, CDAQ or operational acceptance.


## Status (2026-11-25 — P3 M1 audited, M2 in progress)
- [Next-session handoff 06](NEXT_SESSION_HANDOFF_06.md) and [Integration Review 06](research/INTEGRATION_REVIEW_06.md) supersede earlier P3 readiness-only status.
- P3 M1 core region algebra: PASS (CI 45572670465, 9/9 normal and -O; 21,195 literal first-true membership checks). This is not a complete search.
- RGS oracle: PASS (CI 45563857327). Interface boundary readiness: PASS (CI 45565081120, 17/17 normal and -O).
- Independent frontier verifier commit 4c45437 is BLOCKED: CI 45571609270 failed because of selector_v2.schema import. Its O(n²) root_equalities and recursive tree must be replaced by linear root_owner binding and flat iterative node table.
- Core branch still has no DFS/search loop or serialized frontier; no producer certificate exists. Benchmark harness 9/9 uses fake adapters; no native P3 result.
- Seven raw-only fixtures recovered. P2 huge raw closure only: huge_long 512MiB producer MemoryError; original journal/2 bytes unavailable, so hardened ledger/full replay remains NOT RUN.
- [P3 serialization v1](research/P3_SERIALIZATION_V1.md) is frozen at integration commit 1cf4fb9fc935729b9ba021b3e26f791192b76578. It requires flat node table, independent canonicalizer, no quadratic root_equalities, FEASIBLE_MIN region closure, ALL_PAIRS_LEX_V1, explicit suffix/residual and inside-loop resource caps.
- M2 acceptance sequence: verifier CI -> core tiny/small complete certificates -> independent replay of actual bytes -> offline interface integration -> native benchmarks. All PRs #6–#9 remain OPEN/DRAFT/UNMERGED; branches diverged from integration base and must not be merged until rebase/reconciliation.
- P2.1 remains VERIFIED, operational status INCOMPLETE. No external calls, learner/baseline changes, bounded optimization, CDAQ, P4-P7 or operational acceptance.


### P3 v1 contract final refinement
- Latest authoritative contract commit: 3411794ec013e5f7929d3e23960e80632a3e40c5.
- All-pairs alternatives are lazy/symbolic (t=k*(k-1)//2, direct pair_at(j), emitted-prefix cursor log, suffix [cursor,t), symbolic residual). No O(k²) alternative list/hash.
- Flat certificate has no per-node owner/D copies; verifier reconstructs state iteratively from root and path. No recursive JSON tree or O(n*nodes) repeated arrays.
- This supersedes previous P3_SERIALIZATION_V1 drafts. Producer and verifier must follow the latest commit.
