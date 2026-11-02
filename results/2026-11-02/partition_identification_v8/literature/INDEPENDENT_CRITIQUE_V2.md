# C008 independent literature and identifiability critique — v2

**Version note.** V2 preserves V1 and corrects one overstatement: a state bound and complete distinguishing horizon are one sufficient uniform route, not necessary for every finite ownership certificate. V2 also records the independent disposition of theory T6/T7.

**Scope.** Bounded review of the frozen C007 theorem statements and nearby primary literature. Read-only review of C007; no code, provider, experiment, or parent-owned file was changed. Literature notes and counterexamples are separated into `SOURCES_V1.md` and `COUNTEREXAMPLES_V1.md`.

## Decision in one paragraph

C007's mathematical target is well-defined and its central finite-sample statements appear sound under its declared assumptions, but that target is the **finest partition compatible with the supplied finite labels**, not the hidden physical partition. Exact same-language ownership ambiguity is real whenever nonprimitive factors are allowed; it remains even if k is supplied. A stronger and achievable complete-language target is the unique **prime disjoint factorization of a known complete nonempty global language**. That partition is uniquely determined up to permutation if each true local language is alphabet-prime. For finite passive data with unrestricted DFA size, there is no *uniform finite horizon guarantee over the whole class*, even with known k and prime factors. This does not mean every finite sample is ambiguous: T8 supplies a finite certificate without a state bound when trusted k and a sound must-link graph have exactly k components. More generally, finite ownership is identifiable relative to a declared model class exactly when the ownership projection of the sample-consistent version space is a singleton, and a valid certificate proves that fact. A state bound plus complete distinguishing coverage is another sufficient route, not a necessary condition for every finite certificate. Hardware IDs and internal state encodings remain unidentifiable from language behavior alone.

## Literature: closest results and model boundaries

Henry et al. (arXiv:2504.16624v3) is the closest reviewed paper to unknown-alphabet compositional learning. It treats active LTS learning with global membership/equivalence queries; a distribution may overlap, making shared letters synchronizing. Proposition 5 tests whether the finite observations are modeled by a distribution, and Theorem 18 proves finite convergence of that refinement procedure to a distribution that models them. This is useful prior art for compositional learning and observation-derived constraints. It is not a passive finite-sample theorem for disjoint blocks, and its correctness/termination claims do not establish that a returned distribution names the real hardware ownership. Its “canonical distribution” minimizes redundant alphabets while preserving connecting power, a different canonicalization from prime disjoint factors. These distinctions are supported by the paper's definitions and results; the “not physical ownership” reading is a scope inference, not a quotation.

Gold (1967) is relevant only after fixing the presentation model. Under an exhaustive labeled informant, the regular languages are identifiable in the limit; this is an infinite presentation and convergence need not provide a finite stopping certificate. Gold's positive-only text impossibility result is not directly transferable to a passive dataset with both positive and negative labels. The classic result therefore sharpens, rather than replaces, the finite-sample counterexample here.

RPNI/characteristic-sample literature addresses recovery of one DFA language from positive and negative examples, given a characteristic sample condition; the 2024 Balachander–Filiot–Gentilini paper states this background and develops a related passive learner for register automata over an infinite data alphabet. This is relevant to the component-language stage after ownership is known. It does not settle the preceding ownership partition. The shuffle-factorization literature also exists, but Berstel–Boasson's uniqueness theorem is for finite sets of words factored into word factors; it is not the needed theorem for arbitrary regular local languages.

Exact source metadata and attributed notes are in [`SOURCES_V1.md`](SOURCES_V1.md).

## Independent review of C007's proofs

Reviewed files: C007 `theory/PROOFS_v1.md`, `theory/PROOF_BOUNDARIES_v1.md`, `theory/DOUBLED_PAIRS_EXAMPLE_v1.md`, `theory/STAGED_SWAP_SHORTCUT_PROOF_v1.md`, and the scope/claims in `theory/SCIENTIFIC_REPORT_CANDIDATE_FA_v4.md`. This is a textual mathematical audit; it is not a source-code or capture audit.

