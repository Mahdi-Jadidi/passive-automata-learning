# Mandatory interpretation of the C007 proofs

The separator "oracle" in PROOFS_v1.md is an INTERNAL exact search/computation
over the SAME fixed finite P,N. It makes no membership or equivalence query to
the real system, adds no observations and does not request missing coverage
words. Oracle calls are computational subproblems, not active-learning queries.
All returned partitions/collision witnesses must use only the given labels.

With N empty, every partition is feasible, hence the chosen unique finest is
the singleton-letter partition (also when P contains only one complete word).
This is an extreme consequence of the SAMPLE target convention, not a recovery
of each real component as one letter. A real target with larger multi-letter
blocks, or its coarsenings, can have precisely the same observed positives.
No-positive data has the analogous vacuous-feasibility convention. The explicit
infinite-factor constructions and whole-language merging in PROOFS_v1.md further
show why observed finest uniqueness cannot identify the declared architecture.
