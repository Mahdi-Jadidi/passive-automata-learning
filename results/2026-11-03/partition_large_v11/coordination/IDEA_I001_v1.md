# C011-I001: verified maximal binary-interval index

Scientific status: proposed, awaiting independent proof/static review. Execution status: not run. Parent: C010 sound adjacent-swap contraction; contextual binary-anagram rule proposed this cycle. Motivation: avoid P*N full-word scan and recognize semantic mustlinks invisible to single adjacent swaps.

For p=u s v positive and n=u t v negative, s,t over exactly two letters x,y and equal respective counts, separated owners imply equality of every block projection. Thus xy must coown. A mismatch-position-only rule is rejected: p=acb,n=bca can be distinguished by ac|b; the intervening thirdletter must not be ignored.

Proposed complete candidate discovery for this rule:
1. RLE each word. Label transition between consecutive unequal runs by its unordered symbol pair.
2. Each maximal group of consecutive equal transition labels describes one maximal contiguous two-symbol interval. Across a k-run word, sum of run memberships in these windows is (k-1)+number_of_groups <=2(k-1).
3. Index positive intervals by full length, interval bounds, unordered pair, exact local counts, and fingerprints of outside prefix/suffix. Store separate exact-context representatives within each collision bucket, not just the first hash representative.
4. Query negative intervals. A candidate is accepted only after exact unchanged-prefix/suffix comparison and verification of interval symbols/counts. Different local ordering follows from globally disjoint labels. No probabilistic equality assumptions.
5. Every contextual binary-anagram pair extends to matching maximal intervals: outside u,v is identical, interval lengths/counts equal and maximal extension stops at the same outside third symbols. Must be proved/reviewed before acceptance.

Fingerprint construction can use fixed rolling polynomial hashes with O(L) prefix preprocessing. Collisions only add exact candidate work; worst-case bucket cost may remain quadratic. Do not advertise unconditional linear time. Long-word generated adjacent-swap strings can require O(L²) copying; rejected as sole unguarded path.

Graph may retain only replayable spanning-forest certificates if explicitly documented; all pair relations/counts and default witness fields must remain. Do not silently call a reduced-output mode a faster same-output solver. Default expanded results must remain available; cache/reuse identical internal partition/projection/witness objects.

Expected example: doubled-pair m10 previously has 10 singleton graph-atoms and exact fallback52. Binary-interval proof may force five semantic pairs, allowing S(5,k)/Bell5 shortcut, if independent oracle accepts. This is a hypothesis, not an observed benchmark.

Counterexample search required: third-symbol separators; unequal counts; repeated symbols and extending prefix/suffix runs; colliding fingerprints with multiple distinct outside contexts; one-symbol runs; duplicate words; no positive/negative labels; deadlines in preprocessing; fallback without contraction. Frozen C010 remains oracle/baseline.

No claimed novelty, speed result, or physical-identification improvement. Full abstract correctness, implementation exact gates and performance comparison have different roles.
