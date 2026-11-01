# C007 oracle audit addendum v2

Date: 2026-11-02 (Asia/Tehran). This addendum extends the frozen corpus
protocol without changing any corpus row, sidecar, or v1 protocol byte.

## Direct refinement-poset target check

In addition to computing the common-equivalence meet, the independent checker
tests the target definition directly over the complete all-k compatible set:
a partition is a finest candidate exactly when it is compatible and refines
every compatible partition. It reports a unique finest only if exactly one
candidate satisfies that predicate. It then checks agreement with meet
feasibility and with uniqueness of the maximal-refinement frontier. This
provides an independent guard against a shared meet/intersection bug.

The relation `F <= R` means every block of `F` is contained in some block of
`R`. “Unique finest” is a sample claim. Equality with hidden planted DFA blocks
is summarized separately as an exploratory agreement diagnostic and is not
used to label solver correctness.

## Decision versus exact-result completeness

An infeasible partial meet can soundly establish that multiple incomparable
maximal refinements exist, because every compatible partition must refine
that partial meet. It does not establish the exact final meet, enumerate all
maximal partitions, or certify a no-separator search. These are independently
audited output fields and must not be conflated.
