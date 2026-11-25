# Integration review 05 — P2.1 post-hardening closure and P3 authorization

Date: 2026-11-25. Authority: GitHub branches/commits, exact source blobs, committed test logs and GitHub Actions runs. This review supersedes the P2.1 status in REVIEW04 where it said the repinned gate or interface/oracle tests were still pending.

## 1. Final P2.1 disposition

**Narrow structural P2.1 gate: VERIFIED. Operational status: INCOMPLETE.**

Actual clean GitHub Actions run 45562082178, success, Ubuntu 24.04, CPython 3.13.5, checkout core a218ef37f4ad255ec5a9dde6e5a2cc650ceec4a3. Exact dependencies:
- Core: 796a83a5f8f69c4dc7c0db619e1cdb130ddc0b33
- Interface: 0eb1050ad103bad2f93d3b9feb732bf94184f2a2
- Proof: cf5a007571853b6cdf6259fa2a9a95f5c1e351f8
- Runner blob: 82b84b544894bd344436511a3778a26995bb6523
- Hardened checker/test blobs: e1fc61b6f03484d4428642ca157e2dac43f0572d / 6de549b9b4d208be99a419c88fd903a1ce1a6dcc

Machine result gate.json blob a289adef85a316961caf3f582582480ea8f9d888: status VERIFIED, blockers [], operational_status INCOMPLETE. All ten subprocess checks exit 0.

Actual normal combined 40/40 in 12.480s plus boundary 3/3 in 0.088s = 43/43. Optimized combined 28/28 in 0.796s plus boundary 3/3 in 0.085s = 31/31. Four actual published journal/2 artifacts VERIFIED/FIXPOINT in both modes, with unchanged SHA-256 and structural costs: roundtrip 2, adversarial 2, interface-journal2 1, interface-journal2-epochs 2. 24 outer plus 7 delegated mutation cases rejected; five caps INCOMPLETE per mode; false EXHAUSTED INVALID; actual PARTIAL INCOMPLETE. Normal/-O outputs agree. Total elapsed 15.34s, observed max RSS 147252 KiB (not an enforced RSS cap). Exact logs, stdout, pins, hashes and JSON are committed under selector_v2/integration/repin-cf5a007 at output commit d578044a9ac91806d792b5e6cca7d65b86bd9370. Workflow URL: https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45562082178.

The previous c5e7e17 result remains historical for old proof pin 8376243. The new result explicitly covers the hardened proof pin cf5a007 and both new checker blobs.

## 2. Independent proof review by integration lead

Reviewed exact executed stdout, boundary logs, gate JSON, run workflow/job logs, runner source and proof source pins. The independent verifier path is separate from producer validation:
- journal_v2_replay.py imports independent_replay, production_replay, ledger_replay, interface_artifact_replay and bounded_deletion.
- interface_artifact_replay imports only proof-stream modules.
- No producer, adapter, core audit_journal.py or external learner imports occur in the proof replay path.
- Directory inventories at the exact core and interface pins contain no shadow copies of replay_published_j2.py, journal_v2_replay.py, independent_replay.py, production_replay.py, ledger_replay.py, interface_artifact_replay.py or bounded_deletion.py ahead of the pinned proof directory on PYTHONPATH.
- replay_published_j2.py checks the exact four compressed Git blob IDs and decompressed SHA-256 values, calls independent verify_journal with the actual raw sample/scope/journal bytes and DeletionBudget, and checks record counts, structural optimum, FIXPOINT and operational INCOMPLETE. Its actual interface-export mutations are required to return INVALID with no result.
- Core boundary logs independently show 4/4 actual artifact replays, 24 outer mutation rejections and five resource caps. The combined suite includes the seven delegated interface mutation cases and hardened deletion regression.

Independent proof review: **PASS for the narrow P2.1 reference/simulator structural path**. This does not mean live receipt authenticity or operational acceptance.

## 3. P3 preparation independently validated

Proof source:
- Region/frontier contract: research/audit/P3_REGION_COVERAGE_CONTRACT.md, blob 8a5cbeaf6cd3018ea6c077d71d6ab90376841934.
- Literal RGS oracle: tests/reference/rgs_oracle.py, blob 375c36bfb2602894ce783055d1edf31f265aafa0.
- Contract is preparation only; it is not a producer, wire schema or certificate validator.

RGS oracle CI run 45563857327 succeeded on exact proof branch commit 7ac2314d0b8f49cbe4a315ce2d3d6ba4349b1044, Python 3.13.5, normal and optimized. Both outputs: Bell counts 0..8, independent label enumeration 0..5, 7065 region-membership checks; structural examples, duplicate/empty/unused symbols, malformed token and cap checks passed.

Interface contract:
- P3_SEARCH_INTERFACE.md blob 6104ca0f958124b01ca181fc4d8d0d3f4a7d791f.
- test_p3_contract.py blob 063cc799ec32a637881e55cbee73b7dba09cd3c5.
- CI run 45563718490 succeeded on interface branch commit a1516fc0572d8f520422e517adeb2d1db6482f29, Python 3.13.5, 17/17 normal and 17/17 optimized (nine P3 contract methods plus eight existing gateway tests).

