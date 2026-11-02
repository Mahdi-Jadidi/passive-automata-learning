from pathlib import Path
import json,re
from docx import Document
from docx.shared import Cm,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root=Path(__file__).parent
out=root.parents[1]/'output'/'final_1230'
slides=json.loads((root/'slides.json').read_text(encoding='utf8'))
doc=Document();sec=doc.sections[0]
sec.page_width=Cm(21);sec.page_height=Cm(29.7)
sec.top_margin=Cm(1.8);sec.bottom_margin=Cm(1.7);sec.left_margin=Cm(1.9);sec.right_margin=Cm(1.9)
for name in ('Normal','Title','Subtitle','Heading 1','Heading 2'):
    st=doc.styles[name];st.font.name='Tahoma';st.font.color.rgb=RGBColor(0,0,0)
    st.element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:cs'),'Tahoma')
for el in list(doc.styles.element.iter(qn('w:pBdr'))):el.getparent().remove(el)
doc.styles['Normal'].font.size=Pt(11.5)
doc.styles['Normal'].paragraph_format.line_spacing=1.28
doc.styles['Normal'].paragraph_format.space_after=Pt(8)
doc.styles['Title'].font.size=Pt(22)
doc.styles['Heading 1'].font.size=Pt(15)
doc.styles['Heading 1'].paragraph_format.space_before=Pt(15)
doc.styles['Heading 1'].paragraph_format.space_after=Pt(8)
doc.styles['Heading 1'].paragraph_format.keep_with_next=True

def rtl(p):
    logical=p.text;p.clear()
    for part in re.split(r'([A-Za-z0-9\u0370-\u03ff\u2070-\u209f\u2200-\u22ff]+(?:[\x20-\x7e\u0370-\u03ff\u2070-\u209f\u2200-\u22ff]*[A-Za-z0-9\u0370-\u03ff\u2070-\u209f\u2200-\u22ff])?[)\]]*)',logical):
        if part:p.add_run(part)
    p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    b=OxmlElement('w:bidi');p._p.get_or_add_pPr().append(b)
    for r in p.runs:
        r.font.name='Tahoma';rp=r._r.get_or_add_rPr();rf=rp.get_or_add_rFonts()
        for x in ('ascii','hAnsi','cs'):rf.set(qn('w:'+x),'Tahoma')
        lang=OxmlElement('w:lang');lang.set(qn('w:bidi'),'fa-IR');rp.append(lang)
        direction=OxmlElement('w:rtl');direction.set(qn('w:val'),'0' if re.search(r'[A-Za-z0-9\u0370-\u03ff\u2200-\u22ff]',r.text) else '1');rp.append(direction)
    return p

rtl(doc.add_paragraph('متن ارائه انتخاب مسیر یادگیری',style='Title'))
rtl(doc.add_paragraph('همراه پاورپوینت انگلیسی انتخاب Split یا Global پیش از اجرای RPNI'))
rtl(doc.add_paragraph('این متن برای ارائه به استاد تنظیم شده است. اسلایدهای ۱ تا ۱۴ مسیر اصلی ۱۸ دقیقه‌ای و اسلایدهای ۱۵ تا ۲۸ پیوست پاسخ به پرسش‌ها و جزئیات اثبات‌اند. ارائهٔ اصلی پس از اسلاید ۱۴ تمام می‌شود. زمان‌ها پیشنهادی‌اند و برای رسیدن به زمان واقعی باید یک بار با صدای بلند تمرین شوند.'))
rtl(doc.add_paragraph('جمع‌بندی دو محور: تشخیص شرایط کافیِ صدور گواهی و انتخاب مسیر کم‌هزینه‌تر برای ورودی دارای گواهی، اثبات و پیاده‌سازی شده‌اند. کران عمومی برای مثبت‌های دلخواه و منفی‌های اثرگذار معتبر است و یک خانوادهٔ نامتناهیِ دو تریسی گواهی سود خالص Split دارد. پوشش کامل روی یک دامنهٔ متناهی با محاسبهٔ آفلاین ممکن است؛ این نتیجه حل عمومی ارزان همهٔ ورودی‌ها نیست. همهٔ ورودی‌ها حل نشده‌اند. برابری گسترده‌تر زبان خروجی، سؤال پژوهشی مستقل مرحلهٔ بعد است و در پایان بخش اصلی و پایان کل پاورپوینت می‌آید.'))

