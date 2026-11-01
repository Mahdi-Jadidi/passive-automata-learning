"""Master artifact promotion; no solvers, no replacement of old candidates."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
items = []
for name, target in [('README_CANDIDATE_FA_V2.md', 'README_FA.md'),
                     ('REPORT_CANDIDATE_FA_V2.md', 'RESEARCH_REPORT_FA.md')]:
    source = ROOT/'delivery'/name
    content = source.read_text(encoding='utf-8')
    if target == 'RESEARCH_REPORT_FA.md':
        content = content.replace('# گزارش علمی C005 — نامزد نسخهٔ دوم',
            '# گزارش علمی دور پنجم — گسترش پوشش افراز', 1)
        content += '\n\nاین متن، نتایج ممیزی صحت پذیرفته‌شده را ثبت می‌کند. وضعیت کارایی و تحویل نهایی در [تصمیم مستر](MASTER_DECISION_FA.md) و [دفتر نتیجه](coordination/CYCLE_OUTCOME.json) ثبت می‌شود.\n'
    with (ROOT/target).open('x',encoding='utf-8',newline='\n') as handle:
        handle.write(content)
    items.append(dict(source=str(source.relative_to(ROOT)),
        source_sha256=sha256(source.read_bytes()).hexdigest(),target=target,
        target_sha256=sha256((ROOT/target).read_bytes()).hexdigest()))
with (ROOT/'coordination/report_promotion.json').open('x',encoding='utf-8') as handle:
    json.dump(items,handle,ensure_ascii=False,indent=2)
print(json.dumps(dict(promoted=len(items))))
