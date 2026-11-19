# Exact Alphabet Partitioning from Positive and Negative Traces with Unknown Component Count

## Abstract

We study an exact finite-sample partitioning problem for independent disjoint regular factors under conjunctive full-word acceptance. The input is an explicitly declared finite ordered alphabet and finite positive and negative trace lists; neither a component count nor a state bound is supplied. A partition is compatible when some regular language over each block accepts every positive projection while the conjunction rejects every negative. We prove an exact projection criterion, give finite factor witnesses, and enumerate canonical restricted-growth strings to count all compatible partitions, find the greatest possible number of blocks, count its ties, and return reproducible ordered witnesses. We prove the baseline algorithm's completeness, selection invariants and finite termination under sufficient resources, including the empty alphabet. Two separately specified optional extensions use a singleton-compatible full-family certificate and a bounded per-call block-rejection cache. Neither changes the full result contract or provides a general polynomial guarantee. Independent finite audits and bounded timings are reported with their scope; they do not prove correctness for all inputs or identify a physical generating system. The work makes no novelty or publication-acceptance claim.

## 1. Introduction and contributions

A trace may contain events belonging to several unknown subsystems. We ask what partitions of its declared alphabet remain consistent with finite, noiseless membership observations when acceptance means that every independent factor accepts its own projection. Since no component count K is supplied, compatible partitions of all block counts must be considered. We choose the maximum number of compatible blocks as a reproducible sample-based objective. This convention is not evidence that the resulting number or blocks are the physical ones.

The baseline method first reduces language existence to a finite projection test and then enumerates every alphabet partition in canonical order. Its output distinguishes the total number of compatible partitions from the number achieving the maximum, and provides finite regular-factor certificates. We give explicit proofs of the criterion, enumeration, loop invariants, witnesses, completeness, and termination. Two optional full-contract optimizations are analyzed independently. Finally, we describe the limits of identifiability, available correctness tests, and measured timing rather than assuming practical performance from a proof.

The results apply to the stated Boolean, full-word, independent, disjoint-factor AND model. They do not automatically apply to noisy labels, prefix-closed systems, arbitrary process logs, bounded-state factors, partial observations, infinite streams, or coupled factors. No promise is made about unobserved word membership. Mathematical completion requires adequate resources; a finite deadline is not implied.

## 2. Input, semantics, and objective

Let the alphabet be an ordered finite sequence Σ=(a₁,…,aₘ) of distinct atomic identifiers. Its input order—not a sort of their text—determines canonical order. A word w is a finite sequence over Σ; ε is the empty sequence. Let P and N be finite sets obtained from the positive and negative lists by first-occurrence-preserving deduplication. For B⊆Σ, projection π_B(w) erases each event outside B while preserving order and repetitions of events in B. For B⊆D, successive projections satisfy π_B(π_D(w))=π_B(w).

A partition Π is a collection of pairwise disjoint nonempty blocks whose union is Σ. On Σ=∅, the unique partition is ∅. For each B∈Π let F_B⊆B* be a regular factor language. The induced global language is

    L(Π,(F_B)) = {w∈Σ* : ∀B∈Π, π_B(w)∈F_B}.                         (1)

The empty conjunction is true; thus for Σ=∅ its language is {ε}. A partition is sample-compatible if there exist such regular factors with P⊆L and N∩L=∅. Let 𝒱(P,N) be the finite family of compatible partitions. If it is nonempty, define

    C=|𝒱(P,N)|,   k*=max{ |Π| : Π∈𝒱(P,N) },
    O=|{Π∈𝒱(P,N) : |Π|=k*}|.                                           (2)

The recommendation is the lexicographically first maximum-block partition in the canonical encoding defined below. C counts all compatible partitions, O counts optimal partitions, and neither counts automata or probabilities. When 𝒱 is empty, C=O=0 and k* and the recommendation are undefined.

