# Review 03 — independent journal/2 sign-off and bounded deletion replay

## Scope and disposition

Read INTEGRATION_REVIEW_03.md at d6daba598ba382f6c213deb12a598d60d3817b00 and latest issue #10 coordination. Target core 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d, journal selector-v2-journal/2 with inner selector-v2/1. Interface gateway e2f97c4817db13e3ae7ab4dcbb938ab24be3ef8f, export 18d0fab785236dfec1b23e9e0896f48e9961f039, plaintext checkpoint 0eb1050ad103bad2f93d3b9feb732bf94184f2a2. Proof starting head ed20d9b12ea9730e07e7d2d1e0581744a266eb02. Independent proof-stream narrow item 2 PASS for pinned artifacts and tested mutations; combined gate owner #2 must run pinned latest cross-stream boundary. No automatic P3 authorization, no merge, no learner or baseline changes, no external calls or operational acceptance. No new journal schema.

DNS blocked git ls-remote; GitHub connector fetch_file and fetch_blob cannot decode gzip (UnicodeDecodeError). Instead execute actual byte-verified producer modules; reconstructed core roundtrip/adversarial test call sequences using producer public APIs and independently calculated proof fields, then gzip -n -6. Both decompressed SHA256 and *compressed Git blob SHA1* match published exact artifacts, including reported proof bytes. No producer audit_journal.py import. The actual interface exporter was restored verbatim with test_gateway_v2.py and executed normally/-O; both published gzip blob identities and SHA256 matched. Interface later added plaintext artifacts (fetched connector SHA and byte length match local actual exported plaintext). Therefore replay is of byte-identical published artifacts, not substitute fixtures. This is byte-verified reproduction, not network-enabled clean CI.

## Independent API and checks

tests/reference/journal_v2_replay.py: replay_journal(raw,scope,canonical_journal_bytes,expected_records=None,deletion_budget=None) returns {records,proof,attempt_status,pending_candidates,quarantine}; throws InvalidProof or parsing errors for malformed evidence, ReplayIncomplete/MemoryError for limits. Defaults to bounded deletion enumeration. verify_journal(...) maps to {status: VERIFIED/INVALID/INCOMPLETE, result only on VERIFIED, operational_status: INCOMPLETE}. VERIFIED means all supplied evidence checked, not necessarily closed search; gate must additionally require proof.closure_state FIXPOINT or LABEL_CONFLICT as core assess_replay does. PARTIAL/OPEN can contain valid necessary facts, never exhaustion authority. Default byte cap 64 MiB for verify_journal. No hard RSS/wall-time guarantee for entire parsing/replay. No producer/adapter/audit_journal imports in independent kernels. Driver imports actual producer public APIs only.

Reconstruct exact order and schema of RAW, REGISTER, OBSERVE, QUARANTINE; forbid raw request/observation bypass; recompute sample/request/capacity identity, original per-label bijection, origin and retry registration; global attempt uniqueness within journal; canonical normalized wrapper plus exact original wire bytes and their distinct digests; exact inner projection from actual payload; complete named/anonymous/free tables and DFA simulation independently; external receipt token digest and uniqueness, simulator null receipt; no-response diagnostic digest; UNKNOWN closes only correctly matched pending attempt; wrong/late receipt zero semantic records. Compare all projected records to artifact's ordered records, check structural facts and all EXHAUSTED deletion obligations. Candidate IDs remain pending even for mock ACCEPT or opaque bounded NO. No inference of real authentication from internally coherent journal; a fully forged coherent journal cannot be ruled out without external trust. Quarantine reason text is diagnostic, not proof of transport failure.

## Reproduction

