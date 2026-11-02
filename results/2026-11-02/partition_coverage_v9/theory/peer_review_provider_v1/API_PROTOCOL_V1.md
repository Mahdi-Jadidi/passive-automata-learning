# C009 ownership API v1

## Input

```json
{"alphabet":["a","b","c"],"positive":["","ab"],"negative":["a"],"allowed_k":[1,3]}
```

`alphabet` is a nonempty list of unique one-character identifiers. Positive
and negative are exact complete-word labels; `""` is epsilon. Optional
`allowed_k` is a trusted, nonempty list of integers in `1..|alphabet|`; if
omitted, all block counts are allowed. To ask for known k use `[k]`. A
contradictory label, foreign symbol, malformed constraint, or legacy `k`
field is `invalid_input`. A fully searched empty version space is
`model_inconsistent`, not a vacuous ownership identification.

## API and CLI

Python API: `ownership_solver_v1.solve(data, allowed_k=None, deadline=None,
enumerate_partitions=False)`. `deadline` is an absolute
`time.perf_counter()` value. The CLI accepts `--seconds N` as a cooperative
duration and `--enumerate` to request the full partition set.

From the workspace root:

```powershell
& 'C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 'results/2026-11-02/partition_coverage_v9/implementation/ownership_cli_v1.py' 'results/2026-11-02/partition_coverage_v9/implementation/ownership_example_v1.json' --seconds 30
```

## Result semantics

- `identified_unique_partition`: exactly one compatible partition.
- `partial_ownership_identification`: two or more compatible partitions;
  each symbol pair is `forced_same`, `forced_different`, or `ambiguous`, with
  a compatible partition witnessing every relation that actually occurs.
- `model_inconsistent`: no partition satisfies the labels and allowed k set.
- `unknown`, `complete:false`: deadline/interruption prevented completion;
  exact counts, pair relations and universal claims are omitted.
- `invalid_input`: malformed data/constraints.

The representative result includes a replayable direct projection witness:
every negative is rejected by at least one factor. Pair relation witnesses
are complete compatible partitions, so they can be checked against the same
projection criterion. With `--enumerate`, all partitions are returned, or the
whole request is marked incomplete; the CLI never silently truncates.

## Exact algorithm

For each nonempty symbol block B, precompute a bit mask of negatives whose
projection onto B is missing from the positive projection set. A compatible
partition is a canonical exact cover: choose the least remaining symbol for
the next block and require the union of block rejection masks to cover every
negative. Memoized DP state is `(remaining_symbols, covered_negatives,
blocks_left)`. Each result stores the exact number of completions and, for
every symbol pair, the number of completions in which the pair shares the
chosen block. Summing these counts across allowed k gives the exact same/diff
counts. Witness partitions for each realized relation are recovered by
following DP branches; no Bell-partition family is materialized unless
explicit enumeration is requested.

This search can be exponential in alphabet size and output size. It is not a
polynomial-time claim. A unique compatible partition is still a sample-level
conclusion; physical ownership follows only if the true system is in the
assumed model class. Time metrics are scoped counts/timers, not speed claims.
