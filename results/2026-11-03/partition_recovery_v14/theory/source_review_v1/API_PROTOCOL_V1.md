# C014 exact partition family API v1

This is one exact algorithm with an equivalence-proved unary-count branch and
frozen C010 fallback. No heuristic selects a guessed partition. No source has
been executed during implementation; independent static approval precedes runs.

Input JSON must contain exactly alphabet (nonempty distinct one-character
symbols), positive and negative (finite lists of full strings). Unknown symbols,
conflicting labels, truth metadata, k and allowed_k are rejected. Duplicates
are permitted and do not alter the compatible family. No known-K variant is
implemented. No C009/C011 source is used.

Python API: `exact_partition_v1.solve(data, deadline=None)`, absolute finite
perf_counter deadline or None. CLI, from repository root after master GO:

```powershell
python -B results/2026-11-03/partition_recovery_v14/implementation/solve_v1.py INPUT.json --seconds 5
```

The CLI time budget starts before input reading; JSON parsing is standard
in-memory parsing, not a streaming JSON parser. The mathematical precheck scans
each input word once. Input byte hash binds the output to the original file.
Neither the CLI nor algorithm reads a world/truth file. Inference does not
constrain factor start states from the generator's accepting-start choice.

## Branch and output contracts

For each symbol a, let C_a contain its counts in all positive words. The
predicate is: for every negative n there exists a with count_a(n) not in C_a.
This is equivalent, for finite unconstrained regular factors, to compatibility
of the singleton partition, and hence every set partition. If it is false the
algorithm validates the frozen C010 source hash, imports that source by exact
path, and invokes its no-K default exact solve on the same data and deadline.

Top-level complete statuses are identified_unique_partition,
partial_ownership_identification, or the baseline's model_inconsistent when
applicable. `complete:false` and status incomplete carry null exact counts and
relations; they never imply uniqueness or inconsistency. Invalid input has
status invalid_input/complete:false; CLI exit 2. Interrupted/budget-limited
results exit 3. Environment/integrity/program errors are reported without an
exact claim and exit 1. Complete inference exits 0.

Fast branch: branch=unary_closed_form, representation=compact_exact_family.
The family descriptor `all_set_partitions` with singleton base_atoms represents
the entire compatible family; it is not a listing. `partition_count` is Bell(m),
`partition_count_by_k` is S(m,k); k_max_compatible=m. m=1 has one family member
and zero pair rows. For m>=2, every pair is ambiguous, with Bell(m-1) same-block
and Bell(m)-Bell(m-1) different-block partitions.

The witness_pool has two shared partition objects. all_one_block is the single
alphabet block and representative witness. Its local language is exactly the
input positives projected to that block (the positive words themselves).
singletons uses each symbol as a block with local language {a^c:c in C_a}.
Both are finite regular witnesses. Pair rows reference their IDs rather than
copying partitions/traces. `negative_count_certificates` identifies an original
negative-list index, a symbol and its negative count; an independent verifier
must recount that symbol in every positive to check absence. Indices refer to
the original order, including duplicates. Projection strings and DFA transition
tables are not materialized. This is a new compact certificate contract, not
the expanded C010 witness schema.

Fallback branch: branch=frozen_C010,
representation=C010_expanded_default. `baseline_result` retains the full native
C010 complete default payload, including all pair relations and witness
partitions/representative projection evidence. Counts are also exposed at top
level. Enumeration is disabled; the result does not claim that all partitions
have been listed. This branch retains C010's exponential search and output
costs. A C010 unknown/complete:false is normalized to top-level incomplete with
no final counts; partial payloads are not promoted to complete families.

No complete ambiguous result proves the physical generator's true ownership.
The representative is a valid sample-compatible partition; it is not labelled
as the recovered physical partition. Compact output and expanded baseline
output have different costs and must be benchmarked as different contracts.

## Sparse predicate and costs

For positive words, retain nonzero count sets and the number of positive words
containing each symbol. A symbol lacks zero in C_a exactly when it appears in
every positive (including the P-empty convention). For a negative, first check
its nonzero counts. If none distinguishes it, scan the universal-positive
symbol set until finding a symbol absent from that negative. This scan checks
at most support(n)+1 symbols: every earlier symbol was present in n.

Thus expected dictionary/set operation count is O(T+number_of_words+m), plus
alphabet sorting O(m log m), not O(m*number_of_words). Hashing whole words for
contradictory-label validation is also charged; total expected character work
is O(T). Word multiplicities count toward presence consistently. Count bit
arithmetic, hashing worst cases and Python object memory are additional costs.
No global deterministic linear-time runtime claim is made.

Bell/Stirling recurrence uses O(m²) arbitrary-integer arithmetic operations and
O(m) working integer entries. Fast output has O(m²+number_of_negatives) records,
including variable-size exact integers; it does not multiply T by the number
of pairs. Positive count sets can grow with observed counts. Full input is
already resident in memory; this is not a constant-memory file parser.

Metrics characters_scanned counts the validation/count scan, membership checks
count sparse predicate lookups, precheck_seconds includes validation,
closed_form_seconds includes arithmetic and pair/witness construction, and
total_solver_seconds covers API work (including fallback). CLI additionally
reports input_read_and_solver_seconds. Serialization is outside these internal
timers; whole-process wall time and output bytes remain necessary. Python's
decimal digit limit is disabled by the CLI so exact Bell integers are not
truncated. This does not remove arithmetic/output resource costs.

Deadline polling occurs during character scans (each 1024 characters), word
loops, count-set checks, arithmetic and pair loops. Native JSON parsing,
string hashing, allocation and serialization are not preemptible by that
cooperative check; the independent harness must use an external hard timeout.
Frozen C010 keeps its inherited cooperative limitations. No runtime/performance
claim is made before captured audit runs.
