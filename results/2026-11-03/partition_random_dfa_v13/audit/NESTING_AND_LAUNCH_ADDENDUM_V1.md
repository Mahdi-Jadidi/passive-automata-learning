# C013 nesting check and launch boundary

Received generator design after the initial budget proposal: separate per-label/per-candidate RNG streams do not depend on requested sample count. Independently verify, for each fixed K/world/length, that both two-sample label sets are subsets of their eight-sample counterparts. Also verify identical world hashes and allowed-K conditions. Do not infer nesting from seeds alone.

When nesting holds and both exact runs finish, require Z8 <= Z2 and inspect every forced relation from the smaller sample: it must still be forced with the same relation in the larger complete answer. Check exact per-k counts are also nonincreasing. A stronger sample can introduce new forced relations. Timeout/censored results cannot establish these comparisons. This is a metamorphic check, not a complete-family oracle.

Count-information clarification remains pending. No provider launch until the master resolves it or explicitly states the no-K assumption after allowing the user to reply. Generator preparation and static inspection can proceed independently; no data/source/provider execution occurred in this audit at the time of this addendum.

## Timing analysis refinement before any execution

Use actual total solver-input characters T and actual word-length distributions, not nominal maxL, as length axes; repair reserves can vary with K. Each length curve fixes K, saved world, sample count and sampling profile. Display every censored cell. Do not fit completed fast winners as a global complexity order. An optional descriptive log-log slope requires at least three distinct completed actual lengths and explicit startup/censoring caveats; it cannot establish theoretical order.

Record sample construction/repair time and independent DFA-label evaluation time separately from inference. Classification distinguishes compatible saved truth, unique ownership recovery, completed ambiguity and nonfinal/error outcomes. In the no-K model, ambiguity for physical K>1 is expected under coarsening closure, not a classification error. Every reported forced relation must agree with the saved symbol owner table.
