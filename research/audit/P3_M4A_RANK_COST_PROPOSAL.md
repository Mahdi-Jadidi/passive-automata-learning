# RANK_COST proposal, version 1

This proposal is for review. The frontier v1/v2 schemas and their leaf rules stay frozen. The offline prototype consumes checked scope inputs and has no frontier registration path.

Proposed closure payload for a future versioned frontier envelope:

```json
{
  "reason": "RANK_COST",
  "version": "p3-rank-cost/v1",
  "packings": [
    {
      "negative_id": "N0",
      "deletions": [
        {"positive_id": "P0", "support": [0]},
        {"positive_id": "P1", "support": [3]}
      ],
      "weight": [1, 1]
    }
  ]
}
```

1. Replay the original raw and journal/2 bytes and reconstruct the current region from the checked path. Let `E` be its equality relation, `V` its canonical class minima, and `b = n - |V|`. Use the enclosing scope's stable raw positive and negative indexes. Infer all other quantities from checked data.
2. Require exactly the displayed fields, strict JSON integers (excluding booleans) for supports and rational components, valid canonical trace IDs, and nonempty strictly ascending support lists of current representatives. Each support deletes entire current E-classes. Independently compare the ordered original-token residues of the row's negative and the named positive for each deletion. Every comparison must be equal. Different positive IDs are allowed in the same row. Supports are pairwise disjoint within the row after quotient mapping.
3. A valid separating block must hit each deletion support. Missing any support would make the block's negative projection equal to its named positive projection. In the union S of q disjoint supports, this block contains at least q atoms. Thus the rank of the completion restricted to S is at least q-1. Ignoring disequalities in the rank argument preserves validity. Recompute supports and this floor using the current E; descendant contractions can destroy disjointness. Intersecting a deletion with a smaller set requires a fresh exact deletion check.
4. Parse each weight as a reduced fraction with nonnegative numerator and positive denominator. Sum weights for every atom in every row's support union, including repeated rows. Require each load <= 1. For each completion block, choose an anchor. Its contribution to every restricted rank is at most the number of its nonanchor vertices in that support. The capacity inequalities give an upper bound of one per nonanchor vertex on the sum of weighted restricted ranks. Hence the absolute cost floor is `L = b + ceil(sum(weight * (q - 1)))`. Use exact integer/rational arithmetic throughout. Each row alone also provides a local floor. This contract checks a supplied packing and needs no optimization result.
5. Bind to the enclosing expected mode and format. Verify a compatible, cost-checked incumbent for the same raw/journal scope. Permit this closure with `L >= U` in one mode and `L > U` in all mode. With no verified incumbent, the closure is invalid. The schema provides a finite floor only. A feasible transversal gives an upper bound on minimum hitting set size, so it supplies no floor.

## Limits

Require a maximum of 128 packing rows, 2–64 deletions per row, and at most 4,096 representatives per deletion. Cap the total number of support and deletion entries at 2,000,000 across rank closures and the sum of their serialized payload bytes at 64 MiB, further bounded by the enclosing proof cap. Both rational input components have at most 32 bits; reject oversize integer text before conversion. At most 128 input denominators participate in each load and in the weighted objective, bounding unreduced denominator products by 4,096 bits. Allow up to 4,112 bits for the associated numerators and final intermediates. Charge trace scans, exact comparisons, support entries, and rational operations against shared work and elapsed time budgets. A practical verifier can charge rational operations by operand bit lengths and check the deadline before and after bounded big-integer operations. Numeric and structural violations invalidate a proof. Runtime exhaustion yields an incomplete replay with no certified result. A memory cap on the replay process is complementary to these input and work caps.

The Python prototype accepts original symbol IDs and expands their classes through the owner table. The proposed wire uses canonical representatives to simplify parsing and reject stale class IDs. The prototype exercises the theorem and cooperative checks; the JSON parser, cumulative closure admission, and integration into a future frontier version require separate review.
