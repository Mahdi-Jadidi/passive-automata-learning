"""Promote the reviewed candidate without modifying any branch draft."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parents[2]
SOURCE = ROOT / 'structural/C003_RESEARCH_REPORT_CANDIDATE_FA_REV5_FINAL.md'
TARGET = ROOT / 'RESEARCH_REPORT_FA.md'
EXPECTED = 'e0360747e300939fc5560f814fa316f7b1afda3ea2c0b2d37d4d9ebe2ccbc53f'
raw = SOURCE.read_bytes()
assert sha256(raw).hexdigest() == EXPECTED, 'Candidate changed after review'
assert not TARGET.exists(), 'Never overwrite a promoted report'
text = raw.decode('utf-8-sig')
links = []


def rebase(match):
    label, url = match.groups()
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', url) or url.startswith('#'):
        return match.group(0)
    path_part, sep, fragment = url.partition('#')
    local = (SOURCE.parent / path_part).resolve()
    local.relative_to(WORKSPACE)
    assert local.exists(), f'Missing report link: {url}'
    relative = Path(os.path.relpath(local, ROOT)).as_posix()
    new = relative + (sep + fragment if sep else '')
    links.append({'old': url, 'new': new})
    return f'[{label}]({new})'


text = re.sub(r'\[([^\]\n]+)\]\(([^)\n]+)\)', rebase, text)
text = text.replace('# گزارش نهایی نامزد C003:', '# گزارش نهایی C003:', 1)
text = text.replace('**وضعیت:** نامزد نهایی گزارش کل دور برای مستر.',
                    '**وضعیت:** گزارش نهایی پذیرفته‌شده توسط مستر؛ تحویل در ۲۰۲۶/۱۰/۲۷.', 1)
text = text.replace('## تصمیم نهایی پیشنهادی و تحویل دور', '## جمع‌بندی پژوهشی و تحویل دور', 1)
text += ('\n\n## ثبت پذیرش مستر\n\n'
         'این نسخه از نامزد پنجم بدون تغییر در نتایج علمی تهیه شده است. مسیر پیوندها '
         'برای قرارگیری گزارش در ریشهٔ بسته اصلاح شد؛ همهٔ پیش‌نویس‌ها محفوظ‌اند. '
         'تصمیم اجراییِ نهایی در [تصمیم مستر](MASTER_DECISION_FA.md)، '
         'روش اجرای نمونه در [راهنمای بسته](README_FA.md) و توضیحات دامنهٔ ممیزی '
         'در [یادداشت مستر](coordination/AUDIT_ERRATA_FA.md) قرار دارند. '
         'عبارت‌های «پیشنهاد برای مستر» در متن، منشأ گزارش شاخه را حفظ می‌کنند؛ '
         'این پیشنهادها در تصمیم مستقل مستر بازبینی شده‌اند. '
         'ثبت انتقال و هش دقیق منبع در [report_promotion.json](coordination/report_promotion.json) است.\n')
with TARGET.open('x', encoding='utf-8', newline='\n') as handle:
    handle.write(text)
record = dict(at_utc=datetime.now(timezone.utc).isoformat(), client_delivery_date='2026-10-27',
              source=str(SOURCE.relative_to(ROOT)), source_sha256=EXPECTED,
              target=str(TARGET.relative_to(ROOT)), target_sha256=sha256(TARGET.read_bytes()).hexdigest(),
              script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
              edits=['rebase local links', 'final title and acceptance status', 'master acceptance note'],
              local_link_rebases=links, scientific_content_changed=False,
              scientific_status='verified_under_declared_assumptions')
with (ROOT / 'coordination/report_promotion.json').open('x', encoding='utf-8') as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps({'target': str(TARGET), 'sha256': record['target_sha256'], 'local_links': len(links)}))
