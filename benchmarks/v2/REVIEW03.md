# Review 03 final independent replay and P3 fixture handoff

## Pins and scope

- Integration review 03: d6daba598ba382f6c213deb12a598d60d3817b00; issue #10 review comment 7144845512.
- Core: 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d; reviewed predecessor interface b27850a667a55927fd3ad127dccce3956d8ead22 and proof ed20d9b12ea9730e07e7d2d1e0581744a266eb02 for the core's original tests.
- Newly published delegated interface: 0eb1050ad103bad2f93d3b9feb732bf94184f2a2. Final independent proof: e8895a344821f7cd463823774e6bc591e064264c (issue #10 comments 7145032831, 7145087025, 7145173732).
- Git network DNS failed; exact source snapshots reconstructed locally and verified against Git blob IDs, not clean worktree CI. Python 3.13.5, Linux, RLIMIT_AS as indicated. No external attempts. No operational acceptance. Core/interface/proof source and legacy learners/baseline unchanged.
- Core-owned formal combined gate is not declared closed here. Independently reran the reviewed core suite, final delegated tests, final proof unit suite and full outer verifier on regenerated actual artifacts. Did not execute a later core-owned combined runner or every proof-stream stand-alone audit driver.

## Independent execution

| Suite | Normal | Optimized (-O) |
|---|---:|---:|
| Reviewed core full/integration | 21/21, 9.640 s | 9/9, 0.146 s |
| Latest actual delegated gateway | 8/8, 0.038 s | 8/8, 0.040 s |
| Latest independent proof unit suite | 17/17, 1.037 s | 17/17, 1.159 s |
| Full independent outer journal/2 replay | 4/4 | 4/4 |

Core suite exact outputs in results/review03-journal-tests.md. Delegation tests: gateway.py blob 8b314e11c0d935122779365b08666c482697621f; test_gateway_v2.py 502b7c40f7776fc3bab087303e457fae149587c3; export_journal2.py 1d3a16f03171f2259427ecda8de94282ffda8cae. Test auth is HMAC fixture only. Normal/optimized generator exports byte-identical.

Proof tests: test_bounded_deletion.py 2f59257d0ff3396417c2cedf9845f61e2fd20928; test_independent_replay.py cbb924c5ffc13ccda66910313703c4b8723e7ae8; test_ledger_replay.py e42dcec06d7d2e52d2fe7ede112498c74cd6f07a; test_production_replay.py 630e2150d186cff9181d96ca7b8a6d713aa1a7c7. All six proof modules verified against hashes in review03/final_replay.py. Both modes reproduced 4374 corpus-owner cases, 13122 filter checks, long diverse word 20000 symbols, 20001 index entries, 2 exact checks, work 240012; 2187 exhaustive corpora, 4374 structural checks, 925 forced edges; 44 mutation rejections, 30 ledger mutations, 39 epoch structural mutations, 13 request mutations. Wall/RSS normal 1.96 s/110736 KiB, optimized 3.56 s/112672 KiB. Test suite timing excludes interpreter startup.

Fresh actual journal artifacts (normal/-O exact decompressed byte parity and published SHA-256 parity):
| Artifact | Bytes | SHA-256 | Independently verified structural cost |
|---|---:|---|---:|
| roundtrip-v2.json | 34313 | 14f0dc4cb606ca7f1b20a5cd575a937dd6471da594d983d86254e210573e5ab8 | 2 |
| adversarial-v2.json | 32962 | 1b78c4aefe974db58409cb186528af75b1981752ba0a3778634fe3bcb406e97c | 2 |
| interface-journal2.json | 41798 | caf40422d9d3e6d0cd8257da4b757cacd71cda1e6db089493421c912515edf94 | 1 |
| interface-journal2-epochs.json | 3400 | adabd0b274ebaa2ce55aab7f874f6485664399d4b0df59b013d158cfb2338491 | 2 |

Adversarial artifact: a UNKNOWN, b PROJECTION_NO, c BOUNDED_NO, d mock ACCEPT, e PENDING; 3 quarantines. Delegated artifact: a UNKNOWN, b PROJECTION_NO, c BOUNDED_NO, d/e mock ACCEPT, f/g UNKNOWN, h PENDING; 5 quarantines. Operational INCOMPLETE throughout. A work=0 replay of roundtrip returned INCOMPLETE, no result, work=10. Independent verifier imports neither producer, adapter nor audit_journal.

## Resource-bounded replay

Prototype experiment in review03/bounded_join.py only; 3 unit tests (0.224s), 14040 exhaustive comparisons, 900 forced zero-bit collision randomized comparisons. Compact signature filters, streaming literal equality on every hit. This is a benchmark experiment, not production proof. Actual journal/2 raw pipeline used unchanged RegisteredLedger and original archive inputs. At 5 s / 512 MiB choice closure TIMEOUT and long closure MemoryError. At 30 s / 1536 MiB closure and journal succeeded in both. See review03-scale.csv and review03-replay-only.csv for complete phase telemetry. Experimental filter only verifies raw structural facts, not outer journal provenance.

Proof agent's subsequently published bounded API is measured separately on those SAME exported journals (not regenerated approximations). All four trials used 30-second deletion deadline and outer 31-second process timeout, work 200000000, entries 2000000, word length 2000000, process RLIMIT_AS 512 or 1536 MiB. At 512 MiB both official replays return INCOMPLETE (MemoryError before deletion work; no result). At 1536 MiB huge_choice_active verifies mandatory floor 1, optimum absent; huge_long_active verifies floor and structural optimum 10000. See results/review03-final-replay.csv. Replay times include JSON parsing and outer verification; prior prototype phase timing boundaries differ. RSS is observed, not equivalent to virtual address space cap. Literal control on same choice journal at 1536 MiB still MemoryError (10.01s, RSS 1250932 KiB); official bounded replay completes in 1.794086109s (RSS 245428 KiB). No general memory or performance guarantee; single runs. Long case literal control completes 2.216188714s; official bounded outer 2.391398516s; not a speedup claim. Journal hashes: choice dfbc8c72bdecb316fe72dafdb8130b97887c8e7b81cc129bd41eb2eab63463d5; long 779cc7dd5f9198f5e4a5f1460e3ef2f869a2c45e509e0b41daaae016bf8ac3fe.

## P3 fixtures prepared, not solved

Use review03/prepare_p3.py on output of previous recover_inputs.py (original 3 archives). It verifies exact input SHA-256, raw-only keys, archived reference costs; writes input-manifest and seven raw JSONs independently of evaluation directory. Run twice, diff -qr identical. Manifest SHA-256 b69986b320ea9f328e0c107696e6ff4d9f2c71efc0624a6859c98295f16389ba; Git blob 68d2414bd7e1f9294a850268369a55559d440b06. Evaluation index blob 289b7bf33b9d5e47eb863fb7099d1c22722f0722. Four unresolved planted cases + three pinned fixtures. Costs and prior floors are historical evaluation-only, never exposed to exact-search engine. For P3 run only inputs/*.json; do not feed evaluation index, references or planted information. No P3 search begun. Downloadable ZIPs prepared separately: input SHA256 653006171639967447e90b2a60c4f7fd0d33d307e02e6890fe0941e2a268f4c1; evaluation SHA256 4260943245d1b7ce829d46f620fc2e4806754e555947dea19563febbf7d5303b. Raw archive data not duplicated in git; reproducible extraction and manifests committed.

## Reproduction

From scratch review03 directory, populate core/selector_v2/ from core pin, interface/ from reviewed predecessor research/interface/p2 (then add latest gateway, tests and export driver for delegation), proof/ from reviewed predecessor tests/reference, proof-final/ from final proof tests/reference. Verify blobs as in reviewed suite and final_replay.py. Use exact original recovered inputs and references as in REVIEW02.md.
```bash
python -B -m unittest -v test_bounded_join
python -B prepare_p3.py /path/to/recovered p3-fixtures
python -B prepare_p3.py /path/to/recovered p3-fixtures-repeat
diff -qr p3-fixtures p3-fixtures-repeat
# Core reviewed suite: see results/review03-journal-tests.md
(cd interface && PYTHONPATH=../core python -B -m unittest -v test_gateway_v2)
(cd interface && PYTHONPATH=../core python -B -O -m unittest -v test_gateway_v2)
(cd interface && PYTHONPATH=../core python -B export_journal2.py ../delegate-export)
(cd interface && PYTHONPATH=../core python -B -O export_journal2.py ../delegate-export-opt)
diff -qr delegate-export delegate-export-opt
(cd proof-final && python -B -m unittest discover -v)
(cd proof-final && python -B -O -m unittest discover -v)
for artifact in roundtrip-v2.json adversarial-v2.json delegate-export/*.json; do
  python -B final_replay.py "$artifact" --proof proof-final --memory 1536
  python -B -O final_replay.py "$artifact" --proof proof-final --memory 1536
done
for name in huge_choice_active huge_long_active; do
  python -B raw_journal_bench.py /path/to/recovered/planted-inputs/$name.json scale-$name-512 --seconds 5 --memory 512 --replay filter
  python -B raw_journal_bench.py /path/to/recovered/planted-inputs/$name.json scale-$name-1536 --seconds 30 --memory 1536 --replay filter
  for cap in 512 1536; do
    timeout 31s python -B final_replay.py scale-$name-1536 --proof proof-final --memory "$cap"
  done
done
python -B final_replay.py roundtrip-v2.json --proof proof-final --work 0
```
For literal and replay-only experimental controls use raw_journal_bench.py with --stage replay --sources . and original artifact directory/input; see source CLI. Record stderr on resource censoring. No merge, no live endpoint, no CI or operational claim.
