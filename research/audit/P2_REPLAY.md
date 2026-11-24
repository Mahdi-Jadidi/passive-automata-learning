# Issue #10 — independent P2 schema and ledger replay

Status: implemented and independently executed against the published schema proposal; cross-worktree producer artifact interchange, receipt authentication, and P3 coverage schema are not yet certified. Do not merge PR #8 automatically.

## Pinned sources and scope

- Issue #10, integration review at 26d1dc39d04188737677f35d82d91ae0f8af99c6 (implementation/partition_feedback_final/research/INTEGRATION_REVIEW_01.md).
- Core schema and component closure at cd627dcdf2a9b73cb79d313f3b864c8284b55082; then SCHEMA_V1.md and evidence_store.py at 539af04bb0b097de5704c28f2b82f23cea5ef783, both read from research/v2-implementation-core. No producer imports by any verifier.
- Existing branch research/v2-proof-audit and draft PR #8. No merge, no writes to core, interface, benchmark, integration or main; baseline and learner unchanged. The branch remains one integration-review commit behind its base; no merge requested.
- All implementation/test paths under tests/reference/ and documentation under research/audit/, per issue #3 ownership. Python 3.13.5, standard library only. No live evaluator calls.

## Implementation and proof obligations

1. independent_replay.py initially implements documented proposal envelope (prepublication); it retains reusable strict sample parsing, ID/scope checks, owner normalization, literal ordered projection checks, JSON duplicate-key rejection, SHA-256 identity and independently tested reference replay. Its flat-record replay() is explicitly provisional; production callers use production_replay.py or ledger_replay.py.
2. production_replay.py uses the exact published versioned nested record and closure formats. Independently reconstructs singleton forest and each frozen epoch, validates each deletion witness against original ordered words, same-negative edge citations, no redundant edges, all emitted same-negative obligations joined, result_owner and final owner. EXHAUSTED requires equality between all claimed (negative,group) keys and independent exact literal join results, not producer flags. A false no-edge epoch cannot prove FIXPOINT. A component deletion at an arbitrary owner is not proof that the owner is mandatory. PARTIAL remains partial; no continuation is silently discarded. Structural witness per original negative verified, including empty projections/unused symbols, duplicate IDs, empty alphabet raw extension. Raw structural optimum only if the verified mandatory root is structurally compatible; no state-bound feasibility implied. Independently matched both core SHA-256 golden values.
3. ledger_replay.py consumes the published ledger envelope: standalone DELETE_EQUAL, COMPONENT_EPOCH, LABEL_CONFLICT, STRUCTURAL_CHECK, REQUEST, SIMULATOR/EXTERNAL OBSERVATION. Checks request/attempt identity, unique attempts and receipt references, complete original ordered negative IDs, strict projection table group coverage, all named/anonymous zeros and exact free equivalence groups, literal failed-negative witnesses. No response or UNKNOWN remains pending. A projection NO table can establish structural NO by literal raw evidence; bounded opaque NO and ACCEPT observations are not proofs. Receipt/response digests are references only. Pure batch replay, no mutation of a producer ledger or external state; an invalid record aborts the replay. Ledger prefixes remain OPEN, not closure exhaustion.
4. Independent literal exhaustive fixture constructor differs from verifier's exact sparse join and imports no producer code. All production-schema modules have no producer imports. Published blobs were compared to locally executed files via git hash-object, all exact matches.

## Mathematical guards

If erasing component A from negative y and some positive x leaves equal ordered words, any separating block must intersect A. If A is a component of an independently established mandatory partition, a compatible completion coarsens that partition, hence must contain A in its entirety. Two such deletion witnesses for the SAME negative force the two components into its one common separating block. By induction starting at singleton partition, every checked successful union is necessary. Distinct positives are allowed. Frozen owners must be exactly prior verified result_owner; mere true component deletion equality cannot license an arbitrary starting quotient. Rank of the resulting forest is a lower bound, and structural compatibility of that exact root gives a matching upper bound (unrestricted model). Partial discovery can suffice for this special proof; it does not establish fixpoint or operational ACCEPT.

Completeness of independent deletion enumeration: for x != y, a deletion equality cannot occur when the deleted group is absent from both. If touched in both, exact erased-word match at same group; if only negative touched, negative erased word equals positive full word; if only positive touched, positive erased word equals negative full word. Preflight full cross-label duplicate check handles absent-both case. This independently enumerates exact keys using literal tuples, no hash-fingerprint trust. Thus the producer's EXHAUSTED assertion is strengthened to checked completeness. E.g. X={ab},Y={ba}, a|b with empty facts/edges falsely claims FIXPOINT even though both singletons have deletion witnesses. Must reject as incomplete evidence, not infer no merges.

Structural witnesses check each negative has at least one group not sharing its projection with ANY positive; positive absent projection iff some positive misses the group, except p=0, where every actual group separates. Failed-negative checks every block is dead for the same negative. Empty partition cannot separate a negative. Free table columns must be nonmatching, exact equivalence groups and disjoint from fixed zeros; zero in a feasible row is not fixedness. Operational receipt trust is separate.

