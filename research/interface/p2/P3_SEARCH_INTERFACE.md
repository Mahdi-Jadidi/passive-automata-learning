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


## M2 addendum — frozen producer/proof handshake and native fixture preparation

This section supersedes the earlier M1 statement that the producer/proof serialization contract was not yet frozen. The integration-lead freeze is `implementation/partition_feedback_final/research/P3_SERIALIZATION_V1.md` at commit `ff61b1c56138c89fc0ad9a615f0b2a587b03393a` (blob `9dd487605f0dfdc6735f7d53a42627039fb57db8`). It is the sole v1 wire contract: `p3-trusted-scope/v1` and `p3-region-frontier/v1`; no selector-v2/1 or journal/2 schema change.

### Independent proof entry point

Agent #3's current verifier source blob is `a35281492e2677f0c57d8955227bc233d95492ea` in its M2 proof branch. The source imports only independent P2 replay modules and does not import `selector_v2` or producer search/DSU/pruning code. The reported CI run `45591575274` passed 10/10 normal and 10/10 optimized tests on Ubuntu 24.04 / Python 3.13.5. Its stable CLI is:

```sh
python -B tests/reference/p3_frontier_verifier.py \
  --make-trusted-scope --raw RAW.json --journal JOURNAL.json --out TRUSTED.json

python -B tests/reference/p3_frontier_verifier.py \
  --raw RAW.json --journal JOURNAL.json --scope TRUSTED.json --proof CERT.json
```

The verifier receives exact byte files. The trusted-scope builder independently replays the exact uncompressed journal/2 bytes, derives `root_owner`, binds the exact selector-v2/1 unrestricted scope, and hashes the exact journal bytes. Do not parse/reserialize or normalize those byte inputs before invoking the verifier. `VERIFIED` is a structural proof result only; `operational_status` remains `INCOMPLETE`.

### Raw-only integration inputs

Two original raw-only inputs have been copied byte-for-byte from the recovered input ZIP into `research/interface/p2/fixtures/p3/`. They were checked against Agent #4's seven-fixture input manifest and contain only `alphabet`, `positive`, and `negative`; no evaluation index or planted reference is included.

| Fixture | Repository path | Bytes | SHA-256 | Git blob |
|---|---|---:|---|---|
| tiny_choice | `fixtures/p3/tiny_choice.raw.json` | 228 | `1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23` | `ef3f41b4c5e27da6ffd4882804399abf454d51a7` |
| small_choice | `fixtures/p3/small_choice.raw.json` | 416 | `10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b` | `b361642873a73bae454d388cbfb2284559dbd69b` |

The fixture manifest is `fixtures/p3/manifest.json`, blob `206abf0f0e3346a3fb644961934ba1797ceef487`. Source recovered ZIP SHA-256 is `a280e093aa298af359f0e30408b633eefb0283e02471dba52f3d78f1e4059220`; source seven-fixture manifest blob is `68d2414bd7e1f9294a850268369a55559d440b06`.

### Offline integration order

For each actual tiny_choice/small_choice producer certificate (one/all modes), the integration test must:

1. Pin the producer, verifier and core source commits/blobs and verify SHA-256 plus Git blob identities for every raw, journal/2, trusted-scope and certificate file.
2. Pass those exact four byte sequences unchanged to Agent #3's verifier CLI. For raw-only fixtures, journal/2 is the canonical empty export from the pinned core; trusted scope must be generated by Agent #3's independent builder, never by producer-supplied `root_owner`.
3. Require verifier `status=VERIFIED` and `operational_status=INCOMPLETE`. Extract only the independently verified canonical owner array(s) from the verifier result.
4. Only then call `open_gateway(raw)`, assert the returned object is the exact pinned core `RegisteredLedger`, and register the owner array with distinct request and globally unique attempt IDs.
5. Assert registration binds the verifier's exact sample/scope and complete original-alphabet owner; exported journal/2 contains only the ordinary REGISTER/REQUEST observation path and contains neither certificate bytes nor proof records.
6. Run the existing UNKNOWN, BOUNDED_NO, retry, late-response and scope-isolation regressions. UNKNOWN remains pending; BOUNDED_NO is capacity-scoped and cannot prune unrestricted search; a late response cannot mutate another attempt or scope.

The interface gateway source remains blob `8b314e11c0d935122779365b08666c482697621f`; the authoritative core RegisteredLedger source remains blob `092507fc156e604be242e3100117fedc27b96d04` at core pin `4e21dbf0d06c030681e774cb15f1a5cf0c802f0d`.

### Current M2 gate status

The frozen v1 grammar, independent verifier CLI, and raw-only inputs are available. The following actual producer artifacts are now published from core run `45592454384` at producer commit `391abf97df3b67661082c907d9ce20b4f69636c2` (search source blob `73da7bea551df73a8676b0adf0401cd7f2d307b5`, region source blob `657c4e0e4059b32cd9e6477e61c7a3673290f36d`, run harness blob `9dd3c684dcae20dc5dec946878d61ac9647eb535`):