Python 3.13.5. From proof branch tests/reference, CORE_DIR=core worktree implementation/partition_feedback_final, INTERFACE_DIR=interface worktree research/interface/p2. Pin sources at revisions above; drivers verify exact Git blobs before execution. No producer source modification. Use existing published gzip files from respective worktrees, or reconstruct if binary retrieval blocked:
```sh
python audit_journal_v2.py "$CORE_DIR" "$INTERFACE_DIR" /tmp/core-j2
python -O audit_journal_v2.py "$CORE_DIR" "$INTERFACE_DIR" /tmp/core-j2-opt
for f in /tmp/core-j2/{roundtrip,adversarial}-v2.json; do gzip -n -6 -c "$f" > "$f.gz"; done
PYTHONPATH="$CORE_DIR" python "$INTERFACE_DIR/export_journal2.py" /tmp/interface-j2
PYTHONPATH="$CORE_DIR" python -O "$INTERFACE_DIR/export_journal2.py" /tmp/interface-j2-opt
diff -r /tmp/interface-j2 /tmp/interface-j2-opt
python replay_published_j2.py /tmp/core-j2 /tmp/interface-j2
python -O replay_published_j2.py /tmp/core-j2 /tmp/interface-j2
python audit_interface_j2.py "$CORE_DIR" "$INTERFACE_DIR" /tmp/delegated-j2
python -O audit_interface_j2.py "$CORE_DIR" "$INTERFACE_DIR" /tmp/delegated-j2-opt
python -m unittest -q test_bounded_deletion test_independent_replay test_production_replay test_ledger_replay
python -O -m unittest -q test_bounded_deletion test_independent_replay test_production_replay test_ledger_replay
(cd "$INTERFACE_DIR" && PYTHONPATH="$CORE_DIR" python -m unittest -q test_gateway_v2 && PYTHONPATH="$CORE_DIR" python -O -m unittest -q test_gateway_v2)
```
Core source hashes verified: core.py 997304c3adce9d3148d454b079639575f419ba0e; schema.py 65a7522a8442a184c14f7a0fa74fc307ce60229f; sparse_analysis.py f773cc1c6b1a852193ba2afb75aa2fce4941a5c2; component_closure.py 97844bc266556cc04cd54a75c0d57dc00d6709ea; evidence_store.py 42e38c8ee590267b292ebc0d678e9d4f3a56849b; registered_ledger.py 092507fc156e604be242e3100117fedc27b96d04. Interface adapter.py c38e441c7327a44adad8a0fe1125d45c93e8ef69; strict_ledger.py a66975de137e3ec556b8c7aacd108cf975c46344; gateway.py 8b314e11c0d935122779365b08666c482697621f; test_adapter.py bfa7dee3373da7d267c373e238b95d271a8a2669; export_journal2.py 1d3a16f03171f2259427ecda8de94282ffda8cae; test_gateway_v2.py 502b7c40f7776fc3bab087303e457fae149587c3.

## Actual results

All four published artifacts independently verified, normal/-O identical output. Each raw structural optimum cost is unrestricted, not operational.

| Artifact | JSON bytes | gzip Git blob | JSON SHA256 | Events / records | Structural cost |
|---|---:|---|---|---:|---:|
| roundtrip-v2.json.gz | 34313 | eedb6c2fb7ad29346f91230dfc7db1df46eff716 | 14f0dc4cb606ca7f1b20a5cd575a937dd6471da594d983d86254e210573e5ab8 | 9 / 12 | 2 |
| adversarial-v2.json.gz | 32962 | 1f1444631ba3e1b12f95ae8ba4e362f93d5b8246 | 1b78c4aefe974db58409cb186528af75b1981752ba0a3778634fe3bcb406e97c | 12 / 13 | 2 |
| interface-journal2.json.gz | 41798 | a61d493991c7464641c6d182929ba8c185f57421 | caf40422d9d3e6d0cd8257da4b757cacd71cda1e6db089493421c912515edf94 | 18 / 18 | 1 |
| interface-journal2-epochs.json.gz | 3400 | 6efdc4356b79e4368e17c59b6376d50861762c12 | adabd0b274ebaa2ce55aab7f874f6485664399d4b0df59b013d158cfb2338491 | 1 / 4 | 2 |

Core adverse statuses a UNKNOWN, b PROJECTION_NO, c BOUNDED_NO, d ACCEPT, e PENDING, 3 quarantines; interface a UNKNOWN, b PROJECTION_NO, c BOUNDED_NO, d/e ACCEPT, f/g UNKNOWN, h PENDING, 5 quarantines. All registered request IDs remain pending candidate targets. Raw closure FIXPOINT independently proved; no bounded feasibility or operational acceptance. Bounded deletion telemetry core 370 work, peak 6 index entries, 18 exact checks each; interface 150/4/8, epochs 186/5/8. These are small synthetic service response fixtures actually processed by producer, not real service calls.

