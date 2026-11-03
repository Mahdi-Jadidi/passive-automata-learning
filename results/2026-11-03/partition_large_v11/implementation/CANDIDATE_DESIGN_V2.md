# C011 bounded candidate design v2 (static only)

No provider source was changed or executed. This design supersedes the
unguarded generated-swap-only idea in `STATIC_HOTSPOT_REVIEW_V1.md` as the
proposed first must-link route. It is not approved for implementation until
theory proves the interval completeness lemma and master freezes the method.

## Candidate: indexed maximal two-symbol intervals

For each word, RLE-encode its symbol runs. Label each run transition by its
unordered symbol pair. Maximal consecutive transitions with the same pair
identify maximal two-symbol spans. Do not enumerate every substring or create
swapped strings by slicing. Precompute prefix/suffix rolling fingerprints and
per-symbol interval counts from runs. Each interval record stores length,
boundary/context data, its unordered pair and exact two-symbol counts, plus
prefix/suffix fingerprints.

Index positive records by the canonical key: interval length, boundary
context, symbol pair, both counts, and fingerprints for the unchanged prefix
and suffix. Query negative interval records with the same key. For every
candidate match, retain its entire collision class and verify exactly before
unioning: prefix equality, suffix equality, interval boundaries, exactly the
same two-symbol support, and equality of each symbol count. A rolling-hash hit
alone is never a certificate. Multiple positive contexts under a colliding
key are kept; none may overwrite another.

If verified positive `p` and negative `n` agree outside interval I and I has
support exactly `{x,y}` with equal x/y counts, then separating x and y leaves
each factor projection unchanged: inside I each projection retains only its
own repeated symbol, while all outside symbols occur in the same order. Thus
acceptance of p forces acceptance of n, contradicting labels. The certificate
must store p,n, interval endpoints, x/y counts, the pair, and verifiable
unchanged-prefix/suffix evidence. Legacy `swap_edge_witnesses` remains
adjacent-swap-only; new interval certificates go in a separate
`binary_interval_must_link_certificates` field. Pair counts and default
expanded witnesses remain unchanged.

## Required proof and adversarial review before coding

The key completeness obligation is that every sound minimal binary-anagram
interval relevant to a positive/negative pair is represented by the two
words' maximal RLE transition groups with a matching canonical key. Prove
that equal outside context forces alignment of the maximal span boundaries,
including word-edge and single-symbol boundary runs. If one maximal interval
record cannot represent a valid smaller mismatch interval, change the index
design or reject this optimization; do not silently enumerate O(L²) windows.

Check repeated transition patterns (`abab...`), unequal run lengths,
same-symbol boundary extensions, two separated binary spans, one-symbol
intervals, long common prefixes/suffixes, and three-symbol near misses such
as `acb`/`bca`. Only exact two-symbol support with equal counts is eligible.
Adjacent swaps are the length-two special case and must remain discoverable.

Rolling hashes accelerate lookup only. Exact verification handles collisions;
worst-case collision buckets may still cause quadratic comparisons. Report
that honestly. Pre-register counters for RLE transitions/spans, index records,
key candidates, collision-bucket sizes, exact verifications, accepted
certificates, and exact edge-set equality against a frozen slow reference.

## Retained low-risk candidate: exact projection reuse

After the interval rule is independently reviewed, a separate small version
may cache projections by canonical block mask and word identity across the
atom precheck, lazy rejection masks and witness construction. Cache only
requested masks; record hits, misses, scanned characters and memory. Memoize
identical canonical witness partitions internally but expand them back to the
same default JSON fields and ordering. No default compact output and no BDD
expansion in this cycle.

Do not time either candidate until theory proof, static review, source/input/
protocol readiness freeze, and auditor's correctness/performance protocol are
complete. Compare identical default output in fresh captured processes; include
whole-process time and output bytes, preserve censored baseline cells, and
separate input volume, word length, alphabet/atom count, negative coverage and
output size. No general speed claim follows from the index design.
