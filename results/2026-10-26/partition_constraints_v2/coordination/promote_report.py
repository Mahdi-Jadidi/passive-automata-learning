"""Promote the reviewed A report with root-relative links; preserve the source."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
import json
import re

root = Path(__file__).resolve().parent.parent
source = root / 'approaches/eager/FINAL_REPORT_CANDIDATE_FA_REV4.md'
target = root / 'RESEARCH_REPORT_FA.md'
raw = source.read_bytes()
body = raw.decode('utf-8')
links = []
def rebase(match):
    label, address = match.groups()
    if '://' in address or address.startswith('#'):
        return match.group(0)
    path_part, separator, fragment = address.partition('#')
    path = (source.parent / path_part).resolve()
    relative = path.relative_to(root).as_posix()
    if not path.exists():
        raise FileNotFoundError(path)
    links.append(relative)
    return f'[{label}]({relative}{separator}{fragment})'
body = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', rebase, body)
body = body.replace('# نتیجهٔ دور دوم افراز الفبا — نامزد نهایی برای مستر',
                    '# گزارش نهایی دور دوم افراز الفبا', 1)
body = body.replace('ادغام و تصویب گزارش نهایی\nپروژه با مستر است.',
                    'این نسخه پس از بازبینی شواهد توسط مستر پذیرفته شد.')
body += '\n\nتصمیم نهایی، مرز نتیجه و پیشنهاد ادامه در [تصمیم مستر](MASTER_DECISION_FA.md) و راهنمای اجرا در [README_FA.md](README_FA.md) ثبت شده‌اند. متن پایهٔ شاخهٔ A و تمام پیش‌نویس‌های پیشین بدون تغییر باقی می‌مانند.\n'
with target.open('x', encoding='utf-8', newline='\n') as handle:
    handle.write(body)
record = {'at_utc': datetime.now(timezone.utc).isoformat(),
          'source': source.relative_to(root).as_posix(),
          'source_sha256': sha256(raw).hexdigest(),
          'target': target.name, 'target_sha256': sha256(target.read_bytes()).hexdigest(),
          'script_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
          'changes': ['root-relative local links', 'final title and acceptance note', 'master decision and guide links'],
          'checked_local_links': links, 'source_preserved': True}
with (root / 'coordination/report_promotion.json').open('x', encoding='utf-8') as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps(record, ensure_ascii=False))
