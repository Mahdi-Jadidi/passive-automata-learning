"""Promote theory report after independent master acceptance; retain all drafts."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'theory/SCIENTIFIC_REPORT_CANDIDATE_FA_v3.md'
raw=source.read_bytes();text=raw.decode('utf-8')
text=text.replace('**وضعیت:** نامزد گزارش علمی پس از پذیرش گیت مستقلِ runtime منجمد v5.', '**وضعیت:** گزارش پذیرفته‌شدهٔ صحت، پس از بازبینی مستقل و تصمیم مستر.',1)
text+='\n\nشواهد مستقیم: [گیت حل‌گر](audit/validation_v2/solver_v5_gate_v6.json)، [oracle همهٔ kها](audit/validation_v1/oracle_crosscheck.json)، [بازپخش رابط](audit/validation_v2/root_cli_v1.json)، [اثبات‌های اصلی](theory/PROOFS_v1.md)، [قواعد افزودهٔ غیرفعال](theory/ENHANCED_RULES_PROOFS_v1.md)، [منابع](theory/SOURCES_v1.md)، [راهنمای اجرا](README_FA.md)، [تصمیم مستر](MASTER_DECISION_FA.md).\n'
with (ROOT/'RESEARCH_REPORT_FA.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
with (ROOT/'coordination/report_promotion.json').open('x',encoding='utf-8') as f:
 json.dump(dict(source=str(source.relative_to(ROOT)),source_sha256=sha256(raw).hexdigest(),target='RESEARCH_REPORT_FA.md',target_sha256=sha256((ROOT/'RESEARCH_REPORT_FA.md').read_bytes()).hexdigest()),f,indent=2)
print('Scientific report promoted')
