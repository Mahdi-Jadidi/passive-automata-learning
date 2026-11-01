# C006 independent audit protocol v1 (frozen before solver comparisons)

Date: 2026-11-01 (Asia/Tehran). Seed base: `20261101`. This is an audit
protocol only. It does not authorize official timing, modify C005, or assume a
provider output schema. No solver comparison may start until the theory and
implementation leads publish readiness files and the master issues GO.

## Scope and input contract

Each solver input contains only a known ordered alphabet and exact positive and
negative complete words. It contains no hidden `k`, `q`, partition, DFA, grammar,
or generation metadata. Alphabet symbols are distinct one-character strings;
blocks are nonempty, pairwise disjoint, and partition the alphabet. Factors are
independent and preserve local symbol order; words are whole-word labeled.
`k=1` is always a compatible trivial explanation for a consistent finite sample
under unrestricted regular factors, so a non-decomposability claim means no
compatible partition with `2 <= k <= |Sigma|` and must use an explicit
certificate. It never means the sample has no regular explanation at all.

Finite positive-projection languages are only witnesses for sample feasibility;
they do not impose a cardinality cap on true factors. A finite sample cannot by
itself identify the hidden true `k` or distinguish its true regular language
from every other regular language consistent with the observations.

## Frozen corpus design

`generate_corpus_v1.py` uses seed `20261101`, standard-library Python, and emits
120 distinct consistent visible inputs, 20 each for alphabet sizes 2 through 7.
There are product samples with planted regular factors
`(aa | bb | ... | zz)*` for each hidden block, and one-factor controls whose
language is a finite set of observed positives union an infinite unary tail.
Sidecars state the grammar and hidden blocks; these are audit-only and never
passed to a solver. Control cases separately cover:

- a non-decomposable consistent sample with disconnected sound must-link graph;
- all-partitions ambiguity and an ambiguous range of feasible `k`;
- no positives, no negatives (which must make every partition compatible),
  epsilon, unused symbols, unequal blocks, and an alphabet of size one (where
  nontrivial decomposition is structurally impossible even though the sample
  may be valid);
- malformed/conflicting labels and an immediate expired deadline.

The corpus manifest records exact file hashes and distinct payload count. A
separate q=None bridge may select only a directly relevant saved C005 fixture;
it is not a rerun of C005's broad gates.

## Independent all-k oracle

The auditor enumerates all set partitions by restricted-growth strings (RGS),
not by the candidate provider. For each partition `P=(B_1,...,B_k)`, form
`Pos_i = { projection(w,B_i) : w in S+ }`. The partition is compatible exactly
when every `n in S-` has at least one `i` with `projection(n,B_i) not in Pos_i`.
For every compatible partition, store the complete partition and a rejecting
block/projection witness for each negative. Compare full sets of canonical
partitions, split by `k`, and the full compatible bipartition set.

The oracle also checks coarsening closure by coarsening every feasible RGS
partition; checks that the nontrivial feasible k values are exactly the interval
`2..k_max` (with k=1 recorded separately as the trivial explanation for every
consistent input); and independently tests that existence of any nontrivial
partition equals existence of a compatible bipartition. Empty negative sets
must return all partitions, including with no positives. These finite checks
support, not replace, proofs.

The direct-feasibility rationale is independent: any factors containing the
positive projections must accept every observed positive. If all projections
of a negative occur in those positive-projection sets, every factor accepts it,
so the partition is impossible. Otherwise choosing each local factor to be
exactly its finite positive-projection set is a regular witness and rejects the
negative. This is an existential construction, not a true-language estimate.

## Certificate audits and negative controls

For every implementation certificate, the auditor will snapshot the exact
certificate verifier and independently replay each item. Connected must-link
obstructions are checked only as sufficient certificates. Cut-cover
non-decomposition certificates must cover every bipartition of the quotient
components after sound must-links are replayed, and use only sound cut clauses;
all cuts are checked for duplicate, missing, or forged clauses. Tests will
include a certificate with a removed cut, a forged cut, and a
positive/negative-collision control. Every alleged example where a connected
must-link graph is not necessary for non-decomposability is checked against the
all-k oracle. A timeout is `unknown` with an explicit reason and cannot be
reported as non-decomposable.

Capture and preserve provider output before any comparison or assertion.
Mismatch inputs and original outputs are immutable; minimized counterexamples
are additional artifacts. Scientific result (valid, disproved, unknown) is
separate from execution result (success, timeout, program error, environment
error, interrupted). Every launched experiment is first recorded by
`evidence/capture.py` with source snapshots for the driver, all runtime code,
visible input, protocol, and sidecars used only by the auditor. Failed harness
attempts remain in the archive; a corrected attempt has a new source filename.

## Staging

1. Capture corpus generation; freeze visible inputs, audit-only sidecars, and
   manifest.
2. Capture independent all-k oracle and its output before importing any
   candidate implementation.
3. Wait for `theory/READINESS.json` and `implementation/READINESS.json`. Audit
   their proofs/certificate schema and then run a bounded correctness-only
   batch on the identical frozen inputs. No timing until explicit master GO.
4. If authorized, timing uses selected fixed cases, three fresh serial
   repetitions, full result serialization, cooperative 28-second cutoff,
   hard 30-second cap and at most five minutes per method.
