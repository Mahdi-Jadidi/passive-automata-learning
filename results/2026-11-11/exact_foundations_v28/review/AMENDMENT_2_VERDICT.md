# Independent witness serialization review — APPROVED

Biggest overlooked point: a witness indexed against deduplicated negatives must not be replayed positionally against a raw list containing duplicates.

The original SPEC explicitly mandates deduplication in first-occurrence order, but did not explicitly define the serialized rejection list and its index domain. The implementation README documented this after the initial approval; it was not itself the original approved specification. The subsequent AMENDMENT_2 makes the serialization explicit; this verdict approves it prospectively, without claiming it was explicit earlier.

`theory/AMENDMENT_2.md` SHA-256: 4C4F81154C3D861859A4F95EC88FCAF7BFC2C5A19F1725615C00D4CB641750C4.
`implementation/reference.py` SHA-256 checked unchanged: 5F60B27447B37EC07F1FD6BCE75BE6199B898573D4B32E90413E900E3A615A94.

The implemented `_normalize` retains the first occurrence of each word separately per label; `_candidate` records the first rejecting block for each normalized negative in order; `_witness` emits each factor's distinct positive projections in first-occurrence order. Hence its lists and indices match amendment 2. Each duplicate raw negative equals a normalized negative, so its projection and rejection are identical. Empty input and zero-factor witness conventions also match. This is a serialization clarification and leaves all reviewed proofs and search logic unchanged. This review is by a coordinated AI agent; it is not a formal proof-assistant verification or independent human proof review.

## Final pseudocode review — APPROVED

PSEUDOCODE_V4.md SHA-256: CBC7DFBEC0089D45C22D550A1649E55C44E7F51858698F471D9214B3693A90D3. Its semantics agree with SPEC and both amendments, and the source algorithm is unchanged from the approved version. Promotion to PSEUDOCODE.md is acceptable only if its bytes have this exact hash. Review is coordinated AI review, not independent human or proof-assistant verification.
