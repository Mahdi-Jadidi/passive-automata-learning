# C027: specification, proved rules, and exact pseudocode

## Contract and status

Input consists only of finite alphabet Sigma and finite trace sets P,N over Sigma, with epsilon allowed. Trace counts and lengths and |Sigma| are unrestricted finite inputs; no K or state bound is supplied. A partition consists of nonempty, pairwise disjoint blocks covering Sigma. Acceptance is the conjunction of independent regular factors over these blocks. The objective is to return a compatible partition of maximum block count, or INFEASIBLE if none exists. There is no assertion that the optimum identifies physical components. Duplicate traces may be removed. Reject invalid input containing a trace outside Sigma. If both labels contain a word, the instance is infeasible.

We use the ordinary empty-product convention: when Sigma is empty the sole partition is the empty partition and its product accepts epsilon. It is compatible exactly when N is empty. If an application requires nonempty alphabets, it may instead validate Sigma != empty; this is an input-contract choice, not a theorem that the empty case is infeasible.

**Main obstruction:** exact general polynomial time in the full input size is not obtained. The reduction below proves that such an algorithm would imply P=NP. The final algorithm is exact but exponential, so it does not satisfy the original joint polynomial-and-exact goal. All claims below are proved; no greedy choice is assumed safe.

## Semantic criterion

For B subset Sigma let proj_B erase all other symbols and define

    reject(B) = {n in N : for every p in P, proj_B(n) != proj_B(p)}.

A partition Pi is compatible exactly when union over B in Pi of reject(B) equals N. Necessity: every accepting factor must accept every proj_B(p), so every negative must be excluded in a single block that differs from ALL positives. Sufficiency: take the finite regular factor language {proj_B(p): p in P} for each block; every positive is accepted, and every negative is rejected by a covering block. This also handles P empty: the factor language is empty. The quantifier order is essential; distinguishing a negative from each positive on possibly different blocks does not suffice.

Monotonicity: if B subset C, reject(B) subset reject(C), since equality of C projections implies equality of B projections. Consequently merging blocks preserves compatibility. If Sigma is nonempty, oneblock is compatible exactly when P and N are disjoint: its projections are the original words. Nonempty, infinite and prime factor restrictions do not alter the answer under the unbounded regular class: assign each negative to a rejecting block, exclude its assigned projections and one additional word outside the finite positive projections, and accept every other block word. The excluded set is finite and nonempty; all proper-subalphabet projections are universal, so the resulting cofinite factor is prime (unary by convention).

## A direct full-input hardness proof

Reduce HITTING SET to the decision version. Given a finite universe U, nonempty subsets S_1,...,S_q, and bound k with q>=1 and 1<=k<=|U|, take Sigma=U, N={epsilon}, and P containing one word p_i listing the elements of S_i once in a fixed order. The encoding is polynomial. For every B subset U, proj_B(epsilon)=epsilon and proj_B(p_i)=epsilon exactly when B misses S_i. Hence epsilon belongs to reject(B) exactly when B hits every S_i. A compatible partition therefore contains a hitting-set block B. From any such block, replacing every element outside B by a singleton gives a compatible partition with |U|-|B|+1 blocks. Conversely every compatible partition with t blocks has a hitting-set block of size at most |U|-t+1. Thus

    optimum block count = |U| - minimum hitting-set size + 1.

So a hitting set of size at most k exists iff the optimum is at least |U|-k+1. The standard decision HITTING SET problem is NP-complete, and this construction has just one negative; it also works for vertex cover by making each S_i an edge. The partition decision problem is in NP: a partition is a polynomial-size certificate and the projection criterion is checked in polynomial time. Consequently it is NP-complete under polynomial many-one reductions, even with one negative. A polynomial-time exact optimizer for variable Sigma would therefore imply P=NP. This does not rule out exponential exact methods, fixed-parameter methods, or polynomial algorithms on restricted instances.

## Exact fallback, unknown K

Define U as the set of negative indices still needing coverage. All sets below can be bitsets. Precompute reject(B) for every nonempty subset B of Sigma by comparing each negative projection with ALL positive projections. For R nonempty let first(R) be its least element in a fixed input order. Memoization stores only fully computed states. A value of minus infinity means no feasible completion.

