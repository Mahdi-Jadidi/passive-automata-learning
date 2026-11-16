# V42 exact maximum-device optimizer

Experimental implementation of the optimum-only contract. No DFA state bound,
no automata learning, no C/O counting, no outer partition-enumeration loop.
Historical results are unchanged. Scientific novelty and universal superiority
are not claimed. Independent human/agent source-and-proof review remains pending;
the planned pre-code independent gate was not completed. Do not treat author
reasoning and the executed tests as that independent review.

## API and dependencies

Add this directory to Python's module search path, then:

```python
from optimizer import solve_optimal
from verify import verify_optimal
data = {'alphabet':['a','b','c'], 'positive':[[],['a','b','c']], 'negative':[['a']]}
result = solve_optimal(data, {'timeout_seconds':60})
assert verify_optimal(data,result, {'timeout_seconds':60}) == {'status':'ACCEPT'}
```

Result has exactly status, blocks, max_devices, certificate. OPTIMAL contains
one compatible maximizing partition; ties need not be lexicographically first.
INFEASIBLE contains a direct checkable contradiction/empty-alphabet certificate.
INVALID_INPUT and INCOMPLETE contain null mathematical fields. Alphabet IDs are
distinct nonempty opaque strings; word lists use declared IDs. Validation
precedes contradiction; duplicate whole words retain first occurrence. Empty
alphabets, epsilon and unused IDs follow the historical mathematical model.
`limits=None` has no explicit time cap. The only limit option is a finite
nonnegative timeout_seconds; native SAT is interrupted with a timer and Python
stages check deadlines cooperatively. Hard termination can yield no response.
This is a Python API, not a strict JSON CLI; max_candidates is not exposed.

Optimizer uses python-sat 1.9.dev22 / Glucose3 `g3`, and six 1.17.0 from the
existing local `results/2026-11-14/sat_candidate_v37/vendor` installation.
That installation is Windows CPython 3.12 specific. Reproduction elsewhere needs
compatible pinned packages. Checker imports no SAT library and no optimizer.
Both share the trusted deterministic encoder `encoding.py`; this is not two
independently implemented encoders. Integrity and correctness of normalization,
minimal-edge construction, CNF construction and the checker are trusted.

## Algorithm and correctness argument

Positive projection languages H(B) and rejection sets R(B) use whole IDs. A
partition fits iff each negative is in R(B) for at least one block. Enlarging a
block preserves rejection. For each negative n, symbols a for which the full
alphabet minus a does not reject n must occur in its rejecting block. Joining
these forced symbols and taking transitive closure therefore contracts only
mandatory pairs; every compatible partition is a partition of the resulting q
atoms. Atom contraction changes neither feasible partitions nor block count.

Enumerate subsets of atoms by increasing size. Retain each subset T rejecting n
only when none of its previously retained nonempty subsets rejects n. Finiteness
and monotonicity prove that every rejecting block contains one retained minimal
T, and every block containing such a T rejects n. Superset skipping is sound.
This costs up to 2^q subsets, not Bell(q) partitions, and can still be expensive.

CNF pair variables express same-device membership. All three implications per
triangle enforce transitivity; symmetry is implicit in unordered pairs. For
each edge T, a full-equivalence conjunction says all its atoms share a block.
Each negative's disjunction requires at least one such edge. A representative
variable is true exactly when no earlier atom shares its block; their sum is
exactly device count. A deterministic full-equivalence sequential counting
network implements threshold tests. Binary search uses satisfiability monotonicity
to find the largest feasible threshold. A noncontradictory nonempty instance
always has the full-alphabet one-block feasible lower bound. Witness partitions
are decoded in original alphabet order. No satisfying models are enumerated or
blocked and no counts of models/automata are confused with partitions.

Symbol or mandatory-atom bounds certify maximal answers directly when attained.
Otherwise a fresh proof-enabled solver refutes the rebuilt threshold K+1 CNF.
Checker validates the partition against original projections, rebuilds the CNF,
and checks each DRUP addition by reverse unit propagation. Deletion lines are
parsed but safely ignored: keeping extra clauses preserves the RUP implication.
It finally demands a unit-propagation contradiction. If the starting formula is
already unit-inconsistent, an empty proof is legitimate. Solver model or UNSAT
status alone is not a certificate. The optimizer runs proof checking before
returning a nontrivial exact claim. The consumer supplies the original instance
again; it does not trust a producer-supplied CNF or instance hash.

Formula size includes O(q^3) triangle clauses, minimal-edge incidence, and
O(q^2) cardinality gates. Edge extraction, solver search, proof size and naive
proof verification can be exponential. There is no general polynomial guarantee.

## Executed validation

`audit.py`: 2201 oracle comparisons (2187 distinct two-symbol ternary labelings,
four empty-alphabet cases, ten fixed synthetic cases), all optimal values and
feasibility certificates accepted. Three tamper checks and two zero-timeout
checks passed. A further 33-line refutation was accepted and its empty-proof
replacement rejected. Earlier audit evidence is preserved: its failed fixture
incorrectly required rejection of every empty proof, even for unit-inconsistent
base formulas; that was a test error, not a solver failure.

`benchmark.py`: 90 fresh child-process trials, ten fixed synthetic inputs, three
methods, three repeats, cyclic order, sixty-second outer cap. All were OPTIMAL,
each with a checked proof, with identical per-case optimum. Enumeration and DP
baselines solve only the same one-optimum contract, including an exact singleton
shortcut; no baseline counts all solutions. They use a common final certificate
pipeline. Total measured time includes search, formula construction where needed,
proof production and verification, excluding import/serialization. Stage-specific
timing and memory measurements planned earlier are not implemented; no claims
about either are supported. Raw stdout, proof, timings and source digests are in
`benchmark_raw.jsonl`; `audit_raw.jsonl` retains actual audit inputs/results.

| Synthetic case | enumeration seconds | DP seconds | V42 seconds |
|---|---:|---:|---:|
| empty_all_8 | .000254 | .000204 | .000147 |
| all_compatible_10 | .000229 | .000319 | .000193 |
| oneblock_8 | .825698 | .012556 | .001413 |
| ties_8 | .244549 | .053298 | .066464 |
| reverse_9 | .863288 | .045882 | .062735 |
| reverse_10 | 4.926110 | .058919 | .073329 |
| overlap_8 | .290646 | .113649 | .142449 |
| repeated_projections_9 | .000230 | .000310 | .000150 |
| long_words_4 | .001239 | .002192 | .000988 |
| many_words_3 | .004685 | .004904 | .004440 |

These are medians of three, not universal rankings. Tiny timings are especially
sensitive to host noise; no real traces or memory measurement were available.
The encoder is an exact known-style SAT/hypergraph formulation with contracted
mandatory structure, not evidence that no better algorithm can exist. Independent
review, reproducible dependency packaging and larger representative evaluation
remain required before promoting this experimental version.
