# Bounded adversarial audit: passive alphabet partition discovery

This audit checks finite sample feasibility, the proposed swap and insertion-rescue must-link witnesses, the exact two-block solver, and counterexamples to stronger recovery claims. The source, machine-readable counts, and examples are in this directory: [audit_partition.py](audit_partition.py), [audit_results.json](audit_results.json), and [audit_examples.json](audit_examples.json).

## Main findings

For a fixed candidate partition, the finite sample is feasible exactly when every negative word has at least one block whose projection is absent from that block's positive projections. Necessity follows because every positive projection must be accepted by its local factor, while each negative must be rejected by at least one factor. For sufficiency, choose each local factor to be the finite set of observed positive projections; those factors are regular and accept every positive while rejecting each negative at a missing projection.

The witness graph is sound under a true noise-free disjoint-alphabet product model. If two letters belong to different blocks, swapping adjacent occurrences preserves every block projection. For insertion-rescue, assuming the inserted letters belong to different blocks makes the negative's projection in the first letter's block match the rescued positive, and its projections in the other blocks match the base positive. Thus the graph's connected components refine the true partition. With exactly `k` nonempty true blocks, `r >= k`; when `r = k`, the graph components equal the true partition. This requires the true model to exist and every edge used to come from correctly labeled examples. It does not require labels for every possible word.

The strongest counterexample is a complete-generator example where the sample uniquely identifies the partition and the complete-target witness graph does not. Let `Σ={a,b,c}`, `k=2`, `Π*={{a},{b,c}}`, with local languages `L_a={a}` and `L_bc={b,c}`. The complete global positive language is `{ab,ba,ac,ca}`. Use those four positives and negative `abc`; every sample word contains symbols from both true blocks. The negative is rejected because its `{b,c}` projection is `bc`. Each alternative two-block split has all projections of `abc` among the positive projections, so only `{{a},{b,c}}` is feasible. The complete-target graph has no edges: every adjacent-swap partner of a positive length-two word is also positive, and insertion-rescue would require two positive words whose lengths differ by two; every target positive has length two, so no such pair exists. Therefore `r=3>k=2` even though the finite sample gives a unique feasible partition.

## Bounded checks

The deterministic exhaustive checks completed in 33.298 seconds with Python 3.12.14. No random sampling was used, so there is no seed.

- **Independent feasibility oracle:** all `3^7 = 2,187` labeled samples over the seven words of length at most two on `{a,b}`, for the singleton partition. The projection criterion agreed with exhaustive assignments to the local Boolean membership variables in all cases, across 91,913 assignments.
- **Solver cross-check:** all 81 three-labelings of `{ε,a,b,c}` on alphabet `{a,b,c}` were checked against all three two-block partitions using the independent Boolean-variable oracle. Both pruned and unpruned solver results agreed in 162 calls across 4,323 local assignments. Four supplied theory JSON examples also matched their expected feasible-partition counts; the structural graph-gap example returned one feasible partition with zero graph edges and three graph components.
- **Witness regressions:** forward and reverse adjacent swaps, the minimal insertion-rescue example, forward and reverse contextual insertion-rescue, and an infeasible two-block sample all matched the independent oracle. The returned witness payloads were checked against their positive and negative words and positions. These checks covered 176 local Boolean assignments.
- **Known-generator sweep:** all 3 two-block partitions of `{a,b,c}` and all 3,072 pairs of finite local languages formed from block words of length at most two were enumerated. Each local language is regular. Sample labels came from the complete generator for every word of length at most four touching both true blocks. Complete-generator witness labels were checked for contexts `x,y` over `{a,b,c}` of length at most two each, covering every possible witness with a positive word: the generated targets accept words of length at most four, so a positive `xaby` witness requires `|x|+|y|≤2`. Every edge stayed within its true block; every graph refined the true partition; `r≥k` held throughout; and all 1,596 models with `r=k` had exact graph recovery. In 462 models, the bounded sample uniquely selected the true partition while `r>k`.

## Counterexamples and scope

The examples file distinguishes generated models from finite constraint illustrations.

- Same-label swaps do not establish independence: the global product of an even-length language over `{a,b}` and the local language `{c}` accepts both `abc` and `bac`, yet the first factor couples `a` and `b` in one component.
- Positive-only data can fit two different `k=2` partitions and different regular targets. The single word `adbc` is accepted under both `{{a,b},{c,d}}` with factors `{ab}` and `{dc}`, and `{{a,c},{b,d}}` with factors `{ac}` and `{db}`; its order interleaves both blocks under either model.
- `S+={ε,abc}`, `S-={a}` has two incomparable maximally fine feasible two-block partitions, `{{a,b},{c}}` and `{{a,c},{b}}`. This is a finite constraint example, not a claim that both are the generating partition.
- `S+={ab,ac,bc}`, `S-={abc}` has no feasible singleton or one-pair-merged partition, while the all-three-letter block is feasible. This is also a finite constraint example; with known `k=2` on `{a,b,c}`, none of its partitions is feasible.
- A sample-consistent allocation can learn the wrong factor: with true factors `{a}` and `{b,bb}`, `ab` is positive and `abab` is negative. An alternate learner can reject through the `b` factor by excluding the unseen projection `bb`, but then it rejects `abb`, which the true target accepts.

The generated-language enumeration uses finite local factors only, so it corroborates the claims within the stated bounds rather than covering all regular languages. The general witness-soundness and `r=k` conclusions depend on the stated product-model assumptions; the exhaustive audit is not their proof. Finite sample consistency alone does not identify the true partition or target language.

## Reproduction and traceability

Run from this directory with `python audit_partition.py`. The final run used the bundled Python executable recorded in `audit_results.json`. That file also records the elapsed time, Python version, exact executed command, and SHA-256 hashes of the audit and solver sources used for the run.
