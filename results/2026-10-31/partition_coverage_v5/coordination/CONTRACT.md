# C005 — broader coverage with weaker sufficient assumptions

Started 2026-10-31 (Asia/Tehran). Parent C004 commit: 0ab2d9eb.

The master delegates research/implementation/audit and only coordinates,
reviews, freezes, promotes artifacts, and commits. At most three workers.
Worker models: GPT-6.1 Sol medium (structural theorem and certificate),
GPT-6 Luna high (constraint-guided exact search), GPT-6 Luna xhigh
(independent corpus, oracle, proof review, final gate).

## Scientific scope

Complete positive/negative words over a known, disjoint symbol alphabet;
exact labels; independent factors. No claim of learning the generating
partition from a first compatible answer. Core outputs remain unordered
partitions and direct projection witnesses. Distinguish existence,
enumeration, uniqueness, incomplete search, and insufficient certificate.

1. Reduce dense complete-multipartite opposition coverage to sound sparse
   coloring certificates; retain exact fallback and all full-block/negative
   checks. A failed certificate means abstention, not infeasibility.
2. Incorporate sound q-opposition cannot-links into exact bounded-language
   search without losing ANY compatible partition; retain unrestricted
   regular mode and compare q=1,2,3,4 against it on identical inputs.
3. Broaden data beyond constructive recovery: sparse/ambiguous random
   finite-language samples, unequal blocks, missing symbols, repeated events,
   long traces, and more factors. Target exploratory stress ceilings:
   k=16, alphabet=256, length=32768. Actual attained cells and censoring
   must be reported, never substituted by these targets.
4. Investigate reducing the positive sample construction from four to
   three for q=2; separately review any q+1 generalization. Save a negative
   result if false. No unreviewed generalization enters accepted runtime.

Known k remains the core comparison contract. Unknown-k unrestricted
identifiability is impossible without an additional decomposition convention;
do not silently estimate it or confuse regular languages with finite q.
Noise, shared symbols, prefix semantics, and RPNI are not claimed implemented.
If time permits a new relaxation, first freeze its precise model and audit
separately. No novelty claim before primary-source review.

## Ownership and archive

New work lives only in results/2026-10-31/partition_coverage_v5/.
structural/, general/, audit/ belong to the corresponding workers.
coordination/, root CLI/docs, shared files and Git belong to the master.
evidence/capture.py is a byte-identical immutable parent capture helper.
Use it BEFORE every experiment, smoke test, and timing launch, naming all
runtime sources, driver source, input/protocol as sources. Capture stores
unique attempts, content-addressed source bytes, environment, argv,
raw stdout/stderr, exit and timing. Do not overwrite a tested source: use
v2/v3 names and preserve original sources, counterexamples and minimized
versions. Freeze corpus/protocol bytes before running. Never reconstruct
missing historical bytes. Scientific and execution statuses are separate.
No dependencies installed. Do not edit any parent file or legacy folder.

## Independent gates and resource limits

Audit first freezes seed=20261031 shared input-only corpora and hidden
generator sidecars. Exact full partition sets, not just statuses or one
answer, must match a direct independent restricted-growth oracle on small
alphabets (target at least 120 canonical payloads across models/k/q).
Independently validate every returned block projection witness, negative
rejection, and claimed unique sparse certificate. Include unsatisfiable,
ambiguous, disconnected, empty-positive, contradictory, immediate-deadline,
and input validation controls. All discrepancies stop acceptance until
saved/minimized and reviewed; corrected versions get fresh attempts.

Correctness work may proceed in parallel. Performance is serialized only
after master GO fixes source hashes, corpus and schedule. Same task and
full JSON output; fresh processes; three repetitions for selected pairs;
30 seconds hard per job, cooperative 28-second deadline where supported.
Maximum 8 minutes of performance per method this cycle; stop spending on
clearly censored cells. Separate Python tracemalloc from timing; not RSS.
New algorithms may lose on time or abstain: record that honestly.

## Deliverables

Proofs/counterexamples and primary-source notes; versioned code plus a
usable CLI; independent gate and reproducible evidence; Persian report,
README/examples, master decision and complete cycle outcome. C004 remains
unchanged and is not replaced. Final archive byte/link integrity and a
scoped Git commit are required. Avoid repeating already-passed audits.
