# Interface stream progress — issue #5

## M1: source audit and contract
Commands/actions: GitHub fetch_issue(5), fetch_issue_comments, fetch branch metadata, compare_commits, contents and fetch_file for AGENTS.md, nested PROJECT_HANDOFF.md, SELECTOR_V2_INDEX.md, model.py and all four dated reports; project Library read of main (1).pdf, targeted pp.12–14. Actual: issue open, no comments; integration head 4a2f3d6ce0b4b974430f02d79b1a98f2c8fc9e4b; assigned branch c0aae9fb222aef9dfea4c13cb44e5a37f0d86f8a two commits behind, no stream changes. Root handoff/report paths returned 404; resolved under implementation/partition_feedback_final/. Reviewed relevant interface passages of four reports, paper §5.1/5.2 and handoff. Contract records explicit distinction between mathematical semantics and unspecified wire. No live endpoint, no external calls, no deployment claim. Next: executable mock conformance fixtures, test run, draft PR. Paths interpreted literally from issue ownership (root research/interface/ and progress/interface.md). No merge or edits outside stream.

## M2: executable mock conformance
Executed makeFixtures() and runTests(fixtures) on the exact JavaScript function implementations serialized into audit.mjs, in an isolated JavaScript runtime. Actual result: 37 passed, 0 failures. Reproduce using Node.js 18+ from repository root: `node research/interface/test.mjs`. Node CLI itself was not invoked in this session. No real transport or authentication: verifyReceipt is an injected mock predicate; all outputs operational=false. Fixture digests are placeholders, not cryptographic claims. Block/table order and explicit DFA representation are conservative normalized choices, not asserted wire format. The strict reference rejects incomplete tables atomically; it does not implement reference resolution, separate exact-verdict salvage, or global replay storage. No live evaluator invoked. Next: draft PR; owner protocol confirmation and Python integration remain outstanding.

## M3: issue #10 / Python normalized interface checkpoint
Read issue #10, integration review at 26d1dc39d04188737677f35d82d91ae0f8af99c6, and #2 core schema + golden tests at cd627dcdf2a9b73cb79d313f3b864c8284b55082. Posted schema review in issue #10. Implemented standalone Python P2 adapter under research/interface/p2; historical JS unchanged. Recomputes sample digest, restricts family, rejects empty tokens and external empty alphabet, explicit original ID mapping, strict receipt binding, literal table/DFA checks and atomic immutable observation append. Python 3.13.5: cd research/interface/p2 && python -m unittest -v test_adapter; 8 methods passed (including mutation subtests), 0 failures, 0.008s. Four new sample golden vectors and both core golden constants match. Exact local git hash-object equals GitHub blob SHA for adapter.py (c38e441c7327a44adad8a0fe1125d45c93e8ef69), test_adapter.py (bfa7dee3373da7d267c373e238b95d271a8a2669), golden.json (602d16bd2cc54f299521789383cf1753ba66b3eb), results.txt (000031f879c4a61b9cc4f16148c8349bf73b0802). Capacity digest and response grammar proposed; no owner-approved transport, auth, durable attempt registry or final typed core ledger integration. All observations nonoperational and no pruning. Next: review with core/proof streams, verify PR scope, preserve draft.

## M4: registered attempt lifecycle and atomic ingestion
Implemented strict_ledger.py with locally registered immutable attempt/scope/source/capacity/ID maps, duplicate-key and malformed JSON rejection, full normalized input bytes and digest in event/quarantine, locked atomic state replacement, immutable typed outcomes and retry with new attempt. UNKNOWN does not eliminate candidate; replay/unsolicited attempts cannot append evidence. Actual Python 3.13.5 command: cd research/interface/p2 && python -m unittest -v test_adapter test_strict_ledger; 13 test methods passed, 0 failures, 0.014s. Concurrent replay: one accepted observation and 15 UNKNOWN quarantines from 16 deliveries. No operational ACCEPT even with positive test-auth callback. Exact local git hash-object matches GitHub blob SHA strict_ledger.py a66975de137e3ec556b8c7aacd108cf975c46344, test_strict_ledger.py 268a4d118e383f1f4c559d972d1d607a0514fd81, results_p2.txt 748a8e7991a0dbcf4f240b6cc1ef785ec0e5a058. Memory-only; no durable transaction, size/budget cap, live transport or authorized operational evidence. Shared typed ledger integration and independent replay remain pending. Next: post cross-stream checkpoint to #10/PR #7 and existing draft PR #6; do not merge.

