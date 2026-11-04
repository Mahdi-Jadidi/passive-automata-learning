# C019 — identical counts and lengths, different identifiability

Mathematical counterexample only; no execution or new source. Let Σ=abcd,
trusted K=2 and the same single positive P={abcd} in both inputs.

| Input | Negative words | Compatible K2 partitions |
|---|---|---|
| U | bacd, abdc | ab|cd only |
| A | bacd, badc | ab|cd, abc|d, abd|c |

Both inputs have exactly one positive, two negatives, all words length4,
every symbol appearing exactly once in every word. Thus even these matched
sample/length/Parikh summaries do not predict uniqueness.

Proof for U: the two exact adjacent swaps force ab and cd respectively.
The partition ab|cd fits, so with K2 it is the unique possibility.

Proof for A: positive abcd versus negative bacd forces a,b together. Every
partition keeping ab intact already rejects BOTH negatives on their
a,b-containing block: the positive projection has a before b and each
negative projection has b before a. Projecting further onto ab proves those
full-block projections cannot equal the positive projection. Hence the
compatible partitions are exactly coarsenings of ab|c|d. Their three K2
members are precisely the ones in the table.

The second negative badc is therefore valid but redundant for ownership
after ab has been forced; it cannot replace the independent cd information
in abdc. Both datasets satisfy |P||N|=m−K=2, showing the graph-certificate
numeric necessary condition is not sufficient. One positive plus m−K
negative COUNT is not the sufficient theorem: the specific independent
within-block swap structure is the information-bearing premise.

The general one-positive/m−K informative-swap construction and its proof
remain in PREFLIGHT_PROOFS_FA_v1.md T2; the count condition and a graph-fitting
counterexample are in GRAPH_CERTIFICATE_LIMITS_v1.md. Earlier files and their
hashes are unchanged. No timing or executable acceptance is asserted here.
