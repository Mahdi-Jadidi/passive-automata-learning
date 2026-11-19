# Certified Maximum Alphabet Partitioning with an Exact Interactive Teacher

Research article · V46 evaluation of the frozen V45 procedure · 19 November 2026

## Abstract

Given positive and negative whole traces over a declared event alphabet, we seek one disjoint alphabet partition with the greatest number of blocks whose projected regular languages classify the sample conjunctively. We derive a sufficient positive-trie parameter for the supplied bounded-DFA teacher, preserving the unrestricted mathematical objective. An exact SAT master maximizes the block count subject to accumulated necessary constraints. After each completed rejection, projection witnesses justify a generalized cover cut that eliminates the failed partition while preserving all compatible partitions. The first accepted relaxation maximizer is globally optimal. The certificate combines direct sample feasibility with a structural bound or a checked refutation above the returned block count. {{ABSTRACT_RESULTS}}

## 1. Introduction

Passive trace labels give global outcomes while leaving the local decomposition unspecified. Under the whole-trace AND model, each component reads only the events in its block. A positive trace must pass every component, whereas a negative trace must fail at least one. Many different partitions may explain a finite sample. We optimize the number of blocks because that is the stated objective, and return one maximizer with a checkable upper bound. Distinct maximizers can be incomparable under refinement. The objective therefore supplies no uniqueness or identification theorem.

The main contribution is an exact combination of an alphabet-partition relaxation, the supplied manuscript's fixed-partition teacher, witnessed negative feedback encoded as a general cut, and a separate proof consumer. The unrestricted projection criterion connects the decision interface to the target objective. The cut uses a failed negative and multiple witnessed regions without arbitrarily choosing a merge. V46 evaluates V45 with larger resource limits, extends its correctness review, and retains the benchmark and microbenchmark limitations. Implementation and experiment revisions are confined to the new evaluation artifacts.

{{RELATED}}

## 3. Algorithm and implementation

The declared alphabet Σ is ordered, with opaque distinct nonempty string IDs. The wire fields are alphabet, positive, negative. Normalization validates word symbols, removes duplicates separately in first-occurrence order, and retains ε and all declared IDs. Certificate indices are positions after this deduplication. The result fields blocks and max_devices encode P and k=|P|. The word “component” refers to a mathematical factor on a block. All projections erase symbols without reordering, quotienting, or interpreting their names.

### Algorithm 1. Solve and certify

```
Normalize D and check the deadline.
If labels conflict or Σ is empty with a negative, emit direct infeasibility.
If Σ is empty, emit the empty partition with a symbol bound.
Build the projection store. Ask Algorithm 2 about singleton blocks.
If accepted, return singleton blocks with a symbol bound.
Compute mandatory atoms. If their partition differs, ask Algorithm 2.
If accepted, return the atom partition with an atom bound.
Use the completed rejection of the atom partition to learn its first cover.
Build the atom master with that cut. Set upper to the atom count.
Repeat:
    Find a maximum-count model at or below the inherited upper bound.
    Set upper to its decoded block count k and expand its blocks.
    Ask Algorithm 2 about this partition.
    If rejected, add Algorithm 3's cut and continue.
    If accepted, refute threshold k+1 in a fresh proof-enabled SAT solver.
    Check the assembled certificate and return the partition and proof.
On resource exhaustion, return INCOMPLETE with null result fields.
```

Singletons give the largest count possible over Σ. The mandatory contraction tests Σ with each individual symbol removed for each y_i, and takes the equivalence closure of forced co-memberships. If its partition agrees with the singleton proposal, the previous rejection is reused. The master starts from all atom partitions, constrained by the first cut. For fixed cuts, querying threshold t asks whether some partition has at least t classes. Try the inherited upper bound first, then binary search if it fails, keeping one feasible maximizing model. The lower endpoint is witnessed by the all-in-one partition on disjoint labels. Adding clauses preserves learned constraints and can only lower the upper endpoint. The final proof query uses the current clauses and the next threshold regardless of how the search reached k.

### Algorithm 2. Fixed-partition teacher and exact projection