## M5: P2.1 actual shared-ledger integration
Read integration review 02 and latest issue #10 comment at b2c20d7; coordinated directly on PR #7 (comment 7144430457) and issue #10 (7144431039). SharedGateway uses real core EvidenceLedger at 539af04, no standalone observation list; strict normalized conversion, global attempt uniqueness, immutable origin/map/capacity binding, response and receipt artifacts, UNKNOWN control record with no feedback, retry new ID, nonoperational candidate pending. Tested actual core source copied from connector, all five Git blobs matched; clean checkout DNS blocked. Python 3.13.5 combined unittest suite 19 passed 0 failures 0.029s, integration-only -O 6 passed 0.011s. Actual closure/structural/adapter records appended and replayed on fresh EvidenceLedger. 16 concurrent deliveries exactly one observation. Code and result blobs matched (shared_gateway.py 33ef122814c409cc7c0d201b0cb4c3127b078862; test_shared_gateway.py 0eef50c4486df80fa5b6517739b280891500e9d7; results_shared.txt 3b1519724b8d0c5c4a2b9956df26e20fc61933d6). See P21_SHARED.md for commands and source pins. Sidecar and core journal serialized under single in-memory lock; durable atomic metadata schema and proof replay pending. No live protocol/auth or operational ACCEPT. Next: publish actual producer/adapter artifact for proof stream and request joint review.

## M6: actual producer/adapter journal export for independent replay
Generated two actual producer/gateway cases via export_roundtrip.py, replayed both on fresh pinned core EvidenceLedger; Python normal and -O runs byte-identical (cmp). 16 total journal records, five REQUEST and four simulator OBSERVATION entries, one unanswered request; owners [0,0,2] and [0,0,0]. Committed journal 7514 bytes and full bundle 16592 bytes, exact local Git blob matches 1d607710bb6c136800b256f2ad0e4917cb948168 and 03cc14aa5fa099a94a20be2fb296c145d6d8445b. Script blob ddd211111322ff1bae9c7e2a0c0f4eaef40c9d75 and result log 6ca7df167b6dd6d1c80cce6a925f0f150134c785 match. Reproduce using pinned core PYTHONPATH in P21_SHARED.md, python export_roundtrip.py generated, repeat -O and cmp. No external calls or independent proof-kernel replay claim; request #3 replay actual journal, including false EXHAUSTED mutation. No core schema changes; sidecar approval pending.

## M7: review 03 — delegate to authoritative core journal/2
Read review 03 and issue #10 latest core-owner comment. Coordinated #7/#8/#10. New gateway.open_gateway returns the exact core RegisteredLedger at 4e21dbf, no wrapper or state duplication; old ledgers historical only. Actual Python 3.13.5 run against six byte-verified core sources: 27/27 full in 0.066s, 8/8 delegation -O in 0.032s. Verified exact Git blobs of gateway.py (8b314e11c0d935122779365b08666c482697621f), test_gateway_v2.py (502b7c40f7776fc3bab087303e457fae149587c3), results_journal2.txt (e8c92c6b0d8a2f348f4f570133b0647daed79d3d), results_journal2_opt.txt (128f1852b545d33ab4d8089d298bbd3520601353). Tested receipt reuse/tamper, exact-byte and provenance binding, global attempt uniqueness, strict JSON, typed feedback/DFA, rollback, reentrant auth, concurrent registration/observation, UNKNOWN retry/pending. No live external calls; HMAC fixture only. DNS blocks clean checkout; independent /2 sign-off and combined gate remain open. See JOURNAL2.md.

## M8: actual journal/2 artifacts for proof replay
Ran export_journal2.py with actual delegated core 4e21dbf, normal and -O; byte-identical JSON and gzip. Two artifacts 41798 and 3400 decompressed bytes, 18 and 1 outer events, 18 and 4 inner records. SHA256 caf40422d9d3e6d0cd8257da4b757cacd71cda1e6db089493421c912515edf94 and adabd0b274ebaa2ce55aab7f874f6485664399d4b0df59b013d158cfb2338491. Verified uploaded gzip blobs a61d493991c7464641c6d182929ba8c185f57421 and 6efdc4356b79e4368e17c59b6376d50861762c12, script 1d3a16f03171f2259427ecda8de94282ffda8cae and log cb22bed778d85e57d1092706ebc2f576dc860614. Actual core events only; no independent proof result embedded. Request #3 full /2 replay and #2 combined gate. HMAC test-only, no live calls or operational acceptance. DNS/CI, durability and scale remain limitations. See JOURNAL2.md for details.

## M9 — plaintext interchange access
Proof agent #3 requested plaintext artifacts in issue #10 comment 7145087025. Added interface-journal2.json and interface-journal2-epochs.json, byte-identical to decompressed M8 artifacts and the original local generated files: exact Git blob hashes 4c66a0f69633cf1f07bcf04e8852cd4207995b19 and 2e862db654dfbaaba0d6285444ba81b12c984b2b. Same SHA-256 and sizes as the above table, no change to journal content or semantics. For direct retrieval use these plaintext files; independent replay remains proof-stream responsibility.

## M10 — independent proof sign-off and final combined P2.1 gate

