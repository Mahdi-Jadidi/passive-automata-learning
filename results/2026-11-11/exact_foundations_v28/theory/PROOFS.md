# C028 proof obligations and derivations, frozen for independent review

Biggest overlooked point? Exact enumeration proves a data-consistent optimum, not that the observations reveal the physical ownership or that optimal-tie uniqueness equals uniqueness among all compatible partitions. `SPEC.md` fixes the domain, empty product, output, and gate.

## 1. Validation and normalization

Membership in the specified finite JSON-like schema is decidable by scanning the record, IDs and words. Validation rejects malformed structure, duplicate alphabet IDs, empty IDs and unknown word IDs. Word-array equality is elementwise and exact. Removing repeated occurrences within either label set preserves both sets and therefore all compatibility statements. If a word occurs in both labels, every deterministic membership language would need simultaneously accept and reject that same word, so no model fits. Validation finishes before returning any mathematical status. Empty alphabet and epsilon are legal according to the specified word-array representation.

## 2. Projection criterion and witnesses

Suppose a partition Pi is realized by consistent block languages F_B. Because each p in P is accepted by their conjunction, every F_B contains H_B. For n in N to be rejected, some one block B must reject pi_B(n), which is impossible if this projection belongs to H_B. Hence every negative has a block satisfying the criterion. The identical one-block witness must work against all positives; exchanging these quantifiers is invalid.

Conversely take F_B=H_B for each block. Each H_B is finite, and finite languages are regular, including the empty language. Each positive has its projection in every H_B, hence is accepted. By the criterion, each negative has a block whose projection is outside H_B, hence is rejected. Outputting each H_B and one such block per negative is a finite, independently replayable certificate. With Pi empty the conjunction is true, and the criterion says N must be empty; this matches the empty-alphabet convention. Therefore the criterion is necessary and sufficient, including P or N empty, epsilon and unused symbols.

## 3. Canonical enumeration

In input alphabet order, label every block of a partition by the index (starting at zero) of its first occurrence among blocks. The resulting length-m string begins with 0, and each later entry is no larger than one plus the previous maximum. Conversely any such restricted-growth string defines nonempty blocks as the preimages of used labels; the growth condition forces used labels to be exactly 0 through its maximum, so there are no empty blocks. The two maps are inverses. For m=0, the empty string uniquely maps to the empty partition. Therefore complete lexicographic RGS generation visits each partition exactly once, including m=0. This proof uses no externally supplied K.

## 4. Evaluation, counts, optimum and ties

By section 2, evaluating the projection condition on each visited RGS marks exactly the compatible partitions. Distinct RGS encode distinct partitions by section 3. Incrementing an arbitrary-precision compatible counter on every marked RGS thus yields the exact count. For any processed prefix, maintain the invariant: best equals the largest block count among compatible processed strings; optimal_count counts precisely those attaining best; retained optimal witnesses are the first up to two such strings in lexicographic order. A strictly better candidate resets the count and list, an equal one increases the count and appends if space permits, and a worse one does neither. Induction proves the invariant. The analogous all-compatible list retains the first up to two compatible strings. On completion, the best and counts cover the entire family and the first optimum is lexicographically least among all final maximizers. If there is no marked candidate, incompatibility is proved. Witness lists contain exactly min(2,count) distinct partitions, with the optimal list including the recommendation; replaying their factors and negative coverage establishes their consistency.

`UNIQUE_COMPATIBLE`, `AMBIGUOUS`, and `INCOMPATIBLE` follow exactly from compatible_count equal to 1, at least 2, or 0. `optimal_unique` refers instead to optimal_count=1 when feasible. Example: Sigma=[a,b], P=[[]], N=[[a]]. Both a|b and ab are compatible, but a|b alone has the maximum two blocks. Thus unique optimal recommendation does not imply unique compatible ownership.

## 5. Physical meaning and indistinguishability

Take Sigma=[a,b], P=[[]], N=[]: a oneblock generator with language Sigma* and a two-block generator with factors a* and b* are both independent disjoint regular AND models and both accept all observed words (indeed all possible words). Their distinct ownership partitions cannot be distinguished from the sample or even from full behavior under these general assumptions. Thus the canonical maximizer is not a physical-truth certificate. Conditional on the model being correct and the actual generator fitting the data, if exactly one partition is compatible then its partition must equal that sole member. This conditional statement does not identify hidden device names or implementations.

## 6. Termination, edge cases, and resource behavior

A finite alphabet has finitely many set partitions. The RGS generator has finite length and finitely many possible labels at each position; each direct compatibility test compares finite arrays over finite lists. All counters and retained witnesses are finite at completion, though arbitrary-precision storage may be required. Hence the mathematical procedure halts for every finite valid input with unbounded resources. It makes no deadline, practical-memory, polynomial, infinite-input or uninterrupted-execution guarantee. If interrupted before completing the required work, mathematical fields stay null under INCOMPLETE; a completed contradiction proof is sufficient for INCOMPATIBLE. Validation failures are INVALID_INPUT, never INCOMPATIBLE.

For empty Sigma, there is one candidate with zero blocks. If N is empty it is compatible and both counts equal 1; max_blocks=0 and recommendation is empty. If N contains epsilon, no block can reject it, so count=0 and status is INCOMPATIBLE (whether or not P also contains epsilon). Any non-epsilon word is malformed for empty Sigma. For nonempty Sigma, when P and N are disjoint the oneblock candidate matches full words and is compatible; all contradictions are infeasible.

## Review obligations and examples

Reviewer should independently check schema and alphabet convention; necessity/sufficiency and empty product; RGS bijection including m=0; count/reset/tie invariant; finite witness construction; invalid/incompatible/interrupted distinction; physical claims; and finite termination with arbitrary precision. Prior fixture for quantifier order: Sigma=[a,b], P=[[a],[b]], N=[[a,b]]; each positive differs on some singleton but neither singleton distinguishes the negative from both, so only oneblock fits. C026 CE2 demonstrates incomparable maximum proposals after adding observations; C026 CE3 shows compatible cuts can have incompatible meet; C026 CE7 shows that rejection can emerge only after block expansion. These examples check unsound shortcuts; no such shortcut occurs in this baseline. No experimental test is claimed here.
