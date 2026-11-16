# C026 counterexamples and boundaries v1

These are direct constructions; no experiments were run for this document.

## CE1: unique optimum is not unique compatible ownership

Sigma={a,b}, P={epsilon}, N={a}. The singleton partition a|b rejects a through its a-factor and uniquely maximizes block count at two. Oneblock is also compatible. Optimal tie uniqueness and all-K ownership uniqueness must be separate fields.

## CE2: maximum recommendations need not form a merging chain

Sigma={a,b,c}, P={epsilon,abc}, N={a}. Exactly the two cuts ab|c and ac|b are compatible; singleton blocks fail, so both maximize at two. Choose ac|b as an old optimum. Add negative b. Only ab|c remains as a two-block optimum: both a and b have unseen projections on ab. The old ac|b cannot become ab|c by merging. Its only strict coarsening is oneblock, which is suboptimal. This construction is retained from C006 PROPOSAL_MEET_v1.md, not new C026 evidence. The general statement concerns an arbitrary selected old optimum; the implementation's lexicographic convention selects ab|c for this exact ordering. To force its canonical selection to change, instead extend N={a} by negative c: only ac|b survives, whereas the old canonical optimum was ab|c.

## CE3: incomplete observed cuts do not determine a finest answer

In the initial CE2 sample, the meet of the two compatible cuts is a|b|c and is incompatible. Pairwise possible separations cannot necessarily be realized simultaneously. Maximum block count and meet-based unique finest are distinct targets.

## CE4: finite primeness does not exclude oneblock

Given any finite disjoint P,N over nonempty Sigma, choose t outside P and let F=Sigma* minus (N union {t}). F is cofinite, infinite and nonuniversal. Every proper-subalphabet projection is universal, so F is prime (unary primeness is conventional). It fits the labels with oneblock. This is a universal construction, even if a nontrivial prime-factor system generated the sample.

## CE5: no uniform target-independent length bound

For Sigma={x,y}, choose long t containing both symbols and let L=Sigma* minus {t}. L is prime because both unary projections are universal. Every word shorter than |t| is accepted, so observations confined to that length admit x|y. A witness of the coupling needs to encounter the omitted behavior. Q in the Q^3 theorem depends on the target; removing it would give an invalid uniform horizon claim.

## CE6: empty complete language needs separate treatment

Over abc, an empty unary factor on a and a nonempty prime factor on bc give empty global L; an empty unary factor on b with a prime factor on ac gives the same global language. Nonempty L, and therefore nonempty factors, is essential for factors-equal-projections and physical-prime uniqueness. The C026 characteristic/convergence theorem explicitly excludes empty L.

## CE7: partial block conflicts can disappear after expansion

P={ab}, N={ba}. Singleton projections collide with positives, while oneblock rejects ba. A growing block that currently rejects no uncovered negative cannot be discarded merely for that reason. Candidate blocks may also cover no negatives when other blocks supply coverage. The valid prune asks whether the ENTIRE remaining union can reject every uncovered negative.

## CE8: persistent computation limits are not convergence assumptions

The informant theorem concerns the exact maximizer on each finite prefix. A solver repeatedly interrupted before its difficult root subproblem finishes can remain unresolved at all prefixes. Eventual arrival of characteristic observations alone does not prove a fixed-quota implementation eventually certifies optimality.

## Failed routes retained before implementation

1. Stopping after two equal incumbents: a larger unvisited completion may remain; two incumbents certify all-K ambiguity, not optimality.
2. Pruning all branches whose bound equals the incumbent: loses optimal ties and may lose the canonical least optimum.
3. Counting only visible transitions in the epsilon product: does not bound lengths of accepted lifts. The accepted proof counts every transition in a simple accepting path.
4. Calling the DP recurrence new: it is C009's canonical count DP evaluated with max-plus values and saturated optimal tie counts.
5. Treating primeness as a finite-data identifier: Theorem 1 disproves this for the unrestricted regular class.
6. Treating characteristic-sample existence as a stopping certificate: future prime oneblock completions persist at every finite sample.

No failed document drafts were overwritten: this is the first theory draft. Future rejected revisions should be retained separately.