The concrete input is a single record with exactly `alphabet`, `positive`, and `negative`. The alphabet is an array of pairwise distinct nonempty string IDs; each word is an array of whole IDs from the alphabet. Thus `[]` is ε and `["ab","c"]` and `["a","bc"]` are distinct token sequences. Strings may contain Unicode, punctuation or spaces. Equality is exact: no splitting, case-folding or Unicode normalization is performed. Repeated words are removed separately within each label, retaining the first occurrence. Missing or extra keys, wrong types, empty or duplicate alphabet IDs, and unknown word IDs are malformed. A word in both normalized P and N is instead a validly encoded contradiction.

**Lemma 1 (normalization and contradiction).** Within-label deduplication does not change the compatible family; if P∩N is nonempty, no compatible partition exists.

*Proof.* Compatibility quantifies over membership in each label set, so repeating a word adds no requirement. If w lies in both sets, any induced language would have to contain and exclude w simultaneously. ∎

## 3. Projection criterion and regular certificates

For every block B define

    H_B={π_B(p):p∈P},     R(B)={n∈N: π_B(n)∉H_B}.                      (3)

H_B is finite, possibly empty. It is a regular language over B.

**Theorem 1 (exact compatibility criterion).** A partition Π is compatible if and only if

    ∀n∈N  ∃B∈Π  ∀p∈P: π_B(n)≠π_B(p),
    equivalently  ⋃_{B∈Π} R(B)=N.                                       (4)

*Proof.* Suppose compatible factors F_B exist. Each positive p is accepted by the conjunction, hence π_B(p)∈F_B for every B and H_B⊆F_B. Each negative n is rejected by the conjunction, so some one B rejects π_B(n), which therefore cannot equal any member of H_B. This proves (4). Conversely take F_B=H_B for every B. The language H_B is finite and hence regular, including H_B=∅. Every positive is accepted by every factor. By (4), each negative has a block whose projection is excluded, and is rejected by the conjunction. For Π=∅, (4) is true exactly when N=∅, matching the empty-conjunction convention. ∎

The quantifiers in (4) cannot be swapped. For Σ={a,b}, P={a,b}, N={ab}, negative ab differs from each positive on some singleton, but on {a} it matches positive a and on {b} it matches positive b. Thus {a}|{b} is incompatible even though ∀p∈P ∃B π_B(ab)≠π_B(p). The one-block partition is compatible.

**Lemma 2 (certificate).** For a partition satisfying (4), the block languages H_B and, for each n∈N, one block B with π_B(n)∉H_B constitute an independently replayable finite certificate.

*Proof.* The displayed languages are regular and accept every positive projection by construction. The stored block excludes the corresponding negative projection, so the global conjunction rejects that negative. The partition itself can be checked for disjoint, nonempty blocks covering Σ. ∎

The concrete witness record has `rgs`, `blocks`, `factors`, and `negative_rejected_by`. Blocks are ordered by canonical label; factors[i] lists unique projected positive word arrays in first-occurrence order for blocks[i]. For each normalized negative in first-occurrence order, `negative_rejected_by[j]` stores the zero-based index of the first rejecting block in label order. Duplicate raw words are covered by the same normalized entry. With no negatives the list is empty; for a compatible empty partition all four arrays are empty. These factors demonstrate consistency, not reconstruction of unknown original machines.

## 4. Canonical partition enumeration

For m>0 a restricted-growth string (RGS) is a tuple s=(s₁,…,sₘ) satisfying

    s₁=0,   0≤sᵢ≤1+max{s₁,…,sᵢ₋₁}   for 2≤i≤m.                       (5)

For m=0 the only RGS is the empty tuple. Label each block of a partition by the order in which one of its symbols first appears in the declared alphabet. Conversely, the preimage of each used label in an RGS is a block.

**Lemma 3 (bijection).** First-appearance labeling maps partitions of Σ bijectively to RGSs of length m, including the unique empty partition and empty RGS for m=0.

