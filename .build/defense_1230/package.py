from pathlib import Path
import json,shutil,hashlib,zipfile,re,xml.etree.ElementTree as ET
root=Path.cwd();out=root/'output/final_1230';private=root/'.build/defense_1230'
r=out/'research';r.mkdir(exist_ok=True)
for p in (root/'output/research_1230').iterdir():
    if p.is_file() and p.suffix!='.zip' and p.name!='manifest.json':shutil.copy2(p,r/p.name)
source=out/'presentation_source';source.mkdir(exist_ok=True)
for name in ['content.py','notes.py','build.mjs','patch_rtl.py']:shutil.copy2(private/name,source/name)
readme='''# بستهٔ نهایی ارائهٔ انتخاب Split یا Global

فایل اصلی RPNI_Final_1230_EN.pptx شامل ۲۸ اسلاید انگلیسی است: ۱۴ اسلاید اصلی برای حدود ۱۸ دقیقه و ۱۴ اسلاید اثبات در پیوست. شماره‌ها پیوسته‌اند. فایل Speaker_Notes_FA.docx متن فارسی هماهنگ با همان شماره‌ها، زمان پیشنهادی، توضیح اثبات‌های پیوست و پاسخ به پرسش‌های محتمل را دارد. متن فارسی داخل یادداشت هر اسلاید پاورپوینت نیز قرار دارد. زمان واقعی با تمرین بلند مشخص می‌شود.

## نتیجهٔ قابل ارائه

۱. ناحیهٔ گواهی با شرط‌های ساختاری و نامساوی‌های محاسبه‌پذیر از خود داده تشخیص داده می‌شود. انتخاب‌گر static_selector.py برای این تشخیص یادگیرنده را اجرا نمی‌کند. این مرز شرایط کافیِ الگوریتم فعلی است؛ ادعای شناسایی همهٔ ورودی‌های قابل تصمیم با هر روش ممکن نیست.

۲. داخل ناحیه، جهت هزینه با کران اثبات‌شده یا فرمول دقیق مشخص است. گواهی NET هزینهٔ خود انتخاب‌گر H را هم پرداخت می‌کند. PIPELINE فقط مقایسهٔ هزینهٔ دو مسیر را می‌گوید. ارزان‌تر بودن در مدل رویدادهای برنامهٔ مرجع W_ref است؛ زمان واقعی، ساخت محصول صریح و تمام پیاده‌سازی‌های RPNI را شامل نمی‌شود.

نتیجهٔ تازهٔ مهم، خانواده‌ای نامتناهی با دو تریس مثبت و بدون منفی است. برای الفبای دقیق {a,b}، بلوک‌های {a},{b}، مثبت‌های b a^n b^(n-1) و b a b^(n-1) a^(n-1)، هر n>=4 گواهی سود خالص Split دارد. در n=4، پیش از یادگیری ثابت می‌شود 99+170=269<274<=WG. این آستانه کافیِ همان خانواده است، نه حداقل عمومی داده.

خانوادهٔ Global با مثبت‌های تک‌الفبایی غیرخالی و منفی‌های دارای حرف خارج از پشتیبان مثبت نیز اثبات دارد. کران عمومیِ جدید مثبت‌های دلخواه و منفی‌های واقعاً ردکنندهٔ ادغام را مجاز می‌داند؛ معتبر بودن کران الزاماً جدایی بازه‌ها را تضمین نمی‌کند.

## مرز ادعا

UNKNOWN یعنی آزمون‌های فعلی گواهی کافی ندارند؛ اثبات ناممکن بودن تصمیم نیست. پوشش کاملِ ارزانِ پیش از اجرا برای همهٔ ورودی‌های با طول نامحدود هنوز حل نشده است. روی دامنهٔ واژگان متناهی و افراز ثابت می‌توان همهٔ برچسب‌گذاری‌ها را آفلاین محاسبه کرد؛ هزینهٔ آفلاین و بارگذاری باید حساب شوند. total_selector.py نیز مقایسهٔ دقیق عمومی را با اجرای واقعی دو مسیر در موارد حل‌نشده انجام می‌دهد؛ این fallback تصمیم ارزان پیش از اجرا محسوب نمی‌شود.

گواهی هزینه، سازگاری با نمونه، برابری زبان دو خروجی و بازیابی زبان هدف گزاره‌های جدا هستند. سؤال برابری عمومی در اسلایدهای ۱۴ و ۲۸ برای مرحلهٔ بعد نگه داشته شده است. تضمین‌ها ریاضی و مشروط به قرارداد صریح‌اند؛ آزمون متناهی، بازبینی انسانی و این بسته ادعای مصونیت مطلق از خطا یا تأیید داوری نیستند.

## اثبات و بازتولید

مرجع جاری research/Research_Proofs_EN.md است. اثبات‌های ساختاری قبلی که این گزارش به آن‌ها ارجاع می‌دهد در research/Coverage_Proofs_EN.md و گزارش‌های Original و Previous حفظ شده‌اند. آمار قدیمی در گزارش‌های سابق، آمار نسخهٔ جاری نیست. داده‌های عددی جاری در research/final_worked_examples.json و پنج فایل نتیجهٔ audit قرار دارند.

کد پژوهش فقط به کتابخانهٔ استاندارد Python نیاز دارد. از پوشهٔ research می‌توان اجرا کرد:

```text
python -X utf8 -B static_selector.py two_trace_example.json
python -X utf8 -B verify_package.py
```

فرمان اول گواهی قبل از آموزش را برمی‌گرداند. فرمان دوم کنترل سریع رابط‌ها، مثال‌ها و بسته است و همهٔ ممیزی‌های گسترده را دوباره اجرا نمی‌کند. برای تکرار بررسی‌های کامل:

```text
python -X utf8 -B audit_static.py
python -X utf8 -B audit_regressions.py
python -X utf8 -B audit_tree_bounds.py
python -X utf8 -B audit_compiled.py
python -X utf8 -B audit_amortized.py
```

پنج ممیزیِ انجام‌شده مجموعاً ۵۵۶۲۴ اجرای مورد آزمون و ۱۷۴۹۹۸ کنترل مستقلِ خارج‌قسمت ادغام داشته‌اند. ورودی‌ها ممکن است تکرار شوند؛ این شمارش درصد پوشش کل ورودی‌ها یا جایگزین اثبات نیست. بررسی‌کنندهٔ مستقل، افراز حالت‌ها را تا بستار اشباع می‌کند و هم‌ارزی اتوماتا را با حالت رد برای انتقال تعریف‌نشده بررسی می‌کند.

## وضعیت فایل‌ها

گسترش علمی در موعد ۱۲:۳۰ تهران متوقف و پس از آن ارائه نهایی شد. اصلاح‌های بعدی مربوط به بیان، نمایش نمادها و صفحه‌آرایی‌اند. کد پژوهشی نهایی همان نسخهٔ تثبیت‌شده است. فایل‌های نسخه‌های قبلی حفظ شده‌اند. پوشهٔ presentation_source منبع ساخت ارائه است و برای ساخت مجدد به runtime و کتابخانهٔ artifact-tool همان محیط نیاز دارد. manifest.json هش تمام فایل‌های تحویلی را نگه می‌دارد.
'''
(out/'README_FA.md').write_text(readme,encoding='utf8')
# Content, numbering, language, notes and arithmetic checks on actual exported files.
slides=json.loads((out/'slide_content.json').read_text(encoding='utf8'))
assert len(slides)==28 and sum(s['seconds'] for s in slides)==1080
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with zipfile.ZipFile(out/'RPNI_Final_1230_EN.pptx') as z:
    assert z.testzip() is None
    for i,s in enumerate(slides,1):
        tree=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        txt=''.join(tree.itertext())
        assert f'{i} / 28' in txt and s['title'] in txt
        visible=''.join(n.text or '' for n in tree.findall('.//a:t',ns))
        assert not re.search('[\u0600-\u06ff]',visible),(i,'non-English visible text')
        notes=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        nt=''.join(n.text or '' for n in notes.findall('.//a:t',ns))
        assert s['notes'] in nt,(i,'notes mismatch')
