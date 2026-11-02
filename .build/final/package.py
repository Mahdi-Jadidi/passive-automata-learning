from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from xml.etree import ElementTree as ET
from docx import Document
import hashlib,json,re,shutil

build=Path(__file__).parent
workspace=build.parents[1];out=workspace/'output'/'final'
proofs=out/'proofs';research=out/'research';original=research/'original'
for p in (proofs,research,original):p.mkdir(exist_ok=True,parents=True)
shutil.copy2(workspace/'output/defense/Proofs_and_Audit_EN.md',proofs/'Original_Proofs_EN.md')
shutil.copy2(workspace/'output/extensions/Extension_Proofs_EN.md',proofs/'Extension_Proofs_EN.md')
for p in (workspace/'output/extensions').iterdir():
    if p.is_file() and p.suffix.lower()!='.zip' and p.name!='manifest.json':shutil.copy2(p,research/p.name)
for name in ['certified_selector.py','defense_selector.py','rpni_work_reference.py','audit_defense.py',
             'audit_results.json','audit_boundary.py','boundary_audit_results.json','check_interface.py','interface_checks.json']:
    shutil.copy2(workspace/'output/defense'/name,original/name)
slides=json.loads((build/'slides.json').read_text(encoding='utf8'))
assert len(slides)==28 and sum(x['seconds'] for x in slides)==1080
assert all(x['seconds']>0 for x in slides[:14]) and all(x['seconds']==0 for x in slides[14:])
assert 'Progress on the two' in slides[12]['title']
assert 'Next research question' in slides[13]['title'] and 'Future work' in slides[-1]['title']
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with ZipFile(out/'RPNI_Final_EN.pptx') as z:
    for i,s in enumerate(slides,1):
        e=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        t=' '.join(x.text or '' for x in e.findall('.//a:t',ns))
        assert s['title'] in t and f'{i} / 28' in t
        assert not re.search(r'[\u0600-\u06ff]',t)
        for block in s['blocks']:
            expected=([block['text']] if block['kind']!='table' else block['headers']+[v for row in block['rows'] for v in row])
            for v in expected:assert v in t,(i,v)
        e=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        t=' '.join(x.text or '' for x in e.findall('.//a:t',ns))
        assert s['notes'] in t and s['proof'] in t
doc=Document(out/'Speaker_Notes_FA.docx')
normalize=lambda t:' '.join(t.split())
text=normalize(' '.join(p.text for p in doc.paragraphs))
heads=[p.text for p in doc.paragraphs if p.style.name=='Heading 1' and p.text.startswith('Slide ')]
assert len(heads)==28
for i,s in enumerate(slides,1):
    assert heads[i-1]==f'Slide {i} / 28    {s["title"]}'
    assert normalize(s['notes']) in text,(i,'Missing Persian note')
assert 'برابری گسترده‌تر یک سؤال مستقل مرحلهٔ بعد است' in text
budgets=json.loads((research/'deletion_budgets.json').read_text())
table=slides[8]['blocks'][1]['rows']
for n,p,r,remaining in table:
    b=next(x for x in budgets if x['n']==int(n))
    assert (int(p),int(r),int(remaining))==(b['complete_positives'],b['any_deletions_up_to'],b['minimum_remaining_for_this_budget'])
    assert int(p)-int(r)==int(remaining)
for name,values in [('incomplete_net_equal',(142,269,124)),('informative_net_cost',(530,3109,594))]:
    c=json.loads((research/(name+'_certificate.json')).read_text())
    assert (c['selector_work'],c['global_interval'][0],c['split_interval'][1])==values
g=json.loads((research/'simple_informative_global_certificate.json').read_text())
assert (g['selector_work'],g['global_exact'],g['split_exact'])==(12,25,41)
receipt=json.loads((build/'validation-v3.json').read_text())
digest=hashlib.sha256((out/'RPNI_Final_EN.pptx').read_bytes()).hexdigest()
assert digest==receipt['finalSha256']
readme='''# ارائه نهایی و پرونده پژوهش

پاورپوینت انگلیسی ساده و شماره‌دار، ۲۸ اسلاید دارد: ۱۴ اسلاید اصلی برای حدود ۱۸ دقیقه و ۱۴ اسلاید پیوست. متن فارسی در Word و Markdown با شماره‌ها هماهنگ است. زمان‌ها پیشنهادی‌اند و نیاز به تمرین دارند.

اسلاید ۱۳، جمع‌بندی پیشرفت و کار باقی‌مانده در دو محور اصلی است. سؤال برابری زبان خروجی به‌عنوان پژوهش مرحلهٔ بعد، در اسلاید ۱۴ و آخرین اسلاید کل فایل، یعنی ۲۸، آمده است. پژوهش هزینه مستقل از حل این سؤال ادامه پیدا می‌کند.

فرض‌های W_ref و پیاده‌سازی مرجع، شرط گواهی‌ها هستند. نتیجه به تمام ورودی‌ها، زمان واقعی یا بازیابی زبان هدف تعمیم داده نشده است. گواهی صرفاً هزینه با گواهی هزینه و خروجی برابر جداست.

فایل Conclusion_FA.md جمع‌بندی کوتاه دو محور را دارد. پوشه proofs اثبات‌های کامل قبلی و توسعه‌یافته را نگه می‌دارد. پوشه research شامل انتخاب‌گر توسعه‌یافته، مرجع، بررسی‌کننده مستقل، آزمون‌ها، ورودی‌های مثال، نتایج و نمودار حذف مثبت‌هاست. کد و نتایج قبلی در research/original آمده‌اند.

برای بازتولید نتایج جدید، در research اجرا کنید:

    python -B audit_extensions.py
    python -B deletion_budget.py
    python -B extended_selector.py incomplete_net_equal.json
    python -B extended_selector.py informative_net_cost.json
    python -B extended_selector.py simple_informative_global.json

نسخه‌های قبلی در output/defense و output/extensions حفظ شده‌اند.
'''
(out/'README_FA.md').write_text(readme,encoding='utf8')
files=sorted(p for p in out.rglob('*') if p.is_file() and p.name not in ('manifest.json','Presentation_and_Research.zip') and '__pycache__' not in p.parts)
manifest={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
with ZipFile(out/'Presentation_and_Research.zip','w',ZIP_DEFLATED) as z:
    for p in files+[out/'manifest.json']:z.write(p,p.relative_to(out).as_posix())
with ZipFile(out/'Presentation_and_Research.zip') as z:
    for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print(json.dumps(dict(status='passed',slides=28,main_minutes=18,main_words=sum(len(s['notes'].split()) for s in slides[:14]),
                     package_files=len(files)+1,package_bytes=(out/'Presentation_and_Research.zip').stat().st_size),indent=2))
