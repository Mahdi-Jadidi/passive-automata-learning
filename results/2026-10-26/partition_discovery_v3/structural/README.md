# C003 structural recovery: fixed singleton-word factors

`fixed_word_solver.py` is standard-library-only and exports
`solve(data, *, deadline=None, max_solutions=1)`. It imports no C002/shared provider
implementation, receives no target truth and makes no oracle queries. The parent
owns CLI integration. C002 remains immutable.

Input: an object with alphabet (>=2 distinct one-character strings), positive and
negative lists of words over it. Symbols are sorted and duplicate words accepted
and normalized. Contradictory labels, unknown symbols, invalid data types and
invalid limits raise ValueError. Unicode single-codepoint symbols work; there is
no 10-symbol cap. No target support is silently dropped.

The route first checks all positive occurrence counts, then constructs the graph
of positive pair-projection variation, retaining a positive-index witness per
edge. All declared symbols remain vertices. BFS detects odd cycles or recovers
the canonical coloring, first sorted symbol on side zero. If the graph is
connected and bipartite, every positive and negative is checked against the two
fixed projected words. An answer has independently checkable C002-style projection
languages/negative witnesses, plus explicit local_words and graph certificate.

## Semantic contract

| Status | Meaning | decision_complete | search_exhausted | uniqueness |
|---|---|---|---|---|
| found | One valid partition, structurally proved unique IN FIXED-WORD CLASS | true | true | unique |
| assumption_violation | Counts, odd cycle, or sole positive candidate's label conflict rules out this class | true | true | unknown |
| insufficient_coverage | The sufficient structural certificate is unavailable; no general search performed | false | false | unknown |
| incomplete | Cooperative deadline/interrupt; retain any fully validated solution | true only if solution retained | false | unknown |

Every result has method=`fixed-word`, model_class=`fixed_word_product`, solutions,
uniqueness_scope, assumptions, metrics, graph and certificate. No status here
claims global regular-product infeasibility. No uniqueness scope may be broadened
to general_regular_product. A source certificate can prove exhaustion without
enumerating all partitions; that is exactly the point of this route.

Absent symbols, zero positives, one unique positive, or disconnected graph give
insufficient_coverage even if a different method could establish a decision.
Singleton BLOCKS and repeated SYMBOLS work. A local word may be empty, but full
symbol support is needed by the constructive two-positive coverage theorem.

`max_solutions` accepts positive integers or None, rejects bool/zero/negative.
This route is a certificate-only provider and never returns more than one answer:
a connected successful certificate already proves there are no further answers.
On disconnected data it does not enumerate, even for None; its unresolved status
is explicit. Deadline is absolute perf_counter or None. The provider checks it
throughout loops; Python built-in sort/set/join are not forcibly preempted.

## Theory and scope of prior work

`PROOFS.md` gives edge soundness, positive compatibility from singleton/pair
reconstruction, connectedness-based uniqueness, odd-cycle/count witnesses,
negative checking, and uv/vu constructive coverage with every block symbol
present. `SOURCES.md` distinguishes known projection reconstruction and existing
whole-language/DFA shuffle factorization results from partial-sample recovery.
No novelty claim is made. Disconnected-but-unique and class-unique-but-not-general
examples are retained, not hidden as algorithm successes.

`IDEA_C003_S001.json` records initial hypothesis and refuted extensions. Execution
and audit records are separate, linked immutable artifacts; do not overwrite the
initial scientific/execution statuses in that record.

## Reproducible initial smoke, not a benchmark

Use bundled Python with `-B -X utf8`. Every invocation goes through C003
`audit/capture.py`, with project sources and input files supplied as --source.
First run `build_smoke_inputs.py` once through capture to create immutable
`smoke_inputs_v1.json` and `example_input.json`; repeated fixture construction
refuses existing files. Then capture `smoke.py` with the provider, fixture, example,
generator, proof/source/idea records and contract snapshotted. Exact commands,
environment, bytes and source/input hashes are in the shared capture attempts.
The linked execution record will give actual attempt IDs and outcomes.

The smoke uses only each case.input as solver data; target_blocks and expected
outcomes are used only by its checker. It includes 32 seeded small constructive
cases, boundaries/invalidity/deadline cases and two 128-symbol constructions
(balanced and singleton side), with repeated symbols. A small exhaustive local
oracle enumerates partitions only on <=6-symbol fixtures; the 128-symbol cases
check direct projection witnesses and the planted partition. This is branch
verification, NOT the independently frozen recovery audit.

Every raw returned result or exception is written and fsynced into a unique
`smoke_runs/` directory BEFORE any assertion, and printed/flushed into captured
stdout. Failed runs, if any, remain separate. No performance superiority follows
from this smoke; no heavy benchmark is run here.

Initial read-only setup found no workspace-root AGENTS.md (PowerShell reported
the absent path); this is not an implementation/test failure. The literature DOI
access failure is separately recorded in SOURCES.md. Original shell/web outputs
are in the task transcript; no separate unavailable raw log is invented.
