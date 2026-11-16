# Shared algorithm notation

Use the naming of the manuscript `main.pdf` supplied 2026-11-15:

| Mathematical object | Shared name | Python name |
|---|---|---|
| declared ordered alphabet | Σ | Sigma |
| input sample | D=(S⁺,S⁻) | D, S_plus, S_minus |
| candidate alphabet partition | P={B₁,…,Bₖ} | partition |
| component alphabet | B | block |
| erasing projection | π_B | projection |
| component language | K_B | local_language |
| component DFA, when explicitly requested | M_B | local_dfa |
| enumerated negative trace | y_i | S_minus[i] |
| rejection indicator | x_(B,i)=1 iff π_B(y_i)∉K_B | rejection bit |
| negative obligation | Q_i: at least one component rejects y_i | negative constraint |

Our current task has NO state bound m(B) and does NOT learn local DFAs. It
returns one sample-compatible P maximizing k=|P| plus an optimality certificate.
For feasibility one may choose the canonical finite language K_B=π_B(S⁺).
This is a certificate of sample consistency, not the original generating DFA.

Do NOT reuse the manuscript's R_B (a relation of local behaviors) as the name
of a rejection bitmask. Code uses reject_mask(B). New W_i denotes the family of
minimal nonempty symbol/atom sets capable of rejecting y_i. Mandatory groups
are preprocessing atoms, not claimed physical devices. Preserve all declared
IDs, even unused ones. No state bound, known device count, labels on prefixes,
physical ownership or statistical assumptions may be added implicitly.

The established Python input keys `alphabet`, `positive`, `negative` remain
wire-compatible aliases for Σ, S⁺, S⁻. Existing result keys `blocks` and
`max_devices` represent P and k. Historical frozen documents retain their old
notation as evidence; new work should use this map rather than rewrite them.
