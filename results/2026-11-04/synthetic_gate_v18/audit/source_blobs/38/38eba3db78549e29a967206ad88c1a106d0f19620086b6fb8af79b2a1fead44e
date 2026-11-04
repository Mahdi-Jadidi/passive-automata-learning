# C018 frozen v1 — bounded independent static review

Disposition: **STATIC CLEARANCE FOR INDEPENDENT CAPTURED CONTROLS**.
No blocking source or mathematical defect found in the reviewed delta. This
is not runtime correctness or speed acceptance. No provider execution/import
or frozen-source edit by theory. Paper/C017 work remains paused.

Verified READINESS_V1 hashes:

* gate_v1.py: c288448f4a11849f74293b13201fdc578a79e6fbbe24165684807bd32ceeb83d
* partition_gate_v1.py: 60a5865a1846ed060b0954eef9cc7937d8709cb2a1aec4a4dbfc0925fac27758
* API_PROTOCOL_V1.md: 17c68663afe52863afd83d45677dffbee16af12f190153ae5b62301518a35b02
* EQUIVALENCE_ARGUMENT_V1.md: 0a0ecc514d713b9e0a110990f5d4c8edf52f21c1ffa388a6e46ec00ea7661422

The actual independent file diff against baseline gate SHA630850cc1e0ae469438340c5bf6e73bb9fa2ca71e24429d1e58d966c85e4cc05
was inspected, not merely the saved patch. Apart from method/import/constants
and diagnostics, only the per-word counting/foreign-symbol loop differs.
All goal-directed search, status, witness, known-K, sparse-zero and graph logic
is unchanged. CLI bytes match the baseline. git diff exit1 denotes differences,
not a provider execution failure.

## Exact accumulation and key order

Consecutive slices of at most16384 Python characters cover each word once.
Counter(chunk) gives its exact positive nonzero counts. counts.update(partial)
adds rather than overwrites them, so a symbol recurring across boundaries
retains its total count. Empty words give an empty Counter, matching baseline.
There is no normalization or byte decoding in this count substitution.

Partial Counter keys follow first occurrence within each slice; updating an
existing Counter preserves existing key positions and appends new keys in
slice order. Thus the per-word key order matches original first occurrence.
This preserves not just predicate truth but the baseline's deterministic first
nonzero distinguishing-symbol choice. No change to zero/universal alphabet
iteration order or original certificate indices occurs.

## Foreign symbols and partial metrics

Every distinct chunk key is checked against the declared alphabet. All valid
chunks commit their lengths and counts. For an offending chunk, a rare scan
finds the first invalid character; adding its local index to already committed
prior chunk lengths gives exactly baseline characters_counted before the first
invalid character, provided validation reaches that error without interruption.
The offending character itself is not added to that legacy progress count.

The new counter_characters_processed deliberately includes the full already
counted chunk; invalid_validation_characters includes the offending character
in the rare rescan. These diagnostics honestly distinguish actual work from
committed valid progress. An interruption after native Counter can have work
not yet committed to characters_counted; protocol documents that boundary.

Native Unicode code-point slicing cannot split a code point. Non-BMP symbols,
combining characters, epsilon and declared whitespace retain baseline semantics.
An undeclared symbol at the end of a later chunk is still invalid; no early
unary decision skips it or later malformed words.

## Unchanged logical gate and deadlines

Sparse positive-presence/implicit-zero logic continues to use raw multiplicities
consistently. P empty, N empty, duplicate labels, contradictory valid words,
mixed-positive count support and optional known-K are unchanged from the C015
review. All validation precedes scientific shortcut declarations. The same exact
RGS and lazy reject-cache fallback runs when required; no new prune, fingerprint
or assumption was introduced.

poll() runs before each chunk, on its key checks, after count commitment, and
within the rare invalid scan. A native Counter call is cooperative, not
instruction-preemptible; maximum chunk character payload is at most64KiB for
four-byte characters, excluding headers/Counter entries and other objects.
This is no process memory-byte or real-time latency guarantee. Parsing, hashing,
allocation and output still need external hard timeout.

Different progress/timeout outcomes on equal budgets are permissible; every
complete result must preserve the baseline logical certificate/status, modulo
method/timing/diagnostic fields. An expired poll still produces unresolved,
not insufficient information or a provisional released partition. No metric
change is evidence of performance improvement until captured comparison.

## Required independent gate

Proceed with frozen small full-family/status/witness controls and adversarial
chunk/Unicode/late-invalid/duplicate/zero/deadline cases. The corrected reachable
RGS false-prune example is preserved separately in
PRUNING_EXAMPLE_CLARIFICATION_v1.md; this candidate does not alter pruning.
Only after correctness acceptance compare the same compact output contract on
the bounded synthetic long cases. Keep censored/regressing results. No current
source fix or scope/metric churn is requested by this review.

Snapshots and hashes: source_review_v1/MANIFEST.json. No C017 paper experiment
was resumed and no historical artifact was modified.
