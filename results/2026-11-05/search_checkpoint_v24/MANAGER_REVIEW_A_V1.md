# C024-A manager source review v1

Reviewed actual minimal diff against frozen C020. Candidate: `implementation/candidate_c024a_v1/gate_v1.py`, SHA256 `9725a263266f4e131019936e771b5df1cb100cd5715ec85c7dae90040f7e33f4`.

Only METHOD and the new unknown-K fallback change. Full input validation, contradiction checks, known-K routes, forced-atom construction, exact projection and bounded reject cache precede or bypass the insertion unchanged. The insertion is after failed atom compatibility; no trusted count is overridden.

For r atoms, tail ranges from 0 through 2^(r-1)-2. `side0=1|(tail<<1)` yields every proper nonempty atom mask containing atom zero exactly once. `full_mask xor side0` is nonempty and complementary. Thus the loop covers exactly 2^(r-1)-1 unordered atom bipartitions. Every compatible multiblock partition coarsens to one of these. Oneblock is valid on the already validated disjoint labels.

Every accepted split uses unchanged exact `witness`. It and oneblock are distinct, valid alternatives. Unique is emitted only after full loop exhaustion. The loop, witness, oneblock construction and emit poll deadlines. Existing resource exception handler returns unresolved without a selected provisional partition. Very large integer/range allocation can still hit resource limits; no polynomial-time or hard real-time guarantee follows.

Metrics: new search_nodes counts split iterations rather than recursive DFS nodes; these counts must not be described as identical units. complete_candidates still counts witness calls, including initial atom validation, but helper oneblock is not a witness call. New certificate routes/proof_basis/bipartitions_tested are explicit. Compact exhaustion metadata alone is not an independently replayable large-case proof.

No source correctness blocker found. Authorized independent small-family controls and, conditional on their passing and a frozen protocol, six-cell fresh-process A timing. No measured performance or promotion decision yet.

Separate B investigation authorized after cProfile showed D DFS cumulative 0.441 of 0.444 solver seconds and obstruction_m8 0.634 of 0.637 solver seconds. These are profile costs, not ordinary benchmark times. B must start from baseline independently, with no-K path unchanged and no extra heuristics.