elapsed=0
for i,s in enumerate(slides,1):
    if i==15:
        # Appendix follows the main script without a mostly empty page.
        rtl(doc.add_paragraph('پیوست اثبات ها',style='Title'))
        rtl(doc.add_paragraph('این بخش در زمان ۱۸ دقیقهٔ اصلی نیست. برای پرسش‌های استاد و ارائهٔ مراحل تفصیلی استفاده شود.'))
    head=doc.add_paragraph(f'Slide {i} / 28    {s["title"]}',style='Heading 1')
    head.alignment=WD_ALIGN_PARAGRAPH.LEFT
    if s['seconds']:
        end=elapsed+s['seconds'];time=f'{elapsed//60:02}:{elapsed%60:02} تا {end//60:02}:{end%60:02}';elapsed=end
        pp=rtl(doc.add_paragraph('زمان پیشنهادی: '+time))
    else:pp=rtl(doc.add_paragraph('پیوست خارج از زمان اصلی'))
    pp.paragraph_format.keep_with_next=True
    for r in pp.runs:r.font.size=Pt(10);r.font.color.rgb=RGBColor.from_string('555555')
    sentences=re.split(r'(?<=\.)\s+',s['notes']);chunk=[];words=0
    for sentence in sentences:
        chunk.append(sentence);words+=len(sentence.split())
        if words>=68:
            rtl(doc.add_paragraph(' '.join(chunk)));chunk=[];words=0
    if chunk:rtl(doc.add_paragraph(' '.join(chunk)))
    doc.paragraphs[-1].paragraph_format.keep_with_next=True
    pp=doc.add_paragraph('Proof reference: '+s['proof']);pp.alignment=WD_ALIGN_PARAGRAPH.LEFT
    for r in pp.runs:r.font.size=Pt(9);r.font.color.rgb=RGBColor.from_string('555555')

rtl(doc.add_paragraph('پاسخ های کوتاه برای پرسش های محتمل',style='Heading 1'))
for q,a in [
('آیا این مرز همهٔ داده‌ها را تعیین تکلیف می‌کند؟','خیر. این مرز شرایط کافی برای صدور گواهی را مشخص می‌کند. نامعلوم بودن یعنی همین آزمون کافی نبوده است.'),
('آیا خروجی دو روش حتماً هدف واقعی است؟','خیر. حتی در مواردی که برابری دو زبان اثبات شده، هر دو ممکن است نسبت به هدف واقعی بیش‌تعمیم بدهند.'),
('آیا واقعاً قبل از اجرا تصمیم می‌گیریم؟','بله. برای صدور گواهی، داده و فرمول‌های اثبات‌شده بررسی می‌شوند. اجرای بعدی یادگیرنده فقط برای کنترل تطبیق بوده است.'),
('آیا این اثبات زمان واقعی را تضمین می‌کند؟','خیر. معیار رویدادهای حلقهٔ پیاده‌سازی مشخص است. تغییر پیاده‌سازی، ساخت محصول صریح یا محاسبهٔ کل هزینهٔ ماشین به تحلیل تازه نیاز دارد.'),
('آیا دو تریس حداقل عمومی است؟','خیر. خانوادهٔ تازه دقیقاً دو تریس مثبت و صفر منفی دارد و برای n≥4 گواهی سود خالص می‌گیرد. این آستانه کافی است و حداقل عمومی تعداد یا طول تریس‌ها نیست.'),
('آیا همهٔ منفی‌ها بی‌اثرند؟','خیر. کران عمومی برای منفی‌های دلخواه معتبر است. کران تیزتر فقط وقتی استفاده می‌شود که هر منفی حرفی بیرون از پشتیبان مثبت داشته باشد. این شرط برای عامل‌های محلی نیز جدا بررسی می‌شود.'),
('دو محور اصلی چقدر انجام شده‌اند؟','تشخیص عضویت در دامنهٔ گواهی و صحت انتخاب داخل آن اثبات و پیاده‌سازی شده‌اند. دامنهٔ عمومیِ همهٔ ورودی‌ها حل نشده است؛ کار بعدیِ هزینه، دقیق‌تر کردن کران‌ها و ارزان‌تر کردن تشخیص است.'),
('آیا ادامهٔ کار هزینه منتظر حل برابری است؟','خیر. برابری گسترده‌تر یک سؤال مستقل مرحلهٔ بعد است. گواهی‌های صرفاً هزینه با همان دامنهٔ ادعا قابل استفاده‌اند.')]:
    rtl(doc.add_paragraph(q,style='Heading 2'));rtl(doc.add_paragraph(a))

rtl(doc.add_paragraph('منابع همراه',style='Heading 1'))
for line in ['research/Research_Proofs_EN.md: full current proofs and explicit assumptions.',
             'research/static_selector.py and research/rpni_work_reference.py: selector and fixed reference.',
             'research/amortized_audit_results.json: exhaustive checks and independent fold validation.',
             'research/final_worked_examples.json: numerical certificates used in the slides.',
             'research/README_FA.md: research scope and reproducibility guide.']:
    pp=doc.add_paragraph(line);pp.alignment=WD_ALIGN_PARAGRAPH.LEFT
    for r in pp.runs:r.font.size=Pt(9.5)
footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
doc.core_properties.title='متن ارائه انتخاب مسیر یادگیری';doc.core_properties.author=''
doc.save(out/'Speaker_Notes_FA.docx')
print(out/'Speaker_Notes_FA.docx')
