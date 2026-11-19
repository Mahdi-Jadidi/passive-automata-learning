# Standalone V46 and V47 papers

## Six-page proof editions

**An Algorithm for Partitioning Traces** is available as [V46 PDF](../../../output/pdf/An_Algorithm_for_Partitioning_Traces_V46.pdf) and [V47 PDF](../../../output/pdf/An_Algorithm_for_Partitioning_Traces_V47.pdf), with the [V46](v46_proof_complete.md) and [V47](v47_proof_complete.md) editable manuscripts. The shared steps prove contraction, the cut, the encoding, exact search, certificate replay and refutation existence. The teacher proof is specific to each edition. V47 additionally proves NP-completeness of the general threshold problem.

Use `build.py --proof-edition` for the monochrome build. All six pages of each final edition were visually checked, including the teacher proof, Boolean clauses, algorithm and refutation steps, evidence table and references. The [layout record](layout_proof_edition.json) contains the verified page and PDF hashes.

## Earlier five-page editions

- [V46 PDF](../../../output/pdf/V46_Certified_Alphabet_Partitioning_Exhaustive_Teacher_Short.pdf) and [editable English source](v46_complete.md). The exhaustive fixed-partition teacher remains in the loop.
- [V47 PDF](../../../output/pdf/V47_Certified_Alphabet_Partitioning_Polynomial_Teacher_Short.pdf) and [editable English source](v47_complete.md). The projection decision replaces the exhaustive fixed-partition call.

Print editions in monochrome are available for [V46](../../../output/pdf/V46_Certified_Alphabet_Partitioning_Exhaustive_Teacher_Monochrome.pdf) and [V47](../../../output/pdf/V47_Certified_Alphabet_Partitioning_Polynomial_Teacher_Monochrome.pdf). Use `build.py --monochrome` to reproduce them. Both editions were visually checked page by page. The build verifies that all rendered channels are equal and archives the [layout and hashes](layout_monochrome.json).

The separate manuscripts draw on the frozen [V46 checkpoint](../../../CHECKPOINT_2026-11-19.md) and [V47 checkpoint](../../../CHECKPOINT_V47.md). The existing longer V46 article remains at its prior path. The documents use an anonymous manuscript layout and a numbered bibliography.

Run `python -B results/2026-11-19/short_papers/build.py` from the repository root with ReportLab, pdfplumber, pypdfium2 and the named Windows fonts. The templates are `v46.md`, `v47.md` and the shared exact-optimizer section `outer.md`. The build produces complete Markdown sources and the PDFs. [Layout records](layout.json) include PDF and PNG hashes.

## Page check

Each final PDF was inspected at the archived render size.

| Page | V46 | V47 |
|---|---|---|
| 1 | Title, abstract counts, problem statement, projection lemma | Title, abstract comparisons, problem statement, projection lemma |
| 2 | Local rows, forest conditioning, enumeration formula | Pseudocode, invariant, equivalence boundary, cost |
| 3 | Cuts, SAT recurrence, exactness and checked upper bound | Cuts, SAT recurrence, exactness and checked upper bound |
| 4 | Tables, resource limits, observed enumeration, independent audits | Matched results, certificate and master pressure, audit scope |
| 5 | Discussion, reproducibility and bibliography | Hardness reduction, conclusion and bibliography |
