from pathlib import Path
import re, json, importlib.util
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

BASE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('english_builder',BASE/'build_article_docx_v2.py')
en=importlib.util.module_from_spec(spec); spec.loader.exec_module(en)
SOURCE=(BASE.parent/'content/ARTICLE_EN.md').read_text(encoding='utf-8')
TEXT=(BASE/'translation_fa_exact.md').read_text(encoding='utf-8')
PSEUDO=re.search(r'```text\n(.*?)\n```',SOURCE,re.S).group(1)
REFS=SOURCE.split('## References\n\n')[1]
TEXT=TEXT.replace('{{PSEUDOCODE}}','```text\n'+PSEUDO+'\n```').replace('{{REFERENCES}}',REFS)
OUT=BASE/'output/Exact_Alphabet_Partitioning_Article_FA_Exact.docx'
doc=Document(); en.configure(doc)
sec=doc.sections[0]
sec.top_margin=Cm(2.0); sec.bottom_margin=Cm(2.0)
sec.left_margin=Cm(2.1); sec.right_margin=Cm(2.1)

def attr(parent,tag,val):
    e=parent.find(qn(tag))
    if e is None: e=OxmlElement(tag); parent.append(e)
    e.set(qn('w:val'),str(val)); return e

for name,size in [('Normal',11),('Title',18),('Heading 1',14),('Heading 2',12)]:
    st=doc.styles[name]; st.font.name='Arial'; st.font.size=Pt(size)
    rp=st._element.get_or_add_rPr()
    fonts=rp.find(qn('w:rFonts'))
    if fonts is None: fonts=OxmlElement('w:rFonts'); rp.append(fonts)
    for a in ['ascii','hAnsi','cs','eastAsia']: fonts.set(qn('w:'+a),'Arial')
    attr(rp,'w:szCs',str(size*2))
    st.paragraph_format.line_spacing=1.18
    st.paragraph_format.space_after=Pt(6)
    st.font.color.rgb=RGBColor(0,0,0)

def rtl(p,on=True):
    attr(p._p.get_or_add_pPr(),'w:bidi','1' if on else '0')
    # Word mirrors physical left/right for a bidi paragraph. Logical start
    # reliably gives right alignment in the Persian paragraphs.
    attr(p._p.get_or_add_pPr(),'w:jc','start' if on else 'left')

PERSIAN=re.compile(r'[\u0600-\u06ff\u200c]')
MATH=re.compile(r'(0\^\(m−1\)|0\^m|[ΣBak]\*|π_[BD]|[HFV]_B|Σ_k|n_j|[as][₀₁₂₃₄₅₆₇₈₉ₘᵢ₋]+|sᵢ)')

def run(p,t,bold=False,italic=False,mono=False,neutral=False):
    if not t:return
    r=p.add_run(t); r.bold=bold; r.italic=italic
    rp=r._r.get_or_add_rPr(); attr(rp,'w:rtl','1' if PERSIAN.search(t) or neutral else '0')
    fonts=rp.find(qn('w:rFonts'))
    if fonts is None: fonts=OxmlElement('w:rFonts'); rp.append(fonts)
    for k in ['ascii','hAnsi','cs','eastAsia']: fonts.set(qn('w:'+k),'Arial')
    lang=OxmlElement('w:lang');lang.set(qn('w:val'),'fa-IR' if PERSIAN.search(t) else 'en-US');lang.set(qn('w:bidi'),'fa-IR');rp.append(lang)
    if mono:
        r.font.size=Pt(9)
        attr(rp,'w:szCs','18')
    return r

def math_token(p,t):
    om=OxmlElement('m:oMath')
    if t.startswith('0^'):
        ex=t[3:-1] if t.startswith('0^(') else t[2:]
        en.script_node(om,'sSup','0',ex)
    elif '_' in t:
        a,b=t.split('_',1);en.script_node(om,'sSub',a,b)
    elif t.endswith('*'):en.script_node(om,'sSup',t[:-1],'*')
    elif len(t)>1:
        tr=str.maketrans('₀₁₂₃₄₅₆₇₈₉ₘᵢ₋','0123456789mi−')
        en.script_node(om,'sSub',t[0],t[1:].translate(tr))
    p._p.append(om)

