# Exact sample-compatible partitioning by exhaustive enumeration

## Model and problem

Let Σ = (a₁,…,aₘ) be an ordered finite alphabet of pairwise distinct atomic symbol identifiers. A word is a finite sequence of these identifiers, including the empty word ε. Let P,N ⊆ Σ* be finite positive and negative full-word observations. For B ⊆ Σ, π_B deletes every symbol outside B and preserves the order and multiplicity of the remainder. A partition Π of Σ has nonempty, pairwise disjoint blocks whose union is Σ. For each B ∈ Π, a regular language F_B ⊆ B* is an independent local factor. The induced global language is

    L(Π,(F_B)) = {w ∈ Σ* : ∀B ∈ Π, π_B(w) ∈ F_B}.

A partition is *sample-compatible* if some collection of regular factors accepts all P and rejects all N. There is no supplied number K of factors, bound on factor states, hidden target automaton, or owner label. Finite observations leave all unobserved words unconstrained. For Σ = ∅ we adopt the unique empty partition and the convention that the conjunction of zero factors is true; consequently its language is {ε}. These are Boolean full-word labels, not prefix-closed, noisy, timing, or general log semantics.

The optimization objective is

    max {|Π| : Π is sample-compatible}.

When the feasible set is nonempty, a canonical optimum is the lexicographically least restricted-growth string (RGS) among its maximizers, using the supplied alphabet order. This maximizes the number of *sample-compatible blocks*; it does not identify physical owners or the true number of devices. The method additionally computes the number of all compatible partitions and the number of optimal partitions, both exactly. These counts are over partitions, not machines or probabilities.

In the reference interface, the input record has exactly `alphabet`, `positive`, and `negative` keys. Identifiers are distinct nonempty strings; words are arrays of whole identifiers and ε is `[]`. Identifiers may contain multiple characters, Unicode, punctuation, or one another; equality is exact with no tokenization or normalization. Word duplicates within each label are removed in first-occurrence order. Unknown IDs, wrong types, duplicate alphabet IDs, empty IDs, and missing or extra fields are malformed. The exact encoding prevents ambiguity between, for example, `["ab", "c"]` and `["a", "bc"]`.

## Projection characterization and constructive witnesses

For B ⊆ Σ define H_B = {π_B(p) : p ∈ P}.

**Theorem 1 (compatibility criterion).** A partition Π is sample-compatible if and only if

    ∀n ∈ N  ∃B ∈ Π  ∀p ∈ P : π_B(n) ≠ π_B(p).       (1)

*Proof.* If Π is realized by consistent factors, every factor F_B must accept π_B(p) for every p ∈ P. Every negative n must be rejected by at least one factor, so that single block's projection differs from every member of H_B. Conversely choose F_B = H_B for every block. These languages are finite and therefore regular, including when H_B is empty. Every positive is accepted by all factors, while (1) supplies a rejecting factor for each negative. For the empty partition, (1) holds exactly when N is empty, consistent with the empty conjunction. ∎

The order of quantifiers in (1) is essential. With Σ = {a,b}, P = {a,b}, N = {ab}, each positive differs from ab on some singleton, but neither singleton separates ab from *both* positives. Thus {a}|{b} fails while {a,b} fits.

The constructed factor list H_B and one rejecting block per negative form a finite certificate. For the concrete representation, blocks are in RGS-label order; `factors[i]` lists the distinct projected positive words in first-occurrence order; `negative_rejected_by[j]` is the zero-based first rejecting block for the j-th deduplicated negative in first-occurrence order. Hence repeating a raw negative cannot change the proof obligation. These factor languages are a consistent realization, not a claim that they are the actual unknown factors.

## Enumeration and algorithm

For m>0, an RGS s = (s₁,…,sₘ) satisfies s₁=0 and 0≤sᵢ≤1+max(s₁,…,sᵢ₋₁) for i>1. Labels name blocks in order of first occurrence. The empty RGS represents the unique empty partition when m=0. Each partition has exactly one such string: label its blocks by first occurrence. Conversely, the growth rule guarantees that the nonempty label preimages form a partition and first appearances are ordered. These constructions are inverses. Generating the permitted next labels in ascending order therefore enumerates all partitions exactly once in lexicographic RGS order.

The following conceptual recursive generator is extensionally equivalent to the frozen implementation's iterative rightmost-increment/zero-suffix generator. The implementation stores selected RGS strings and constructs witnesses after enumeration; constructing them during checking, as below, is semantically equivalent. `INCOMPATIBLE` has zero counts and no recommendation; `INVALID_INPUT`, `ERROR`, and `INCOMPLETE` have null mathematical result fields. Resource interruption is handled outside the displayed mathematical loop as described below.

