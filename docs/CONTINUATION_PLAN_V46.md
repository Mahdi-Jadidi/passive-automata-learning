# Continuation plan: longer-budget validation and a full English paper

## Fixed decisions

Continue the V45 interactive algorithm. Keep the manuscript teacher's algorithm unchanged. Do not implement the fast feasibility adapter or any internal teacher strengthening. User explicitly requested only increased time limits, rigorous tests/review and a full English research paper, with teacher improvement suggestions at the end. Preserve V43–V45 evidence and the supplied PDF. Work in `results/2026-11-16/teacher_assessment_v46/` or a new dated continuation folder if V46 evidence already exists.

## Phase 1 — environment and integrity

1. Read the current handoff, notation and V45 code/proof/conformance; inventory the V46 draft files and review their contents rather than assuming their quality.
2. Verify recorded V43 hashes and every listed V45 manifest hash read-only. Compare the in-repo supplied manuscript copy to its recorded digest. Record missing/platform-specific dependencies and provision an isolated runtime. Ensure versions are tested in separate processes.
3. Inventory prior result schemas and inputs. Do not overwrite old raw files or regenerate frozen manifests. Store harness settings, source/corpus digests, dependency versions, platform, hardware, actual limits and process startup measurements with new results.

## Phase 2 — increased limits, same algorithm

1. Create a new parameterized harness; V45's parent benchmark command hardcodes one-second workers. Confirm the actual worker receives the new budget and record it per row.
2. Replay all 2,261 frozen-reference inputs at **0.25 seconds each**, up from 0.03 seconds, as a correctness/resource audit. This is not a broad timing benchmark. Every completed result must match the reference objective/infeasibility and pass the V45 consumer. Incomplete is censored, not a pass, rejection or infeasibility proof.
3. Run the ten fixed V33 benchmark inputs in sequential fresh processes with **60 seconds per solver call**, and a separate 60-second certificate-consumer budget. Compare unchanged V43/V45 under the same contract and caps. Run each method/case once first. For cases that complete, add two repetitions with alternating method order; do not waste duplicate 60-second censored trials solely to fill a median table. Report repetition count explicitly and medians only for the completed repeated group. Avoid simultaneous CPU-heavy audits/agent tests during timing.
4. Re-run the ordinary interaction fixture, the two-cut diagnostic and the two-symbol ab/ba atom-bound case with 60-second budgets. Replay feasible witnesses/certificates and trace each completed rejection to its cut. Compare output with an independent small-partition oracle. The two-cut fixture is model-dependent diagnostic evidence, not an unbiased benchmark.
5. For still-incomplete representative cases, log current teacher bound, block size, named-DFA progress and theoretical enumeration scale. Escalate at most **two** documented representatives to **300 seconds** each; preserve both budgets/outcomes. Do not use unbounded execution or silently switch to a faster teacher. If higher limits still do not finish, report that honestly and proceed with review/paper.
6. Record total pipeline and per-phase elapsed times, teacher calls/time, enumeration progress/cache hits, SAT calls, cut count, proof size and native process peak working set where supported. Separate startup, verification and censored outcomes. Memory includes Python/native imports and cannot establish allocation superiority. Repeat projection-only measurements under the SAME old cached-scanner baseline; retain unfavorable comparisons.

## Phase 3 — review from first principles

1. Prove finite-language projection characterization and the sufficient trie-bound bridge; distinguish caller-selected sufficient parameters from an imposed unknown-system state ceiling.
2. Check exhaustive local-table completeness, row dedup witnesses, distinct negative columns, positive-forced zeros, feedback-edge conditioning and both semijoin traversals against main.pdf. Check fresh conditioned tables versus immutable original cache, epsilon, empty positive/negative sets, contradictions, unused opaque Unicode IDs and deep words.
3. Prove exact DAG projection identity and cache publication rules, mandatory-atom contraction bijection, greedy maximal-false-region construction and generalized-cut soundness/progress. Never infer a particular merge from a disjunction of repairs.
4. Prove master equivalence/gate/counting semantics, relaxation and threshold invariants, validity of inherited bounds, first accepted maximizing candidate optimality, finite termination with adequate resources, and INCOMPLETE semantics. Worst-case exponential/Bell-scale behavior is possible.
5. Prove certificate soundness via original-word false-region witnesses, deterministic CNF reconstruction and DRUP/RUP induction. Test corrupt masks/indices/witnesses/proofs, negative-index rebinding, timeout paths and duplicate/tautological literals. Identify shared trusted code; do not describe software as formally verified.
6. Independently test small cases against brute partition/projection oracles and the raw Cartesian join for teacher relations. Review V46 drafts and cite concrete findings/resolutions, including failures. New bugs require new versioned fixes and regression evidence; do not silently alter historical sources. Any teacher algorithm change needs explicit user approval before implementation.

## Phase 4 — final article and delivery

Produce a standalone English paper with title/abstract, introduction, precise contribution boundaries, notation/model, primary-source related work, all subsystem descriptions, numbered pseudocode, worked interactive example, complete theorem/lemma proofs, complexity/resource analysis, reproducible methods, full results including incomplete/negative outcomes, limitations/trust base, conclusion, references and reproducibility appendix. End with proposals for strengthening the teacher, clearly NOT implemented. Discuss which proposals preserve every main.pdf interface and which apply only to restricted unbounded feasibility.

Use measured results; do not claim higher budgets made everything good if they did not. Scope innovation to the objective-specific construction and checked failure-generalization/certificate combination; distinguish it from established SAT, CEGAR/Benders and monotone search ideas. Scientific priority still needs systematic literature verification.

Retain Markdown/LaTeX source, bibliography, build scripts, raw logs, configs, summary scripts, complete page renders/QA and hashes. Produce a new English PDF, inspect EVERY rendered page and check text/tables/formulas. Keep V44/V45 PDFs unchanged. Update a concise status/claim ledger and repo start pointer. User confirmed no suitable field data: explicitly report zero valid AND-model field trials; this does not prevent completing the synthetic and theoretical tasks.

## Acceptance and stop rules

- A completed result must match its reference and pass a consumer; no unresolved correctness mismatch may be hidden.
- Every no-better claim needs a checked structural bound or refutation. Incomplete runs have no mathematical result claim.
- Teacher-preservation and hashes are explicit. Suggestions are not executed changes.
- Full article proofs, code correspondence, experiment limitations, raw evidence and build are reviewable from the repo without prior chat access.
- Final report states achieved versus unresolved obligations. Do not promise universal superiority, formal software correctness, real-field success or scientific-first novelty from finite tests.