*Proof.* The first symbol's block receives zero. Whenever a new block first occurs, its label is exactly one greater than the preceding maximum, so the resulting tuple satisfies (5). Conversely, (5) forces the used labels to be consecutive from zero; every label has a nonempty preimage, the preimages are disjoint, and together they cover all alphabet positions. First-appearance labeling of these preimages returns the original RGS. The empty case is immediate. ∎

**Lemma 4 (complete lexicographic generation).** Lines 1–7 of Algorithm 1 generate every RGS exactly once in lexicographic order.

*Proof.* For m=0 line 2 yields exactly the empty string. For m>0 line 3 uses the only permitted first label. At every prefix with current maximum q, lines 6–7 visit exactly the next labels 0,…,q+1 in increasing order. Induction on remaining length shows that every valid continuation appears once and that all strings below a smaller next label precede those below a larger next label. Therefore generation is complete, unique, and lexicographic. ∎

## 5. Algorithm 1: exhaustive exact baseline

The following mathematical pseudocode checks each candidate against all normalized positives and negatives. It maintains arbitrary-precision counts and retains up to two witnesses from each specified family. `INCOMPATIBLE` results have zero counts and no recommendation; invalid input, incomplete computation and replay failure do not carry mathematical result fields. The external interruption rules are stated in §7.

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

Here `witness` constructs the factor and rejection-index lists described in §3. The source implementation stores selected RGSs during the loop and constructs witnesses afterwards; their equivalence is proved in §6. The checks are over arrays of whole IDs, not raw concatenations.

**Lemma 5 (CHECK correctness).** For every generated RGS, lines 8–16 return FAIL exactly when the represented partition is incompatible; otherwise they return a valid certificate in canonical block and negative order.

*Proof.* Lines 9–10 construct its blocks and each H_B. For every normalized negative, lines 12–14 require one block whose projection is outside the entire H_B. Theorem 1 says exactly this is necessary and sufficient. If it exists, line 13 chooses the first and line 15 records its index. Line 16 constructs the positive projections in first-occurrence order and returns the certificate justified by Lemma 2. ∎

**Lemma 6 (prefix invariant).** After any prefix of the RGS iteration, C is the number of compatible candidates seen and `all_witnesses` contains their first min(2,C) in lexicographic order. If C>0, best is their largest block count, O is the number attaining best, and `opt_witnesses` contains the first min(2,O) such candidates in lexicographic order.

*Proof.* Initially C=O=0 and the lists are empty, so the invariant is vacuous. By Lemma 5, a failed check is not compatible and line 24 leaves the invariant unchanged. Otherwise the newly visited RGS is compatible and unique by Lemma 4; lines 25–27 count it and retain it only if fewer than two prior compatible witnesses exist. If its block count k is greater than best, all previous optimal candidates cease to be optimal for the prefix; line 29 sets best=k, O=1 and replaces their witnesses with the current candidate. If k=best, line 31 increments O and line 32 appends it only when fewer than two exist. If k<best, neither optimum value nor its witnesses changes. Since enumeration is lexicographic, retained witnesses are the first two. Induction proves the invariant. ∎

**Theorem 2 (soundness, completeness, and optimum).** Given a well-formed finite input and sufficient resources, if enumeration completes and witness replay succeeds, Algorithm 1 returns INCOMPATIBLE exactly when no compatible partition exists. Otherwise C, best, O, status, recommendation and both witness lists equal the quantities specified in (2), with the lexicographically first optimal recommendation.

*Proof.* Validation and normalization preserve the input sets by Lemma 1; the contradictory-label early return is sound by that lemma. Otherwise Lemma 4 visits every partition once, and Lemma 5 marks exactly compatible partitions. At loop completion the prefix invariant of Lemma 6 therefore describes the entire family. If C=0, line 33 correctly declares incompatibility. If C>0, best and O have the required global meanings, `opt_witnesses[0]` is the first optimal RGS, and both lists contain exactly the first min(2,count) candidates. Lemma 2 validates the finite-factor witnesses. Lines 34–37 return the specified complete output. If replay fails, ERROR is returned instead and the theorem's successful-replay premise does not hold. ∎

