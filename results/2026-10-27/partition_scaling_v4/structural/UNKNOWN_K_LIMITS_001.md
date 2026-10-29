# C004 unknown-k identifiability limits: whole-language preservation

Date: 2026-10-27. Scientific status: elementary proof, no novelty claim. Execution status: text/proof only during the auditor's serial timing window; no provider, test, benchmark or experiment was run. This is a new note; frozen S001/S002 proofs are unchanged.

## Setup

Let Sigma=B1 disjoint-union ... disjoint-union Bk, where every alphabet block is nonempty, and let Li be a regular language over Bi. Words are finite complete traces. Erasing projection to B is pi_B. The disjoint-alphabet product accepts

    L = { w in Sigma* : for every i, pi_Bi(w) belongs to Li }.

Alphabet ownership and the acceptance semantics are the same as C004. Local languages need not be finite, nonempty, singleton or irreducible for the following proof.

## Merging factors preserves the entire product language

Choose a nonempty set J of factor indices, and let C be the union of Bj for j in J. Define a language over the merged alphabet:

    M_J = { v in C* : for every j in J, pi_Bj(v) belongs to Lj }.

This is precisely the disjoint-alphabet shuffle of the local languages in J: it contains all interleavings of one chosen word from each Lj, preserving each chosen word's internal order. If some Lj is empty, both this definition and the shuffle are empty. Empty local words are permitted and cause no exception.

Replace all factors indexed by J with the single factor (C,M_J), retaining the other factors. For every global word w and every j in J, projection composition gives

    pi_Bj(pi_C(w)) = pi_Bj(w).

Consequently, membership of pi_C(w) in M_J is equivalent to simultaneous membership of pi_Bj(w) in Lj for all j in J. All unmerged factors keep their original conditions. Thus the merged product accepts exactly L, for every w in Sigma*, not merely on a finite observation set. Repeating the operation allows any coarsening of the original alphabet partition, down to one factor on Sigma with local language L.

## The merged language remains regular

For each j in J take a complete DFA (Qj,Bj,delta_j,qj,Fj) recognizing Lj. Build a DFA over C whose state is a tuple in the Cartesian product of the Qj. Reading a letter a in Bj advances exactly coordinate j using delta_j and leaves all other coordinates unchanged; disjoint ownership makes this unambiguous. The initial tuple contains the local initial states and a tuple is accepting iff every coordinate is in its local final set. Induction on word length shows coordinate j equals the local state reached by pi_Bj(v). This DFA recognizes M_J and has at most product_j |Qj| states. Hence regularity is preserved by every merge. No appeal to unobserved examples or an oracle is involved.

## Identifiability consequence

Whenever an unrestricted regular-factor product explanation with k>=2 exists, a one-factor regular explanation with the same entire global language also exists. Therefore factor count and architectural partition cannot in general be identified from global language observations alone, even if every word's label is known exactly. A finite consistent sample's one-factor explanation using the finite positive set as its local language is only a weaker special case: that explanation need fit only the sample, whereas the construction above preserves the complete target language.

An irreducibility, finest-factorization, maximal-decomposition, state-complexity or architectural convention can change the target of identification, but must be stated explicitly. Merely selecting the largest number of factors compatible with a finite sample does not prove that the same decomposition is irreducible, true, or uniquely finest for the full language. This note does not prove that a preferred decomposition exists uniquely under any particular convention. It also does not claim that every arbitrary partition or refinement preserves a language: the guaranteed direction is merging existing factors with the specifically constructed merged language.

This result uses the disjoint-alphabet complete-word product semantics. Different synchronization semantics, shared symbols, transition structure beyond accepted words, state observations, or additional interfaces are outside its statement. The degenerate empty global language may admit still more explanations and does not weaken the obstruction.

## Contrast with the unknown-k singleton certificate

S002's prepared certificate assumes exactly one local word per factor. Contextual positive/negative swap witnesses force letters together; their transitive closure forms must-link components. Positive pair opposition, which is sound only under the singleton assumption, separates those components. A clique in the quotient opposition graph can therefore force both the partition and k within the singleton class.

Merging singleton factors generally leaves that class. If two merged singleton local words are nonempty and use disjoint alphabets, placing the first entire local word before the second or the second before the first gives two distinct shuffle words. The merged language is regular but is no longer singleton. Thus the unrestricted regular merge obstruction does not contradict a class-conditional singleton uniqueness certificate. The qualification matters: merging with an epsilon-only factor can leave the shuffle singleton, and merging several epsilon-only factors does as well. A valid singleton unknown-k certificate must rule out such unresolved coarsenings through actual must-link/opposition evidence; one must not assume every singleton merge necessarily creates multiple words.

## Relationship to reviewed literature

This is a direct DFA/projection proof using the model fixed in coordination/CONTRACT.md, not a claimed new theorem. The primary compositional-learning lineage and its different active query/synchronization setting are documented in LITERATURE_COMPOSITIONAL_S001.md: Henry et al., arXiv:2504.16624v3, https://arxiv.org/html/2504.16624v3 . That lineage is background; no claim is made that its active correctness result proves passive identifiability here. The regular merging proof above is self-contained.
