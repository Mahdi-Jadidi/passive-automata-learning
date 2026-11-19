# V47 exact polynomial fixed-partition teacher

The frozen V46 checkpoint is tagged `v46` at `bc915ffd5e591202b0ab8ffd55342a004c791138`. V47 uses a separately versioned entry point on `codex/v47-polynomial-teacher`. The V45 teacher, its manuscript and V46 evidence stay at their original paths.

V47 checks compatibility by testing membership in the finite projected positive language of each block. It does zero DFA enumeration. The [proof ledger](PROOF.md) gives the criterion, the code invariant, equivalence to the completed V45 verdict on the fixed-partition interface, polynomial complexity, and the composition proof. The outer search, cuts, and optimum consumer keep the same mathematical contract. Bounded local behavior relations remain outside the new teacher interface.

## Results

| Evidence | Outcome |
|---|---|
| Frozen 2,261-case corpus at 0.25 seconds each | 2,259 checked optima and two checked infeasibility results. All matched reference. The V46 V45 run completed 1,247 of these inputs. |
| Previous 158 outer-audit runs | 121 checked optima and 37 checked infeasibility results. All reference matches. Six production master maxima and six cuts checked independently. |
| Vertex Cover reduction | All 103 graph-derived samples matched brute-force minimum covers via k = n−τ+1 and passed certificate replay. |
| Fixed-partition teacher | 4,374 direct comparisons over all labelings of seven two-symbol words and both partitions. An injected interruption propagated without returning a decision. |
| Ten fixed cases, fresh processes, 2-second cap per solver and checker | V47 completed 10/10. V45 completed 3/10 and left seven incomplete. V47 solve times ranged from 0.195 to 45.262 ms. |
| Ordinary interactive fixture, matched sequential fresh processes, two repetitions | Median solve time V45 4.137 s and V47 7.528 ms. All four optimum certificates accepted. Process startup excluded from solve times. |
| Known-optimum clique stress, 2-second cap | K10, K12 and K16 exhausted the cap during the internal certificate check. K20 exhausted it during master search. All returned `INCOMPLETE`. |

On `overlap_8`, the new solver took 45.262 ms, of which 0.152 ms was in the teacher decision and 0.429 ms in the full set of teacher calls including retrieval of projections. This matched trial and the previous V45 uncapped trace have distinct measurement protocols. The matched fixture timings demonstrate the gain on those fixtures. The stress tests show that the remaining costs can be certificate checking and master search.

## Complexity boundary

General exact optimization remains NP-hard because the maximum compatible block count computes minimum Vertex Cover even when the sole negative is ε and every positive has length two. A worst-case polynomial total bound for arbitrary declared alphabets would imply P=NP. With a fixed alphabet size bound, the combined procedure is polynomial in the length of the encoded sample. See [the reduction and proof](PROOF.md).

## Reproduction

Use Windows x64 CPython 3.12 with the committed Glucose3 vendor package. Run comparisons sequentially in fresh processes. For API use, put this folder first on the import path and call `optimizer_v47.solve_optimal(D, limits)`. The consumer is the frozen V45 `verify.verify_optimal`. The current flat-module layout requires a fresh interpreter when switching versions.

```powershell
$d = 'results/2026-11-19/polynomial_teacher_v47'
& $py -B "$d/evaluate.py" --out new-v47-evidence
& $py -B "$d/check.py" new-v47-checks
```

`check.py` replays traces from the archived outer suite. [Run settings and hashes](evidence/environment.json), [solver summary](evidence/summary.json), [matched raw trials](evidence/matched.jsonl) and [independent checks](checks/summary.json) link to the retained evidence. Valid field trials under whole-trace AND labels remain at zero.
