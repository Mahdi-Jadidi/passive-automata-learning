# C011 frozen readiness V3 — bounded static disposition

Decision: BLOCKED by a true fallback witness-retrieval regression, below.
No provider execution or source edits. Source hashes were read and verified
against READINESS_V3.json before review:

* solver v2: 699f88004cc12201642eccb801fde5a0f6a720b063815a99032cac078fa29ba0
* CLI v2: 842dd27b149e1b1aade9ff2692f9ab25191259b027a2414c28edbb2d62e2471c
* protocol V2: 9ed1f7f0358731753af81406cf41bb4ca061a317ec58bf17d0779c583c7c5519

The filename/version convention is retained exactly as received; no claim
that this readiness is a successful gate. Snapshot manifest is in
static_review_v3/MANIFEST.json. Prior sources/attempts remain untouched.

## B1: optional witness None is interned as a partition (blocking)

In fallback's per-pair k loop, the candidate now uses

    diff_w = intern_partition(find_partition(k, ai, aj, False))

and the analogous same_w statement. find_partition legitimately returns
None when the requested relation has no witness at this particular k,
even though it exists at another k. intern_partition immediately passes its
argument to _partition_key, whose `for block in partition` raises TypeError
for None. This is not caught by the deadline/KeyboardInterrupt handler.

Minimal mathematical counterexample (not run):

    alphabet=[a,b,c], positive=["", "abc"], negative=["a"]

No valid binary-interval or adjacent-swap edge exists: opposite-label word
lengths differ. Singleton atoms fail direct feasibility. The three feasible
partitions are abc, ab|c and ac|b. Pair a,b has a different-block witness
at k=2 (ac|b), and a same-block witness at k=1. The loop starts at k=1,
where totals[1]=1, global diff>0, but find_partition(1,a,b,False)=None.
intern_partition(None) raises as described. Any similar fallback ambiguous
pair can encounter this. C010 allowed None and kept searching; wrapping
the optional result without guarding introduced the regression.

Required narrow correction: do not intern a missing witness (guard before
interning, or a defined None pass-through). Preserve this source and freeze
a new revision. No new feature or metric change is requested. A future
complete-set gate must include graph-empty fallback with ambiguous pairs.

## RLE discovery, exactness and certificate checks

* _rle_windows groups equal unordered transition labels; run endpoints and
  counts match the proved maximal-interval enumeration. Unary/empty words
  yield no windows; every run enters at most two groups.
* Keys contain exact length/interval/pair/counts plus polynomial outside
  fingerprints. Positive buckets retain **all** records, so distinct exact
  contexts are not lost through collisions. This uses more storage than
  representative deduplication, but preserves the proved lookup completeness.
* Every candidate checks exact outside strings with _same_context, full
  actual interval alphabet/counts and unequal words with _verify_interval,
  and exact stored window equality before union. Fingerprints never serve
  as an equality proof. Monkeypatching fingerprints to a constant can cause
  extra scans but does not change the mathematical decision on any candidate.
* certified_pairs skips further binary witnesses only after a valid witness
  for that pair was retained. It may omit many witnesses, not the discovered
  pair. The graph is not advertised as all semantic must-links; I003 remains
  a separately documented missed family.
* Binary certificates retain actual positive/negative, exact interval, sorted
  pair, counts and identical left/right contexts. They replay T1 directly.
* Legacy swap_index uses each RLE transition's last/first adjacent characters.
  Exact outside comparison plus reversal/unequal checks preserves the meaning
  of the legacy adjacent-swap certificate field. Indexed representative choice
  need not reproduce the same list of every C010 witness.

## Caches, counts and completion scope

* Projection LRU keys exact word plus sorted block-symbol tuple; values are
  exact strings. Eviction changes only recomputation. Empty block projection
  is correctly empty. Capacity is entries, not bytes; that known limit is
  not a blocker or memory guarantee.
* Interned partition/projection-witness records preserve default expanded
  fields when arguments are actual partitions. Shared returned Python lists
  must be treated read-only, as documented; JSON expansion is not omitted.
  B1 is independent of that known mutability caveat.
* Atom direct feasibility, Stirling spectrum, Bell totals/pairs, lazy masks,
  anchored count/pair recurrence and remaining-mask prune retain C010 proof
  structure. No mathematical count regression found in this bounded reading.
* The atom_sets loop is now inside the protected preprocessing handler. The
  accepted contract uses status=incomplete with complete=false and null exact
  fields. CLI maps this status to its incomplete exit code. Validation before
  protection, cooperative polling, metric scopes and resource exceptions
  remain documented limitations; no unrelated churn requested.

Disposition: fix B1 only in a new immutable revision, then perform bounded
delta review and the independent gate. No correctness acceptance or empirical
speed/memory conclusion follows from this static review.
