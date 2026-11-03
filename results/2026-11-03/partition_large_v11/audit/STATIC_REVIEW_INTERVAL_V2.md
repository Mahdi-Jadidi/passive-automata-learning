# C011 independent static review — frozen solver v2

## Scope and frozen inputs

This is a read-only review of the candidate named in `READINESS_V3.json`.
No provider, test, smoke, oracle, benchmark, or memory code was executed.

| Artifact | SHA-256 |
|---|---|
| `implementation/unrestricted_solver_v2.py` | `699f88004cc12201642eccb801fde5a0f6a720b063815a99032cac078fa29ba0` |
| `theory/RLE_INTERVAL_INDEX_PROOF_v1.md` | `7b59106887d99abce6102af22d439061a51f2e8cbe049d292db92e284f30f1f9` |
| `implementation/READINESS_V3.json` | `e7ddabdf87b08f309866dffb73d584d7a664b45265c1c601fcd9e25159b7df9c` |

The solver hash matches the requested v2 candidate. This verdict applies to
that exact source only; later readiness/source versions were not reviewed.

## Decision

**Blocked for the correctness gate.** The RLE interval extractor and its T1
certificates appear sound under the stated model, but the exact fallback can
raise an uncaught `TypeError` while trying to produce a pair-relation witness.
The following reasoning establishes a concrete triggering input without
executing the solver.

Use alphabet `{a,b,c}`, positives `{"", "abc"}`, and negative `{"a"}`.
The full singleton atomization is incompatible: on the negative `a`, the
projection on `a` is present among positive projections and both other
projections are epsilon, also present. In the exact fallback, the compatible
partition counts by number of blocks are one partition for `k=1`, two for
`k=2`, and zero for `k=3`: `abc` as one block rejects `a`; at `k=2`, `ab|c`
and `ac|b` reject it, while `a|bc` accepts it; all singletons accept it.
Thus for the pair `(a,b)`, the aggregate `same` and `diff` counts are both
positive, but a different-block witness exists only at `k=2`.

At `implementation/unrestricted_solver_v2.py:713-717`, witness search scans
`k` from 1 and invokes `intern_partition(find_partition(k, ai, aj, False))`
whenever `totals[k]` and the *aggregate* `diff` count are nonzero. At `k=1`,
`totals[1]` is nonzero but no pair-different partition exists, so
`find_partition(...)` returns `None`. `intern_partition` passes that value to
`_partition_key` (`:454-455`), whose loop at `:146-150` attempts to iterate it.
That raises `TypeError` before the valid `k=2` witness can be found. The same
pattern can occur for same-block witnesses when the first compatible `k`
cannot realize the requested relation. This is an implementation blocker,
not a counterexample to the mathematical model or interval theorem.

## Findings that passed static reasoning

1. **RLE interval coverage (source `:330-374`; proof R1-R3).** The source
   groups adjacent RLE transitions with equal unordered symbol pairs and
   records the whole run-spanning interval. This enumerates maximal binary
   intervals that contain both symbols. In particular, `aabb` and `bbaa`
   each have two consecutive `ab` transition labels and produce the intended
   full interval; the non-alternating repeated-run case is not omitted.
   The proof's R3 extension argument aligns a T1 witness to matching maximal
   windows with the same exact boundaries, symbol counts, and outside text.

2. **Sound interval edge and certificate (source `:228-259`, `:376-411`).**
   A candidate positive and negative must first share the coarse indexed key
   and exact outside prefix/suffix. `_verify_interval` then checks equal
   lengths, distinct complete words, two-symbol support throughout the
   interval, and both exact per-symbol counts. `_validate` rejects
   contradictory labels before indexing. Under the independent-factor model,
   every separate factor sees the same projection on the two words, so a
   positive/negative label contradiction forces the two symbols to share a
   factor. The emitted certificate carries the words, interval, contexts,
   pair, and counts needed for replay.

3. **Collision handling (source `:192-215`, `:228-239`).** The positive index
   retains all records for each fingerprint key rather than one arbitrary
   representative. Negative lookup scans the bucket; exact context and
   interval checks precede union. A fingerprint collision can increase work
   but cannot create a false edge or hide a later correct record. The planned
   constant-fingerprint runtime control is still needed to validate that
   implementation behavior empirically.

4. **Exact fallback logic, apart from witness construction.** For each atom
   block, `reject` marks precisely the negatives whose projection is absent
   from the positive projection language. The DP accepts a partition exactly
   when the union of its blocks' rejection masks covers all negatives.
   Since extracted edges are sound must-links, enumerating atom coarsenings
   preserves the answer family. The witness-search crash above prevents this
   candidate from reliably returning the promised complete result in all
   such cases.

## Remaining caveats and gate conditions

- Extractor completeness is specifically completeness for the documented T1
  binary interval witness rule, not for every possible semantic must-link or
  every witness. The exact fallback remains responsible for the full family.
- The two `lru_cache(maxsize=None)` tables in the fallback are unbounded by
  entry count or bytes. This is a memory-risk caveat to measure and report;
  it is separate from the deterministic witness-construction blocker.
- The review does not establish runtime correctness, constant-hash behavior,
  deadline behavior, or performance.
- A corrected candidate must be versioned separately. It should only
  intern a non-`None` witness and continue searching later `k` values when an
  earlier compatible `k` cannot realize the desired pair relation. The
  frozen v2 source and this blocker record should remain unchanged.
