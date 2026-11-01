"""Preserve final-manifest R1 and update delivery-only path audit metadata."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent.parent
report=ROOT/'RESEARCH_REPORT_FA.md'
text=report.read_text(encoding='utf-8')
text=text.replace('زمان‌گیری منتظر پیوست مستقل است؛ هیچ عدد سرعت یا حافظه از', 'پیوست مستقلِ زمان‌گیری در پایان همین گزارش آمده است؛ هیچ عدد سرعت یا حافظه از')
text=text.replace('نامزد حاضر برای ادغام و تصمیم مستر\nآماده است', 'گزارش حاضر پس از بازبینی مستر برای تحویل نهایی\nثبت شد')
text+='\n\nکنترل بایگانی: [نتیجهٔ نهایی](implementation/FINAL_INTEGRITY_R2_2026-11-01.json). بررسی نخست فقط یک ارجاعِ نسبیِ سند کپی‌شده را نادرست تفسیر کرد؛ فایل اصلی و هش درست آن موجود بود. [گزارش اولیهٔ حفظ‌شده](implementation/FINAL_INTEGRITY_2026-11-01.json) و [شرح مسیر و اصلاح ابزار](implementation/INTEGRITY_PATH_ERRATUM_V1.json) جدا باقی‌اند.\n'
report.write_text(text,encoding='utf-8',newline='\n')
manifest=ROOT/'coordination/runtime_final.json'
backup=ROOT/'coordination/runtime_final_R1.json'
with backup.open('xb') as f:f.write(manifest.read_bytes())
data=json.loads(manifest.read_text(encoding='utf-8'))
for entry in data['files']:
 path=ROOT/entry['path']
 if not path.exists():path=ROOT.parents[2]/entry['path']
 entry['sha256']=sha256(path.read_bytes()).hexdigest()
for p in ['implementation/archive_integrity_v3.py','implementation/INTEGRITY_PATH_ERRATUM_V1.json','coordination/runtime_final_R1.json']:
 data['files'].append(dict(path=p,sha256=sha256((ROOT/p).read_bytes()).hexdigest()))
data['revision']='R2 delivery checker path portability, no provider changes'
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(dict(final_files=len(data['files']))))
