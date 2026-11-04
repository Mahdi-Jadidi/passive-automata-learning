# C020 — bounded exact scaling proposals and independent limits

Direct proofs before candidate source review. No executions, dependencies,
old edits or paper work. Baseline C018 gate SHA256
c288448f4a11849f74293b13201fdc578a79e6fbbe24165684807bd32ceeb83d.
C019's prerequisite/coverage results remain mathematical ingredients, not
evidence that arbitrary large generated data become uniquely recoverable.

## 1. Variables and actual bottlenecks

m is symbol count, r≤m the witnessed atom count, P/N raw or unique trace
counts as declared, T total characters, L maximum length, K an optional
externally trusted exact count. Hidden local DFA state count s is generator
metadata only and does not enter inference. Large s need not yield more
observed distinctions: unreachable/rare states or a short observation horizon
can produce the same sample from very different large worlds.

Distinguish generated K_true and s from supplied known_k and inferred r.
Do not pass the former into the solver unless the known-count variant is
explicitly chosen. With no-K a nontrivial partition still has a one-block
alternative; ambiguity is expected, not program error or physical recovery.

C018 already accelerates validation with exact chunked Counter, but its
adjacent-swap discovery still scans P×N pairs with up to L character work.
Search is goal-directed RGS with stop2 and a lazy4096-entry reject cache,
not default Bell-family enumeration. Expensive known-K unique/incompatible
cases can still require exhaustive search. Output contract stays unchanged.

## Candidate A (primary): exact adjacent-swap neighbor index

Index all validated negative words by (length, deterministic word fingerprint),
retaining every distinct exact word and its original index (or all records).
For each positive p and each adjacent unequal position i,i+1, compute the
fingerprint of the word obtained by swapping only those two positions.
Look up the bucket. For every candidate n, verify EXACTLY that

    |p|=|n|, p[i]!=p[i+1],
    n[i]=p[i+1], n[i+1]=p[i],
    n[j]=p[j] for all other j.

Only after this check union the two letter owners and retain the ordinary
positive_index/negative_index/positions/symbols forest certificate. No
materialized swapped string or altered label is required.

### A1. Constant-work fingerprint update

For H(w)=Σ_j code(w[j]) B^(ell−1−j) modulo a fixed M, the swapped value is

    H' = H(p) + (code(p[i+1])−code(p[i]))(B−1)B^(ell−2−i) mod M.

This is algebraic replacement of the two affected terms; no primality or
collision probability is needed for the identity. Codes must be deterministic
and exact equality must imply identical fingerprints. Compute powers once,
or iterate positions right-to-left maintaining the required power, avoiding
a power array. Initial word fingerprints and candidate generation take O(T)
character/arithmetic steps under fixed-width modular arithmetic, excluding
lookup collisions and exact verification. Original strings remain immutable.

### A2. Exact graph-component equivalence

Every inserted edge is a true baseline adjacent-swap edge by verification.
Conversely every baseline positive/negative swap at position i yields the
same target fingerprint and length, so the matching negative is in the
queried bucket. Keeping all exact words under collisions prevents loss.
Therefore enumerating all such positions discovers every baseline edge.

It is safe to skip a position whose two symbols are already connected and
to stop a bucket after finding one actual matching swap: any omitted edge's
endpoints are then connected. The final components equal baseline components
even if the retained spanning forest/witness indices/order differ. Proof:
the candidate forest is a subgraph of the baseline graph, so cannot overmerge;
every baseline edge is either inserted or already connected, so cannot
undermerge at termination. Consequently exact feasible families, statuses,
canonical atoms and physical conditional scope remain unchanged.

The existing compact output schema is preserved; a valid alternative forest
certificate is semantically equivalent, not necessarily byte-identical to
baseline forest selection. Auditor must validate every edge and final decision,
not demand the same chosen positive index if several witness the same merge.
No default fields, alternatives, checks or labels may be omitted for timing.

### A3. Counterexample attempts and resource limits

