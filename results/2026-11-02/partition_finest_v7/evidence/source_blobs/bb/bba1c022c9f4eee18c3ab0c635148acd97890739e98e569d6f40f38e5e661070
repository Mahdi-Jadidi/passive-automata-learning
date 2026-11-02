# C007 staged exact swap preprocessing — v4 protocol

## Scope

`finest_solver_v4.py` is a new immutable candidate derived from v3. In adaptive
mode it first derives exact must-link edges only from equal-length positive /
negative pairs differing by one adjacent transposition. If the resulting
components are directly sample-compatible, it returns the certified unique
finest partition. Otherwise it invokes the unchanged full v3 graph and
separator path. Reference mode bypasses staging. No heuristic or assumption
change is introduced.

The proof rule is exact: if a positive word and a negative word differ only by
reversing adjacent distinct symbols `a,b`, then a partition that separates
`a,b` gives the two words identical projection in every factor. Such a
partition cannot reject that negative word. Hence every compatible factor
partition keeps `a,b` together. The component partition is therefore a
coarsest forced grouping; when it passes the direct compatibility test, every
compatible partition refines it and it is the unique finest answer. Failure
of the direct test yields no conclusion and triggers the complete v3 path.

## Frozen predecessor and source isolation

v3 (`finest_solver_v3.py`, SHA-256
`c783929cc75b0979cab679f82c0e43e3aceab014db0b2d063628d0302b33477a`) and its
v1 CLI/readiness remain unchanged. v4 is additive. The parent C006 provider
and C005 graph helper are loaded from their previously frozen paths and hashes
are checked by the solver. No dependencies are installed.

## Correctness gate

Run `smoke_v4.py` in a fresh process. It compares adaptive and reference v4
against an independent restricted-growth-string enumeration of every set
partition on eight fixed small labeled samples. It checks the whole meet,
status, maximal-refinement multiplicity, and proof replay. Cases exercise a
three-block finest partition, multiple maximal refinements, one-block-only,
empty bipartition family, positive-only, negative-only, epsilon/unused symbol,
and a direct swap-stage success. It additionally checks edge recognition for
exact adjacent reversal versus nonadjacent / multiple mismatches, interrupted
fallback behavior, contradictory labels, and rejection of unknown `k`.

This is a smoke gate, not the independent 218-input audit. The auditor must
regate the frozen corpus with both modes after the provider hash is shared.
No timing claim is made from this gate.

## Authorized scale follow-up

The only new scale cell authorized for v4 is the exact historical input
`audit/scale_v1/cli_inputs/scale_m16_len65536.json`, previously censored in the
v3 scale campaign. Capture timeout remains the historical 30 seconds. This
single cell is exploratory evidence about the proposed swap-stage shortcut,
not an official timing comparison or a substitute for the correctness audit.
No other performance runs are authorized in this branch.
