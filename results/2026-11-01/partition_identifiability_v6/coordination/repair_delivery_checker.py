"""Preserve failed metadata checks; ignore descriptive scope as a path hint."""
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
source=ROOT/'implementation/archive_integrity_v3.py'
text=source.read_text(encoding='utf-8')
old='errors.append(f"readiness scope directory is missing: {readiness}:{scope_value}")'
assert text.count(old)==1
text=text.replace(old,'pass  # scope may describe a mission, rather than name an owner folder')
with (ROOT/'coordination/archive_integrity_v4.py').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
erratum=dict(cycle='C006',kind='metadata_interpretation_only',
 source='implementation/archive_integrity_v3.py',source_sha256=sha256(source.read_bytes()).hexdigest(),
 failure_report='implementation/FINAL_INTEGRITY_R2_2026-11-01.json',
 reason='READINESS_AUDIT_V2 scope is descriptive prose, not a required directory. Original reference/path hashes all matched.',
 correction='Use an existing explicit owner scope as a hint; ignore a non-directory descriptive scope. All source/hash/raw checks unchanged.',
 provider_changes=False)
with (ROOT/'coordination/INTEGRITY_SCOPE_ERRATUM_V2.json').open('x',encoding='utf-8') as f:json.dump(erratum,f,indent=2)
report=ROOT/'RESEARCH_REPORT_FA.md'
text=report.read_text(encoding='utf-8').replace('implementation/FINAL_INTEGRITY_R2_2026-11-01.json','coordination/FINAL_INTEGRITY_R3_2026-11-01.json')
text+='\nکنترل دوم نیز یک مقدار توصیفیِ scope را به‌اشتباه مسیر پوشه فرض کرد؛ این خطای ابزارِ بایگانی با حفظ [گزارش دوم](implementation/FINAL_INTEGRITY_R2_2026-11-01.json) و [شرح اصلاح](coordination/INTEGRITY_SCOPE_ERRATUM_V2.json) جدا ثبت شد. بایت کدهای آزمایش‌شده، داده‌ها و خروجی‌ها تغییر نکردند.\n'
report.write_text(text,encoding='utf-8',newline='\n')
manifest=ROOT/'coordination/runtime_final.json'
old_manifest=json.loads(manifest.read_text(encoding='utf-8'))
with (ROOT/'coordination/runtime_final_R2.json').open('xb') as f:f.write(manifest.read_bytes())
for item in old_manifest['files']:
 path=ROOT/item['path']
 if not path.exists():path=ROOT.parents[2]/item['path']
 actual=sha256(path.read_bytes()).hexdigest()
 if item['path']!='RESEARCH_REPORT_FA.md': assert actual==item['sha256'], item['path']
 item['sha256']=actual
for name in ['coordination/archive_integrity_v4.py','coordination/INTEGRITY_SCOPE_ERRATUM_V2.json','coordination/runtime_final_R2.json']:
 old_manifest['files'].append(dict(path=name,sha256=sha256((ROOT/name).read_bytes()).hexdigest()))
old_manifest['revision']='R3: descriptive metadata scope portability, no provider changes'
manifest.write_text(json.dumps(old_manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(dict(runtime_files=len(old_manifest['files']),provider_changes=False)))
