# Critical equation and fidelity inventory, C031

Status: reviewer approval pending. Source `ARTICLE_EN_DRAFT_2.md` SHA-256 `43a786ba43256db277d76d80986a58a7506721c8b91d71f2c9755fe694c1e6af`; numbered pseudocode `NUMBERED_PSEUDOCODE.txt` SHA-256 `4f87f5ed50cdafd53d8f02dcbf6d4cdb32b00030e3a2834b4295f8be88d002df`. The final ARTICLE_EN.md must have identical bytes or be re-reviewed. Biggest overlooked point: mathematical asterisks are Kleene stars, not Markdown emphasis delimiters.

Renderer must faithfully preserve all article text and each of the 37 numbered pseudocode rows, even if a row wraps. At minimum independently extract/read back these exact semantics; mathematical typography may vary only without changing indices, quantifier order, set complement, multiplication, or the symbol *:

1. `Σ=(a₁,…,aₘ)` with declared input order; `P,N⊆Σ*`; `F_B⊆B*`; unique empty partition and empty conjunction true.
2. `L(Π,(F_B)) = {w∈Σ* : ∀B∈Π, π_B(w)∈F_B}`.
3. `C=|𝒱(P,N)|`, `k*=max{ |Π| : Π∈𝒱(P,N) }`, `O=|{Π∈𝒱(P,N) : |Π|=k*}|`.
4. `H_B={π_B(p):p∈P}`, `R(B)={n∈N: π_B(n)∉H_B}`; preserve negative-index convention in prose.
5. `∀n∈N ∃B∈Π ∀p∈P: π_B(n)≠π_B(p)` and `⋃_{B∈Π} R(B)=N`; quantifier order must not change.
6. RGS condition `s₁=0`, `0≤sᵢ≤1+max{s₁,…,sᵢ₋₁}` for `2≤i≤m`; correct empty RGS.
7. `R(B)⊆R(D)` when `B⊆D`; all-singleton compatible implies every partition compatible, not vice versa without the singleton check.
8. First global RGS `0^m`; second `0^(m−1)1` for m≥2. Optimum singleton `(0,1,...,m−1)` and unique maximum O=1; empty m=0 handled separately.
9. `S(0,0)=1`, `S(i,k)=S(i−1,k−1)+kS(i−1,k)` and `Bell(m)=Σ_k S(m,k)`; retain signs, subscript `k` and addition/multiplication.
10. `V_B[j]=true iff π_B(n_j)∉H_B`; cache capacity 256, per-call, no cross-input reuse.
11. Preserve `C=2, O=1` in the unique-optimum counterexample, empty-alphabet `C=O=1`, `best=0`, and 48 runs/three of eight higher medians exactly as source.
12. Preserve bibliography CoALA `[3, §4.1, Proposition 5; §6.1, Corollary 12]`, related scope, author names/URLs, and all bibliography references. Do not invent authors, institution or physical claims.

The reviewer, not the rendering step, decides correctness; any substantive text/equation change requires a new version and re-review. Save extraction/readback comparison, source+output hashes, environment and commands. Inspect all PDF pages at original resolution for clipping, overlap, code wrapping, symbols, headers/footers, table fit, and link rendering; check file opens and actual page count. Do not remove technical details to hit the 10–14 page preference. No v28/v29 files modified.
