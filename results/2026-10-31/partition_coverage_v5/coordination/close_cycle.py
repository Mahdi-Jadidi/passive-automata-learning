"""Master closes C005 after accepted gates and unique archive integrity check."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent.parent
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def digest(p): return sha256(p.read_bytes()).hexdigest()
integrity=read(ROOT/'delivery/FINAL_INTEGRITY_2026-11-01.json')
assert integrity['status']=='pass', integrity['errors']
perf=read(ROOT/'audit/PERFORMANCE_RUN_REPORT_V2.json')
assert perf['scientific_status']=='completed' and perf['counts']['validation_errors']==0
assert perf['counts']['actual_provider_processes']==16
lines=['## کاراییِ محدود و ثبت شکست‌ها','',
 '۱۶ فرایند واقعیِ مجزا، شامل ۱۲ اجرای دقیق، سه اجرای گواهی و یک اجرای جداگانهٔ حافظه، با صفر خطای اعتبارسنجی و بدون پایان مهلت تکمیل شدند. همهٔ خروجی JSON در زمان انتهابه‌انتها محسوب شد. دو ورودی دقیق فقط هفت نماد و q=1 دارند؛ نتایج آن‌ها دربارهٔ qهای بزرگ‌تر یا تریس‌های بلند تعمیم داده نمی‌شود.','',
 '| ورودی | میانهٔ زمان با قید / بدون قید (ثانیه) | گره با قید / بدون قید |',
 '|---|---|---|']
for row in perf['exact_summary']:
    on,off=[next(c for c in row['conditions'] if c['toggle']==x) for x in ['on','off']]
    lines.append(f"| {row['case_id']} | {on['median_subprocess_seconds']:.3f} / {off['median_subprocess_seconds']:.3f} | {on['median_nodes']} / {off['median_nodes']} |")
s=perf['sparse_summary_from_completed_v1_jobs']
memory=perf['memory_summary_from_completed_v1_job']['tracemalloc_peak_bytes']
lines+=['',f"گواهیِ نمونهٔ ۱۶نمادی/۶عاملی با q=4 و طول ۳۲۷۶۸، میانهٔ زمان کامل {s['median_subprocess_seconds']:.3f} ثانیه داشت؛ مقایسهٔ دقیقِ جفت‌شده برای آن انجام نشده است. اوج تخصیص Python در اجرای جداگانه {memory:,} بایت بود؛ RSS نیست. کاهش گره در دو نمونهٔ کوچک دیده شد، اما زمان انتهابه‌انتها به سربار فرایند حساس است و این مطالعه برتری عمومی را ثابت نمی‌کند.",'',
 '۱۲ تلاش اولیهٔ ثبت آزمایش، به‌علت مسیر نادرست فایل و پیش از راه‌اندازی فرایند حل‌گر، شکست خوردند. نسخهٔ اول و همهٔ خطاها حفظ شدند؛ فقط همان ۱۲ فرایندِ شروع‌نشده با اجراگر اصلاح‌شده اجرا شدند. در مجموع ۲۸ تلاش ثبت و ۱۶ فرایند واقعی داریم؛ خطای پیش از اجرا، پایان مهلت حل‌گر محسوب نمی‌شود. خطاهای سرویس ایجنت‌ها نیز جدا ثبت شده‌اند.','',
 'اجرای اصلاح‌شده را مستر با اجراگرِ آماده و ثابتِ ممیز انجام داد؛ هیچ نمونهٔ موفق قبلی تکرار نشد. [گزارش کامل و شواهد هر اجرا](audit/PERFORMANCE_RUN_REPORT_V2.json).','']
report=ROOT/'RESEARCH_REPORT_FA.md'
content=report.read_text(encoding='utf-8')
before=digest(report)
start=content.index('## وضعیت کارایی و ادعاها')
end=content.index('این روش یادگیری عمومی',start)
report.write_text(content[:start]+'\n'.join(lines)+'\n'+content[end:],encoding='utf-8',newline='\n')
with (ROOT/'MASTER_DECISION_FA.md').open('a',encoding='utf-8') as f:
    f.write('\nدور پنجم در ۲۰۲۶/۱۱/۰۱ بسته شد؛ ۱۶ فرایند کارایی کامل و بدون اختلاف تأیید شدند. کاهش گره در دو نمونهٔ کوچک مشاهده شد؛ برتری عمومی ثابت نشده است. گزارش زمان و هزینهٔ بایگانی در گزارش نهایی و دفتر نتیجه پیوند دارند.\n')
gates=['SMALL_GATE_REPORT_V2.json','EXACT_TOGGLE_GATE_REPORT_V1.json','SPARSE_SCALING_AUDIT_REPORT_V1.json','ROOT_CLI_AUDIT_REPORT_V1.json','PERFORMANCE_RUN_REPORT_V2.json']
outcome=dict(cycle='C005',status='complete',completed_utc=datetime.now(timezone.utc).isoformat(),
 scientific_status='confirmed_under_stated_assumptions',parent_commit='0ab2d9eb',
 reports=[dict(path='audit/'+name,sha256=digest(ROOT/'audit'/name)) for name in gates],
 integrity=integrity,performance_counts=perf['counts'],
 report_promotion_amendment=dict(prior_sha256=before,final_sha256=digest(report),reason='Append accepted performance and preserve original candidate versions'),
 limitations=['known k','known disjoint alphabet','noise-free complete words','bounded local-word languages for certificates','no RPNI experiment','no general performance claim'],
 unexecuted_corpus='30 stage2 frozen corpus cases are not all audited; only explicitly reported cells were executed',
 coordination_note='Master executed auditor frozen recovery launcher once after interrupting idle coordination and checking no running performance processes')
path=ROOT/'coordination/CYCLE_OUTCOME.json'
with path.open('x',encoding='utf-8') as f: json.dump(outcome,f,ensure_ascii=False,indent=2)
links=[]
for name in ['README_FA.md','RESEARCH_REPORT_FA.md','MASTER_DECISION_FA.md']:
    doc=ROOT/name
    for target in re.findall(r'\]\(([^)]+)\)',doc.read_text(encoding='utf-8')):
        if '://' in target or target.startswith('#'): continue
        local=(doc.parent/target.split('#')[0]).resolve()
        assert local.exists(),(name,target)
        links.append(dict(document=name,target=target))
with (ROOT/'coordination/DELIVERY_LINKS.json').open('x',encoding='utf-8') as f: json.dump(dict(count=len(links),links=links),f,ensure_ascii=False,indent=2)
with (ROOT/'coordination/journal.jsonl').open('a',encoding='utf-8') as f:
    f.write(json.dumps(dict(event='cycle_completed',at_utc=outcome['completed_utc'],outcome='coordination/CYCLE_OUTCOME.json',link_count=len(links)))+'\n')
print(json.dumps(dict(status='complete',links=len(links),performance_processes=16)))
