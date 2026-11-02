# C008 addendum — prefix-closed prime factors remain finitely ambiguous

Status: direct proof ready for independent review; no experiments, novelty
claim, or changes to the original PROOFS_v1.md / CLAIM_LEDGER_v1.json.
This is a separate application-alignment result for finite trace languages
of independent labelled transition systems (LTS).

## Assumptions and exact construction

Retain a known disjoint alphabet, independent shuffle composition, anonymous
global events and no bound on local DFA/LTS size. A trace language here is
prefix-closed: if w is possible then every finite prefix of w is possible.
Its words are finite executable event sequences; no termination marker or
acceptance-at-final-state requirement is added. Device IDs remain unobserved.

Fix any finite horizon L≥0. Choose an integer M≥1 with 2M>L. For each pair
of distinct letters x,y define

    F_xy = {w∈{x,y}*: x^M y^M is NOT a subsequence of w}.

Subsequence means deleting any positions while retaining the remaining order;
the matched positions need not be adjacent. Use the two partitions

    Π₁ = { {a,b}, {c,d} },   factors F_ab, F_cd,
    Π₂ = { {a,c}, {b,d} },   factors F_ac, F_bd.

The true component count is the same known k=2 in both models.

## P1. Each local factor is nonempty, infinite, regular and prefix-closed

Nonempty and infinite: ε and every unary word x^r or y^r are accepted,
for every integer r≥0; no such word can contain both required letters.

Regularity: let t=x^M y^M, of length 2M. A DFA has states q=0,...,2M,
initial state 0, accepting states 0,...,2M−1, and rejecting absorbing state
2M. At state q<2M it advances to q+1 if the next letter equals t[q], and
otherwise stays at q. The state records the longest prefix of t that is a
subsequence of the input consumed so far. This invariant holds initially.
An extra letter can extend that prefix by at most one; if it matches the
next required letter, extending greedily is optimal, and otherwise no longer
prefix can become realizable. This proves the invariant by induction. Thus
state 2M is reached exactly when t has occurred as a subsequence. The DFA
accepts exactly F_xy.

Prefix closure: if a prefix u of an accepted word w contained t as a
subsequence, the same positions would make t a subsequence of w, a
contradiction. In fact this language also closes under deleting arbitrary
letters, which is stronger than required.

LTS realization: delete the rejecting state and every transition entering it
from the DFA above, retaining all other states as executable states. A word
is the label of a path from state 0 precisely when the DFA never enters its
rejecting sink, equivalently when it belongs to F_xy. All reachable LTS
states can end a finite trace. This gives a finite partial deterministic LTS
with exactly this trace language. State size grows with M; no uniform state
bound has been assumed. ∎

## P2. Each local factor is prime for independent disjoint composition

The only proper partition of {x,y} is {x}|{y}. Its two projections satisfy

    π_{x}F_xy = {x}*,   π_{y}F_xy = {y}*.

Indeed every unary word is itself accepted, and projection cannot introduce
other letters. Suppose F_xy were an independent unary product A||B. Both
factors must be nonempty because F_xy is nonempty. In a nonempty independent
product, projection onto one block equals its factor: every accepted local
word extends by shuffling any word of the other factor, and every global
word projects to a locally accepted word. Therefore A={x}* and B={y}*.
Their product is {x,y}*, which accepts x^M y^M, whereas F_xy rejects it.
This contradiction proves primeness, even if potential unary factors are
allowed to be arbitrary languages rather than just regular ones. ∎

## P3. Identical bounded observations, different true ownership

Let L₁ and L₂ be the global languages of the two models. Every word w
with |w|<2M is accepted by both. Its projection on any block has length
at most |w|, so cannot contain a subsequence of length 2M. Consequently
both models agree on **every** word through the specified horizon L,
not merely on the words selected for the log.

The full global languages are different. For w=a^M b^M, model Π₁ rejects:
its ab projection is exactly the forbidden subsequence. Model Π₂ accepts:
its ac projection is a^M and its bd projection is b^M, both accepted unary
words. This distinguishing word has length 2M, and no shorter distinguishing
word exists because both languages contain every shorter word.

The global languages are prefix-closed as well: projection of a global
prefix is a prefix of each corresponding local projection, and each local
language is prefix-closed. Their global LTSs can be realized by the ordinary
asynchronous product of the local partial deterministic LTSs. Thus this is
an actual pair of finite independent LTS models with different symbol
ownership, known k=2, infinite prime prefix-closed factors, and indistinguishable
bounded traces. ∎

## P4. Consequence and limits

For every finite horizon, the two models meet all the stated restrictions
yet induce identical observations through that horizon. The version-space
criterion T1 therefore forbids a universal guaranteed ownership identifier
from finite positive-only logs, even under known k and local primeness in
the prefix-closed/LTS setting. An exhaustive list of all feasible traces
through that horizon is also insufficient for this family.

Important scope: all words through the horizon are positive in this particular
construction. It does **not** supply a bounded sample with both positive and
negative labels under prefix-closed factors. The earlier parity-deletion
construction in PROOFS_v1.md T4 does supply mixed labels, but its factors
are not generally prefix-closed. These results must not be combined into
an unproved mixed-label prefix-closed assertion.

Nor does P3 assert equal complete languages: a^M b^M explicitly distinguishes
them. It is compatible with the separate optional complete-language prime
decomposition theorem. It does not say every finite dataset is ambiguous;
trusted known-k sound must-link certificates can identify some datasets.
The obstruction is to a guarantee uniform over this unbounded-state class
without extra verified information about unseen behavior.

An absent word in an ordinary positive log is not a negative label. In a
real LTS application, the source and semantics of any asserted negative
trace must be established separately. No timed scheduling, fairness, finite
sampling distribution, maximum state size, or hidden physical device ID is
inferred from this construction.

## Refutation attempts and decision

1. Could accepting all unary traces make the factor decomposable? No: a
   unary independent decomposition would then be universal, contradicted
   by the rejected ordered word (P2).
2. Does deletion of a subsequence condition violate prefix closure? No: a
   forbidden subsequence in a prefix persists in every extension (P1).
3. Might global interleavings expose a difference before 2M? No: projection
   only shortens words, so no local forbidden subsequence can occur (P3).
4. Does a complete DFA's rejecting state make this unlike executable LTS
   traces? No: removing the sink and its incoming transitions realizes the
   prefix-closed trace language exactly (P1). A requirement that every
   event be enabled in every state would be a different, stronger model.
5. Does this prove arbitrary mixed-label finite samples are ambiguous?
   No. That attempted extension is unsupported and is not claimed (P4).

Decision: candidate is mathematically sound under the assumptions stated;
independent review is pending. No executable experiment was needed or run.
