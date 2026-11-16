# Concrete optional follow-up — requires user approval, NOT implemented

The exhaustive teacher's cost is sum(q^(|B|*q)*2^q) for q=1..m(B), before the relational join. No change was made to that algorithm to avoid this cost.

For THIS caller only (unrestricted local states, independent sufficient trie bounds, no partial local-behavior assignment), there is an exact faster feasibility adapter:

1. Choose K_B=pi_B(S_plus), represented by a finite trie.
2. Its rejection row has bit 1 exactly for projections absent from pi_B(S_plus).
3. Every positive-consistent DFA's rejection row is componentwise at most this row: a forced positive cannot be rejected.
4. This maximum row is itself realizable within the caller's sufficient bound.
5. The global conditions are positive ORs, so simultaneous maximum rows satisfy all conditions iff any choice of rows does.

Thus this adapter would replace exhaustive local table construction and joining with exact projection coverage for the partition-only question. It would still feed the NEW generalized-cut outer loop, so it is not V43's eager all-minimal-witness extraction.

This is NOT a valid replacement for the entire manuscript algorithm. Arbitrary partial assignments, acceptance queries, complete behavior relations, and other smaller prescribed state bounds need the original semantics and can lose answers under a maximum-row replacement. A separate, explicitly restricted adapter would be required; `teacher_main.py` and the supplied manuscript should remain the reference.

No adapter implementing this proposal is activated or added to production. Approval must explicitly authorize this restricted feasibility adapter before it is implemented or compared as a production method. The current slow teacher remains in use.
