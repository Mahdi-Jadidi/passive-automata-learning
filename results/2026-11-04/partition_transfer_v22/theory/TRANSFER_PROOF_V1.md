# C022: exact transfer of a validated atom witness to a coarsening

This round contains one candidate. It changes only the `compatible_forced_atoms` ambiguity route of frozen C020 C2. It introduces no new heuristic, generator, data assumption, or search pruning. No timing or solver execution has been performed by the implementer. Syntax was checked with `ast.parse`.

## Contract and theorem

Let A=(A_0,...,A_{r-1}) be the nonempty, pairwise disjoint forced atoms covering the declared alphabet. Let W be the **already successfully validated** `atom_witness`. For each negative word n, W supplies an index j(n) such that

    pi_{A_j(n)}(n) not in {pi_{A_j(n)}(p): p in P}.

Let C=(C_0,...,C_{k-1}) be a partition constructed by `coarsenings(atoms, known_k)`. Each atom lies wholly within exactly one C_i. Denote this containment map by f(j). Transfer the rejection for n to block f(j(n)). Keep the local-language rule `positive_projections_from_input`, now interpreted on C.

**Claim.** The transferred certificate is a valid witness for C.

**Proof.** Suppose its rejection of n were invalid. Then for some positive p,

    pi_{C_f(j(n))}(n) = pi_{C_f(j(n))}(p).

Because A_j(n) is a subset of this C block, projection again onto A_j(n) gives

    pi_{A_j(n)}(n) = pi_{A_j(n)}(p),

contradicting W. Thus the transferred block rejects n against **every** positive. Every positive is accepted by each local finite language of positive projections. Those languages are regular, so C is compatible under the same unrestricted regular-factor model. The proof applies to every n; it does not exchange the quantifiers exists-block and for-every-positive. Empty-word projections and declared but unseen symbols require no exception. ∎

This is the existing coarsening-monotonicity argument applied to certificate construction, rather than replaying projections to rediscover a rejecting block. It is not a new identifiability theorem or an established novelty claim relative to the literature.

## Scope of behavioral equivalence

The branch is reachable only after the original validation, contradiction checks, unary shortcut, graph construction, atom-count checks, and successful exact atom feasibility check. The unique return when `r == 1` or `known_k == r` is unchanged. The unary route is unchanged. If atoms are incompatible, the original count rejection or exact DFS follows unchanged. The DFS, cache capacity of 4096, projection implementation, schema, CLI, and resource-interruption exception handling are unchanged.

For completed, resource-unlimited computations, the status, constructive alternative partitions, family of compatible partitions, forced atoms, and swap forest are unchanged. The chosen rejecting block for a negative may differ: baseline replay selected the first rejecting output block, while transfer chooses the block containing the rejecting atom stored by W. Both are exact. `METHOD` changes to identify C022. `complete_candidates` still counts the atom witness and two constructive alternatives, as before. Projection/cache counters and cache contents may differ; fewer projections are the intended mechanism. Other than `METHOD`, unique and unary output logic is untouched.

With a deadline, completion or interruption can occur at different times. We claim no equality of interrupted counters or of deadline-limited statuses. `unresolved` remains computation-incomplete, never a certificate of ambiguity or incompatibility. Existing cooperative polling remains; added symbol mapping and rejection transfer loops also poll. Memory allocation and the original native operations retain cooperative-budget limitations.

The runtime assertion checks that each atom is wholly assigned to one output block. Completeness and disjointness of the output partition follow from the unchanged internal `coarsenings` constructor; this helper does not accept arbitrary external partitions. Every rejection index comes from the previously validated atom witness, and rejection order is preserved.

## Cost and limits

For each of the two alternatives, constructing symbol ownership and checking atom containment costs O(m); transferring rejection records costs O(|N|). Thus added certificate work is O(m+|N|) per alternative, apart from integer sizes and ordinary allocation costs. It does not scan the input words or call `reject` again. The original atom feasibility check still scans projections and is indispensable.

Baseline replay sometimes hits the existing cache, so no unconditional runtime or memory improvement is claimed. The transferred route avoids new projections for merged masks that would have missed that cache. There is no claimed gain in unique routes, unary routes, or DFS routes. The Bell/Stirling candidate space and worst-case combinatorial search remain unchanged. Timing and independent certificate replay are pending separate audit.

## Existing evidence and code

- Mathematical model, compatibility criterion, and coarsening family: `results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md`, especially T3.
- Compatibility and quantifier guard: `results/2026-11-04/preflight_certificates_v19/theory/GRAPH_CERTIFICATE_LIMITS_v1.md`.
- Frozen parent: `results/2026-11-04/scaling_v20/implementation/candidate_c2_v1/gate_v1.py`, SHA256 `5331a1787a9ff74afe1afcbea1668dbe9ee69ef1f7121fec14c7281caa2d8680`.
- Candidate: `../implementation/candidate_transfer_v1/gate_v1.py`.
- Exact delta: `../implementation/TRANSFER_C2_DELTA_V1.patch`.