def math_expr(p,t):
    tmp=doc.add_paragraph()
    cursor=0
    om=OxmlElement('m:oMath')
    for m in MATH.finditer(t):
        if m.start()>cursor:en.math_run(om,t[cursor:m.start()])
        math_token(tmp,m.group())
        node=tmp._p[-1]
        for child in list(node):om.append(child)
        tmp._p.remove(node)
        cursor=m.end()
    if cursor<len(t):en.math_run(om,t[cursor:])
    doc._element.body.remove(tmp._p)
    p._p.append(om)

def plain(p,t,bold=False,italic=False,mono=False):
    # Explicit run direction prevents English technical phrases and equations
    # from being reversed inside the Persian paragraph.
    for part in re.split(r'([\u0600-\u06ff\u200c]+(?:[ \u200c]+[\u0600-\u06ff\u200c]+)*)',t):
        if not part:continue
        if PERSIAN.search(part):run(p,part,bold,italic,mono);continue
        lead=re.match(r'^\s*',part).group();trail=re.search(r'\s*$',part).group()
        core=part.strip()
        run(p,lead,bold,italic,neutral=True)
        if not core:continue
        run(p,'\u200e',bold,italic)
        if mono:
            run(p,core,bold,italic,True)
            run(p,'\u200e',bold,italic);run(p,trail,bold,italic,neutral=True);continue
        cursor=0
        for m in MATH.finditer(core):
            run(p,core[cursor:m.start()],bold,italic);math_token(p,m.group());cursor=m.end()
        run(p,core[cursor:],bold,italic)
        run(p,'\u200e',bold,italic);run(p,trail,bold,italic,neutral=True)

def inline(p,t):
    t=re.sub(r'(?<=[A-Za-z`])[\u064b-\u065f]+','',t)
    cur=0
    for m in re.finditer(r'(\*\*[^*]+\*\*|`[^`]+`|\*اثبات\.\*)',t):
        plain(p,t[cur:m.start()]);s=m.group()
        if s.startswith('**'):plain(p,s[2:-2],bold=True)
        elif s.startswith('`'):
            s=s[1:-1]
            # API keys, hashes, paths, and literal arrays stay literal.
            iscode=bool(re.search(r'[A-Za-z]{2,}_|/|\.py|\.md|\.json|^[0-9a-f]{64}$|^\[|^candidate_calls',s))
            if not iscode and re.search(r'[ΣΠπ∈∉∅⊆≥≤≠∀∃ε𝒱]|[=^*]|^min\(|^O\(',s):
                math_expr(p,s)
            else:plain(p,s,mono=iscode)
        else:plain(p,s[1:-1],italic=True)
        cur=m.end()
    plain(p,t[cur:])

def table(lines):
    rows=[]
    for l in lines:
        if re.match(r'^\|[-| ]+\|$',l):continue
        rows.append([v.strip() for v in l.strip('|').split('|')])
    tb=doc.add_table(rows=0,cols=2);tb.style='Table Grid';tb.autofit=False
    pr=tb._tbl.tblPr;bi=OxmlElement('w:bidiVisual');pr.append(bi)
    for idx,vals in enumerate(rows):
        row=tb.add_row();en.cant_split(row)
        if idx==0:en.repeat_table_header(row)
        for j,v in enumerate(vals):
            c=row.cells[j];c.width=Cm(2 if j==0 else 14.8)
            en.set_cell_margins(c,top=90,bottom=90,start=100,end=100)
            p=c.paragraphs[0];rtl(p);inline(p,v)
            p.paragraph_format.space_after=Pt(3)
            if idx==0:
                en.set_cell_shading(c,'EEEEEE')
                for r in p.runs:r.bold=True

