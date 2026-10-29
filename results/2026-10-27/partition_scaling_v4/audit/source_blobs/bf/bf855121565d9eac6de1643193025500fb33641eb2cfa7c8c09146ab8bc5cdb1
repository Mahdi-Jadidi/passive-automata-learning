# General known-k proof notes

## Adjacent-swap must-link (regular factors, any k)

Let a negative word be `n = u b a v` and a positive word be `p = u a b v`,
where `a != b` and the displayed pair is adjacent. Suppose `a` and `b` are
assigned to different alphabet blocks. For each block `B`, projection erases
symbols outside `B` while preserving order. If `a` is in `B` and `b` is not,
then both projections are `pi_B(u) a pi_B(v)`. If `b` is in `B` and `a` is
not, both are `pi_B(u) b pi_B(v)`. For any other block, both are
`pi_B(u) pi_B(v)`. Thus `pi_B(n) = pi_B(p)` for every one of the k blocks.

Since `p` is positive, every local factor must accept `pi_B(p)`. Equality
therefore makes every factor accept the corresponding projection of `n`, so
the product accepts `n`, contradicting its negative label. Hence `a` and `b`
must be in the same block. The argument is independent of k and works with
unrestricted regular local languages and with any finite-language cap that
contains all observed positive projections.

This is a contextual family: `u` and `v` may both be nonempty and may have any
length or symbols from the known alphabet. There is no dependency on an empty
positive word or a short whole trace. The witness itself is local (one
adjacent transposition); longer contexts do not change the equality proof.

## Insertion-rescue must-link (regular factors, any k)

Let negative `n = x a y` have positive base `p0 = x y` and positive rescue
`p1 = x a b y` or `x b a y`, with `a != b`. Suppose `a` and `b` are assigned
to different blocks. In the block containing `a` but not `b`, the projection
of `n` equals the projection of `p1`: the inserted `b` is erased. In the
block containing `b` but not `a`, the projection of `n` equals that of `p0`:
the removed `a` is erased. Every other block erases both `a` and `b`, so its
projection of `n` equals that of either positive. Thus every local projection
of `n` has appeared in some accepted positive word's corresponding local
language. The product cannot reject `n`, a contradiction. Therefore `a,b`
must share a block. This reasoning is valid for arbitrary regular factors and
all k; it does not require singleton local languages.

This is also contextual: x and y may both be nonempty and arbitrarily long.
The positive base may be longer than epsilon, so no empty or short positive
is required.

## Rejected proposed counterexample

An initial concern used alphabet `{a,b}`, positives `{epsilon,b}`, negative
`{a}`. It omitted the required rescued positive `ab` or `ba`, so it is not an
insertion-rescue witness and cannot refute the rule. The old helper correctly
reports no insertion-rescue edge for that sample. With the missing `ab`
positive added, `{a}|{b}` no longer fits: the `a` projection of the negative
is already observed through `ab`, while the `b` projection is observed through
epsilon, so every factor accepts it. The false-positive issue was therefore
in the proposed counterexample, not the graph lemma.

## Cap-q monotonicity

At a search node, let `S` be the already assigned symbols of one block and
`T` any extension (`S subseteq T`). If two positive words have different
projections onto `S`, their projections onto `T` remain different: projecting
both `T` projections back onto `S` recovers the original distinct strings.
Therefore the number of distinct positive projections cannot decrease as a
block grows. A partial block with more than q such projections can be pruned
without losing a q-feasible completion. For a complete partition, choose each
factor language to be exactly its finite set of observed positive projections.
It has size at most q and accepts all positives; it rejects every negative
precisely when at least one block has an unseen negative projection. This also
defines the empty-positive case: all observed languages are empty and every
negative projection is unseen. The provider makes no implication from this
cap semantics to the singleton-exactly-one class.