**Corollary 1 (status and ties).** In completed feasible output, UNIQUE_COMPATIBLE holds exactly when C=1 and AMBIGUOUS exactly when C≥2. `optimal_unique` means O=1 and is a distinct statement.

*Proof.* The statuses are the exhaustive alternatives for the exact family size C; the optimal flag is calculated from the separately counted maximum subset. For example Σ={a,b}, P={ε}, N={a}: both {a,b} and {a}|{b} are compatible, while only the latter has two blocks. Thus C=2, O=1, and the unique optimum does not imply unique compatibility. ∎

### Proof-to-line dependencies

| Lines | Required fact |
|---|---|
| 1–7 | Lemmas 3–4 establish unique, ordered, complete RGS generation, including m=0. |
| 8–16 | Theorem 1 and Lemma 5 establish exact projection checking and finite witness construction. |
| 17–20 | Lemma 1 and whole-record validation distinguish invalid structure from contradictory labels. |
| 21–27 | Lemma 6 establishes all-compatible counts and first-two witnesses for the processed prefix. |
| 28–32 | Lemma 6 proves max reset, optimal tie count, and lexicographic optimal witnesses. |
| 33–37 | Theorem 2 and Corollary 1 establish completed statuses, exact output, and replay error handling. |
| Outside loop | Section 7 defines bounded-computation and uncatchable-termination behavior; incomplete work makes no exact claim. |

## 6. Refinement to the frozen implementation

The recursive generator is conceptual. The frozen Python source uses an iterative lexicographic successor: start with the all-zero RGS; choose the rightmost position whose label can increase while respecting the unchanged prefix, increment it by one, and set the suffix to zero. If no position can increase, stop.

**Lemma 7 (generator and witness refinement).** The iterative source generator yields exactly the same RGS sequence as lines 1–7, and deferred witness materialization produces the same witnesses as conceptual eager materialization on fixed normalized input.

*Proof.* Any lexicographically larger string must first differ at some position that can be increased while retaining its prefix. Choosing the rightmost such position makes the changed prefix as late, hence as small, as possible; increasing by one is minimal, and an all-zero suffix is the lexicographically least legal completion. Thus the described successor is the immediate next valid RGS. If no position can increase, no greater RGS exists. Both generators begin at all zeros and hence enumerate the same sequence, including the separately handled empty string. Witness construction is deterministic in the selected RGS and fixed normalized P,N. It therefore yields the same factor lists and rejecting indices whether invoked at selection time or after enumeration. ∎

The actual internal verifier checks block coverage, canonical RGS agreement, factor equality as sets, acceptance of positives, and rejection by each cited block. It does not independently check positive-projection serialization order or that the cited block is the *first* rejecting block. Those ordering properties follow from the source constructor and were separately checked by the independent audit. This distinction is part of the implementation claim.

## 7. Termination, complexity, and error semantics

**Theorem 3 (finite termination of the mathematical procedure).** For every finite well-formed input, the unbounded-resource algorithm terminates with an exact result or with a mathematically justified incompatibility result.

*Proof.* The alphabet has finitely many partitions; by Lemma 4 the generator emits each once and ends. Every projection, set comparison, validation operation, count update, certificate construction, and replay compares finite objects and terminates under sufficient resources. A contradiction check can finish earlier. Theorem 2 gives the completed result. ∎

There are Bell(m) partitions, with Bell(0)=1 [1]. A noncontradictory exhaustive baseline run evaluates exactly Bell(m) candidates. Each evaluation takes polynomial work in the explicit input size, so a conservative bound is Bell(m) times a polynomial factor that includes identifier representation and arbitrary-precision arithmetic. This is not a polynomial-time guarantee for variable m. Retained candidate witnesses and the iterative RGS state are finite; the two exact counts can grow to Bell(m) and require O(log Bell(m)) bits. A sufficiently large finite input can exceed available time or memory even though the mathematical process terminates.

