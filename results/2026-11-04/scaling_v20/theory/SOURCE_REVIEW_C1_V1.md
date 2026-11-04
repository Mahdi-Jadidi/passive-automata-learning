# C020 C1 v1 — hash-bound static review

Decision: **STATIC CLEARANCE FOR INDEPENDENT CAPTURED CORRECTNESS GATE**.
No blocking source or mathematical defect found in the reviewed delta. No
provider execution/import, timing or frozen-source edit by theory. Paper
goal remains paused. This is not runtime acceptance or measured improvement.

Verified implementation/READINESS_C1_V1.json bindings:

* candidate_c1_v1/gate_v1.py:
  `334772356836e5dcc5376af756518125c94cf8df3119b9a0492bff86f7b7d8f0`
* candidate_c1_v1/partition_gate_v1.py:
  `60a5865a1846ed060b0954eef9cc7937d8709cb2a1aec4a4dbfc0925fac27758`
* candidate_c1_v1/PROTOCOL_V1.md:
  `5e316fa99ee4c48e6b0acc1365941af114fd99cbfde0e897f1e106a978f8e008`
* C1_ARGUMENT_V1.md:
  `9bffc1b30443d0d9d76a16aaad03a78acefd250ee070fa34190aead2d04c746b`

The actual independent diff against frozen C018 gate
`c288448f4a11849f74293b13201fdc578a79e6fbbe24165684807bd32ceeb83d`
was inspected. It agrees with the saved change description: new exact word
signatures, negative graph buckets, method/diagnostic metrics only. Count
validation, unary predicate, known-K, exact swap comparison, DSU, atom
feasibility, projections, reject cache, RGS and output remain unchanged.
CLI is byte-identical to C018. diff exit1 is expected file difference,
not an executed scientific failure.

## Exact signatures and validation

Each signature is `(len(word), tuple(sorted(counts.items())))` from the
fully validated chunk-accumulated Counter. Entries are positive exact counts
only; absent symbols are implicit zero in the same fixed validated alphabet.
Thus equal keys mean equal full Parikh vectors. Unicode characters are
unchanged Python code points, not bytes or normalized spellings. Epsilon
has length0 and empty entries. Sorting creates a new list/tuple and does not
reorder counts.items(), so the baseline unary witness's first-occurrence
selection is preserved.

Positive/negative signature arrays have one element per original list entry,
including duplicates, and retain alignment with their respective indices.
No sample is removed from subsequent mask/witness logic. Foreign symbols,
non-string late entries and contradictory valid labels retain original full
validation priority. Empty P/N, implicit-zero and presence multiplicities
are unchanged. Signatures are computed even on inputs later handled by a
unary/known-K shortcut; this is extra cost, not a hidden skip of validation.

## Graph filtering and forest equality

Every adjacent swap preserves all counts and length, so no baseline edge
lies outside its positive signature's exact negative bucket. Inside a bucket
the original exact mismatch-count, adjacency, reversal and unequal-symbol
tests are unchanged. Signature agreement by itself never unions symbols.
Dictionary key hashing is followed by exact tuple equality automatically;
colliding unequal tuples are not conflated or discarded.

Negative groups append `(ni,n)` in the original N order, duplicates included.
The positive outer loop keeps original P order. Removed comparisons are only
nonedges and could never change DSU. Induction over retained edge order gives
the same successful-union forest, witness indices and final components as
the baseline on completed uninterrupted computation. Therefore this particular
implementation preserves deterministic certificate choices as well as feasible
families/statuses, modulo method/timing/diagnostic fields. This stronger claim
depends on those explicitly checked ordering properties; it is not a general
claim for all future indexes.

## Deadline, memory and reporting limits

Signature sort has before/after polls, bucket build and pair loops poll, and
all work is inside the existing protected solve region. Native sorting/hash/
allocation are still not instantaneously preemptible; external hard timeout
remains required. Equal budgets may lead to different completion trajectories.
Any incomplete path still releases no selected partition or insufficiency
claim. No change to original validation progress counters was found.

Extra storage scales with summed per-word supports, tuple/count objects and
negative list references. Count integer digits and Python overhead are real
costs; this is not a fixed-byte memory bound. Worst case every word has the
same signature, leaving PN exact graph comparisons while paying all indexing
cost. Unary shortcut cases can pay signatures with no graph benefit. Measure
all preprocessing, output and regressions; no general speedup follows here.

graph_pair_universe is populated only if graph extraction is entered;
graph_pairs_filtered is partial progress on interruption and equals skipped
pairs after complete graph traversal. Neither metric is a count of compatible
partitions or independent observations.

## Required next evidence

Proceed with fixed independent small-family/decision/witness controls and
signature-specific adversaries (all signatures equal, different vectors,
equal-count nonadjacent permutations, Unicode, duplicates, empty classes,
late malformed/contradictory labels, deadlines and graph-empty exact fallback).
No generator truth may enter solver features. Timing only after correctness,
using the existing bounded matrix and plateau rule. This review does not
approve an unseen C2, profiler or generator source. No extra feature/metric
churn is requested. Hash snapshots: source_review_c1_v1/MANIFEST.json.