The reviewed contract preserves complete canonical owner arrays over the original ordered alphabet, including unused symbols; distinguishes structural candidate, scoped evaluation and request/attempt identities; keeps UNKNOWN pending; treats BOUNDED_NO as candidate/capacity-scoped only; and preserves the authoritative RegisteredLedger journal/2 without competing state. Test fixtures remain mock-only.

## 4. Benchmark limitation — explicit and not a gate failure

Benchmark commit 635bc6cc182f2215d6cd354b894c8a0eb6a831a0 / REVIEW04_HARDENED_UNIT.md reports exact hardened unit tests 6/6 normal and 6/6 optimized, with 4374 exhaustive cases, 13122 collision checks, 500 randomized cases and a 20k-symbol synthetic trace. The actual huge_choice_active and huge_long_active raw closure, full journal/2 replay and 512 MiB trials were **NOT RUN**, because original raw input and journal bytes were not available to that execution runtime. They must not be reported as INCOMPLETE or as a memory failure; they are NOT RUN/BLOCKED under the new checker pin. Old-checker Review03 numbers do not transfer. This scale rerun is parallel work, not a prerequisite for the structural-only P3 start. The Project Library raw-byte materialization attempt for review03-benchmark-evidence.zip and p3-exact-search-inputs.zip was independently retried and denied; files are not committed in Git.

## 5. Four branch / PR status

All four PRs remain open, draft and unmerged:
- Core #7: research/v2-implementation-core at 3c5b8f42f1a268505acec3a2e871a08c6e51b22c.
- Proof #8: research/v2-proof-audit at 7ac2314d0b8f49cbe4a315ce2d3d6ba4349b1044.
- Benchmark #9: research/v2-benchmarks at 635bc6cc182f2215d6cd354b894c8a0eb6a831a0.
- Interface #6: research/v2-interface-audit at a1516fc0572d8f520422e517adeb2d1db6482f29.

The added CI workflow files are validation-only. No learner/baseline changes, external calls, merges or deployment.

## 6. P3 authorization

**AUTHORIZED: P3 EDR-BB unrestricted structural exact search only, B=0.**

Allowed initial scope:
1. Root region R(E0,empty), with E0 reconstructed independently from the verified raw journal/2 evidence. E0 is not trusted from producer counters.
2. Region R(E,D): E is an equivalence relation over all original symbol IDs; D is branch-local disequality. Use rollback DSU (no path compression; union-by-size and canonical minimum original ID) or an independently replayable equivalent. Never leak D between siblings.
3. For ordered complete alternatives L=(e1,...,et), split into first-true children: child j adds equality e_j and disequalities e_1..e_(j-1); preserve residual R(E,D union L). Child/residual disjointness and full coverage are mandatory.
4. Residual may be eliminated only by a separately checked necessary disjunction. Generic safe fallback is every unordered pair of distinct E-classes. No canonical merge-parent restriction, symmetry pruning or omitted alternatives.
5. A sound primitive conflict disjunction may use one fixed negative and two disjoint nonempty supports S,T, each a union of E-classes, with separately verified positive witnesses whose deletion remainders equal the negative. Enumerate the complete cross-support pair family unless every omission is proved impossible.
6. Initial lower bound is n minus number of E-classes. No double-counting mandatory unions. One-optimum prune at LB >= U; all-optima prune only at LB > U. No rank/AEFC/advanced dead-cover pruning in this milestone.
7. Complete candidate output is the canonical length-n owner array on original ordered alphabet, including unused symbols. RGS and DSU labels are internal only.
8. UNKNOWN stays pending; BOUNDED_NO cannot prune unrestricted regions; mock ACCEPT is not an incumbent without independent structural witness.
9. Search status VERIFIED only after independently replayed complete frontier coverage and a valid incumbent or full infeasibility proof. Invalid evidence is INVALID; timeout, memory/work/entry cap, missing chunk, OPEN node or unresolved suffix is INCOMPLETE with no result.
10. Keep P2 journal/2 unchanged. No external learner/simulator modification or calls. No operational acceptance, bounded search, CDAQ, P4-P7 or performance claims.

## 7. P3 work split

- Core #2: deterministic structural producer, rollback region state, complete first-true split, generic fallback, residual handling, base cost bound, explicit work/entry/time caps and restartable frontier. Commit every milestone.
- Proof #3: independent serialized-region/frontier verifier and literal coverage checks; no producer imports, DSU reuse, cache reuse or producer pruning logic. Exhaustive RGS oracle for n<=8 and direct literal region comparisons for small cases; mutation and normal/-O tests. Review every proof rule before enabling it.
- Benchmark #4: keep seven raw-only fixture manifest and benchmark harness ready; do not expose evaluation references to the engine. Recover original input/journal bytes when user supplies them; rerun hardened huge cases separately. Missing bytes remain NOT RUN, not a substitute synthetic result.
- Interface #5: preserve canonical owner/ID/scope boundary and one authoritative RegisteredLedger; add only selector-side integration after the core/proof contract review. No live calls.

Every milestone requires pushed commit SHA, exact Git blobs, reproducible commands, logs, counters, caps and VERIFIED/INVALID/INCOMPLETE or NOT RUN semantics. PRs remain draft/unmerged pending integration review. P3 authorization is structural-only, not operational approval.
