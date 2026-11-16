# C029 final mathematical and scientific content review — APPROVED

Biggest overlooked point: the finite-sample optimum need not be the original physical partition, and a familiar projection obstruction cannot be claimed as new merely because this implementation rederives it.

Approved immutable content SHA-256:
- `content/PAPER_SECTION_EN.md`: 27E04E663E35E7513570E2F065719F0118D91A77D13B6978EBA74A92EA06FEB2
- `content/WALKTHROUGH_FA.md`: CE8B787B3C45805C190D27EC3230488BFC7024F136764333AD7C0322D9164947
- `content/NUMBERED_PSEUDOCODE.txt`: 4F87F5ED50CDAFD53D8F02DCBF6D4CDB32B00030E3A2834B4295F8BE88D002DF

The EN and FA hashes match reviewed drafts 2 and 1 respectively. Review also re-opened v28 source, pseudocode, spec, proofs, both amendments and actual V2 results; their hashes and detailed obligation table appear in SOURCE_THEORY_REVIEW.md.

| Check | Verdict and basis |
|---|---|
| Model/scope | Correctly restricts to Boolean full-word labels, independent disjoint arbitrary regular factors, declared alphabet and no supplied K/state bound; distinguishes physical ownership and sample-optimality. |
| Projection theorem | Necessary/sufficient quantifier order and finite projected-positive factor construction are correct, including P empty, N empty and empty product. Quantifier counterexample checks out. |
| RGS enumeration | RGS/partition bijection and recursive lexicographic generation are correct; text supplies the rightmost-increment/zero-suffix successor proof connecting iterative source and conceptual recursion. Canonical ordering uses input alphabet order. |
| Core counting | Prefix invariant, strict-best reset, equality counting, all-compatible vs optimal uniqueness, exact tie witnesses and canonical first optimum are correct. |
| Refinement | Source defers materialization from saved RGS; deterministic construction on fixed normalized input yields the conceptual eager witnesses. Internal replay's narrower checks versus first-order construction and independent audit are described correctly. |
| Wire contract | Atomic IDs, duplicate normalization, malformed-before-contradictory priority, empty alphabet, normalized negative indices, factor order and INCOMPLETE/ERROR null mathematical fields match amended source. |
| FA examples and line coverage | All lines 1–37 are explained. The two-pair example has C=2, best=2, O=1; the three-symbol tie example has C=3, best=2, O=2, and after adding c the canonical optimum changes while best remains 2. |
| Cost/termination | Bell(m) full enumeration times a polynomial in encoded input, including replay and arbitrary-precision qualifications, fits this reference method; no DP bound or general polynomial runtime is falsely ascribed. Termination is mathematical with sufficient resources, not a deadline guarantee. |
| Prior work | CoALA v3 §4.1 and Corollary 12 contain a closely related projection obstruction; active LTS/possibly overlapping synchronization are distinguished. Moerman 2019 concerns active Moore-machine outputs. The section disclaims a novelty clearance; bounded literature reading is not exhaustive. |
| Evidence | Results correspond to actual audit V2 JSON; finite tests are not substituted for general proof, and review is explicitly coordinated AI rather than human or proof-assistant verification. |

No unresolved material content defect identified in the checked versions. This approval is for the scientific text and pseudocode and does not approve a subsequently generated DOCX without faithful content readback/layout inspection. It is not a claim of manuscript novelty, acceptance, or error-free behavior under every software/hardware failure. A broader literature review and application-specific evidence remain necessary for a research publication.

## Citation-locator amendment — renewed approval

The prior frozen sentence cited “§4.1 and Corollary 12” without tying each locator to its proper section; that wording was ambiguous, although it did not explicitly assert that Corollary 12 appeared in §4.1. The author preserved that candidate and changed the sentence to specify “§4.1, Proposition 5, and §6.1, Corollary 12.” The directly inspected arXiv v3 places these results in those respective sections. A byte comparison shows only that citation clarification and a trailing blank line; all prior scientific checks remain applicable.

New approved `content/PAPER_SECTION_EN.md` SHA-256: 8009AF278F09837E1CC8B5F9744D93601414F756B63F5417A289DDCAC317DEC2. The old SHA 27E04E66... is preserved as `PAPER_SECTION_EN_FREEZE_CANDIDATE_1.md`; FA and pseudocode hashes remain as above. Typesetting should use the new hash and must be followed by DOCX readback.
