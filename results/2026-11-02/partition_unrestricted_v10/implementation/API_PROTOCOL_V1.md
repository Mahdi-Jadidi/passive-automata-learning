# C010 no-K API, candidate v1

## Input

```json
{"alphabet":["a","b","c"],"positive":["","abc"],"negative":["a"]}
```

The input has exactly the needed information: a nonempty list of unique
one-character symbol IDs and positive/negative lists of complete words.
`""` is epsilon. Symbols outside the alphabet and contradictory labels are
invalid. Any `k` or `allowed_k` key is rejected; the solver never silently
uses an externally supplied count. With no count information all values
`1..|alphabet|` are considered.

## API and CLI

Python API: `unrestricted_solver_v1.solve(data, deadline=None,
enumerate_partitions=False)`. `deadline` is an absolute
`time.perf_counter()` value. CLI options are `--seconds N` and `--enumerate`.
The standard library is sufficient.

```powershell
& 'C:/Users/Mahdi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -X utf8 'results/2026-11-02/partition_unrestricted_v10/implementation/unrestricted_cli_v1.py' 'results/2026-11-02/partition_unrestricted_v10/implementation/unrestricted_example_v1.json' --seconds 30
```

## Complete-result semantics

- `identified_unique_partition`: exactly one sample-compatible partition.
- `partial_ownership_identification`: a complete family with multiple
  partitions; every symbol pair has exact counts and same/different witnesses.
- `model_inconsistent`: no compatible partition (should be unreachable for
  consistent labels in this unrestricted class because the one-block model
  fits every finite sample).
- `unknown`, `complete:false`: interrupted or deadline-limited; no exact
  count, spectrum, pair relation, or uniqueness claim is returned.
- `invalid_input`: malformed data or an attempted external count constraint.

By default the result includes exact total and per-k counts, a representative
partition with negative-projection rejection evidence, forced-same/ambiguous
pair relations, and witnesses. Since all k are allowed and a one-block model
always exists, forced-different pairs cannot occur. `--enumerate` returns the
full family; it is never silently truncated.

`k_max_upper_bound` is the number of contracted atoms, not an estimate of the
true component count. Physical ownership is fully identified only when the
admissible family is a singleton; otherwise partial forced-same information
may still be useful. In particular, a unique finest atom partition is not
mistaken for unique physical ownership.

## Exact method and limits

Replayable adjacent-swap positive/negative pairs produce sound must-link edges.
Their connected components are atoms and every compatible partition must
coarsen them. The solver first checks whether the atom partition itself fits
the labels. If so, every coarsening fits; Stirling/Bell counts and constructive
same/different witnesses avoid family enumeration. Otherwise canonical DP
searches exact atom coarsenings. Rejection masks are computed lazily. It prunes
only when `covered OR R(remaining_atoms) != all_negatives`, because merging
all remaining atoms gives an upper bound on future rejectable negatives.

The worst case remains exponential in atom count and output size. This is not
a polynomial-time or general speedup claim. `unknown` is non-final. Metrics
record masks, DP states/branches and scoped times; witness-recovery and CLI
I/O are not represented by a complete end-to-end timing claim.
