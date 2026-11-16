"""Readback, mathematics, pseudocode, links, and package checks for the DOCX."""
from pathlib import Path
import hashlib
import json
import re
from zipfile import ZipFile

from docx import Document
from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "document" / "output" / "Exact_Alphabet_Partitioning_Method_EN.docx"
EN = ROOT / "content" / "PAPER_SECTION_EN.md"
PSEUDO = ROOT / "content" / "NUMBERED_PSEUDOCODE.txt"
OUT = Path(__file__).resolve().parent / "DOCX_READBACK_V1.json"
TEXT_OUT = Path(__file__).resolve().parent / "DOCX_TEXT_READBACK_V1.txt"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"w": W, "m": M, "r": R}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def strip_inline(text):
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"\*\*([^*]+?)\*\*", r"\1", text)
    text = re.sub(r"\*(?=\S)([^*]*?\S)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def expected_text(source):
    out, in_code = [], False
    for raw in source.replace("\r\n", "\n").splitlines():
        if raw.startswith("```text"):
            in_code = True
            out.extend(["Line", "Pseudocode"])
            continue
        if raw.startswith("```") and in_code:
            in_code = False
            continue
        if in_code:
            m = re.fullmatch(r"\s*(\d{2})\s+(.*)", raw)
            if not m:
                raise AssertionError("unexpected pseudocode source line: " + raw)
            out.extend(m.groups())
            continue
        if not raw.strip():
            continue
        if raw.startswith("|"):
            if re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", raw.strip()):
                continue
            out.extend(strip_inline(x.strip()) for x in raw.strip().strip("|").split("|"))
            continue
        if raw.startswith("# "):
            raw = raw[2:]
        elif raw.startswith("## "):
            raw = raw[3:]
        elif raw.startswith("### "):
            raw = raw[4:]
        elif raw.startswith("#### "):
            raw = raw[5:]
        elif raw.startswith("    "):
            raw = raw[4:].strip()
            # These indices become structural OMML sub/superscripts.
            raw = raw.replace("F_B", "FB").replace("π_B", "πB")
        else:
            raw = raw.strip()
        out.append(strip_inline(raw))
    return "".join(out)


def main():
    doc = Document(DOC)
    with ZipFile(DOC) as z:
        xml = etree.fromstring(z.read("word/document.xml"))
        rels = etree.fromstring(z.read("word/_rels/document.xml.rels"))
        styles = etree.fromstring(z.read("word/styles.xml"))
        content_types = etree.fromstring(z.read("[Content_Types].xml"))
    got_text = "".join(node.text or "" for node in xml.xpath(".//w:t|.//m:t", namespaces=NS))
    want_text = expected_text(EN.read_text(encoding="utf-8"))
    normalize = lambda s: re.sub(r"\s+", "", s)
    assert normalize(got_text) == normalize(want_text), "document text differs from approved markdown after documented equation serialization"

    # Read the full numbered pseudocode back from the first table, row by row.
    expected_code = []
    for line in PSEUDO.read_text(encoding="utf-8").replace("\r\n", "\n").splitlines():
        if line.strip():
            m = re.fullmatch(r"\s*(\d{2})\s+(.*)", line)
            assert m
            expected_code.append((m.group(1), m.group(2)))
    assert len(expected_code) == 37
    code_table = doc.tables[0]
    assert len(code_table.rows) == 38
    actual_code = [(row.cells[0].text.strip(), row.cells[1].text.strip()) for row in code_table.rows[1:]]
    assert actual_code == expected_code, (actual_code, expected_code)

    # Verify the key display and inline mathematical forms in searchable text.
    for token in ["Σ*", "B*", "∅", "ε", "≤", "≠", "⊆", "∈", "∀", "∃", "H_B", "C", "O", "NONE"]:
        assert token in got_text, "missing math/text token: " + token
    omath = xml.xpath(".//m:oMath", namespaces=NS)
    assert len(omath) == 3, f"expected 3 native display equations, got {len(omath)}"
    assert len(xml.xpath(".//m:sSub", namespaces=NS)) >= 5
    assert len(xml.xpath(".//m:sSup", namespaces=NS)) >= 1
    formulas = ["".join(x.xpath(".//m:t/text()", namespaces=NS)) for x in omath]
    assert "Σ*" in formulas[0] and "πB" in formulas[0]
    assert "sample-compatible" in formulas[1]
    assert formulas[2].count("∀") == 2 and "∃" in formulas[2] and "≠" in formulas[2]

    links = {r.get("Id"): r.get("Target") for r in rels if r.get("Type", "").endswith("/hyperlink")}
    assert "https://arxiv.org/html/2504.16624v3" in links.values()
    assert "https://proceedings.mlr.press/v93/moerman19a.html" in links.values()

    sect = xml.xpath(".//w:sectPr/w:pgSz", namespaces=NS)[0]
    width, height = int(sect.get("{%s}w" % W)), int(sect.get("{%s}h" % W))
    assert (width, height) == (11906, 16838), (width, height)
    title_style = styles.xpath('.//w:style[@w:styleId="Title"]', namespaces=NS)[0]
    assert not title_style.xpath(".//w:pBdr", namespaces=NS), "Title style still has a border"
    # Package includes editable OMML and no rasterized equation drawings.
    assert not xml.xpath(".//w:drawing", namespaces=NS)
    assert "word/document.xml" in ZipFile(DOC).namelist()

    TEXT_OUT.write_text(got_text, encoding="utf-8")
    result = {"status": "passed", "docx_sha256": digest(DOC),
              "approved_english_sha256": digest(EN), "approved_pseudocode_sha256": digest(PSEUDO),
              "document_text_matches_approved_content": True, "pseudocode_lines_checked": len(expected_code),
              "native_equations": len(omath), "subscripts": len(xml.xpath(".//m:sSub", namespaces=NS)),
              "superscripts": len(xml.xpath(".//m:sSup", namespaces=NS)),
              "hyperlinks": sorted(links.values()), "page_size_twips": [width, height],
              "readback_file": TEXT_OUT.name}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
