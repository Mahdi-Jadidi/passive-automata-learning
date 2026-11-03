# Counterexample v1 clarification: first failing pair row

The main counterexample uses the `(b,c)` pair row to show that its aggregate
different count can be positive while no different witness exists at k=1.
That is a row-local derivation, not the first row the implementation would
process.

With alphabetical symbol-pair ordering, the actual first failure is `(a,b)`:
the k=1 partition `{abc}` witnesses `a,b` same, while a different `a,b`
witness exists only at k=2 (`{ac}|{b}`). Therefore the old code would call
`find_partition(k=1, a, b, False)`, obtain `None`, and pass it to
`intern_partition` before it reaches the `(b,c)` row. The candidate v3 guard
fixes both row-local cases symmetrically. This clarification does not change
the input, hand-derived partition family, code delta, or any runtime status.