Whole-record validation precedes any mathematical conclusion. `INVALID_INPUT` means malformed representation or invalid IDs, not contradictory data. A valid word in both P and N is `INCOMPATIBLE`; if no compatible partition is found after exhaustive completion, the same status is justified by Theorem 2. For m>0 and P∩N=∅, oneblock is always compatible because its projection is the original word; for m=0, compatibility holds exactly when N=∅, in which case C=O=1 and best=0. P=∅, N=∅, ε, unused declared symbols, repeated words, and arbitrary finite trace lengths require no special data truncation.

The optional implementation argument `max_candidates` limits candidate inspections, not K or model states. On candidate-budget exhaustion, a caught keyboard interruption, or a caught memory exhaustion, the implementation returns `INCOMPLETE` with null mathematical fields; no partial count or maximum is certified. If replay fails it returns `ERROR` with null mathematical fields. A hard-killed process or a failure preventing even error construction may return no response. In particular, an absent or timed-out computation is not evidence of incompatible data.

## 8. Optional exact optimization A: full-family certificate

After validation and contradiction handling, if there is no explicit candidate budget, check the singleton partition S. If it is not compatible, fall back to the baseline without a conclusion. If it is compatible, use a full-family certificate.

**Lemma 8 (coarsening monotonicity).** If B⊆D and n∈R(B), then n∈R(D). Consequently, every coarsening of a compatible partition is compatible.

*Proof.* If π_D(n)=π_D(p) for some positive p, projecting both sides to B yields π_B(n)=π_B(p), contradicting n∈R(B). Thus R(B)⊆R(D). Each block B of a compatible partition is contained in one block D of a coarsening; a rejecting block for each negative remains rejecting in its containing block. ∎

**Theorem 4 (certificate, exact counts, and witness order).** If S is compatible, all partitions of Σ are compatible. Their total is Bell(m), the maximum block count is m, and the unique maximum is S. Their lexicographically first RGS is 0^m; for m≥2 the second is 0^(m−1)1. For m=0 or 1 there is no second partition.

*Proof.* Every partition is a coarsening of S, so Lemma 8 proves compatibility for all. For m=0 this is the sole empty partition; its certificate condition requires N=∅. The number of partitions is Bell(m). A partition of m elements can have m nonempty blocks only if every block is a singleton, so S is the unique optimum, also for m=0. The all-zero RGS is lexicographically first; among all other valid RGSs, delaying the first nonzero label to the final position and using label 1 yields 0^(m−1)1, which exists iff m≥2. ∎

Compute Bell(m) exactly with S(0,0)=1, S(i,k)=S(i−1,k−1)+kS(i−1,k), and Bell(m)=Σ_k S(m,k), treating out-of-range S as zero [1,2]. The recurrence partitions by whether the last element forms a singleton or joins one of k existing blocks. It requires O(m²) arithmetic operations and O(m) stored arbitrary-precision values; the cost of those operations and of rendering large integers is not constant. A pure Python result does not guarantee a separate JSON/decimal conversion can exceed the host's configured integer-string limit. The certificate constructs and verifies witnesses using the baseline rules; it never claims Bell(m) candidate evaluations occurred. With *any* explicit `max_candidates`, including zero, A is bypassed and baseline budget boundaries are preserved.

## 9. Optional exact optimization B: bounded block memo

For each normalized negative n_j and block B, define the Boolean vector entry

    V_B[j] = true  iff  π_B(n_j)∉H_B.                                   (6)

A bounded per-invocation least-recently-used cache of at most 256 block vectors uses a tuple of whole IDs in declared order as its key. On a miss, compute all entries from the fixed normalized input; on eviction discard only cached data. A candidate partition is accepted exactly when every negative index has a true entry in at least one of its block vectors.

