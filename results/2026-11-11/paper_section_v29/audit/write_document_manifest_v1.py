"""Freeze final paper DOCX/PDF and QA evidence hashes."""
from pathlib import Path
import hashlib
import json
import platform
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORKSPACE = ROOT.parents[1]
FILES = [
    ROOT / "content" / "PAPER_SECTION_EN.md",
    ROOT / "content" / "WALKTHROUGH_FA.md",
    ROOT / "content" / "NUMBERED_PSEUDOCODE.txt",
    ROOT / "review" / "FINAL_CONTENT_VERDICT.md",
    ROOT / "review" / "DOCX_MATH_VERDICT.md",
    ROOT / "document" / "build_docx_v1.py",
    ROOT / "document" / "render_with_word.ps1",
    ROOT / "document" / "output" / "Exact_Alphabet_Partitioning_Method_EN.docx",
    ROOT / "document" / "output" / "Exact_Alphabet_Partitioning_Method_EN.pdf",
    ROOT / "document" / "render" / "Exact_Alphabet_Partitioning_Method_EN.pdf",
    ROOT / "document" / "render" / "page-1.png",
    ROOT / "document" / "render" / "page-2.png",
    ROOT / "document" / "render" / "page-3.png",
    ROOT / "document" / "render" / "page-4.png",
    ROOT / "document" / "render" / "page-5.png",
    HERE / "docx_readback_qa_v1.py",
    HERE / "DOCX_READBACK_V1.json",
    HERE / "DOCX_TEXT_READBACK_V1.txt",
    HERE / "DOCUMENT_QA_REPORT_V1.md",
    HERE / "preqa_v1" / "Exact_Alphabet_Partitioning_Method_EN.docx",
    HERE / "preqa_v1" / "Exact_Alphabet_Partitioning_Method_EN.pdf",
    *sorted((HERE / "preqa_v1").glob("page-*.png")),
]

def info(path):
    raw = path.read_bytes()
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}

docx = ROOT / "document" / "output" / "Exact_Alphabet_Partitioning_Method_EN.docx"
pdf = ROOT / "document" / "output" / "Exact_Alphabet_Partitioning_Method_EN.pdf"
out = {
    "audit": "C029 English paper-section document build and visual QA",
    "python": sys.version,
    "platform": platform.platform(),
    "python_docx": "1.2.0",
    "approved_sha256": {
        "english": "8009af278f09837e1cc8b5f9744d93601414f756b63f5417a289ddcac317dec2",
        "persian_walkthrough": "ce8b787b3c45805c190d27ec3230488bfc7024f136764333ad7c0322d9164947",
        "numbered_pseudocode": "4f87f5ed50cdaf d53d8f02dcbf6d4cdb32b00030e3a2834b4295f8be88d002df".replace(" ", ""),
    },
    "deliverables": {"docx_sha256": hashlib.sha256(docx.read_bytes()).hexdigest(),
                     "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
                     "page_count": 5, "page_size": "A4"},
    "commands": [
        "C:\\Users\\Mahdi\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe build_docx_v1.py",
        "C:\\Users\\Mahdi\\Documents\\ChatGPT\\passive automata learning\\results\\2026-11-11\\paper_section_v29\\document\\render_with_word.ps1",
        "C:\\Users\\Mahdi\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\native\\poppler\\Library\\bin\\pdftoppm.exe -png -r 144 Exact_Alphabet_Partitioning_Method_EN.pdf page",
        "C:\\Users\\Mahdi\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe ..\\audit\\docx_readback_qa_v1.py",
    ],
    "packaged_renderer": {"attempted": True,
        "command": "C:\\Users\\Mahdi\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe C:\\Users\\Mahdi\\.codex\\plugins\\cache\\openai-primary-runtime\\documents\\26.1105.12137\\skills\\documents\\render_docx.py Exact_Alphabet_Partitioning_Method_EN.docx --output_dir render --emit_pdf",
        "outcome": "FileNotFoundError: LibreOffice soffice.exe was not found on PATH",
        "fallback": "Hidden Microsoft Word COM export from the exact DOCX to PDF, then bundled Poppler to five page PNGs"},
    "visual_review": "All five final Word-rendered page PNGs inspected at original resolution; final pagination, math, tables, and text fit cleanly.",
    "text_readback": json.loads((HERE / "DOCX_READBACK_V1.json").read_text(encoding="utf-8")),
    "files": [info(path) for path in FILES],
}
dest = HERE / "DOCUMENT_BUILD_MANIFEST_V1.json"
dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"manifest": dest.name, "files": len(FILES), "docx": out["deliverables"]["docx_sha256"],
                  "pdf": out["deliverables"]["pdf_sha256"]}, sort_keys=True))
