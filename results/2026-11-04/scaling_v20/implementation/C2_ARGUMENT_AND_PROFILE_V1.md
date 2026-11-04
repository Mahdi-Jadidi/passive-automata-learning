# C2: profile-motivated exact native Unicode projection

Second and final optimization slot: C1 plus chunked str.translate deletion.
No generator, new search pruning, alternate output contract, third direction,
hidden state/count input or prior-source edit is introduced.

## Actual complete baseline profile

Auditor capture20261104T115446.210146Z_2f43e52a24 profiled frozen C018 on
A with explicit knownK4, soft20/hard25. It returned certified_unique through
compatible_forced_atoms, with4mask computations and0search nodes. Counted
input characters4066861; projected characters16267444; swap pairs264708.
The solve cumulative profile time was14.6496358seconds. project own time
9.644482 and cumulative11.3012277 across4116calls dominated that completed
profile; list.append own time was1.5889588. Counter own time was0.9118988.

Read-only sources under ../audit/profile_baseline_A_K4_v1/:

| File | SHA-256 |
|---|---|
| receipt.json | `d28977b3e76a3ca761ac45965e132410f352054c3e08496743f35ac9d4ad57b7` |
| functions.json | `82aa324bd80cfb1f0cc382fb7ce6e9637fa79ec578677f01d90c292d322570f9` |
| result.json | `5fbc14b0dee4c13d081112c7972462f59b0fd3ce0b27d6af06a9c0bf453039de` |

Input hashd4def66ffc40bbd0a383382008171622e4fde36fe1122c9b46d629e60f3295d3;
baselinec288448f4a11849f74293b13201fdc578a79e6fbbe24165684807bd32ceeb83d;
profiler42af21debce9e878584c322ed361221de558f86fa287e8f9760d46fbc40e4969.
The process-profile receipt14.7437969seconds and auditor capture overhead are
different boundaries. Both baseline profiles cost24.3813691seconds in the
auditor budget. These are diagnostic cProfile runs, NOT speed measurements.
The earlier B5s profile did not reach projection and is preserved separately.

## Exact projection proof

All input words have already passed complete alphabet validation before any
reject-mask call. For a selected symbol block B within alphabet Σ, construct
the mapping ord(a)->None for every a in Σ\B. No mappings insert or replace
characters. Every character in B is absent from the mapping and remains
unchanged; every character outside B is deleted. Hence str.translate returns
exactly the original order-preserving projection onto B.

This applies to arbitrary one-code-point Unicode symbols, including BMP,
non-BMP, combining code points and null characters. No ASCII assumption,
normalization, regex metacharacter interpretation, byte encoding, approximate
hash comparison or target substitution is involved. It is essential that the
full existing validation remains in front of this operation: otherwise a
foreign character not present in the deletion mapping would survive.

Projection is a homomorphism: projection(w1...wj)=projection(w1)...projection(wj).
Therefore projecting disjoint consecutive at most16384-code-point chunks and
joining their results equals the reference character loop exactly. No chunk
boundary splits a code point. One temporary input chunk has at most64KiB UTF-32
payload (object/Counter/output overhead is separate). A single deletion table
is constructed per exact uncached block mask and reused for all P/N words in
that mask computation. Native join may allocate a full word projection, as
the reference did; no constant whole-process memory bound is promised.

The same positive projection sets and every exact negative rejection bit
follow. Thus atom feasibility, all complete candidates, witness rejection
indices, search order, known-K filtering, final status and selected/alternative
partitions are unchanged on completed runs. C1's exact Parikh filtering and
order/index guarantees remain unchanged. No false must-link or unsafe partial
negative pruning can be introduced by this local replacement.

## Polling/counters and independent gate

Each chunk polls before and after native translation. Projection character
metrics add the input chunk length after successful translation: completed
logical character totals match the reference. Interrupted progress may differ,
and no unfinished decision is promoted to final. Table-building polls per
alphabet symbol; join is followed by a poll. Native translate/join/allocation
remain non-preemptible operations requiring the outer hard timeout.

projection_chunks counts completed native chunk calls. deletion_tables_built
counts tables fully built on reject-cache misses, possibly more than completed
block_masks_computed when an interruption follows. Existing compact witnesses
and all other metrics keep their meanings. Method and these diagnostics/timers
are the expected nonsemantic differences.

Static review must check the exact C2-minus-C1 diff. Runtime gate must cover
independent small complete families; empty/duplicate/malformed/late-invalid
data; arbitrary Unicode and undeclared non-BMP characters; source blocks
containing all/no observed symbols; projection chunk boundaries16383/16384/
16385; known-K/graph-empty unique and ambiguous controls; and unresolved/hard
cutoff semantics. Independently replay every available witness under the
original observations. Only after that gate and master approval may the
auditor run the existing same-input/default-output six timing cells.

The extra table/chunk/join work may regress short cases and counting remains
untouched on cases whose precheck dominates. No win is claimed before fresh
unprofiled captures. After this candidate's measured comparison, stop at the
two-slot/plateau boundary rather than add another optimization or new fixtures.
