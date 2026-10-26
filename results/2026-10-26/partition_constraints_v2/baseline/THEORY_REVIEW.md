# Second formal review

Reviewed on 2026-10-26: `LITERATURE_REVIEW.md` and the draft `RESEARCH_REPORT_FA.md`. Review scope was mathematical and attribution boundaries, not independent verification of every bibliographic source. Henry v3 Proposition 5 and Corollary 12 were checked against primary full text.

No substantive error was found in the synthesis's feasibility proof, sound witness rules, graph coarsening statement, known-k graph certificate, exact feasible-set enumeration, or empty-graph unique example. All recovery claims require the existence of a true target in the stated model and correctness of supplied k. The finite-language construction establishes regular-factor feasibility only with unrestricted state counts. Neither graph recovery nor singleton finite feasible-set recovery identifies the local languages or a canonical/prime decomposition of a completely known language.

Clarifications sent to the literature editor and supervisor:

1. State explicitly that Pi* belongs to F_k(S), explaining why a singleton feasible set recovers the true declared partition under the model assumptions.
2. Explain that extending local DFAs by self-loops outside assigned blocks embeds the projection model into full-alphabet DFA conjunction. The distinction from Lauffer/Meng is the disjoint-support structural constraint, not an inability of their general conjunction formalism to express these languages.
3. Add that positive-only and negative-only samples leave every candidate partition feasible under unrestricted regular factors. Both label classes are necessary for nontrivial data-based discrimination, but are not sufficient.
4. Replace potentially ambiguous wording that a local projection is "forced negative" with the exact condition that at least one projection is not positively witnessed; the negative global label demands a local rejection but may not identify its block.
5. Do not present regularity by itself as a substantive added finite-sample constraint: finite positive projection languages already supply regular witnesses. State bounds or an explicit complexity objective would add constraints.

The draft appropriately avoids novelty, performance, general passive recovery and unknown-independence claims. The unresolved status of Cano Gomez's independence-relation assumption is clearly marked. The present witness graph is explicitly incomplete, and the four-symbol example proves exact finite-data inference can exceed its information. These boundaries should survive future editing.

The initial solver example runs are distinct from the independent audit; audit completion should determine the final report's verification status. This review adds no experiment or empirical claim.
