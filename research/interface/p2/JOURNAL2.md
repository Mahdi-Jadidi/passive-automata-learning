# Review 03 — authoritative interface journal/2

Authority: INTEGRATION_REVIEW_03.md at d6daba598ba382f6c213deb12a598d60d3817b00, issue #10 latest core-owner comment 7144997981. Core pinned 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d. Coordination posted to #7 (7145006171), #8 (7145006821), #10 (7145007486).

Use gateway.open_gateway(raw, authenticate=hook) for the production-shaped normalized interface. Returns the exact core RegisteredLedger instance with selector-v2-journal/2 version guard. No wrapper, persistent EvidenceLedger, second attempt registry, observation list, receipt set or artifact sidecar. Adapter request/map/validate and strict parser are pure dependencies; old adapter.Ledger, strict_ledger.RegisteredLedger and shared_gateway.SharedGateway remain historical reference paths, not production entry points. No changes to core schema or learner. Existing historical tests remain reproducible.

Core API: register(owner,request_id,attempt_id,...), ingest(request_id,attempt_id,normalized_input_bytes), original_id(request_id,attempt_id,label,wire_id), attempt_status(request_id,attempt_id), append_raw(records), journal, records, pending_candidates, export(), export_records(). Do not trust echoed IDs, and normalize wire IDs before ingest using registered maps. Auth hook receives canonical request bytes, exact normalized input bytes (including whitespace), canonical registration metadata; test hook is not operational authentication. Version /2 hashes exact input bytes for response_digest, hashes UTF-8 external receipt token for receipt_ref, uses NO_RESPONSE_DIGEST for absent bytes. Simulator receipt has no core receipt digest. UNKNOWN closes only correctly matched pending attempt; wrong request/late/unsolicited responses cannot close another or append another observation. Retry same request target and provenance, new global attempt ID within journal. All candidates remain unresolved at this layer, even mock ACCEPT and opaque bounded NO. Core producer exhaustion metadata is not independently verified; no pruning based on it.

## Actual test execution

Python 3.13.5. DNS prevented clean checkout (git ls-remote failed Could not resolve host github.com); exact core sources reconstructed/verified by Git blob hash, no vendoring. Core files: core.py 997304c3adce9d3148d454b079639575f419ba0e; schema.py 65a7522a8442a184c14f7a0fa74fc307ce60229f; sparse_analysis.py f773cc1c6b1a852193ba2afb75aa2fce4941a5c2; component_closure.py 97844bc266556cc04cd54a75c0d57dc00d6709ea; evidence_store.py 42e38c8ee590267b292ebc0d678e9d4f3a56849b; registered_ledger.py 092507fc156e604be242e3100117fedc27b96d04. Interface adapter.py c38e441c7327a44adad8a0fe1125d45c93e8ef69 and strict_ledger.py a66975de137e3ec556b8c7aacd108cf975c46344 unchanged. New tested code/logs verified exact Git blob identity.

Reproduce in network-enabled checkout, no branch merge:
```sh
git worktree add --detach /tmp/core-j2 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d
cd research/interface/p2
export PYTHONPATH=/tmp/core-j2/implementation/partition_feedback_final
python -m unittest -v test_adapter test_strict_ledger test_shared_gateway test_gateway_v2
python -O -m unittest -v test_gateway_v2
```
Actual 27/27 tests normal (0.066s), including 8 new delegation tests; optimized 8/8 (0.032s). Exact logs results_journal2.txt and results_journal2_opt.txt. Tests exercise type identity/no alternate state, /1 rejection, immutable snapshots, literal table conversion, raw bypass and batch rollback, duplicate JSON keys/float/NaN/UTF-8, global attempt reuse and concurrent registration/delivery (16 each: one successful), timeout/retry/wrong request/late receipt, tampered receipt and provenance, bound mismatch, malformed DFA, unavailable/auth reentry. Test-only HMAC allowlist checks exact bytes and registration. No external calls or operational ACCEPT. Journal/2 independent replay, final combined gate and clean CI still pending. Memory-only, quadratic full-history replay, no real transport or capacity policy approval.

## M8 — actual delegated journal/2 interchange

Run with the pinned core PYTHONPATH above:
```sh
python export_journal2.py generated_j2
python -O export_journal2.py generated_j2_opt
diff -r generated_j2 generated_j2_opt
for f in generated_j2/*.json.gz; do gzip -dc "$f" | sha256sum; done
```
Normal and optimized runs produced byte-identical JSON and deterministic gzip (mtime=0). Each artifact contains {raw,scope,journal,records}; records are the exact ordered projection of the journal, not a second authority. Neither artifact includes a proof result; independent proof stream must calculate it. All observations are simulated or test-HMAC external fixtures, not live receipts.

| File | Uncompressed bytes | Events / inner records | Uncompressed SHA-256 | Git gzip blob |
|---|---:|---:|---|---|
| interface-journal2.json.gz | 41798 | 18 / 18 | caf40422d9d3e6d0cd8257da4b757cacd71cda1e6db089493421c912515edf94 | a61d493991c7464641c6d182929ba8c185f57421 |
| interface-journal2-epochs.json.gz | 3400 | 1 / 4 | adabd0b274ebaa2ce55aab7f874f6485664399d4b0df59b013d158cfb2338491 | 6efdc4356b79e4368e17c59b6376d50861762c12 |

First case: Unicode, duplicate negatives, epsilon, unused symbol, actual closure and structural record, eight registrations, four accepted observations (projection NO, bounded NO, simulator ACCEPT, test-auth external ACCEPT), three UNKNOWN closures (timeout, receipt reuse, whitespace tamper), two no-record quarantines (wrong request, late response), one pending attempt. Second: actual multi-epoch contraction and structural record, no observations. Independent replay should verify exact wire/normalized bytes, literal table/DFA conversion, receipt references and original ID maps, pending lifecycle, mandatory owner/exhaustion, rejection of mutations with recomputed digests. No external authority is provided.

Source export_journal2.py blob 1d3a16f03171f2259427ecda8de94282ffda8cae and actual results_export_journal2.txt cb22bed778d85e57d1092706ebc2f576dc860614 match local bytes. Both committed gzip Git blobs match local generated bytes. Gzip SHA-256 and complete event sequences in the results log. No independent verifier invoked in this milestone; proof agent is the separate authority. No P3, merge, deployment or operational acceptance.
