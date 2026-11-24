# Passive Automata Learning — Project master handoff

**Version:** 1.0 | **Date:** 2026-11-24 | **Status:** research design complete enough to begin integration; production implementation and external validation pending.

This is the canonical continuity document for the project conversation **Implement Exact Partition Search** and its four follow-up research assignments. It is written in English to be reusable by coding and research agents. It distinguishes historical evidence, newly reproduced tests, and proposed work. It does not authorize changes to the external learner.

## 1. Identity, source of truth, and recovery

- Repository: https://github.com/Mahdi-Jadidi/passive-automata-learning
- Previous research branch (recovered conversation): `codex/v47-polynomial-teacher`; `main` also existed. Current branch heads were not re-audited.
- Previously supplied ref: `7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd` (39 characters). GitHub commit lookup in this session resolved it to **`7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6`**, title *Publish uncapped solver, scale evidence and research handoff*.
- Pinned path: `implementation/partition_feedback_final/`. [Pinned tree](https://github.com/Mahdi-Jadidi/passive-automata-learning/tree/7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6/implementation/partition_feedback_final).
- Main paper: *Passive Compositional Automata Learning from Global Logs*, `main (1).pdf` (31 pages). Model authority: §2, Lemma 1 / Eq. (5), Theorem 1, §5.1 and Fig. 2 / Eq. (23), §5.2, Appendix B. The Library paper was located and Lemma 1 and Theorem 1 checked; original PDF export into this archive was denied by the file service.
- Earlier research: `independent_partition_selection_report.md`; `Alphabet partition research report.md`. Earlier handoff archives: `research-reports-and-audit.zip`, `partition-scale-improved.zip` (numbered variants in reports), `partition-benchmark-lite.zip` (light package previously prepared for 50 MB uploads); two full planted benchmark parts were used in some assignments. Their exact raw bytes are not present in this recovery bundle. The lightweight archive is not equivalent to all raw benchmark inputs. Preserve them separately when available.
- Four current reports and Python validation are preserved byte-for-byte in the accompanying ZIP under `research/`, with hashes in `MANIFEST.sha256`. Report 03 mentions `03_reference_checks.py`, which was not included in the current five uploads; do not pretend its results have been rerun here. Report 01 contains a reference pilot in Appendix A; Report 04 contains a finite check in Appendix A.

## 2. Immutable research contract

The external automata learning/evaluation system is a BLACK BOX. The selector may read original ordered positive and negative traces, propose a complete alphabet partition, receive the documented verdict and feedback, independently verify mathematical facts, choose subsequent proposals, and certify the optimum. It must not redesign, replace, inspect hidden state/caches of, or modify the learner/evaluator. Do not submit block-only queries, fabricate witnesses, use planted reference labels as solver input, or label a timeout as NO.

For declared alphabet Σ, n = |Σ|, ordered indexed positives X and negatives Y, projection π_B erases only symbols outside B, preserving repetitions and order. Every proposed P is a disjoint collection of nonempty blocks covering **all** Σ, including unused symbols. Keep immutable original trace IDs; storage interning within a label is allowed, renumbering feedback is not. Maximize |P|, equivalently minimize c(P) = n − |P|. Default research regime: all complete partitions, unrestricted local DFA states. Explicitly distinguish any restricted admissible family or bounded-state regime.

Structural compatibility (paper Lemma 1): every negative y_i has a block B where its projection differs from every positive projection. One common separating block per negative; different negatives may use different blocks. A structural NO propagates to all refinements; a structural YES propagates to coarsenings. Neither implication holds for generic bounded feasibility. Optimization is NP-complete even for length-two words (paper Theorem 1); no claim of universal polynomial optimizer.

Raw words determine unrestricted compatibility and feedback. Thus query optimization is computational evidence acquisition, not acquisition of unknown labels. Raw evidence can prove mathematical feasibility, but the operational result must include the unchanged external service's ACCEPT and returned witness output. Maintain distinct raw/mathematical and external incumbent records. If external acceptance cannot be obtained, report structural optimum separately, operational INCOMPLETE. A proved conflict from identical opposite-label words establishes global structural infeasibility; no fabricated ACCEPT is required for infeasibility.

## 3. External adapter (selector-side only)

The paper describes semantics, not an RPC/JSON wire schema. Obtain the actual endpoint protocol, mode/capacities, negative-column order, receipt/artifact format and table completeness/reference contract from the owner. Normalize internally:

| Status | Meaning | Permitted action |
|---|---|---|
| PROJECTION_NO | Structural failure, one failed original negative, positive witness per block, unrestricted rejection tables R∞_B | Verify and ingest named/anonymous zeros and free groups; exclude refinements, derive further certified constraints |
| ACCEPT | Complete partition and local DFA witnesses; bounded success may include joint row | Verified external incumbent; do not demand tables on success |
| BOUNDED_NO | Conclusive failure for exact partition/capacity/sample | Exact scoped nogood only unless independently structural facts exist |
| UNKNOWN | Timeout, interruption, ambiguous or malformed response | Preserve pending candidate; retry/defer; no semantic rejection |

A trusted separately authenticated exact verdict may survive malformed optional feedback, but that feedback must be quarantined. Keep raw response, request ID, sample and regime digests, canonical partition identity, original IDs and ordered columns. Never promote an untyped NO to structural without evidence. Complete unrestricted base table: 0 means local acceptance, 1 rejection; fixed zeros exactly positive matches, free groups have independent bits. One zero in a row proves nothing about fixedness; one sound rejecting bit proves separation. Fixed-zero columns need not share projections. All-zero row always exists; free does not mean mandatory 1. Bounded/conditioned tables cannot be interpreted as unrestricted equality tables. Paper guarantees named witnesses for the failing negative, not every zero. Recover unnamed witnesses by literal raw comparison when useful; provenance RAW_LOOKUP, not EXTERNAL.

Historical `model.ProjectionOracle` is a local unrestricted simulator (`status`, `blocks`, `tables`, `failed`, zero pairs and free groups, tables even on ACCEPT). It is not the paper's actual service and returns no DFA artifacts. Preserve it as baseline/test fixture only. Do not change the external system to fit it. For unknown regime use conservative exact-only rejection semantics until resolved.

## 4. Historical engineering state and reproducibility

Recovered architecture: Hybrid Merge Search and SAT Feedback Master; prior rule families A01–A15 / S01–S12. Relevant baseline modules: `sample.py`, `model.py`, `hybrid.py`, `staged.py`, `search.py`, `compact.py`, `verify.py`, `check_rules.py`. Existing strengths: count/atom analysis, zero/separation antichains, witnessed lower bounds, repair, merge-layer search, optional rank and diagnostics, replayable certificates. Existing problems: dense one-hot Python integer masks, cross-label Cartesian comparisons, pair/triple scans, duplicate merge paths/frontier memory, local teacher assumptions on success tables, missing complete external timeout lifecycle. Keep old baseline unchanged for paired tests. The improved scale archive differs from pinned code (reverse contractions, verifier/fast path); audit exact diff before migration, do not conflate variants.

Reported historical results (not new measurements): HDFS-1024 and holdout cost 2 / 27 blocks; cover path-8 cost 4 / 12 blocks; scale improved 1,000 symbols / 10,000 traces cost 986 / 14 blocks, 986 mandatory unions, one local simulator call, 0.109 s producer and 0.319 s verifier. Prior 30 s incomplete run dominated by pair scanning. Planted suite: 33 independent samples, 41 run records (19 OPTIMAL, 14 INCOMPLETE, 8 MEMORY_LIMIT; 17 VERIFIED, two OPTIMAL with incomplete verifier). Historical 100,000-symbol cases exhausted memory or timed out; one collection of 100,000 singleton masks measured ~638 MiB. A producer OPTIMAL string is not a verified certificate. Archive timings are not controlled same-host speedup comparisons.

## 5. Four research deliverables and synthesis

### R01 — SDJ-IDA / sparse analysis (`01_SPARSE_ANALYZE(2).md`)

Replace alphabet-wide masks with compact integer IDs, sparse sets/complements, packed trace/position arrays and DSU. Sparse singleton counts and sparse fixed-partition checking handle empty projections explicitly. Three-way deletion-signature join: touched on both sides, negative deletion vs positive full word, positive deletion vs negative full word. Hash only filters; literal erasure validates every witness. For the same negative, two singleton/current-component deletion obligations force co-membership, even with distinct positive witnesses. Store a spanning forest with endpoint/trace IDs. Rerun on frozen mandatory quotient snapshots if budget permits; a fixpoint is only complete for this rule class, not global mandatory relations. Do not relabel original trace tokens by quotient labels.

Implicit discrepancy descriptor: unary count differences and inversions of occurrence ranks of stable symbols. Query exact discrepancies without a dense pair matrix; derive exact discrepancy support, weighted obligations and greedy inclusion-maximal equal regions (not maximum size). Missing alternatives may not be treated as exhaustive; only full implicit predicate or verified superset of alternatives can support necessity. Use lazy comparisons and capped cache.

Report validation: 14,520 ordered distinct word-pair join checks, 1,000 random corpora, nine target roots. Both `huge_long_active` and `huge_reverse_unused` (100k symbols, 20k traces) yielded 10,000 verified forced unions and 90,000 structurally compatible blocks. Discovery 0.7632/0.1094 s, raw check 0.1346/0.0159 s, RSS 185.66/130.06 MiB respectively. These are raw-only prototype measurements, not end-to-end external calls. Nine structural optima matched references; general sparse engine/quotient closure/implicit descriptors and new proof I/O are not production-tested. See §§3–8, 10–12 and Appendix A.

### R02 — AEFC / complete history implication (`02_NO_IMPLICATION(2).md`)

Retain two indexes: per-negative maximal dead regions for containment, AND identity-specific named equalities/free-group equality stars for stitching. Do not delete a named fact because an anonymous/larger region with a different witness subsumes its deadness. Use separate sparse DSUs over **trace IDs per unary/binary projection atom**, not the symbol DSU. Equality on all unary/binary atoms implies equality on the full block. Named least-equivalence closure is polynomial per target for consistent opaque-ID histories with named equalities and difference-monotone constraints. A negative matching a positive signature on every candidate block proves structural NO; distinct signatures in the least model do not prove actual separation. Realizability theorem: atom equivalence families are realizable by finite ordered words iff each binary relation refines both unary ones; constructed words are countermodels, never replacement inputs.

For anonymous zeros, choose positive witnesses exhaustively or use proof-producing Boolean logic. Check every consistent alternative; discard inconsistent branches by certified difference constraints; stop with UNKNOWN under budget unless a complete proof exists. Raw witness recovery may be cheaper in actual raw-input workflow. No eager n² atom index. Do not confuse completeness in opaque-ID evidence regime with knowledge of the actual literal corpus.

Report baseline audit: 2,529 cases, 26 targeted, 10,211 replays, 5,553 node checks, 7 rejected corruptions; four legacy certificates VERIFIED. Independent new AEFC test was **rerun in this session**: 615 realizability systems, 14,760 projection comparisons, 1,037 NO histories, 2,980 named and 2,860 anonymous target checks, 15,305 synthesized branches, both targeted strict examples passed. No strict gain in random/exhaustive-small sweep, and anonymous choices capped at 243. This is important negative evidence for deciding when to enable advanced closure. No live external calls or production speed measurements. See §§4–10. Raw comparison and region containment should remain cheap first tiers; named closure is lazy, anonymous branch search optional.

### R03 — EDR-BB / exact search and rank bounds (`03_EXACT_SEARCH(2).md`)

A node represents R(E,D): complete partitions coarsening equality partition E and satisfying branch-local disequality pairs D. Root E is certified mandatory quotient. An unsatisfied conflict is a necessary disjunction of allowed current-component pairs; derive from same-negative dead cover, disjoint deletion supports, complete alternatives, or proved rank constraint. Order pairs e_1,...,e_t. Child j forces e_j equal and e_1,...,e_(j−1) unequal. These children are disjoint and cover every completion satisfying the disjunction by unique first true pair. Keep residual if not proved infeasible; stream lazily with rollback DSU and a cursor. Generic all-pair fallback after exact-only NO excludes only representative E, covers every strict coarsening. UNKNOWN E remains pending even if strict coarsenings expand. Do not combine conflict-only branching with canonical merge-parent pruning (counterexample in §4.1).

Base cost n−|E|. Lower bound adds only additional quotient rank, never charges mandatory unions twice. Cheap deletion hitting floors, disjoint supports, degree, existing overlap correction; exact localized witness-rank/DP small supports and rational fractional rank packing as second tier. For r_P(S) = |S| − number of final blocks touching S, if verified local floors l_h and λ_h≥0 with Σ_{h:v∈S_h}λ_h≤1, additional rank ≥ ceil(Σ_h λ_h l_h). Use exact rationals and proof replay. Only retain alternative families fully contained in support (never truncate); heuristic transversals yield upper, not lower, bounds. Decomposition from partial evidence is valid for relaxation bounds only. Full structural decomposition requires proved independence. SAT/PB/ILP/RGS optional baselines or small kernels; solver OPTIMAL text is not proof.

Report reference checks: 600 random corpora, 27,800 compatibility comparisons, 3,705 reference nodes, 203 six-symbol fractional tests; strict overlap example floor 2 rather than 1 for specified primitive bounds. These are reported, not rerun; companion script absent. Full EDR-BB, local proof generation and verifier are design only. See §§3–10, 12–13.

### R04 — CDAQ / query policy (`04_QUERY_POLICY(2).md`)

Exact engine supplies a protected anchor; policy ranks a small pool of complete candidate partitions (anchor, repair, frontier alternatives, coarse diagnostics). For residual weighted sample C, an ACCEPT on Q removes all R with cost≥c(Q); structural NO removes R refining Q, optionally more via same-negative history simulation. Robust conditional score = min(ACCEPT removal mass, NO removal mass), normalized by estimated cost if desired. Use common weights/sample for all proposals. A coarse diagnostic may be useful but ACCEPT alone cannot prove optimality. Never credit entire region from rejecting one representative. Scores are heuristics for order only; conditional sampled floor is not a guaranteed global query saving. Timeout unconditional progress can be zero. Optional probe budget B per unresolved anchor; default B=0 until exact engine validated, then B=1–2 and small pool 16. No probabilistic pruning, no starvation, no unaccounted query attempts. Later optional expected gain, calibration and latency model only after robust baseline.

Report finite check: 250 random four-symbol corpora, 3,900 conditional checks; no policy-vs-baseline end-to-end measurement. Logarithmic bound only under explicit balanced-query condition or special unique-pair promise; not general. See §§4–9, 11–12, Appendix A.

## 6. Integrated architecture (proposed names, not existing files)

Use one selector, one immutable evidence ledger, one exact coverage engine and one independent proof verifier. No parallel competing production solvers. Suggested layout inside `implementation/partition_feedback_final/` (new `selector_v2/` namespace to avoid overwriting legacy, subject to repo conventions):

```
selector_v2/
  core.py             # immutable sample, digests, stable IDs, sparse partition/region views
  sparse_analysis.py  # count index, deletion join, implicit discrepancy, raw proof facts
  external_adapter.py # complete request + response normalization; no learner logic
  evidence_store.py   # append-only source facts, antichain and named indexes
  aefc.py             # lazy trace-atom closure, optional anonymous branch proof
  rank_bounds.py      # quotient obligations, cheap and localized exact bounds
  region_search.py    # rollback symbol DSU, disequalities, disjoint coverage, pending frontier
  query_policy.py     # read-only proposal generation/ranking; protected anchor
  runner.py           # orchestration, attempt budgets, restart/checkpoint, status
  certificate_schema.py # shared versioned grammar, not proof trust
  verify_v2.py        # independent proof kernel; no producer caches or ranking imports
  tests/              # literal small oracle, exhaustive tests, adversarial fixtures
```

Dependency contract: Core → raw analysis and adapter → evidence; evidence → AEFC and bounds; evidence/bounds → exact engine; exact engine → policy snapshot; policy → runner → adapter; adapter → verified ledger. Verifier reads original sample, immutable schema and proof artifact independently. Never make a policy output a proof. Separate symbol DSU (mandatory and branch merges) from per-atom trace DSUs (equality evidence). One source of canonical partition identity and cost; raw projection comparison retains original token IDs; use schema-versioned immutable group snapshots. Index caches are disposable, proof facts append-only. Root constraints vs branch constraints are scoped separately.

Common proposed interfaces:

- `Sample`, `PartitionRef`, `RegionRef`, `Budget`, `EvidenceId`, `ProofId`, `Scope(sample_digest, regime_digest)`.
- `discover_deletions(sample, owner_snapshot, budget) -> verified facts + cursor + exhausted`.
- `raw_check(sample, complete_partition) -> structural result + proof` (not external verdict).
- `evaluate(complete_partition, request_id) -> NormalizedResponse` (only documented external transport, or explicitly labeled simulator).
- `ingest(response) -> validated delta`; `prove_no(partition, budget) -> proof | UNKNOWN`.
- `lower_bound(region, ledger_version, budget) -> absolute bound + proof`.
- `next_anchor() -> task`; `split(region, certified_conflict) -> coverage proof + lazy cursor`.
- `rank_proposals(snapshot, pool, budget) -> order only`; `verify(sample, proof, receipts) -> independent status`.

## 7. End-to-end algorithm and status semantics

```
validate immutable sample and declared regime
initialize singleton symbol DSU, ledger, independent proof writer
check label conflicts and legal degeneracies
run budgeted sparse deletion join; replay mandatory edges
root := complete mandatory quotient; cost floor := n - |root|
raw_check(root) and use it as evidence / proposal
if root structurally compatible and unrestricted:
    prove structural optimum from mandatory floor + root witness
    submit complete root externally; verify receipt/witnesses
    if ACCEPT -> operational OPTIMAL; if unresolved -> structural optimum, operational INCOMPLETE
    if contradictory external verdict -> quarantine and diagnose scope/evidence
otherwise:
    initialize exact region frontier covering all admissible completions
    while unresolved tasks and budget:
        obtain protected anchor; compute verified bounds and NO evidence
        if region proved infeasible/nonimproving against external incumbent: close with proof
        else if conflict implies necessary pair disjunction: split disjointly, retain cursor
        else choose representative proposal or bounded optional diagnostic (CDAQ)
             submit complete partition, count every attempt
             normalize and validate response, append proven evidence
             ACCEPT -> update external incumbent, close only justified region/cutoff
             PROJECTION_NO -> derive same-negative conflict/closure and propagate
             BOUNDED_NO -> exact nogood, generic remaining-region coverage
             UNKNOWN -> preserve candidate and pending work, fair retry
        checkpoint proof/ledger/frontier and bounds
    independently verify final certificate
```

Unrestricted raw mathematical optimum may be reported separately even if service unavailable. Structural evidence remains necessary under bounded mode, but disable unbounded-only shortcuts, unused-symbol dominance and decomposition without applicable proof. If a raw root is compatible but external mode is bounded, proceed with bounded exact search rather than assuming optimum. `OPTIMAL` operationally = verified external ACCEPT plus independent proof all strictly cheaper admissible candidates excluded. `INFEASIBLE` = verified exhaustion or global contradiction, with bounded opaque verdict trust disclosed. `INCOMPLETE` = unresolved search/receipt/verification, best external incumbent if any, certified global lower bound, gap if U finite, pending frontier and attempt log. Separate statuses producer / verifier / external; verifier failure is not certification. For all-optima enumeration change cutoff to strict >, otherwise equality cutoff is allowed. Never promote a timed-out result or local emulator success to an external operational ACCEPT.

## 8. Implementation roadmap and gates

Effort windows below are proposed engineering estimates in work sessions, not guaranteed dates. Do not enable advanced modules before foundation gates pass. Assign one integration owner; merge only after tests and proof review.

| Phase / priority | Work and dependencies | Required acceptance gate | Indicative sessions |
|---|---|---|---|
| P0 | Freeze baseline SHA, archive exact variants, document actual service protocol, sample schema, mode, receipt; choose isolated selector branch | Reproducible baseline; adapter contract or explicit simulator-only blocker; no external system changes | 1–2 |
| P1 | Core sparse representation, raw check, singleton counts, three-way deletion join, endpoint contraction proof; independent root verifier | 100k sparse fixtures without dense masks; literal exhaustive equivalence; forced proof mutation rejected; nine root results if raw inputs restored | 3–5 |
| P2 | Adapter normalization, evidence store, region containment, raw witness recovery, persistent attempts and checkpoints | ACCEPT without tables; malformed IDs and group coverage; timeout/UNKNOWN; bounded NO exact only; all original IDs preserved; legacy simulator tests | 2–4 |
| P3 | Minimal EDR-BB, rollback symbol DSU and disequalities, conflict iterator, base lower bound, independent region proof replay | All small exhaustive optimum costs match literal/RGS reference; disjoint coverage verified; restart same unresolved region; no unproved pruning | 4–6 |
| P4 | Cheap rank bounds, R01 implicit support/region descriptors, named AEFC lazy closure, proof verifier extensions | Every bound ≤ true small optimum; both AEFC targeted cases and random regressions; sparse budget; no false NO | 3–5 |
| P5 | Localized joint rank + rational fractional packing, optional component join closure, anonymous AEFC with cap | Exact rational capacity and support proofs; strict examples; UNKNOWN on incomplete branches; ablation establishes incremental usefulness | 3–5 |
| P6 | CDAQ robust cone/cutoff ranking, then same-negative amplified score; B=0 vs B=1/2; optional learned estimator later | Fair anchor under repeated probes, all attempts counted, common sample and scope, no rank-dependent proof; compare against identical exact engine | 2–4 |
| P7 | Full controlled benchmark suite, actual external handoff where available, independent replay, paper contribution audit | Zero accepted corrupted proofs; verified optimum rate, latency/RSS/wire/bytes and query counts, independent final receipt; document negative results | 3–6 |

Parallelizable after shared schema freeze: sparse raw producer and independent raw proof verifier; adapter contract tests; small exhaustive RGS reference. P3 search consumes P1/P2 types and proofs; P4 bounds and AEFC can be built on the shared ledger in separate branches; CDAQ must wait for stable frontier API and meaningful metrics. Suggested first milestone MVP = P0–P3, simple containment and cheap base bounds, B=0, no anonymous SAT, no ML. Root shortcut alone is not general search. Freeze schema before assigning coding agents; keep code in one integration branch with separate small PRs.

## 9. Validation plan and research claims

Baseline ladder under the same sample, external interface and resource budget: legacy pinned; enhanced archive; v2 sparse + base exact; + region evidence; + AEFC; + localized/rational bounds; + CDAQ robust; optional learned ranking. Also raw-only structural exact versus external-confirmed runs. Use same local evidence budgets for policy comparisons. Keep input-only directory separate from references and planted generators/expected labels. Use HDFS, cover-path, count, choices, long/interleaved, imbalanced, duplicate/empty, huge active/unused fixtures, and new nonplanted corpora. Generate exhaustive small instances including adversarial bounded and timeout protocol tests; mock bounded verdicts only to validate adapter/search semantics, not bounded learner performance. Use seeded generators, fixed host/runtime, RLIMIT semantics documented, same budgets 5/30 s and memory caps as appropriate. Re-run all older certificates or mark schema-specific incompatibility explicitly.

Measure attempts (including incomplete), distinct complete candidates, accepted/NO split, inferred NO by rule, explored regions, proof bytes, raw/preprocessing time, generation/ranking time, external/transport/parse time, independent verification time, peak RSS, response bytes, lower and upper bounds, gap, verified optimality rate. Record full failures and censored runs. Distinguish logical structural success from operational ACCEPT. Do not claim measured end-to-end gains from raw-only prototypes or compare old/new unlike phases. At 90,000 blocks and 10,000 negatives a fully expanded external table may be 900 million columns across blocks; verify supported compact references, do not modify service. External latency and proof I/O remain blockers.

Mandatory counterexamples: union of dead regions can separate; mixing negatives invalid; one zero row not fixed zero; anonymous zero identity unknown; free not forced 1; partial atom alternatives insufficient; count equality misses order; quotient-token relabeling loses order; no unconditional bounded monotonicity; canonical-parent + conflict pruning can miss optimum; LP restricted columns not valid lower bound absent exact pricing; no inferred actual separation from least-model signature difference; branch cursor cannot disappear at cap; interrupted optimum proof is incomplete. Reject malformed and mutated certificate fields without relying on Python `assert` in hardened verifier.

Novelty candidate, not established publication priority: (1) SDJ-IDA exact sparse deletion join and implicit evidence extraction, (2) AEFC atom-equivalence realizability and complete named/anonymous history closure, (3) disjoint evidence-directed search and fractional restricted-rank packing, (4) certificate-progress conditional scoring plus protected scheduling. Paper's atom characterization, monotonicity, NP-completeness, prior witness-rank and zero region rules, hashing and generic equality branching are existing results/techniques; do not rebrand. Do literature audit only after integrated algorithm and ablation, with clear theoretical assumptions. Main contribution should be coherent proof-carrying selector, not four unrelated claims. Open issues: actual external protocol, realistic marginal AEFC gain (random sweep showed zero strict gains), compressed closure, profitable localized supports, dense conflict tails, global score balance, actual query savings and end-to-end scalability.

## 10. Immediate implementation task (copyable agent prompt)

> You are the integration engineer for the passive-automata-learning partition selector. Read PROJECT_HANDOFF.md, the four research reports, the main paper if available, and the repository at verified commit 7c90eb59561bd25ec4fdca5ac08b0e5d60d17fd6. Implement only P0/P1 in a new selector_v2 namespace/isolated branch; do not modify the external automata evaluator or legacy solver. First inventory exact existing source and archive diffs; preserve raw ordered words, IDs and declared alphabet. Implement compact sparse representation, sparse literal compatibility checker, three-way deletion-signature join with exact collision resolution, mandatory forest and independent root proof replay. No dense singleton masks, no all-pairs preprocessing by default, no planted labels, no external protocol assumptions. Keep raw feasibility separate from ACCEPT. Produce unit/exhaustive tests, input-only benchmark runner, explicit incomplete outcomes, changed-file list, reproducible commands, per-stage timings/RSS, independent verification and unresolved blockers. Add a versioned schema and integration API document for P2/P3; do not claim full exact optimization from root-only success. Stop at the gate; report failures rather than silently fixing reference labels or weakening checks.

Next agent (after P1 shared schema): implement P2/P3 with strict normalization, independent evidence checks, disjoint search coverage and checkpoint/resume; keep policy B=0, use small literal exhaustive oracle to verify every optimum and mutated proof. No speculative feedback or new external endpoints. Later agents implement P4/P5 and P6 against shared interfaces, not separate solvers.

## 11. Decision log / continuity

- 2026-11-24: original scope recovered; exact commit resolved; all four research reports reviewed, Python AEFC validation rerun successfully. No GitHub writes, production code changes or real evaluator calls in this session.
- Proposed integration decision: build sparse foundation first, exact engine with policy disabled, then add advanced evidence/bounds and diagnostic ranking. Names, directory layout, work-session estimates and default budgets above are recommendations, not existing implementation or user-approved deadlines.
- Blockers: real external protocol/capacities/receipt access unspecified; prior ZIP raw bytes and full benchmark inputs not recovered here; main PDF and earlier report identified but materialization denied; companion R03 script not supplied. Historical tests and timings beyond the rerun remain reported evidence, not new reproduction.
- Update this document at every milestone: commit SHA, change list, proof schema, test commands/results, external status, data fingerprints, unresolved cases, next action. Store the master document in the repo, e.g. `implementation/partition_feedback_final/PROJECT_HANDOFF.md`, plus source archives separately. This session did not commit/upload to GitHub. Do not mark milestone complete until independent gate passes.