Proof agent #3 signed off the exact four core/interface journal/2 artifacts at executable proof pin 83762437ba05e1def9dde5edff8c7d44878f4269; sign-off docs head e8895a344821f7cd463823774e6bc591e064264c (compare confirms only two audit documents changed). Issue #10 comment 7145173732 records 4/4 artifact replays, structural costs 2/2/1/2, 31 counted malformed outer/interface cases rejected, four resource caps INCOMPLETE, false EXHAUSTED INVALID and operational INCOMPLETE. No producer/audit_journal imports in independent verifier.

Core owner then published checkpoint 9 at c5e7e170add6f92e129099bf7444f5fd7a29eb3a. Inspected REVIEW03_FINAL.md and final-gate.json: status VERIFIED, blockers [], operational_status INCOMPLETE. The core report records 40/40 normal, 28/28 optimized, four exact artifact replays VERIFIED, 31 counted mutation cases rejected per mode, five caps INCOMPLETE, false EXHAUSTED INVALID and PARTIAL closure INCOMPLETE; 23.04s elapsed, 219272 KiB peak RSS. The combined runner was executed by core owner; this interface stream inspected the committed report and machine-readable result, not a separate rerun. Four artifact SHA-256 and structural costs are in research/interface/p2/REVIEW03_FINAL.md.

The narrow P2.1 structural gate is closed for the specified reference/simulator path. Earlier M7/M8/M9 notes describe status at those historical checkpoints and are superseded by M10 where they said independent replay/combined gate pending. Interface delegation remains actual core RegisteredLedger with no competing production state. PR #6 remains open/draft/unmerged. No external calls, live receipt authority, deployment, learner/baseline changes, P3 implementation or operational acceptance. Limitations remain DNS-blocked clean checkout/CI (byte-verified snapshots instead), memory-only journal, potentially quadratic full-history replay, and separate transport/authentication/capacity/durability gates. Benchmark stream is not part of this narrow gate.
See research/interface/p2/REVIEW03_FINAL.md and core selector_v2/integration/REVIEW03_FINAL.md.


## M11 — post-hardening P3 boundary review and integration handshake

Read NEXT_SESSION_HANDOFF_05.md at 80445eb0c3977389342eeb92aa7e530f817cbff8, INTEGRATION_REVIEW_05.md at 53da42edb57cdfd970a475d2d71f750ebd0fcbbc, issue #11 and issue #5 comments, P3_SEARCH_INTERFACE.md and test_p3_contract.py. Confirmed current interface branch head a1516fc0572d8f520422e517adeb2d1db6482f29 and PR #6 remains OPEN/DRAFT/UNMERGED. P2.1 narrow structural gate is VERIFIED at hardened proof pin cf5a007571853b6cdf6259fa2a9a95f5c1e351f8; operational status remains INCOMPLETE. P3 authorization is unrestricted structural exact search only (B=0).

Independently inspected the exact interface CI run 45563718490, job 139033302286, including job steps and logs. Ubuntu 24.04 / CPython 3.13.5; both commands exited 0:
- python -B -m unittest -v test_p3_contract test_gateway_v2 — 17/17 in 0.064s.
- python -B -O -m unittest -v test_p3_contract test_gateway_v2 — 17/17 in 0.060s.
Nine P3 boundary methods and eight existing gateway delegation methods passed in each mode. The workflow checked out interface commit a1516fc0572d8f520422e517adeb2d1db6482f29 and core RegisteredLedger pin 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d. Exact blobs: gateway.py 8b314e11c0d935122779365b08666c482697621f; adapter.py c38e441c7327a44adad8a0fe1125d45c93e8ef69; strict_ledger.py a66975de137e3ec556b8c7aacd108cf975c46344; test_gateway_v2.py 502b7c40f7776fc3bab087303e457fae149587c3; test_p3_contract.py 063cc799ec32a637881e55cbee73b7dba09cd3c5; workflow .github/workflows/p3-interface-contract.yml dc03532eb9635f84ce3c9c283d0fcb87ec0b6640; P3_SEARCH_INTERFACE.md before this update 6104ca0f958124b01ca181fc4d8d0d3f4a7d791f. The gateway delegates to the exact core RegisteredLedger; journal/2 remains sole observation authority.

Smallest next integration is test-only and waits on #2/#3 to agree and publish the exact producer candidate serializer and serialized region/frontier certificate contract. The current proof contract blob 8a5cbeaf6cd3018ea6c077d71d6ab90376841934 explicitly says DRAFT/not a wire schema; core #2 has not yet published a serialized producer interface. Do not invent envelope or certificate fields. Once agreed: exercise producer serialization -> complete original-alphabet owner array -> open_gateway registration -> exact journal/2 binding; feed mock-only observations through ingest; pass the serialized certificate to the independent verifier and prove observations do not become frontier closures. No endpoint or external learner call. Existing P3 boundary suite already covers owner-array validity, unused symbols, candidate/scope/request identities, maps, all four verdicts, UNKNOWN/retry/late isolation and core delegation, but it does not test the producer serializer or independent certificate grammar.

