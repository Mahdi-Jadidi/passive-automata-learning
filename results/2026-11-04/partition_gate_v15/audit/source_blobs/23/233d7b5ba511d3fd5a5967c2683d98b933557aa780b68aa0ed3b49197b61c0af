# C015 frozen v1 — bounded independent static review

Decision: **STATIC CLEARANCE FOR INDEPENDENT CAPTURED GATE**. No blocking
source/mathematical defect found in the reviewed paths. No runtime/source
edits by theory. This is not executable or performance acceptance.

Verified source hashes against implementation/READINESS_V1.json:

* gate_v1.py: 630850cc1e0ae469438340c5bf6e73bb9fa2ca71e24429d1e58d966c85e4cc05
* partition_gate_v1.py: 60a5865a1846ed060b0954eef9cc7937d8709cb2a1aec4a4dbfc0925fac27758
* API_PROTOCOL_V1.md: 828eada435681f5ca4c7b33b7437a429efd1ee94a027aac2f3865ddc5a067a4e
* REVIEW_OBLIGATIONS_V1.md: 461e7c85341213825aeb0442ec163c6196deb7dc92aa4a8e03d677318751110e

## Status quantifiers and all-input validation

Only unique() adds a top-level selected partition. ambiguous() asserts two
different block lists and returns alternatives without selecting one. Known
count/label contradictions or completed zero search produce incompatible;
timeouts, interruptions, recursion and memory failures produce unresolved,
with data_insufficient=null and no provisional selected partition. Ambiguity
sets data_insufficient=true only after two constructive witnesses exist.
Its computation-complete flag describes the goal proof, not full enumeration.

The full positive and negative lists are checked before final scientific
routes. Unary predicate failure does not trigger early fallback/skip validation.
Contradiction records original positive/negative indices and is returned
only after the remaining input is validated. The protocol explicitly treats
conflicting labels as incompatible, malformed types/constraints as invalid.
known_k is external API/CLI only and rejects bool, out-of-range and non-integer.
An expired deadline may precede validation and return unresolved as documented.

## Sparse unary condition and constructive shortcuts

Nonzero count sets plus per-list-occurrence presence preserve implicit zero
support exactly, including duplicate positives. universal contains symbols
missing zero, including every symbol when P is empty. Nonzero negative checks
and universal absent-symbol checks implement the necessary/sufficient predicate.
N empty is vacuous; epsilon and m1 behavior align with the theorem.

oneblock() is valid after consistent-label validation: its language is P,
so every indexed negative is rejected. It handles explicitly known k1 even
without the unary condition. unary_witness uses the distinguishing unary
symbol's owner to identify a rejecting coarsened block; a projected equality
on that block would imply equal unary count, so the evidence is sound.

For 1<k<r, coarsenings constructs a first block of r−k+1 atoms and k−1
singleton atoms, then swaps one atom of that first block with a singleton.
There is a singleton because k>1 and a nontrivial first block because k<r.
The two expanded partitions are distinct and have exactly k blocks. Boundary
k1, k=r, r1 and k>r are handled before this construction. No-K uses one-block
and all atoms, distinct when r>1. Optional K is not inferred from the data.

## Exact swaps and complete-candidate feasibility

Swap extraction checks exactly two unequal adjacent mismatches with reversal
and identical other positions. The DSU saves only successful union edges,
forming a sound spanning-forest proof of its components. Every compatible
partition coarsens these atoms; missing edges imply no separation.

reject(mask) uses exact original positive projections and original negative
indices; duplicate labels retain their bit positions. The 4096-entry LRU
evicts only reusable exact values, never solutions. witness(masks) computes
the union and records one valid rejecting block for each newly covered
negative; the returned records are sorted by original negative index.
Each witness's positive-projection local language rule accepts all positives.
Masks are allocated lazily, not in a 2^m array.

If atom partition fits, every coarsening fits and no atom may split. The
unique/ambiguous count routes are exact and constructive; both ambiguous
coarsenings are independently checked with witness(). If it fails with k=r,
the only possible k-block candidate is excluded. k>r excludes all possible
coarsenings. These are valid incompatibility proofs, not graph completeness
assumptions.

## Actual fallback is RGS, not subset-block DFS

The source inserts atom pos into each existing block or into the next new
block. Restricted-growth insertion order gives exactly one path per unordered
atom partition: the block containing each next atom is determined, and newly
created blocks are ordered by first occurrence. Conversely every partition
has such a path. This proves the same exhaustive coverage as theory's subset
recursion despite different internal states.

The only partial pruning checks existing blockcount>k or existing count plus
unassigned atoms<k. These exclude impossible final counts; at rem0 they force
exact k. There is no unsound partial projection rejection prune. Every leaf
is checked exactly. witness() returns fresh block lists, so later in-place
mask backtracking does not mutate retained solutions. Stop2 is duplicate-free
and complete for ambiguity; stop1/zero is reported unique/incompatible only
after DFS returns without hitting2. A resource/deadline exception bypasses
those declarations. No exact all-count or all-pair claim is made.

The graph-empty doubled-pair known-k2 case must be included by the auditor;
its uniqueness depends on exhaustive fallback rather than swap coverage.
This reviewer has not executed that or any other case.

## Cost, certificates and remaining scope

The gate's requirement is logical: proving singleton V can cost full inference,
not an independently cheap prerequisite. See GATE_COST_ADDENDUM_v1.md. No
universal polynomial runtime or NP-hardness theorem is asserted. Default
no-K nontrivial ownership remains ambiguous against the one-block model.

Certificate witness indices are directly replayable. An exhaustion route's
search_exhausted=true is a declaration of trusted executed exhaustive code,
not a serialized full proof tree independently proving exhaustion by itself;
large-case verifier claims must distinguish this from replaying two witnesses.
Independent full-set/decision oracles on small cases remain required.

Cooperative polling covers explicit loops and emit checks. Native parsing,
string hashing, sorting, allocation and serialization require external hard
timeout. The cache limit is entries, not bytes. Resource failure handling is
best-effort under actual memory exhaustion. CLI program/environment exceptions
are unresolved with stderr detail, never scientific incompatibility.
Internal timing excludes final output serialization; no speed acceptance here.

Physical interpretation requires actual independence, disjoint alphabets,
correct labels and any trusted count to hold. Finite input cannot establish
those hardware assumptions or named-device identities. No extra scope change
or metric churn requested. Proceed with frozen independent controls/gate.

Hash-bound snapshots: source_review_v1/MANIFEST.json. All old artifacts remain.
