# V33 subset-DP candidate: frozen for review

Status: **candidate frozen for independent source/proof review and audit; no speedup has been demonstrated.** This is a research artifact, not a public default. The only candidate in this package is `candidate.py` with API `solve(record, *, max_candidates=None)`. From the project root on this machine, run the bounded local smoke check with `py results/2026-11-13/exact_candidates_v33/candidate_dp/smoke.py`. It uses Python 3.14.6 and compares the complete output against C028 for eight focused records and six budget values (including None, zero, invalid, and boolean). This is smoke evidence, not the independent audit or timing experiment. `SMOKE_OUTPUT.txt` contains the output.

The source computes counts by coverage-state subset DP and obtains first two compatible and optimum RGS witnesses by exact prefix-feasibility queries. `PROOF.md` gives the bijection, lexicographic proof and exponential complexity, including potential overhead. It imports the reference through its repository-relative path and checks its SHA-256 at import; this is a dependency, not a standalone file. Baseline helpers implement validation, projection, witness creation/replay, error format and all explicit candidate-budget behavior. A missing or modified reference makes import fail rather than silently using different code. C028 catches keyboard/memory failure in fallback; unlimited candidate additionally reports caught recursion exhaustion as INCOMPLETE. An uncatchable hard stop may yield no result. No new budget or public API is added.

The baseline compares exact Python data structures, including factor order and first rejecting block, not merely optimum values. Epsilon, empty alphabet, empty P, contradictions, repeated traces, Unicode/opaque and unused IDs, invalid input and budget fallback have focused smoke coverage. The largest overlooked issue is that RGS prefixes leave existing blocks open: their future additions affect rejection, and feasible-prefix testing must quantify over those additions before using the DP on newly formed blocks. Canonical order is not inferred from anchored subset iteration.

Provisional limitations: no official independent validation or performance evidence yet; recursion, exponential memory, prefix-query overhead, and 2^n coverage masks can make this slower or incomplete under finite resources. The candidate imports and inherits the exact reference helper behavior and needs those bytes available. The C030 optional optimizer was inspected, not incorporated. Any source correction requires a new version/hash and review; preserve this frozen version and evidence.

## SHA-256 bindings

- `candidate.py`: `8EC5B68A08D9EC430C0BF5F10D86024408C3BB9408A4045F7EFB41EED6E5F86F`
- `PROOF.md`: `37E99838EE8B869ACDE908191819DD31B3B173E5024A0017B0EB1CB7E0A80623`
- `smoke.py`: `EDF9F875405537241633C68EF9DD101AA85AC96433FB8838E405978A58516079`
- Frozen C028 `results/2026-11-11/exact_foundations_v28/implementation/reference.py`: `5F60B27447B37EC07F1FD6BCE75BE6199B898573D4B32E90413E900E3A615A94`
- Inspected C030 `results/2026-11-11/review_optimization_v30/optimization/candidate_v1.py`: `7501901C6DE5D7BB78FFC60F152B818733E3BD4460C9A655B8D783F384E8FC2B`
