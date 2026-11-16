"""Full article DOCX/PDF readback against the frozen English source files."""
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

import pdfplumber
from docx import Document
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "content" / "ARTICLE_EN.md"
PSEUDO = ROOT / "content" / "NUMBERED_PSEUDOCODE.txt"
INVENTORY = ROOT / "content" / "EQUATION_INVENTORY_V1.md"
DOCX = ROOT / "audit" / "work" / "v2" / "Exact_Alphabet_Partitioning_Article_EN.docx"
PDF = ROOT / "audit" / "render" / "v2" / "Exact_Alphabet_Partitioning_Article_EN.pdf"
TEXT_OUT = ROOT / "audit" / "PDF_TEXT_READBACK_V2.txt"
JSON_OUT = ROOT / "audit" / "READBACK_QA_V2.json"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "m": M}
EXPECTED_HASHES = {
    "ARTICLE_EN.md": "43a786ba43256db277d76d80986a58a7506721c8b91d71f2c9755fe694c1e6af",
    "NUMBERED_PSEUDOCODE.txt": "4f87f5ed50cdafd53d8f02dcbf6d4cdb32b00030e3a2834b4295f8be88d002df",
    "EQUATION_INVENTORY_V1.md": "56e440a8c310060ea293f5bce8ba6f6e01b351e1365bdf2073b1b7856e3a6332",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_inline(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\*\*([^*]+?)\*\*", r"\1", text)
    text = re.sub(r"\*(?=\S)([^*]*?\S)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def source_math_to_ooxml_text(text, *, display=False):
    text = re.sub(r"0\^\(([^)]+)\)", r"0\1", text)
    text = text.replace("0^m", "0m")
    text = text.replace("⋃_{B∈Π}", "⋃B∈Π")
    for old, new in (("F_B", "FB"), ("H_B", "HB"), ("V_B", "VB"),
                     ("π_B", "πB"), ("π_D", "πD"), ("Σ_k", "Σk"), ("n_j", "nj")):
        text = text.replace(old, new)
    if display:
        for old, new in (("₀", "0"), ("₁", "1"), ("ᵢ", "i"), ("ₘ", "m"), ("₋", "−")):
            text = text.replace(old, new)
    return text


def expected_stream(source):
    out = []
    in_code = False
    lines = source.replace("\r\n", "\n").splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        if raw.startswith("```text"):
            in_code = True
            out.extend(["Line", "Pseudocode"])
            i += 1
            continue
        if in_code and raw.startswith("```"):
            in_code = False
            i += 1
            continue
        if in_code:
            m = re.fullmatch(r"(\d{2})( {2,})(.*)", raw)
            assert m, raw
            out.extend([m.group(1), m.group(3)])
            i += 1
            continue
        if not raw.strip():
            i += 1
            continue
        if raw.startswith("|"):
            if not re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", raw.strip()):
                out.extend(source_math_to_ooxml_text(strip_inline(x.strip()))
                           for x in raw.strip().strip("|").split("|"))
            i += 1
            continue
        if raw.startswith("# "):
            out.append(source_math_to_ooxml_text(strip_inline(raw[2:].strip())))
            i += 1
            continue
        if raw.startswith("## "):
            out.append(source_math_to_ooxml_text(strip_inline(raw[3:].strip())))
            i += 1
            continue
        if raw.startswith("### "):
            out.append(source_math_to_ooxml_text(strip_inline(raw[4:].strip())))
            i += 1
            continue
        if raw.startswith("#### "):
            out.append(source_math_to_ooxml_text(strip_inline(raw[5:].strip())))
            i += 1
            continue
        if raw.startswith("    "):
            out.append(source_math_to_ooxml_text(raw[4:].strip(), display=True))
            i += 1
            continue
        paragraph = [raw.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|", "```", "    ")):
            paragraph.append(lines[i].strip())
            i += 1
        out.append(source_math_to_ooxml_text(strip_inline(" ".join(paragraph))))
    return "".join(out)


def normalize_stream(text):
    return re.sub(r"\s+", "", text)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    for path in (SRC, PSEUDO, INVENTORY):
        actual = sha(path)
        assert actual == EXPECTED_HASHES[path.name], (path.name, actual)

    with ZipFile(DOCX) as zf:
        xml = etree.fromstring(zf.read("word/document.xml"))
    got_docx = "".join(node.text or "" for node in xml.xpath(".//w:t|.//m:t", namespaces=NS))
    want_docx = expected_stream(SRC.read_text(encoding="utf-8"))
    assert normalize_stream(got_docx) == normalize_stream(want_docx), "DOCX full text differs from approved source"

    doc = Document(DOCX)
    pseudo_lines = []
    for line in PSEUDO.read_text(encoding="utf-8").replace("\r\n", "\n").splitlines():
        m = re.fullmatch(r"(\d{2})( {2,})(.*)", line)
        assert m, line
        pseudo_lines.append((m.group(1), m.group(3), len(m.group(2)) - 2))
    table = doc.tables[0]
    assert len(pseudo_lines) == 37 and len(table.rows) == 38
    row_matches = []
    for expected, row in zip(pseudo_lines, table.rows[1:]):
        line_no, statement, indent_spaces = expected
        assert row.cells[0].text.strip() == line_no
        assert row.cells[1].text == statement
        indent = row.cells[1].paragraphs[0].paragraph_format.left_indent
        twips = 0 if indent is None else int(round(indent.pt * 20))
        expected_twips = indent_spaces * 108
        assert twips == expected_twips, (line_no, twips, expected_twips)
        row_matches.append({"line": line_no, "text_exact": True,
                            "source_indent_spaces": indent_spaces,
                            "docx_indent_twips": twips})

    formulas = ["".join(node.xpath(".//m:t/text()", namespaces=NS))
                for node in xml.xpath(".//m:oMathPara/m:oMath", namespaces=NS)]
    expected_formulas = [
        "L(Π,(FB))={w∈Σ*:∀B∈Π,πB(w)∈FB}.(1)",
        "C=|𝒱(P,N)|,   k*=max{|Π|:Π∈𝒱(P,N)},",
        "O=|{Π∈𝒱(P,N):|Π|=k*}|. (2)",
        "HB={πB(p):p∈P},     R(B)={n∈N: πB(n)∉HB}. (3)",
        "∀n∈N ∃B∈Π ∀p∈P: πB(n)≠πB(p),",
        "equivalently ⋃B∈Π R(B)=N. (4)",
        "s1=0,   0≤si≤1+max{s1,…,si−1}   for 2≤i≤m. (5)",
        "VB[j]=true iff πB(nj)∉HB. (6)",
    ]
    compact = lambda s: re.sub(r"\s+", "", s)
    assert len(formulas) == len(expected_formulas) == 8
    assert [compact(x) for x in formulas] == [compact(x) for x in expected_formulas], (formulas, expected_formulas)
    assert len(xml.xpath(".//m:sSub", namespaces=NS)) >= 17
    assert len(xml.xpath(".//m:sSup", namespaces=NS)) >= 3
    w_text = "".join(x.text or "" for x in xml.xpath(".//w:t", namespaces=NS))
    all_text = got_docx
    for token in ("Σ*", "B*", "∅", "ε", "≤", "≠", "⊆", "∈", "∀", "∃", "HB", "C", "O", "NONE"):
        assert token in source_math_to_ooxml_text(all_text) or token in all_text, token
    for status in ("UNIQUE_COMPATIBLE", "INVALID_INPUT", "INCOMPATIBLE", "INCOMPLETE", "ERROR"):
        assert status in w_text, status

    with pdfplumber.open(PDF) as pdf:
        pdf_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        page_count = len(pdf.pages)
    assert page_count == 10, page_count
    pdf_compact = re.sub(r"\s+", "", pdf_text)
    for token in ("Σ", "∀", "∃", "≠", "⊆", "∈", "∅", "ε", "UNIQUE_COMPATIBLE", "INVALID_INPUT"):
        assert token in pdf_text, token
    assert all(f"({n})" in pdf_text for n in range(1, 7))
    for line_no, statement, indent_spaces in pseudo_lines:
        code = re.sub(r"\s+", "", statement)
        assert code in pdf_compact, (line_no, statement)
    assert "Theorem 5 (memo equivalence)" in pdf_text
    assert "Appendix A. Reproducibility and provenance" in pdf_text
    assert "References" in pdf_text
    TEXT_OUT.write_text(pdf_text, encoding="utf-8")
    result = {
        "status": "PASS", "approved_source_hashes": EXPECTED_HASHES,
        "docx_sha256": sha(DOCX), "pdf_sha256": sha(PDF), "pdf_pages": page_count,
        "complete_docx_text_matches_source": True,
        "numbered_pseudocode_rows_exact": len(row_matches),
        "pseudocode_source_indentation_compared": True,
        "pseudocode_indentation_rows": row_matches,
        "display_omml_equation_lines": len(formulas), "display_formula_readback": formulas,
        "omml_subscripts": len(xml.xpath(".//m:sSub", namespaces=NS)),
        "omml_superscripts": len(xml.xpath(".//m:sSup", namespaces=NS)),
        "status_tokens_literal_in_word_runs": True,
        "pdf_text_chars": len(pdf_text), "pdf_critical_tokens_checked": True,
        "pdf_text_readback": TEXT_OUT.name,
    }
    JSON_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