Updated research/interface/p2/P3_SEARCH_INTERFACE.md to record Review05 authority, actual CI evidence and this integration handshake. This checkpoint is documentation/coordination only; no production source, ledger, journal schema, learner, or transport changed. The documentation update was tested by push workflow run 45565081120 (job 139037792674) on Ubuntu 24.04 / CPython 3.13.5: python -B -m unittest -v test_p3_contract test_gateway_v2 passed 17/17 in 0.071s; python -B -O -m unittest -v test_p3_contract test_gateway_v2 passed 17/17 in 0.057s; all job steps succeeded. The tested documentation commit is d60d686e30e317ec162ed61ba4e6d5c9d188a980; subsequent dc1643d... changes only this progress log. Operational status remains INCOMPLETE.


## M12 — M2 frozen-contract coordination and byte-pinned native inputs

Read Handoff 06, Integration Review 06, the final serialization contract at `ff61b1c56138c89fc0ad9a615f0b2a587b03393a` (blob `9dd487605f0dfdc6735f7d53a42627039fb57db8`), the P3 interface contract/tests, and issues #11/#5 plus #2/#3/#4 comments. Confirmed PR #6 remains OPEN/DRAFT/UNMERGED and branch baseline was `98bc69dcc013d28a74e2035fd417dbe66ba74e00`.

Proof #3 M2 verifier source blob `a35281492e2677f0c57d8955227bc233d95492ea` exposes `build_trusted_scope(raw, exact_journal2_bytes)`, `verify_frontier(raw, exact_journal2_bytes, trusted_scope, proof, *, budgets)`, and the frozen CLI in the v1 contract. Its reported CI run `45591575274` passed 10/10 normal and 10/10 optimized on Ubuntu 24.04 / Python 3.13.5. Source imports only independent P2 replay modules; no `selector_v2` or producer imports. Proof PR report head `72144bb8799c00c2629a853303f122f4e825c9a5`; follow-up documentation-triggered run `45591893784` was in progress at inspection.

Core #2 PR head remains `fa12fdcca0a8d7a9a697bb617ed09453cb56c3d5` (M1 primitives). No native serializer/CLI or actual tiny_choice/small_choice certificates are published at this pin. Posted exact artifact/CLI/source-pin requests to issues #2 and #3 (comments `7159278885`, `7159279694`) and an M2 dependency checkpoint to PR #6 (comment `7159347795`). No speculative wire fields or synthetic certificate were introduced.

Recovered the input-only Library ZIP `/Passive learning research/p3-exact-search-inputs-recovered.zip`, SHA-256 `a280e093aa298af359f0e30408b633eefb0283e02471dba52f3d78f1e4059220`, and verified the exact original tiny/small fixture member bytes against Agent #4's seven-fixture manifest. Added copies under `research/interface/p2/fixtures/p3/` with no newline or content normalization:
- `tiny_choice.raw.json`: 228 bytes, SHA-256 `1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23`, Git blob `ef3f41b4c5e27da6ffd4882804399abf454d51a7`, file commit `65ed53a2afdc4fe91cafa34e1f101addec0a910e`.
- `small_choice.raw.json`: 416 bytes, SHA-256 `10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b`, Git blob `b361642873a73bae454d388cbfb2284559dbd69b`, file commit `b946850931b7050d373d41da9ecec1fa53e327a6`.
- Fixture manifest: Git blob `206abf0f0e3346a3fb644961934ba1797ceef487`, file commit `6a6575bd93067c30e27d942cb2a3198ed37cae71`; source seven-fixture manifest blob `68d2414bd7e1f9294a850268369a55559d440b06`.

Verification performed by extracting each member from the recovered ZIP, checking its byte length and SHA-256, computing the Git blob object SHA-1, then fetching each committed path from GitHub and confirming its returned blob SHA and byte count match exactly. Reproduction after checkout:
```sh
sha256sum research/interface/p2/fixtures/p3/{tiny_choice,small_choice}.raw.json
git hash-object research/interface/p2/fixtures/p3/{tiny_choice,small_choice}.raw.json
```

Updated `research/interface/p2/P3_SEARCH_INTERFACE.md` with the frozen v1 verifier handshake, exact CLI, pinned fixture hashes, required verify-before-register order, and the explicit NOT RUN blocker. Documentation commit: `2dbef769f7cda2a950063cb29ec38b80cbb80fad`; new document blob `b56ff9951e6f2d55bc53f4835f3c04e2b18b82e3`.

This milestone validates raw input bytes and integration coordination only. No producer certificate was available, so no proof replay or candidate registration was run. Existing interface tests have not yet been rerun on these commits; push CI is the next check. No gateway/adapter/core source, journal schema, learner, external endpoint, or transaction authority was changed.


## M13 — Native P3 certificate → independent verifier → authoritative ledger integration

### Exact source pins

