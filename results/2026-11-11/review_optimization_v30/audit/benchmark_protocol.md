# C030 independent audit and timing protocol (pre-run freeze)

Status: fixture/protocol preparation only. No optimization candidate has been executed. Candidate runs require approved proof, frozen source SHA, and explicit manager GO. Biggest overlooked point? A full result includes exact compatible and optimum counts, two ordered witness families, and normalized rejection references; a maximum-only match is insufficient.

## Oracles and contract

`reference_oracle_v28.py` is the unchanged recursive set-insertion oracle (distinct from baseline RGS generation). It projects tuples of atomic IDs and reconstructs canonical RGSs. For source-compatible serialization, the harness will transform its independent witnesses to the C028 output shape and independently generate factor lists in first-occurrence positive-projection order. The frozen C028 source remains a second comparator. Every candidate result is compared field-for-field with both after documented normalization; no expected output is inferred from a candidate.

Compare status, exact `compatible_count` C, `optimal_count` O, `max_blocks`, `optimal_unique`, full recommendation witness (including factors and `negative_rejected_by`), first up to two `compatible_witnesses`, first up to two `optimal_witnesses`, and null-field behavior for `INCOMPLETE`, `INVALID_INPUT`, and `ERROR`. For all complete results, additionally replay each witness against normalized samples and check partition coverage/order, factors, and first rejecting block. Compare all K values derived from the returned maximum/status. Input ordering and first-occurrence deduplication are retained.

## Frozen correctness corpus

The committed fixed file contains 24 adversarial records; with the oracle's 2187 exhaustive and 60 seeded inputs, the unlimited comparison suite has 2271 cases. Candidate budget checks use eight additional fixed input/budget pairs per variant; invalid-input/budget checks use nine pairs per variant.

1. Exhaustive two-ID labelings: all 3^7 assignments over `epsilon, a, b, aa, ab, ba, bb` (2187 records).
2. Seeded generic IDs: 60 deterministic records for alphabet sizes 3..8, seeds `280000 + 100*m + j`, matching the unchanged oracle generator.
3. Fixed adversarial cases: empty alphabet/epsilon; no observations; P empty; N empty; all-compatible and zero-compatible; contradiction; unused IDs; duplicate positive/negative words with ordering-sensitive witness refs; nonadjacent forced symbols; multiple tied optima; distinct compatible count vs optimum count; unicode and punctuation/whitespace IDs; tuple-collision IDs `a,bc,ab,c`; long words over a small alphabet; a batch of many distinct traces on a small alphabet; added-sample changes to the canonical optimum; malformed schema and invalid budget.
4. Applicable C026 finite-sample regression fixtures: CE1; CE2 initial plus extensions by `b` and `c`; CE3's same finite sample; CE7; and the quantifier counterexample `Sigma=[a,b], P=[a],[b], N=[ab]`. CE4–CE6 are about physical-language constructions, not distinct finite partition inputs; CE8 concerns a persistent interrupted implementation, not an exact finite input. They are not misrepresented as independent sample cases.
5. Candidate A explicit-budget boundary: singleton-compatible inputs with budgets `0`, `1`, `Bell(m)-1`, and `Bell(m)`, plus `m=0`, `m=1`, and an already contradictory input. Verify unlimited shortcut vs budgeted baseline semantics exactly.
6. Candidate B memo cases: the frozen source uses a per-invocation 256-entry LRU. A 9-ID all-compatible case reaches >256 distinct nonempty subsets; diagnostic-only OrderedDict instrumentation must observe an eviction and later reinsert/recompute of an evicted key. Also run two consecutive solves with disjoint inputs to expose stale cross-solve data and an early-negative-failure case where baseline stops at its first negative but a cache miss computes the full negative vector. Instrumentation is a separate non-timed diagnostic and must not alter the candidate source; do not require speedup on early-failure.

Invalid input cases check exact `INVALID_INPUT` status and null mathematical fields, not exception text unless specified by the frozen contract. Empty alphabet has exactly one empty partition; empty positive and negative sets make every partition compatible. A contradiction short-circuits as specified by the source. All words and blocks remain tuples/lists of whole IDs; never concatenate symbols.

## Mutation checks for the independent checker

Before comparing official candidates, apply five local mutations only to copied expected-result objects: change C or O by one, reverse first-two witnesses, change one RGS label, and change a rejection index. Also assert that treating the tuple-collision fixture as concatenated strings contradicts the oracle result. Cache freshness, eviction/reinsertion, and early-stop/full-vector behavior are separate diagnostic-only candidate checks after GO. Mutations do not alter candidate/source files and are not counted as candidate defects.

## Frozen bounded timing plan (after correctness gate only)

Eight fixed inputs: singleton-compatible/no observations; a second singleton-compatible case; forced nonadjacent block; tied nontrivial optimum; B repeated-mask pressure; B early-negative-failure regression; long small-alphabet/many-trace case; and one general no-fast-path case with alphabet size bounded so baseline completes within the cap. Benchmark exactly baseline and combined candidate, up to three repetitions each, same full-result contract, fixed order and input files. Both receive identical unlimited budget for every timing input. Explicit-budget fallback is correctness-only. Run each solver process with a 20-second timeout and 25-second outer timeout; record timeout as a failure/incomplete observation and never omit it. Correctness gates precede timing. Do not rerun unfavorable measurements for presentation. Report per-case raw durations, all repetitions, medians only alongside all raw samples, environment, exact commands, source/protocol/corpus hashes, and that time includes process startup. Do not claim asymptotic improvement from these bounded timings. Separate any solver-provided CPU/work counters from wall time; no memory claims without direct instrumentation.

## Limits

The oracle and bounded cases are falsification tools, not proof of general correctness or polynomial runtime. Any universal exactness claim depends on the independently reviewed proof plus frozen source correspondence. Actual completion is separate from mathematical finiteness and host resource limits. Samples constrain the inferred compatible partition problem; they do not identify the unique physical hidden partition in general.
