# C010 unrestricted ownership: theorem ledger and counterexamples — v1

## T0. Finite consistent labels always have a one-block regular explanation

Let the known finite alphabet be `Σ`, and let the exact finite positive and negative samples satisfy `P∩N=∅`. Use one block `Σ` and local language `FΣ=P`. A finite language is regular. Every positive is accepted; every negative is rejected because it is not in P. Therefore the unrestricted version space is nonempty for every valid input.

Consequences:

1. `model_inconsistent` cannot be the mathematical result for a valid, label-consistent unrestricted input. Contradictory labels and malformed fields belong to `invalid_input`.
2. The one-block partition co-owns every symbol pair, so when `Z>0`, every pair has a same-block witness. `forced_different` is impossible.
3. A complete singleton compatible-partition family must be `{Σ}`. Any unique multiblock ownership claim contradicts T0.
4. The complete `kmax` is a data/model-class upper bound on true k, conditional on the true model belonging to the declared unrestricted class. It is not a point estimate and does not name physical devices.

## T1. Coarsening closure

Let a feasible partition have blocks `B1,...,Bt` with regular local languages `F_i`. Merge any set of blocks into `C`. Define a local language on their union by

`F_C = {w∈C*: for every i, π_Bi(w)∈F_i}`.

Each inverse projection of a regular language is regular and a finite intersection of regular languages is regular. This merged factor enforces exactly the conjunction of the original constraints, so the global language and all labels are preserved. Repeated merges show every coarsening, including the one-block partition, is feasible. This also proves that all compatible partitions coarsen any forced must-link relation.

## T2. A replayable adjacent-swap edge is a sound must-link

Suppose a positive `p` and negative `n` differ only by one adjacent transposition of distinct symbols x,y: `p=u x y v`, `n=u y x v`, with identical contexts u,v. If a partition separates x and y, then projection onto the x-owner sees x in the same place relative to every other symbol in that block; y is erased. The y-owner analogously sees the same y projection, and all blocks containing neither see unchanged projections. Therefore every block projection of p and n is equal. A componentwise model accepting p must accept n, contradiction. Thus every compatible partition must put x and y together.

The edge checker must compare the full words and prove this exact adjacent-swap relation. Co-occurrence, a graph heuristic, or a fabricated edge is not a proof. Connected components of verified edges form atoms; every compatible partition coarsens this atom partition.

## T3. Exact coarsening-family fast path

Let A be the partition into connected components of verified adjacent-swap edges. If A itself passes the direct projection criterion, then it is feasible. T2 says every feasible partition coarsens A; T1 says every coarsening of A is feasible. Hence the compatible family is exactly the coarsenings of A.

For r atoms, the number of compatible partitions with k blocks is `S(r,k)` (Stirling number of the second kind), and total `Z=Bell(r)`. A pair in the same atom has same-count Bell(r). A pair in two distinct atoms has same-count Bell(r−1), because co-owning the two fixed atoms is equivalent to partitioning r−1 merged atoms. All cross-atom pairs are ambiguous for r≥2; no pair is forced different. These counts and one partition witness per realized relation do not require listing the Bell(r) partitions.

If A is infeasible, the fast path does not apply. The exact residual block-cover DP may operate over atoms with lazy rejection masks; only proved pruning is allowed. For remaining symbols U define `R_union(U)=⋃_{∅≠B⊆U} R(B)`. At a state with already covered negatives C, if `C∪R_union(U)` is not the full negative set, no completion exists. This is a sound overestimate of all masks available from disjoint future blocks; if even the overestimate misses a negative, pruning is safe. No other heuristic pruning is inferred.

## Small counterexamples and boundary controls

* **A former forced-different result disappears without K.** For `Σ=ab, P={ab}, N=∅`, the one-block partition co-owns a,b and the split partition separates them. Unrestricted output has two answers, k=1 and k=2, and the pair is ambiguous. Supplying `K={2}` would force different, but C010 forbids external K.
* **One-block-only is possible.** For `Σ=ab, P={ab}, N={ba}`, the split projections of ba equal the positive projections on both singleton blocks, so the split is infeasible. Only `{ab}` remains. This is consistent with T0 and is the only possible singleton case.
* **An empty simple swap graph does not prove no semantic structure.** The graph-empty doubled-pairs sample has `P={ε,aabb,ccdd,eeff}`, `N={bbaa,ddcc,ffee}`. Direct projection reasoning forces `ab`, `cd`, `ef` together. Compatible partitions are exactly their coarsenings: five partitions, with spectrum 1,3,1 for k=1,2,3. Within-pair ownership is forced same, cross-pair ownership is ambiguous.
* **Positive observations/co-occurrence do not certify ownership.** With `Σ=abcd, P={ε}, N=∅`, all Bell(4)=15 partitions are compatible. Every pair is ambiguous (q=Bell(3)=5, d=10). Fabricated graph edges on this input can encode a wrong partition.
* **Empty observations retain all partitions.** With `Σ=abc, P=N=∅`, all five partitions are compatible. With P empty and arbitrary negatives, every partition is also feasible by choosing empty local languages; this is a no-positive boundary, not inconsistency.
* **A false external count can exclude the truth.** A global even-parity language over `abcd` can have true factors `ab|cd`; a false supplied K={4} could select singleton blocks despite the actual k=2. This is why C010 removes K rather than treating an arbitrary count as inferred truth.

## What can and cannot be identified

Under this unrestricted regular-factor class, if a multiblock partition is compatible, its one-block coarsening is compatible too. Thus a finite sample alone cannot yield a unique multiblock answer or certify `k>1`; it can still certify forced-same groups, exact count spectra, kmax, and ambiguity. If the complete answer set contains only one partition, it is the one-block partition. Any stronger physical claim requires a new, explicit class restriction (for example nonempty/prime/state-bounded factors) and a separately proved admissibility test; it is not smuggled into this cycle.
