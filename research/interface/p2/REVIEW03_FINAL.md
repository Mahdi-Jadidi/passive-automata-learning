# Review 03 — interface stream final handoff (P2.1)

## Disposition

The interface delegation milestone and independent proof item are complete. The core owner's committed combined gate closes the narrow P2.1 structural integration gate as VERIFIED. Operational status remains INCOMPLETE. This is not external evaluator acceptance, not deployment approval and not permission to begin operational or bounded optimization.

Authoritative journal format remains selector-v2-journal/2 with inner selector-v2/1. No schema revision, external learner edit, baseline edit, merge or P3 implementation in this interface stream.

## Exact source pins and authority

- Authoritative core implementation: RegisteredLedger at 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d. The core combined run used a later tested core predecessor 796a83a5f8f69c4dc7c0db619e1cdb130ddc0b33; the final report confirms the RegisteredLedger implementation itself is unchanged from 4e21dbf.
- Interface delegation and actual exports: 0eb1050ad103bad2f93d3b9feb732bf94184f2a2 (this branch).
- Independent proof executable pin: 83762437ba05e1def9dde5edff8c7d44878f4269.
- Independent proof sign-off/documentation: e8895a344821f7cd463823774e6bc591e064264c. Compare from executable pin shows only research/audit/PROGRESS.md and research/audit/REVIEW03_JOURNAL2.md changed; no executable source changed.
- Core combined-gate report: c5e7e170add6f92e129099bf7444f5fd7a29eb3a, selector_v2/integration/REVIEW03_FINAL.md and final-gate.json.
- Review authority: INTEGRATION_REVIEW_03.md at d6daba598ba382f6c213deb12a598d60d3817b00; proof sign-off issue #10 comment 7145173732.

## Interface contribution

research/interface/p2/gateway.py exposes open_gateway(raw, authenticate=...) and returns the actual core RegisteredLedger instance. There is no stateful gateway wrapper, competing observation ledger, receipt sidecar, alternate attempt registry or dual-write. Adapter request/map/response validation and strict parsing are dependencies only. Prior SharedGateway, strict_ledger.RegisteredLedger and standalone adapter ledger remain historical/reference regression code.

The delegated tests verify the returned object's exact type and absence of alternate state; journal version guard; registration and exact input-byte/authentication binding; origin, capacity and original-ID mapping provenance; global attempt ID uniqueness; receipt-token digest/reuse; strict JSON; normalized table conversion; DFA validation; atomic rollback; reentrant write rejection; UNKNOWN retry and pending-candidate semantics; wrong-request/late response isolation; and concurrent registration/delivery.

Interface milestone results:
- Combined interface regression: 27/27 normal.
- Delegation suite: 8/8 under Python -O.
- Actual interface journal/2 exports regenerated in normal and optimized Python with byte-identical JSON and deterministic gzip.
- Four artifacts later independently replayed by proof stream; see below.
- External-labelled observations are test-only HMAC fixtures. No live external calls or operational receipt trust.

## Actual journal/2 artifacts and independent replay

All four committed artifacts were independently replayed by proof agent #3 using separate proof-stream code, with no producer validation or core audit_journal.py imports in the verifier. The proof agent's report is research/audit/REVIEW03_JOURNAL2.md at e8895a3; sign-off is issue #10 comment 7145173732.

| Artifact | Decompressed bytes | Events / records | SHA-256 | Independent structural cost |
|---|---:|---:|---|---:|
| roundtrip-v2 | 34,313 | 9 / 12 | 14f0dc4cb606ca7f1b20a5cd575a937dd6471da594d983d86254e210573e5ab8 | 2 |
| adversarial-v2 | 32,962 | 12 / 13 | 1b78c4aefe974db58409cb186528af75b1981752ba0a3778634fe3bcb406e97c | 2 |
| interface-journal2 | 41,798 | 18 / 18 | caf40422d9d3e6d0cd8257da4b757cacd71cda1e6db089493421c912515edf94 | 1 |
| interface-journal2-epochs | 3,400 | 1 / 4 | adabd0b274ebaa2ce55aab7f874f6485664399d4b0df59b013d158cfb2338491 | 2 |