- Interface branch current checkpoint: `cbaa5952ab2d7a1b4b20948fc62f4f97aec806eb`.
- Producer artifact run: `45592454384`, producer commit `391abf97df3b67661082c907d9ce20b4f69636c2`; `selector_v2/edr_search.py` blob `73da7bea551df73a8676b0adf0401cd7f2d307b5`, `edr_bb.py` blob `657c4e0e4059b32cd9e6477e61c7a3673290f36d`, `run_case.py` blob `9dd3c684dcae20dc5dec946878d61ac9647eb535`.
- Independent verifier commit `d89bab4c005d17c8b27d4c1e6dd291135aca649a`; verifier blob `540a7cf9e7b048684d3ea03def744175ae629b65`; RGS12 oracle blob `da28e66ca4ff74388be79bf9549c8e02f0c60410`.
- Authoritative core ledger commit `4e21dbf0d06c030681e774cb15f1a5cf0c802f0d`; `registered_ledger.py` blob `092507fc156e604be242e3100117fedc27b96d04`.
- Interface gateway/adapter/strict parser blobs: `8b314e11c0d935122779365b08666c482697621f`, `c38e441c7327a44adad8a0fe1125d45c93e8ef69`, `a66975de137e3ec556b8c7aacd108cf975c46344`.

### Actual producer byte pins

The interface workflow downloaded these three actual producer artifacts from core run `45592454384`; the Agent #3 proof replay logs independently reproduced every file hash and Git blob ID.

| Fixture/mode | Raw (bytes; SHA-256; Git blob) | Journal/2 (bytes; SHA-256; Git blob) | Trusted scope (bytes; SHA-256; Git blob) | Certificate (bytes; SHA-256; Git blob) |
|---|---|---|---|---|
| tiny_choice / one | 228; `1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23`; `ef3f41b4c5e27da6ffd4882804399abf454d51a7` | 130; `290c8490b2a4ab5b4c6f49012c7580152ecc6eb7c4bad036bcf71b91925c48f5`; `3a50ce7567b563fa87dc54395451af58b19d75fa` | 560; `9a43619ffabac9c44e65e69ccc0fc7e5c30033e021625582aa6e31668bdcd172`; `adf7723aa76cdf9bed09e9d42c65511c8c1e8ae8` | 46,588; `91996d9bc6a3d7e88b5c89fc44158bc1cd89cf778256ec67839e1d38555e7ec8`; `bce55d7db1ddbcf6140b2a841f74bb51dad8f2f0` |
| tiny_choice / all | same raw | same journal | same trusted scope | 99,931; `1be8394e233fe2c5a337766d73a1385145ab82b95d75273d5d548f60b2b781c0`; `eafd651d28fc1f06f60bdbc4c0a4095a04dc390b` |
| small_choice / one | 416; `10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b`; `b361642873a73bae454d388cbfb2284559dbd69b` | 130; `3d4ae1a0cff38cbc7b1bf7a2269c29a256abe205b7efc8f7ed3a31eb17334019`; `191247f1112e15ccc571656026e6591b42a13d3b` | 754; `89ade477b7f9029acdf8c44b4fe5d1f724038cd795c28b289cd2154e387c841b`; `616e0b864a0119a333bcb8d3248bec0d871bc6f4` | 264,463,193; `dafa72f9e8ec4cc63330d4a7cd420cd478237dd7431c7e488267345ed810471e`; `d1539a0a9ed03d208a88c515c51f6e6473126c3c` |

Normal and optimized producer certificates are byte-identical for all three artifacts. For small_choice/one, producer checkpoint/resume output is also byte-identical. Trusted scopes were independently built from exact raw and journal/2 bytes; the interface test rebuilt them again with the pinned Agent #3 CLI and required byte equality.

### Independent proof evidence

Agent #3 published-artifact replay run `45592784988`:
- tiny_choice/one job `139134218981`: `VERIFIED`, optimum 2, owner `[0,0,2,3,3,5]`, 221 frontier nodes, 215 exact checks, 60,140 verifier work units; independent RGS visited 203 partitions and found 4 optima.
- tiny_choice/all job `139134171067`: `VERIFIED`, optimum 2, 461 frontier nodes, 677 exact checks, 131,556 work units; independent RGS visited 203 partitions and matched all 4 owner arrays.
- small_choice/one job `139134169293`: `VERIFIED`, optimum 4, owner `[0,0,2,3,3,5,6,6,8,9,9,11]`, 1,091,642 frontier nodes, 659,914 exact checks, 457,570,571 verifier work units; independent RGS visited 4,213,597 partitions and matched all 16 optima.
- Every replay passed in normal and optimized Python and retained `operational_status=INCOMPLETE`.

### Interface integration evidence

New test `research/interface/p2/test_p3_native_integration.py` and workflow `.github/workflows/p3-native-integration.yml` are committed. The test passes exact raw, journal/2, trusted-scope and certificate bytes through Agent #3's CLI; verifies independently rebuilt scope bytes; requires `VERIFIED`; only then opens the gateway and registers the returned owner array(s). It checks exact core ledger type/export, original-alphabet owner arrays, `(sample_digest, tuple(owner))` identity, exact selector-v2/1 scope, distinct request/global attempt IDs, pending candidates, and absence of certificate/proof material in journal/2. A corrupted certificate returns `INVALID` and does not open/register a ledger. The native fixture also confirms `UNKNOWN` remains pending. The existing suite verifies BOUNDED_NO cannot prune unrestricted candidates; a new regression verifies late responses cannot cross sample scopes even when attempt tokens collide.

