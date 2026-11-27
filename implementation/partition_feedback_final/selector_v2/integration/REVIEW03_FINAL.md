# Review 03 — P2.1 final structural integration gate (checkpoint 9)

Decision: narrow structural research gate VERIFIED (review 03 items 1–3), operational status INCOMPLETE. No external calls, P3 implementation, merge, or schema revision. The authoritative format remains selector-v2-journal/2 over selector-v2/1. All other operational and scale gates remain separate.

## Exact pinned inputs

- Core tested predecessor 796a83a5f8f69c4dc7c0db619e1cdb130ddc0b33; authoritative RegisteredLedger implementation unchanged from 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d.
- Interface 0eb1050ad103bad2f93d3b9feb732bf94184f2a2, actual open_gateway delegation, exports and plaintext.
- Independent proof executed 83762437ba05e1def9dde5edff8c7d44878f4269. Independent proof-stream sign-off at e8895a344821f7cd463823774e6bc591e064264c (issue #10 comment 7145173732). GitHub compare shows only research/audit/PROGRESS.md and research/audit/REVIEW03_JOURNAL2.md changed from executed proof pin to sign-off head; all executable sources identical.
- Benchmark branch progresses independently; not a dependency of this narrow gate, not executed in this run.

Review 03 read at d6daba598ba382f6c213deb12a598d60d3817b00. Interface coordination and publication comments 7145098088 and 7145121210, proof independent sign-off 7145173732. All consumed sources checked against exact Git blob IDs in runner before execution. No vendoring or changes to other agent paths. DNS still blocks direct git checkout; tested byte-verified snapshots, not CI.

## Actual reproduction

Python 3.13.5. From implementation/partition_feedback_final, place the interface research/interface/p2 and proof tests/reference source snapshots at the pinned heads in separate directories; use the two committed core gzip files in selector_v2/integration (or their exact blob-matched copies). The new runner itself and new tests are in this checkpoint. Commands used on local byte-verified snapshots:

    /usr/bin/time -f 'elapsed=%e maxrss_kib=%M' env PYTHONPATH=. python -m selector_v2.integration.run_final_gate --interface-dir pinned/interface-review03 --proof-dir pinned/proof-review03 --core-artifacts . --output-dir final-gate-run3

For actual worktrees, substitute their absolute directories and --core-artifacts selector_v2/integration. Fresh output directory required. Child commands use exact dependency paths, run both normal and optimized Python, regenerate interface/core artifacts, compare exact SHA256 and gzip/plaintext Git blobs, run the independent proof-stream published-artifact driver and gate-specific mutation tests. No arbitrary verifier argument or alternate authority.

Actual final run (exit 0):
- Normal combined 37 tests, 10.996s, OK; independent gate boundary 3 tests, 0.072s, OK: 40/40.
- Optimized combined 25 tests, 0.728s, OK; independent boundary 3 tests, 0.075s, OK: 28/28.
- Normal and optimized proof-stream published artifact audit: 4/4 VERIFIED, 7 interface mutations rejected in each.
- 24 core outer mutations INVALID; five actual caps (work, entries, word length, seconds, journal bytes) INCOMPLETE/no result. Also actual false EXHAUSTED INVALID; actual PARTIAL gate INCOMPLETE/no closure proof. 20 older core diagnostic mutations rejected, not counted as independent new cases. 31 independent mutation cases per mode (24 core + 7 delegated interface). No operational result.
- Exact independent bounded test: 4374 corpus-owner cases, 13122 filter checks, 20k diverse symbols with 20001 index entries, two exact comparisons, 240012 work units. This is not a huge_choice_active benchmark result.
- Actual gateway delegation suite 8/8 in both modes, type identity, global ID uniqueness, receipt provenance/exact-byte binding, normalized conversion, pending/retry, concurrency, rollback.
- Entire process elapsed 23.04s; max RSS 219272 KiB. Runtime includes Python process startup, synthetic large core tests, tracemalloc, export, and independent verification. Not a solver benchmark.
- Both preceding final-gate trials on proof heads d1aeede and 8724980 also passed, but final decision uses the latest executable pin above.

| Actual artifact | Bytes (decompressed) | Events | Records | Independent structural cost |
|---|---:|---:|---:|---:|
| roundtrip-v2 | 34313 | 9 | 12 | 2 |
| adversarial-v2 | 32962 | 12 | 13 | 2 |
| interface-journal2 | 41798 | 18 | 18 | 1 |
| interface-journal2-epochs | 3400 | 1 | 4 | 2 |

All four exact artifact hashes and proof statuses in final-gate.json; regenerated normal/-O bytes match the published originals. The proof-stream driver additionally compares committed core proof/result objects to independent replay. Pending interface attempt h stays PENDING, a/f/g UNKNOWN, b PROJECTION_NO, c BOUNDED_NO, d/e fixture ACCEPT. All candidate request IDs remain pending at this layer. No external incumbent.

## Gate disposition and remaining limitations

1. Interface delegation PASS: actual type is the core RegisteredLedger, no wrapper/parallel state; legacy stateful gateway remains historical/reference only.
2. Independent journal/2 replay PASS: separate proof-stream code and published driver executed; independent agent signed off (issue #10 comment 7145173732, report at e8895a3). Exact artifact/projection/lifecycle/receipt-reference/structural checks.
3. Combined fail-closed gate PASS: runner returned VERIFIED; invalid proof has no result, resource-censored/missing/partial closure INCOMPLETE; no producer EXHAUSTED authority. Raising-boundary consumer explicitly exercised with real independent proof and actual work cap. Proof-stream public verifier may verify consistency of a PARTIAL journal, but closure gate must remain INCOMPLETE. No new journal schema.
4. Independent benchmark follow-up continues; long-diverse optimization now exists, but resource-safe replay of every planted case is not asserted by this core run. Historical full proof/interface suites are separately reported by agents; this runner executes relevant actual cross-stream tests, not every historical suite.
5. Operational gates remain: owner transport/authentication, real receipts/artifacts, capacity policy, durable crash recovery and scaling of full-history validation. Current journal is memory-only; revalidation of full history per event is potentially quadratic. Verified structural evidence is not cryptographic authentication or external ACCEPT. No external calls, no deployment, no P3 begun and no merges.

The narrow P2.1 gate is closed for the specified structural-only reference/simulator P3 path, with future P3 proof/coverage review required. Do not use this gate result as a claim that an arbitrary partial or resource-censored future certificate is verified. Do not start operational or bounded optimization from it.
