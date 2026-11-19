"""Build both five-page manuscripts and archive rendered page checks."""
import hashlib
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

import pdfplumber
import pypdfium2
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FONTS = Path('C:/Windows/Fonts')
OUTPUT = {
    'v46': 'V46_Certified_Alphabet_Partitioning_Exhaustive_Teacher_Short.pdf',
    'v47': 'V47_Certified_Alphabet_Partitioning_Polynomial_Teacher_Short.pdf',
}
INK = colors.HexColor('#1d272c')
ACCENT = colors.HexColor('#244658')
RULE = colors.HexColor('#c5ced2')
WIDTH = A4[0]-108


def fonts():
    faces = {'Roman':'times.ttf', 'Bold':'timesbd.ttf', 'Italic':'timesi.ttf',
             'BoldItalic':'timesbi.ttf', 'Mono':'consola.ttf', 'Symbols':'seguisym.ttf'}
    for name, file in faces.items():
        pdfmetrics.registerFont(TTFont(name,str(FONTS/file)))
    pdfmetrics.registerFontFamily('Roman',normal='Roman',bold='Bold',italic='Italic',
                                  boldItalic='BoldItalic')


def inline(raw):
    s = escape(raw)
    s = re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s = re.sub(r'(?<!\S)\*([^*]+?)\*',r'<i>\1</i>',s)
    s = re.sub(r'@link\(([^|]+)\|([^()]+)\)',r'<link href="\2" color="#244658">\1</link>',s)
    s = re.sub(r'\^\{([^{}]+)\}',r'<super>\1</super>',s)
    s = re.sub(r'\^(\d+|[a-zA-Z])',r'<super>\1</super>',s)
    s = re.sub(r'([A-Za-zπ])_\(([a-zA-Z,]+)\)',r'\1<sub>\2</sub>',s)
    s = re.sub(r'(?<![\w/])([A-Za-zπ])_([A-Za-z0-9]{1,2})\b',r'\1<sub>\2</sub>',s)
    glyphs = pdfmetrics.getFont('Roman').face.charToGlyph
    symbols = pdfmetrics.getFont('Symbols').face.charToGlyph
    pieces = []
    for c in s:
        if ord(c) in glyphs:
            pieces.append(c)
        elif ord(c) in symbols:
            pieces.append('<font name="Symbols">'+c+'</font>')
        else:
            raise ValueError(f'No glyph for {c!r}')
    return ''.join(pieces)


def table(block, body):
    cells = [r.strip('|').split('|') for r in block.splitlines()]
    del cells[1]
    cell = ParagraphStyle('Cell',parent=body,fontSize=10.1,leading=13,spaceAfter=0)
    data = [[Paragraph(inline(x.strip()),cell) for x in row] for row in cells]
    result = Table(data,colWidths=[178,WIDTH-178],repeatRows=1,hAlign='LEFT')
    result.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf0')),
        ('LINEBELOW',(0,0),(-1,0),0.65,RULE),
        ('LINEBELOW',(0,-1),(-1,-1),0.65,RULE),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f6f8f9')]),
        ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5),
    ]))
    return result


def build(version):
    text = (HERE/(version+'.md')).read_text(encoding='utf-8')
    text = text.replace('{{OUTER}}',(HERE/'outer.md').read_text(encoding='utf-8').strip())
    pages = text.strip().split('<!-- page -->')
    assert len(pages)==5 and '{{' not in text
    target = ROOT/'output/pdf'/OUTPUT[version]
    title = text.splitlines()[0][2:]
    (HERE/(version+'_complete.md')).write_text(text,encoding='utf-8')
    body = ParagraphStyle('Body',fontName='Roman',fontSize=11,leading=14.5,textColor=INK,
                          spaceAfter=8,allowWidows=0,allowOrphans=0)
    h2 = ParagraphStyle('Section',parent=body,fontName='Bold',fontSize=15,leading=19,
                        spaceBefore=6,spaceAfter=7,textColor=ACCENT,keepWithNext=True)
    h3 = ParagraphStyle('Subsection',parent=h2,fontSize=11.4,leading=15,spaceBefore=4)
    title_style = ParagraphStyle('Title',parent=body,fontName='Bold',fontSize=24,
                                 leading=27.5,spaceAfter=9,textColor=ACCENT)
    meta = ParagraphStyle('Meta',parent=body,fontName='Italic',fontSize=10,spaceAfter=13)
    code = ParagraphStyle('Code',parent=body,fontName='Mono',fontSize=8.8,leading=12,
                          spaceBefore=2,leftIndent=13,textColor=ACCENT)
    citation = ParagraphStyle('Reference',parent=body,fontSize=9.8,leading=12.7,spaceAfter=5)
    story = []
    for number, page in enumerate(pages):
        if number:
            story.append(PageBreak())
        for block in re.split(r'\n[ \t]*\n',page.strip()):
            if block.startswith('# '):
                story.append(Paragraph(inline(block[2:]),title_style))
            elif block.startswith('@ '):
                story.append(Paragraph(inline(block[2:]),meta))
            elif block.startswith('## '):
                story.append(Paragraph(inline(block[3:]),h2))
            elif block.startswith('### '):
                story.append(Paragraph(inline(block[4:]),h3))
            elif block.startswith('|'):
                story.extend([table(block,body),Spacer(1,9)])
            elif block.startswith('```'):
                lines = block.splitlines()[1:-1]
                assert all(pdfmetrics.stringWidth(line,'Mono',code.fontSize)<WIDTH-code.leftIndent
                           for line in lines)
                story.append(Preformatted('\n'.join(lines),code))
            else:
                style = citation if re.match(r'^\[\d+\]',block) else body
                story.append(Paragraph(inline(' '.join(block.split())),style))

    def footer(canvas, doc):
        canvas.setStrokeColor(RULE)
        canvas.line(54,42,A4[0]-54,42)
        canvas.setFont('Roman',9)
        canvas.setFillColor(ACCENT)
        canvas.drawString(54,29,'Certified maximum alphabet partitioning  /  '+version.upper())
        canvas.drawRightString(A4[0]-54,29,str(doc.page))

    doc = SimpleDocTemplate(str(target),pagesize=A4,leftMargin=54,rightMargin=54,
                            topMargin=49,bottomMargin=54,title=title,invariant=1)
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return target


def verify_layout(pdf, version):
    directory = HERE/'rendered'/version
    directory.mkdir(parents=True,exist_ok=True)
    info = []
    raster = pypdfium2.PdfDocument(pdf)
    with pdfplumber.open(pdf) as document:
        assert len(document.pages)==5, (version,len(document.pages))
        for i,page in enumerate(document.pages,1):
            text = page.extract_text()
            words = page.extract_words()
            assert len(words)>190 and '\ufffd' not in text and '(cid:' not in text
            assert min(w['x0'] for w in words)>45 and max(w['x1'] for w in words)<page.width-45
            assert max(w['bottom'] for w in words)<page.height-19
            image = raster[i-1].render(scale=1.6).to_pil()
            path = directory/f'page-{i}.png'
            image.save(path)
            info.append(dict(page=i,first_line=text.splitlines()[0],words=len(words),
                             render_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return dict(file=pdf.relative_to(ROOT).as_posix(),pages=info,
                pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())


def main():
    fonts()
    records = {version:verify_layout(build(version),version) for version in OUTPUT}
    (HERE/'layout.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:len(v['pages']) for k,v in records.items()}),flush=True)


if __name__=='__main__':
    main()
