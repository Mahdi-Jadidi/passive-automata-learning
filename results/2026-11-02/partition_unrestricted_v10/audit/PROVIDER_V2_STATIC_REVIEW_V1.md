# Independent static review — C010 provider v2

## Frozen candidate examined

This review reads the following source state only; it does not execute provider code or mutate implementation files.

| Artifact | SHA-256 |
|---|---|
| Readiness v2 snapshot | `610cecf727498b7061c2b76196fdc6df7a81e2499287332df669d64537242611` |
| Solver v2 | `4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502` |
| CLI v2 | `3140df25bab5d60c6c2705098029db9061e3c9d76743bf1dfd48d46aaf2d5eaa` |
| API protocol v2 | `0120261cec26de42a812a18760d0dea598b9085fb14a9e72f63da073bc3a9562` |

All implementation file hashes and byte counts matched `READINESS_V2.json` during this review. The readiness record says sources are frozen, the v1 spectrum defect is fixed, and the theory review was received.

## Static findings

1. **The v1 Stirling/Bell defect is repaired.** `_stirling_bell(r)` now retains each row `S(n,k)` and the shortcut reads `stirling[r][k]`; the Bell total still comes from summing the row. For an atom-feasible `r=3`, source arithmetic therefore yields `1,3,1` and total `5`. The returned shortcut `k_max_compatible=r` is exact because every coarsening is feasible.
2. **Deadline and interruption protection now covers atom extraction.** `_extract_atoms` checks the absolute deadline for each positive/negative pair, while scanning long words, and while building connected components. Its call is enclosed by a handler returning `unknown`, `complete:false`, with count and relation claims omitted. The main projection, DP, witness and enumeration work remains inside the subsequent protected block.
3. **The exact fallback logic retains its proof shape.** V2 reuses the anchored subset DP, exact lazy rejection masks and monotone remaining-coverage pruning reviewed in T5. The new atom-to-symbol map is used consistently for pair aggregation, and fallback `k_max_compatible` is derived from the largest nonzero exact count.
4. **The output contracts match the unrestricted theorem.** A complete valid result must have a nonzero one-block count, all pairs have a same-block witness, and no pair can be forced different. V2's status choice remains based on the complete total; only the one-block family can be a singleton.

## Caveats for the behavioral gate and final report

* Input validation still runs before deadline/interrupt protection. The implementation does not promise an interrupt-safe return while validating extremely large inputs. The preregistered frozen cases are small, and the capture hard deadline bounds their run; report this boundary rather than describing all entry work as cooperatively interruptible.
* The API rejects `k` and `allowed_k` but ignores other unrecognized object keys. Keep inputs to the frozen three-field schema and do not imply that extension fields are validated or enforced.
* `preprocessing_seconds`, `search_seconds` and `provider_seconds` have the scoped meanings documented in API_PROTOCOL_V2; use capture wall time for total end-to-end time. This audit round is correctness-focused and does not authorize a performance benchmark.
* No runtime behavior has yet been independently checked. This file clears only the static source review; acceptance requires the preregistered complete-set provider gate, invalid/deadline/interruption controls, independently replayed certificates, and then the four bounded scale correctness cells.

## Decision

No additional mathematical blocker was found in the reviewed v2 delta. The exact-k fast-path correction is consistent with the independently proved theorem and source hashes match readiness. **Static review cleared; do not treat v2 as accepted until the independent captured behavioral gate completes.**