## Validated milestones

| Commit | File / outcome |
|---|---|
| 28bb28dfff1f1c50db39004c6aeb1a65236cf562 | Independent proposal kernel |
| 52310d2dd4090509143ac8c9890df6e673c20e4a | Six proposal tests; actual exhaustive and mutation results |
| 55ffb65d883b99ae4514c0e33c6eb12d0df85e0c | Exact core component epoch replay |
| 8b4057b767a2faa1bcdab8c39b60ca53ca87fb1c | Five production-schema tests, core golden vectors |
| 0d9611a40972161e986d204b3ccda960d7571e38 | Explicit OPEN epoch prefix, no exhaustion inference |
| 56f1201eb7fcf71429395a76d58140839eaed50f | Typed ledger replay |
| fc7284973776c7bdd173a6dde2fbb46b1d753035 | Three ledger tests and 30 corrupt-record cases |
| 79cf2610e02990541ce01a70c5760a300d1d8b0b | Synthetic scale proof replay |

Reproduce from repository root (Python 3.13.5 used):
```sh
cd tests/reference
python -m unittest -v test_independent_replay test_production_replay test_ledger_replay
python -O -m unittest -q test_independent_replay test_production_replay test_ledger_replay
/usr/bin/time -f 'process_seconds=%e max_rss_kib=%M' python scale_replay.py
```

Actual final combined run:
```text
Ran 14 tests in 0.406s
OK
exhaustive_corpora=2187 structural_checks=4374 forced_edges=925
golden_vectors=["b3e6b42446211a76362e92236de37cf631bee2bcaf04c4fff3463d061904fc1c", "d4d34208a22f662dea22de0c3fa9d983e74c08a9c77984d5be7dafc774806128", "55860bacb2ab0d7ee214c489b206145a14d1276e4a8fbbb17d547c3f1fdf89c9"]
mutation_rejections=44
epoch_structural_mutations=39
production_corpora=2187 epochs=3112 deletion_facts=7087 structural_checks=4374
core_golden_vectors=2 request_mutations=13
ledger_mutations=30
```

Optimized Python (-O): 14 tests, 0.392s, OK; identical counts. The 44+39+13+30=126 enumerated corruption cases are across distinct audit suites, not necessarily distinct underlying error classes; additional negative tests are not included in this count. The two 2,187-corpus sweeps use the SAME finite domain (all disjoint labelings of binary words of length <=2), not 4,374 distinct corpora. Production replay also covers a three-symbol multi-epoch case, partial, open prefixes, label conflict, no positives, no negatives, unused symbols, bounded scope and Unicode/duplicate/epsilon goldens. All source blobs matched local Git object IDs.

Synthetic short-word proof fixture, independently constructed: 100,000 declared symbols, 20,000 traces, 30,000 deletion facts, 10,000 mandatory contractions, structural optimum cost 10,000 / 90,000 blocks. Replay 0.489 s; full process 1.24 s; max RSS 154244 KiB; operational INCOMPLETE. Earlier same fixture exploratory run 0.4428 s replay, 1.25 s process, 154232 KiB RSS. This is not a producer run, real evaluator performance, controlled comparison or original benchmark archive. Scale fixture uses short words and large unused alphabet; literal tuple deletion index can cost quadratic time/space in highly diverse long words, and fully expanded feedback remains potentially huge.

## Integration blockers / decisions

- Container git ls-remote could not resolve github.com. Retrieved source and schema via GitHub connector; Python tests executed local exact audit source and independently constructed serialized fixtures, not a clean checkout running real producer exports. Cross-worktree producer roundtrip and interface cross-language vectors still needed before gate closure. Core two exact sample/request golden digests matched.
- Exact schema revision is 539af04 (proposal, not formally frozen); retain preliminary flat wire reference only for regression; production entry points replay_serialized and replay_ledger_json. No imports of producer proof checker; raw request expected scope provided by caller. A ledger may contain multiple request scopes by schema design; per-request scope validated, not equated with default mathematical scope.
- No authenticated receipt, artifact binding, DFA simulation, actual capacity policy, or operational proof certificate. UNKNOWN and missing responses remain pending attempt records; unauthenticated conclusive observations are not an operational candidate closure. P3 E/D frontier schema and persistent restart/checkpoint replay do not exist yet; fail closed on unknown kinds rather than claim full search coverage.
- Strict completeness check intentionally stronger than producer intake's stated EXHAUSTED policy. A producer ledger accepting necessary edges is not equivalent to independent fixpoint verification. Need joint review of proof budget / incomplete verification semantics and long-trace memory bound. Current code is reference proof kernel, not a deployed verifier; no wall-time budget or resource caps. JSON parser rejects duplicate keys and explicit nonfinite constants; no resource-hardened streaming parser.
- No external learner, baseline or other stream changes. Draft PR #8 remains open/unmerged; issue #10 remains open for coordinated cross-stream review.