1. **Finite-sample compatibility (T1): sound under the stated model.** Every positive forces its projection into that block's local language, so a negative is rejectable only if at least one block projection is absent from the positive projections. Conversely, those finite positive projection sets themselves are regular witness factors. The claim is existential over arbitrary regular local languages; it says nothing about the target's true factors or their state counts.
2. **Coarsening and binary meet (T1–T2): sound.** A coarse projection equality would imply equality after projection to every contained fine block, so a fine rejection witness survives merging. Any separation in a feasible partition induces a feasible bipartition by merging its blocks. Thus binary answers preserve all pairwise separations in the all-k sample-compatible family.
3. **Finest test and ambiguity (T3): sound as an order-theoretic sample claim.** Feasible partitions form a finite nonempty coarsening-closed poset. The meet is finest if and only if it is itself feasible. If it is infeasible, there cannot be a unique maximal refinement; the conclusion is at least two incomparable maximal refinements, not a computed frontier or kmax.
4. **Must-link and adaptive certificates (T4–T7): the stated implications follow.** Universally sound edges plus a feasible component partition prove that this partition refines every sample-compatible answer. Separator refinement preserves the meet invariant; a complete no-separator proof is needed for finality. A feasible partial meet is not itself a finality proof. An infeasible meet of already validated feasible partitions is a valid early ambiguity certificate by coarsening closure.
5. **Critical interpretation boundary.** None of T1–T7 identifies the generating partition. Even the `all-infinite-factor` construction only constructs one more regular completion of the observations. And a unique sample-finest partition can be finer than the physical factorization: the true factor may be prime as a *whole language*, while its restriction to the finite sample admits a split. The `N=∅` boundary noted by C007 is an especially clear warning: singleton sample-finest is vacuous, not evidence of singleton devices.
6. **Semantic boundary to check for the application.** C007 assumes arbitrary regular acceptor languages on finite words. If the intended data are execution traces of LTSs, whose trace sets are prefix-closed and contain ε, the input semantics and witness-language construction need to enforce those conditions. Henry's LTS semantics is prefix-closed; the C007 finite-projection construction was not stated as a prefix-closed construction. This is a model-alignment question, not a refutation of C007 within its written assumptions.

No logical counterexample to T1–T7 was found in this bounded review. This statement is not a formal proof-assistant check and does not certify the implementation.

### Separate review of C008 theory T6/T7 and L1

**Disposition: ACCEPT under the written assumptions.** I checked the projection/shuffle construction in `theory/OPTIONAL_COMPLETE_LANGUAGE_PROOF_v1.md`. In the converse direction of L1, nonemptiness lets us choose one local word per factor whose projection agrees on its intersection with B. Scanning the proposed B-word from left to right, we can emit from the owner factor the pending off-B prefix before each required B-letter, emit that letter, and finally emit the remaining suffixes. This preserves every factor's local order and produces a global shuffle with exactly the requested B-projection. Thus the stated projection identity holds.

Given that identity, T6 follows: each factor `π_B(L)` of the first decomposition is itself the shuffle of the projections onto `B∩C` from the second decomposition. The nonempty product condition also gives `F_B=π_B(L)`. Replacing all such factors yields a decomposition over the common refinement. Projection preserves regularity. T7 then follows because the common-refinement finest decomposition refines the actual partition; a strict split of an actual block would decompose its projected local factor, contradicting primeness. Hence the complete-language prime-partition conclusion is sound for a nonempty language, nonempty local factors, disjoint alphabets, and the declared independent shuffle semantics. It is not a finite-passive-sample certificate. The empty-global-language caveat in the theory file is necessary if empty local factors are permitted.

## A complete-language theorem that does identify a canonical partition

Let finite `Σ` have a nonempty regular language `L⊆Σ*`. A partition `Π` of `Σ` is a product decomposition when there are nonempty local languages `K_A⊆A*` such that

`L = {w∈Σ* : π_A(w)∈K_A for every A∈Π}`.

Call a local language `K⊆A*` **alphabet-prime** if there is no nontrivial disjoint split `A=U⊎V` for which

`K = {x∈A* : π_U(x)∈π_U(K) and π_V(x)∈π_V(K)}`.

### Theorem

If the same nonempty complete language L has two disjoint product decompositions whose local factors are all alphabet-prime, their alphabet partitions are equal up to permutation.

### Proof

Take a block `A∈Π`. Since all other local factors are nonempty, the projection of the complete product language onto A is exactly its local factor: `π_A(L)=K_A`. Suppose a second prime decomposition has blocks `B∈Λ` and factors `H_B`. Projecting that product onto A gives the product over all nonempty intersections `A∩B` of the projected local factors `π_{A∩B}(H_B)`. These intersections partition A. If two or more intersections were nonempty, this would be a nontrivial product split of `π_A(L)=K_A`, contradicting that `K_A` is prime. Therefore A is contained in one block B of Λ. By symmetry, each B is contained in one block A of Π. Since both are partitions, their blocks coincide up to order. ∎

For finite Σ, a prime factorization exists by repeatedly splitting any decomposable block; each split strictly increases the number of blocks, so the process stops after at most `|Σ|−1` splits. With regular L, projected factors remain regular. Thus the prime partition is a canonical property of the complete language. Exhaustively checking candidate partitions and exact regular-language equivalence is a finite, decidable route to compute it; no polynomial complexity claim is made here.

