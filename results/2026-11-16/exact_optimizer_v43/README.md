# V43 — exact optimization of |P| from D=(S⁺,S⁻)

The current objective is ONE sample-compatible alphabet partition with the
maximum number of devices and a checkable optimum certificate. There is no DFA
state bound, no DFA inference and no requirement to count all solutions.
Naming follows `docs/ALGORITHM_NOTATION.md`, based on the user's manuscript.
Mandatory atoms are not inferred physical devices. Historical files are frozen.

## API

Put this folder on the Python module path and run:

```python
from optimizer import solve_optimal, solve_profiled
from verify import verify_optimal
D = {'alphabet':['a','b','c'],
     'positive':[[],['a','b','c']], 'negative':[['a']]}
result = solve_optimal(D, {'timeout_seconds':60})
assert verify_optimal(D, result, {'timeout_seconds':60}) == {'status':'ACCEPT'}
```

The Python wire keys alphabet/positive/negative alias Σ/S⁺/S⁻. Result keys
status/blocks/max_devices/certificate are preserved from V42. OPTIMAL contains
P and k=|P|; ties are arbitrary and display order follows declared Σ. INFEASIBLE
has a direct contradiction or empty-alphabet proof. INVALID_INPUT and INCOMPLETE
have null mathematical fields. `limits=None` has no explicit deadline; the only
option is finite nonnegative timeout_seconds. Python stages use cooperative
checks, native SAT is interruptible, hard termination can produce no response.
No candidate-prefix budget is claimed. `solve_profiled` returns result and
separate metrics; incomplete metrics may not account for an interrupted phase.

Uses the existing local python-sat 1.9.dev22 / Glucose3 `g3`, six 1.17.0, under
results/2026-11-14/sat_candidate_v37/vendor. Tested on Windows CPython 3.12.14;
the installed native binaries are specific to that platform. It does not import
any old partition solving backend. A fresh assumption-free SAT call is used
only when a refutation is needed. The checker imports no SAT solver or optimizer,
but shares the deterministic encoding module, which is part of the trusted base.
This is algorithm/backend independence, not an independent author/peer review.

## Exact routes and elimination of repeated work

1. Normalize D and validate all IDs before contradiction checks. Test the
   singleton partition using a per-call rejection cache.
2. Derive mandatory atoms. If their own partition fits, return it with the
   attained atom-count upper bound, without mining or constructing SAT.
3. With one negative y₁, find a smallest rejecting atom set of size d by
   cardinality-ordered subset search. Merge it and keep all other atoms separate;
   k=q-d+1 is provably maximum. No SAT or all-minimal-set enumeration is used.
4. For multiple negatives, enumerate minimal rejecting witnesses W_i using
   antichains of maximal unexplored regions. A false region excludes all its
   subsets; a known witness T splits a region into the exclusions U\{a}, a∈T.
   This replaces the old loop over every subset. Worst-case exponential work
   remains possible. Each original symbol mask is evaluated once per solve;
   its rejection bitmask is shared across all negatives and search stages.
5. Encode same-device equivalence, witness containment, Q_i obligations and
   representative count. Tighten the device bound using witness cardinality.
   Reuse one CDCL session and learned clauses across threshold queries.
6. Check the output on D. Self-check any DRUP proof against the already built
   formula instead of rebuilding that formula internally. External consumers
   independently reconstruct it from D. Indexed RUP propagation reuses clause
   occurrence lists rather than repeatedly scanning all clauses per unit.

These are exact reductions with a general exact continuation, not approximate
answers selected by scores. The mathematical arguments and bounds are in
PROOF.md; independent source/proof review is still pending. There is no claim
of universal fastest performance or established scientific novelty.

## Validation, history and reproducibility

`audit.py` passed 2261 oracle optimum/certificate checks and compared every
extracted W_i with the old exhaustive subset implementation. Includes 2187
distinct two-symbol labelings, empty inputs, the fixed ten cases and 60 seeded
three-to-five-symbol cases. Three proof/output tamper and two zero-limit checks
passed. `audit_boundaries.py` passed 14 schema, Unicode, unused-ID, validation-order,
false-bound and rebinding checks. `audit_mining.py` checked all 167 antichains
of nonempty subsets on four atoms. `audit_propagation.py` matched indexed/scanning
RUP on 4000 seeded comparisons. `audit_legacy_proofs.py` replayed three new DRUP
traces using V42's separate process, old exhaustive encoder and scanning checker.
These are bounded falsification tests; no formal software correctness claim.

Final raw correctness and benchmark files are audit_raw.jsonl and
benchmark_raw.jsonl. Earlier pre-indexing and pre-single-negative runs are
retained under their descriptive filenames; previous checker and optimizer
sources are in history/. A harness indentation issue was fixed before the first
V43 audit data were generated; it was not an algorithm failure. Do not merge
or overwrite runs. `summarize.py` rechecks frozen source hashes, trial identities,
all verifier statuses and common optimum values and recomputes the summaries.

Final benchmark: same one-optimum-plus-checked-certificate contract for
enumeration, DP, V42 and V43; ten fixed synthetic inputs, three fresh processes
per method/case, cyclic order, 60-second outer watchdog. All 120 were OPTIMAL
with accepted certificates and matching optimum per case. Measurements separate
solver pipeline time, external verification, startup wall, and V43 phase counters.
Windows PeakWorkingSetSize includes Python, native SAT and imports; it is total
process peak, not isolated algorithm allocation. See REPORT_FA.md for results.

Run audits only in a fresh copy/output location or preserve the existing logs;
scripts refuse to overwrite evidence. No public entrypoint, publication, commit
or push was changed. Next acceptance work is independent proof/code review and
representative real-input evaluation; heuristic/approximation research remains
a separate later phase.