```
For each block B of P:
    Retrieve exact labeled projections. Derive m(B) from positive prefixes.
    Enumerate every named complete DFA of size 1 through m(B).
    For DFAs accepting all positives, insert the rejection row in R_B
    with one DFA witness per distinct row. Publish a completed table.
Construct each Q_i as the relation of assignments rejecting y_i.
Substitute projection-forced zeros and build the responsibility graph.
Choose a spanning forest. For each assignment to the other edge bits:
    Filter and project fresh working tables using the assigned values.
    Discard the branch if a relation is empty.
    Apply upward semijoins. Discard a branch with an empty root.
    Apply downward semijoins and reconstruct compatible local rows.
    If reconstructed, return ACCEPT with witnesses.
Return REJECT after exhausting all branches.
```

The teacher names column x_(B,i) by both block and negative index, including when projected negatives coincide. A table entry holds the original rejection row for witness recovery. Cache keys include the block, both ordered projected samples and m(B). Cached local tables are complete and never conditioned in place. The wrapper checks every completed teacher answer against the direct projection predicate and stops on disagreement. This agreement check occurs after the call. The manuscript's Sections 5.1 through 5.3 define the implemented decision procedure. Full behavior queries in the manuscript and the partition optimizer in this article have different interfaces.

The external projection store hash-conses exact (parent, symbol) pairs. It first records terminals for the full alphabet. On a cache miss, it selects the smallest cached superset of the requested mask, breaking ties by numeric mask, and transforms its reachable prefix nodes iteratively from the root. The root denotes ε. Each other node is the word of its parent followed by its symbol, so two distinct interned nodes cannot represent the same word by induction on depth. If B⊆C, then π_B(π_C(w))=π_B(w). For an old node, append its symbol to the transformed parent exactly when it lies in B. This implements that identity by induction on depth. Terminal ranks preserve sample order. Materializing each distinct terminal once per entry and recording the first matching positive yields exact membership and witnesses. A mask entry becomes visible only after its projections, witness map and rejection mask are complete. Partly created nodes are valid prefix nodes but supply no completed entry. This cache avoids redoing a cached mask and can trade tuple scans for pointer walks, hashing and word reconstruction.

### Algorithm 3. Generalize a completed rejection

```
Pick the first y_i for which every proposed block is nonrejecting.
For each proposed block B:
    Set U to the atom set of B.
    Scan atoms in declared order and add an atom if U remains nonrejecting.
    Retain a matching original positive for the final U.
Deduplicate and sort the witnessed regions by mask.
Require some future block to escape every retained region.
```

If adding an atom causes rejection, any later superset containing that addition still rejects by monotonicity. Hence one scan yields an inclusion-maximal false region for each initial block. This rule may find different maximal regions from different starting blocks or scan orders. Maximality generalizes the prohibition but is unnecessary for certificate soundness. The certificate records the negative index, atom-space region masks, and normalized positive indices witnessing equality of original-word projections.

### Algorithm 4. Check a result

```
Normalize the input and validate the certificate and partition schemas.
For direct infeasibility, check a labeling contradiction or empty-alphabet case.
For optimality, check the declared cover and all negative separations directly.
For a symbol bound, compare k with |Σ|. For an atom bound, recompute atoms.
Otherwise, recompute atoms, validate every region witness and rebuild the CNF.
Apply RUP checks to the refutation of the threshold k+1 formula.
Accept only if the required checks complete and succeed.
```

### 3.5. An interactive example

Let Σ=(a,b,c), S⁺={cba}, and S⁻={abc,bac}. Every singleton projection agrees with the positive for both negatives. No two symbols are forced together. All two-symbol projections separate abc, while bac can be separated on {a,c} or {b,c}. For abc and the singleton partition, ascending atom growth leaves precisely the three singleton regions. Each is witnessed by cba. The cut requires a block of size at least two. Taking {a,c} and {b} gives a compatible partition of size two. Threshold three in the one-cut master is unsatisfiable. The fixture exercises this reasoning with an actual teacher call and a proof checked on the original sample.

The first rejection on the fixed overlap_8 case illustrates generalization beyond excluding a single partition. Its positive traces are ε and the ordered concatenation of all events. The negative consisting of s0 has the false regions {s0} and Σ∖{s0}, witnessed by the full positive and ε, respectively. A block escapes both regions exactly when it contains s0 and at least one other event. The cut excludes every partition leaving s0 alone, while allowing any choice of a companion that satisfies the remaining constraints.

{{PROOF}}

### Search invariants and consumer details