**Unknown-k consequence and what the theorem does not identify:** the prime partition itself determines k, so k need not be supplied if the hidden decomposition is assumed prime. Without that assumption, any two or more local factors can be merged into one factor on their union: define the merged language by requiring each old block projection to be in its old local language. It is regular and preserves exactly the same global L. Thus behavior alone cannot determine physical k. Nor can it determine physical names/IDs (permuting devices changes no language) or nonminimal internal state structures. Recovering physical ownership requires the additional assumption that the real architecture is exactly the prime factorization and an external convention mapping blocks to device IDs. This prime assumption also excludes packing behaviorally unused symbols into a larger physical factor.

## Finite passive traces: a bounded impossibility, then a sufficient condition

Counterexample family B in [`COUNTEREXAMPLES_V1.md`](COUNTEREXAMPLES_V1.md) proves: for every finite horizon h, there are two different k=2 partitions with infinite regular **prime** local factors whose complete global languages agree on every word of length at most h but differ later. Thus there is no one finite trace horizon that guarantees ownership uniformly over the unrestricted-state class. This is worst-case non-identifiability; it does not mean every finite dataset is ambiguous or that finite ownership certificates cannot exist.

One sufficient uniform-horizon route is available. Suppose every candidate global language is recognized by a complete DFA with at most Q states, and the passive sample contains the correct ± label for **every** word of length at most `H=Q²−1`. Any two such DFAs that disagree have a distinguishing word of length at most `Q²−1`: their symmetric difference is recognized by a product DFA with at most `Q²` states, and a shortest path from the initial pair to a disagreement state is simple. Therefore every bounded candidate consistent with this exhaustive sample has exactly the target global language. If the target factors are disjoint and alphabet-prime, the theorem above then identifies the alphabet partition up to permutation. This is a sufficient, potentially expensive coverage guarantee—not a necessary condition for a finite sample certificate.

For a known k and per-factor state bound q, the global product DFA has at most `Q=q^k` states (a sharper `Q=∏q_i` applies with individual bounds), yielding the brute-force horizon `q^(2k)−1`. If k is unknown but the alphabet has m symbols and blocks are nonempty/disjoint, `k≤m`, so `Q≤q^m`. These are sufficient but potentially enormous exhaustive horizons. More directly, a validated model class can supply any tighter known distinguishing-length bound H. Merely observing that the longest trace has length H, or running an RPNI-like learner on a finite sample, does not establish exhaustive coverage or that a characteristic sample has arrived. Other finite certificates do not need this route; they need a sound argument that rules out every remaining ownership alternative.

### General finite-sample criterion and T8

Let `C` be a declared class of candidate models, `S` a finite labeled sample, and

`V_C(S)={M∈C : M agrees with every label in S}`.

Assuming the true model is in C, its abstract ownership is determined by S relative to C iff

`{own(M) : M∈V_C(S)}`

is a singleton. The candidate models themselves need not form a singleton: different local DFAs or state encodings may induce the same ownership. This is a necessary-and-sufficient version-space criterion; to make it an operational certificate, the singleton claim must itself be proved under the declared class.

**T8 is one finite certificate and needs no state bound.** In the known-k candidate class, if trusted k is the true number of nonempty blocks and every graph edge is sound for every S-consistent model in C, each connected component lies inside an ownership block. Any admissible ownership partition must therefore be a coarsening of the graph components; when the graph has exactly k components and candidate models are restricted to the same trusted k, no component merge is possible. Hence the graph partition is the unique ownership in the version space. This is exactly the condition/proof in `theory/PROOFS_v1.md`, T8. It uses finite edge witnesses plus external trusted k, not a DFA-state bound. It is distinct from a uniform guarantee over all samples/models: T8 may fail to apply on samples lacking enough sound edges or lacking trusted k.

## Decision for C008

- Keep C007's result named **sample-finest compatibility**, and do not promote it to true ownership.
- If the research target is true ownership, state whether the objective is (a) canonical prime alphabet partition of the complete language, or (b) physical device identification. The former has the theorem above; the latter also needs external identity/provenance and a declaration that physical components are exactly prime factors.
- For passive finite logs, distinguish per-instance certificates from uniform guarantees. A verified singleton ownership version space or T8 can certify an individual finite sample without a state bound. To guarantee a finite horizon uniformly over unrestricted DFA sizes is impossible; a state/distinguishing bound plus complete coverage is one sufficient way to recover a uniform guarantee.
- If those conditions are unavailable, the honest attainable output is a set/poset of compatible partitions and factors, with explicit ambiguity; not one asserted true partition.

## Review limits

This is a bounded literature and proof review, not an exhaustive survey. No provider was run and no executable counterexample was tested. The mathematical constructions and sufficient-horizon route are proved directly above and in `COUNTEREXAMPLES_V1.md`. V1 remains unchanged as an audit trail of the overstrong wording. No C007 source, runtime, coordination, public document, or Git file was edited.
