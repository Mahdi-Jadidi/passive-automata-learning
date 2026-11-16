"""Typeset the approved C029 English paper section as an editable DOCX."""
from pathlib import Path
import re
import sys

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "PAPER_SECTION_EN.md"
PSEUDO = ROOT / "content" / "NUMBERED_PSEUDOCODE.txt"
OUT = Path(__file__).resolve().parent / "output" / "Exact_Alphabet_Partitioning_Method_EN.docx"

MATH = "http://schemas.openxmlformats.org/officeDocument/2006/math"
XML = "http://www.w3.org/XML/1998/namespace"


def math_run(parent, text, normal=False):
    r = OxmlElement("m:r")
    if normal:
        rpr = OxmlElement("m:rPr")
        rpr.append(OxmlElement("m:nor"))
        r.append(rpr)
    t = OxmlElement("m:t")
    t.set("{%s}space" % XML, "preserve")
    t.text = text
    r.append(t)
    parent.append(r)


def script_node(parent, typ, base, script):
    node = OxmlElement("m:" + typ)
    node.append(OxmlElement("m:" + typ + "Pr"))
    e = OxmlElement("m:e")
    math_run(e, base)
    node.append(e)
    which = "sub" if typ == "sSub" else "sup"
    child = OxmlElement("m:" + which)
    math_run(child, script)
    node.append(child)
    parent.append(node)


def equation_paragraph(doc, parts):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(8)
    mp = OxmlElement("m:oMathPara")
    mpr = OxmlElement("m:oMathParaPr")
    jc = OxmlElement("m:jc")
    jc.set(qn("m:val"), "center")
    mpr.append(jc)
    mp.append(mpr)
    om = OxmlElement("m:oMath")
    for kind, value, extra in parts:
        if kind == "text":
            math_run(om, value)
        else:
            script_node(om, kind, value, extra)
    mp.append(om)
    p._p.append(mp)
    return p


def display_equation(doc, text):
    s = " ".join(text.split())
    if s.startswith("L(Π,"):
        return equation_paragraph(doc, [
            ("text", "L(Π, (", ""), ("sSub", "F", "B"),
            ("text", ")) = {w ∈ ", ""), ("sSup", "Σ", "*"),
            ("text", " : ∀ B ∈ Π, ", ""), ("sSub", "π", "B"),
            ("text", "(w) ∈ ", ""), ("sSub", "F", "B"), ("text", "}.", "")])
    if s.startswith("max {"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(8)
        mp = OxmlElement("m:oMathPara")
        om = OxmlElement("m:oMath")
        math_run(om, "max { |Π| : Π is ")
        math_run(om, "sample-compatible", normal=True)
        math_run(om, " }.")
        mp.append(om)
        p._p.append(mp)
        return p
    if s.startswith("∀n") or s.startswith("∀ n"):
        return equation_paragraph(doc, [
            ("text", "∀ n ∈ N  ∃ B ∈ Π  ∀ p ∈ P : ", ""),
            ("sSub", "π", "B"), ("text", "(n) ≠ ", ""), ("sSub", "π", "B"),
            ("text", "(p).       (1)", "")])
    raise ValueError("Unrecognized display equation; refusing to flatten math: " + s)


# Markdown emphasis is recognized only with nonwhitespace content adjacent to
# both delimiters. This leaves mathematical Kleene stars in Σ* and B* literal.
INLINE_RE = re.compile(r"(\*\*[^*]+?\*\*|\*(?=\S)[^*]*?\S\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    rid = part.relate_to(url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1F4E79")
    rpr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    rpr.append(underline)
    run.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    run.append(t)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_inline(paragraph, text):
    cursor = 0
    for match in INLINE_RE.finditer(text):
        if match.start() > cursor:
            paragraph.add_run(text[cursor:match.start()])
        token = match.group(0)
        if token.startswith("**"):
            r = paragraph.add_run(token[2:-2]); r.bold = True
        elif token.startswith("*"):
            r = paragraph.add_run(token[1:-1]); r.italic = True
        elif token.startswith("`"):
            r = paragraph.add_run(token[1:-1]); r.font.name = "Cascadia Mono"; r.font.size = Pt(9)
        else:
            m = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", token)
            add_hyperlink(paragraph, m.group(1), m.group(2))
        cursor = match.end()
    if cursor < len(text):
        paragraph.add_run(text[cursor:])


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=70, start=100, bottom=70, end=100):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for edge, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn("w:" + edge))
        if node is None:
            node = OxmlElement("w:" + edge)
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def cant_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    tr_pr.append(el)


def repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    tr_pr.append(el)


def cell_text(cell, text, *, code=False, header=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(text)
    r.bold = header
    if code:
        r.font.name = "Cascadia Mono"
        r.font.size = Pt(8.2)
    else:
        r.font.name = "Cambria"
        r.font.size = Pt(9.2 if not header else 9.4)
    r.font.color.rgb = RGBColor(0, 0, 0)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_margins(cell)


def pseudocode_table(doc, pseudo_text):
    lines = [line.rstrip() for line in pseudo_text.splitlines() if line.strip()]
    parsed = []
    for line in lines:
        m = re.fullmatch(r"\s*(\d{2})\s+(.*)", line)
        if not m:
            raise ValueError("Unexpected pseudocode line: " + line)
        parsed.append((m.group(1), m.group(2)))
    table = doc.add_table(rows=1, cols=2)
    table.autofit = False
    table.columns[0].width = Inches(0.42)
    table.columns[1].width = Inches(6.12)
    table.style = "Table Grid"
    header = table.rows[0]
    repeat_table_header(header)
    cant_split(header)
    cell_text(header.cells[0], "Line", header=True)
    cell_text(header.cells[1], "Pseudocode", header=True)
    set_cell_shading(header.cells[0], "E7EBF0")
    set_cell_shading(header.cells[1], "E7EBF0")
    for line_no, statement in parsed:
        row = table.add_row()
        cant_split(row)
        cell_text(row.cells[0], line_no, code=True)
        cell_text(row.cells[1], statement, code=True)
    for row in table.rows:
        row.cells[0].width = Inches(0.42)
        row.cells[1].width = Inches(6.12)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)


