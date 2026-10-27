# B static review of C003 corpus v1

Scope: freeze_corpora.py and frozen_c003_v1/freeze_manifest.json, exact copies and
hashes in manifest.json. No generator, solver, test or label-recomputation run was
performed. Read-only file-integrity checks are saved there. All seven v1 file
hashes match their manifest; generator bytes match generator_sha256. Both C002
reference-file hashes also match the values recorded in v1. This establishes
byte identity at review time, not independent semantic validation of every row.

Generator SHA256 b0f27caa9c2c8b090e6217feed676b5f22e32ac55ea7054045add4d08a3f5d64
Freeze manifest SHA256 145276692ac76037fd20a29c16b96f933a0e14f5674e353df45d8f792e129e79

## C1 — known job duplication: block execution of unchanged v1 plan

The fixed_in loop already appends 120 fixed-word jobs. jobs.extend appends those
same method/case IDs a second time. With 78 regressions, the logical unique plan
has 2*78 + 2*120 + 120 = 516 IDs, whereas the recorded v1 count is 636 rows.
This matches the master's previously discovered defect; it is not claimed as a
new independent discovery. Repeated execution can overwrite ID-based outputs,
double-count structural results, or exhaust budgets unfairly. Keep the original
636-row artifact unchanged. Use a separately versioned corrected plan with a
uniqueness gate and explicit parent v1 hash. Do not silently deduplicate and
publish the old plan as if it originally had 516 rows.

## C2 — reference binding is not enforced by this loader

load_c002_regressions loads IDs from the C002 frozen manifest but takes input and
F2 from gzip rows without checking their input against the manifest's expected
per-case hashes. It does not first require the gzip/manifest hashes to match
trusted C002 acceptance evidence. Hashes computed and recorded only at the end
describe whatever was read; they are not an authenticity gate. A row missing or
marked incomplete is silently skipped, potentially shrinking selected tiers.
Repeated case IDs in baseline_rows would silently replace prior rows.

Before accepting the selected references, independently bind each selected ID,
its original dataset/index and canonical input bytes to the frozen C002 manifest,
and bind its F2 to the verified saved baseline row. Require every planned selected
reference to exist/complete, or record missing-reference coverage explicitly.
The hashes currently match the known C002 manifest and saved baseline gzip, so
this is an absent loader/provenance-validation guarantee, not evidence that these
actual rows were corrupted. The earlier C002 summary says the overall scientific
run was incomplete because lazy timed out on 17 cases; its baseline completed all
10594 exact-set comparisons. Thus that overall incomplete status alone does NOT
invalidate complete baseline reference rows, and lazy partial answers must not be
substituted for full F2.

## C3 — v1 generator is not safe to rerun in place

OUT.mkdir(exist_ok=True), dump_jsonl.write_bytes and final manifest.write_bytes
allow an existing frozen_v1 to be overwritten. Versioned freeze generation must
refuse an existing destination or write a new directory. The reviewed old source
can be preserved as evidence, but must not be rerun against frozen v1 during
correction. A changed job plan belongs to a separate plan v2 as already directed
by master. This task changed no frozen file.

## C4 — v1 alone does not cover the full C003 control protocol

Generated fixed_word_cases are all positive constructive-coverage cases with
genuine negatives. The job loop skips fixed-word regression jobs and applies the
structural solver only to fixed_in. Consequently this v1 structural job list
contains no explicit missing-positive/empty/absent-symbol controls, disconnected
coverage ablations, count/odd-cycle assumption violations, accepted-negative
conflicts, or class-versus-general ambiguity contrasts. General regressions may
contain some such inputs but do not test structural statuses when the structural
method is skipped. These controls must be frozen separately and executed before
claiming the full approved C003 validation protocol complete. A later corrected
plan/control extension may resolve this; it is outside this exact v1 review.

## Planted DFA labels and size coverage

dfa_make creates 2..5 states with at least one accepting and one nonaccepting
state, arbitrary start, and a complete transition table over each local block.
dfa_accepts performs ordinary deterministic transition traversal. A global word
is positive exactly when both projected local DFA runs accept; otherwise it is
negative. This is the intended independent disjoint regular-factor product.
The source never calls the old validator capped at ten. Alphabet sizes
4,6,8,10,12,16 use distinct one-character symbols, 20 cases per size, giving the
declared 120 cases; twelve distinct positives and twelve negatives are retained
per successful case. No silent truncation of alphabet 12/16 occurs here.

The fill loop retries DFAs if both label classes cannot be sampled, with a bounded
number of retries; exhaustion raises rather than pretending a filled dataset.
Sampling is conditioned on finding both classes, so these are not uniform draws
over all random DFAs. Candidate lengths are 1..24, allowing longer traces, but
retention sorts all accumulated words lexicographically and takes the first 12.
This is a lexical selection bias and does not guarantee every case contains a
long word. Report actual length strata from an independent corpus validator
rather than asserting long-trace coverage from the upper sampling bound alone.

All DFA planted partitions use the same contiguous half split for a given size.
This is a limited benchmark distribution, not evidence of recovery on arbitrary
hidden ownership patterns. Empty projected local words are allowed through DFA
start-state acceptance; sampled global words need not touch both blocks. This is
valid in the unrestricted product model and should not be mislabeled a sampling
bug. No epsilon global word is drawn, so epsilon edge coverage needs controls.

## Structural labels, repetitions and sufficient coverage

fixed_word_cases shuffles declared symbols into two nonempty blocks and includes
every block symbol at least once in its local word. uv and vu are guaranteed
positives; shuffle_merge preserves the order of both local words, so added
positives are genuine shuffles. For every cross-block pair, uv and vu have
different pair projections, proving a connected complete bipartite opposition
graph. Negative construction explicitly rejects strings whose two projections
equal those local words; sampled negatives cannot be positives. De-duplication
preserves the uv/vu coverage because both local words are nonempty and disjoint.

The declared 20 cases for each size 2,8,16,32,64,128 total 120 and reach the
requested 128-symbol constructive scope. Symbols chr(0x100+i) remain individual
Python characters. The source comment 'Two copies ensure deliberate repeats'
does not match code: multiplicities are randint(1,3), not at least two. Repetitions
are possible, not guaranteed for every case, particularly at m=2. Independent
inventory should report which frozen cases actually repeat symbols; do not claim
guaranteed repeated-symbol coverage for each sample from this comment.

## Regression subset and truth separation

The selector takes 60 fixed-seed random_ternary_5000 indices and only first/middle/
last for other main frozen C002 tiers. The declared 78 rows are therefore a
subset, not reuse of every old exhaustive case or every targeted control. For
prior_theory_4, indices 0,1,3 are selected, omitting index 2. For nine targeted
controls only 0,4,8 are selected. The separate C002 legacy-generator extension
is not selected by this main-manifest loop. Describe exactly that coverage and
supplement specific old controls if needed; do not call it a full C002 re-audit.

Input files contain only case IDs and alphabet/positive/negative samples (plus
reference provenance fields on regression records). DFA tables, local words and
true blocks are written to distinct truth sidecars; F2 references are also
separate. The generator imports no candidate provider, so no target truth enters
a solver through this generator. This review cannot certify downstream worker
dispatch: its independent validator must pass ONLY row['input'] and verify that
truth metadata remains in the audit process. A valid first answer need not equal
the planted partition; planted agreement is a separate audit statistic, never a
general identification theorem.

Remaining: independent per-row labels and witness/reference validation, frozen
control extension, unique corrected plan, trusted provenance gates, and actual
observed coverage inventory. None was run or fabricated by this static task.