Actual audit_journal_v2.py output (both modes):
```text
roundtrip events= 9 records= 12 optimum= 2 operational= INCOMPLETE
adversarial events= 12 records= 13 quarantine= 3 states= {'a': 'UNKNOWN', 'b': 'PROJECTION_NO', 'c': 'BOUNDED_NO', 'd': 'ACCEPT', 'e': 'PENDING'} operational= INCOMPLETE
roundtrip-v2.json 34313 14f0dc4cb606ca7f1b20a5cd575a937dd6471da594d983d86254e210573e5ab8 published_digest_match= True
adversarial-v2.json 32962 1b78c4aefe974db58409cb186528af75b1981752ba0a3778634fe3bcb406e97c published_digest_match= True
outer_mutants_rejected= 24 resource_censored= 4
actual_atomic_rollback=PASS global_reuse=REJECTED wrong_attempt=PENDING unknown_retry=PASS receipt_reuse=UNKNOWN false_exhaustion=INVALID concurrent_registrations=1/16
```

Published interface mutations: 7 additional malformed exports rejected (bool ID, retry origin rebound, omitted anonymous zero, erased UNKNOWN control record, wrong attempt quarantine, receipt mismatch, DFA bool state with recomputed hashes). 31 counted outer corruptions across core and interface (not distinct categories). Independent additional driver audit_interface_j2.py executed actual gateway; 22 events, 22 records, 7 quarantines, 10 attempts, cost 1, operational INCOMPLETE. Output delegated-journal-v2.json 51223 bytes SHA256 ae396f40b98a6aa6c6ed53b05e20da680dbac05f8dfa0b2af684b512bfbe3b8e identical normal/-O. HMAC allowlist fixture valid exact-byte receipt; reuse, whitespace alteration, wrong map, unsigned responses UNKNOWN. Actual delegated interface test_gateway_v2: 8/8 normal 0.031s and 8/8 optimized 0.026s. No claim of production authentication.

## Resource-bounded exact deletion enumeration

bounded_deletion.py: a deterministic polynomial fingerprint of each original word and its deletion projections is a filter, never an equality proof. For each touched group accumulate maximal retained intervals using polynomial concatenation. Maintain one global rolling prefix, previous prefix at last deleted position, accumulated retained hash and deletion count per group; one array of powers up to maximum word length. The hash and length for an erased word are identical for equal original ordered projections, hence filter cannot discard a true equality. Full/erased positive fingerprints bucketed with original positive ID and group (or sentinel for full); enumerate negative touched-group deletions against full or same-group positives, and negative full against positive-only deleted groups. Exact tuple equality after erase on *every candidate hit*, only two transient remainders, no stored remainder tuple index. If neither trace touches group then deletion equality implies full cross-label duplicate, preflight rejects EXHAUSTED in that case. Count and check all keys against actual claimed keys (no second set of expected keys), no collision-based acceptance. This uses linear auxiliary entries in max trace length and touched positive group occurrences, plus original sample/claim storage and transient literal checks, not quadratic remainder storage. Work can still be large or adversarial collision buckets can be large. Work/deadline/index-entry/word-length caps throw ReplayIncomplete; no verified proof returned on cap or memory error. Caps cooperative, not hard bytes/wall time for the full pipeline. Actual producer facts and structural witness checks still have their own cost. Legacy exact tuple index remains for comparison in v1 tests; journal/2 uses bounded path by default.

Actual final test run: 17/17 normal 0.736s; 17/17 -O 0.708s. 4374 corpus-owner cases, 13122 fingerprint checks at 0/2/64 bits, all pass; zero-bit forces collisions. 20,000-symbol synthetic diverse trace, 20,001 index entries, two exact candidate checks, work 240012. Missing/extra facts and duplicate conflict rejected; work/index/length/deadline caps tested. Same old 2187 corpora/4374 checks and 126 prior counted corruptions rerun (not new distinct corpus domain). Benchmark #4 informed via issue #10 comment 7145032831 and requested real huge_choice_active/huge_long_active at stated caps. Actual large recovered cases are benchmark-stream pending as of this proof checkpoint; synthetic long word is not a recovered archive run.

## Milestones and limitations

0f7140f bounded deletion; 315ab38 and b6448d4 optional budget wiring; ba3c5eb tests; b550ca8 independent journal/2; 8f20b39 actual core regeneration+mutations; d1aeede delegated actual gateway; 5f16a50 bounded default/cause classification, bd9677f final deadline check; 8724980 published artifact verifier; 8376243 actual interface mutation suite. Exact final local source blobs matched remote: bounded_deletion.py 64eda7d13b3153175f09b70e41be66e1615846b2; production_replay.py 4666c3f1aca6189331a83ff2f00de0e376e2a710; ledger_replay.py 0b615b6c17258e621d73147baa262d791985d8d0; test_bounded_deletion.py 2f59257d0ff3396417c2cedf9845f61e2fd20928; journal_v2_replay.py 6c49013e809b5ac4d2b2a37850e6e6cece513072; audit_journal_v2.py 7fc40c4f99ee13bbbb8b219c77bdd9e0927df512; audit_interface_j2.py 32dec464d89470022c81ee9926ee94b9a8263acf; replay_published_j2.py d32d3bed22dc06a0d51ff7965c7f621950b16455.

