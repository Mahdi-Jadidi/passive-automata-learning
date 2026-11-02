# C010 final bounded static delta review — frozen v2

Disposition: **v1 spectrum blocker resolved; reviewed delta is suitable for
independent main-gate execution.** This is static clearance, not executable
acceptance or a speed claim. No provider executions or source edits by theory.
The failed v1 review/counterexample remain preserved separately.

Authoritative freeze: implementation/READINESS_V3.json. Reviewed source hashes:

* unrestricted_solver_v2.py:
  `4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502`
* unrestricted_cli_v2.py:
  `3140df25bab5d60c6c2705098029db9061e3c9d76743bf1dfd48d46aaf2d5eaa`
* API_PROTOCOL_V2.md:
  `0120261cec26de42a812a18760d0dea598b9085fb14a9e72f63da073bc3a9562`

## 1. B1 resolved: fixed-r Stirling spectrum

`_stirling_bell` now retains each Stirling row. The loop starts at S(0,0)=1
and updates nxt[k]=row[k−1]+k*row[k], then saves stirling[n]=row[:n+1].
The shortcut reads stirling[r][k] for k≤r and zero otherwise; its total
remains Bell(r). Thus it reports S(r,k), not Bell(k).

The former mathematical m=2 no-label counterexample now gives row [0,1,1],
total2 and spectrum1,1 by direct source derivation. For r=3 the derived row
is [0,1,3,1], total5. These are not executions by this reviewer. r=1 and
zero counts above r remain correctly covered. No independent gate result
is inferred from these hand derivations or from implementation preflight.

## 2. Swap preprocessing is now protected and polled

The original exact mismatch/swap logic was moved into `_extract_atoms`.
It polls per positive/negative pair, every1024 compared positions, and per
symbol while grouping components. `solve` calls it after `_check(deadline)`
inside a try catching _Stop and KeyboardInterrupt, returning unknown with
complete=false and count/spectrum/relations/witnesses omitted.

The exact-swap condition is unchanged: at most two mismatches, adjacent,
with reversed unequal letters. Therefore the sound must-link proof is not
weakened. The returned atom_for_symbol map replaces access to extraction's
local union-find in the shortcut and fallback; it is built from the same
atom tuples and preserves same-component membership.

Input validation/type checks and some setup remain outside protected regions;
cooperative checks are not an arbitrary-instruction interrupt or strict
whole-process time guarantee. CLI reading/serialization is outside solver
timing. These remain bounded documented scopes, not new change requests.

## 3. Exact kmax distinguished from atom-count bound

`k_max_upper_bound` remains r. New `k_max_compatible` is r on a feasible atom
shortcut, None for empty version space, and max{k:totals[k]>0} on a completed
nonempty fallback. This is exactly the largest supported sample count; it
does not identify nature's declared count. In the graph-empty doubled-pairs
example, the intended distinction is upper_bound6 versus compatible3.
The maximum is only evaluated after the zero-total return, so its support
is nonempty. Incomplete outputs do not claim either exact spectrum or kmax.

## Remaining scope and decision

The fallback count/pair recurrence, lazy masks, remaining-coverage prune,
witness retrieval and optional enumeration have no substantive mathematical
delta from the already reviewed v1 paths. Existing metric scopes are now
explicit in protocol v2: search_seconds excludes witnesses/listing, shortcut
zero search time is not zero work, and provider_seconds excludes final
representative construction. No metric-only or validation-zone churn is
requested. Unknown non-k fields do not enforce extra model restrictions.

Proceed with the frozen v2 independent full-set/count/pair/witness gate.
Its result, interruption checks and scale acceptance remain the auditor's
separate evidence. No new mathematical blocker found in this bounded delta.