**Theorem 5 (memo equivalence).** Replacing baseline compatibility evaluation with the bounded memo test preserves the completed output—including C, best, O, all-compatible status, canonical RGS and both ordered witness families—for the same input and budget, provided no resource interruption occurs.

*Proof.* For fixed normalized P,N and B, (6) is exactly membership in R(B) from (3), independent of other blocks or enumeration history. A hit returns the same vector as a fresh computation; a miss or eviction recomputes that vector. Union coverage of the negative indices is therefore equivalent to (4), including the vacuous N=∅ case and Π=∅. The same Boolean decision is made for every candidate in the unchanged RGS order, so the prefix induction in Lemma 6 gives identical C, best, O and retained RGSs. The unchanged deterministic witness constructor and verifier then give the same serialized witnesses. Budget checks are performed at the same candidate boundary. ∎

An explicit budget bypasses A; B may still be used without changing the inspected candidate prefix. A and B may be enabled separately or together. The cache is local to a solve and cannot import facts from an earlier sample. Its 256-entry cap bounds retained vectors, not the number of input symbols or candidates; evicted blocks can be recomputed. A full vector may take more work than the baseline's early-negative exit, and either optimization can add memory or runtime overhead. Caught resource failures remain INCOMPLETE with null mathematical fields; different implementations need not fail at the same physical point.

## 10. Identifiability and limitations

The maximum is an exact recommendation under the sample criterion, not a certificate of the original physical decomposition. For Σ={a,b}, a single universal factor Σ* and two singleton universal factors a* and b* both produce the complete language Σ*. Their different partitions are indistinguishable even with all possible membership observations, unless further assumptions rule one out. If an actual generator belongs to the stipulated model, fits the labels, and exactly one partition is compatible, then its partition must equal that one partition; this conditional conclusion does not determine factor implementations, device names, or labels. By Corollary 1, O=1 alone is weaker than C=1.

The method is exact only for finite inputs with specified symbols and full-word Boolean labels. It does not infer physical K, bound unobserved behavior, predict every future trace, or guarantee that any interrupted execution can finish. It does not address noise, state-minimality, prefix closure, synchronization across overlapping ownership blocks, or arbitrary real logs without separate modeling and proofs. No polynomial runtime for the general variable-alphabet optimization is claimed.

## 11. Validation and measured behavior

The C028 baseline was audited with an independently written set-insertion partition oracle, distinct from its RGS generator. The post-clarification audit passed 2,187 exhaustive ternary labelings of the seven words of length at most two over a two-symbol alphabet, 60 seeded cases with 3–8 symbols, 19 edge records, 11 malformed-schema controls, and three withheld-DFA sample controls. Metamorphic, witness replay, and budget checks passed. A 1,200-ID control was deliberately stopped after one candidate; it was not a completed large-alphabet exhaustive solve. An initial audit checker mistakenly used raw duplicate-negative positions rather than normalized indices. That failure was retained, the serialization convention was clarified, and the unchanged baseline was rerun. This finite audit is evidence for the implementation, not a proof for every finite input.

The C030 candidate audit is separate: each of A-only, B-only, and A+B matched the independent oracle on 2,271 unlimited records, and the baseline on eight explicit-budget and nine invalid-schema/budget checks per variant, comparing complete outputs and replaying witnesses. A nine-ID diagnostic observed 366 LRU evictions and 111 later reinsertions. In an early-failure diagnostic, the baseline used 6 projection calls and B used 10 with the same decision. The first C030 run failed in a harness-only fixture assertion; the failure was retained, a corrected diagnostic was independently reviewed, and the unchanged candidate source passed the rerun. The legacy audit JSON field `candidate_calls: 0` is a baseline-mode artifact; per-variant counters record actual candidate comparisons.

