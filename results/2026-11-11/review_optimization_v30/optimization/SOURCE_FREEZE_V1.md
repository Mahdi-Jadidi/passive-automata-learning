# C030 candidate source freeze v1

Biggest overlooked point? A Bell count from a certificate is an exact mathematical family size, not a count of candidates actually enumerated. Neither baseline nor this candidate adds work telemetry.

Proof-approved proposal: `PROPOSAL_PROOFS_V1.md` SHA-256 `4a11b61337b0a1dda5e9969fdb1741e5d87d43a03ec74f5afbddbb712955ef79`. Candidate source `candidate_v1.py` SHA-256 `7501901c6de5d7bb78ffc60f152b818733e3bd4460c9a655b8d783f384e8fc2b`; do not edit after freeze. The old frozen C028 baseline SHA-256 is `5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94` and remains unchanged.

Entry points `solve_a`, `solve_b`, `solve_combined` have same signature and full result contract as C028 `solve`; the copied original `solve` remains baseline in this new file only. A is disabled for any explicit candidate budget, including zero; B is a fresh 256-entry LRU per invocation. No public entrypoint changed. This freeze is not code approval or an official experiment.

Developer smoke only: Bell(0..6) = [1,1,2,5,15,52,203]; five cases (empty alphabet, empty negative, opaque IDs, quantifier obstruction, contradiction) times budgets None,0,1,2,5 times three variants matched the copied baseline exactly. This is not independent verification.

The Bell recurrence takes O(m^2) bigint arithmetic operations, with nonconstant operand and output bit length. Returning a Python integer does not guarantee that a separate JSON/decimal conversion will succeed under a host's integer-string digit limit; serialization may require explicitly configured resources and is not silently claimed. B eviction may force recomputation and can increase memory/work compared with the baseline's early-exit behavior; no per-block-once or universal speed claim is made. Independent review, fixture/source freeze, and manager GO precede official provider runs.
