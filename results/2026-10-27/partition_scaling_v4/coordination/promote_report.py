"""Promote the reviewed final branch report, retaining every draft unchanged."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent
WORKSPACE=ROOT.parents[2]
SOURCE=ROOT/'structural/C004_FINAL_REPORT_CANDIDATE_FA_REV3_FINAL.md'
TARGET=ROOT/'RESEARCH_REPORT_FA.md'
EXPECTED='82043d3949fe5af8225ad7ae159ff4e9ef2e6536cbf10a8446e11c1727729cff'
raw=SOURCE.read_bytes()
assert sha256(raw).hexdigest()==EXPECTED
assert not TARGET.exists(), 'Do not overwrite a promoted report'
changes=[]


def rebase(match):
    label,url=match.groups()
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',url) or url.startswith('#'):
        return match.group(0)
    name,sep,fragment=url.partition('#')
    path=(SOURCE.parent/name).resolve()
    path.relative_to(WORKSPACE)
    assert path.exists(),url
    destination=Path(os.path.relpath(path,ROOT)).as_posix()+(sep+fragment if sep else '')
    changes.append(dict(old=url,new=destination))
    return f'[{label}]({destination})'


text=raw.decode('utf-8-sig')
text=re.sub(r'\[([^\]\n]+)\]\(([^)\n]+)\)',rebase,text)
text=text.replace(text.splitlines()[0], '# گزارش نهایی C004: تریس‌های بلندتر، مؤلفه‌های بیشتر و فرض‌های ضعیف‌تر',1)
text=text.replace('[بازبینی استاد]', '[بازبینی مستر]')
text+='\n\n## ثبت پذیرش مستر\n\n'
text+=('گیت‌های مستقل صحت و اندازه‌گیری هر دو مرحله پذیرفته شده‌اند. '
       'نسخهٔ اجرایی در [runtime_final.json](coordination/runtime_final.json)، '
       'فرمان‌ها در [راهنمای اجرا](README_FA.md) و حدود پذیرش/ادامه در '
       '[تصمیم مستر](MASTER_DECISION_FA.md) هستند. '
       'همهٔ پیش‌نویس‌ها محفوظ‌اند؛ شکاف آرشیویِ صریحِ گزارش، با پذیرش علمی نتایج مخلوط نمی‌شود. '
       'این انتقال هیچ حل‌گر یا benchmark تازه‌ای اجرا نکرد.\n')
with TARGET.open('x',encoding='utf-8',newline='\n') as handle:
    handle.write(text)
record=dict(at_utc=datetime.now(timezone.utc).isoformat(),client_delivery_date='2026-10-29',
    source=str(SOURCE.relative_to(ROOT)),source_sha256=EXPECTED,
    target=str(TARGET.relative_to(ROOT)),target_sha256=sha256(TARGET.read_bytes()).hexdigest(),
    script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
    edits=['rebase local links','final title','master label','master acceptance note'],
    scientific_content_changed=False,local_link_rebases=changes)
with (ROOT/'coordination/report_promotion.json').open('x',encoding='utf-8') as handle:
    json.dump(record,handle,ensure_ascii=False,indent=2)
    handle.write('\n')
print(json.dumps(dict(target=str(TARGET),sha256=record['target_sha256'],rebased_links=len(changes))))