* Digest equality alone is UNSOUND: force all fingerprints equal; unrelated
  equal-length words would become false edges. Exact swapped-stream check
  must reject them.
* One negative representative per digest bucket loses completeness. P=abc,
  bucket containing negatives cba then bac: cba is not p's first-position
  swap but bac is. Retain separate exact words and try candidates until an
  exact match or bucket exhaustion.
* Blindly replacing p by every swapped word and declaring it negative is
  invalid; only actually labelled negative records provide evidence.
* Different processing order changes forest certificates, not permitted
  graph components. Missing original-index mappings or unchecked metadata
  would invalidate certificate replay.

Worst-case bucket work remains O(PNL) comparisons, each up to O(L), giving
a conservative O(PNL²) exact-verification bound without stronger collision
structure. Typical benefit is empirical, not guaranteed. Distinct-word
hashing/deduplication and output also cost work. Fixed-width fingerprint
collisions can increase runtime but never alter a verified edge. Native
hash/index operations and scans require cooperative polls plus outer hard
timeout. This is not a polynomial whole-solver guarantee.

## Candidate B (conditional second slot only): sound RGS envelope pruning

Do NOT implement merely because two slots exist. Consider only if counters
show exact search rather than graph/validation dominates and Candidate A
has plateaued. This candidate needs separate source review/freeze/gate.

At an RGS node let growing blocks be B₁,...,B_j, unassigned atoms U, and R(S)
the exact negatives rejected by the expanded symbol block S. Every completed
existing block is contained in B_i∪U and every new block is contained in U.
The monotonic lemma R(A)⊆R(S) for A⊆S follows because projection equality
on S implies equality on A. Therefore all rejectable negatives in any
completion lie in

    envelope = OR_i R(B_i∪U) OR R(U)  (omit R(U) when U empty).

If this envelope misses any negative, prune soundly. Passing is only necessary,
not sufficient. Known-k block-count bounds remain independent safe pruning.
All mask calls must use the immutable full sample and exact projections.

UNSAFE alternative: prune because the CURRENT growing blocks fail coverage.
Counterexample alphabet abc, P={aaccbb}, N={ccaabb}, known_k2. No adjacent
swap edge; at pos2 blocks a|b with c unassigned reject nothing, yet extending
c into a gives ac|b with aacc versus ccaa and is compatible. The envelope
remains sound because ac is included in a∪U. RGS cannot merge already
created blocks; this example extends one rather than assuming such a merge.

Envelope calls can add many expensive masks, evict useful cached values and
slow the solver. No speedup is implied by sound pruning. Do not eagerly
allocate 2^m masks, change negative-index semantics or apply paper selected-
output assumptions; the monotonic lemma is for this DFA-AND model only.

## 2. Compact suite and stop criteria for master/auditor

Use a small staged matrix, not a Cartesian explosion: independent small
full-family controls first (known-K/no-K, graph-empty unique, commutative
ambiguous, contradictions and all validation boundaries). Compare decisions
to exhaustive families and independently replay alternatives/rejections.
Then choose a few preregistered larger cells isolating data volume, L,
alphabet/observed r and hidden s; same input/default output for all providers.
Include same-P/N/r cells from small versus large saved DFA worlds, and a
graph-empty hard case so fast graph improvements are not generalized to search.
Synthetic labels must be independently replayed from saved generators by the
auditor, never consulted by inference. Compatible true partition is not an
independent full-family oracle on a large case.

Limits from authorization: at most two reviewed optimization candidates,
20s soft/25s hard per cell and ≤10min timing per provider. Three fresh
process repetitions only within the frozen budget. Charge parsing, preprocessing,
search, witness construction and output; preserve every slow/censored/error
and unstarted-budget cell. Memory measured separately if preregistered.
Stop when measured plateau or regression is established on this bounded
suite; do not keep adding favorable cells/features or raise budgets post hoc.

Timing reveals observed resource behavior only, not asymptotic exponents or
general speed dominance. More local DFA states alone is not a proof of harder
observed inference. Full physical recovery remains conditional on the declared
model and count information. Paper goal remains paused throughout this task.
