# P3 search/interface boundary contract

Date: 2026-11-25. Scope: selector-side preparation and regression tests only.
Authority: NEXT_SESSION_HANDOFF_05.md at 80445eb0c3977389342eeb92aa7e530f817cbff8, INTEGRATION_REVIEW_05.md at 53da42edb57cdfd970a475d2d71f750ebd0fcbbc, and P3 authorization in issue #11.

## Gate and non-goals

The post-hardening P2.1 narrow structural journal/2 gate is VERIFIED at the exact hardened proof pin cf5a007571853b6cdf6259fa2a9a95f5c1e351f8. The gate's operational status remains INCOMPLETE. P3 EDR-BB is authorized only for unrestricted structural exact search (B=0), as recorded in issue #11. This document and tests do not certify P3 search coverage, authorize any unreviewed pruning, or establish bounded/operational optimization. No learner or baseline changes, endpoint calls, real transport, new journal version, competing state or dual-write.

Use the existing gateway.open_gateway(raw, authenticate=...) which returns the actual core RegisteredLedger; use register, ingest, original_id, attempt_status, records and export. The P3 search process owns only its search frontier, not a second ledger of observations. The authoritative journal remains selector-v2-journal/2 with inner selector-v2/1. Historical SharedGateway, adapter.Ledger and strict_ledger.RegisteredLedger are not production paths. No new production API is proposed by this milestone.

## Complete original-alphabet candidates

Let A=(a_0,...,a_(n-1)) be the original ordered, distinct alphabet, including unused symbols. The sole boundary representation is the length-n JSON integer array owner, where owner[i] = min{j : a_j lies in the same block as a_i}. For each i, 0 <= owner[i] <= i and owner[owner[i]] = owner[i], with genuine integers (not bool or float). Every symbol occurs exactly once in the induced block partition; no projected words or quotient IDs replace original symbols. Cost is n - number of distinct roots.

These equations are necessary and sufficient: equal owners define equivalence classes; the fixed-point equation puts the root in its own class; the inequality makes it the least member. Consequently each complete partition has exactly one owner array. Restricted growth strings and DSU representatives may be internal search representations only; expand to original IDs and canonicalize before registration. Example: blocks {0,1},{2} are [0,0,2], not RGS [0,0,1]. Region R(E,D), partial assignments, omitted unused symbols and incomplete quotient owners are not requests. A structurally valid empty alphabet partition remains local: current adapter/core request validators explicitly reject empty-alphabet submission.

## Three distinct identities

* Structural candidate identity is the pair (sample_digest, tuple(owner)); compare full canonical owner, not a hash alone. This is a conceptual key, not a new wire field or journal schema.
* Scoped evaluation identity additionally includes the existing complete scope object and the registered provenance (origin, capacities, per-label ID maps). Never transfer bounded decisions between capacity vectors or regimes. Same structural candidate does not imply same evaluation target.
* Request/attempt identity uses the existing request_id and attempt_id plus the existing canonical request digest identity(request). The request digest includes both IDs. A retry retains request_id and all registration provenance, changes only attempt_id, and obtains a different request digest. Attempt IDs are globally unique within one authoritative journal. A different request ID does not turn the same partition into a different structural partition.

Scope is exactly the existing selector-v2/1 object: sample_digest, family ALL_PARTITIONS, regime UNRESTRICTED with null capacity_digest or BOUNDED with the digest of ['capacity-v2', [[root, capacity], ...]] in ascending original-root order. The version field is also mandatory. P3 unrestricted submissions have capacities=None. Bounded tests check isolation only and are not permission to issue bounded evaluations. Never use a region identifier as family or change scope in a response. Response registration must match the whole request, not merely its digest or candidate cost.

The sample digest binds ['sample-v2', alphabet, encoded_positive, encoded_negative] with the existing canonical serialization. Both label lists retain order, multiplicity and epsilon. Distinct occurrences of equal words retain separate original IDs. IDs are zero-based original positions independently per label; request.negative_ids is the full ordered range. Wire maps, when needed, are explicitly registered ordered bijections [wire_string, original_index] for each label, not inferred from word content, hash, sorting or deduplication. Maps and request provenance remain immutable on retry. When no map is registered, do not guess translation. Projection and DFA witnesses use original symbol IDs and original trace positions.

## Verdict boundary: observations are not search certificates

| Outcome | Existing acceptance conditions | P3 interpretation |
|---|---|---|
| ACCEPT | complete bound response with valid total deterministic DFA for each block, all projected positives accepted and each negative rejected by at least one block; capacity respected if specified; optional joint row matches recomputed bits | Candidate-specific reference evidence only after independent verification; does not prove global optimality, close a region, or create an operational incumbent. |
| PROJECTION_NO | complete UNRESTRICTED_BASE table for every block, one failed original negative with a named positive equality witness in every block, complete original negative columns, correct zero/free equivalence groups | The underlying projection collision rules out the exact complete partition in unrestricted semantics (also when observed under bounded scope), but not arbitrary coarsenings. Only independently rechecked facts may enter a sound region proof; a verdict string or anonymous zero alone licenses no pruning. |
| BOUNDED_NO | bounded registration and exact=true, with matching capacity provenance | An opaque claim scoped to the exact candidate/capacity. The flag is not an independent proof of infeasibility. No unrestricted or structural pruning, no region exclusion, no bounded optimization authority. |
| UNKNOWN | missing, malformed, stale, wrong-scope, partial, ambiguous NO, untrusted external response, unsupported status or failed validation | No structural witness, incumbent, exclusion, lower bound, or completion claim. Close only a matching pending attempt, not the candidate. Retry with a fresh attempt ID and unchanged registration; isolate late/wrong/unregistered deliveries. |

