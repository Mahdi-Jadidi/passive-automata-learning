# Structural hybrid — frozen for source review and separate audit round

Experimental `solve(data, *, max_candidates=None)` chooses C030 singleton certificate, then graph component certificate, then DP fallback. The dispatch is based solely on exact structural compatibility tests, never timing case IDs. Explicit budgets go straight to frozen C028. It checks SHA-256 of all five dependency files at import; see `PROOF.md` for branch-by-branch equivalence and caveats. No existing candidates, audit data, or public defaults were altered. It duplicates preprocessing on fallback and can be slower than DP; import/hash overhead is outside solve-only timing. No measured speedup is claimed.

Local smoke: `py results/2026-11-13/exact_candidates_v33/candidate_dp/hybrid/smoke.py` (Python 3.14.6) compares full C028 output for seven focused records with six budget values and checks that singleton, graph and DP branches are each exercised. Captured `SMOKE_OUTPUT.txt`. This is not the official independent audit. The locked V33 corpus and existing original raw timing data must remain unchanged; any hybrid evaluation is a separately identified appended round after independent review.

| Frozen file | SHA-256 |
|---|---|
| `candidate.py` | `6377CCD75281567BE11AF5820AE52668612A069240C31D2A5AEE0CF4F1022063` |
| `PROOF.md` | `27094F9595D2F04034718667712098839B8D882C970491C81E297E5C348BB219` |
| `smoke.py` | `6CA6879A6FF59271E534C1506867F75739ABBBB335BCAC8E61F952D3286483BB` |
| `SMOKE_OUTPUT.txt` | `2C4C6ABBAC09474F09BFA42176BA83692E80802E8EAF35BC44DE8FA6270CCBDC` |

Biggest overlooked issue: mandatory components give only necessary constraints; Bell counting is valid only after testing the component partition itself. Resource exhaustion, helper hash mismatch, output ordering and full C/O witness requirements remain explicit in the proof.
