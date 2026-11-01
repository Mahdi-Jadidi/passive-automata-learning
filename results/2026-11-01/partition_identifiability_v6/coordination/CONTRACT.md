# C006 — unknown k, unrestricted regular factors, and non-decomposability

Parent C005 commit eb521fdd. Started 2026-11-01, Asia/Tehran.
User explicitly retains assumptions 1,3,4,5: known disjoint alphabet, independent
factors/interleavings preserving local order, exact whole-word labels, and
complete words. Remove known k and the finite local-language cardinality cap.

Nontrivial decomposition means at least TWO nonempty alphabet blocks. One
block is a trivial compatible explanation for any consistently labelled finite
sample, so never report impossibility without declaring this convention.
All regular local languages are permitted, including infinite ones. Finite
positive-projection witnesses are existential models, not a restriction on
the true generator. Do not claim recovery of hidden k from finite labels.

Three delegated workers maximum, master coordinates/finalizes only:
theory (Sol medium), implementation (Luna high), independent audit (Luna xhigh).
Ownership: theory/, implementation/, audit/ respectively. Master owns shared
coordination/, root CLI/docs, Git and parent freeze. No edits to C005 or older
artifacts. No nested workers. No dependency installs.

Research targets:
1. Prove coarsening closure and whether existence of any nontrivial compatible
   partition reduces exactly to existence of a compatible bipartition. State
   possible k sets, ambiguity and true-k identifiability boundaries.
2. Necessary-and-sufficient finite-sample regular-factor feasibility by direct
   projections; exact algorithm for non-decomposability with independently
   checkable obstruction certificate. Investigate connected sound must-links
   as a cheap sufficient obstruction; its failure is not decomposability.
3. Return a compatible partition/witness, a validated impossibility certificate,
   or incomplete. Unknown-k frontier/maximal refinements optional secondary;
   never relabel a chosen finest compatible partition as hidden true partition.
4. Broaden class coverage beyond finite q, including infinite regular planted
   generators, unequal blocks, sparse/insufficient observations and long words.

Archive every execution BEFORE launching through immutable evidence/capture.py,
including driver, all runtime dependencies, input and protocol source snapshots.
Use unique attempts. Preserve failed versions/counterexamples and their minimized
versions; corrected code/protocol gets new filename, no overwriting tested bytes.
Scientific status separate from execution status. No fabricated missing logs.

Independent gates: freeze seed 20261101 corpus before execution, at least 120
distinct small consistent payloads over 2..7 symbols, all-k independent oracle
on small cases; compare exact FULL partition sets and existence/frontiers.
Audit every positive/negative witness and replay every obstruction independently.
Require non-decomposable samples without contradictory labels and ambiguity
controls. Include no positives, no negatives, unused symbols, epsilon, invalid
input and immediate deadline. Preserve all discrepancies before correcting.
Useful general obstructions should be tested on scalable synthetic examples.
Do not repeat prior approved C005 tests except relevant regression bridges.

Timing only after correctness and master frozen GO; bounded representative
schedule, fresh serial processes, three repetitions selected comparisons,
full JSON serialization, cooperative 28s/hard30s, <=5min per method. Separate
memory if useful; no generic speedup claim. Target prior scale ceilings only
where meaningful; prioritize weakening assumptions, not another size record.

Deliver proof/literature notes, versioned usable algorithm/certificate verifier,
independent gate/evidence, Persian report/README/examples, master decision and
Git closure. Ordinary data-dependent non-decomposability must be distinguished
from absence of a unique decomposition and timeout. No RPNI/noise/shared-symbol
work in this cycle. Negative findings are valid scientific deliverables.
