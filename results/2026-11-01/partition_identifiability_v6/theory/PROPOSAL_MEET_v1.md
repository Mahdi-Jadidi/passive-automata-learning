# C006-T005: meet of all compatible bipartitions (separate future proposal)

Status: THEORY DERIVATION ONLY, independent review pending. No runtime activation,
provider change, experiment, counterexample search, performance claim or novelty
claim. Frozen v5 decision delivery/gates retain priority. Requires a COMPLETE
compatible-bipartition set, never a first answer, truncated enumeration or sample
of answers. Depends on T1/T2 in PROOFS_v1.md, not fixed-word assumptions or q.

Let F be all sample-compatible unordered partitions of the known finite alphabet
A. For consistent labels it contains the one-block partition. Let B be its
two-block members. Write pi <= rho when pi REFINES rho. Let E_pi relate letters
in the same block of pi. Define E_M=intersection_{beta in B} E_beta. The empty
intersection is A x A, so when B is empty M is the one-block partition, NOT the
singleton partition. Intersections of equivalence relations are equivalences;
M is well-defined even if it is not itself feasible.

## K1. Bipartitions determine all universally inseparable pairs

Claim: intersection_{pi in F} E_pi = intersection_{beta in B} E_beta.
One inclusion follows from B subset F. For the other, suppose some pi in F
separates letters a,b. It has at least two blocks. Coarsen it into the block
containing a and the union of all its other blocks. This is a nonempty
bipartition separating a,b and belongs to B by coarsening closure. Thus every
separation anywhere in F is witnessed by a compatible bipartition. Contraposition
proves equality of the intersections. With B empty, T3 gives F={one-block},
consistent with the explicitly universal empty intersection.

Consequently M is the meet of ALL feasible partitions, not merely the meet of
binary answers. M refines every member of F. It records universal same-block
relations; different M blocks need not be simultaneously separable in ONE
feasible partition. This last distinction is exactly why checking M matters.

## K2. A unique finest feasible partition exists iff M is feasible

If T1 accepts M, it is feasible and refines every feasible partition by K1, so
it is the unique finest feasible partition. In fact F then consists EXACTLY of
all coarsenings of M: one direction is K1, the other is coarsening closure.
Conversely if a finest feasible partition f exists, E_f is contained in every
E_pi and appears in that intersection, so E_f=E_M and f=M. Hence M is feasible.
No promise that the intersection of feasible partitions stays feasible is made.

If M is infeasible, the finite nonempty refinement poset F has at least TWO
distinct refinement-maximal members (i.e. members having no strictly finer
feasible partition). For if it had only one such member f, refining any pi
inside finite F eventually reaches a maximal member, necessarily f. Then f
refines every pi, is finest, and K2 would force M=f feasible, a contradiction.
"Maximal refinement" here does not mean merely largest numerical block count.

## K3. Exact unique binary answer and conditional true k

If B={beta}, no feasible partition with k>=3 can exist: take a block C1 versus
the rest and a DIFFERENT block C2 versus the rest. For >=3 nonempty blocks these
give distinct unordered compatible bipartitions by coarsening. This contradicts
|B|=1. Thus F={one-block,beta}, kmax=2, and beta is the unique finest member.
Under the ADDITIONAL promise that the actual hidden target has a nontrivial
decomposition in the declared model, its declared k is therefore 2 and its
partition is beta. Without that promise, k=1 remains indistinguishable. If B is
empty, every feasible architecture has k=1 (assuming a true target within the
declared regular model); this is nontrivial impossibility, not no regular model.

## Retained boundary examples (proof examples, not new runs)

* A=abc, P={epsilon,abc}, N={a}: B consists of ab|c and ac|b. Their meet is
  a|b|c, which fails T1 since epsilon is seen on each singleton for negative a.
  Two incomparable maximal refinements exist. This example was captured in
  the prior theory smoke; this proposal does NOT claim a new captured experiment.
* N empty: every partition feasible, M is the singleton partition for |A|>=2,
  which is uniquely finest; hidden k may nevertheless be ANY 1..|A|.
* A=ab, P={a,b}, N={epsilon}: B empty; M is one-block and feasible. This avoids
  an incorrect empty-intersection implementation producing singleton blocks.
* A=abc, P={epsilon,abc}, N={a,b}: only binary ab|c fits. The singleton
  partition fails. Conditional on nontrivial hidden architecture, k=2 follows;
  one-block remains a possible unconstrained explanation.

These examples illustrate the proved statement rather than refute it. No
counterexample found by execution or independent acceptance is claimed.

## Future API caution

This is a possible OPTIONAL unknown-k convention/frontier feature: form M only
after certified complete binary enumeration, run T1, and report finest_unique
or multiple_maximal_exist. The latter establishes existence, not an enumeration
of frontier members. It does not compute hidden architecture absent the declared
convention, and it can require exponentially many binary answers. Complete
v5 output could supply B in principle; no code or API is added in this cycle.
