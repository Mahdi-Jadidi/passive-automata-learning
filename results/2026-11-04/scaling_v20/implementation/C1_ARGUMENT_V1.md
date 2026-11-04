# C1: exact validated Parikh filtering

This candidate retains the existing C018 per-word counts as an immutable key
`(len(word), tuple(sorted(counts.items())))`. Only positive nonzero entries
occur. The alphabet is fixed and validated, so equality of these keys means
equal full per-symbol counts including implicit zeros. Signatures are made
after each word is fully validated. No additional character pass is introduced.

An actual unequal adjacent swap changes order only. Length and every symbol
count are invariant. Therefore every baseline positive/negative swap pair is
inside the selected exact negative bucket. Pairs outside cannot add a baseline
edge. Inside each bucket the entire original swap checker remains unchanged,
including exact character comparisons and original sample indices. Counts alone
never establish an edge.

The negative bucket retains every original record, duplicates included, in
original negative-index order. Positives are traversed in original order.
Removing only nonedges preserves the order of all actual edges. Thus on an
uninterrupted run even the successful-union spanning forest and its witness
indices match the baseline, not just its connected components. Exact Python
dictionary key equality handles hash collisions; no fingerprint is accepted
as a certificate and no colliding record is discarded.

Validation, zero-count/duplicate/contradictory-label semantics, unary/known-K
shortcuts, atom feasibility, RGS search, block-mask cache, projections and
output witness construction are unchanged. Signature sorting uses a new object
and cannot alter the Counter iteration order used by unary certificates. All
input labels are still validated before any decision, including late errors.

Additional memory is O(sum of per-word supports) signature entries plus
original negative record references. Additional signature time is
O(sum support*log(support)) comparisons, plus native hash/key overhead. Pair
character comparisons reduce to selected buckets; worst case still P*N*L
when every pair has the same Parikh vector. No speedup is guaranteed and unary
shortcut cases may pay only added work. Signature native sorting/hashing has
cooperative checks before/after, with external hard timeouts still required.

Review exact Unicode counts, empty words and zero vectors, duplicate word
indices, mixed positive unary count witnesses, equal-count non-swap near misses,
all signatures equal, foreign symbols late in input, deadlines, graph-empty
known-K unique fixtures and unchanged full small-family decisions. Every
complete output/witness must be independently checked. Timing progress may
differ under the same soft budget, but unresolved must stay nonfinal.

Implementation review target: candidate_c1_v1/gate_v1.py and its byte-identical
C018 CLI. No provider/source run or measured result is claimed by this proof.
