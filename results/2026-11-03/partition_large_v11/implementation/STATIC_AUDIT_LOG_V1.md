# C011 implementation audit log v1

## Status

This is a versioned record of static candidate development. No solver or CLI
execution, smoke test, benchmark, or provider capture has been performed for
C011. Candidate correctness and API equivalence remain unverified.

## Preserved rejected attempt: materialized adjacent swaps

The first implementation sketch generated swapped words by slicing at every
adjacent position. It was rejected before capture because repeated string
construction can copy O(L) characters at O(L) positions per word. This
approach and rationale remain in `STATIC_HOTSPOT_REVIEW_V1.md` and
`HANDOFF_TO_MASTER_V1.md`; it has not been erased or reported as a failed
runtime experiment.

## Current candidate

`unrestricted_solver_v1.py` indexes maximal RLE two-symbol intervals by
context fingerprints and verifies every candidate exactly before adding a
must-link. It retains exact C010 atom-coarsening search, adds bounded projection
reuse, and keeps adjacent-swap certificates distinct from interval
certificates. The theory proof is documented in
`../theory/RLE_INTERVAL_INDEX_PROOF_v1.md` and is awaiting independent review.

## Static repair notes

Before the source freeze, static inspection found and corrected two draft
defects: a duplicate RLE extraction call in the negative-word path and a
mis-indented pair-witness initialization in the fallback relation loop. Added
deadline polling to RLE transition/window loops and bucket counting. These
were pre-freeze source-edit defects, not observed runtime failures; the earlier
working copy is not being presented as an evaluated attempt.

## Outstanding gates

1. Receive independent proof and implementation review; record all findings,
   including rejected concerns and dispositions.
2. Freeze source, CLI, example, protocol and their hashes.
3. Only after explicit correctness gate clearance, run preflight and compare
   the complete partition families, output witnesses, collision behavior,
   interruption semantics and fresh-process costs against C010.

## Independent review disposition (pre-freeze)

The independent proof review accepted R1–R4 under T1 and found no
counterexample, while limiting completeness to T1 edges (not all semantic
must-links). It also identified shared mutable witness lists and the inherited
`provider_seconds` boundary; the API now documents read-only result handling
and requires external whole-process timing.

The implementation review confirmed collision safety and found no syntax or
control-flow defect by inspection. Its interruption-status suggestion was
resolved in favor of the frozen C010 API: `unknown` with `complete:false`
continues to mean incomplete, and the CLI keeps exit code 3 for `unknown`.
Certificate context copying now polls the deadline and counts copied
characters. `_partition_from_masks`, projection/witness traversal, DP subset
loops, and result pair-row loops now poll cooperatively. The projection LRU
remains bounded by 4096 entries rather than bytes; this limitation and the
empty-block counter bypass are explicit in the API protocol. Input validation
remains inherited and precedes deadline checking.

A first review message raised possible loss of multiple positive swap witnesses;
static reconciliation with the old predicate shows one exact positive string
per validated negative string and position (the positive set is deduplicated),
so the exact-context lookup and first verified hit preserve the legacy witness
set. This disposition still requires frozen-corpus comparison.

## Post-review contract adjudication

The frozen C010 API used `unknown`, but the C011 user-approved plan explicitly
requires the literal `incomplete` status. The first readiness draft retained
`unknown`; the hash-bound implementation reviewer correctly blocked it as a
plan deviation. The current candidate now returns `incomplete` with
`complete:false`, and the CLI maps that status to exit code 3. This is an
intentional status-value change from C010; all incomplete-result semantics are
otherwise retained.

The reviewer also identified an unpolled scan for `total_input_characters`.
That scan now runs under the same deadline/interruption handler as preprocessing
and polls once per input word. Input validation itself still precedes deadline
checking, as inherited from C010.
