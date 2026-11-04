# C018 — exact chunked counting proof and safe scope

Direct proof before candidate source review. No scientific executions or
historical edits. C017 paper work remains paused; its selected-output model
is NOT used here. Baseline: C015 gate_v1.py SHA256
630850cc1e0ae469438340c5bf6e73bb9fa2ca71e24429d1e58d966c85e4cc05.
The model/output/status meanings are unchanged independent regular DFA-AND
sample inference with optional explicitly trusted known_k.

## T1. Chunked exact counts equal character scanning

Split a Python string w into consecutive disjoint slices w₁,...,w_q, including
every character exactly once. Define its count map by adding the exact
Counter maps of all slices with integer addition. For every symbol a,

    count_w(a) = Σ_i count_{w_i}(a).

Proof. The occurrences of a are partitioned by the slice containing each
position. Summing disjoint occurrence counts gives their full cardinality. ∎

Thus chunked Counter.update (accumulation), or an equivalent positive-count
sum, supplies exactly the baseline count dictionary. Never replace update
by dictionary overwrite: a symbol crossing chunk boundaries must accumulate.
Count units are Python string characters/code points, not UTF-8 bytes or
UTF-16 code units. No Unicode normalization or action-token reinterpretation
is introduced. Chunk size must be a positive integer with actual progress.

## T2. Validation is exact only if it covers all chunks/words

A word uses only declared symbols iff every symbol in every chunk Counter
belongs to the alphabet. An undeclared symbol at its final position must
therefore be rejected exactly as one at its start. Empty strings have empty
count maps and remain valid. Validate word types before slicing/counting.

If the entire alphabet is validated first, per-chunk key validation can
replace per-character membership checks without losing information. All
input words must be validated before any final scientific outcome. Finding
an early unary failure, contradiction or an apparently sufficient shortcut
does not authorize skipping a later malformed word. A deadline may interrupt
this process honestly with unresolved, not an unsupported data decision.

For completed valid scans, a character metric can add exact processed slice
lengths rather than incrementing per character. Interrupted/invalid partial
metrics need a declared boundary; a bulk count can have finished work before
an error is detected. Such diagnostic differences must not become false
claims about identical validation latency or exact failed-prefix counters.

## T3. Sparse zeros and duplicates remain unchanged

Retain nonzero positive count sets C⁺_a and presence[a], the number of raw
positive list entries containing a. The full count set C_a additionally
contains zero iff presence[a]<len(P). For P empty, C_a is empty, not {0}.
Duplicate positives must either count consistently in both presence and
len(P), or be deduplicated consistently with original certificate index maps.
Mixing raw length with deduplicated presence is unsound.

For each negative, test nonzero counts against C⁺_a; if none is missing,
search symbols present in every positive for one absent from the negative.
This is exactly count_n(a)∉C_a. Each failed zero test encounters a different
symbol actually present in n, so at most support(n)+1 such tests occur.
P/N empty, epsilon, and original duplicate negative indices are preserved.
The first-occurrence order of count keys may choose which valid symbol is
used as witness; any valid choice is logically equivalent. If literal
certificate equality is required, preserve that traversal order explicitly.

## T4. Gate equivalence, not just predicate equivalence

Assume the candidate changes only count extraction/validation with T1–T3,
and leaves known_k validation, all-input validation order, swap proofs,
canonical search, witnesses and final status logic intact. Then every
completed valid input has the same compatible partition family as C015,
and therefore the same unique/ambiguous/incompatible decision. A malformed
input is invalid under the same schema; conflicting valid labels follow
the baseline incompatible route. The proof is substitution of equal count
maps into the identical logical predicate plus unchanged exact fallback.

An equivalence of completed decisions does not require identical timeout
status on the same wall budget: a faster implementation may finish while
the baseline is unresolved. Every unresolved result must still release no
selected/provisional partition or observational-insufficiency conclusion.
Shared schema and full witness fields must remain for same-contract timing;
new compacting, omitting evidence or relabelling ambiguity is not a scan
optimization. No measured speedup follows from this proof.

## Deadlines and implementation obligations

Poll before each bounded chunk (and preferably after it), between words,
count-key loops and before any final declaration. Counter/native slicing
work within a chunk is not preempted by a cooperative poll; chunk length
limits that amount of character work, not an absolute latency in seconds.
String hashing for contradiction lookup, JSON parsing, sorting, allocation
and output remain native non-preemptible sections. External hard timeout
and preserved partial streams are still required. No whole-process hard
bound or deterministic linear-time theorem is claimed.

Expected scan/dictionary work is O(T+wordcount+m), plus alphabet sorting,
bit costs and duplicate/contradiction hashing. Counter reduces Python-loop
overhead; it does not change the asymptotic exact-search worst case. Memory
includes input, count maps, a temporary chunk and native Counter objects;
it is not constant-byte streaming of the entire input file.

## Safe search pruning boundaries (not activated by this proof)

C015 actual fallback is RGS insertion of remaining atoms into growing blocks.
Its safe known-k tests are current blockcount>k or current+remaining<k.
Do not prune because a current incomplete partition fails negative coverage:
adding symbols can enlarge block rejection masks. Example P={ab}, N={ba}
has incompatible singleton blocks but compatible merged block ab.

For any final block B and superblock S, R(B)⊆R(S), because equality of a
negative and some positive on S implies equality on B. A possible proved
RGS envelope uses remaining symbols U and existing growing blocks B_i:

    E = (OR_i R(B_i∪U)) OR R(U),

omitting R(U) if U empty. Every final existing block lies in B_i∪U and every
new block lies in U, so every final rejection mask is contained in E.
If E misses a negative, the node is impossible. Passing is not sufficient.
When U and existing blocks are both empty, use the exact leaf condition.
This is only an optional mathematical bound; it is not implemented, measured,
or recommended for the current count-only candidate without separate freeze.
Its repeated projection cost may outweigh any pruning benefit.

Pure fingerprints are not exact count/context evidence. Collision-verified
indexes can be sound but are a separate change; none is authorized by this
count-equivalence proof. Keep the bounded C018 implementation focused.

## Source-review and scientific status

These proofs specify obligations for upcoming source; they do not approve
unseen code. Independent source hashes and review must precede captured runs.
The auditor owns full-small-family oracles and long/deadline controls. Failed
source versions, raw captures and negative timing outcomes must remain.
