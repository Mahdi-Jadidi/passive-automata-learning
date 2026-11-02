# C008 theory — preserved candidate approaches and decisions

Documentation only. These were mathematical candidate directions, not executed
programs. No source versions, run logs, seeds or measured outputs exist for
them; those fields are **not applicable / not available**, not reconstructed.

## FC01 — Universal factors as the only ownership counterexample

Idea: assign Σ_B* to every local factor; all partitions yield Σ*.
Decision: mathematically valid but insufficient as the principal example
because it is trivial and does not address nontrivial accepted/rejected words.
Replacement, retained separately in PROOFS T2: even counts of every letter,
same k=2, infinite proper local/global languages and exact equality on all words.

## FC02 — Parity grouping proves impossibility even for prime factors

Idea: use the same even-count product under ab|cd and ac|bd and call the local
pair factors prime. Decision: REJECTED. Each pair language is a product of
two unary parity languages. This is a failed strengthening, not a failure of
the unrestricted same-k counterexample. Repaired finite-data construction:
T4 removes one unseen long word from each pair factor, making each prime.

## FC03 — Seek distinct prime nonempty decompositions of one complete language

Idea: strengthen finite-data impossibility to complete membership while keeping
nonempty prime local factors. Decision: REJECTED under the specified disjoint
independent-product model. Projection lifting proves meet closure; the unique
finest complete-language decomposition is exactly every prime decomposition
(T6/T7). Shared symbols, synchronization or empty factors change assumptions
and cannot be silently inserted. Empty-language degeneracy is preserved in T7.

## FC04 — Known k plus local primeness suffices on finite labelled logs

Idea: exclude arbitrary coarsening with known k and exclude decomposable factors
with primeness, then claim true identification. Decision: REJECTED by T4.
Different prime products agree on all words through an arbitrary finite cutoff;
the unknown coupling is beyond that cutoff. No finite experiment disproves
the universal theorem; the explicit construction proves the counterexample.

## FC05 — C007's unique finest sample partition is automatically physical

Idea: read the algorithm's uniqueness certificate as true per-symbol ownership.
Decision: REJECTED without additional verified assumptions. Sample-compatible
coarsenings are still alternatives. Complete-language prime decomposition and
known-k sound-component certificates are distinct qualified routes (T7/T8).

## FC06 — Unknown k is always impossible, even with complete language and primes

Idea: use coarsening for every model class. Decision: REJECTED as overbroad.
Merging prime factors generally creates decomposable factors and leaves the
prime-restricted class. T3 applies to the unrestricted class; T7 identifies
the partition for a nonempty complete language in the prime class.

## FC07 — Missing must-link coverage proves non-identifiability

Idea: if a chosen graph leaves r>k components, declare ownership ambiguous.
Decision: REJECTED. It only fails that certificate; additional constraints may
identify ownership. The sufficient r=k condition assumes trusted true k and
sound edges. Coverage of the actual blocks cannot be assumed from sparse logs.

## FC08 — Correct blocks identify named devices

Idea: report ab belongs to device 1 solely because ab is a certified block.
Decision: REJECTED for anonymous observations. Device-name permutation leaves
all observations fixed (T9). Identity anchors are separate information.

All decisions are proved in PROOFS_v1.md. Experimental execution status for
this note: no experiments. Scientific statuses are qualified mathematical
confirmation or rejection, not measured run success/failure.