Independent narrow proof requirement passes for these actual frozen artifacts; do not treat metadata-only producer exhaustion as proof, use independently replayed verified closed result. Combined runner against latest interface/proof head and core owner gate decision remain #2 responsibility; benchmark scale runs separate parallel work, not arbitrary added structural gate. Real transport, authenticated receipt provenance outside journal, durable crash recovery, approved bounded policy, resource caps for other proof phases, clean network CI and P3 coverage remain separate. Work confined to existing proof branch and draft PR #8. No merge or external learner modification.


## Follow-up — core combined gate and bounded-index hardening (2026-11-25)

### Combined P2.1 decision

After the independent proof sign-off, core owner published checkpoint `c5e7e170add6f92e129099bf7444f5fd7a29eb3a` and updated PR #7. I independently inspected `REVIEW03_FINAL.md`, `final-gate.json`, `run_final_gate.py` and `test_final_gate.py`, and confirmed the runner pins the intended core/interface/proof source identities. The report records actual final-run exit 0: 40/40 normal, 28/28 optimized, all four exact artifacts VERIFIED at structural costs 2/2/1/2, 31 independent outer mutations INVALID, five caps INCOMPLETE/no result, actual PARTIAL closure INCOMPLETE, false EXHAUSTED INVALID, operational status INCOMPLETE, elapsed 23.04 s, peak RSS 219272 KiB. The four artifact hashes and closure states in final-gate.json match this proof stream's earlier independent result. This closes the specified structural P2.1 gate at that exact executable proof pin. It does not confer operational acceptance, real external authentication, durability, or scale acceptance.

### Bounded deletion implementation hardening

A code review of the proof checker found two avoidable memory-accounting weaknesses in the earlier implementation: auxiliary `seen` and `full_words` sets duplicated trace keys outside the index-entry budget, and exact candidate comparisons materialized two temporary remainder tuples. The proof branch now removes both sets and all remainder tuple allocations:

- Positive deduplication uses the full-word fingerprint bucket followed by exact streaming equality; duplicates are not stored twice.
- `entries` counts every persistent full-word and per-group index reference for unique positive traces.
- Exact collision resolution uses `zip_longest` over ordered retained-symbol generators, with periodic deadline checks. Fingerprints remain filters only.
- Powers use a bounded `array('Q')`; per-trace signature state is bounded by the configured maximum word length. This is an enumeration-memory improvement, not a hard RSS guarantee for the whole replay pipeline.

Exact updated source blobs: `bounded_deletion.py` e1fc61b6f03484d4428642ca157e2dac43f0572d; `test_bounded_deletion.py` 6de549b9b4d208be99a419c88fd903a1ce1a6dcc. These exact files were materialized into a local isolated Python test directory; `git hash-object` reproduced both Git blob IDs before execution. The actual committed test module ran 6/6 normal (0.422 s) and 6/6 optimized (0.362 s), Python 3.13.5. Results: 4,374 exhaustive corpus/owner cases, 13,122 checks at 0/2/64-bit fingerprints, 500 seeded randomized collision/conflict cases, 1,000 repeated positive traces deduplicated under a two-entry cap, all four budget types, missing/extra facts and cross-label duplicates rejected. The 20,000-symbol diverse synthetic case used 20,001 index entries, two exact checks and 200,010 work units. This does not substitute for a recovered planted benchmark.

This follow-up changes the independent proof implementation and test source pins after the prior combined gate. Core's `run_final_gate.py` currently pins the earlier proof blobs (bounded_deletion.py 64eda7d... and test_bounded_deletion.py 2f59257...). Core owner #2 must update those two expected hashes and rerun the combined gate before this hardened proof revision is treated as part of the final combined executable pin. The prior combined gate remains valid for its recorded earlier pin.

### Actual large-input benchmark status and coordination

Inspected benchmark commit `678027476d912a5a753b03c67dc6204466f82c6b` and `results/review03-replay-only.csv`:

