# C020 auditor protocol: large-state worlds and planted exact swap anchors

Read-only mathematical review of audit/PROTOCOL_V1.md as present before
generation. No generator executed or source cleared. Original seed/model/input
hashes and actual replay belong to the auditor's forthcoming evidence.

## Minimal local state count

Let states be Z/SZ, a(q)=q+1 modS, b any permutation, with only0 accepting.
Every state q is reachable by a^q. Distinct q,q' are distinguished by
a^((−q) modS): it reaches0 from q but a nonzero state from q'. Therefore
every state has a distinct right language and the complete DFA has exactly
S minimal states. Extra b transitions do not destroy this distinguishing
a-suffix. An a-cycle also makes the graph strongly connected.

Noncommutation of a and b means there exists q with

    u=δ(q,ab) != v=δ(q,ba).

Such a q must be verified from the complete saved tables. S=2 cannot have
a noncommuting permutation b, because both permutations commute with its
2-cycle; the planned S=64/256/1024 avoid this impossibility. As a simple
deterministic proof fixture for S≥3, b(q)=−q modS works: ab maps to −q−1,
ba to −q+1, distinct because S does not divide2. This fixture is not a claim
that the actual random b generator used reflection.

## Positive anchor and one negative per device

For device i construct local word

    a_i^S · a_i^q · a_i b_i · a_i^((−u) modS).

The first cycle visits all states and returns0; the next prefix reaches q;
ab reaches u; the last suffix repairs to0. The word is accepted. Swap ONLY
that displayed adjacent ab to ba while keeping the same repair suffix.
Its final state is v−u modS, nonzero, so it is rejected. This uses the
bijective a-cycle; simply choosing an arbitrary accepting repair in a
general DFA would not prove the swapped path remains rejecting.

Concatenate one accepted local anchor for each disjoint device. Its global
projections are those local words and it is positive. Swapping the planted
pair on device i leaves every other device's accepted projection unchanged
and makes exactly i reject. Independent full-DFA replay must verify every
emitted positive/negative, bounds and swap position. Each local length≤3S,
so total anchor length≤3KS; all actual lengths/duplicate checks still belong
to the frozen generator contract.

There is one forced edge for each two-symbol device. With m=2K the edges
form K components equal to truth. The truth partition fits every legitimate
base/anchor label. Thus known K gives unique sample-compatible ownership;
no-K still has all coarsenings of those components. No cross edge can be
sound against actual complete-world labels. Anchor state visits and label
effects must be reported separately from base sampling, since these anchors
can make observed inference easy despite genuinely large minimal DFAs.

The construction is deliberate informative acquisition, not evidence that
random passive logs spontaneously reveal every device. The saved-state
minimality proof is independent of whether base traces visit every state.

## Auditor handoff questions before source clearance

Please bind q/u/v and repair exponent to the actual table convention (ab
means first a then b), retain raw anchor positions and verify all swaps
against source word indices. Confirm the full a-cycle is in the positive
anchor before claiming observed all-state visitation, rather than only
declared/reachable state counts. Record any duplicate with base samples as
the protocol's explicit failure, not a silently changed class count.

Theory only inspected the preregistered design, not generator code. No new
test cell or direction is requested; existing bounded suite remains fixed.
