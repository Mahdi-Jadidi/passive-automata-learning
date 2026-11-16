# Claim ledger and proof obligations — V44

This assessment concerns the frozen V43 exact optimizer. It does not alter the mathematical objective in `docs/ALGORITHM_NOTATION.md` and does not rewrite historical evidence.

| Claim | Evidence | Status and limit |
|---|---|---|
| Projection criterion with unrestricted regular factors | Article Theorem 1; `encoding.reject`, `encoding.feasible` | Mathematical proof supplied; no local DFA learning or state cap required. |
| Monotonic rejection | Article Lemma 1 | Projection-composition proof supplied. |
| Mandatory-group contraction preserves every compatible partition and its objective | Article Theorem 2; `Prepared.prepare_atoms` | Proof supplied; groups are necessary equalities, not a recovered physical decomposition. |
| Single-negative optimum q-d+1 | Article Theorem 3; `optimizer._solve`, `verify_optimal` | Exact; finding/ruling out smaller rejecting sets can still be exponential. |
| Minimal-witness extraction terminates and is complete | Article Lemma 2 and Theorem 4; `Prepared.minimal_witnesses` | Frontier coverage and strict-shrink proof supplied; finite resource assumption. All 167 nonempty-subset antichains on four atoms audited in V43. |
| SAT feasibility and objective equal the partition problem | Article Theorem 5 and Appendix A; `encoding.build`, `threshold` | Gate and count recurrence specified. V44 checks 15,664 assignments/thresholds on 100 samples. |
| Whole algorithm returns an optimum on successful completion | Article Theorem 6; `optimizer._solve` | Conditional mathematical proof: exact operations, sound complete SAT, sufficient resources. Not formal verification of Python/native execution. |
| Returned upper bound or DRUP proof certifies optimality | Article Section 6; `verify_optimal`, `check_drup`, `RupDatabase` | Producer CNF/UNSAT flag not trusted. Shared encoder remains trusted; three traces also checked through frozen V42 code. |
| Polynomial work on ab/ba plus unused-symbol family | Article Theorem 7; `structural_family.py`, nine raw outputs | Proved for this family. Tested up to 256 symbols; tests do not prove arbitrary-input polynomial complexity. |
| Strict superiority over the specified exhaustive optimum traversal on that family | Article Theorem 7 | Restricted-family separation only; another algorithm can use the same reduction. |
| Universal speed or memory superiority | Ten-case benchmark explicitly has counter-ranking cases | Not established. DP is faster on overlap_8; V42 is faster on oneblock_8. |
| Scientific first-in-literature novelty | Article related-work comparison and primary-source references | Not certified. SAT, monotone extraction, conjunctive responsibility and alphabet refinement have prior art. Specific construction merits independent expert review. |
| Defect-free final software | Bounded oracle, boundary, mutation, proof and encoding audits | Not proved. No theorem prover or verified native runtime; finite tests are evidence, not a universal software proof. |
| Successful real AND-model field validation | `field_readiness.json` and pinned BGL source audit | Zero valid field trials. Existing labels concern individual alerts/selected outputs. Whole-trace acceptance labels and episode provenance are missing. |
| Independent scientific/software review | No independent review report in this assessment | Not completed; author checks and independently coded comparisons must not be described as peer review. |

## Exact execution invariants

1. Every rejected projection is absent from **all** positive projections on that block. A per-positive choice of a different block is insufficient.
2. Every contracted atom is contained in one block of every feasible partition. Rejection queries always expand atoms to original identifiers.
3. A false region excludes every subset. Splitting by a known minimal witness covers all different undiscovered minima. Frontier dominance cannot remove the last coverage of a witness.
4. Representative gates and the counting recurrence are equivalences. Their positive threshold cannot be satisfied by an auxiliary assignment unrelated to the partition.
5. A SAT model supplies a feasible incumbent; an UNSAT threshold supplies only an upper bound. Interrupted queries supply neither.
6. `OPTIMAL` carries an attained-bound certificate or a refutation of k+1. The consumer checks either type. The producer's general path checks feasibility and replays DRUP when present; shortcut returns do not invoke that internal check. `INCOMPLETE` carries no claimed mathematical result.
7. A certificate consumer reconstructs the instance-dependent constraints; an external producer cannot redefine the sample or threshold by supplying a CNF.

## Remaining acceptance requirements

User-confirmed data limitation: suitable field data are currently unavailable. The user explicitly requested recording this limitation. Field validation is deferred pending appropriate data; no field-success claim is supported by the present experiments.

- Supply real episodes with whole-trace acceptance/rejection under the specified conjunctive model, declared Σ, reset/episode provenance and a sampling protocol. The optimizer assesses sample compatibility; without extra assumptions it does not identify the true physical devices.
- Obtain independent review of the mathematical reductions, literature positioning and checker/encoder trust base before describing the result as a validated scientific contribution.
- Formal software verification, if required literally, is a separate project: port/specify the trusted normalization, projection, contraction, extraction, encoding and proof-checking routines in a proof assistant. This assessment does not substitute finite tests for that work.

No real labels were fabricated and no observed failure of universal dominance was omitted.

## AI-assisted review and resolution

`REVIEW_PROOFS.md` and `REVIEW_EVIDENCE.md` are read-only reports from two Terra agents using low reasoning effort at the user's request. They are separate agent audits, not independent scientific peer review. Neither reported a definite incorrect optimum or accepted invalid certificate. They identified (a) an ambiguity about shortcut self-checking, now clarified in the article, and (b) insufficient individual encoding outcome logging, addressed by a new 15,664-check detailed replay. Aggregation validates stored records and hashes; it does not rerun the full 120 benchmark or 2,261-case historical audit. Original reviewer reports are preserved rather than rewritten after fixes.
