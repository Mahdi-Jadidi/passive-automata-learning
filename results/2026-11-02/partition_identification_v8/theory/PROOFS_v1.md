# C008 — Identifying physical ownership from passive observations

Status: direct mathematical proofs under the explicit assumptions below; no
novelty claim and no experimental claim. This note distinguishes an unordered
partition of symbols from a mapping to named physical devices.

خلاصه: دادهٔ متناهی به‌طور عمومی مالکیت واقعی را تضمین نمی‌کند، حتی اگر k
معلوم و تمام عوامل واقعی تجزیه‌ناپذیر باشند. زبان کاملِ ناتهی، همراه با
تجزیه‌ناپذیری تمام عوامل، افراز انتزاعی را تعیین می‌کند؛ نام دستگاه‌ها همچنان
به اطلاعات هویتی نیاز دارد. شرط کافیِ قابل بررسی با دادهٔ متناهی نیز ممکن
است، ولی فقط در یک کلاس مدلِ محدودشده و با فرض‌های تأییدشده.

## 1. Model, observations and target

Let Σ be a finite nonempty known alphabet. A partition Π consists of nonempty, disjoint
blocks covering Σ. A model M=(Π,(F_B)_{B∈Π}) assigns each block a regular
language F_B⊆B*. Its global language is

    L(M) = {w∈Σ*: for every B∈Π, π_B(w)∈F_B}.

Here π_B erases letters outside B and preserves local order. There are no
shared symbols, synchronization side conditions, noise, hidden context labels,
or bounds on DFA states unless explicitly added to the model class. The
language is shuffle composition, not concatenation of local words.

A finite labelled observation is S=(P,N), with P∩N=∅ and all words complete.
Consistency means P⊆L(M) and N∩L(M)=∅. Positive-only observations set N=∅.
Complete-language observation means knowing membership of **every** finite
word; it is an information-theoretic object, not an available finite log.
No passive sampling distribution or coverage guarantee is assumed.

The ownership target own(M) is initially the **unordered partition** Π.
Physical device IDs are treated separately in §8. A nonempty local language
is prime/indecomposable if it has no representation of the same independent
form over any proper partition of its own alphabet. Regularity of candidate
factors is required. One-letter factors are prime by definition.

## 2. Exact identification is a version-space property

Fix a declared model class C containing the true model. Define

    V_C(S) = {M∈C: M is consistent with S},
    T_C(S) = {own(M): M∈V_C(S)}.

**T1.** Assuming V_C(S) is nonempty, a partition is guaranteed correct from S
under C if and only if T_C(S) is a singleton.

Proof. If T_C(S)={Π}, every possible true model has ownership Π. Conversely,
if two consistent models have different ownerships, the identical input S
can arise with either model as the truth. Any proposed answer is wrong in at
least one of those worlds. Randomization cannot provide a probability-one
correct answer in both worlds, because its output distribution is the same
on identical input. Abstention is valid but does not identify ownership.
An empty version space signals violated assumptions/inconsistent data; the
vacuous universal statement is not an identification certificate. ∎

This theorem is information-theoretic. It does not assert an efficient or
decidable implementation for every restricted model class. Sound guarantees
depend on the **true** system belonging to the specified class.

## 3. Complete language still need not identify ownership

**T2: nontrivial same-k complete-language ambiguity.** Let Σ={a,b,c,d} and

    E_B = {u∈B*: every letter of B occurs an even number of times in u}.

