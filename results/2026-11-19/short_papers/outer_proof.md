## 3. Reduction to a SAT Relaxation

Order the atoms by their first event in Σ. When an atom set occurs as the argument of a projection or rejection predicate, expand it to the union of its events. Write r_i(B) for π_B(y_i)∉H_B.

### Step 1. Contract mandatory events

**Lemma 2.** Rejection is upward monotone. If B⊆C and r_i(B) holds, then r_i(C) holds. *Proof.* If π_C(y_i)=π_C(x) for a positive x, projecting again onto B gives π_B(y_i)=π_B(x), a contradiction. ∎

For negative y_i form M_i={a∈Σ : r_i(Σ∖{a}) is false}. A block rejecting y_i must contain each a∈M_i. Otherwise it lies inside Σ∖{a}, contradicting Lemma 2. Hence all symbols in M_i share a block of every compatible partition. Join the symbols within each M_i and take the transitive closure. The resulting equivalence classes are the atoms. Every compatible partition contracts uniquely to atom blocks and expands back without changing its count or any projected word. Thus q atoms give an upper bound of q blocks. A compatible singleton partition attains |Σ| and a compatible atom partition attains q.

### Step 2. Turn a completed rejection into a necessary cut

By Lemma 1, a rejected partition has an index i for which every block B fails r_i. For each such B, start from its atom mask and add an atom only if the larger region U still fails r_i. Keep a positive x_U with π_U(y_i)=π_U(x_U). An addition skipped because it would reject cannot become legal later by Lemma 2. Therefore one scan yields an inclusion-maximal false region per block. A positive match alone suffices for validity.

**Lemma 3.** Require some block C of the next partition to satisfy C⊄U for every recorded U. The rejected partition fails this requirement because each of its blocks has its own containing region. In any compatible partition, some C rejects y_i. If it were contained in a recorded U, Lemma 2 would force that U to reject y_i despite its witness. Therefore the cut preserves every compatible partition and excludes the rejected one. ∎

### Step 3. Encode exactly the partitions, counts and cuts

Use e_ab for each unordered atom pair. Set the diagonal implicitly to true and interpret e_ba=e_ab. For a<b<c, with pair bits x=e_ab, y=e_ac, z=e_bc, impose (¬x∨¬y∨z), (¬x∨¬z∨y) and (¬y∨¬z∨x). These are exactly the three transitivity implications for distinct atoms. Cases with repeated atoms follow from reflexivity and symmetry. Every model therefore yields equivalence classes, and every partition gives one such pair assignment.

Let z_j be true exactly when no earlier atom is equivalent to j. This selects the least index of each class once. Define T(j,d) as “at least d representatives among the first j atoms.” Set T(j,0)=true and T(0,d)=false for d>0. For d>0 use T(j,d)=T(j−1,d)∨(z_j∧T(j−1,d−1)). Induction on j proves it by splitting on whether the first j−1 already suffice. Thus T(q,d) is the exact block-count test.

For anchor a, the class of a escapes U if a lies outside U or some b outside U has e_ab=true. Conjoin these tests over U and disjoin over a. This implements Lemma 3 because each class has an anchor. Each AND output v over inputs l_j uses (¬v∨l_j) for each j and the clause (v∨¬l_1∨…∨¬l_d). The OR clauses are the dual. Hence each gate is equivalent to its function. A partition satisfying the cuts extends to a model by evaluation, and every model decodes to a partition satisfying all cuts.

<!-- page -->

## 4. Algorithm, Exactness and Verification

**Algorithm 1.** Maximize the number of compatible blocks.

```
Validate and normalize D. Resolve label conflicts or an empty alphabet.
Test singleton blocks with the teacher. If compatible, certify |Σ|.
Construct mandatory atoms. If their partition is compatible, certify q.
Learn the first cut from the rejected atom partition.
repeat:
    Maximize T(q,d) under the current cuts by SAT threshold queries.
    Decode a maximizing partition P and ask the teacher.
    If it rejects, learn a witnessed cover cut and repeat.
    If it accepts, let k = |P| and obtain a refutation at threshold k+1.
    Return P and the checked certificate.
On resource exhaustion, return INCOMPLETE with no optimum claim.
```

The atom test reuses the singleton verdict when the partitions coincide.

**Step 4. Maximize the current relaxation.** The bounds start at an attained lower endpoint 1 and upper endpoint q, or an upper endpoint certified in a previous round. The one-block partition is compatible on disjoint labels over nonempty Σ, so every learned cut preserves it. New cuts only shrink the relaxation. If a query for T(q,d) is satisfiable, a decoded model attains some m≥d and supplies the updated lower endpoint and candidate. If it is unsatisfiable, no relaxation partition has count ≥d, so d−1 is a valid upper endpoint. The algorithm tests the inherited upper endpoint and otherwise bisects the remaining interval. Each interior query strictly reduces the interval and preserves both bounds, so at convergence the retained candidate attains the exact relaxation maximum.

**Theorem 1 (soundness, optimality and termination).** On a valid input with sufficient resources for exact calls, Algorithm 1 returns a certified infeasibility result or one optimal compatible partition. *Proof.* The boundary cases are justified in Section 1. For the general case, by Step 1 every feasible partition is represented and by Lemma 3 each learned cut retains it. The current relaxation maximum is therefore an upper bound on every compatible objective. A completed teacher acceptance of a maximizing candidate attains that bound. After each completed rejection, the failed proposal is removed permanently and at least one compatible partition remains. The domain of atom partitions is finite. The exact teacher operations and threshold searches terminate on each call, so the algorithm eventually accepts. A resource interruption supplies neither a rejecting verdict nor any cut derived from an unfinished teacher check. ∎

**Step 5. Replay the certificate.** For infeasibility, check the label conflict or empty-alphabet condition in Section 1. For optimality, check that the blocks are nonempty, disjoint and cover Σ, then check Lemma 1 directly. Check the attained bound for a structural certificate. Otherwise recompute the atoms, check each equality π_U(y_i)=π_U(x_U), and regenerate the CNF at k+1. By Lemma 3, these matches suffice for cut validity. Every better compatible partition would satisfy the reconstructed formula.

**Step 6. Check the refutation.** Unit propagation under the negation of each added clause must yield conflict. Propagations are logical implications, so by induction all retained additions follow from the initial CNF even if deletions are ignored. A final conflict without assumptions proves unsatisfiability [3]. With Step 5 this proves optimality. The checker trusts the shared normalization, contraction and encoder.

For existence, discard tautologies and eliminate each variable by retaining pivot-free clauses and adding the non-tautological resolvents of opposite-sign pivot clauses. A remaining assignment extends unless it violates a retained clause or forces both pivot values, violating a resolvent. Unsatisfiability therefore yields the empty clause. Negating a resolvent forces both pivot signs, which verifies the addition.
