"""Master promotes reviewed documents and freezes C009 bytes; no experiments."""
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parent.parent
WORKSPACE=ROOT.parents[2]
def digest(p):return sha256(p.read_bytes()).hexdigest()
def write_new(p,data):
    with p.open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
assert digest(ROOT/'implementation/ownership_solver_v1.py')=='79255b0a306f8a30dffdd813c018bc4fd9368dad880c07489a86abd50968a5e7'
assert digest(ROOT/'implementation/ownership_cli_v1.py')=='356ac0db3ca272403d95bc275e4babc48c5d7fc29caf00cb9685f8e49aed8507'
assert digest(ROOT/'solver.py')=='543a020f690e0403f21799f2875df08aa9546688bccb65119499bff09a9b57a2'
report=ROOT/'theory/REPORT_CANDIDATE_FA_v2.md'
readme=ROOT/'implementation/ROOT_README_CANDIDATE_FA_v3.md'
assert digest(report)=='e2edf0c0429d0f8b4537a4356622e69ffce87a6021303a9dbdcc518d33c61f39'
assert digest(readme)=='0e1c6ebdce2093c8615f68836f3300246f18d773899f3c5b9727990d24bb39ee'
assert json.loads((ROOT/'coordination/FINAL_ACCEPTANCE.json').read_text())['complete_scale_cells']==3
with (ROOT/'README_FA.md').open('x',encoding='utf-8',newline='\n') as f:f.write(readme.read_text(encoding='utf-8'))
text=report.read_text(encoding='utf-8').replace('](../audit/','](audit/')
text += '\n\nاثبات‌های کامل: [T1 تا T7](theory/PROOFS_v1.md)، [تعدادهای مجاز](theory/ADDENDUM_FEASIBLE_COUNTS_v1.md)؛ [تصمیم مستر](MASTER_DECISION_FA.md) و [پذیرش نهایی](coordination/FINAL_ACCEPTANCE.json).\n'
with (ROOT/'RESEARCH_REPORT_FA.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)

# The project entry point is mutable. Preserve both its before and after bytes
# inside this immutable cycle; don't bind future cycle integrity to a live index.
start=WORKSPACE/'START_HERE_FA.md'
before=start.read_bytes()
with (ROOT/'coordination/START_HERE_BEFORE_C009.md').open('xb') as f:f.write(before)
old=before.decode('utf-8')
body=old.split('\n',1)[1] if old.startswith('# ') else old
body=body.replace('آخرین تحویل:', 'تحویل پیشین:',1)
prefix='''# شروع و ادامهٔ پژوهش یادگیری غیرفعال اتوماتا

آخرین تحویل: **دور نهم، ۲۰۲۶/۱۱/۰۲**. شمارش دقیق افرازها با مجموعهٔ معتبر تعدادهای مجاز، شناسایی کاملِ مشروط و روابط قطعیِ جزئیِ هر زوج نماد پیاده و ممیزی شد. ۱۲۹ مجموعهٔ کامل برابر بودند؛ سه مورد مقیاس کامل و مورد ۱۴نمادی ناتمام ثبت شد. این نتیجه تضمین همگانیِ بازیابی سخت‌افزار از هر لاگ نیست.

- [گزارش دور نهم](results/2026-11-02/partition_coverage_v9/RESEARCH_REPORT_FA.md)
- [راهنمای اجرا](results/2026-11-02/partition_coverage_v9/README_FA.md)
- [تصمیم مستر](results/2026-11-02/partition_coverage_v9/MASTER_DECISION_FA.md)
- [نتیجه و بایگانی](results/2026-11-02/partition_coverage_v9/coordination/CYCLE_OUTCOME.json)
- [دور هشتم: مرز شناسایی مالکیت واقعی و مثال‌های نقض](results/2026-11-02/partition_identification_v8/RESULT_FA.md)

## تحویل‌های پیشین
'''
after=(prefix+body).encode('utf-8')
start.write_bytes(after)
with (ROOT/'coordination/START_HERE_C009_SNAPSHOT.md').open('xb') as f:f.write(after)
write_new(ROOT/'coordination/delivery_promotion.json',dict(
    report_source=str(report.relative_to(ROOT)),report_sha256=digest(report),
    readme_source=str(readme.relative_to(ROOT)),readme_sha256=digest(readme),
    shared_index_before_sha256=sha256(before).hexdigest(),shared_index_after_sha256=sha256(after).hexdigest(),
    shared_index_note='Live START_HERE changes intentionally; historical cycle bytes are preserved in snapshots and Git. No older research file was changed.'))
files=[dict(path=p.relative_to(WORKSPACE).as_posix(),sha256=digest(p),bytes=p.stat().st_size)
       for p in sorted(ROOT.rglob('*')) if p.is_file()]
write_new(ROOT/'coordination/runtime_final.json',dict(cycle='C009',status='frozen_final_pending_integrity',files=files))
print(json.dumps(dict(promoted=True, runtime_files=len(files))))
