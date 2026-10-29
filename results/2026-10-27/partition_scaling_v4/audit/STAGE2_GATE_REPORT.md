# Stage 2 independent correctness gate

**Decision:** accepted for correctness and source integrity. No Stage 2 performance run has been authorized or executed.

The machine-readable gate is `stage2_gate_report_v1.json` (SHA-256 `f1ab159020e3b16d8e6ce80e9989b68e3ec646d898e45cb323a1ed436883adcf`). It binds the active `solver_v2.py` release candidate and six provider/support sources to `runtime_stage2_r2.json` (manifest SHA-256 `e2a1d0fbff9294370e37a1244624fef79c177f397c5a88266cf3a8eaf6cc4ea8`). Both source-integrity and capture-reconciliation error lists are empty. The final read-only aggregation is captured as `20261029T083738.673610Z_824c7d2293`.

## Correctness evidence

- The frozen corpus contains 106 case records plus one separate QOP example. There are 104 canonical normalized solver payloads and three duplicate-payload groups; these are test records, not 107 independent observations.
- S002 matches the independent full partition oracle on 82 records, including 80 imported small cases and two sparse `k=3` controls.
- General `q=2` matches exact full sets on 88 small records; six `q=1` controls also match. The four larger constructive cases are separately checked. General search returned `found` on two and `incomplete` on two, so no uniqueness claim is made for those incomplete searches.
- QOP passes eight small controls and returns a unique certificate on all four positive-only scale cases (up to alphabet size 128, `k=8`). The public tiny example has oracle counts `q=2: 1`, `q=1: 0`, unrestricted: `7`.
- The four long contextual regular cases return an exhausted unique solution. The independent summary recomputes counts from the frozen inputs and confirms word lengths against the hidden sidecars: `(alphabet, k, max/min word length, positive raw/distinct, negative raw/distinct)` are `(32,4,128/126,29/29,28/4)`, `(32,4,1024/1022,29/29,28/4)`, `(32,8,4096/4094,25/25,24/8)`, and `(128,8,1024/1022,121/121,120/8)`. The realizability proof uses `L_i = u_i E_i*`, with `u_i` the block projection of `C` and `E_i` the 2-symbol tree tiles.
- Unknown-`k` singleton checks omit `k` from provider inputs; the active v4 correctly returns `incomplete` on the injected interruption. The historical v3 `KeyError` is preserved as a regression record. Twelve R2 CLI checks pass, including examples and invalid/deadline boundaries.

## Scope and preserved infrastructure events

The QOP result is conditional on known `k`, `q=2`, exact finite labels, and a verified q-opposition certificate; it is not an unrestricted DFA-factor result. The four large general q2 rows with incomplete search establish a valid first answer only.

A reported service HTTP 404 is preserved as an infrastructure event. Its raw response, request identifier, endpoint, and timestamp were unavailable, and there is no linked provider attempt; the existing provider captures were used without rerunning providers. Two failed read-only aggregation attempts are retained as superseded auditor records; neither started a provider. The final aggregation succeeded.

See the JSON gate report for per-capture IDs, hashes, source bindings, limits, and duplicate record accounting. Stage 2 timing remains pending explicit authorization.
