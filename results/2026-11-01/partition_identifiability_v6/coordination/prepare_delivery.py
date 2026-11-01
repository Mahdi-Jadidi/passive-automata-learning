"""Accept six independent benchmark replays, append report, freeze final files."""
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return sha256(p.read_bytes()).hexdigest()
benchpath=ROOT/'audit/benchmark_v1/benchmark_results_v2.json'
bench=read(benchpath)
assert bench['actual_captured_provider_processes']==6
assert bench['independently_validated_provider_processes']==6 and not bench['errors']
report=ROOT/'RESEARCH_REPORT_FA.md'
before=digest(report)
text=report.read_text(encoding='utf-8')
text=text.replace('زمان‌گیری هنوز بخش جداگانهٔ در انتظار است؛ این گزارش ادعای سرعت ندارد.', 'شش اجرای مستقلِ محدود و بازپخش گواه‌های آن‌ها نیز پذیرفته شدند؛ نتیجهٔ آن‌ها در پیوست پایانی آمده است. برتری عمومی سرعت ادعا نمی‌شود.',1)
lines=['','## پیوست نهایی: هزینهٔ دو مسیر گواه','',
 'شش اجرای مجاز، هر نمونه سه بار در فرایند تازه، با خروجی کامل JSON ثبت و مستقل بازپخش شدند. هر دو نمونه از زبان‌های منظم نامتناهی ساخته شده‌اند و هیچ k یا q به حل‌گر داده نشد. این اندازه‌گیری مقایسه با روش قدیمی نیست.','',
 '| نمونه | الفبا / بیشینهٔ طول | گواه | میانهٔ زمان کامل فرایند (ثانیه) | بایت خروجی |',
 '|---|---|---|---:|---:|']
for name,desc,kind in [('large_connected_m64','۶۴ / ۱۳۰','۶۳ یال اجباری؛ بدون جست‌وجوی برش'),('small_full_cover_m4','۴ / ۴','برخورد کاملِ هر ۷ برش')]:
 c=bench['primary_cells'][name]
 lines.append(f"| {name} | {desc} | {kind} | {c['subprocess_seconds']['median']:.3f} | {c['stdout_bytes']['median']} |")
lines+=['',
 'زمان شامل آغاز Python، خواندن ورودی، پیش‌پردازش، تصمیم، ساخت گواه و خروجی کامل است؛ سربار کپی منابع ابزار capture در آن نیست. حافظه اندازه‌گیری نشد و مقیاس‌پذیری عمومی از دو نمونه نتیجه نمی‌شود. نمونهٔ مثبت‌تنهای ۶۴نمادیِ اختیاری، فقط منجمد شد و اجرا نشد.','',
 'ممیزِ پس از اجرا ابتدا به‌سبب مسیر نادرستِ فایل ورودی متوقف شد. نسخهٔ اولیه و گزارش شکست حفظ شدند؛ فقط همان شش خروجی با نسخهٔ اصلاح‌شده بازبینی شدند و هیچ فرایند حل‌گر تکرار نشد. [دادهٔ هر شش اجرا](audit/benchmark_v1/benchmark_results_v2.json) و [شرح اصلاح ممیز](audit/benchmark_v1/POSTRUN_AUDIT_V2.md).','']
report.write_text(text+'\n'.join(lines),encoding='utf-8',newline='\n')
with (ROOT/'MASTER_DECISION_FA.md').open('a',encoding='utf-8') as f:
 f.write('\nشش اجرای محدود و بازپخش مستقلشان پذیرفته شدند؛ نمونهٔ ۶۴نمادیِ نامتناهی با ۶۳ پیوند اجباری، عدم تجزیهٔ غیرتک‌بلوکی را اثبات کرد. نمونهٔ چهارنمادی بدون پیوند محلی از مسیر هفت شاهد برش رد شد. برتری عمومی سرعت یا کران چندجمله‌ای نتیجه نشده است.\n')
files=['solver.py','implementation/solver_v5.py','implementation/cli_v4.py','implementation/archive_integrity_v2.py','theory/PROOFS_v1.md','theory/ENHANCED_RULES_PROOFS_v1.md','README_FA.md','RESEARCH_REPORT_FA.md','MASTER_DECISION_FA.md','audit/validation_v2/solver_v5_gate_v6.json','audit/validation_v1/oracle_crosscheck.json','audit/validation_v2/root_cli_v1.json','audit/benchmark_v1/benchmark_results_v2.json']
items=[dict(path=p,sha256=digest(ROOT/p)) for p in files]
helper='results/2026-10-31/partition_coverage_v5/general/known_k_qexact_v2.py'
items.append(dict(path=helper,sha256=digest(ROOT.parents[2]/helper)))
runtime=dict(cycle='C006',status='frozen_final',files=items)
with (ROOT/'coordination/runtime_final.json').open('x',encoding='utf-8') as f:json.dump(runtime,f,ensure_ascii=False,indent=2)
with (ROOT/'coordination/PERFORMANCE_ACCEPTANCE.json').open('x',encoding='utf-8') as f:
 json.dump(dict(event='master_accepts_benchmark',at_utc=datetime.now(timezone.utc).isoformat(),path=str(benchpath.relative_to(ROOT)),sha256=digest(benchpath),actual_processes=6,validated=6,old_report_sha256=before,final_report_sha256=digest(report)),f,indent=2)
print(json.dumps(dict(runtime_files=len(items),accepted_processes=6)))
