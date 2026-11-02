# C008 identifiability counterexamples — v1

These constructions are mathematical arguments; no executable experiment or provider run was used.

## A. Same complete language, same k, different physical groupings

Let the global alphabet be `Σ={a,b,c,d}` and define the regular language

`L = { w ∈ Σ* : |w|_a is even and |w|_d is even }`.

It has two 2-component product representations on different disjoint partitions:

1. `π₁ = {{a,b},{c,d}}`, with local factors
   - `K_ab = {u∈{a,b}* : |u|_a is even}`;
   - `K_cd = {v∈{c,d}* : |v|_d is even}`.
2. `π₂ = {{a,c},{b,d}}`, with local factors
   - `H_ac = {u∈{a,c}* : |u|_a is even}`;
   - `H_bd = {v∈{b,d}* : |v|_d is even}`.

In either representation a global word is accepted exactly when the same two unary parity conditions hold. Thus the complete global language, not merely a finite sample, is identical; both partitions have `k=2` and two-symbol blocks. The local factors are regular but **not prime**: for example, `K_ab` is the product of the even-`a` unary language and unrestricted `b*`.

**Conclusion.** Knowing the complete language and k does not identify physical ownership when factors may be decomposable. This example does not refute uniqueness under a prime-factor assumption.

## B. Any finite trace horizon can miss a coupling, even with k=2 and prime regular factors

Fix any finite observation horizon `h`. Choose integer `M≥1` with `4M>h`. For two distinct symbols x,y, let

`F_xy = {u∈{x,y}* : |u|_x and |u|_y are both even} \ {x^(2M)y^(2M)}`.

Each `F_xy` is regular: it is the intersection of two parity languages minus one finite word. It is infinite. It is **alphabet-prime** over `{x,y}`: its projections are exactly the even unary languages `E_x={x^(2r):r≥0}` and `E_y={y^(2r):r≥0}`, but `x^(2M)y^(2M)∈E_x || E_y` while that word was removed from `F_xy`. Therefore `F_xy ≠ E_x || E_y`; with a two-symbol alphabet this rules out every nontrivial alphabet split.

Define two global languages, each with two disjoint factors:

`L₁ = F_ab || F_cd`, with partition `{{a,b},{c,d}}`;

`L₂ = F_ac || F_bd`, with partition `{{a,c},{b,d}}`.

For every word `w` of length `<4M`, no two-symbol projection can equal a removed word `x^(2M)y^(2M)`, which itself has length `4M`. On all such words each local test therefore reduces to even counts of its two symbols. Consequently

`w∈L₁ ⇔ |w|_a,|w|_b,|w|_c,|w|_d are all even ⇔ w∈L₂`.

But `a^(2M)b^(2M)` has length `4M`: its `ab` projection is the removed word, so it is rejected by `L₁`; its `ac` and `bd` projections are the separate even unary words, so it is accepted by `L₂`.

**Conclusion.** For every finite horizon, even exhaustive ± labels for all words through that horizon can be consistent with two different hidden partitions; here both targets have known `k=2`, infinite regular local languages, and prime factors. The state sizes can grow with M, so this does not contradict a fixed state-bound theorem. It is a worst-case impossibility family, not a claim that every finite dataset is ambiguous.

## C. What this does not say

- It does not say every finite labeled dataset admits two ownerships. C007 has sample-level examples with a unique finest compatible partition; that is a statement about the finite sample's compatibility poset.
- It does not say two different prime decompositions can yield the *same complete* nonempty global language. Under disjoint ownership and the prime definition above, the proof in `INDEPENDENT_CRITIQUE_V1.md` gives uniqueness of the prime partition.
- It does not identify physical device names or internal nonminimal state encodings. Those can differ while their extensional component languages are the same.
