# Exact partition proposals from coverage tables

For a fixed sample D = (S⁺, S⁻), the master proposes a partition P of Σ. The
black box returns `ACCEPT`, `REJECT` with a complete coverage table for each
block, or `INCOMPLETE`. Column i always refers to the original negative trace
yᵢ. Each row is a simultaneous set of rejections by one local language K_B that
accepts the positive projections. Local languages are independent across blocks.

## Turning a rejection into constraints

In the unbounded model, the componentwise OR of the rows of a block table is
itself a feasible row. For each attainable 1, take a local language witnessing
that 1. Their finite intersection is regular, still accepts all positives, and
rejects every negative covered by any of them. If there are no attainable 1s,
the universal language realizes the all-zero row. This argument uses the
problem's language model and does not require knowing how the black box obtained
its tables.

For each column i, keep Zᵢ, the inclusion-maximal observed blocks on which the
column was all zeros. For U in Zᵢ, every nonempty B ⊆ U is also incapable of
covering yᵢ. Indeed, any K_B that rejected yᵢ could be lifted to a regular
language over U by taking the inverse image under the projection from U to B.
It would still accept all positives and reject yᵢ, contradicting the zero on U.

In the next master solve, impose the following for every i:

```text
At least one block B of P must satisfy B ⊄ U for every U in Zᵢ.
```

Each constraint rules out exactly the partitions on which all blocks are known
incapable of covering that negative under these subset deductions. Even columns
covered by the rejected partition can contribute zeros for later rounds. An
unseen block is allowed provisionally if none of the stored regions contains
it. A 1 on a block U also implies possible coverage on supersets of U, but
recording those positives as hard constraints does not shrink this relaxation.

For example, take Σ = {a,b,c,d}, S⁺ = {ab, cd}, and y₁ = ε. If the learned
regions for y₁ include {a,b} and {c,d}, the master needs a block that contains
a symbol from each of those sets. The same stored facts eliminate both the
four-singleton partition and {{a,b},{c,d}}. The partition {{a,c},{b},{d}}
satisfies the new constraint and is confirmed by the black box.

## Exact search and certificate

1. Propose the singleton partition, the initial maximum of |P|.
2. After a complete rejection, add the zero regions from every column. For at
   least one negative all current blocks have zero coverage, since otherwise
   using the simultaneous row at each block would witness acceptance. The new
   constraint for that negative excludes the current proposal.
3. Maximize |P| subject to the accumulated constraints with the SAT partition
   master. A new proposal may reorganize the whole alphabet.
4. Every compatible partition survives every round. The first accepted proposal
   is feasible and reaches the best remaining upper bound, so it is globally
   optimal. If the relaxation becomes unsatisfiable, the sample is infeasible.
   There are finitely many partitions and each rejection removes at least one.

The prototype returns `table_feedback_drup`. Its independent verifier checks
every zero region directly against D, checks the final partition against D if
one was returned, and checks the DRUP refutation of the relaxation at |P| + 1
(or at threshold 0 for infeasibility). Only this verifier uses projections.
An interrupted run returns `INCOMPLETE` with no feasibility or optimum claim.
There is no polynomial-time or runtime improvement claim for the whole search.
The Windows Glucose backend hit a proof-file error when repeatedly opening
hundreds of native proof sessions in one process. The prototype uses an empty
proof whenever unit propagation suffices and reports a native SAT error as
`INCOMPLETE`.

## Prototype interface

`implementation.table_feedback_master.solve_optimal(D, teacher, limits=None)`
uses the existing SAT partition encoding and requires `python-sat`. The caller
binds `teacher(blocks, tick)` to D. On rejection, `verdict['tables']` is a
mapping from a tuple of symbols in a proposed block to a list or tuple of binary
rows. The column order is exactly `D['negative']`, including duplicate traces.
`verify_optimal(D, result, limits=None)` checks the certificate without a teacher
or a SAT solver. V47's public interface returns the verdict only. The prototype
is ready to accept the table-producing callback described here.

Arbitrary table families without a feasible componentwise OR require a
different master relaxation. For example, rows `10` and `01` alone do not cover
both columns with a single block. One must then encode a choice of one row per
selected known block, and any cross-block deductions need their own justification.