The independent proof audit checked outer journal/event bindings, registration metadata, exact wire and normalized bytes/digests, response projection, receipt references and reuse, original-ID maps, attempt lifecycle, UNKNOWN quarantine, structural facts and deletion obligations. It rejected 24 core outer mutations plus seven delegated-interface mutations (31 counted mutation cases per mode). Four resource-capped verifier cases returned INCOMPLETE without proof. False EXHAUSTED was INVALID; partial closure remained INCOMPLETE. Normal and optimized proof runs agreed. All artifact results retain operational_status=INCOMPLETE.

## Core owner's combined gate

The core owner subsequently published REVIEW03_FINAL.md and final-gate.json at c5e7e17. I inspected these committed reports and the machine-readable gate result; this interface stream did not independently rerun the core combined runner.

Reported actual combined execution:
- Normal: 37 combined tests + 3 independent gate-boundary tests = 40/40 passed.
- Optimized: 25 combined tests + 3 independent gate-boundary tests = 28/28 passed.
- Independent published-artifact audit: 4/4 VERIFIED in both modes.
- Interface delegation suite: 8/8 in both modes.
- 31 counted outer/delegated interface mutation cases rejected per mode.
- Five resource caps (work, entries, word length, seconds, journal bytes) returned INCOMPLETE/no result.
- Actual false EXHAUSTED rejected; actual PARTIAL closure did not certify exhaustion.
- Exit status 0; reported elapsed 23.04s, peak RSS 219272 KiB.
- final-gate.json has status VERIFIED, blockers [], operational_status INCOMPLETE; all four artifact statuses VERIFIED and all artifact closure states FIXPOINT.

The narrow P2.1 structural gate is therefore closed for the specified reference/simulator evidence path. This does not authorize arbitrary partial/resource-censored certificates, operational acceptance, or an operational candidate. Any later P3 work requires its own proof/coverage review.

## Reproduction and evidence locations

Interface tests and artifact export:
```sh
git worktree add --detach /tmp/core-j2 4e21dbf0d06c030681e774cb15f1a5cf0c802f0d
cd research/interface/p2
export PYTHONPATH=/tmp/core-j2/implementation/partition_feedback_final
python -m unittest -v test_adapter test_strict_ledger test_shared_gateway test_gateway_v2
python -O -m unittest -v test_gateway_v2
python export_journal2.py generated_j2
python -O export_journal2.py generated_j2_opt
diff -r generated_j2 generated_j2_opt
```

Core owner's final combined gate reproduction is documented in core commit c5e7e17:
```sh
/usr/bin/time -f 'elapsed=%e maxrss_kib=%M' env PYTHONPATH=. \
  python -m selector_v2.integration.run_final_gate \
  --interface-dir pinned/interface-review03 \
  --proof-dir pinned/proof-review03 \
  --core-artifacts . --output-dir final-gate-run3
```
Use the exact source pins above and a fresh output directory. The committed core report lists exact commands, source blob checks and measurements.

## Limitations and non-claims

- Git DNS prevented clean network-enabled worktree checkout/CI. The cited suites used byte-verified source snapshots; this is not a CI pass.
- Journal authority is in-memory; no durable crash recovery.
- Full-history revalidation on each event may be quadratic in transaction count.
- No live external endpoint, transport, cryptographic receipt authority or owner-approved capacity policy was exercised.
- HMAC signatures in interface fixtures are test-only.
- Benchmark follow-up and large planted-case replay are separate work; the combined structural gate did not claim every recovered planted case had been benchmarked or verified.
- No external calls, deployment, merge, learner/baseline changes, P3 implementation or operational acceptance.

## Interface branch milestones

- M7 delegation and interface tests: e2f97c4817db13e3ae7ab4dcbb938ab24be3ef8f.
- M8 actual compressed journal/2 exports: 18d0fab785236dfec1b23e9e0896f48e9961f039.
- M9 plaintext proof-agent interchange: 0eb1050ad103bad2f93d3b9feb732bf94184f2a2.
- M10 final proof and combined-gate handoff: documented in this commit.

PR #6 remains open and draft, based on research/selector-v2. No merge was performed.
