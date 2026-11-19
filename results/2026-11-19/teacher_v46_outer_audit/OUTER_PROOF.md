# Exactness of the optimizer outside the teacher

The **teacher** answers compatibility for one specified partition. The **outer optimizer** contracts mandatory symbols, searches a SAT relaxation, generalizes completed failures and returns one maximum partition with a checkable upper bound. We use the proved V45 decision theorem as a premise for completed teacher calls.

## 1. Compatibility and the teacher interface

Let `H_B = π_B(S⁺)` and define `reject_i(B)` to mean `π_B(y_i) ∉ H_B`. Every factor accepting the positives must accept all of `H_B`. Hence a compatible partition has some block satisfying `reject_i` for every negative index i. Conversely, if this condition holds, choosing `H_B` as each local language accepts all positive words and rejects every negative. The finite language `H_B` is realized by its positive-prefix trie plus a rejecting sink, or by one rejecting state if empty. Thus a complete teacher with the derived bound decides the unrestricted finite-sample condition. The bound is solely an interface parameter.

On disjoint labels and nonempty Σ, the one-block partition is compatible because the projection on Σ is the identity. Conflicting labels make the sample infeasible. For empty Σ the empty partition accepts ε, so it is compatible exactly when the negative set is empty. The normalizer preserves alphabet order, unused event IDs and distinct words within each label set. Deduplication does not affect the condition.

The cached projections used for proposals and failed-cover witnesses are exact. The interned node keyed by (parent, symbol) represents the parent's unique word with the symbol appended. By induction on depth, these keys give identical nodes exactly for identical words. For B contained in C, erasing outside B after erasing outside C equals erasing outside B directly. Transforming the parent first and then keeping or erasing the last event implements this identity. The cache publishes an entry after forming all projected words and indexes. The verifier uses independent direct projection from the original words.

## 2. Mandatory atoms and structural bounds

If B lies in C and B rejects a negative, then C rejects it. Otherwise a positive would match the negative on C, so the same words would match on B. If Σ without event a is nonrejecting for y_i, every block rejecting y_i contains a. Accordingly the mandatory symbols for i occur together in a block of every compatible partition. Taking the transitive closure across i preserves this property. Its disjoint components are the atoms.

Every compatible partition of Σ contracts to one partition of the atoms. Expanding the atom blocks gives back the same original blocks and count. Conversely each atom partition expands uniquely, and its compatibility is evaluated on the expanded symbol blocks. Therefore at most q blocks are possible for q atoms. An accepted singleton partition attains the alphabet upper bound. An accepted atom partition attains the atom upper bound. These shortcuts return certified maxima by checking attainment, with no need for an UNSAT proof.

## 3. A witnessed failure cut is necessary and excludes its source

After a completed rejection, choose one y_i with no rejecting block. Cover each proposed block by an atom region U whose projection of y_i matches an original positive. The greedy growth changes U only while such a match exists. If adding an atom would make U reject, every later superset containing that atom also rejects by monotonicity. Thus the single pass produces inclusion-maximal false regions. Maximality helps exclude candidates and is unnecessary to justify the cut.

The cut requires at least one block C in the next partition with C not contained in any recorded U. The failed candidate violates it because each of its blocks lies inside its own false region. Any compatible candidate has a block rejecting y_i. That block cannot lie in a region matching an actual positive because monotonicity would make that region reject. The cut therefore retains all compatible partitions, regardless of refinement relation, while excluding the failed one.

## 4. Exact Boolean master and search invariant

Use a Boolean e_ab for each unordered pair of atoms. With implicit diagonal truths and symmetry, the three pair implications per unordered triple force transitivity and characterize equivalence relations. Their equivalence classes are in bijection with atom partitions. A representative r_a holds exactly when a is not related to any smaller atom, creating one representative per class. A Boolean gate for “at least t among the first j” equals the disjunction of “at least t among the first j−1” and “r_j is true and at least t−1 among the first j−1.” The base case is true for t=0 and false for positive t on the empty list. Induction gives exact threshold semantics. Full equivalence clauses for AND and OR preserve both directions.

For anchor a, its class escapes U when a is outside U or when e_ab is true for some b outside U. Conjoin over the regions and disjoin over anchors. This equals the cut of Section 3, since every class has an anchor and relates precisely its members. Therefore each cut-augmented CNF represents exactly its relaxation on the atom partitions, including all compatible partitions.

Initially q is a valid upper bound. Adding a necessary cut can only shrink the relaxation, so its previous maximum is still an upper bound. On disjoint labels the one-block partition remains a feasible lower endpoint. A SAT answer supplies an actual decoded model and permits raising the lower endpoint to its attained count. An UNSAT answer at t permits lowering the upper endpoint to t−1. These updates preserve both bounds. At convergence the retained model attains the maximum of the current relaxation.

If the teacher accepts this maximizer, it is compatible and every compatible candidate has count at most its count. It is therefore globally optimal. For each completed rejection the next relaxation loses at least the current candidate and retains every compatible candidate. There are finitely many atom partitions and a compatible one remains, so under complete exact calls and enough resources the loop eventually accepts. This is finite termination with no practical runtime bound. Exceeding a resource budget returns `INCOMPLETE` without a partition, objective or certificate. It supplies no new cut based on an unfinished teacher check.

## 5. What the accepted output proves

The consumer directly validates the returned partition and its compatibility. A structural certificate proves the attained alphabet or atom bound. For a general certificate the consumer rebuilds the contraction, checks each region's positive witness against the identified negative and regenerates the pair, count and cut clauses. At threshold k+1 every hypothetical better compatible partition would satisfy this CNF by Sections 2–4. A checked refutation therefore rules all of them out.

For each RUP addition, a contradiction obtained by unit propagation under the negation of the addition means the current formula entails it. By induction every retained addition is a consequence of the original threshold CNF. Ignoring deletions keeps consequences already established. A final unit conflict without assumptions proves unsatisfiability, even when the proof log is empty and the base clauses alone conflict.

Thus an accepted certificate proves optimality without assuming that the teacher's verdict or the producer's SAT search was correct. The executable checker still relies on correct normalization, direct projection, mandatory grouping, deterministic CNF reconstruction and RUP replay. The fresh implementation tests exercise these claims without constituting formal verification of that code.
