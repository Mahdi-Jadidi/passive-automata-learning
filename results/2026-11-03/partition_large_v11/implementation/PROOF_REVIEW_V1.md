# Independent proof review v1

## Scope and method

Independent static review of `theory/RLE_INTERVAL_INDEX_PROOF_v1.md` and the
matching C011 implementation. The reviewer did not edit or execute code. This
review is preliminary to the source/API hash freeze; final readiness remains
pending.

## Findings

1. **R1–R4 accepted under T1 assumptions.** Maximal-window enumeration,
   aligned interval/context keys, collision-safe record retention and exact
   verification support completeness for the T1 symbol-pair edge set.
2. **Union soundness accepted.** Exact context, interval support and count
   checks occur before union. Constant fingerprints can add candidates but
   do not create false edges or lose candidates, because collision records
   are retained.
3. **Certificate fields accepted for replay.** Positive/negative words,
   half-open interval, contexts, pair and per-symbol counts allow independent
   verification.
4. **Completeness boundary:** this proves discovery of every T1 symbol-pair
   edge; it does not enumerate every witness or all possible semantic
   must-links. The exact coarsening search, not a missing index edge, governs
   the answer.
5. **Python object aliasing:** nested pair-witness partition lists may be
   shared in the returned object. The protocol now tells callers to treat
   results as read-only; JSON serialization still emits all rows and fields.
6. **Timer boundary:** `provider_seconds` is recorded before final witness
   construction. The protocol documents this inherited C010 behavior and
   requires external whole-process timing for comparisons.

No counterexample was found by static reasoning. This is not a runtime
correctness result, collision experiment, or performance measurement.
