# Method draft v1

We consider a finite nonempty declared alphabet A and finite noiseless samples P,N⊆A*, with complete words and disjoint labels. An architecture is an unordered partition π of A into nonempty blocks. Each block B has an arbitrary regular language L_B⊆B*. A word is accepted exactly when every block projection belongs to its local language. There is no state bound, finite-language assumption, or access to a hidden generator. Optional K is an externally trusted exact block count.

**Proposition 1 (finite-sample feasibility).** π admits consistent regular factors iff for every n∈N there exists B∈π such that for every p∈P, projection_B(n)≠projection_B(p). The finite languages of positive projections prove sufficiency; positively forced local acceptance proves necessity.

**Proposition 2 (coarsening).** If S⊆C and a negative projection on S is absent from all positive projections, its projection on C is also absent. Therefore feasibility is preserved by coarsening. For unknown K, any feasible nontrivial partition implies a feasible bipartition. The oneblock partition is always feasible on disjoint labels.

Sound adjacent-swap constraints identify symbols that every feasible partition must keep together. Their connected components, called forced atoms, provide a quotient with r atoms. No completeness claim is made for these constraints. Every feasible partition is a partition of the atoms, and every atom partition is evaluated by Proposition 1.

**Algorithm A (unknown-K fallback).** Preserve validation, shortcuts, known-K search and exact witness construction. After the atom partition fails, enumerate canonical atom bipartitions:

```text
unknown_K_fallback(atoms, validated_sample):
    F := (1 << number_of_atoms) - 1
    W1 := exact_oneblock_witness(validated_sample)
    for M in 1, 3, 5, ..., F-2:        # atom zero stays on first side
        poll_resource_budget()
        W2 := exact_witness([M, F xor M], validated_sample)
        if W2 exists:
            return ambiguous(W1, W2)
    return certified_unique(W1, exhausted=True)
# Any resource interruption before return gives unresolved.
```

There are 2^(r−1)−1 candidates. Each split occurs exactly once; Proposition 2 shows that rejection of every split excludes all nontrivial partitions. The first accepted split and oneblock suffice for ambiguity. This reduces the fallback candidate family from general set partitions to bipartitions; it does not bound preprocessing or total runtime by that count. Exact masks, projection caching and witness output carry additional costs.

The stress family n=a1...am, P={n with ai deleted}, N={n} has m² total characters, empty swap graph and r=m. Every proper block collides with a positive obtained by deleting an outside symbol; only oneblock is feasible. For m≥2 the unary shortcut fails. This is a designed analytic obstruction, not natural benchmark data.

## LIMITATIONS

Uniqueness refers to the sample-compatible partition within this declared model, not identification of the true factor languages, automaton states, or hidden architecture. Unknown K admits coarsenings and always admits oneblock. Known-K conclusions are conditional on externally correct K; Algorithm A does not replace fixed-K search. Worst-case enumeration remains exponential. A compact exhaustion flag alone is not an independently checkable proof artifact; independent exhaustive or analytic controls have their own stated scope. Interrupted runs remain unresolved. No speedup, benchmark outcome, deployment decision or external novelty claim is asserted here.

Local provenance: C006 PROOFS_v1.md T1–T4/T7–T9 supplies the feasibility, coarsening, split and obstruction ingredients; C020 EXACT_SCALING_PROPOSAL_v1.md supplies the optional known-K envelope. These are reintegrations of prior project results. External novelty review is pending. This draft contains mathematical reasoning, not new experimental evidence.