The adapter's normalized observation always has operational=false and scope=NONE. Even locally authenticated EXTERNAL-labelled test fixtures are not live owner-approved trust. The core pending_candidates view intentionally retains all registered request IDs, including observed mock ACCEPT/NO; it is not a certified search frontier. Simulator/mock observations, opaque bounded failures, and unauthenticated external observations are operationally INCOMPLETE. Independent raw structural verification and independent region/frontier coverage remain necessary for a structural optimum. A resource interruption or partial frontier remains INCOMPLETE; INVALID evidence must not be used. No implication across distinct partitions is assumed.

## Regression matrix

test_p3_contract.py uses only open_gateway and actual core types. Nine unittest methods cover all 27 length-three owner vectors (five legal, 22 illegal), additional malformed owners, empty alphabet request policy, structural/scoped/request identity, duplicate and empty original traces and unused symbols, ID-map order and immutability, sample/scope/request corruption, four distinct verdict paths, table and DFA corruption, UNKNOWN/late/retry/global-attempt isolation, and test-only external authentication. Existing delegation tests must remain intact. The small literal owner list tests interface encoding only; it is not the proof agent's independent exhaustive RGS or region coverage oracle.

## Producer/proof handshake and smallest integration milestone

The interface boundary is ready for offline integration, but the producer and certificate serialization contracts are not yet frozen. The current core assignment (#2) authorizes the structural producer and requires coordination with proof #3; the proof-side P3_REGION_COVERAGE_CONTRACT.md at blob 8a5cbeaf6cd3018ea6c077d71d6ab90376841934 explicitly remains a draft, not a wire schema. Do not infer candidate-envelope fields, certificate fields, or entry-point names from these preparation documents.

The smallest next integration milestone, once #2 and #3 publish matching serialized contracts, is test-only and has no external calls:

1. Consume one producer-emitted complete candidate using the producer's agreed serializer; validate that its complete original-alphabet owner array is canonical and retains unused symbols.
2. Register that exact owner array through open_gateway on the pinned core and assert the returned object is the authoritative RegisteredLedger.
3. Assert the journal/2 REGISTER record binds the exact owner array, sample digest, full scope, request ID, attempt ID and immutable registration provenance.
4. Feed only locally constructed/mock responses through the existing ingest path; assert ACCEPT and PROJECTION_NO remain candidate observations, BOUNDED_NO cannot affect unrestricted search, and UNKNOWN remains pending with safe retry and late-response isolation.
5. Pass the producer's serialized region/frontier certificate to the independently implemented proof verifier using its agreed contract; assert that candidate observations are not silently promoted into region closures or an optimum claim.

Do not add a production ledger, transaction authority, candidate/certificate journal schema, endpoint, transport, or learner modification. The search frontier and its certificate remain search/proof artifacts; the existing journal/2 remains the sole observation ledger. If #2/#3 contracts are not agreed, stop at the already passing boundary suite rather than inventing a compatibility layer.

## Reproduction and status

Authoritative core pin: 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d. Relevant core blobs: registered_ledger.py 092507fc156e604be242e3100117fedc27b96d04, core.py 997304c3adce9d3148d454b079639575f419ba0e, schema.py 65a7522a8442a184c14f7a0fa74fc307ce60229f, evidence_store.py 42e38c8ee590267b292ebc0d678e9d4f3a56849b, sparse_analysis.py f773cc1c6b1a852193ba2afb75aa2fce4941a5c2. Interface production blobs at branch head a1516fc0572d8f520422e517adeb2d1db6482f29: gateway.py 8b314e11c0d935122779365b08666c482697621f; adapter.py c38e441c7327a44adad8a0fe1125d45c93e8ef69; strict_ledger.py a66975de137e3ec556b8c7aacd108cf975c46344; test_gateway_v2.py 502b7c40f7776fc3bab087303e457fae149587c3; test_p3_contract.py 063cc799ec32a637881e55cbee73b7dba09cd3c5; this contract's pre-update blob was 6104ca0f958124b01ca181fc4d8d0d3f4a7d791f.

Pinned interface CI workflow: .github/workflows/p3-interface-contract.yml blob dc03532eb9635f84ce3c9c283d0fcb87ec0b6640, introduced at interface commit a1516fc0572d8f520422e517adeb2d1db6482f29. Actual GitHub Actions run 45563718490 succeeded on Ubuntu 24.04 / CPython 3.13.5 with the exact interface branch head and core pin above. The job ran:
~~~
python -B -m unittest -v test_p3_contract test_gateway_v2
python -B -O -m unittest -v test_p3_contract test_gateway_v2
~~~
Actual logs: 17/17 normal in 0.064s and 17/17 optimized in 0.060s; all checkout, setup and test steps succeeded. The 17 tests are nine P3 contract methods plus eight existing gateway delegation methods. The workflow uses the real pinned core RegisteredLedger; responses are local fixtures and no external endpoint is called.

Limitations: this CI validates the selector boundary and delegation contract, not the not-yet-frozen producer serializer, proof-certificate grammar, independent P3 frontier replay, live evaluator, transport/authentication, durable recovery, bounded optimization, or operational acceptance. P2.1 structural status is VERIFIED for the exact hardened gate; operational status remains INCOMPLETE. No external call, learner edit, merge, deployment or operational acceptance is claimed.