Workflow run `45595243572` completed SUCCESS:
- Exact source pin checks: PASS.
- Actual artifact downloads: 3/3.
- Existing gateway/journal/2 tests: 18/18 normal and 18/18 optimized.
- Native verify-before-register tests: 2/2 normal (82.056 s, max RSS 2,028,348 KiB) and 2/2 optimized (83.818 s, max RSS 2,031,096 KiB).
- Uploaded reproducible logs/summary artifact: `15012841664`, `p3-native-interface-45595243572`.

### Remaining gate

Only `small_choice / all` is outstanding. Core expanded run `45593819618`, producer commit `f8de4b6b14b3840d699d3c47ccc06a71eb5e04ae`, is still executing with 6,000,000 entry cap, 600 seconds and 13 GiB address-space cap. No artifact or independent proof exists yet. Once available, require Agent #3 exact-byte replay and RGS agreement over 4,213,597 partitions, then add the fourth artifact to the interface workflow and rerun normal/-O. Until then M2 is a successful partial integration, not complete acceptance. Operational status remains INCOMPLETE. PR #6 remains OPEN/DRAFT/UNMERGED.


## M14 — Small/all exclusion and expanded-resource gate

Agent #4's audit of the earlier `small_choice / all` artifact from core run `45592454384` found it is NOT a usable P3 certificate:
- producer result PARTIAL / ENTRY_CAP; generated 4,000,000 entries, expanded 150,745, closed 3,849,256, exact checks 192,520, work 114,128,965, frontier bytes 857,999,077;
- partial certificate 1,020,213,083 bytes, SHA-256 `bde267836723cf0de3d66e2f19424f165701c6633dd68d83c71b2db260a55c89`;
- the earlier proof verifier pin `e1d022496f98bf50fd57d5ef3a7a0bc8194c817c` returned INCOMPLETE / MemoryError before visiting a frontier node (nodes=0, exact checks=0, work=1,372, peak RSS 5,195,692 KiB);
- the one-entry checkpoint/resume output differs: 1,020,213,333 bytes, SHA-256 `dfa0dc54d984dcee07ab1aca8ac905c960e6ae8199933ff695c930531cd6b748`; `checkpoint_resume_equal=false`.

This artifact is excluded from the interface native workflow and MUST NOT be registered. It is not an INVALID proof; the verifier did not replay the frontier, and the producer did not exhaust the search.

Expanded replacement run `45593819618` is still executing. Workflow commit is `f8de4b6b14b3840d699d3c47ccc06a71eb5e04ae`; it checks out the unchanged producer source commit `391abf97df3b67661082c907d9ce20b4f69636c2` (solver blob `73da7bea551df73a8676b0adf0401cd7f2d307b5`) and requests 6,000,000 entries, 600 seconds and 13,312 MiB RLIMIT_AS. The expanded workflow itself is blob `1bde518e6e2036a74295f7287e54fc926f404687`. No artifact is available at this checkpoint. If it completes, require EXHAUSTED normal/-O certificates, exact normal/-O and checkpoint/resume byte equality, then Agent #3 latest verifier (commit `d89bab4c005d17c8b27d4c1e6dd291135aca649a`, blob `540a7cf9e7b048684d3ea03def744175ae629b65`) plus exact RGS12 oracle replay before adding small/all to the interface integration workflow.

Updated #2 and #3 coordination comments `7159907331` and `7159908220`. The three-case native interface integration remains fully green; small/all remains an explicit blocker. M2 overall and operational status are INCOMPLETE.


## M15 — Expanded small_choice/all producer artifact published

Core expanded run `45593819618` completed SUCCESS. Its workflow commit is `f8de4b6b14b3840d699d3c47ccc06a71eb5e04ae`; the workflow explicitly checked out the unchanged producer source commit `391abf97df3b67661082c907d9ce20b4f69636c2` (solver blob `73da7bea551df73a8676b0adf0401cd7f2d307b5`, region blob `657c4e0e4059b32cd9e6477e61c7a3673290f36d`). The expanded workflow blob is `1bde518e6e2036a74295f7287e54fc926f404687`.

