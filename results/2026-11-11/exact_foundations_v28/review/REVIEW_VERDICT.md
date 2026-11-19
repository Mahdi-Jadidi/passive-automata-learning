# C028 independent proof gate — APPROVED v1

Biggest overlooked point: exact sample compatibility and an optimal recommendation do not, without additional assumptions, identify the physical ownership partition or true factor count.

Reviewed source SHA-256 (raw bytes):
- `theory/SPEC.md`: C42EEDB77EE7F78AA0303FC4D568B73F24C547CFBF82A8A615688FFFB067D669
- `theory/PROOFS.md`: 96AFDE6CC60C51B2F247EA19F5CE4F9BA2131B05C6A65567FB927D1CA57392CB

The reference algorithm is approved for implementation against these exact files; changes require review against new hashes. This verdict does not certify code or experiments.

Independent checks:
1. Necessity and sufficiency use the correct quantifier order: for each negative, some one block must distinguish it from every positive. The finite projected-positive factors prove sufficiency, including empty P and unused IDs; no bounded-state, prefix-closed, physical factor or K premise is smuggled in.
2. Input order fixes canonical RGS labels. The first-occurrence bijection covers each partition exactly once, including the single empty RGS. Enumeration in ascending label order is lexicographic.
3. The candidate and count invariants give exact compatible and optimal counts, distinguish their uniqueness notions, and retain canonical optimum plus two witnesses when present. Reset on an improved maximum is essential.
4. For empty alphabet the empty conjunction accepts epsilon. It yields one compatible empty partition exactly when N is empty. All incompatible and contradictory cases avoid a fabricated optimum.
5. Any finite valid input implies finitely many candidates and finite word-projection comparisons. This is mathematical termination with unbounded resources, not a deadline or practical storage guarantee. INVALID_INPUT and INCOMPLETE do not assert counts; a completed contradiction proof may soundly conclude INCOMPATIBLE.
6. The physical counterexample is correct: one universal factor on {a,b} and two universal singleton factors yield the same complete language. Unused IDs can likewise be separated in a recommendation without proving physical ownership.

Independently replayed paper examples: for P={a,b}, N={ab}, singleton projections each match one of the positives, so only the oneblock partition rejects the negative. For P={epsilon}, N={a}, both ab and a|b fit but the two-block optimum alone is maximal. These expose the quantifier and uniqueness errors, respectively.

No proof defect requiring repair found. Implementation must still independently replay all output witnesses and be tested by the designated independent auditor after source freeze.

## Amendment 1 re-review — APPROVED v2

Original SPEC and PROOFS hashes above remain unchanged. AMENDMENT_1.md SHA-256: 6A6004B9A8BBCA4C120DC03F25CB2310CE5E570DE4FD25C60F7D0401910C9193. It requires the exact serialized keys `alphabet`, `positive`, `negative`, while retaining arbitrary atomic nonempty string IDs, array-valued words, whole-record validation, and the existing mathematical proofs. ERROR on failed witness replay is a nonclaim with null mathematical fields. INCOMPLETE and INVALID_INPUT likewise give no mathematical result. This amendment introduces no proof defect. Approval covers the original files together with amendment 1; no source code was written before this re-review.

## Pseudocode review — APPROVED

PSEUDOCODE_V2.md SHA-256: 3DE99EC294A4AA8DAE48A0733548B807CE0F9E9372CA3451E859E4F6A486AA42. It agrees with the amended single-record schema, exhaustive RGS/projection test, exact counters, tie reset, canonical selection, failure and interruption policy. Recursion is conceptual; an implementation may generate the same RGS sequence iteratively to avoid host recursion limits. This review certifies the pseudocode's correspondence to the mathematical procedure, not the implementation or measured experiments.