| Case | CSV mode | Cap | Result |
|---|---|---:|---|
| huge_choice_active | filter | 512 MiB / 30 s | MEMORY_ERROR |
| huge_choice_active | literal | 1536 MiB / 30 s | MEMORY_ERROR |
| huge_long_active | filter | 512 MiB / 30 s | MEMORY_ERROR |
| huge_long_active | literal | 1536 MiB / 30 s | VERIFIED_RAW_ONLY, floor/optimum 10,000, replay 2.216 s |

Separately, benchmark agent #4's PR #8 comment 7145073442 reported a benchmark-only signature-filter raw replay at 1536 MiB / 30 s: huge_choice_active complete replay 2.161 s, RSS 241340 KiB, mandatory floor 1 only; huge_long_active 2.639 s, RSS 245168 KiB, structural optimum 10,000. These results use the benchmark agent's prototype and the old v1 proof kernel; they are not execution of this exact proof-branch bounded_deletion module or full outer /2 verifier. The CSV's filter rows are at 512 MiB, so the apparent mode/cap discrepancy must be reconciled with exact source and run identity.

Requested agent #4 to run this exact proof module through `journal_v2_replay.verify_journal` / `replay_journal` on both recovered cases at matched 30 s / 1536 MiB caps, normal/-O, separating raw closure from full outer /2 replay, and recording input hashes, source blob IDs, telemetry, RSS and time. Coordination comments 7145339368 (#10) and 7145340155 (#9). Until those runs exist, no large recovered-case success is claimed. A resource cap or MemoryError must remain INCOMPLETE, never a verified lower bound or optimum.

### Current disposition

- Narrow P2.1 structural gate: PASS at core checkpoint c5e7e17 and proof executable pin 8376243 / sign-off e8895a3.
- Hardened bounded deletion checker: local exact-blob tests PASS; combined gate re-pin/rerun pending.
- Actual recovered huge-choice/huge-long replay using this exact hardened verifier: pending benchmark agent.
- Operational status: INCOMPLETE. No P3 implementation, merge, learner edit, baseline edit, external call, or operational acceptance.


### Benchmark agent's official full outer /2 replay (pin e8895a3)

Benchmark branch subsequently published commit 52d21e672b0ae6420cf677ff09c01bb2a3fd6b05 and benchmarks/v2/REVIEW03.md. Its review03/replay_only.py is a benchmark-only prototype and its review03/final_replay.py independently invokes the official journal_v2_replay.verify_journal with an address-space limit and checks exact source Git blob IDs. The official replay pins proof sign-off e8895a3 and the earlier bounded_deletion blob 64eda7d13b3153175f09b70e41be66e1615846b2, not the later hardening blob e1fc61b6.

Exact official full outer /2 measurements from results/review03-final-replay.csv (30 s deadline; work 200,000,000; index references 2,000,000; word length 2,000,000):

| Case | Address-space cap | Status | Elapsed | RSS | Work | Index refs | Exact checks | Floor | Optimum |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| huge_choice_active | 512 MiB | INCOMPLETE (MemoryError) | 0.965 s | 203,228 KiB | 0 | 0 | 0 | — | — |
| huge_choice_active | 1536 MiB | VERIFIED | 1.794 s | 245,428 KiB | 2,006,999 | 111,999 | 20,999 | 1 | — |
| huge_long_active | 512 MiB | INCOMPLETE (MemoryError) | 0.812 s | 200,620 KiB | 0 | 0 | 0 | — | — |
| huge_long_active | 1536 MiB | VERIFIED | 2.391 s | 261,336 KiB | 2,400,024 | 110,000 | 30,000 | 10,000 | 10,000 |

These are full outer /2 verifier results on the original raw journal/2 exports, not just raw closure. The 512 MiB failures occur before deletion work and expose no result. huge_choice_active verifies a mandatory floor of 1 only; do not label it optimal. huge_long_active independently verifies structural optimum 10,000. Operational status remains INCOMPLETE. The same report records the distinct raw-only filter experiment and literal controls; their phase timing boundaries differ and are not interchangeable.

This resolves the earlier CSV discrepancy: review03-replay-only.csv contains the literal control and 512 MiB prototype-filter rows, while the official bounded full-replay measurements are in review03-final-replay.csv. The official full replay used old checker pin e8895a3. Benchmark #4 was asked to rerun both cases with the new hardening blob e1fc61b6 and updated test blob 6de549b9, with normal/-O and separate raw/full phase telemetry; until then, the improved checker itself has only synthetic tests, not recovered-input execution.
