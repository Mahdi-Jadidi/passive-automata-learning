# C020 selected implementation direction — C1 and conditional C2

Direct proofs, no runs or source acceptance. Supersedes the recommendation
priority of the v1 proposal, not its preserved mathematical content. Rolling
hash indexing and RGS envelope remain unimplemented alternatives; no separate
branch or third candidate is requested. C1 is exact Parikh filtering of graph
pairs; only if measured bottlenecks justify it, C2 adds native str.translate
projection. Max two reviewed candidate versions and the frozen suite remain.

## C1. Equal counts are necessary for an adjacent swap

Define sig(w) as the exact tuple of nonzero (symbol,count) entries in a fixed
symbol order. Missing symbols have count0. An unequal adjacent swap preserves
every symbol count, so p,n can be a baseline swap witness only if sig(p)=sig(n).
Thus index/group negative records by exact signature and test only those in
the positive's matching bucket. All skipped pairs had no baseline edge.
All retained pairs still need the unchanged exact mismatch/reversal test;
matching signatures alone is not an edge or a compatibility decision.

The discovered graph therefore has exactly the baseline edges, or the same
components if only successful forest merges are retained. Every exact gate
decision/family is preserved. If positive traversal and original negative
order within each bucket match the baseline order, the saved forest choices
can also match: removed comparisons never performed a union. Otherwise
claim semantic equivalence with independently verified forest evidence,
not byte-identical deterministic witnesses.

Python dict hashes may index tuples, but exact tuple equality must distinguish
collisions. Do not replace the signature by a lone digest. Reuse fully validated
exact counts if possible; do not add a contradictory zero convention. Counters
are arbitrary exact integer counts and arbitrary declared Unicode code points;
no byte counting, case folding or Unicode normalization is allowed.

Critically, this filter applies ONLY to GRAPH PAIRS. P and N themselves must
remain unchanged for feasibility, unary tests and witness construction.
P={aa},N={b} has unequal vectors yet its negative is a real constraint.
P={abc},N={cba} has equal vectors but is not a single adjacent swap; it must
not create unchecked edges. Keep original list indices and duplicate conventions.

If n_s,p_s are bucket populations, graph comparisons become Σ_s p_s n_s
instead of PN. This is ≤PN and may equal PN. Signature work/storage, tuple
sorting, dictionary lookups and input-count reuse all cost resources; no
empirical or strict whole-program speedup follows from dropping comparisons.
Full validation still finishes before any scientific final declaration,
including late invalid words, contradictions and externally supplied known_k.

## C2. Native translate implements exactly the same projection

For a declared allowed block B⊆Σ, build a translation table mapping ord(a)
to None for every a∈Σ\B and leaving every a∈B unchanged. After full input
validation, every word character is in Σ. Then w.translate(table)=π_B(w):
each character outside B contributes epsilon and each inside contributes
itself, in original order. No mapped value may expand into other characters
or alter a retained code point. The same theorem holds chunkwise followed
by concatenating chunk results in order, because projection respects
concatenation. Empty/full blocks, epsilon, non-BMP/combining characters,
declared whitespace and NUL all obey this per-character proof.

The table must be keyed by Unicode ordinals (or the proper maketrans output),
not arbitrary character keys assumed interpreted without checking. Its identity
must bind to the exact block and alphabet. Reusing another block's deletion
table can silently corrupt masks. Undeclared characters must be rejected during
validation, not deleted as a convenient projection. Membership/equality of
projection strings remains exact, never a fingerprint-only test.

With unchanged project output, every reject mask, feasible witness and search
decision is unchanged. Partial metrics/deadlines need explicit boundaries:
on a completed valid projection add len(w) to logical projection_characters;
an interrupted native call is not a character-by-character progress proof.
Chunked translate can poll before/after bounded chunks and preserve output
with a single final join. Whole-word native translate with polls only outside
has a larger cooperative uninterruptible region; do not promise baseline's
1024-character polling granularity then. External hard timeout is necessary
in either case. Input validation, not projection speed, controls late-symbol
errors and contradictions. Source review must inspect actual timer/metric scope.

C2 is not requested before C1 results: table construction, repeated setup,
native allocations, joining and output may outweigh gains or leave an already
different bottleneck. No changed output schema or missing fields are permitted.

## Bounded adversarial source/gate obligations

1. Different whole-word signatures must only skip graph work, never samples.
2. Equal signatures/nonadjacent permutation must fail exact-swap verification.
3. Duplicate records and multiple valid swaps must preserve original indices.
4. Signature ordering independent of first occurrence; counts spanning chunks
   and all-zero/absent symbols must compare exactly.
5. Forced signature/dict collision must not equate different exact signatures.
6. Translate on B=empty/full/singleton, Unicode/NUL/combining and chunk ends;
   ensure exact retained order and unchanged positive/negative label policy.
7. A foreign symbol at the end, or malformed late word after a unary/graph
   shortcut would otherwise pass, still fails all-input validation.
8. Expired/injected deadlines during count/index/projection/search/emit return
   unresolved, without a selected provisional partition. Different budget
   trajectories need not agree, completed logical outcomes must.
9. Graph-empty known-K unique and incompatible controls still use exact
   fallback. Small exhaustive family oracle plus every returned witness is
   required; large truth-compatible output is not a full-family oracle.

No experiment was run for this proof. New source freeze/static review precedes
master GO. Paper work stays paused and public partition.py is untouched.