Artifact:
- Name `p3-m2-small_choice-all-expanded`, artifact ID `15013931205`.
- ZIP size 85,624,447 bytes; ZIP SHA-256 `ebbdf7655c7dd6b8935783c12f3d1f2165c00c88f1afc15a366654f45af9dd11`.
- Certificate size 1,399,367,871 bytes; SHA-256 `9fb5f5bbc1c64e90bc955f73d2325a1d159224e91258e8a8758a34595102e2a7`; Git blob `e2f00717be846336b1f3287a8dd58070272434fd`.
- Raw/journal/trusted-scope bytes are the same exact small_choice inputs already pinned in M13: raw 416 bytes, journal/2 130 bytes, trusted scope 754 bytes.
- Producer normal 188.458 s, optimized 179.590 s; certificate bytes match.
- Core's older pinned verifier normal 251.009 s and optimized 251.348 s; both exit 0.
- One-entry partial checkpoint is 588 bytes and correctly verifies INCOMPLETE/exit 2; resuming it yields the exact same 1,399,367,871-byte EXHAUSTED certificate. `normal_optimized_equal=true`, `checkpoint_resume_equal=true`, `structural_gate=PASS`, `operational_status=INCOMPLETE`.

This resolves the producer exhaustion and resume-equivalence blocker. It does NOT yet establish independent proof: core run used its older verifier pin `e1d022496f98bf50fd57d5ef3a7a0bc8194c817c`. Agent #3 has been asked to replay the exact 1.4GB certificate with current verifier commit `d89bab4c005d17c8b27d4c1e6dd291135aca649a` / blob `540a7cf9e7b048684d3ea03def744175ae629b65`, and to compare all 4,213,597 RGS partitions. No small_choice/all candidate may be registered before that independent result.

The native integration test now streams certificate hashing and passes the artifact file path directly to the verifier, avoiding a 1.4GB parent-process byte buffer. It pins all four exact certificate SHA-256/Git blob identities. All-four interface workflow run `45597292393` is in progress, downloading tiny one/all, small one and expanded small all; its proof subprocess is capped at 2 GiB proof bytes / 5 GiB address space pending Agent #3's memory result. M2 remains INCOMPLETE until Agent #3's proof/RGS result and this all-four interface run both pass.


## M16 — Four-artifact interface replay and exhaustive oracle gate

The first all-four interface attempt `45597292393` used the earlier 4M/240s/5GiB limits and is superseded. The current run is `45597784081`, using the streaming certificate-hash/file-path test, 6,000,001 node/entry caps, 600-second verifier budget, 2 GiB proof-byte cap and 13 GiB address-space limit. It pins:
- producer source commit `391abf97df3b67661082c907d9ce20b4f69636c2`;
- expanded small/all workflow commit `f8de4b6b14b3840d699d3c47ccc06a71eb5e04ae` and workflow blob `1bde518e6e2036a74295f7287e54fc926f404687`;
- verifier commit `d89bab4c005d17c8b27d4c1e6dd291135aca649a` / blob `540a7cf9e7b048684d3ea03def744175ae629b65`;
- RGS oracle blob `da28e66ca4ff74388be79bf9549c8e02f0c60410`;
- core ledger commit/blob `4e21dbf0d06c030681e774cb15f1a5cf0c802f0d` / `092507fc156e604be242e3100117fedc27b96d04`.

All four actual producer artifacts downloaded successfully; exact source-pin checks passed; existing gateway/journal/2 suites passed normal and optimized. The native verify-before-register step is still running. For each all-mode artifact, it now invokes the pinned RGS oracle on the exact raw bytes, requires 203 partitions for tiny_choice and 4,213,597 for small_choice, and compares the complete sorted owner-array set and optimum with the frontier verifier BEFORE registration. The test registers only after both proof checks pass. The all-four run has not yet produced a final result; do not treat it as passed until normal and optimized native steps both succeed and logs are uploaded.


## M17 -- Correction to historical M2 native integration evidence

Direct logs from runs [45597784081](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45597784081/job/139148344348)
and [45599363934](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45599363934/job/139153841846)
show four normal cases and three optimized cases. The optimized P3_CASE_MODES
omitted small_choice:all. Instrumentation in the second run shows 22 normal
registrations (1+4+1+16) and six optimized registrations (1+4+1).
The original M17 claim of all-four optimized coverage was incorrect. These
interface runs did not execute the RGS oracle. Independent proof-only replay
[45627330072](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45627330072)
remains valid. Review 07 classified Gate D as partial on this evidence.

## M18 — M2 native verify-before-register in both Python modes

Two fresh Actions runs passed at `3060be31fe0e38059587b7737e317ebd75b23386`. Each ran normal and `-O` Python 3.13.5 in separate jobs with independent downloads, proof subprocesses and per-case ledgers. Direct job logs show 18 gateway/journal regressions and two native tests passing in each job. Each job verified all four exact certificates and registered **22 candidates**.