The bound inherited at each new round is the previous relaxation maximum. Every assignment in the new formula was feasible in the old formula on its old variables, so the maximum cannot increase. In the binary search, the retained candidate proves the lower endpoint achievable. A SAT answer may increase that endpoint to the full count of its decoded model, and an unsatisfiable threshold reduces the upper endpoint to t−1. The one-block witness satisfies every cut because it is compatible. At convergence the retained model is a maximum, including when the search never increases the lower endpoint above one.

For the downward semijoin, a child row surviving its upward subtree reduction can be extended outside its subtree exactly when a surviving parent row agrees. The parent row already has a full extension by induction from a surviving root. Its child-subtree choice can be replaced by the candidate child row's extension since the edge bit is the only shared column across that cut. This proves downward reduction preserves exactly the extendable rows. Taking one supporting row per child is consequently consistent. Conditioning erases only columns fixed on both incident relations, which retains all compatibility constraints.

For DRUP [SAT13], negate all literals of each proposed addition. Unit propagation preserves implications of the current formula and the negated addition. If it derives a contradiction, the current formula entails that addition. By induction, all retained additions follow from the rebuilt threshold formula. Ignoring deletions retains entailed clauses, allowing at least as much propagation. Removing repeated literals preserves clause semantics and detects unit clauses reliably. A tautological addition is always entailed and can be discarded. A final conflict with no assumptions proves unsatisfiability of the base formula. Even an empty proof log must establish that conflict. No SAT search run by the producer serves as an axiom of the consumer.

## 5. Complexity and resource behavior

Write n=|Σ|, q for the number of atoms, N=|S⁻|, and L for the total symbol occurrences after normalization. Let s=|B|. For one uncached block the number of enumerated named DFA representations on a completed call is exactly A(s,m)=∑_{h=1}^{m} 2^h h^{sh}. Positives can short-circuit simulation. With word-length sum L_B and W_B projected words, simulation and candidate construction take O(A(s,m)(1+L_B+W_B+s m)) elementary operations. Building the prefix set by tuple slicing costs O(∑_{w∈π_B(S⁺)} (|w|+1)²) when the sum is taken over the input projection list with repeats. The local table has at most min(2^N,A(s,m)) rows. A witness needs O(sm+m) entries plus its rejection vector. The bound m is at most L_B+2 when there are positives, and is one otherwise. The resulting enumeration can be very large even for tiny alphabets with long words.

For a candidate with k blocks, let T_v be the size and d_v the schema width of working relation v before conditioning. A negative relation explicitly generates 2^{d_v} assignments and retains 2^{d_v}−1. With f feedback edges, there are at most 2^f branches. One branch filters rows in O(∑_v(1+T_v)(1+d_v)+f), apart from hashing and graph bookkeeping, and uses at most twice the sum of T_u T_v across forest edges in pairwise support comparisons. Column lookup, traversal and reconstruction add polynomial work in the graph and table sizes. Only one branch's reduced tables need to be retained at a time. Completed local caches can persist across calls.

The master starts with q(q−1)/2 pair variables, 3 binom(q,3) transitivity clauses, and O(q²) additional representative and counting variables and literal occurrences. For a cut with u regions, let W=∑_{U}(1+|U|(q−|U|)). The anchor/escape construction uses O(W+q+qu) literal occurrences and O(q u+q) auxiliary variables. The current loops can take O(q²u) mask tests to construct a cut, even when many gates simplify. The number of SAT calls per round is O(1+log q). Worst-case solving time is exponential in the CNF variables by exhaustive Boolean search, and the deployed backend has no practical polynomial-time guarantee. The number of distinct rejected proposals is at most the qth Bell number, and the greedy step tests at most kq enlargements per rejected proposal. A cache miss examines the existing mask keys and visits the selected source's reachable prefixes once, plus materialization and index construction. Across all masks the cache can still be exponential in n. Counts treating tuples, hashing, and integer masks as elementary operations describe the encoding and enumeration scales. Python tuple length, hashing and multiword integers contribute separately to actual runtime.

The checker scans original words for feasibility, atoms and cut witnesses. Its simple repeated-scan RUP routine makes at most V+1 passes over the current clauses per addition or final conflict, where V is the number of encoded variables. Its worst-case time in a fixed formula and proof is O((p+1)(V+1)F), with p proof lines and F an upper bound on current literal and clause occurrences, plus clause parsing and normalization costs. The current normalization uses membership scans of clauses to discard tautologies. The proof size itself is not generally polynomially bounded. Timeouts are cooperative, with an interrupt timer around native SAT. Windows peak working set is a process-level measure including runtime and native imports.

