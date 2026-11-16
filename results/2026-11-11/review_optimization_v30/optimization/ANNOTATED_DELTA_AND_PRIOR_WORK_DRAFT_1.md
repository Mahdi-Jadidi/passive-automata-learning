# Exact full-contract optimization: annotated delta and prior work

Status: proof and candidate source independently reviewed; correctness experiments and performance evidence are pending. Biggest overlooked point? C and O count different families, and neither a fast certificate nor caching permits falsely reporting enumeration work or silently altering the first two witnesses.

## Base proof and proposed delta

The C028 proof remains the proof of the baseline exhaustive algorithm under its documented model and unbounded-resource mathematical completion; this review has not found a substantive flaw in that argument. Its scope is exact finite-sample consistency and optimization, not an unseen-behavior or physical-identification theorem. It must not be read as proving a practical runtime bound, universal 100% physical accuracy, or the serialization capability of a host. C029 additionally refined the conceptual recursive/actual iterative RGS equivalence and witness-order specification. A fresh code audit and independent tests are still required for the new code.

Let H_B be positive projections on B; let R_B be the set of normalized negative indices whose projections are not in H_B. Original criterion: a partition is compatible iff the union of R_B over its blocks covers every normalized negative index. C028 enumerates RGSs in declared alphabet order, accumulating exact C, best, O and first two witnesses for both full and optimal families.

```text
SOLVE(record, optional max_candidates):
    perform exactly C028 input/budget validation and first-occurrence deduplication
    if a word belongs to both labels: return C028 INCOMPATIBLE result
    create empty per-call cache, maximum 256 entries
    if A enabled and max_candidates is None:
        s_single = (0,1,...,m-1)
        if baseline CHECK(s_single) succeeds:
            C = Bell(m) via exact Stirling recurrence
            all = [0^m] plus [0^(m-1)1] iff m >= 2
            optimal = [s_single]; best = m; O = 1
            construct and independently replay C028-format witnesses
            return full exact result, or ERROR if replay fails
    initialize original exact enumeration counters/witness RGS lists
    for s in C028 lexicographic RGS order:
        enforce original explicit max_candidates boundary
        if B enabled:
            for each block B of s:
                retrieve R_B from fresh bounded LRU or compute and cache it
            compatible = every normalized negative index lies in some R_B
        else:
            compatible = original baseline CHECK(s)
        perform unchanged C028 C, best, O, first-two update
    perform unchanged witness construction and replay; return full result
    on caught interrupt/memory exhaustion: return C028 INCOMPLETE null fields
```

The implementation keeps the original C028 helper functions, offers `solve_a`, `solve_b` and `solve_combined` as separate ablation entry points, and does not modify the C028 public entrypoint. An explicit candidate budget always bypasses A, so for equal inputs and budgets the baseline and all variants traverse the same candidate prefix and have the same complete/incomplete boundary. In particular, no result from A is mislabeled as having enumerated Bell(m) candidates. Timing of externally injected interrupts cannot be synchronized between different implementations; the no-partial-claim policy is preserved.

**A correctness argument.** Rejection is monotone in block inclusion: a projected equality on a larger block would imply equality on every smaller block. If the singleton partition is compatible, every partition is its coarsening and each negative retains at least one rejecting block, so all partitions are compatible. The number is the Bell number; the first two RGS are `0^m` and, for m≥2, `0^(m-1)1`. The singleton RGS uniquely has m blocks, so O=1 and it is the canonical optimum. At m=0 there is one empty RGS and the certificate passes only if N is empty; at m=1 there is one RGS. C028 witness construction/replay yields the same factor lists and first-rejecting indices as baseline, and the same errors are treated as nonclaims. Exact Stirling recurrence `S(i,k)=S(i-1,k-1)+k S(i-1,k)` counts all partitions by placement of the last symbol; B_m=Σ_k S(m,k). It uses O(m²) arithmetic operations but bigint bit complexity and output size are not constant. The pure Python integer result may exceed the runtime's decimal/JSON digit conversion limit; no change of that exact value or unsupported wire-serialization guarantee is implied.

**B correctness argument.** A cached block vector is a pure function of the current call's normalized P,N and the block's tuple of complete IDs. A cache hit, miss, or eviction therefore returns the same rejection mask. Coverage of every negative across the blocks is identical to the original per-negative existential block test. For every RGS the compatibility Boolean is identical; unchanged iteration, prefix budget checks, counters and tie operations then give identical C, best, O, all-compatible status and stored first-two RGS. Unchanged witness construction and replay provide the same first-positive-projection factor serialization and first rejecting block. For m=0 with N nonempty the empty union fails; with N empty it succeeds vacuously. Fixed 256 entries bound cache entries, not work or input; evictions permit recomputation and full rejection vectors can take more time or memory than the baseline's early failure.

The arguments apply to A alone, B alone, and the combination. They do not prove the program bug-free or performance-positive on real inputs. As C026 already used rejection-mask caching and forced-atom/max-block fast checks, this is an adaptation of established ideas to the C028 full-count/two-witness contract, not a claimed research novelty.

## Bounded primary-source comparison

- [Stamatelatos and Efraimidis, *Lexicographic Enumeration of Set Partitions*](https://arxiv.org/abs/2105.07472) surveys algorithms for ordered enumeration; the method's RGS-based baseline is in that well-studied area, not newly invented here.
- [NIST DLMF §26.7](https://dlmf.nist.gov/26.7) gives the Bell-number partition count and its relation to Stirling numbers. This is the combinatorial basis for the full-family certificate; neither the Bell number nor the Stirling recurrence is new.
- [Simon, Tittmann and Trinks, *Counting Connected Set Partitions of Graphs*](https://arxiv.org/abs/1005.1726) studies a different restricted set-partition counting problem and its complexity. It illustrates the broader counting literature, but its graph-connectivity constraints do not prove this sample-coverage algorithm.
- [Björklund, *Exact Covers via Determinants*](https://arxiv.org/abs/0910.0460) studies randomized detection for specified exact-cover problems. It does not by itself return this task's exact labeled-partition counts, canonical first two witnesses, or interruption semantics; no determinant-based algorithm is substituted here.
- [Drescher, *Symmetry Breaking for Answer Set Programming*](https://arxiv.org/abs/1008.5033) discusses detecting and breaking symmetry in a different setting. For C028, naive orbit representative counting would generally lose labeled partition multiplicities or required lexicographic witnesses; a valid quotient would need explicit orbit weights and canonical reconstruction, and no such claim is made.
- [Henry et al., *A Detailed Account of Compositional Automata Learning through Alphabet Refinement*](https://arxiv.org/html/2504.16624v3), §4.1 Proposition 5 and §6.1 Corollary 12, contains a closely related observation-projection obstruction in active LTS learning, including potentially overlapping distributions; it should not be represented as identical to the disjoint-factor optimization or overlooked as prior theory.

This targeted literature check is not a comprehensive novelty search. No third candidate, symmetry quotient, separate exact-cover solver, or complexity improvement is claimed. The fast certificate can add precheck overhead when it fails; the LRU may thrash or do extra work; actual results must report regressions as well as gains.
