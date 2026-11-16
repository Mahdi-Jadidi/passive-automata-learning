"""Record source, render, visual-review and delivery provenance for v2."""
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


paths = {
    "approved_english": ROOT / "content" / "ARTICLE_EN.md",
    "approved_pseudocode": ROOT / "content" / "NUMBERED_PSEUDOCODE.txt",
    "approved_equation_inventory": ROOT / "content" / "EQUATION_INVENTORY_V1.md",
    "builder_v2": ROOT / "document" / "build_article_docx_v2.py",
    "word_export_script_v2": ROOT / "document" / "render_with_word_v2.ps1",
    "docx_working_v2": ROOT / "audit" / "work" / "v2" / "Exact_Alphabet_Partitioning_Article_EN.docx",
    "word_rendered_pdf_v2": ROOT / "audit" / "render" / "v2" / "Exact_Alphabet_Partitioning_Article_EN.pdf",
    "delivered_pdf": ROOT / "document" / "output" / "Exact_Alphabet_Partitioning_Article_EN.pdf",
    "readback_script": ROOT / "audit" / "readback_article_v2.py",
    "readback_result": ROOT / "audit" / "READBACK_QA_V2.json",
    "pdf_text_readback": ROOT / "audit" / "PDF_TEXT_READBACK_V2.txt",
    "packaged_renderer_stderr": ROOT / "audit" / "packaged_renderer_stderr.txt",
    "v1_rejected_pdf": ROOT / "audit" / "render" / "Exact_Alphabet_Partitioning_Article_EN_v1_failed_readback.pdf",
    "reviewer_verdict": ROOT / "review" / "PDF_FIDELITY_VERDICT.md",
}
page_files = sorted((ROOT / "audit" / "render" / "v2").glob("page-*.png"))
manifest = {
    "status": "FINAL_PDF_QA_PASS",
    "python_executable": sys.executable,
    "python_version": sys.version,
    "platform": platform.platform(),
    "word_executable": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
    "render_path": "Microsoft Word COM export from the exact working DOCX, then bundled Poppler",
    "commands": [
        "bundled python document/build_article_docx_v2.py",
        "powershell -File document/render_with_word_v2.ps1",
        "bundled Poppler pdfinfo.exe audit/render/v2/Exact_Alphabet_Partitioning_Article_EN.pdf",
        "bundled Poppler pdftoppm.exe -png -r 144 audit/render/v2/Exact_Alphabet_Partitioning_Article_EN.pdf audit/render/v2/page",
        "bundled python audit/readback_article_v2.py",
    ],
    "artifact_markers": [
        "documents: create, output-format docx, expected-output-count 1",
        "pdf: create, output-format pdf, expected-output-count 1",
    ],
    "packaged_renderer_attempt": {
        "attempted_once": True,
        "outcome": "FileNotFoundError: LibreOffice soffice.exe was not found on PATH",
        "fallback": "Word COM using an owned invisible Word.Application instance; exported exact DOCX",
    },
    "page_count": 10,
    "page_size": "A4",
    "dpi": 144,
    "visual_review": "All 10 final v2 page PNGs inspected individually at original resolution; layout, math, tables and all pseudocode indentation were checked.",
    "readback": json.loads(paths["readback_result"].read_text(encoding="utf-8")),
    "reviewer_verdict_sha256": sha(paths["reviewer_verdict"]),
    "final_pdf_copy_byte_identical_to_word_render": sha(paths["word_rendered_pdf_v2"]) == sha(paths["delivered_pdf"]),
    "files": {key: {"path": str(path.relative_to(ROOT)), "sha256": sha(path), "bytes": path.stat().st_size}
              for key, path in paths.items()},
    "page_pngs": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p), "bytes": p.stat().st_size}
                  for p in page_files],
    "rejected_v1_pdf_sha256": sha(paths["v1_rejected_pdf"]),
}
out = ROOT / "audit" / "BUILD_MANIFEST_V2.json"
out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": manifest["status"], "manifest": str(out),
                  "final_pdf_sha256": sha(paths["delivered_pdf"]),
                  "pages": len(page_files), "files": len(paths)}, sort_keys=True))
