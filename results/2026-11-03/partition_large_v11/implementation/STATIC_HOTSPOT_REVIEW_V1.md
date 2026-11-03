# C011 static hotspot review and bounded optimization proposals

Baseline inspected read-only: C010 `unrestricted_solver_v2.py`, SHA-256
`4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502`.
No provider, benchmark, or generator was run. No timing or speedup claim is
made here.

## Hotspots visible from source

1. **Swap extraction scans the Cartesian product.** `_extract_atoms` compares
   every positive with every negative and scans their common word length,
   even though a hit must be one exact adjacent unequal swap. Cost is
   `O(|P||N|L)` in the worst case and scales poorly with sample count.
2. **Projection work repeats across phases.** `atom_partition_feasible`, lazy
   `reject(blockmask)`, and `_witness` each project positive/negative words
   separately. Enumeration can call `_witness` once per compatible partition;
   the same `(word, block)` projection may be rebuilt many times.
3. **Pair witness search repeats partition traversal.** For each symbol pair
   and each realized relation, `find_partition` searches again. The default
   output requires these witnesses, so output cannot simply be dropped. The
   output contains bare pair witness partitions; the representative carries
   projection evidence. Canonical partition-key deduplication can share
   internally recovered witness objects without changing the public schema.
4. **Fallback DP remains exponential.** `reject` is lazy, but each requested
   block mask projects every positive and negative word. Remaining-coverage
   pruning is sound and already present; further pruning needs a separate
   proof and independent counterexample search.

## Candidate order, pending theory approval

### A. Exact adjacent-swap hash lookup (first candidate)

Build a set of the deduplicated negative words. For each positive word, scan
each adjacent unequal position once, construct that exact one-swap string,
and perform an exact set lookup. Each hit records the positive, matched
negative, position and swapped symbols, then unions that symbol pair. Python
hash collisions are resolved by string equality; no digest is used as proof.
Every edge recognized by the current pairwise predicate is generated, and
every lookup hit replays that predicate, so this is a direct candidate for an
equivalent edge set. Keep a retained slow-reference checker in the audit,
not in production execution. Measure candidate count, lookup hits and
edge-set equality.

### B. Projection reuse for default output

Introduce an exact projection cache keyed by word ID/content and canonical
block mask, shared by atom feasibility, rejection masks and witness building.
Keep the output schema and ordering unchanged. First bound the cache to
actually requested masks; report hit/miss counts and peak memory separately.
For enumerated outputs, memoize constructed witness payloads by canonical
partition key and expand references into the unchanged default JSON before
comparing same-output runtime and byte counts.

### C. Two-letter anagram-interval must-links (theory gate required)

Candidate witness: positive `p` and negative `n` agree outside one contiguous
interval; both interval strings use only the same two distinct symbols `x,y`
and have equal counts of each. If `x,y` were owned by different factors,
reordering only x/y within that interval leaves each factor's projection
unchanged, so acceptance of `p` forces acceptance of `n`, a contradiction.
The extracted must-link is only `x~y`. The interval/signature finder must
verify exact boundaries, support size and both symbol counts before emitting
an edge. Do **not** infer ownership from the two mismatch letters alone:
`acb` versus `bca` is not an adjacent swap and the three-symbol mismatch
pattern does not certify a pairwise must-link. Have theory prove the exact
candidate rule and audit it against complete partitions before coding it.

## Bounded evaluation plan to preregister with audit

Use the frozen C010 no-K correctness set plus targeted repeated-word,
long-word, duplicate-label, swap-collision, two-letter interval and
three-symbol near-miss cases. Require exact edge/component equality where
applicable, full compatible partition sets, per-k/total/pair counts, and
independent replay of all witnesses before performance comparison.

Separate data volume (`|P|,|N|`), maximum/total word length, alphabet size,
negative coverage, atom count, and output size. Record candidates/lookup
hits, exact edges, projection calls and scanned characters, cache hits/misses,
mask counts, DP states/branches, recovered unique witness partitions and
serialized output bytes. Compare the unchanged C010 baseline and candidate on
identical frozen inputs/default expanded output in three fresh CLI processes;
include input read, preprocessing, witness construction, serialization and
capture wall time. Preserve baseline censored cells. Measure memory separately
or mark it unmeasured. No compact-output run is comparable to default output.

Implement only the first proof-cleared bounded candidate, then stop for the
independent correctness gate. Any mismatch or rejected idea remains a separate
versioned record; never edit C010.
