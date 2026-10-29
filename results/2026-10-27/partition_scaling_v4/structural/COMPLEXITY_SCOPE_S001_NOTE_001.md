# Scope qualification for S001 complexity

Date 2026-10-27. Status: static peer-review clarification, no provider execution and no frozen source edits. Parent: S001 v1. This note qualifies interpretation of earlier proof/report wording; it does not replace or alter that preserved evidence.

The O(mL+m²) claim in PROOFS_S001.md applies specifically to all-pair projection extraction for one word: incidence construction/bucket setup is O(m²), each letter is appended m-1 times, and joining/comparing all pair projections costs O(mL+m²). For P positive words this phase is O(P*m² + m*sum_positive_length), with reference/current projection storage O(mL+m²) per word length bound L. Whole input validation, sorting/deduplication, graph certificate construction, candidate projection, witness materialization and output serialization are separate costs.

The implemented complete-multipartite certificate finder repeatedly sorts the remaining symbols during complement BFS. A direct worst-case upper bound includes O(m² log m) sorting work plus O(m²) complement membership scans/final pair validation. Thus the implementation does not establish an overall solver bound of O(mL+m²). At m<=128 this can be modest in practice, but only measured data can establish its actual contribution. The shortcut is mathematically sound; this is a runtime-scope qualification.

Sorting/deduplicating the positive/negative sample lists and sorting strings can also depend on total sample length and shared prefixes. Large solution/witness output carries its own unavoidable materialization/serialization cost. Deadline checks occur between coarse Python operations, and external capture enforces a hard timeout. No asymptotic statement here claims a strict cooperative wall-clock deadline bound.
