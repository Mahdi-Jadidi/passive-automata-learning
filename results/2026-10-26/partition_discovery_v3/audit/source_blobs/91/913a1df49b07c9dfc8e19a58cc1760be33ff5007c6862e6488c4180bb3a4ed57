# C003-B002: linear-size coverage for infinite regular targets

Scientific status: conditional mathematical derivation, implementation/fixtures
unexecuted and independently unvalidated. Parent: known sound must-link graph
r=k theorem from the prior theory notes. This instantiates that theorem and makes
no novelty claim. It does not assume singleton-word local languages.

## Family and explicit deterministic targets

Partition a known alphabet Sigma into exactly two nonempty blocks B0,B1. For a
block B with |B|>=2 choose an undirected spanning tree T (the candidate uses a
path). Let E_B contain BOTH length-two orientations ab,ba for each tree edge.
Define L_B = (union E_B)*. For a singleton B={a}, define L_B=(aa)*. Every local
language contains epsilon and has only even-length words. It is infinite: any
chosen length-two token can be repeated arbitrarily many times with distinct
lengths. Both global components are thus infinite regular languages.

An explicit deterministic DFA has accepting start q0, one pending-letter state
q_a for each a in B, and an absorbing dead state. From q0, a goes to q_a. From
q_a, b goes to q0 if ab is an allowed token, otherwise dead. All dead transitions
stay dead. For singleton B this is q0--a-->q_a--a-->q0. Token boundaries are at
even positions, so induction on processed pairs proves this DFA recognizes
exactly the token star. It has |B|+2 states and is not claimed minimal. The
explicit complete transition table uses O(|B|^2) entries; linear label size is
not a claim of a linear-size explicit DFA table or truth sidecar.

The global target is the intersection of inverse projections onto L_B0,L_B1.
It admits arbitrary interleavings of accepted local token strings. This differs
from the fixed-word route, which permits only one fixed projection per side.

## Labeled coverage set and its validity

S+ contains epsilon and ONE chosen oriented word ab per undirected tree edge
inside either block. It may also contain aa for each singleton block (the
candidate includes it). S- contains every one-letter word a for a in Sigma.

epsilon is accepted on both sides. An edge-word ab projects to an allowed token
on its owner's side and epsilon on the other; singleton aa does likewise. Every
negative a projects to an odd-length singleton word on its owner, which rejects,
and epsilon on the other side. Thus all labels match the declared infinite
targets, and positive/negative labels never conflict.

## Observed graph has exactly two connected components

For each observed tree edge's oriented positive ab, epsilon is positive, a is
negative, and inserting b into a gives the positive ab (or ba for reversed
orientation). The insertion-rescue rule therefore adds the must-link {a,b}.
Both endpoints are indeed in the same planted block. All tree edges appear,
so each block of size >=2 is internally connected. Singleton blocks are isolated
vertices, each already a connected component.

There are NO other cross-block edges in the observed swap/rescue construction:
a swapped length-two positive remains length two and cannot be a negative,
since all negatives are unary. Rescue begins from a unary negative and deletes
its only symbol to reach epsilon. A different inserted symbol gives an observed
positive exactly when those two distinct symbols form one chosen tree edge.
The optional aa gives no distinct-symbol edge. Consequently the graph's two
components are exactly B0 and B1, including singleton cases.

The insertion-rescue rule is necessary even for UNRESTRICTED regular factors:
if a,b belonged to different blocks, a's projection would match the rescued
positive on its owner, while the other side's projection would match epsilon.
Both sides would then accept the unary negative a. This contradiction does not
depend on the token-star target or a bound on the factors' state counts.

## Unique partition in the unrestricted regular-factor class

Every sample-compatible nonempty two-block partition must keep each graph
component indivisible. With exactly two components and exactly two nonempty
blocks, there is only one unordered assignment of those components to blocks.
The explicit targets above establish existence; equivalently the direct finite
positive-projection criterion validates that sole candidate. Therefore this
sample has a UNIQUE sample-compatible alphabet partition even among arbitrary
unbounded regular factors. This is stronger in model scope than the fixed-word
certificate, while relying on this special informative sample coverage.

This partition certificate does NOT identify the actual infinite local languages:
the finite positive-projection languages also fit the finite sample. It does not
infer infinity or a state bound from observations. Infinity is a fact of the
separately specified hidden targets, checked only by the auditor. No claim is
made that arbitrary passive sampling supplies these labels, that sparse traces
generally identify components, or that r=2 is necessary for uniqueness.

## Size and construction/search cost

The two trees have m-2 edges in total, m=|Sigma|. There are m negatives and
1+(m-2) positives, plus at most two optional singleton aa positives. Thus there
are 2m-1+s labels, s the number of singleton blocks with aa included. Word lengths
are at most two. For m>=4 there is at most one singleton block.

The prior witness_graph implementation considers each unary negative against
every possible inserted symbol, so its work is O(m^2) on these constant-length
words (hash-set membership under the usual expected-cost model). The resulting
graph has O(m) edges. General's quotient then has two ownership variables; its
continuing DFS visits only three prefixes, excludes the empty side and directly
checks its sole nonempty candidate. No learned cut or root restart is required.
The direct projection/witness work and output labels are O(m) on these samples;
the graph's O(m^2) phase remains. These are operation-count claims for this
family, not measured runtime or a universal speed comparison.

## Boundary and source distinctions

The theorem also applies at m=2 (two singleton components, optional aa/bb), though
the proposed 24-case corpus starts at m=4. Repeated-symbol target words arise
from token repetition; the target is never a singleton-word language. Removing
coverage labels can destroy this certificate without proving non-identifiability;
no necessity result or ablation outcome is asserted here.

Sources: prior C002 baseline/THEORY_NOTE.md and C003 general/PROOFS.md for the
must-link/quotient feasibility argument. No new literature search or novelty
assessment was performed for this fixture task. There is no counterexample
found by this static derivation; no experimental search was run or claimed.
