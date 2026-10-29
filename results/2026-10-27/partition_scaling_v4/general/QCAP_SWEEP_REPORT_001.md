# q-cap exhaustive small-instance sweep

**Run ID:** `general_qcap_sweep_001` / `20261027T094124.415915Z_6dad41771a`  
**Scientific status:** captured full-set comparison passed; independent review still required  
**Scope:** seven small complete-word samples, known k=2 or 3, alphabet size 2–4; q=1,2,3 and unrestricted. This is correctness smoke evidence, not official timing.

## Method and provenance

One independent restricted-growth-string oracle enumerated all unordered
exactly-k partitions directly over the sorted alphabet. For each fixed
partition it recomputed observed positive projection sets and the negative
rejection condition without calling provider helpers. The captured harness
then compared complete partition sets against the frozen general V3 provider,
checked every projection-language record and negative witness, checked
exhaustion, and asserted the nesting
`F1 ⊆ F2 ⊆ F3 ⊆ F∞` on every identical sample. Raw full comparison output was
printed before assertions and retained by `audit/capture.py`.

The planted partition and local words for `actual_true_q2` are in a separate
audit sidecar and were not passed to `solve`. The case has positive words `a`
and `b`, negative `aa`, and planted split `{a}|{b}` with local languages
`{epsilon,a}` and `{epsilon,b}`. The provider/oracle found no q=1 partition and
the unique split for q=2, q=3, and unrestricted mode.

| Case | q=1 | q=2 | q=3 | Unrestricted |
|---|---:|---:|---:|---:|
| one-projection control | 1 | 1 | 1 | 1 |
| actual true q=2 | 0 | 1 | 1 | 1 |
| three-projection cap violation | 0 | 0 | 1 | 1 |
| empty positive sample | 3 | 3 | 3 | 3 |
| repeated-projection control | 0 | 0 | 0 | 0 |
| higher-order pair-projection trap | 0 | 6 | 6 | 7 |
| three-factor mixed sample | 0 | 3 | 4 | 4 |

All 28 provider/oracle full-set comparisons were equal; all reported negative
witnesses were valid; every search exhausted; and all seven nested-set checks
passed. The higher-order trap has four distinct positive full words on `abc`
while every binary pair has at most two observed projections. It confirms why
the general provider checks complete block projection cardinalities rather
than treating pair evidence as sufficient.

For the empty-positive sample (`alphabet=abc`, k=2), all three unordered
partitions fit at every q because the selected finite local languages are
empty and every negative projection is unseen. This records the bounded
finite-language semantics and does not assert singleton-exactly-one recovery.
The repeated-projection sample has zero feasible partitions even without a
cap: its negative is accepted by the only alphabet split.

Cap pruning was exercised: the actual q=2 sample’s q=1 run pruned one partial
node before a complete partition. The three-positive-projection example
pruned under q=2 and fit under q=3. No V3 source changes were made.

## Captured identities

- Provider: `general/known_k_v3.py`, SHA-256
  `1519189883c8dcfa9dcfa8e309f8e2c942b46a53d1988720baae58c4ab817ed9`.
- Independent oracle/harness: `general/qcap_sweep.py`, SHA-256
  `eef499589b8c66d45c8aeb83de0063ece64a9659c144ef380b8ac4275f48b024`.
- Inputs: `general/fixtures/qcap_sweep_inputs.json`, SHA-256
  `2638a595aeb4b0354ddc7dd8d8f90f6a1a144318e974c6b1d3ddd8d73ff9edfe`.
- Hidden audit sidecar: `general/fixtures/qcap_sweep_truth.json`, SHA-256
  `44c6deef5a419993b0cdde6a8fc0ebe0a8a5057632a078cf81c4692e78b9ee0f`.
- Prepared protocol fixture also snapshotted: `general/fixtures/q2_prepared_inputs.json`, SHA-256
  `c5409dc2174650aa65d58afa62ff32f5fbc4f2775ef54452473eb805a4a121a2`.
- Attempt manifest, complete raw stdout and stderr: `audit/attempts/20261027T094124.415915Z_6dad41771a/`.

These tiny instances do not estimate scaling and do not replace the auditor’s
large-corpus or proof review. Official stage-2 timings remain held until the
source/corpus correctness gate.
