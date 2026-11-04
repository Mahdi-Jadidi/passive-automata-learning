# C020 implementation staging and candidate selection

No source, fixture, profile or comparison has been executed in this branch.
The auditor owns the generator and approved matrix; implementation does not
duplicate the fixtures or inspect hidden models through a solver. Initial
generator discussion is a design suggestion only, not an implemented attempt.

The approved A/B/C/D matrix is in coordination/MATRIX_APPROVAL_V1.json. It
contains six timing cells including explicit trusted-K and no-K variants,
not a Cartesian sweep. Public partition.py and all older sources remain
untouched. Paper/LANCER work remains paused. Timing limits remain600seconds
per provider,20soft/25hard per case, three fresh repetitions only as budgeted.

## Baseline profile first

profile_baseline_v1.py binds C018 c288448f... exactly, loads only the supplied
observational input, and records cProfile function costs, raw gate result,
pstats and hashes. It has a default5second soft gate budget, maximum20, and
needs the auditor's external <=25second hard supervision. It writes a fresh
directory and does not read a world/hidden generator file. Profiling overhead
means these wall times are hotspot evidence, not candidate speed measurements.
Input reading/import/profile-output cost still appears in its receipt and
outer capture. A normal unresolved gate return is retained rather than retried.

After fixture/schema freeze and master GO, request one compact matched-Parikh
graph case (A or a frozen small subset) and one long case only if necessary
to distinguish counting, swap scanning and block projection costs. Do not run
a comparison grid or add generator variants without the auditor's approval.

## At most two optimization candidates

First proposed direction, pending measured profile: retain exact validated
per-word Parikh summaries from the existing count precheck, then compare graph
pairs only within equal-length/equal-Parikh groups. Adjacent swaps require
both properties. Original indices and exact swapped-word validation remain.
This is a filtering optimization, not a new graph rule. If order/index traversal
is preserved, even forest witness choice can remain the same; any changed
forest still requires independent replay and semantic equality checks.

Second slot is conditional on the remaining hotspot after the first measured
candidate. If projection dominates, consider exact str.translate deletion of
all alphabet symbols outside a block, with arbitrary one-codepoint Unicode
handled literally. If exact search instead dominates, the theory's sound RGS
envelope alternative may be considered. These are alternatives for ONE second
slot, not permission to implement both. Every adopted candidate needs its own
proof, immutable source/readiness, static review and correctness gate.

The theory's rolling fingerprint-neighbor index is preserved as a separate
proposal in theory/EXACT_SCALING_PROPOSAL_v1.md. It has not been implemented or
benchmarked here. A Python per-character index may cost more than count reuse
and native operations; no direction is adopted merely because it is proved
sound. Coordinate any replacement choice with master/theory and preserve all
rejected plans/evidence.

Candidate1 code is intentionally not created before the baseline hotspot is
observed. The exact unchanged C018 API/status assumptions and compact output
must be compared. Generated K/state counts are hidden evaluation metadata;
known-K variants must explicitly supply a separately trusted count. Recovered
conditional partition is distinct from mere compatibility or no-K ambiguity.

Stop at the preregistered measured plateau/regression or after the two reviewed
slots. Preserve censored/unstarted cells and unsuccessful candidates. No claim
of global optimality, worst-case improvement or arbitrary physical recovery
can follow from this compact benchmark.
