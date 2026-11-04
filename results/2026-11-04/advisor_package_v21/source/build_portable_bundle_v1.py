"""Build a small offline meeting bundle without large raw research fixtures."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parents[1]
ROOT = R.parents[2]
stage = R / 'private/portable_v1'
stage.mkdir(exist_ok=False)
for name in ('output', 'algorithm', 'demo'):
    (stage / name).mkdir()
for p in (R / 'output').iterdir():
    if p.suffix in ('.pptx', '.pdf', '.md'):
        shutil.copy2(p, stage / 'output' / p.name)
original = ROOT / 'results/2026-11-04/scaling_v20/implementation/candidate_c2_v1'
for name in ('gate_v1.py', 'partition_gate_v1.py'):
    shutil.copy2(original / name, stage / 'algorithm' / name)
assert hashlib.sha256((stage / 'algorithm/gate_v1.py').read_bytes()).hexdigest() == '5331a1787a9ff74afe1afcbea1668dbe9ee69ef1f7121fec14c7281caa2d8680'
(stage / 'partition.py').write_text(
    '"""Portable dispatch to the unchanged audited C020 C2 solver."""\n'
    'from pathlib import Path\nimport runpy\nimport sys\n'
    'if __name__ == "__main__":\n'
    '    impl = Path(__file__).resolve().parent / "algorithm"\n'
    '    sys.path.insert(0, str(impl))\n'
    '    runpy.run_path(str(impl / "partition_gate_v1.py"), run_name="__main__")\n', encoding='utf8')
demo = (R / 'demo/run_demo.py').read_text(encoding='utf8')
demo = demo.replace('ROOT = Path(__file__).resolve().parents[4]',
                    'ROOT = Path(__file__).resolve().parents[1]')
demo = demo.replace('    if args.large:\n',
                    '    if args.large:\n        raise SystemExit("Large fixtures are excluded from the meeting ZIP; use the full repository.")\n')
(stage / 'demo/run_demo.py').write_text(demo, encoding='utf8')
(stage / 'README_FA.md').write_text(
    '# بستهٔ آفلاین جلسه با استاد\n\n'
    'ارائهٔ اصلی حدود۲۰دقیقه و۱۹اسلاید است. فایل‌ها در پوشهٔ output هستند.\n\n'
    '- [ارائهٔ قابل‌ویرایش](output/Advisor_Briefing_FA.pptx)\n'
    '- [نسخهٔ PDF](output/Advisor_Briefing_FA.pdf)\n'
    '- [خلاصهٔ جلسه](output/Advisor_One_Page_FA.md)\n'
    '- [اثبات‌ها و توضیح الگوریتم](output/Research_Brief_FA.md)\n'
    '- [متن صحبت](output/Speaker_Notes_FA.md)\n'
    '- [پرسش‌وپاسخ دفاع](output/Defense_QA_FA.md)\n'
    '- [منابع منتخب](output/Related_Work_FA.md)\n\n'
    'پس از استخراج ZIP، از همین پوشه اجرا کنید: python demo/run_demo.py\n'
    'فقط Python با کتابخانهٔ استاندارد لازم است. پنج مثال کوچک، خروجی‌ها را نشان می‌دهند.\n'
    'کد اصلی حل‌گر C2 در algorithm بدون تغییر کپی شده؛ فقط مسیر رابط و دمو برای بستهٔ مستقل تنظیم شده است.\n'
    'تریس‌های بزرگ و آرشیو خام برای کوچک‌ماندن این بسته اضافه نشده‌اند. گزینهٔ --large اینجا غیرفعال است.\n'
    'این بسته گزارش پیشرفت با فرض‌های صریح است؛ نوآوری جامع، بازیابی عمومیِ دادهٔ واقعی و بهبود RPNI را ادعا نمی‌کند.\n', encoding='utf8')
hashes = {p.relative_to(stage).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in stage.rglob('*') if p.is_file()}
(stage / 'MANIFEST.json').write_text(json.dumps({'files': hashes,
    'original_solver_unchanged': True, 'scope': 'offline meeting bundle; no large fixtures'}, indent=2), encoding='utf8')
target = R / 'output/Advisor_Meeting_Package.zip'
with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
    for p in sorted(stage.rglob('*')):
        if p.is_file():
            archive.write(p, p.relative_to(stage).as_posix())
print('Portable package created: ' + str(target))
