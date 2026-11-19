# Related work and positioning

The present task is to maximize the number of blocks in a partition of the declared alphabet, subject to compatibility with a finite labeled sample under conjunctive projected acceptance, without a state bound. It returns one optimum and a checkable certificate. It does not seek all optima or local DFA models. The supplied manuscript is an unpublished project source, not independent prior-art validation.

Clarke et al.'s counterexample-guided abstraction refinement [1] establishes a broad abstraction/check/refine paradigm in model checking. V45 similarly refines a relaxation after a failed candidate, but its candidate is an alphabet partition and its witnessed false-region cover is a problem-specific necessary constraint. This analogy does not establish novelty of refinement itself.

Logic-based Benders decomposition [2] provides a closer optimization analogy: a master proposes decisions and a subproblem supports logically derived cuts. The V45 cover cut excludes a rejected partition and possibly others while preserving every compatible partition. Calling this Benders-like is a structural comparison, not a claim that the general decomposition or cut-learning idea is new.

Lauffer et al. [3] study learning conjunctive DFA decompositions from examples and demonstrations, with bounds on component sizes. Conjunction is shared, but bounded automaton decomposition and unrestricted-state maximization of alphabet-partition cardinality are different optimization questions. Heule and Verwer [4] use SAT for exact DFA identification; SAT and exact identification are established, whereas V45's SAT master encodes equivalence classes, learned cover constraints and a block-count threshold. Henry et al. [5] study compositional automata learning through alphabet refinement in an active-learning setting; its queries and objective should not be conflated with passive finite-sample partition optimization.

The defensible contribution is the joint construction: derive a witnessed false cover from a completed failure, learn a sound family-excluding constraint, maximize the remaining partition relaxation, and combine a feasible output with checked upper-bound evidence. The sufficient trie bound connects the unchanged bounded teacher to the unrestricted sample problem. These claims are conditional on the stated model and proof and are not a certification of first-in-literature novelty. A broader systematic prior-art search is needed before any priority claim. Neither shared projections nor SAT use alone supports one. V45's reported measurements show a costly teacher and no general speedup; field validation remains absent.

## References

1. E. Clarke, O. Grumberg, S. Jha, Y. Lu, H. Veith, “Counterexample-Guided Abstraction Refinement,” CAV 2000, pp. 154–169. https://doi.org/10.1007/10722167_15
2. J. Hooker and G. Ottosson, “Logic-based Benders decomposition,” Mathematical Programming 96, 33–60 (2003). https://doi.org/10.1007/s10107-003-0375-9
3. N. Lauffer et al., “Learning Deterministic Finite Automata Decompositions from Examples and Demonstrations,” 2022. https://arxiv.org/abs/2205.13013
4. M. Heule and S. Verwer, “Exact DFA Identification Using SAT Solvers,” ICGI 2010. https://www.cs.cmu.edu/~mheule/publications/DFA_ICGI.pdf
5. Henry et al., “A Detailed Account of Compositional Automata Learning through Alphabet Refinement,” arXiv:2504.16624v3, revised 1 April 2026. https://arxiv.org/abs/2504.16624v3

Sources consulted 16 November 2026.
