# Independent SAT engine: design and proof checkpoint

Status: mathematical design only, pending independent review. No solver implementation or benchmark is authorized at this checkpoint. Select a standalone CNF/DPLL engine implemented independently in a later stage: no existing reference, RGS enumerator, DP, graph, or hybrid engine is imported or called as solver or fallback. DPLL is a search over Boolean assignments, not traversal of the old partition algorithms. A separate certificate checker may use independently written projection logic; the C028 reference is a test oracle only. No performance claim is made.

## Model and normalization

Input alphabet Σ=(a₀,…,aₘ₋₁) comprises distinct nonempty opaque string IDs in declared order. Input record has exactly alphabet, positive, negative arrays; words are arrays of declared IDs, including ε. Reject malformed schema/unknown IDs and deduplicate each label preserving first occurrence. P∩N is inconsistent. A partition covers Σ by disjoint nonempty blocks; empty Σ has the unique empty partition, whose conjunction is true. K and factor state counts are unknown and unbounded. For B, H(B)={π_B(p):p∈P}, R(B)={n∈N:π_B(n)∉H(B)}. Necessity and sufficiency: every negative must lie in R(B) for some block B, because every factor accepts H(B), and the finite regular languages H(B) themselves are witnesses. This concerns sample compatibility, not physical truth.

## CNF encoding — PROVED mathematically, implementation OPEN

Use Boolean y[i,k], 0≤i,k<m, asserting symbol i belongs to slot k; exactly one k per i. Symmetry break by clauses ¬y[i,k] ∨ (∨_{j<i} y[j,k−1]) for every k>0. Every nonempty slot k then has an earlier occurrence of k−1, recursively; first-occurrence labels are consecutive. Conversely every partition has exactly one such assignment, its first-occurrence labels. Set active[k] ↔ ∨_i y[i,k]. These equivalences and exactly-one constraints are polynomial size.

For each negative n, positive p and slot k construct Eq(n,p,k). For words u=u₁…uᵣ,v=v₁…vₛ, let xᵢ=y[index(uᵢ),k], zⱼ=y[index(vⱼ),k]. Define E(0,0)=true; E(i,0)=E(i−1,0)∧¬xᵢ; E(0,j)=E(0,j−1)∧¬zⱼ; and

 E(i,j)=(¬xᵢ∧E(i−1,j)) ∨ (xᵢ∧¬zⱼ∧E(i,j−1)) ∨ (xᵢ∧zⱼ∧[uᵢ=vⱼ]∧E(i−1,j−1)).

Induction on i+j proves E(i,j) iff filtered prefixes match: discard an unselected last symbol, else compare the two selected last symbols. Each equality test on IDs is computed exactly from the input, without token splitting. Introduce full Boolean gate equivalences and assert for each n: ∨ₖ(active[k] ∧ ∧ₚ ¬Eq(n,p,k)). Empty P makes the inner conjunction true; N empty adds no coverage constraints. A Tseitin-style full-equivalence encoding gives every gate a unique extension for a fixed y assignment, including constants; alternatively explicitly project model counting onto y. With m=0 handle directly: feasible iff N empty, then C=O=1, k*=0, both first-witness lists contain the empty partition. Any negative over empty Σ is ε and cannot be rejected. For m>0 and P=∅ all partitions are feasible, as they are for N=∅. Unused IDs retain y variables. Contradictory labels imply UNSAT, independent of early checks.

Encoding creates O(m²) assignment variables plus O(m Σ_(n,p)(|n|+1)(|p|+1)) equality gates and polynomial clause and cardinality size, apart from bit costs for IDs and input reading. Build a polynomial-size Boolean counting circuit for active slots and threshold k. CNF construction is polynomial in explicit input length; DPLL worst-case solving and model enumeration can be exponential. NP-hardness does not forbid finite exact algorithms.

## Exact solve and full output — PROVED conditional on complete, correct SAT decision

Pseudocode, with SAT(F) returning SAT model or proven UNSAT, or INCOMPLETE on resource interruption:

1. Validate fully. Build hard F. If SAT(F) is UNSAT return C=O=0 and infeasible; interruption returns null exact fields. Otherwise continue.
2. For k=0,…,m query F ∧ (sum active≥k); take largest SAT threshold k*. Exhaustion/UNSAT of next threshold proves optimum. Each satisfying y yields its partition; cardinality equals the number of nonempty blocks, proving objective preservation.
3. For total C, repeatedly query F with a blocking clause ∨ᵢ ¬y[i,labelᵢ] for every previously seen canonical assignment. Increment arbitrary-precision C and retain the two lexicographically smallest label vectors. The clause excludes exactly that partition, independently of auxiliary assignments. Stop only on UNSAT. For O, repeat under sum active=k*, with a fresh blocking set; retain first two optimum vectors and set recommendation to the first. A solver need not return models in lexical order: compare every returned canonical vector, and do not assert canonicality until exhaustion. Every partition is represented once, model blocking removes it once, and the finite model set guarantees termination under sufficient resources and a complete terminating SAT procedure. Enumeration is potentially Bell(m) SAT calls, each potentially exponential; storage of blocking clauses can be O(m Bell(m)). No automatic speed or practical feasibility guarantee follows.
4. Build H(B) preserving first-positive occurrence, and first rejecting block index for each normalized negative. Independently replay blocks, factors and both label sets, and compare each chosen rejection index to the first rejecting block. Distinguish C=1 from O=1 and neither from physical identification. Exact counts/canonicality require completed exhaustion, not replay alone.

A standalone complete DPLL decision algorithm may branch on an unassigned Boolean variable, simplify clauses, recursively try both truth values, and return UNSAT only if both branches do. Every recursion reduces remaining variables, so the finite search is complete and terminates with sufficient resources; an interrupted run cannot be reported as UNSAT. SAT model satisfies every clause by direct evaluation. A separately developed checker independently verifies returned partition/factor certificates and original projections; a full machine-checkable UNSAT proof or independently verified DPLL trace is an additional engineering obligation, OPEN, not established by replay. On caught exhaustion return INCOMPLETE with null mathematical claims. Explicit C028 max_candidates prefix semantics cannot be imposed on arbitrary DPLL model order; compatibility with that optional budget is OPEN unless a separate precisely specified baseline-prefix budget is implemented without invoking old solving engines. Never reinterpret it silently.

Biggest overlooked issue? SAT satisfiability or one optimum neither counts distinct partitions nor proves first witnesses; symmetry and auxiliary-model multiplicity can silently overcount. Full-output proof above requires canonical y and partition blocking, and exact completion requires an actually complete solver.

## فارسی کوتاه

برای هر نماد دقیقاً یک جایگاه تعریف می‌شود و قید تقارن شمارهٔ بلوک‌ها را بر اساس نخستین ظهور یکتا می‌کند. مدار برابریِ تصویر دو واژه را برای هر بلوک بررسی می‌کند و هر نمونهٔ منفی باید در یک بلوک از همهٔ تصاویر مثبت متمایز باشد. با حل SAT و حذف مدلِ هر افراز، تعداد کل و تعداد جواب‌های بهینه و دو شاهد اول پس از پایان کامل قابل محاسبه‌اند؛ هزینه می‌تواند نمایی باشد. این طرح هنوز کد یا ارزیابی تجربی نیست و داده‌های محدود هویت فیزیکی مؤلفه‌ها را ثابت نمی‌کنند.

## Primary sources and scope

- Davis, Logemann and Loveland, [A Machine Program for Theorem-Proving](https://dl.acm.org/doi/10.1145/368273.368557), 1962: foundational satisfiability search background, not a claim about this encoding's novelty or speed.
- Karp, [Reducibility Among Combinatorial Problems](https://cgi.di.uoa.gr/~sgk/teaching/grad/handouts/karp.pdf), 1972: classical complexity/reductions background. The projection circuit and counting construction here are derived from the stated model and V32; no novelty claim.
