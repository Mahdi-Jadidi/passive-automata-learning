# Bounded primary-source literature check: alphabet factors and q-caps

**Review ID:** C004-G-LIT-QCAP-001  
**Checked:** 2026-10-27  
**Scope:** a few primary sources on compositional alphabet discovery, projections, shuffle decomposition, and finite local-language cardinality. This is a bounded related-work check, not a survey and not a novelty assessment. No provider or experiment was run.

## Primary sources actually read

### 1. Active refinement of component alphabets

Léo Henry, Mohammad Reza Mousavi, Thomas Neele, and Matteo Sammartino,
“[Compositional Active Learning of Synchronizing Systems Through Automated Alphabet Refinement](https://doi.org/10.4230/LIPIcs.CONCUR.2025.20),” CONCUR 2025, LIPIcs 348, pp. 20:1–20:22, DOI `10.4230/LIPIcs.CONCUR.2025.20`.

**Access/read record:** The official Dagstuhl/DROPS HTML full text was accessible. I read the abstract and Sections 1, 3, 4.1–4.3; the particularly relevant passages are Definition 3.4 (parallel product of languages by local projections), Definitions 3.6–3.8 (finite observation functions and induced local observations), Definitions 4.1–4.5 (possibly overlapping alphabet distributions and product observations), Proposition 4.6, and the distribution counterexample/refinement discussion in Section 4.2. The official page gives the title, authors, date, pages and DOI. The matching 37-page arXiv companion `arXiv:2504.16624v3` (“A Detailed Account of Compositional Automata Learning through Alphabet Refinement”) was also opened; its PDF front matter identifies it as a preprint submitted to *Logical Methods in Computer Science*, and I inspected pp. 7–10, 14, 24–25 and 30–32 for the distribution and counterexample theory. The preprint has an arXiv identifier; no separate DOI for that preprint was located in the inspected metadata.

**Relation to this project:** This is the closest source for automatically discovering component alphabets from global observations. Its formal model is active learning of prefix-closed LTS behavior with a teacher, synchronizing actions, potentially overlapping component alphabets, and iterative refinements driven by global/local observation discrepancies. The product-language semantics are expressed through projections. It is not the same task as passive exact-label fitting over complete finite traces with pairwise disjoint blocks and a finite cap q on each factor’s observed positive projection set. I found no q-cardinality threshold or q-opposition certificate in the sections read.

### 2. Whole-language shuffle decomposition with a bounded factor

Masami Ito, “[Shuffle Decomposition of Regular Languages](https://doi.org/10.3217/jucs-008-02-0257),” *Journal of Universal Computer Science* 8(2) (2002), pp. 257–259, DOI `10.3217/jucs-008-02-0257`.

**Access/read record:** The journal page and the complete three-page PDF were accessible. I read the abstract and pp. 257–259. The paper defines the shuffle product and decides whether a given regular language A can be written as B shuffle C when B is regular with a bounded number of automaton states; its Corollary 5 separately handles a finite B whose words have bounded maximum length. The paper’s `I(n,X)` bound is a state-count bound for a regular factor, while its `F(n,X)` corollary is a word-length bound. Neither is a bound of q on the number of distinct words in a local language.

**Relation to this project:** It is relevant to finite-factor shuffle decomposition and algorithmic boundaries, but differs in the main object and evidence: it asks equality of an entire regular language with a shuffle product, using an automaton for A, rather than compatibility with a finite positive/negative sample and a known partition into disjoint symbol blocks. The paper does not establish the current projection-count criterion or q-opposition graph certificate.

### 3. Shuffle quotient and decomposition decision results

C. Câmpeanu, K. Salomaa, and S. Vágvölgyi, “[Shuffle Quotient and Decompositions](https://doi.org/10.1007/3-540-46011-X_15),” in *Developments in Language Theory (DLT 2001)*, LNCS 2295, pp. 186–196 (Springer, 2002), DOI `10.1007/3-540-46011-X_15`.

**Access/read record:** The official Springer record’s metadata and abstract were available through search results. The abstract says the paper introduces a shuffle analogue of the Nerode right congruence, obtains decidability for some subclasses of regular languages, and proves undecidability for context-free shuffle decomposition. I did **not** read the chapter body: opening the official DOI redirected to a Springer page inaccessible to this browser, and the nonpublisher PDF mirror returned HTTP 404. No theorem-level detail from this chapter is used here.

**Relation to this project:** It supplies relevant context that exact whole-language shuffle decomposition is a distinct and nontrivial problem. Its abstract gives no result about passive sample partitions, pair projection cardinalities, or a finite local-language word-count cap.

## Searches and access failures

The targeted web searches included `arxiv 2504.16624 active compositional alphabet refinement`, `shuffle factorization alphabet decomposition regular languages projections`, `passive learning disjoint alphabet factors positive negative samples regular languages decomposition`, `finite local language cardinality bound projections alphabet partition learning`, `shuffle decomposition regular language factorization`, and `q-opposition automata learning projection`. They returned the compositional learning paper, general shuffle-decomposition results, and unrelated finite-language/state-complexity items; I found no primary source directly matching a q-bounded observed-projection or q-opposition certificate. This is only a report of the limited search, not evidence that no such work exists.

The publisher’s page for “Shuffle Factorization is Unique” (DOI `10.1016/S0304-3975(00)00433-3`) returned HTTP 403 when opened, so I did not use its theorem in this note. The DLT mirror and official Springer chapter failures are recorded above. No other inaccessible search result is relied upon.

## Scope contrast and safe use

The closest conceptual overlap is that both the project and active compositional-learning work reason about symbol-alphabet components through trace projections. The assumptions and outputs differ: the cited active method learns synchronizing, possibly overlapping components through membership/equivalence queries; this project certifies finite-sample compatibility for known-k, disjoint blocks from exact labels. Classic shuffle-decomposition papers concern equality of whole languages and bound factor automaton size, word length, or decomposition structure—not the q cardinality of observed local words. The q-cap theorem and threshold `>q` remain project-specific proof claims in this cycle and must be justified independently; this literature check makes no novelty claim.
