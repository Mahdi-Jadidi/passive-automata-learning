# Next-session handoff 05 — P2.1 closed, P3 authorized

Date: 2026-11-25. Read this file and INTEGRATION_REVIEW_05.md before any work. GitHub issues/branches are authoritative. Repository baseline and black-box boundary are unchanged.

## Current decision

- Post-hardening P2.1 narrow structural journal/2 gate: **VERIFIED**.
- Operational status: **INCOMPLETE**. No external ACCEPT, live receipt authority, deployment or operational acceptance.
- P3 EDR-BB: **AUTHORIZED for unrestricted structural exact search only, B=0**.
- No merge. PRs #6–#9 remain open/draft/unmerged.
- Never modify the external learner, evaluator or baseline. No live external calls.

Parent coordination: issue #11, https://github.com/Mahdi-Jadidi/passive-automata-learning/issues/11.
Integration review: INTEGRATION_REVIEW_05.md at commit 53da42edb57cdfd970a475d2d71f750ebd0fcbbc.

## Four current branch heads

| Stream | Branch | Current head | PR |
|---|---|---|---|
| Core | research/v2-implementation-core | 3c5b8f42f1a268505acec3a2e871a08c6e51b22c | #7 |
| Proof | research/v2-proof-audit | 7ac2314d0b8f49cbe4a315ce2d3d6ba4349b1044 | #8 |
| Benchmark | research/v2-benchmarks | 635bc6cc182f2215d6cd354b894c8a0eb6a831a0 | #9 |
| Interface | research/v2-interface-audit | a1516fc0572d8f520422e517adeb2d1db6482f29 | #6 |

Integration branch research/selector-v2 includes Review05 and this handoff. Do not merge PRs or change the external learner.

## Exact P2.1 gate evidence

GitHub Actions run 45562082178 succeeded on Ubuntu 24.04 / Python 3.13.5. Exact run checkout and dependency pins:
- Core checkout a218ef37f4ad255ec5a9dde6e5a2cc650ceec4a3; core source pin 796a83a5f8f69c4dc7c0db619e1cdb130ddc0b33.
- Interface pin 0eb1050ad103bad2f93d3b9feb732bf94184f2a2.
- Proof pin cf5a007571853b6cdf6259fa2a9a95f5c1e351f8.
- Runner blob 82b84b544894bd344436511a3778a26995bb6523.
- Hardened checker/test blobs e1fc61b6f03484d4428642ca157e2dac43f0572d / 6de549b9b4d208be99a419c88fd903a1ce1a6dcc.

Normal combined 40/40 plus boundary 3/3 = 43/43. Optimized combined 28/28 plus boundary 3/3 = 31/31. Four actual journal/2 artifacts VERIFIED/FIXPOINT, structural costs 2/2/1/2. 24 outer + 7 delegated mutations rejected. Five caps INCOMPLETE per mode; false EXHAUSTED INVALID; PARTIAL INCOMPLETE. All exact artifact hashes and normal/-O parity match. Total elapsed 15.34s; observed max RSS 147252 KiB. Gate JSON status VERIFIED, blockers empty, operational_status INCOMPLETE. Outputs at core commit d578044a9ac91806d792b5e6cca7d65b86bd9370. Do not use historical c5e7e17 results as proof of hardened pin; this new run supersedes them for the narrow gate.

Independent lead review checked the verifier import graph and actual logs. Proof modules are separate from producer, adapter and core audit_journal; no shadow copies exist in earlier core/interface PYTHONPATH roots. Published replay validates exact compressed Git blobs, decompressed SHA-256, raw sample/scope/journal, deletion obligations, FIXPOINT and structural result. Review details are in INTEGRATION_REVIEW_05.md.

## P3 preparation CI

- Interface boundary CI run 45563718490 succeeded: 17/17 normal and 17/17 optimized (nine P3 contract methods + eight existing gateway tests). Workflow was added in interface branch commit a1516fc.
- Independent RGS oracle CI run 45563857327 succeeded: normal and -O; Bell counts 0..8, label enumeration 0..5, 7065 region membership checks. Workflow was added in proof branch commit 7ac2314.
- RGS oracle blob 375c36bfb2602894ce783055d1edf31f265aafa0. Interface P3 contract test blob 063cc799ec32a637881e55cbee73b7dba09cd3c5.

## P3 exact-search rules

Search complete partitions of the original ordered alphabet A, including unused symbols. Structural compatibility:
C(P) iff for every negative y there exists block B in P such that for every positive x, pi_B(y) != pi_B(x). Objective c(P)=n-|P|.

Region R(E,D): E is equality equivalence over original IDs; D is branch-local disequality. Root E0 is reconstructed from independently verified journal/2 evidence, not producer counters.

For complete ordered alternatives L=(e1,...,et), first-true child j adds equality e_j and disequalities e_1..e_(j-1); residual retains all e_i disequal. Prove disjointness and full coverage. Preserve residual; eliminate only with an independently verified necessary disjunction. Generic fallback uses all unordered pairs of distinct E-classes. No canonical merge-parent restriction, symmetry pruning or omitted alternatives.

Use rollback DSU without path compression (or an independently replayable equivalent), branch-local D, and canonical original IDs. Initial lower bound n - number of E-classes; do not double-count mandatory unions. One-optimum prune at LB>=U; all-optima only LB>U. No rank/AEFC/advanced dead-cover pruning yet.

Complete candidate output is the canonical length-n owner array: owner[i] is the minimum original member of its block, owner[i]<=i and owner[owner[i]]==owner[i]. RGS and DSU labels are internal only.

UNKNOWN remains pending. BOUNDED_NO cannot prune unrestricted regions. Mock ACCEPT is not an incumbent without an independently checked structural witness. Resource/time/work/entry caps, OPEN nodes, ungenerated suffix, missing chunks or UNKNOWN yield INCOMPLETE/no result. Invalid evidence is INVALID. VERIFIED only after complete independent frontier coverage plus valid incumbent or full infeasibility proof.

## Agent responsibilities

- #2 Core: implement deterministic structural producer, rollback region state, complete first-true branching, generic fallback, base cost bound, residual handling and restartable frontier. Add explicit work/entry/time caps. No unproved pruning.
- #3 Proof: implement independent serialized region/frontier checker; no producer, DSU, cache, ranking or pruning imports. Verify parent-child E/D transformations, alternatives, residual, lazy cursor suffix, incumbents, cutoff, scope and status. Exhaustive RGS/literal comparisons and corruption tests in both modes. Review every new proof rule before enabling it.
- #4 Benchmark: maintain seven raw-only fixture manifest and harness; never expose evaluation references/planted costs to solver. Hardened large-case replay remains NOT RUN, not INCOMPLETE: raw inputs/journals are not available to runtime. Project Library materialization of review03-benchmark-evidence.zip and p3-exact-search-inputs.zip was denied. Ask user for direct raw upload when large-case replay is required; no synthetic substitute and no old-checker result transfer.
- #5 Interface: preserve authoritative core RegisteredLedger journal/2, canonical owner/ID/scope boundary and pending semantics. Selector integration only after #2/#3 agree on contract. No competing ledger, dual-write, schema fork or live calls.

Each milestone must be committed/pushed with exact Git blobs, commands, logs, work/entry/exact-check counters, caps, and VERIFIED/INVALID/INCOMPLETE or NOT RUN semantics. Keep all PRs draft/unmerged pending review. No bounded optimization, CDAQ, P4-P7, learner changes or operational acceptance.