{{RESULTS}}

## 7. Limitations and trust boundary

The exhaustive named-state enumeration can dominate even the first singleton query. The projected finite-language witness proves that the teacher bound is sufficient, independently of how many states a real source might have. The experiments exercise finite synthetic and diagnostic inputs and report zero valid whole-trace AND field trials. Historical BGL and selected-output observations use different label semantics. These results support no statistical generalization or physical recovery guarantee. Solver rankings are workload-specific. In the historical four-method comparison, dynamic programming led on overlap_8 and V42 led on oneblock_8. The projection measurements concern the specified workloads and cached scanner.

The proof checker does not import the teacher, DAG projection store or native SAT solver. It shares normalization, atom construction and deterministic master encoding with the producer. Those components and the RUP interpreter are trusted for the correspondence from original data to clauses and from proof to conflict. The assessments, including Terra contributions, were AI-assisted. No formal verification or external peer review is claimed. Source-level conformance refers to the supplied manuscript algorithm and its reference implementation. There was no supplied original executable to compare with V45. Deadline granularity depends on cooperative polling and native interrupt handling. A deadline can also expire after a completed teacher call during explanation or proof. Only an already completed rejection can justify its recorded cut, and no mathematical result or certificate is returned on interruption.

## 8. Conclusion

The teacher-guided procedure offers an exact way to return one maximum compatible alphabet partition with a checked upper bound under sufficient resources. It connects bounded local-DFA tables to unrestricted sample feasibility and derives globally valid cut constraints from completed failed proposals. {{CONCLUSION_RESULTS}}

{{REFERENCES}}

## Appendix A. Reproduction

Use Windows x64 CPython 3.12 with the committed PySAT wheel contents and run each solver version in its own process. From the repository root, run the new harness with the following commands, choosing a new output directory each time. The retained environment records file digests, commit, CPU, interpreter, native binary versions or hashes, and each frozen-manifest check. The raw JSONL gives the input, worker and consumer limits, profiles, proofs, verdicts and measured durations.

```
python -B results/2026-11-19/teacher_v46/run.py all --out new-results
python -B results/2026-11-19/teacher_v46/summarize.py new-results
python -B results/2026-11-19/teacher_v46/audit/review.py new-review.json
```

The release directory contains the full raw evidence, review scripts and generated tables. V43 exports finer phase timings. V45 exports total duration, teacher-call duration including image retrieval on the completed path, per-call trace and the current or final teacher-call counters. The timings and counters have these scopes, so last-call enumeration is not cumulative. Separate process timing captures standalone verification and worker startup. The builder uses ReportLab with the installed Windows Times New Roman, Consolas and Segoe UI Symbol fonts. The rendered page images and layout checks apply to the archived PDF. The teacher source and supplied manuscript are identified by the verified V45 manifest.

## Final section. Proposals for future teacher strengthening

Future teacher changes require explicit approval. First, try canonical state numbering or accessible-state enumeration. Removing representations equivalent under state renaming preserves all behavior rows when each original DFA still has a representative of no greater size. Unreachable states can be removed without affecting behavior and the bound is an upper bound. Reconstruct a named DFA witness for each row and compare full tables on bounded cases, including partial assignments and behavioral queries. Measure the cost of canonicalization alongside enumeration savings.

Second, encode the bounded DFA and acceptance constraints in SAT, with transition-function, designated initial state, final-state and path variables. A decision solver for prescribed rejection bits can preserve bounded existential responses if the encoding is proved equivalent and checked witnesses are decoded. Full table and behavior-query interfaces additionally require complete projected enumeration or exact support queries over the same relation. A single satisfiable model does not establish table completeness. A third approach is to index semijoin support by shared bits, preserving conditioned rows and witness recovery at the same interface. Each proposal needs its own equivalence and performance study against the frozen reference.

For the restricted unrestricted-state feasibility call only, the canonical H_B produces a maximal local rejection row that dominates the other rows. For positive-OR obligations Q_i and no externally fixed bits, putting these rows together decides compatibility by the projection criterion. A direct feasibility adapter could exploit this property. It would change the evaluated teacher and would not answer general partial assignments, arbitrary bounded calls or all realizable behavior queries. No proposal in this section was implemented.
