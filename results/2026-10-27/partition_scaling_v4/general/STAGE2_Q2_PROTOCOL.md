# Stage-2 q=2 protocol (prepared, not run)

**Status:** awaiting the master’s stage-1 correctness gate. No q=2 ablation has
been executed by this worker.

## Question

For the same labeled observations and fixed known k, compare unrestricted
regular-factor feasibility with the finite-language provider that allows at
most two distinct observed positive projections per block. Change only this
language-size bound; keep alphabet, k, positives, negatives, trace contents,
and search/output limits fixed.

## Correctness gate before measurement

1. Freeze the selected provider source and all inputs; capture every run through
   `audit/capture.py` with source and input paths.
2. On the affordable small-alphabet tier, compare the complete unordered
   partition sets from the provider with an independent exhaustive oracle for
   q=2. Check every negative’s unseen-projection witness and each returned
   projection language.
3. Include controls where all factors have one observed positive projection,
   where a factor has exactly two, and where a factor has at least three. The
   last control must be rejected by the q=2 model even if unrestricted regular
   factors fit. Preserve empty-word and repeated-projection cases separately.
4. Only after exact-set and witness checks pass, measure q=2 against unrestricted
   mode on identical inputs. Report results as conditional on finite local
   languages with at most two distinct observed positive projections.

Prepared, unexecuted controls are in `fixtures/q2_prepared_inputs.json`. They
separate a one-projection baseline, a q=2-only fit, a three-projection cap
violation, the empty-positive boundary, and repeated projections.

## Semantics and boundaries

The q=2 provider chooses each local language to be exactly its finite set of
observed positive projections. It accepts all positives when each set has at
most two members. A negative is rejected iff at least one block’s projection
is absent from that block’s observed set. The empty-positive case gives empty
observed languages; this is valid for the bounded finite-language model but
does not mean “exactly one local word.” Keep empty-positive cases out of claims
equating q=1 with singleton-exactly-one recovery unless a separate target
semantics supplies the missing local word.

Do not combine q=2 with removal of coverage assumptions, unknown k, or any
noise/label change. Do not infer arbitrary DFA identification from q=2
compatibility. A compatible first partition is existence only; uniqueness
requires exhaustive search or a valid certificate, and timeout remains
incomplete. Do not run q=3 until q=2 is separately accepted and authorized by
the stage plan.

## Provenance and reporting

Assign each input and measured attempt a fresh ID. Keep the raw stdout/stderr,
source snapshots, hashes, full correctness records, and any failed/minimized
counterexample. Report q, k, alphabet size, sample counts, trace lengths,
graph components, visited nodes/leaves, cap-pruned nodes, runtime, and output
materialization separately. State any censoring; a timeout cannot establish
infeasibility or uniqueness.
