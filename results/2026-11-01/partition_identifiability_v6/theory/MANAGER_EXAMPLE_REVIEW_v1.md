# C006 manager candidate: checked without modifying the candidate

Original A=abcd, P={acdb,cabd,bcda,dabc}, N={abcd} is preserved bytewise as
examples_manager_v1.json. Captured all-k check:
evidence/attempts/20261101T153400.800636Z_5918e0fe41 (relative to ROOT).
Execution success, exit 0, empty stderr. All returned partition sets and collision
witnesses were printed/flushed before assertions. This is theory-branch checking,
not the independent auditor's gate or a performance job.

All 15 unordered partitions were enumerated. Only the trivial partition is
feasible. All seven canonical bipartitions have the saved collision witnesses.
The tested swap/rescue graph has no edges. Singleton cuts fail because deleting
a,b,c,d from the negative gives bcd,acd,abd,abc, available respectively in positives
bcda,acdb,cabd,dabc. On each two-two cut each required pair projection appears
somewhere in P (the two sides may use different positives); the saved cover
replays their exact choices. No positive is a single adjacent swap of abcd, and
no positive has the length-five requirement for a rescue of that negative.

Therefore this confirms incompleteness of the SPECIFIED graph obstruction,
not of every possible sound contextual inference rule. This useful equal-length,
same-count example avoids explaining the gap merely by short-word count effects.

The smaller A=ab, P={a,b}, N={epsilon} is also captured in that attempt and in
20261101T153244.750418Z_c884922f4c. It has zero graph edges and no nontrivial
feasible partition. Deleting either positive admits the sole bipartition. It was
manually constructed independently, NOT obtained by an automated shrinker from
the manager case. No sequence of automatic minimization operations is claimed.
Alphabet-two minimality and deletion-minimality within its stated setting are
the exact proved claims; unrestricted global minimality is not claimed.
