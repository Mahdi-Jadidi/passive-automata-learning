"""Rebuild the English research manuscript with embedded Windows fonts."""
from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / 'output/pdf/Certified_Maximum_Component_Alphabet_Partitioning_EN.pdf'

def inline(s):
    s = escape(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'`(.+?)`', r'<font name="Mono">\1</font>', s)
    s = re.sub(r'\b(W_i|Q_i|r_j|d_i|y_i|e_ab|R_B|K_B)\b', lambda m: m[0].split('_')[0]+'<sub>'+m[0].split('_')[1]+'</sub>', s)
    s = s.replace('π_B','π<sub>B</sub>')
    # References retain selectable URLs, allowing breaks inside long identifiers.
    s = re.sub(r'https?://[^\s]+', lambda m: '<font size="8">' + m[0] + '</font>', s)
    return s

def main():
    for name, filename in [('Article','times.ttf'), ('Article-Bold','timesbd.ttf'),
                           ('Article-Italic','timesi.ttf'), ('Mono','consola.ttf')]:
        pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/' + filename))
    pdfmetrics.registerFontFamily('Article', normal='Article', bold='Article-Bold', italic='Article-Italic', boldItalic='Article-Bold')
    body = ParagraphStyle('Body', fontName='Article', fontSize=10.5, leading=14,
                          spaceAfter=7, splitLongWords=True, allowWidows=0, allowOrphans=0)
    title = ParagraphStyle('Title', parent=body, fontName='Article-Bold', fontSize=20,
                           leading=23, alignment=TA_CENTER, spaceAfter=13)
    subtitle = ParagraphStyle('Subtitle', parent=body, fontSize=12, leading=15, alignment=TA_CENTER, spaceAfter=12)
    heading = ParagraphStyle('Heading', parent=body, fontName='Article-Bold', fontSize=12,
                            leading=15, spaceBefore=12, spaceAfter=7, keepWithNext=True)
    cell = ParagraphStyle('Cell', parent=body, fontSize=8.5, leading=11, spaceAfter=0)
    statement = ParagraphStyle('Statement', parent=body, keepWithNext=True)
    story = []
    lines = (HERE/'ARTICLE_EN.md').read_text(encoding='utf-8').splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[:\- ]+', x) for x in cells):
                    rows.append([Paragraph(inline(x), cell) for x in cells])
                i += 1
            count = len(rows[0])
            widths = [145] + [(A4[0]-110-145)/(count-1)]*(count-1)
            tab = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
            tab.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf1f4')),
                ('LINEBELOW',(0,0),(-1,0),0.6,colors.HexColor('#4c5965')),
                ('LINEBELOW',(0,-1),(-1,-1),0.5,colors.HexColor('#4c5965')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',(0,0),(-1,-1),5), ('RIGHTPADDING',(0,0),(-1,-1),5),
                ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            story.extend([tab, Spacer(1,9)])
            continue
        if line.startswith('# '):
            story.append(Paragraph(inline(line[2:]), title))
        elif line.startswith('## '):
            if line == '## References':
                story.append(PageBreak())
            story.append(Paragraph(inline(line[3:]), subtitle if i < 5 else heading))
        else:
            para = [line]
            while i+1 < len(lines) and lines[i+1].strip() and not lines[i+1].startswith(('#','|')):
                i += 1
                para.append(lines[i].strip())
            sty = statement if line.startswith(('**Theorem','**Lemma','**Algorithm')) else body
            story.append(Paragraph(inline(' '.join(para)), sty))
        i += 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    def footer(c, d):
        c.saveState()
        c.setStrokeColor(colors.HexColor('#c9ced2'))
        c.line(55,43,A4[0]-55,43)
        c.setFont('Article',8)
        c.setFillColor(colors.HexColor('#52606b'))
        c.drawString(55,31,'Research manuscript | V43 / V44 | 16 November 2026')
        c.drawRightString(A4[0]-55,31,str(d.page))
        c.restoreState()
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=55, leftMargin=55,
                            topMargin=47,bottomMargin=56,
                            title='Certified Maximum-Component Alphabet Partitioning from Global Traces',
                            author='Project research artifact', subject='Exact optimization, correctness proofs and bounded evaluation')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print(OUTPUT)

if __name__ == '__main__':
    main()
