# Static peer review of structural S001

**Review ID:** C004-G-PEER-001  
**Review type:** read-only proof/code inspection; no provider execution or new experiment  
**Scientific status:** no blocking soundness defect found in the reviewed S001 certificate argument; deadline granularity and complexity wording need to remain qualified  
**Scope:** `structural/singleton_solver_v1.py`, `structural/PROOFS_S001.md`, and the prepared theory in `structural/PROOFS_S002_PREPARED.md`. This does not review the S002 implementation or constitute independent execution/audit acceptance.

## Frozen source identities

| File | SHA-256 |
|---|---|
| `structural/singleton_solver_v1.py` | `16065fdfabf52d4280e3c0f5a7f427aff8990583579bd97b4ea64f70c5a023e` |
| `structural/PROOFS_S001.md` | `437167d2c294ef3c4ef13f2be8c3daafc4cd0c7dfd1ff0156ac738270ae9f1d84` |
| `structural/PROOFS_S002_PREPARED.md` | `ed5f40f67815420cb0ea4bd1ca633513dae77bd5ceacd4ee13eb91a0ef0f1273` |

## S001 proof/code findings

### 1. Count and pair-projection characterization

For singleton local factors, every positive must have the same count of each symbol as the reference positive; `validate` plus the per-symbol `projections` check catches any count mismatch before graph construction. Given count agreement, an opposition edge for `{a,b}` means some positive has a different binary projection from the reference. The two symbols cannot belong to one singleton factor in any compatible partition, so every compatible partition is a proper coloring of the opposition graph. Because blocks are required nonempty and exactly k, the coloring is surjective.

Conversely, if a block contains no opposition edge, every same-symbol occurrence has the same rank/order across positives by count agreement. For every pair of distinct symbols in that block, the binary projection fixes the relative order of all their occurrences. Hence the complete occurrence order, and therefore the block projection, is identical in every positive. This proves the other direction: positive-compatible partitions are exactly the proper surjective k-colorings. The code constructs pair projections by preserving word order and uses the full positive projections again before returning a candidate.

### 2. Arbitrary-k certificate boundary

The complete-k-partite check is correctly stronger than merely finding k connected components: the code verifies every symbol pair against the proposed parts. In a complete k-partite opposition graph, one representative from each part forces k distinct colors; every remaining vertex is adjacent to representatives of all other parts and must use its own part’s color. Thus the unordered partition is unique for arbitrary k, including k=1.

The connected-bipartite shortcut is guarded by `k == 2`; it is not extended to k>=3. This matches the proof’s scope and avoids treating connectedness as a general coloring-uniqueness certificate. When neither certificate applies, `insufficient_coverage` is the right status: it does not claim infeasibility or ambiguity.

### 3. Empty-positive semantics

`positive == []` returns `insufficient_coverage` before choosing a reference local word. This is necessary for the singleton-exactly-one model: no observed positive determines the local words. The distinction from a nonempty positive sample containing only `""` is respected; the latter has a real reference word and may determine epsilon projections. The code does not equate “no observed local projection” with an observed epsilon projection.

### 4. Negative checking and result status

For a certified candidate, the code computes every negative’s local projections and accepts the negative iff every projection equals its unique local word. Returning a witness for any differing block is sound. If all blocks match, `unique_candidate_accepts_negative` eliminates the only positive-compatible partition in this class, so the infeasibility claim is class-conditional and valid. Unsupported certificate and empty-positive outcomes remain unresolved; a deadline becomes `incomplete` and does not assert uniqueness or exhaustion.

## Deadline and complexity qualifications

Deadline checks appear in word validation, projection scans, pair bucket construction, pair comparisons, graph traversal, and candidate checks. Some operations are still coarse-grained: sorting/deduplicating sample lists; constructing the all-pairs list and bucket dictionaries; sorting/filtering `remaining` inside each complement-BFS iteration; and the inner pair loop in the final complete-multipartite verification (which checks once per outer symbol). These are bounded for the stated small alphabet tiers, but a very large alphabet or sample collection can delay cooperative deadline recognition. A hard subprocess capture timeout remains appropriate.

The pair bucket extraction bound in S001 is consistent with the code: each letter is appended to its m−1 incident pair buckets, giving O(mL) character appends and O(m²) pair setup/comparison per word. One additional bound should be stated for the implemented certificate path: complement BFS repeatedly sorts the remaining symbols, so its straightforward worst-case bound includes O(m² log m) sorting work (plus O(m²) membership scans), rather than only the final O(m²) pair verification. This does not affect correctness.

## Prepared S002 proof review

The prepared known-k relaxation is consistent with S001: enumerating restricted-growth strings over sorted symbols gives one canonical representation per unordered partition, opposition-edge checks enforce proper colorings, and direct full positive/negative checks define the singleton feasibility predicate. Exhaustion is required for uniqueness/infeasibility; a limit or timeout is unresolved.

The prepared unknown-k certificate is also sound as stated: a positive/negative adjacent transposition `xaby` / `xbay` forces a,b together in any disjoint-alphabet product because separating them makes every factor projection equal. Transitive closure therefore gives must-link components. If an opposition edge lies within one such component, the singleton class is infeasible. If the quotient opposition graph is a clique, every component must occupy a distinct block, and no additional nonempty block is possible; direct language checks are still necessary. These are sufficient certificates, not completeness claims. This review did not inspect or run the S002 provider.

## Conclusion

No blocking mathematical or semantic defect was found in the reviewed S001 source/proof. Retain the stated class boundary, “insufficient coverage” semantics, and the caveat that cooperative deadlines can be recognized only between coarse built-in operations. The separate V1 source and proof files were not edited.