Take Π₁={ab,cd} and Π₂={ac,bd}, with local factors E_B. Both models have
known k=2 and nonempty infinite regular factors. Their global language is

    E_Σ = {w: #a(w),#b(w),#c(w),#d(w) are all even}.

Proof. In either grouping the four local parity conditions are exactly the
four global parity conditions. A DFA for a two-letter factor tracks its
two count parities. The language accepts ε, aa and aabb, and rejects a and
ab, so it is neither empty nor universal. Π₁≠Π₂ but membership agrees on
every word, hence also on every possible passive log or membership answer.
No algorithm can distinguish these ownerships from language alone. ∎

The pair factors here are decomposable into unary even-count languages.
Thus T2 does **not** establish complete-language ambiguity under prime-factor
assumptions. That stronger attempted claim is false for nonempty languages;
see optional T7 in OPTIONAL_COMPLETE_LANGUAGE_PROOF_v1.md. T2 nevertheless refutes any unrestricted same-k guarantee.

**T3: unknown-k coarsening ambiguity.** For any model with at least two
blocks, merge two blocks B,C and replace their factors by

    H={u∈(B∪C)*: π_Bu∈F_B and π_Cu∈F_C}.

H is regular (inverse projection and intersection preserve regularity), and
substitution leaves the global language unchanged. Repeated merging yields
a one-block explanation with the same complete language. Consequently an
unrestricted class with unknown k cannot identify a nontrivial physical
partition. This argument permits decomposable merged factors; it must not
be used to refute T7 under a prime-factor restriction. ∎

## 4. Finite labelled ambiguity even with known k and prime factors

**T4.** For every finite length bound ℓ≥0, there are two different ownership
partitions with the same known k=2, nonempty infinite regular **prime**
local factors, and identical membership on every word of length ≤ℓ.

Construction. Set Σ={a,b,c,d}, Π₁={ab,cd}, Π₂={ac,bd}. Choose integer M≥1
with 4M>ℓ. For each ordered pair x,y used as a block, set

    F_xy = E_{x,y} \ {x^(2M)y^(2M)}.

Use these factors for each partition. They are regular: a finite-state
parity test intersected with the complement of one fixed word. They are
nonempty and infinite; for example x^(2r) is accepted for every r≥0.

Primeness proof. The only proper partition of {x,y} is {x}|{y}. Both unary
projections of F_xy are exactly even-count unary stars: parity excludes
odd counts; each even x-word and each even y-word is itself in F_xy,
because the forbidden word contains positive counts of both letters.
If F_xy were an independent unary product, its factors would equal these
projections (both are nonempty). That product accepts x^(2M)y^(2M), a
contradiction. Therefore every two-letter factor is prime.

Agreement proof. A global word of length ≤ℓ cannot have a block projection
equal to a forbidden word of length 4M. Thus on these words both models
accept exactly when every letter has even count. They agree on the whole
bounded universe, not merely on a selected training sample. In particular,
any finite labelled sample from E_Σ with maximum length ℓ fits both models.
For ℓ≥1, this can contain both positive (ε) and negative (a) observations.

The two full global languages are genuinely different: w=a^(2M)b^(2M)
is rejected by Π₁'s ab factor, but accepted under Π₂ because its ac and bd
projections are a^(2M) and b^(2M), respectively. Thus this is finite-data
ambiguity, not complete-language ambiguity. The missing coupling occurs
outside the observed length range. ∎

Consequences. Known k, factor primeness, exact negatives, and exhaustively
labelling every word up to any finite cutoff do not yield a universal
finite-data ownership guarantee when state size is unbounded. This is an
existential obstruction to a universal guarantee; it does not claim that
every finite sample in every restricted class is ambiguous. It also does
not forbid eventual identification for a fixed target under additional
coverage, state or sampling assumptions. No such assumptions are silently
present here.

## 5. Positive-only finite logs are weaker still

**T5.** Given any finite positive-only sample P and any proposed partition
Π, there is a model with partition Π, all local factors nonempty infinite
regular and prime, that accepts P.

Proof. Let ℓ=max({|p|:p∈P}∪{0}). For each block B choose a word t_B∈B*
of length >ℓ and let F_B=B*\{t_B}. It is nonempty infinite and regular.
If |B|=1 it is prime by convention. For |B|≥2, every projection onto a
proper nonempty D⊊B is D*: for any v∈D*, append a sufficiently long word
over a letter of B\D to obtain a word unequal to t_B with projection v.
Hence if F_B decomposed over any proper partition, all its projected factors
would be universal and their product would be B*, contradicting t_B∉F_B.
Thus F_B is prime. Every projection of a positive has length ≤ℓ and is
accepted. ∎

Therefore, whenever the permitted k allows two distinct partitions,
finite positive-only logs do not guarantee ownership even under primeness.
Without primeness, universal local languages already suffice. A known
length bound on the *observed log* is not a bound on future behavior.

## 6. Complete-language prime-factor question: separate optional proof

The full direct proof candidate for L1, T6 and T7 is preserved separately
in OPTIONAL_COMPLETE_LANGUAGE_PROOF_v1.md. Independent review is pending.
It is not a dependency of the finite-data impossibility, T8, T9 or T10.
Its nonempty hypothesis and distinction from finite logs are explicit there.

## 7. An attainable finite-data target with verified extra information

**T8 (known k and sound must-link certificate).** Assume the true model is
in the declared class, its exact number of nonempty ownership blocks is a
verified k, and a graph G on all symbols has edges proven to join symbols
that co-own in **every** S-consistent class model. If G has exactly k connected
components, those components equal the true ownership blocks.

Proof. By edge soundness and transitivity, each graph component lies within
one true block. Thus the true partition is a coarsening of the component
partition. A proper coarsening decreases the number of nonempty blocks;
both counts are k, so no merge is possible. ∎

The count r=k is checkable once the graph and trusted k are supplied.
The truth of k is an external assumption, not inferred merely by counting
components. Edge proofs can be checked against fixed labels without new
queries. A simple sound rule is a positive p and negative n obtained by
swapping adjacent unequal letters x,y: if their owners differed, every
block projection would be unchanged, forcing n accepted whenever p is.
Therefore x,y must co-own. Another rule applies when a positive/negative
pair have identical projections under every partition separating x,y;
that stronger premise needs its own proof, not a heuristic correlation.

Coverage (“enough observed witnesses connect every actual block internally”)
is a sufficient **data-generation condition**, not automatically a property
one can verify against the unseen truth. With trusted k and sound edges,
the observable condition r=k certifies sufficient coverage. With r>k,
this particular certificate is inconclusive; identification by other valid
constraints may still be possible. Edge incompleteness is not a proof that
the actual system has more blocks, nor proof of non-identifiability.

More generally any extra assumptions making T_C(S) a verified singleton
make the abstract ownership target attainable by T1. Examples include
trusted ownership anchors, a correctly specified finite candidate class
whose remaining models agree, or a completeness guarantee that actually
determines the global language combined with T7. A state/length bound or
coverage slogan alone is not a proof: the required distinguishing coverage
or residual version-space singleton still must be established.

## 8. Device IDs versus blocks

**T9 (label symmetry).** If a model has k abstract blocks assigned to k named
devices but the observations contain no device-identifying metadata, permuting
device names leaves L(M) and all global labels unchanged. For k≥2, a correct
unordered partition therefore does not uniquely identify the named-device
ownership map.

Proof. Composition depends only on which local words are accepted by each
block, not on the string used to name its device. Relabelling devices changes
the requested map but not any observation. Apply T1 to the stronger map
target. In a fully symmetric class there are k! such assignments. Trusted
anchors or identity-bearing event metadata can break the symmetry, but
they are additional information beyond anonymous global traces. ∎

## 8A. Honest exact identification algorithm for the unrestricted sample class

**T10 (finite exact identifier).** Restrict C here to arbitrary regular local
factors on the known disjoint Σ, with either a trusted exact k or no k
restriction. Do not additionally require prime factors, state bounds, or
other conditions without changing the feasibility test.

For a candidate partition Π define the local finite languages
H_B={π_Bp:p∈P}. The partition is feasible if and only if

    for every n∈N, some B∈Π has π_Bn∉H_B.

Necessity: any consistent factor must contain every projection of a positive;
if every negative projection occurs among positive projections on its block,
every factor would accept that negative. Sufficiency: choose F_B=H_B. These
finite languages are regular, accept every positive globally, and the displayed
condition rejects every negative. They are explicit countermodels, not claims
about nature's full local languages. If P is empty, all H_B are empty and
the resulting empty global language is a valid witness for this unrestricted
class. Exact negative labels alone do not certify nonempty true factors.

Bounded pseudocode (a stop is a real computational cutoff, not proof):

```text
identify(S, Σ, trusted_k=None, budget):
    answers = []
    for Π in all unordered partitions of Σ, in a fixed canonical order:
        if budget exhausted: return UNKNOWN, answers, complete=false
        if trusted_k is supplied and |Π| != trusted_k: continue
        construct H_B = projections of P on B
        if every negative has an H_B-rejecting projection:
            save (Π, explicit finite regular factors H_B)
            if two distinct partitions saved:
                return NOT_IDENTIFIABLE, two countermodels,
                       search_complete=false, conclusion_certified=true
    if no partition saved:
        return INCONSISTENT_WITH_DECLARED_MODEL, complete=true
    return IDENTIFIED_PARTITION, sole partition and witness, complete=true
```

The two-model return needs no full enumeration: two valid incompatible
ownership explanations already refute guaranteed uniqueness. Its search is
not exhaustive but its non-identifiability conclusion is certified. A cutoff
with zero or one saved answers is UNKNOWN, never inconsistency or identification.
A proof-producing alternative may establish uniqueness without enumerating
every partition (T8), but missing search branches cannot be assumed impossible.

Proof of algorithm. There are finitely many partitions. The feasibility
equivalence above means enumeration visits exactly the ownership image of
the unrestricted version space, or the trusted-k slice. The three completed
cases and the two-model early exit follow from T1. All reported models are
independently checkable against the finite sample using their explicit factors.
Regular DFA implementations can use tries with a rejecting sink for H_B. ∎

With unknown k in this unrestricted class, a consistent labelled sample
always has the one-block explanation F_Σ=P. If any nontrivial feasible
partition exists, it and the one-block model give different ownerships.
Thus the only uniquely identifiable physical partition in this class is
the one-block partition, when all nontrivial partitions are infeasible.
This situation can occur: on Σ={a,b}, P={ab}, N={ba}, the singleton split
accepts ba whenever it accepts ab, so only the one-block partition fits.
Accordingly, the theorem does **not** say that every finite dataset is
ambiguous. With trusted known k>1, T8 can likewise identify a true nontrivial
partition on suitable finite data. The guarantee is always conditional on
the declared class actually containing the true system.

## 9. What C007 established, and what it did not

C007 selected the finest partition consistent with a finite labelled sample
when that partition exists, and otherwise certified multiple maximal sample
partitions. Its exact projection criterion concerns sample consistency.
These are useful structural computations but are a different target from
unrestricted true ownership.

A unique sample-finest answer does not establish that nature chose it:
every coarsening remains sample-consistent in the unrestricted class. Even
complete-language fineness needs a prime-factor assumption to coincide
with the actual ownership. Finite sample fineness and complete-language
fineness must not be equated. A local finite witness language is not evidence
that the real factor contains only those observed projections.

The number of successful adaptive meet refinements, test-set exactness,
scaling to many symbols, and ability to replay a certificate do not supply
missing identifiability information. They certify their declared sample
target. C008 must report impossibility for the unrestricted physical target
and explicitly state the additional assumptions for every attainable variant.

## 10. Scope and preserved rejected directions

These are direct proofs (with §6 explicitly separated for independent review),
not novelty assertions. No executable experiment
was used to establish universal claims. The companion CLAIM_LEDGER_v1.json
indexes assumptions/status, and FAILED_CANDIDATES_v1.md records why simpler
or stronger attempted conclusions fail. Nothing here claims a real dataset,
new learner, practical state bound, statistical coverage rate or physical
device metadata that was not supplied.