def markdown_table(doc, lines):
    rows = []
    for line in lines:
        if not line.strip() or re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?", line.strip()):
            continue
        rows.append([x.strip() for x in line.strip().strip("|").split("|")])
    if not rows:
        return
    table = doc.add_table(rows=1, cols=len(rows[0]))
    table.style = "Table Grid"
    table.autofit = False
    widths = [Inches(0.85), Inches(5.69)] if len(rows[0]) == 2 else [Inches(6.54 / len(rows[0]))] * len(rows[0])
    for j, width in enumerate(widths):
        table.columns[j].width = width
    row = table.rows[0]
    repeat_table_header(row); cant_split(row)
    for i, value in enumerate(rows[0]):
        cell_text(row.cells[i], value, header=True)
        set_cell_shading(row.cells[i], "E7EBF0")
    for data in rows[1:]:
        cells = table.add_row().cells
        cant_split(table.rows[-1])
        for i, value in enumerate(data):
            cell_text(cells[i], value)
    for row in table.rows:
        for i, width in enumerate(widths):
            row.cells[i].width = width
    doc.add_paragraph()


def configure(doc):
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.0); sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.1); sec.right_margin = Cm(2.1)
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Cambria"; normal.font.size = Pt(10.5); normal.font.color.rgb = RGBColor(0,0,0)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Cambria")
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.08
    normal.paragraph_format.widow_control = True
    for name, size in (("Title", 20), ("Heading 1", 14), ("Heading 2", 11.5), ("Heading 3", 10.8)):
        st = styles[name]
        st.font.name = "Cambria"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0,0,0)
        st._element.rPr.rFonts.set(qn("w:eastAsia"), "Cambria")
        st.paragraph_format.keep_with_next = True
    title_ppr = styles["Title"]._element.get_or_add_pPr()
    title_border = title_ppr.find(qn("w:pBdr"))
    if title_border is not None:
        title_ppr.remove(title_border)
    styles["Title"].paragraph_format.space_after = Pt(12)
    styles["Heading 1"].paragraph_format.space_before = Pt(12)
    styles["Heading 1"].paragraph_format.space_after = Pt(5)
    styles["Heading 2"].paragraph_format.space_before = Pt(8)
    styles["Heading 2"].paragraph_format.space_after = Pt(4)


def build():
    md = CONTENT.read_text(encoding="utf-8")
    pseudo = PSEUDO.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    fences = re.findall(r"```text\s*\n(.*?)\n```", md, flags=re.S)
    if len(fences) != 1 or fences[0].strip() != pseudo:
        raise ValueError("Approved English pseudocode block differs from frozen numbered pseudocode")
    doc = Document()
    configure(doc)
    lines = md.replace("\r\n", "\n").splitlines()
    i = 0
    in_code = False
    in_table = False
    while i < len(lines):
        raw = lines[i]
        if raw.startswith("```text"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i]); i += 1
            pseudocode_table(doc, "\n".join(block))
            i += 1
            continue
        if raw.startswith("|"):
            tab = []
            while i < len(lines) and lines[i].startswith("|"):
                tab.append(lines[i]); i += 1
            markdown_table(doc, tab)
            continue
        if not raw.strip():
            i += 1
            continue
        if raw.startswith("# "):
            p = doc.add_paragraph(style="Title")
            add_inline(p, raw[2:].strip())
            i += 1; continue
        if raw.startswith("## "):
            p = doc.add_paragraph(style="Heading 1")
            add_inline(p, raw[3:].strip())
            i += 1; continue
        if raw.startswith("### "):
            p = doc.add_paragraph(style="Heading 2")
            add_inline(p, raw[4:].strip())
            i += 1; continue
        if raw.startswith("#### "):
            p = doc.add_paragraph(style="Heading 3")
            add_inline(p, raw[5:].strip())
            i += 1; continue
        if raw.startswith("    "):
            display_equation(doc, raw[4:].strip())
            i += 1; continue
        para_lines = [raw.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "|", "```", "    ")):
            para_lines.append(lines[i].strip())
            i += 1
        text = " ".join(para_lines)
        p = doc.add_paragraph()
        if text.startswith("**Theorem ") or text.startswith("**Proof.") or text.startswith("**Termination"):
            p.paragraph_format.keep_together = True
        add_inline(p, text)
    doc.core_properties.title = "Exact Sample Compatible Partitioning by Exhaustive Enumeration"
    doc.core_properties.subject = "A paper section on finite-sample compatible partitioning"
    doc.core_properties.keywords = "partitioning, exhaustive enumeration, regular languages, restricted-growth strings"
    doc.save(OUT)
    print(f"saved={OUT}")


if __name__ == "__main__":
    build()