| Trigger | Python mode | Job log | Log artifact | Native wall time | Peak RSS (KiB) |
| --- | --- | --- | --- | ---: | ---: |
| Push | Normal | [139278752312](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45635226507/job/139278752312) | [15033037097](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45635226507/artifacts/15033037097) | 6:24.05 | 10,341,024 |
| Push | `-O` | [139278752784](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45635226507/job/139278752784) | [15030974967](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45635226507/artifacts/15030974967) | 5:08.00 | 10,342,868 |
| Dispatch | Normal | [139278940045](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45635276132/job/139278940045) | [15034375180](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45635276132/artifacts/15034375180) | 6:18.88 | 10,341,200 |
| Dispatch | `-O` | [139278940366](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45635276132/job/139278940366) | [15032668670](https://github.com/Mahdi-Jadidi/passive-automata-learning/actions/runs/45635276132/artifacts/15032668670) | 5:32.85 | 10,342,740 |

Every job logged the following per-case results before its `P3_MODE_PASS` marker. All four proof replays returned `VERIFIED`. RGS exhausted the original alphabet, matched the optimum cost, checked membership for one-mode winners and matched the complete all-mode winner sets before registration.

| Case | Search | Proof nodes | Work units | Exact checks | RGS partitions | Optimum cost | RGS optima | Registrations per job |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| tiny_choice | one | 221 | 60,140 | 215 | 203 | 2 | 4 | 1 |
| tiny_choice | all | 461 | 131,556 | 677 | 203 | 2 | 4 | 4 |
| small_choice | one | 1,091,642 | 457,570,571 | 659,914 | 4,213,597 | 4 | 16 | 1 |
| small_choice | all | 5,496,670 | 2,494,969,001 | 4,460,579 | 4,213,597 | 4 | 16 | 16 |

Each job checked the original raw, journal and trusted-scope bytes against the published manifests and rebuilt the trusted scope independently. Its exact source checks covered the gateway, adapter and strict parser at the tested interface revision, plus these pins.

- Producer `391abf97df3b67661082c907d9ce20b4f69636c2`, search blob `73da7bea551df73a8676b0adf0401cd7f2d307b5`, region blob `657c4e0e4059b32cd9e6477e61c7a3673290f36d`. Producer artifacts from run `45592454384` were `15011318454` (tiny one), `15012345186` (tiny all) and `15011812225` (small one).
- Expanded small/all run `45593819618`, artifact `15013931205`, workflow commit `f8de4b6b14b3840d699d3c47ccc06a71eb5e04ae` and blob `1bde518e6e2036a74295f7287e54fc926f404687`. All four exact certificate SHA-256/Git blob pairs are checked by the native test and the manifests are archived with the logs.
- Independent proof commit `d89bab4c005d17c8b27d4c1e6dd291135aca649a`, verifier blob `540a7cf9e7b048684d3ea03def744175ae629b65`, RGS blob `da28e66ca4ff74388be79bf9549c8e02f0c60410`.
- Authoritative ledger commit `4e21dbf0d06c030681e774cb15f1a5cf0c802f0d`, `RegisteredLedger` blob `092507fc156e604be242e3100117fedc27b96d04`.

Validation caps per job were 13,631,488 KiB address space, 600 seconds per proof (630-second subprocess timeout), 4 billion work units, 200 million exact checks, 6,000,001 nodes and entries, and 2 GiB proof bytes. The independent RGS cap was 120 seconds (135-second subprocess timeout), 4,213,597 partitions, 150 million work units and 100,000 entries. These are expanded validation limits.

For each case, `open_gateway` returned the sole authoritative `RegisteredLedger`. Its original journal/2 bytes matched the proof input. Each candidate wrote an ordinary `REGISTER` event with `REQUEST` records and distinct request and attempt identifiers. The offline `UNKNOWN` probe reused an existing request, kept every candidate pending and appended only the ordinary quarantine event with an `UNKNOWN` observation and null feedback. The test checked both exports for absence of proof data. Malformed and unapproved v2 proofs returned `INVALID` with zero gateway calls and zero registrations in both jobs of both runs. Separate local Python 3.13.5 probes in both modes confirmed `INCOMPLETE` for the actual tiny partial checkpoint and a PARTIAL proof with an UNKNOWN root leaf, and `INVALID` for false exhaustion of that leaf. All three probes made zero gateway calls. No live calls occurred. Operational status remains `INCOMPLETE`.

The all-four M2 verify-before-register item in Review 07, assignment #3, is complete at these pins. The input journals for these four certificates were empty. Native verification rooted in a genuine nonempty journal is still pending.

### M3 interface preparation

The M2 job remains pinned to the v1-only verifier and tests rejection of the v2 format at the admission boundary.

## M19 — Review 08 M3 opt-in offline admission

Normal and optimized Python 3.13.5 each passed 21 tests and verified all eight native case/mode combinations before 29 candidate registrations. Both independently completed exact retained checkpoints and matched the fresh and retained resumed bytes. The nonempty fixture reproduced the exact RAW journal via the authoritative ledger, and the independent proof derived its contracted root before registration on that same ledger. The gate preserved UNKNOWN pending and proof-outside-journal semantics. Operational status remains `INCOMPLETE`. [Results and committed transcripts](../research/interface/p2/P3_M3_OFFLINE_RESULTS.md)

The reconciliation audit found no shared changed file paths across the four draft snapshots and recorded their shared contracts, source and evidence dependencies. [Reconciliation plan](../research/interface/p2/P3_DRAFT_RECONCILIATION.md)