| Fixture/mode | Certificate bytes | SHA-256 | Git blob | Independent proof |
|---|---:|---|---|
| tiny_choice / one | 46,588 | `91996d9bc6a3d7e88b5c89fc44158bc1cd89cf778256ec67839e1d38555e7ec8` | `bce55d7db1ddbcf6140b2a841f74bb51dad8f2f0` | VERIFIED |
| tiny_choice / all | 99,931 | `1be8394e233fe2c5a337766d73a1385145ab82b95d75273d5d548f60b2b781c0` | `eafd651d28fc1f06f60bdbc4c0a4095a04dc390b` | VERIFIED |
| small_choice / one | 264,463,193 | `dafa72f9e8ec4cc63330d4a7cd420cd478237dd7431c7e488267345ed810471e` | `d1539a0a9ed03d208a88c515c51f6e6473126c3c` | VERIFIED |
| small_choice / all | 1,399,367,871 | `9fb5f5bbc1c64e90bc955f73d2325a1d159224e91258e8a8758a34595102e2a7` | `e2f00717be846336b1f3287a8dd58070272434fd` | VERIFIED by pinned verifier + full RGS |

The small_choice/one proof replay is Agent #3 run `45592784988`, job `139134169293`: normal and optimized verifier runs both returned `VERIFIED`, `operational_status=INCOMPLETE`, 1,091,642 frontier nodes and 659,914 exact checks. Independent RGS replay visited 4,213,597 partitions and confirmed optimum cost 4 with all 16 optima. Its exact raw/journal/trusted/certificate pins are in the proof artifact; the certificate Git blob is `d1539a0a9ed03d208a88c515c51f6e6473126c3c`.

The pre-existing P2.1 `shared_gateway.py` path is unchanged and is not used by P3. P3's only registration entry point is `open_gateway`, which returns the exact pinned core `RegisteredLedger`; the core's internal `EvidenceLedger` is a disposable batch validator, not a second authority. The native test asserts the returned object has exact type `RegisteredLedger` and that its initial `export()` bytes equal the independently replayed journal/2 bytes.

The interface branch now has an offline native integration test and workflow. It pins producer commit/blob, proof commit/blob, core RegisteredLedger commit/blob, and interface gateway/adapter/parser blobs; downloads all four actual producer artifacts; rebuilds trusted scope with Agent #3's pinned CLI; passes exact raw, journal/2, trusted-scope and certificate bytes unchanged to the verifier; and only then registers verifier-returned owner arrays through `open_gateway`.

All-four native integration run `45597784081` completed SUCCESS:
- Exact producer/verifier/core/interface/workflow source pin checks passed.
- Actual artifact downloads: 4/4.
- Existing gateway/journal/2 suite: 18/18 normal and 18/18 optimized.
- Native verify-before-register suite: 2/2 normal and 2/2 optimized.
- Normal native suite: 329.730 s, maximum RSS 10,341,116 KiB.
- Optimized native suite: 51.194 s, maximum RSS 2,028,580 KiB.
- The pinned frontier verifier returned VERIFIED for all four actual certificates in both modes.
- The pinned RGS oracle visited 203 partitions for tiny_choice and 4,213,597 partitions for small_choice; it matched the complete owner-array sets (4 and 16 optima) before registration.
- The invalid certificate was rejected before gateway registration; UNKNOWN remained pending; BOUNDED_NO remained non-pruning; late responses could not cross scopes; journal/2 contained only ordinary request/registration records and no proof/certificate material.
- Reproducible logs/summary artifact: `15014038954` (`p3-native-interface-45597784081`).

The previous small_choice/all artifact from core run `45592454384` remains excluded: it was PARTIAL/ENTRY_CAP at 4,000,000 entries, its earlier verifier returned INCOMPLETE/MemoryError before checking a frontier node, and its checkpoint/resume certificate differed. The expanded replacement run `45593819618` completed SUCCESS at workflow commit `f8de4b6b14b3840d699d3c47ccc06a71eb5e04ae`, checking out producer source commit `391abf97df3b67661082c907d9ce20b4f69636c2`. It produced the 1,399,367,871-byte EXHAUSTED certificate (SHA-256 `9fb5f5bbc1c64e90bc955f73d2325a1d159224e91258e8a8758a34595102e2a7`, Git blob `e2f00717be846336b1f3287a8dd58070272434fd`); normal/optimized and fresh-run/checkpoint-resume bytes match; the core's older pinned verifier exited 0 in both modes; `structural_gate=PASS`, `operational_status=INCOMPLETE`.

Agent #3's separate published-artifact replay/report is still requested for project audit, but this interface workflow directly executed Agent #3's exact verifier source commit `d89bab4c005d17c8b27d4c1e6dd291135aca649a` / blob `540a7cf9e7b048684d3ea03def744175ae629b65` and RGS oracle blob `da28e66ca4ff74388be79bf9549c8e02f0c60410` on the exact artifact files. The instrumentation follow-up run `45599363934` is collecting per-case verifier/RGS counters; it is supplementary to the already successful all-four gate. Structural/operational acceptance remains INCOMPLETE; PR #6 remains OPEN/DRAFT/UNMERGED.
