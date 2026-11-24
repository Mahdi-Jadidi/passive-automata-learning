# Core stream checkpoint 1 (issue #2)

Status: local P1 foundation tested; schema proposed for review, not frozen. No external calls or learner modifications.

Read PROJECT_HANDOFF, SELECTOR_V2_INDEX and the research reports on integration head 4a2f3d6ce0b4b974430f02d79b1a98f2c8fc9e4b (R01 implementation sections in detail; R02–R04 interface and design cross-check). Branch starting point c0aae9fb222aef9dfea4c13cb44e5a37f0d86f8a. Legacy code unchanged.

## Proposed shared schema (for proof/interface streams)

- Sample.from_input accepts exactly alphabet, positive, negative arrays, matching legacy sample.py. Declared alphabet order defines original token IDs; positive and negative IDs are separate zero-based original positions. Ordered immutable tuples retain repetitions and duplicate IDs. sample_digest = SHA-256 of compact UTF-8 JSON array ["sample-v2",alphabet,positive_encoded,negative_encoded], in declaration and original trace order (ensure_ascii=True).
- PartitionRef.owner is a complete tuple mapping every original ID to its block's minimum original ID. Canonical identity is (sample_digest, owner); cost = number of nonrepresentatives. blocks() materializes full sorted blocks only on demand. SymbolDSU is union-by-size with path compression, NOT the rollback branch DSU.
- DeletionResult carries sample_digest, frozen owner_snapshot, DeletionFact(negative,group,positive), exhausted, diagnostic cursor (phase,index), optional label_conflict (negative,positive). An exact same-label positive representative is used, but original IDs never renumbered. Group IDs reference the frozen snapshot; retain original tokens when erasing. Exact opposite-label conflict is a separate outcome, not an exhausted join.
- ForcedEdge(negative,a,positive_a,b,positive_b) is a singleton-only forest certificate. Verify IDs and two literal erasures for the SAME negative, then connect endpoints. Count successful unions independently; derive owner from graph connectivity. No dependence on hash, budget completeness, or producer metadata. singleton_forest rechecks facts locally; independent hardened verifier is issue #3.
- StructuralResult(compatible,separating_groups,failed_negative) is mathematical evidence ONLY; no external ACCEPT or normalized external verdict. On success separating_groups follows original negative order; failure gives first failed negative. Empty alphabet and empty classes are handled explicitly.

## Validation

From implementation/partition_feedback_final:
    python -m compileall -q selector_v2
    /usr/bin/time -f 'elapsed=%e maxrss_kib=%M' python -m unittest discover -s selector_v2/tests -v

Actual local run: 6 tests OK, unittest 1.197 s, process elapsed 2.34 s, maximum RSS 168592 KiB (includes tracemalloc overhead). 40 ordered words of length <=3, 1560 distinct ordered cross-label pairs x 2 snapshots, zero-bit fingerprints, literal obligation and compatibility equality. Seed 921: 250 random corpora, all five 3-symbol partitions checked, mandatory edges hold for every compatible partition. 45 work caps plus zero-second timeout, invalid fact rejected, repeated tokens, empty/absent groups, duplicates and original IDs tested. Synthetic 100k declared symbols / 2000 total traces: 1000 forced unions, compatible raw root, peak traced Python allocations 23889403 bytes. No planted reference data supplied to selector. Not a controlled benchmark or external test.

Local tested file git blob hashes:
core.py 997304c3adce9d3148d454b079639575f419ba0e
sparse_analysis.py f58889e4e94b680408abdcbba8a5f11aa9262975
tests/test_sparse_analysis.py 903d107155de92547c5903576cebf9c55a430b1a

## Limits and next gate

Expected linear input indexing and sparse projection checking; join complexity includes inspected collision buckets, literal replay and output size. No alphabet-wide masks or broad pair scan. Python tuples/lists rather than packed arrays; digest currently serializes entire sample. Budget is cooperative, per word/candidate; not a hard resource cap. Interrupted facts are sound, cursor diagnostic only; restart pass with fresh budget, not persistent resume. Raw check is unbudgeted. Quotient deletion joins supported but only singleton forest replay implemented; automatic component closure deferred. Production independent verifier, full 100k/20k archived cases, wire protocol and receipts not available here. Next: review shared schema with issue #3/#5, add independent proof replay, then address resumable indexing and larger benchmark harness. No deployment, structural general-optimum, or external acceptance claim.