lines=TEXT.splitlines();i=0
while i<len(lines):
    l=lines[i]
    if not l.strip():i+=1;continue
    if l.startswith('```text'):
        b=[];i+=1
        while not lines[i].startswith('```'):b.append(lines[i]);i+=1
        br=doc.add_paragraph();br.paragraph_format.page_break_before=True
        br.paragraph_format.space_after=Pt(0);br.paragraph_format.space_before=Pt(0)
        br.paragraph_format.line_spacing=Pt(1);br.paragraph_format.keep_with_next=True
        en.pseudocode_table(doc,'\n'.join(b))
        for row in doc.tables[-1].rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    rtl(p,False)
                    for r in p.runs:
                        attr(r._r.get_or_add_rPr(),'w:rtl','0')
        i+=1;continue
    if l.startswith('|'):
        b=[]
        while i<len(lines) and lines[i].startswith('|'):b.append(lines[i]);i+=1
        table(b);continue
    if l.startswith('    '):
        p=en.display_equation(doc,l.strip());rtl(p,False);p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        i+=1;continue
    h=re.match(r'^(#{1,3}) (.*)',l)
    if h:
        style={1:'Title',2:'Heading 1',3:'Heading 2'}[len(h.group(1))]
        p=doc.add_paragraph(style=style);rtl(p);inline(p,h.group(2));i+=1;continue
    p=doc.add_paragraph();rtl(p);inline(p,l)
    if re.match(r'^\[\d\]',l):
        rtl(p,False);p.paragraph_format.space_after=Pt(9)
    if l.startswith('**'):p.paragraph_format.keep_with_next=True
    i+=1

# Set all native equation runs to LTR, independent of surrounding bidi text.
for om in doc._element.iter(qn('m:oMath')):
    for mr in om.iter(qn('m:r')):
        rp=mr.find(qn('w:rPr'))
        if rp is None:rp=OxmlElement('w:rPr');mr.insert(0,rp)
        attr(rp,'w:rtl','0')
        f=OxmlElement('w:rFonts');f.set(qn('w:ascii'),'Cambria Math');f.set(qn('w:hAnsi'),'Cambria Math');rp.append(f)

doc.core_properties.title='تعیین دقیق alphabet partition از traceهای positive و negative با تعداد نامعلوم componentها'
doc.core_properties.subject='ترجمهٔ کامل فارسی مقاله با حفظ اصطلاحات تخصصی و فرمول‌های انگلیسی'
doc.core_properties.language='fa-IR'
OUT.parent.mkdir(parents=True,exist_ok=True);doc.save(OUT)

# Content preservation checks: all sections, proof starts, displayed equations,
# the literal pseudocode, references, and provenance hashes must be present.
assert len(re.findall(r'^## ',TEXT,re.M))==len(re.findall(r'^## ',SOURCE,re.M))
assert len(re.findall(r'^\*اثبات',TEXT,re.M))==len(re.findall(r'^\*Proof',SOURCE,re.M))==15
assert len(re.findall(r'^    ',TEXT,re.M))==len(re.findall(r'^    ',SOURCE,re.M))==8
assert PSEUDO in TEXT
for token in re.findall(r'`([0-9a-f]{64})`',SOURCE):assert token in TEXT
assert TEXT.split('## منابع\n\n')[1].strip()==REFS.strip()
summary={'output':str(OUT),'source_sections':len(re.findall(r'^## ',SOURCE,re.M)),
         'translated_sections':len(re.findall(r'^## ',TEXT,re.M)), 'proofs':15,
         'display_equation_lines':8,'pseudocode_lines':len(PSEUDO.splitlines()),
         'references':6,'native_equations':len(list(doc._element.iter(qn('m:oMath'))))}
(BASE/'translation_fidelity_checks.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=True,indent=2))
