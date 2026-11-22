# Handoff for the coverage table partition master

Continue on `codex/v47-polynomial-teacher`. The V47 reference immediately before
this work is `7f327fb181f0269953b8385440a40060601c1ccf`. The frozen V46 reference
is tag `v46` at `bc915ffd5e591202b0ab8ffd55342a004c791138`. Read
[AGENTS.md](AGENTS.md), [the notation map](docs/ALGORITHM_NOTATION.md), and
[the master contract and proof](docs/TABLE_FEEDBACK_MASTER.md) first. The
[V47 checkpoint](CHECKPOINT_V47.md) and [V47 black box summary](docs/V47_BLACK_BOX_HANDOFF.md)
provide background on the earlier decision-only interface.

## Current scope

Given D = (S⁺, S⁻) over declared Σ, return one compatible alphabet partition P
with the maximum number of blocks and a checkable certificate. Work on the
outer proposal algorithm. Treat the teacher as a black box. Keep the unbounded
local-language model and exact optimization. `INCOMPLETE` makes no feasibility
or optimality claim and provides no feedback for a new cut.

## What is available

- The [prototype](implementation/table_feedback_master.py) accepts an injected
  `teacher(blocks, tick)` bound to D. After `REJECT`, it receives one complete
  table per proposed block. Rows are simultaneous coverage patterns, with a 1
  meaning rejection of the corresponding negative trace. Preserve original
  negative-column order, including duplicate traces. V47's public interface
  supplies the verdict only. The prototype was exercised with a simulated
  table-producing callback.
- In the unbounded model, the bitwise OR of a block's rows is attainable by
  intersecting local languages. An all-zero column on U implies that every
  subset of U also fails to cover that negative. The master accumulates the
  inclusion-maximal observed zero regions for each column. For each negative,
  it requires a block that is contained in none of that column's zero regions.
  The constraint preserves every compatible partition. A complete rejection
  eliminates the current proposal, and the SAT master selects a maximum-block
  proposal under the accumulated constraints. The first accepted proposal is
  globally optimal.
- `table_feedback_drup` is the prototype's certificate type. Its verifier
  checks zero regions and final feasibility against D and replays a DRUP
  refutation of the bound. The proposal loop uses the teacher tables to learn
  its cuts. Existing V47 certificates and files are historical references.

## Validation and next work

The prototype matched exhaustive partition search on 2,217 exhaustive sample
labelings over alphabets of size at most two and 300 seeded samples over three
to six symbols. Four clique instances, K4 through K7, produced nonempty SAT
proofs accepted by the verifier. Checks also covered duplicate columns, altered
certificates, interrupted runs and invalid simultaneous-row feedback. These
were local development checks with a simulated callback. The Windows Glucose
backend failed to open a proof file after hundreds of native proof sessions in
one process. The prototype uses unit propagation when sufficient and maps a
native SAT error to `INCOMPLETE`.

1. Connect the master to the supplied table-returning teacher through its public
   contract. Target the master-side integration and preserve the teacher's
   implementation. Confirm column order, complete `REJECT` replies and
   propagation of `INCOMPLETE` on the real interface.
2. Save a reproducible comparison of the outer search against a reference that
   excludes each rejected partition individually. Use identical teacher,
   inputs, budgets and certificate criteria. Record proposal counts and time
   for teacher calls, master search, and proof generation and replay. Report
   completed and incomplete cases separately. No runtime improvement has been
   established.