## Checkpoint 2 — component fact replay and scale extension

Previous checkpoint: 5e6bec593263beca282d7aa0201f4a8f42e4fb7c; draft PR #7.

Added replay_deletion_facts(sample,result) to validate the sample digest, frozen owner snapshot, canonical group IDs, original trace IDs, literal deletion equalities, and exact duplicate-label conflict witness. It does not assert exhaustiveness or mandatory status of arbitrary component groups. Singleton forest now calls this helper. Added corruption/scope tests and two synthetic 100k-symbol / 20k-trace fixtures (length 2 and length 10 with repeated shared context). Each discovered 10000 singleton forced unions, 90000 blocks, raw compatibility, and test-only literal replay of all 20000 deletion witnesses. These are synthetic inputs, not the archived nine benchmark cases or a live service.

Same unittest command as checkpoint 1: 7 tests OK, 9.918 s; process elapsed 10.92 s, max RSS 216512 KiB (includes tracemalloc). Traced peaks 29333203 and 42753347 bytes respectively. No legacy modifications. Tested blob hashes: sparse_analysis.py f773cc1c6b1a852193ba2afb75aa2fce4941a5c2; tests/test_sparse_analysis.py 965abe7e10fecf35b441fefa844aebf75e549646. Core unchanged.

Remaining limitations unchanged: restart-only budget cursor; no persistent continuation, no component-contraction closure driver, no independent production proof kernel (issue #3), no archived benchmark replay, no external acceptance, schema review pending.

## Checkpoint 3 — P2 schema and component epochs (issue #10)

Integration review read at 26d1dc39d04188737677f35d82d91ae0f8af99c6. Schema proposal posted to #6, #8 and #10; review pending. New selector_v2/schema.py and component_closure.py, tests/test_schema_closure.py. Version selector-v2/1, canonical JSON sorted keys, ensure_ascii=True, compact separators, UTF-8. Sample digest unchanged; request rejects empty alphabet; raw extension permits it. Scope ALL_PARTITIONS only; bounded scope requires capacity digest, not a bounded optimizer. Request IDs, attempt IDs, exact negative order and canonical owner validated. Unicode/duplicate/epsilon sample digest 7ddb11d457a25ee2b1d273529cf3f3e2064054dc154ebc901acb796b08708bbb; request digest 1f43bbcd2081c20e84469b2220928c7a5f61674ce9a7d4bfec84e7e55285ee72 (golden test). Component epoch envelope RAW/COMPONENT_EPOCH includes frozen owner, epoch, facts, same-negative edges, result_owner, EXHAUSTED/PARTIAL, cursor. Final outcome FIXPOINT/PARTIAL/LABEL_CONFLICT. Raw STRUCTURAL_CHECK and LABEL_CONFLICT records distinct from external verdicts.

Commands from module root: python -m compileall -q selector_v2; /usr/bin/time -f 'elapsed=%e maxrss_kib=%M' python -m unittest discover -s selector_v2/tests -v. Actual 10 tests OK, unittest 10.120 s, elapsed 11.26 s, max RSS 216588 KiB; 156 distinct tiny word pairs x five partitions (compatible completions checked), 100 interruption caps, multi-epoch targeted fixture, strict schema mutations; existing scale cases rerun (29235923 / 42752483 traced bytes). Local files matched remote predecessor blob hashes; no network checkout (DNS failure). New tested blobs: 65a7522a8442a184c14f7a0fa74fc307ce60229f, 97844bc266556cc04cd54a75c0d57dc00d6709ea, ad959bcd10615d951f4207a7b0e0cf8098c753db. No independent verifier yet; epoch exhaustion metadata is producer-reported, not independently certified. Repeated full joins and full owner snapshots may be expensive; restart-only cursor, cooperative budget, no persistence. No external calls; P3 blocked. Next typed ledger and atomic intake.