```text
01  GENERATE(m):
02      if m = 0: yield []; return
03      yield from EXTEND([0], 0, m)
04  EXTEND(s, q, m):
05      if |s| = m: yield s; return
06      for x = 0, 1, ..., q+1:
07          yield from EXTEND(s · [x], max(q,x), m)
08  CHECK(Sigma, P, N, s):
09      blocks ← nonempty label preimages of s in Sigma order
10      for each block B: H[B] ← {projection(p,B) : p ∈ P}
11      rejecting ← empty list
12      for each n ∈ N in normalized input order:
13          find first B in block-label order with projection(n,B) ∉ H[B]
14          if no such B exists: return FAIL
15          append index(B) to rejecting
16      return witness(s, blocks, H, rejecting)
17  EXACT(record):
18      validate record and IDs; if malformed: return INVALID_INPUT
19      Sigma, P, N ← normalized input; deduplicate each label set
20      if P ∩ N ≠ ∅: return INCOMPATIBLE with counts 0
21      C ← 0; O ← 0; best ← NONE; all_witnesses ← []; opt_witnesses ← []
22      for each s yielded by GENERATE(|Sigma|):
23          w ← CHECK(Sigma,P,N,s)
24          if w = FAIL: continue
25          C ← C+1
26          if |all_witnesses| < 2: append w to all_witnesses
27          k ← number of blocks in w
28          if best = NONE or k > best:
29              best ← k; O ← 1; opt_witnesses ← [w]
30          else if k = best:
31              O ← O+1
32              if |opt_witnesses| < 2: append w to opt_witnesses
33      if C = 0: return INCOMPATIBLE with counts 0
34      replay retained witnesses; if replay fails: return ERROR
35      status ← UNIQUE_COMPATIBLE if C = 1 else AMBIGUOUS
36      return status, C, best, O, (O = 1), opt_witnesses[0],
37             all_witnesses, opt_witnesses
```

**Theorem 2 (completed-run correctness).** On a well-formed finite input, assuming the search and witness replay complete without resource failure, the algorithm returns `INCOMPATIBLE` exactly when no partition is sample-compatible. Otherwise C is the number of compatible partitions, best is their maximum block count, O is the number attaining best, and the returned recommendation is their lexicographically least optimal RGS. The witness lists contain the first min(2,C) compatible and first min(2,O) optimal partitions respectively.

*Proof.* Full validation precedes a mathematical result. A trace in P∩N cannot be both accepted and rejected, so line 20 is sound. By the RGS bijection, lines 1–7 and 22 visit exactly the partitions once. By Theorem 1, lines 8–16 and 23–24 pass exactly the compatible candidates. After any processed prefix, C counts compatible candidates in it and `all_witnesses` contains the first at most two. If there are any compatible candidates in the prefix, best is the greatest block count seen, O is the number of candidates attaining it, and `opt_witnesses` contains their first at most two in lexicographic order. Initially the invariant is vacuous. Lines 25–27 update the all-compatible part. When k exceeds best, line 29 resets the optimal count and witnesses; on equality, lines 30–32 increment and retain an additional witness if space remains; smaller k changes neither. Induction proves the invariant. At exhaustion it applies to the full family; its first optimal witness is the lexicographically least optimum. Line 33 handles the empty family. By Theorem 1, each retained H_B and rejecting index is a certificate; the concrete construction records first-occurrence order as specified above. Lines 34–37 verify and return the claimed results. ∎

Theorem 2 treats arbitrary-precision integers and mathematical completion. The actual internal replay checks the block partition, RGS agreement, equality of each finite factor as a set, positive acceptance, and rejection by the reported block. The stronger serialization requirements—first-occurrence order of projected words and first rejecting block—follow from construction and were independently checked in the audit; the internal replay alone does not check those ordering properties.

### Line-to-proof obligations

| Lines | Obligation and justification |
|---|---|
| 1–3 | Generate one empty RGS for m=0; otherwise initialize the only valid first label 0. |
| 4–7 | Enumerate all legal next labels in ascending order; induction on remaining length and the RGS bijection give unique complete lexicographic coverage. |
| 8–10 | Decode the partition and compute every positive projection for each block, establishing the H_B used by Theorem 1. |
| 11–16 | For each negative test for one block excluding its projection from the entire H_B, rejecting exactly when (1) fails; retain the first rejecting index. |
| 17–20 | Validate before mathematical conclusions, deduplicate without changing the sets, and detect the contradictory-label impossibility. |
| 21–27 | Initialize the prefix invariant, count each compatible partition exactly once and keep its first two witnesses. |
| 28–32 | Reset on an improved block count; increment and retain ties on equality. This preserves the exact prefix maximum, optimal count, and first two optimal witnesses. |
| 33–37 | Classify the exhausted family, replay finite-factor certificates, and return the global counts and canonical optimum; replay failure is ERROR. |
| Outside displayed loop | A caught interruption or budget exhaustion returns INCOMPLETE with null mathematical fields, never partial mathematical certification. A force-killed process need not return an output at all. |