with zipfile.ZipFile(out/'Speaker_Notes_FA.docx') as z:
    tree=ET.fromstring(z.read('word/document.xml'));text=''.join(tree.itertext())
    for i,s in enumerate(slides,1):assert f'Slide {i} / 28' in text
assert 99+170==269<274
assert sum([754,493,15,925])==2187
for n in range(4,100):assert (20*n+19)+(2*n*n+28*n+26)<8*n*n+38*n-6
# Record visual review and renderer limitation accurately.
qa=dict(status='passed',slides=28,main_seconds=1080,docx_pages=12,
        visual_review='All 28 final v3 slides and all 12 final DOCX page images inspected individually.',
        native_powerpoint_text_fit_flags=0,geometry_warning='Slide 23 table estimate exceeded by 0.02 inch; native PowerPoint rendering inspected and has no collision or clipping.',
        docx_renderer='Packaged render_docx.py failed because LibreOffice soffice.exe is absent; native Microsoft Word exported PDF and Poppler produced all page images.',
        scope='Structural/content/visual and recorded numeric checks; not machine-checked formal proof or infallibility.')
from PIL import Image,ImageChops
changed=[]
for i in range(1,29):
    name=f'slide-{i:02d}.png'
    if ImageChops.difference(Image.open(private/'render-v2'/name).convert('RGB'),Image.open(private/'render-v3'/name).convert('RGB')).getbbox():changed.append(i)
assert len(changed)<=28
qa['intended_slide_text_changes_since_v2']=[7,17,19,21,23]
qa['research_case_executions']=55624;qa['independent_candidate_checks']=174998
(private/'final_qa.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
(out/'Validation_Summary.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
paths=sorted(p for p in out.rglob('*') if p.is_file() and p.suffix!='.zip' and p.name!='manifest.json')
manifest={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
archive=out/'RPNI_Final_1230_Package.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in paths:z.write(p,p.relative_to(out))
    z.write(out/'manifest.json','manifest.json')
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print(json.dumps(dict(status='passed',files=len(paths)+1,archive_bytes=archive.stat().st_size,slides=28,script_pages=12,seconds=1080,changed_slides=changed),indent=2))
