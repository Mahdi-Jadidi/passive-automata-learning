# Paper section document QA v1

## Deliverables

- DOCX: `document/output/Exact_Alphabet_Partitioning_Method_EN.docx`
- PDF: `document/output/Exact_Alphabet_Partitioning_Method_EN.pdf`

The DOCX was built from the approved English source SHA-256 `8009AF278F09837E1CC8B5F9744D93601414F756B63F5417A289DDCAC317DEC2` and numbered pseudocode SHA-256 `4F87F5ED50CDAFD53D8F02DCBF6D4CDB32B00030E3A2834B4295F8BE88D002DF`.

## Readback and structure

- DOCX SHA-256: `7e5547d68ea0e2e48eb2cf7f8e2492528df5d4923491baeccc658c9e5ed1e0da` (45,804 bytes).
- PDF SHA-256: `b065a4bda4d49b664b69a293e6274088535a0422cabfa8915924618397cd9552` (546,872 bytes).
- Full document text readback matches the approved English source after Markdown syntax is removed and display equations are read from their native subscript/superscript runs.
- All 37 numbered pseudocode statements match `NUMBERED_PSEUDOCODE.txt` exactly, line by line.
- Three display equations are editable native Word OMML: five subscripts and one superscript. Readback retains `Σ*`, `B*`, `∅`, `ε`, `≤`, `≠`, `⊆`, `∈`, `∀`, `∃`, `H_B`, `C`, `O`, and `NONE`.
- Both external references link to the versioned arXiv v3 page and the PMLR paper page.
- Word metadata and A4 page dimensions were checked. Output directory contains only the final DOCX and PDF.

The original render exposed two formatting faults: the first inline-Markdown parser removed Kleene stars, and the initial code-table column widths clipped a long pseudocode row. The parser now restricts emphasis to unambiguous prose delimiters, preserving mathematical stars; the table widths and title/table styles were corrected. The original defective DOCX, PDF and five page renders remain under `audit/preqa_v1/` for traceability. The final DOCX text readback and all 37 pseudocode lines pass.

## Render and visual review

The required `render_docx.py` call was attempted and failed with `FileNotFoundError: LibreOffice soffice.exe was not found on PATH`. The runtime override/fallback inventory contains Poppler utilities but no LibreOffice. A hidden, separate Microsoft Word COM instance exported the DOCX to PDF; `pdfinfo` confirms five A4 pages and identifies Microsoft Word as the PDF producer. The bundled Poppler `pdftoppm.exe` rendered all five pages at 144 dpi. I inspected every page image at original resolution after the final rebuild; no clipping, overlap, missing equation glyphs, or table overflow remains. PNGs and raw render evidence are under `document/render/`.

Exact authoring and verification commands, executable paths, final asset hashes, readback output, and page image hashes are recorded in `DOCUMENT_BUILD_MANIFEST_V1.json`.

Biggest thing overlooked? Markdown emphasis delimiters can coincide with mathematical asterisks. The final parser protects the Kleene-star notation and the readback checks the exact symbols.