After correctness, an eight-case baseline-versus-combined timing matrix used three fresh processes per solver and input, with identical unlimited budgets: all 48 executions completed and passed full-output checks. Process startup was included. The combined median was higher in three of eight cases and lower in five, with only three observations per cell and substantial variability; these measurements do not establish a general speedup or isolate either optimization. A-only and B-only were not timed separately, and memory was not measured. The unchanged C028 baseline remains the recommended default; the C030 variants are experimental. Raw timings, failures, exact inputs, commands and hashes are identified in Appendix A.

## 12. Relation to prior work

The projection obstruction is closely related to Henry et al.'s compositional automata-learning work: [3, §4.1, Proposition 5; §6.1, Corollary 12] characterizes incompatibility through a negative observation whose projections match positive observations on all local alphabets. That work concerns active learning of labeled transition systems and permits overlapping distributions and synchronization; its whole problem formulation is not identical to this passive disjoint-factor optimization. The criterion is not claimed to be novel. Lexicographic generation of set partitions is established in the combinatorial literature [4], and Bell/Stirling counting is standard [1,2]. Moerman [5] considers active learning of Moore machines with decomposable outputs, rather than the present sample-compatible alphabet partition objective. Exact-cover and related counting algorithms exist in broader settings [6], but do not automatically supply these exact family counts, first-two labeled witnesses, and interruption semantics. This limited comparison is not a comprehensive novelty search or a publication-acceptance guarantee.

## 13. Conclusion

The exact compatibility criterion and exhaustive canonical enumeration solve the specified finite sample problem with unknown K when resources permit. The proofs justify exact counts, canonical optimum, witness order and finite regular realizations; the optional certificate and memo preserve that contract under their stated conditions. Neither finite testing nor optimization of the sample objective recovers physical ownership in general. Further claims require additional assumptions, broader literature review, suitable experimental evidence and independent peer assessment.

## Appendix A. Reproducibility and provenance

The frozen baseline is `results/2026-11-11/exact_foundations_v28/implementation/reference.py`, SHA-256 `5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94`. Its complete specification, proof, serialization amendments, and pseudocode are under `exact_foundations_v28/theory/` and `PSEUDOCODE.md`. Its independent test evidence is `exact_foundations_v28/audit/AUDIT_REPORT_V2.md` and `AUDIT_MANIFEST_V2.json`.

The optional candidate is `results/2026-11-11/review_optimization_v30/optimization/candidate_v1.py`, SHA-256 `7501901c6de5d7bb78ffc60f152b818733e3bd4460c9a655b8d783f384e8fc2b`. Its proposal proof, source verdict, final report and audit are in `review_optimization_v30/optimization/`, `review/`, `REPORT_EN.md`, and `audit/AUDIT_REPORT_V2.md`. The v2 audit's frozen manifest records commands, executable versions, corpus hashes, retained failure, and all source hashes; `timing_results.json` records every raw timing and complete solver result. Proof and source reviewers and the auditor were coordinated AI agents, not human referees or a formal proof assistant. No old source or public entry point was modified for the optimization.

## References

[1] NIST Digital Library of Mathematical Functions, §26.7, “Set Partitions: Bell Numbers,” https://dlmf.nist.gov/26.7.

[2] NIST Digital Library of Mathematical Functions, §26.8, “Set Partitions: Stirling Numbers,” https://dlmf.nist.gov/26.8.

[3] L. Henry, M. R. Mousavi, T. Neele and M. Sammartino, “A Detailed Account of Compositional Automata Learning through Alphabet Refinement,” arXiv:2504.16624v3, 2026, https://arxiv.org/html/2504.16624v3.

[4] G. Stamatelatos and P. S. Efraimidis, “Lexicographic Enumeration of Set Partitions,” arXiv:2105.07472, 2021, https://arxiv.org/abs/2105.07472.

[5] J. Moerman, “Learning Product Automata,” Proceedings of Machine Learning Research 93, pp. 54–66, 2019, https://proceedings.mlr.press/v93/moerman19a.html.

[6] A. Björklund, “Exact Covers via Determinants,” arXiv:0910.0460v3, 2010, https://arxiv.org/abs/0910.0460.
