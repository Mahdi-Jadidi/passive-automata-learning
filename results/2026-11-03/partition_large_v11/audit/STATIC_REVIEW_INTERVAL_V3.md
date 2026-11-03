# C011 independent static review — frozen solver v3

## Scope and hash binding

Read-only review of the candidate frozen in `implementation/READINESS_V5.json`.
No provider, solver, test, smoke, oracle, benchmark, or memory code was run.

| Artifact | SHA-256 | Binding |
|---|---|---|
| `implementation/unrestricted_solver_v3.py` | `42726e740198787645783acefd1fa06f6490ec16d609ef07d22cbfafd34a00fa` | Matches readiness |
| `implementation/unrestricted_cli_v3.py` | `169d7d468a5e3d8a0ba93b686ccb2b058ba231fa1b8e85150d5840df4fec563c` | Matches readiness |
| `implementation/API_PROTOCOL_V3.md` | `73a89169040d0d2bfe678f9d4f54dbd214de700c1e791364449dbc289eb792f7` | Matches readiness |
| `implementation/READINESS_V5.json` | `89c06f317213fa72f2c061927b3ae69b2c246a3ce42f2190310ca350e47d64fc` | Current readiness |
| `implementation/unrestricted_solver_v2.py` | `699f88004cc12201642eccb801fde5a0f6a720b063815a99032cac078fa29ba0` | Prior reviewed source |
| `implementation/unrestricted_cli_v2.py` | `842dd27b149e1b1aade9ff2692f9ab25191259b027a2414c28edbb2d62e2471c` | Prior reviewed CLI |

The protocol, source, CLI, and readiness hashes in V5 agree. Readiness V5
records execution as not run and explicitly identifies the v2 `None` witness
failure as the superseded issue.

## Delta from v2

The source diff is limited to the same-block and different-block witness
branches in pair-row construction (`unrestricted_solver_v3.py:713-721`). Each
branch now stores the result of `find_partition` in a local candidate and
calls `intern_partition` only when that candidate is not `None`. The loop
continues to later `k` values while the requested witness is still missing.
The CLI delta is only the import and call changing from
`unrestricted_solver_v2` to `unrestricted_solver_v3`; the API document updates
the module name. No other solver behavior changed in the source diff.

## Prior counterexample and witness completeness

For alphabet `{a,b,c}`, positives `{ε,abc}`, and negative `{a}`, the singleton
atom partition is infeasible. Exact compatible partition counts are one for
`k=1`, two for `k=2`, and zero for `k=3`. For `(a,b)`, both same and different
relations occur overall, but a different-block witness occurs only at
`k=2`. In v2, the `k=1` constrained search returned `None` and that value was
passed to `_partition_key`, causing a `TypeError` before reaching `k=2`.

In v3, `candidate is not None` prevents interning the absent `k=1` witness.
Since the corresponding `*_w` remains `None`, the loop reaches `k=2` and
stores the witness when found. The same guard handles same-block witnesses
whose first compatible block count cannot realize that relation.

The guard does not skip a valid witness by itself. `same` and `diff` are
aggregate counts over all compatible partitions; a positive aggregate means
some `k` has a witness. `find_partition(k, ...)` enumerates canonical
anchor-containing blocks, prunes only with the unconstrained compatible-DP
count, and enforces the requested pair relation through `decided`. Thus a
valid relation witness at that `k` remains reachable; a `None` result at an
earlier `k` is correctly treated as “not available at this k,” not “none
exists globally.” This is static reasoning, not runtime evidence.

## API and deadline review

- The CLI parses `--seconds` as a finite nonnegative duration, forms an
  absolute `perf_counter()` deadline, calls the v3 module, and maps
  `incomplete` to exit code 3 (`unrestricted_cli_v3.py:10-31`).
- The API contract continues to specify `incomplete`, `complete: false`, and
  null exact counts/relations on cooperative timeout or interruption. The
  solver checks deadlines in the constrained recursive search; the outer
  handler still catches `_Stop` and `KeyboardInterrupt` and returns the
  documented incomplete result (`unrestricted_solver_v3.py:659-691, 765-772`).
  The new guard does not catch or suppress either signal.
- Input/deadline validation remains before the protected search, as documented
  in the inherited contract. This review found no delta-related API or
  deadline regression; it does not certify hard real-time interruption.

## Decision and remaining limits

**The v3 source delta is statically cleared for the preregistered correctness
gate.** The previous v2 blocker is fixed without an apparent lost-witness
path. This is not runtime correctness acceptance; the frozen family oracle,
certificate validation, deadline controls, and subsequent performance gates
remain necessary.

The previously documented limitations are unchanged, including unbounded
entry-count `lru_cache` tables in fallback search and the need to measure
whole-process behavior separately. No v3 execution or performance result is
claimed here.
