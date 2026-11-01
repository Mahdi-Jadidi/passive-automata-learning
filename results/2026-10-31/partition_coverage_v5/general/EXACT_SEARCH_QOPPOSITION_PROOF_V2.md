# q-aware exact search v2 proof and API erratum

## Provider and review

The frozen provider is `known_k_qexact_v2.py`, SHA256 `9f08dd645e7fcccbe8ea8022c758b7cf3277a5f01b6533fb9c1ad0cf08b6c84d`. API:

```text
solve(data, *, k=None, local_word_cap=None, deadline=None,
      max_solutions=None, use_q_opposition=True,
      use_contextual_must_links=True)
```

The deadline is a finite non-boolean numeric absolute `time.perf_counter()` value. `None` means no deadline. `max_solutions=None` exhaustively enumerates all compatible partitions. The provider is stdlib-only. The structural worker's read-only review is in `../structural/PEER_REVIEW_EXACT_V2.md`; it found no mathematical pruning or enumeration blocker, subject to the independent full-set audit.

## Proofs carried forward

- Contextual swap and insertion-rescue must-link proofs are in the immutable parent artifact [contextual_swap_proof.md](../../../2026-10-27/partition_scaling_v4/general/contextual_swap_proof.md). Candidate hashing is only an index; exact string equality guards collisions.
- For q-opposition, if symbols `a,b` share block B, every positive projection onto `{a,b}` is the projection of `pi_B(p)`. The former projection set is an image of the latter and cannot have larger cardinality. Therefore `|{pi_{a,b}(p):p in P}| > q` soundly separates `a,b`. Likewise `|{pi_a(p):p in P}| > q` is globally infeasible, because every symbol has an owner block.
- A partial block's distinct positive projections cannot merge when the block grows: projecting both new projections back to the old block recovers the old distinct strings. Pruning a partial block already over q therefore loses no q-feasible partition.
- Must-link components are the indivisible atoms. Fixed-order restricted-growth assignment (first atom color 0; later atoms use an existing color or the next unused color) yields exactly one representative for each unordered k-way partition. A q-cannot-link only prunes equal colors. A leaf directly computes complete positive projection sets and verifies every negative has an unseen block projection.

The direct check is the semantic gate. Pair constraints never stand in for full-block cardinality or negative rejection. Empty positive sets and absent alphabet symbols follow the at-most-q finite-language convention: empty languages are allowed, empty-set projections are counted as ordinary strings, and unsupported symbols remain in the partition.

## API and status erratum versus v1

V1 is retained unchanged. Its first immediate deadline interrupted before `unary_conflicts` was initialized, so its return path raised `UnboundLocalError`. The preserved failure is captured at `../evidence/attempts/20261031T064047.799924Z_bc22f2153e`; the v1 hash and defect are recorded in `V1_REVIEW_NOTE.md`. V2 initializes output state before any interruptible operation and rejects non-finite or boolean deadlines.

V2 defines `complete` and `enumeration_complete` as search exhaustion, separate from `decision_complete` (existence is decided as soon as one valid partition is found). A found partition with pending work has `status=found`, `complete=false`, and `uniqueness=unknown`. `uniqueness=unique` requires exhaustion with one solution; two solutions establish `ambiguous` even if enumeration is incomplete. An interruption always has `status=incomplete`, `complete=false`, and `search_exhausted=false`. No program exception is translated into infeasibility.

## Semantic boundaries

With finite q, the class is finite local projection languages containing at most q strings. With q omitted, exact search uses unrestricted regular factors and the observed positive projection sets as finite regular witnesses; this is sample compatibility, not hidden-factor identification. Uniqueness refers only to the complete set of sample-feasible unordered partitions under known k. Unknown-k identifiability is outside scope. Noise, shared symbols across factors, and prefix semantics are not implemented.