```text
EXACT-MAX-PARTITION(Sigma, P, N):
    validate alphabet and words; remove duplicate words
    if Sigma is empty:
        if N is empty: return empty partition
        else: return INFEASIBLE
    if P intersects N: return INFEASIBLE
    precompute reject(B) for all nonempty B subset Sigma
    (value, answer) = SOLVE(Sigma, N)
    if value = -infinity: return INFEASIBLE
    return answer

SOLVE(R, U):
    if R is empty:
        if U is empty: return (0, empty partition)
        else: return (-infinity, no partition)
    if U is empty:
        return (|R|, {{a} : a in R})
    if U is not a subset of reject(R):
        return (-infinity, no partition)
    if (R,U) is memoized: return memo[(R,U)]
    best = -infinity; best_partition = none
    for each B subset R with first(R) in B:
        (v, Q) = SOLVE(R minus B, U minus reject(B))
        if v != -infinity and 1 + v > best:
            best = 1 + v
            best_partition = {B} union Q
    memo[(R,U)] = (best, best_partition)
    return memo[(R,U)]
```

If a deterministic tie rule is wanted, compare canonical encodings of *full* candidates whenever 1+v equals best. The displayed algorithm returns an arbitrary optimum and makes no uniqueness claim.

**Invariant and proof.** SOLVE(R,U) returns the greatest number of blocks in a partition of R whose rejection masks cover U, and a partition attaining that value; it returns minus infinity exactly when no such completion exists. For R empty this is immediate. Every partition of nonempty R has exactly one block B containing first(R). After choosing B, the remaining blocks must cover precisely U minus reject(B); conversely any such completion together with B is feasible. By induction, maximizing all children gives the optimum. The U-empty shortcut returns the unique maximum |R|. The pruning condition is sound: by monotonicity no subblock of R rejects a negative not rejected by R. Thus the root returns an optimal compatible partition, including when N is empty. It terminates because each call strictly reduces |R|. Canonical anchoring visits every unordered partition without omitting any; it does not itself justify a lexicographic tie rule.

For m=|Sigma|, n=|N|, there are at most 2^m 2^n states and at most O(3^m 2^n) subset transitions; projection precomputation requires 2^m times a polynomial in the explicit input length. Bitset operations and stored witnesses add polynomial factors; the time and space bounds are exponential in the input, not polynomial. Recursive pseudocode specifies the mathematical method, without a claim about stack limits or interruption guarantees.

## Proved polynomial quick cases and bounded-deficit certificate

Compatibility of a given partition is polynomially checkable. In particular, if the singleton partition is compatible, it is the unique maximum, with m blocks. If singleton fails but a partition formed by merging one pair is compatible, then it is optimal with m-1 blocks. Test all O(m^2) pairs. These checks include variable m and arbitrary numbers and lengths of traces. Failure of both checks does not mean infeasibility or establish the optimum.

More generally, for any fixed constant d, enumerate all partitions obtainable from the singleton partition by at most d pair merges and check them in descending block-count order. A partition with m-j blocks can be formed by exactly j merges; there are at most O((m^2)^d) merge sequences for fixed d. Thus if this procedure finds a compatible partition, its first block count is the global optimum: every partition with more blocks also has at most d merges and was already examined. If it finds none, return UNKNOWN and use the exact fallback; do not call this a general polynomial solver. The degree depends on d, so this is not a polynomial bound when d is input-variable.

## Proof obligations for any future polynomial proposal

1. Preserve the single-block/all-positives quantifier in every test and guarantee a regular-factor witness.
2. Prove every discarded partition cannot improve the incumbent, including after input extension; local maximality alone is insufficient.
3. Prove exhaustive coverage or a valid bound on the whole remaining search space, including ties if canonical output or uniqueness is claimed.
4. Bound all work by a polynomial in the explicit length of Sigma, P, and N, without treating alphabet size, K, deficit, or a hidden target state count as constant.
5. Reconcile the hardness reduction: an unrestricted polynomial exact method would imply P=NP. Experimental evidence is not a complexity proof.

## Counterexample obligations

C026 COUNTEREXAMPLES_V1 CE2 and CE3 exhibit incomparable old/new optima and show that the meet of feasible cuts can fail; CE7 shows that a growing block with no current rejection may later reject a negative. These are mathematical examples, not a claim that new C027 tests have run. A separate test audit should replay these and explicitly test alleged pairwise merging rules, greedy tie decisions, and incomplete cut lists; a proposed rule must be stated precisely before a test can refute or validate it.

Biggest overlooked issue? The known exact criterion is local to a finished block, while choosing a partition couples which negatives can be covered simultaneously. Pairwise possibilities or a locally unsplittable compatible partition cannot establish the maximum block count.

**Explicit quantifier counterexample.** Sigma={a,b}, P={a,b}, N={ab}. In the singleton partition, for p=a the b-block distinguishes ab from p, and for p=b the a-block distinguishes them. Nevertheless neither singleton block distinguishes ab from ALL positives: its projection matches the positive with the same letter. Hence the singleton partition is incompatible, while the oneblock partition is compatible. Any rule interchanging `for every positive, there exists a block` with `there exists a block, for every positive` is unsound. This is a direct hand derivation, pending the separate replay audit.
