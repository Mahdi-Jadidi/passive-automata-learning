# C018 exact synthetic gate: count-loop optimization

This version keeps the C015 input, status, proof-route and compact-witness
contract. Only the input character-count loop changes; graph extraction,
component feasibility, known-K logic, constructive witnesses, exact RGS search,
bounded reject cache and uncertainty semantics are copied without alteration.
No source has been executed during preparation. Independent static approval
and master GO precede auditor-owned runtime controls/comparisons.

Frozen baseline sources, unchanged:

- C015 implementation/gate_v1.py:
  `630850cc1e0ae469438340c5bf6e73bb9fa2ca71e24429d1e58d966c85e4cc05`.
- C015 implementation/partition_gate_v1.py:
  `60a5865a1846ed060b0954eef9cc7937d8709cb2a1aec4a4dbfc0925fac27758`.

The new CLI is a byte-identical copy of the latter and imports the colocated
C018 gate_v1.py. No C015/C011/external source is imported at runtime. After GO:

```powershell
python -B -X utf8 results/2026-11-04/synthetic_gate_v18/implementation/partition_gate_v1.py INPUT.json --seconds 5
```

Optional --known-k remains an explicitly externally trusted integer. Input
contains exactly alphabet/positive/negative, with the same finite noiseless
independent-disjoint arbitrary regular-factor assumptions. The default allows
all counts. No truth file, host ID or generated-device count is read.

Statuses remain certified_unique, ambiguous, incompatible, unresolved and
invalid_input. Only certified_unique contains a selected partition. Two
compatible distinct alternatives prove ambiguous without all-answer listing;
unresolved carries computation_incomplete=true/data_insufficient=null and no
chosen partition. Contradictory labels are incompatible; invalid schema/types/
symbols/constraints are invalid_input. API solve(data,known_k=None,deadline=None)
and CLI budget/exit-code semantics remain those documented in C015.

## Exact counting replacement

Each word is split into consecutive at most16384-code-point pieces. Their
UTF-32 character payload is at most65536bytes (64KiB); ASCII pieces have at
most16KiB payload. Python object/Counter overhead is separate and no entire
process byte-memory bound is asserted. Slicing never splits a Unicode code
point. These character chunks are not UTF-8 byte slices.

Counter counts each piece exactly. Its distinct keys are checked against the
declared alphabet; valid piece counts are added to the per-word Counter. There
is no Python metric increment per input character on this valid-data path.
The per-word counter still has only positive nonzero entries, and insertion
order follows first occurrence in the original word, preserving deterministic
missing-count witness choice.

If a key is foreign, the small offending piece is scanned to the first foreign
character with1024-character polling. The API returns the same invalid-input
error, and characters_counted includes exactly the preceding valid-character
prefix as in C015. No count-based decision is made from an invalid word.
Counts are not normalized, estimated, sampled or inferred from a chunk prefix.

Word/schema checks, zero-count logic, original-list indices, duplicate handling
and contradictory-label detection are otherwise unchanged. In particular an
earlier false unary predicate does not skip validation of later words.

## Metrics and time bounds

Existing characters_counted counts committed valid input characters; in a
completed valid precheck it is exactly the total input character count T.
During an interruption it is progress, not an assertion that all observations
were processed. Invalid-symbol results preserve the C015 first-invalid prefix
count. Additional diagnostics:

- count_chunks: Counter calls actually completed on nonempty pieces.
- counter_characters_processed: sum of sizes of those pieces, including a
  foreign-symbol piece or a piece processed before the next deadline check.
- invalid_validation_characters: characters actually inspected by the rare
  Python scan of an offending piece, including its first invalid character.

Deadline checks occur before each bounded Counter call, on distinct-key checks,
after count commitment, and in the invalid-symbol scan. A native Counter call
cannot itself be preempted; the next poll returns unresolved on expiration.
Input parsing/hash/output and inherited native operations still require an
external hard timeout. The optimization changes polling locations and wall
time, so equal budgets need not produce identical cutoff outcomes; every
complete scientific decision must remain exact. Common complete results are
compared modulo method/timing/diagnostic metrics, with all witnesses checked.

The method field is C018-exact-chunked-count-gate-v1. No wider search shortcut,
new model assumption, heuristic choice or physical-recovery promise was added.
Counter's stdlib implementation may use native acceleration; speed is an
empirical environment-dependent question. Startup, JSON I/O, hashing, output
bytes, regressions and censored runs must remain in the benchmark. A million
character target is a measurement goal, not an achieved or guaranteed result.
