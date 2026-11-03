# Static counterexample: pair witness absent at first feasible k

## Status and provenance

This is a mathematically derived, unexecuted counterexample to the v3-parent
fallback witness-recovery loop. It was reported during static review. No result
or log is fabricated; no provider process was run. The exact source example is
the input below, and its behavior follows by enumerating the five set
partitions of a three-symbol alphabet on paper.

## Input

```json
{"alphabet":["a","b","c"],"positive":["","abc"],"negative":["a"]}
```

## Hand derivation

A partition is compatible exactly when the block containing `a` also contains
at least one of `b` or `c`: if `a` is a singleton, its projection of the
negative word is `a`, which is already among that factor's positive
projections `""` and `"a"`; if a block contains `a` plus `b` or `c`, its
positive projection of `abc` has length at least two and the negative
projection `"a"` is rejected.

The compatible partitions are therefore:

| k | partition | relation of b and c |
|---:|---|---|
| 1 | `{abc}` | same |
| 2 | `{ab}|{c}` | different |
| 2 | `{ac}|{b}` | different |

Thus the total family has three partitions; `b,c` are ambiguous overall, but
there is no `b,c`-different witness at k=1. In the old fallback loop, the
aggregate `different_partition_count` is positive, so it calls
`find_partition(1, b, c, False)`. That correctly returns `None`, but the
caller immediately passes `None` to `intern_partition`, whose key-building
iteration raises `TypeError`. The fallback cannot produce the promised
complete output for this input.

## Repair recorded in candidate v3

For each same/different witness search at each k, retain the result only if it
is not `None`; continue searching later k values otherwise. This guard is
applied symmetrically to same and different witnesses. The exact v2 source is
preserved and this issue is not represented as an observed runtime failure.

## Required verification

The v3 implementation must be compared with the exact baseline on the full
partition set for this input and all prior controls. Independent witness
replay remains required. Until then, this artifact documents the static
counterexample and repair only.