**Termination and cost.** There are Bell(m) set partitions (Bell(0)=1). On any non-contradictory run that completes exhaustive enumeration, the number of candidate evaluations is exactly Bell(m); validation and completed contradiction detection may return earlier. Each candidate's projection checks and witness construction use polynomial work in the explicit finite input size under ordinary exact string and array operations. Thus a conservative total bound is Bell(m) times a polynomial in input size, including symbol-ID encoding and arbitrary-precision count operations; no polynomial bound in variable m is claimed. The retained witness data are polynomial in the explicit input size, while exact counts require O(log Bell(m)) bits and the enumerator keeps a finite RGS state; this says nothing about a practical time or memory budget. Completion on every finite input is a mathematical statement under sufficient resources, not a wall-clock guarantee.

For a valid nonempty alphabet, oneblock fits iff P∩N is empty. For the empty alphabet, the sole empty partition fits iff N is empty; its completed counts are C=O=1 and best=0. Empty P, empty N, ε, unused symbols, duplicate words, and arbitrarily long finite word arrays are handled by the same criterion. A contradictory sample is `INCOMPATIBLE`; malformed input is `INVALID_INPUT`. Candidate-budget exhaustion, caught interruption, or caught resource exhaustion produce `INCOMPLETE` with null mathematical fields; an external hard termination cannot be promised a returned status. A witness-replay error is `ERROR`, not a data-incompatibility result.

## Identifiability, prior work, and evaluation

All-compatible uniqueness and optimal uniqueness are different. For Σ={a,b}, P={ε}, N={a}, both {a,b} and {a}|{b} are compatible, but only the latter has the optimal two blocks. More generally, a single universal factor over {a,b} and universal singleton factors over {a} and {b} have the same complete global language. Consequently even full membership behavior cannot recover which of those physical partitions generated it under the unconstrained model. If the assumed model is correct, an actual generator fits the observations, and exactly one partition is compatible, its partition is conditionally identified within the model; factor implementations and physical names remain undetermined. The RGS tie-break is deterministic, not a measure of confidence.

The projection obstruction is closely related to prior compositional learning theory: Henry et al., *A Detailed Account of Compositional Automata Learning through Alphabet Refinement*, arXiv:2504.16624v3, §4.1 and Corollary 12, characterize incompatibility through a negative whose projections match positive observations on all local alphabets ([paper](https://arxiv.org/html/2504.16624v3)). Their setting includes active learning, labeled transition systems and potentially overlapping distributions with synchronization; it must not be conflated with this finite passive disjoint-factor optimization. Moerman's *Learning Product Automata* studies active learning of Moore machines with decomposable outputs ([PMLR 93, 2019](https://proceedings.mlr.press/v93/moerman19a.html)). The proof above is self-contained for the stated full-word regular-factor model; this limited comparison does not establish novelty. Exhaustive maximum-block partition enumeration is the method specified here, not a claim of a novel projection criterion.

A frozen Python reference was checked against an independently written set-insertion partition oracle. The post-clarification audit reports zero mismatches in 2,187 exhaustive ternary labelings of all seven two-symbol words of length at most two, 60 seeded cases over alphabets of size 3–8, 19 edge records, 11 malformed-schema controls, and three withheld-DFA sample controls; metamorphic and budget checks also passed. The 1,200-symbol control was deliberately interrupted after one candidate and is not a completed exhaustive large-alphabet solve. An initial audit-checker failure compared duplicate raw negatives with normalized witness indices; it was retained, the index domain was clarified prospectively, and the unchanged source was rerun. Detailed hashes, environment, exact commands, and evidence are in `../../exact_foundations_v28/audit/AUDIT_REPORT_V2.md` and `AUDIT_MANIFEST_V2.json`. The proof reviewer and auditor were coordinated AI agents, not human reviewers or a formal proof assistant. These finite experiments support, but do not replace, the proof; they establish no physical recovery or performance guarantee.

This section is a method candidate for a manuscript, not a claim that the contribution is novel, sufficient for acceptance, or suitable without a broader literature review, application evidence, and peer review.
