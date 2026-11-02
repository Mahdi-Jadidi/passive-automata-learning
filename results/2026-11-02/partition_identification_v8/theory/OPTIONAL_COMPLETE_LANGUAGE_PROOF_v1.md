# C008 optional complete-language proof candidate

Independent review pending. Not needed for the finite-data impossibility result.
Definitions and T2 are in PROOFS_v1.md.

## 6. Optional separate proof candidate: complete nonempty language

This section is a new direct proof candidate for independent review. It is
not required by T1–T5, T8, T9 or the finite-data impossibility conclusion.
No independently accepted complete-language factorization theorem is claimed.

We give the full closure argument because importing finite-sample intuition
here would lead to a false impossibility claim.

**Lemma L1 (projection of a nonempty independent product).** Suppose
L=||_{C∈Q}G_C is nonempty. For any B⊆Σ,

    π_B L = ||_{C∈Q, B∩C≠∅} π_{B∩C}G_C.

Proof. Projection of any accepted global word satisfies the right side.
Conversely let w satisfy the right side. For each C choose u_C∈G_C with
π_{B∩C}u_C=π_{B∩C}w. Such a choice exists by the right-side condition;
for C∩B=∅ choose any u_C∈G_C, possible because L is nonempty.
Construct a shuffle of the u_C retaining w as its B-projection. Read w
left-to-right. For each next letter owned by C, emit from u_C its as-yet
unemitted prefix before that next B-letter (this prefix contains only
letters outside B), then emit the letter. After reading w, emit all remaining
suffixes of the u_C; they contain no B-letter. Each local order is preserved,
the global B-projection is w, and every local projection is u_C. This yields
an accepted global extension of w. ∎

In particular, for a nonempty independent product over Π, the factors are
necessarily F_B=π_B L: each local accepted word extends by shuffling any
accepted words of the other nonempty factors.

**T6 (meet closure).** If a nonempty language L decomposes over partitions
Π and Q, then it decomposes over their common refinement
R={B∩C: B∈Π,C∈Q,B∩C≠∅}.

Proof. By L1 and F_B=π_B L, each factor on B decomposes over the intersections
B∩C, with factors π_{B∩C}G_C. These equal π_{B∩C}L because G_C=π_C L.
Substitution into L=||_{B∈Π}π_B L gives exactly
L=||_{D∈R}π_D L. Regularity is preserved under projection. ∎

There are finitely many partitions of finite Σ. The one-block partition
always decomposes L. Repeatedly applying T6 to all decompositions produces
a unique finest decomposition Π*: it refines every valid decomposition
and itself decomposes L. Conversely every coarsening of Π* decomposes L
by merging factors. Thus the valid partitions for the **complete nonempty
language** are exactly the coarsenings of Π*.

**T7 (prime complete-language identification).** If the actual factors are
nonempty and prime, the actual partition equals Π*. Consequently complete
global membership plus these verified assumptions uniquely determines
the unordered physical ownership partition, even if k was initially unknown.

Proof. Π* refines the actual partition Π. If it split a block B of Π,
L1 or substitution of Π*'s factors would give a proper independent
decomposition of π_B L=F_B. That contradicts primeness. Hence Π=Π*.
Conversely any decomposable factor of Π* would produce a strictly finer
decomposition of L, contradicting fineness. ∎

Known k alone is weaker. If Π* has r blocks, complete-language-compatible
partitions with exactly k blocks correspond to partitions of those r atoms
into k groups. They number the Stirling number S(r,k), for 1≤k≤r; none
exist for k>r. In particular, k=r or k=1 gives a unique partition, whereas
1<k<r gives more than one. T2 has r=4 and known k=2, hence seven compatible
partitions, including the two displayed ones.

The nonempty hypothesis matters. For example on abc, use an empty unary
factor on a and a nonempty prime factor {b,c}*\{bc} on bc; alternatively
an empty unary factor on b and a nonempty prime factor {a,c}*\{ac} on ac.
Both global languages are empty and both partitions have k=2. Under a
convention permitting empty unary prime factors, all local factors are
prime. They remain indistinguishable even with complete membership.
Requiring every factor nonempty excludes this degeneracy.

T6/T7 are mathematical identifiability statements, not an assertion that a
finite passive learner receives a complete language or can certify primeness
from a finite log. T4 explicitly prevents that transfer without more structure.

