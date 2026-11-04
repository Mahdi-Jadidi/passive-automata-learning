# C019 supplementary graph-count condition and compatibility counterexample

Direct derivation; no executions or changes to the v1 proof/readiness.

## Count condition restricted to this graph certificate

A graph with m vertices and K connected components needs at least m−K
independent forest merges. Each opposite-label word pair can witness at most
one exact adjacent unequal swap: its two differing positions uniquely specify
the swapped letter pair. Therefore

    |P| * |N| >= m−K

is necessary for THIS adjacent-swap graph route to reach r=K. Duplicate
word lists only enlarge this raw upper bound and do not add new independent
merges. Several word pairs may induce the same edge, or edges completing
cycles, so the inequality is not sufficient. It is not a lower bound for
all possible uniqueness certificates or the exact fallback; no general
sample-complexity theorem is inferred from it.

## r=K is insufficient without exact atom feasibility

Let Σ=abcd, K=2, and reverse the earlier positive/negative construction:

    P={bacd,abdc},    N={abcd}.

The first positive versus negative forces ab by an adjacent swap; the
second forces cd. Thus the graph has exactly two atoms ab|cd. But its
projection languages are

    block     positive projections     negative projection
    ab        {ba,ab}                  ab
    cd        {cd,dc}                  cd.

Both negative projections are positively forced, so this sole possible
two-block partition accepts the negative. There is NO compatible K2 model.
Thus a graph with r=K is not enough by itself; the sample must also fit its
component partition. Contradiction-free labels alone do not establish that.

For each individual positive there is a block distinguishing it from the
negative (ab for bacd, cd for abdc). Nevertheless no single block rejects
the negative against ALL positives. The correct criterion is

    for each negative n, exists block B, for every positive p:
        projection_B(n) != projection_B(p).

The false quantifier exchange “for every positive, exists a block” would
accept this counterexample. The graph labels/edges are themselves sound;
it is the count-restricted version space that is empty. Without count2,
the one-block language P remains a regular compatible witness.

This note is a mathematical supplement, not a new solver or measured case.
