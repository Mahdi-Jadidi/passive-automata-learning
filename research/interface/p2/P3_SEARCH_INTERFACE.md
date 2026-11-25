# P3 search/interface boundary contract (draft for integration review)

Date: 2026-11-25. Scope: selector-side preparation and regression tests only.
Authority: NEXT_SESSION_HANDOFF_04.md at integration head 44ac8cd29dc51ad19da7c28095d4ecb87d06121b and REVIEW03_FINAL.md at interface parent ae04a28304507fa16830fcb470f52103d9a588c4.

## Gate and non-goals

The recorded P2.1 structural gate passed on its previous pins. The post-hardening combined regression still requires confirmation by the core and independent proof owners. This document and tests do not start P3 search implementation, authorize pruning, certify coverage, or establish bounded/operational optimization. P3 initially means unrestricted structural/reference search only (B=0). No learner or baseline changes, endpoint calls, real transport, new journal version, competing state or dual-write.

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

## Reproduction and status

Core authority pin: 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d. Relevant blobs: registered_ledger.py 092507fc156e604be242e3100117fedc27b96d04, core.py 997304c3adce9d3148d454b079639575f419ba0e, schema.py 65a7522a8442a184c14f7a0fa74fc307ce60229f, evidence_store.py 42e38c8ee590267b292ebc0d678e9d4f3a56849b, sparse_analysis.py f773cc1c6b1a852193ba2afb75aa2fce4941a5c2. Interface production blobs unchanged: gateway.py 8b314e11c0d935122779365b08666c482697621f; adapter.py c38e441c7327a44adad8a0fe1125d45c93e8ef69; strict_ledger.py a66975de137e3ec556b8c7aacd108cf975c46344.

From the interface branch checkout:
```sh
git worktree add --detach /tmp/core-p3-interface 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d
cd research/interface/p2
export PYTHONPATH=/tmp/core-p3-interface/implementation/partition_feedback_final
python -m unittest -v test_p3_contract test_gateway_v2
python -O -m unittest -v test_p3_contract test_gateway_v2
```

Initial validation: local test source compiled with python -m py_compile and python -O -m py_compile (both exit 0); Git blob 063cc799ec32a637881e55cbee73b7dba09cd3c5. Direct git ls-remote failed with 'Could not resolve host: github.com'. GitHub connector reads/writes are available. Full actual gateway execution not yet established at this commit; no runtime pass, timings/RSS, independent certification, CI, or operational acceptance is claimed. Any subsequent runtime validation must explicitly record exact source bytes and actual results.
