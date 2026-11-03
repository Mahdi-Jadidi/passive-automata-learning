# C014 source review v1 — exact unary predicate and C010 fallback

Disposition: **STATIC CLEARANCE FOR INDEPENDENT CAPTURED CONTROLS**.
No blocking mathematical/source defect found in the reviewed paths. This is
not runtime acceptance. No source execution or frozen-source edits by theory.

Verified against implementation/READINESS_V1.json:

* exact_partition_v1.py:
  e943e3f4f6d71713e7a49a39efcec0c36fa9ffceaf25bd8e4acffe03e9a5b74b
* solve_v1.py:
  7812e1cac73fb0aaf3d827bcf000430ff8c1703eb981f683ebd469d30f8598d5
* API_PROTOCOL_V1.md:
  48dd12e1b26822f6c5c7bb1a1f1d6013785795ae498dbfe5416ebeef265f7082
* PROOF_OBLIGATIONS_V1.md:
  25d439309aab6f276e2bbdd58daa571292e77ea6594b9401b7416729fbf1db9e

## 1. Sparse counts including zero

observed[a] stores precisely the nonzero positive counts. presence[a]
increments once for each positive list occurrence containing a; this matches
the raw list length, including duplicates. Thus zero belongs to the true
positive-count set iff presence[a]<len(positive). universal contains exactly
the symbols missing zero from that set. On a negative, its nonzero counts
are tested first; missing nonzero counts distinguish exactly as required.
If none distinguishes, scanning universal for an absent negative symbol
tests exactly the missing-zero possibilities. Other absent symbols have
positive zero support and cannot distinguish.

If P is empty, all observed sets are empty and universal is the entire
alphabet. A nonempty negative is distinguished by any occurring symbol;
epsilon is distinguished by zero on any symbol. This correctly yields the
all-partitions family with empty local languages. If N is empty, predicate
is true. With P=[a], N=[epsilon], a's missing zero is correctly found.
Duplicate positives do not change predicate truth because presence and the
positive length use the same multiplicity convention.

The universal scan checks at most support(n)+1 symbols: every failed test
encounters a symbol actually present in n; if none is absent, it visits at
most support(n). This supports the declared expected sparse operation count,
not a deterministic total-linear runtime or byte-memory claim.

## 2. Full validation and quantifiers

Exact input keys reject count/truth metadata. Alphabet and every word are
checked before final branch selection. A failed negative predicate does not
short-circuit precheck; subsequent words are still validated and contradictions
against the complete positive set are rejected. Each negative certificate
has one symbol whose count differs from every positive's count, not merely
one positive. Original negative-list indices remain valid even with duplicates.

Mathematical control P={ab,aabb}, N={aab} fails the predicate: a-count2
occurs in aabb and b-count1 in ab. It must use fallback even though no full
positive count vector equals the negative vector. This source does so by
direct inspection; no execution of that control is claimed here.

## 3. Counts, family and compact witness correctness

bell_spectrum implements S(n,k)=S(n−1,k−1)+kS(n−1,k), retaining the prior
row's sum as Bell(m−1). It returns Bell(m), that prior Bell and S(m,k).
For m=1 it gives total1/priorBell1 and no pair rows; for m≥2 every pair
correctly has same=Bell(m−1), different=Bell(m)−same and relation ambiguous.

The family descriptor states all set partitions, justified by the exact
predicate and regular-language coarsening proof. The registry's one-block
factor rule is exactly P; the singleton factor rule is positive unary counts.
They accept all positives and reject every negative, as independently
reconstructible from the input and count certificates. They witness both
relations of every ambiguous pair; no hardware-owner truth is inferred.

IMPORTANT contract distinction: this fast branch is explicitly the NEW
compact_exact_family schema, not C010's expanded default JSON. Pair IDs and
language reconstruction rules replace repeated full projection strings.
This is a valid declared separate contract; smaller output cannot be cited
as a faster identical-output C010 solver. The optional known-K variant and
full family enumeration are not implemented or implied by theory T1-K.

## 4. Frozen fallback and incomplete semantics

BASELINE resolves from the implementation file's parents[3] to results/,
then to the frozen C010 v2 path. Its bytes are hash-checked against
4c7959e96c02023d85943c8c52fae3f198c0de67ea172a72ad0669485f60c502
before import. Data and the SAME absolute deadline are forwarded; enumeration
is false. The native complete expanded payload is retained under baseline_result.
Unknown/incomplete baseline results and post-baseline deadline expiration
are normalized to incomplete with null counts/relations, not final answers.

Stop and KeyboardInterrupt inside protected work discard partial certificate
and exact-family information. The fast path checks the deadline before its
complete return. The CLI starts its deadline before reading and decoding
input. Native parsing/hashing/allocation/output and inherited C010 polling
remain cooperative limitations, not a hard wall bound. External hard-timeout
capture is still required. Environment/import/integrity/program failures are
reported by the CLI without scientific finality; no claim of API totality
on every resource failure is made.

The finally-updated metrics dictionary is shared into the returned object,
so total_solver_seconds includes protected API work. CLI input_read_and_solver
excludes final JSON serialization and output; these clocks are not fresh
whole-process wall time. No metric-only change is requested.

## 5. Next gate

Proceed with independently frozen exact full-family comparisons and certificate
replay, including empty P/N, epsilon, duplicates, absent-symbol zeros, mixed
positive count support, contradictions after predicate failure, m1, deadlines
and fallback. Large all-Bell cases need the explicit theorem, not materialized
Bell(large m) enumeration. No scientific execution or capacity/timing result
has been established by this static clearance. Source snapshots and hashes
are in source_review_v1/MANIFEST.json; original readiness is preserved.
