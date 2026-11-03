# C015 unified exact gate v1

Source is frozen for independent static review before any execution. No
generator, provider or test has been run during implementation. Pure stdlib;
no previous solver/accelerator is imported. Older cycles are immutable.

After master GO, from repository root:

```powershell
python -B -X utf8 results/2026-11-04/partition_gate_v15/implementation/partition_gate_v1.py INPUT.json --seconds 5
```

Add `--known-k 2` only when the exact count is explicitly externally trusted.
Default allows every count 1..m. Input is exactly alphabet/positive/negative:
finite lists, alphabet nonempty/distinct one-character symbols, words using
only declared symbols. A conflicting positive/negative word is incompatible;
malformed syntax/types/foreign symbols/out-of-range or bool API K are invalid.
No world, generator states or truth metadata is read. CLI flag syntax errors
use standard argparse stderr/exit2; scientific data outcomes are JSON.

API: `gate_v1.solve(data, known_k=None, deadline=None)`. Deadline is finite
absolute perf_counter time or None. CLI defaults to five seconds and starts
its cooperative timer before input reading. Input byte hash is added by CLI.

## Result semantics

- certified_unique: only this outcome has a top-level partition. A witness and
  a complete uniqueness proof route are included in certificate. This is
  conditional on model assumptions and any trusted K, not a proof that actual
  hardware satisfies those assumptions.
- ambiguous: exactly two distinct compatible alternatives, each with blocks
  and indexed negative rejection evidence. There is no chosen partition. The
  ambiguity proof is complete without enumeration of all remaining answers.
- incompatible: contradictory labels, a trusted-count contradiction certified
  by must-link atoms, or a fully exhausted zero-answer search. No partition
  is selected. A mathematically completed no-model result exits0, not exit2.
- unresolved: deadline/interrupt/resource exhaustion prevents finality.
  findings.data_insufficient=null and computation_incomplete=true; no selected
  or provisional partition is released. CLI exit3. Unexpected program errors
  also remain unresolved, with traceback on stderr and an explicit reason.
- invalid_input: schema/type/constraint failure, exit2. No scientific family
  decision or observational-insufficiency claim.

For ambiguous, findings.data_insufficient=true; all completed outcomes have
computation_incomplete=false. The latter flag concerns the decision proof,
not enumeration of every answer. No exact-count, all-pair or family listing
is promised. Fields forced_atoms/swap_forest describe evidence, not a selected
partition. Only explicit partition in certified_unique is the released choice.

Every compatible witness uses the finite regular local languages
H(B)={projection_B(p):p in positive}. Witness blocks and original negative
indices/rejected_by_block refer to the unchanged input lists, duplicates
included. Projection strings are omitted to avoid repeating long words.
Independent replay must project each indexed negative and every positive onto
its rejecting block and check absence; the other blocks need not reject.
All positives are accepted by definition of H(B). Thus a verifier needs only
the observational input, witness blocks and certificate references.

## Proof routes and search

Validation/count scanning builds nonzero positive count sets plus presence
counts. For each negative a distinguishing nonzero count is sought, then a
zero count missing from positives. Universal-positive support scanning costs
at most support(n)+1 checks. All labels are scanned and validated even if an
earlier negative disproves the unary predicate. Empty P/N, epsilon and duplicate
observations are supported; no accepting-start restriction is imported.

If the exact unary condition holds, every set partition is feasible. Default
is unique only for m=1; otherwise one-block/singleton alternatives suffice.
With exact K, k1 or km is unique; interior1<k<m has two constructive witnesses.
K1 also has a direct consistent-label one-block certificate without the unary
condition. negative_count_certificates index each negative and its missing
positive unary count. Projecting onto any block containing that symbol
preserves the distinction, so the constructed witness evidence is valid.

Otherwise opposing-label adjacent unequal swaps yield sound same-owner edges.
Only successful union edges are saved, giving a spanning-forest proof of all
forced atoms. Missing edges imply no separation. Every admissible partition
must coarsen the atoms. If their exact projection feasibility check passes,
all coarsenings fit and the same count-specific constructive logic applies.
K>number_of_atoms proves incompatible; K=number_of_atoms and rejected atom
partition also proves incompatible because it is the sole count-valid candidate.
Failure of the atom test otherwise proceeds to exact search, not a no-model
or ambiguity guess.

The fallback is canonical restricted-growth DFS assigning atoms in fixed
order to an existing block or the next new block. Each unordered atom
partition is visited once. Safe known-K pruning excludes states with current
blockcount>K or current blockcount+remaining_atoms<K. At a leaf these checks
force the exact count. There is no partial-negative-rejection pruning.
Complete candidates are checked by union of exact block rejection masks:
for every negative at least one block projection must be absent from that
block's full positive projection set. Stop immediately after two verified
distinct leaves. Exhaustion with one proves unique; exhaustion with zero
proves incompatible. This RGS variant is equivalent in coverage to the
least-remaining-atom block recursion in theory/PROOFS_v1.md section3.

Reject masks are computed lazily with a bounded4096-entry LRU; there is no
2^m allocation. Cached objects are negative-index bit masks, not repeated
projection strings. This is an entry-count bound, not a memory-byte bound.
Projection languages are temporary per block computation. Search can still
take exponential time to establish uniqueness/incompatibility. Recursive
stack or memory failure returns unresolved, not an unsupported exact outcome.

## Resource and interpretation limits

Sparse counting has expected O(T+wordcount+m) dictionary work plus sorting.
Swap extraction may cost O(|P||N|*wordlength). Exact search and serialization
costs remain. Character loops poll every1024 characters and explicit word,
graph, DFS, mask and certificate loops poll cooperatively. Native JSON parsing,
hashing, sorting, allocation and output serialization cannot be preempted by
those checks; an external hard timeout is still necessary. API None permits
unbounded computation, not a promised low runtime. CLI --seconds0 may return
unresolved before validation, which is honest nonfinality.

Metrics count character scans/projections, swap pairs, search nodes, complete
candidates (including shortcut verification), masks computed and cache limit;
reject_cache_hits is available after normal DFS. solver_seconds covers API
work. CLI input_and_solver_seconds includes reading/parsing/hash work but
excludes JSON output; independent process wall time must include serialization.
All assumptions are declared conditions. Even an exact unique result can
misdescribe physical ownership if a trusted K or independence assumption is
false. Event ownership never identifies named physical device IDs by itself.
