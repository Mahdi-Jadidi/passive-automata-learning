"""Assemble Markdown sources, build the article and render every PDF page."""
import argparse
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
from reportlab.platypus import (KeepTogether, Paragraph, Preformatted, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STUDY = HERE.parent
PDF = ROOT/'output/pdf/Certified_Maximum_Alphabet_Partitioning_Interactive_Teacher_V46_EN.pdf'
INK = colors.HexColor('#172329')
BLUE = colors.HexColor('#174c61')
RULE = colors.HexColor('#b5c8cf')


def compose():
    evidence = STUDY/'evidence'
    summary = json.loads((evidence/'summary.json').read_text(encoding='utf-8'))
    review = json.loads((STUDY/'audit/foundations.json').read_text(encoding='utf-8'))
    mutations = json.loads((STUDY/'audit/adversarial_replay_results.json').read_text(encoding='utf-8'))
    nc = summary['corpus'].get('INCOMPLETE',0)
    completed = sum(summary['corpus'].values())-nc
    b = summary['benchmark_first_completed']
    assert all(p['returncode']==0 for p in review['kernel_replay'])
    assert all(p['ok'] for p in review['opaque_oracle_cases']) and review['teacher_timeout']['passed']
    assert all(p['actual']==p['expected'] for p in mutations['checks'])
    src = {name:(HERE/(name+'.md')).read_text(encoding='utf-8').strip()
           for name in ('article','proof','related','references')}
    rendered = src['article']
    proof = src['proof'].replace('# Correctness of the exact teacher-guided optimization',
                                 '## 4. Correctness and optimality',1)
    proof = re.sub(r'(?m)^## (?!4\.)','### ',proof)
    for a,z in {
        'RELATED': src['related'].replace('## Related work','## 2. Related work',1),
        'PROOF': proof,
        'REFERENCES': src['references'],
        'RESULTS': (evidence/'results.md').read_text(encoding='utf-8').strip(),
        'ABSTRACT_RESULTS': f'The longer-budget audit verified {completed:,} of 2,261 inputs '
                            f'and left {nc:,} incomplete. V45 finished {b["v45"]}/10 fixed cases '
                            f'at 60 seconds, compared with {b["v43"]}/10 for V43. '
                            'Finite tests concern sample compatibility and proof validity.',
        'CONCLUSION_RESULTS': f'The 60-second budget increased fixed-case V45 completions '
                              f'from 3/10 to {b["v45"]}/10. The remaining censored cases and '
                              'projection timings delimit the practical results.',
        'REVIEW_RESULTS': f'The four frozen V45 kernel scripts passed again, including the '
                          f'30 raw Cartesian-join comparisons and 5,000-symbol projection case. '
                          f'The new review passed {len(review["opaque_oracle_cases"])} independent '
                          f'small partition-oracle cases with opaque IDs, a deterministically '
                          f'interrupted teacher build, and {len(mutations["checks"])} certificate '
                          'replays and mutations. The interruption produced no completed local '
                          'table, candidate verdict or cut. In the first opaque-ID attempt, one '
                          'case exceeded the 2-second solver cap. It completed at the revised '
                          '60-second review cap. The initial resource outcome is preserved. '
                          'The first review driver also invoked the verifier on the incomplete '
                          'envelope. Its schema rejection carried no feasibility meaning. The '
                          'replay submits completed mathematical results only.',
    }.items():
        rendered = rendered.replace('{{'+a+'}}',z)
    assert '{{' not in rendered
    return rendered


def render(source, out, fonts):
    font_files = {'Text':'times.ttf','Bold':'timesbd.ttf','Italic':'timesi.ttf',
                  'BoldItalic':'timesbi.ttf','Mono':'consola.ttf','Symbols':'seguisym.ttf'}
    for name, file in font_files.items():
        pdfmetrics.registerFont(TTFont(name, str(fonts/file)))
    pdfmetrics.registerFontFamily('Text', normal='Text', bold='Bold', italic='Italic',
                                  boldItalic='BoldItalic')
    glyphs = pdfmetrics.getFont('Text').face.charToGlyph
    symbols = pdfmetrics.getFont('Symbols').face.charToGlyph

    def inline(s):
        s = escape(s)
        s = re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
        s = re.sub(r'(?<!\S)\*(\S(?:[^*]*?\S)?)\*',r'<i>\1</i>',s)
        s = re.sub(r'\^\{([^{}]+)\}',r'<super>\1</super>',s)
        s = re.sub(r'\^(\d+(?:\.\d+)?|[a-zA-Z])',r'<super>\1</super>',s)
        s = re.sub(r'([A-Za-zπ∑⋂])_\{([^{}]+)\}',r'\1<sub>\2</sub>',s)
        s = re.sub(r'([A-Za-zπ∑⋂])_\(([A-Za-z,]+)\)',r'\1<sub>\2</sub>',s)
        s = re.sub(r'(?<![\w/])([A-Za-zπ∑⋂])_([A-Za-z0-9]{1,2})\b',r'\1<sub>\2</sub>',s)
        s = re.sub(r'`([^`]+)`',r'<font name="Mono">\1</font>',s)
        parts = []
        for c in s:
            if ord(c) in glyphs:
                parts.append(c)
            elif ord(c) in symbols:
                parts.append('<font name="Symbols">'+c+'</font>')
            else:
                raise ValueError(f'Unsupported glyph {c!r}')
        return ''.join(parts)

    body = ParagraphStyle('Body',fontName='Text',fontSize=11,leading=14.5,textColor=INK,
                          spaceAfter=7, allowWidows=0,allowOrphans=0)
    title = ParagraphStyle('Title',parent=body,fontName='Bold',fontSize=26,leading=29,
                           spaceAfter=12,textColor=BLUE)
    meta = ParagraphStyle('Meta',parent=body,fontName='Italic',fontSize=10,spaceAfter=15)
    h2 = ParagraphStyle('H2',parent=body,fontName='Bold',fontSize=15,leading=19,
                        spaceBefore=12,spaceAfter=5,keepWithNext=True,textColor=BLUE)
    h3 = ParagraphStyle('H3',parent=h2,fontSize=12,leading=15,spaceBefore=9)
    code = ParagraphStyle('Code',parent=body,fontName='Mono',fontSize=8.7,leading=12.5,
                          leftIndent=12,spaceAfter=9,textColor=BLUE)
    cell = ParagraphStyle('Cell',parent=body,fontSize=9.3,leading=11.5,spaceAfter=0)
    cell_head = ParagraphStyle('Cell head',parent=cell,fontName='Bold')

    width = A4[0]-102
    story = []
    algorithm = None
    heading = {1:title,2:h2,3:h3}
    chunks = re.split(r'\n[ \t]*\n', source.strip())
    for i, raw in enumerate(chunks):
        is_formula = raw.startswith('    ')
        chunk = raw.strip()
        if chunk.startswith('```'):
            lines = chunk.splitlines()[1:-1]
            assert all(pdfmetrics.stringWidth(x,'Mono',code.fontSize) < width-code.leftIndent
                       for x in lines), lines
            block = Preformatted('\n'.join(lines),code)
            story.append(KeepTogether([algorithm,block] if algorithm else [block]))
            algorithm = None
        elif chunk.startswith('|'):
            data = [[x.strip() for x in row.strip().strip('|').split('|')]
                    for row in chunk.splitlines()]
            del data[1]
            n = len(data[0])
            assert all(len(row)==n for row in data), data
            first = 115 if n>=5 else 128
            tab = Table([[Paragraph(inline(x),cell_head if i==0 else cell) for x in row]
                         for i,row in enumerate(data)],
                        colWidths=[first]+[(width-first)/(n-1)]*(n-1),repeatRows=1)
            tab.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4eef1')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LINEBELOW',(0,0),(-1,0),0.6,RULE),
                ('LINEBELOW',(0,-1),(-1,-1),0.6,RULE),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f8f9')]),
                ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
            ]))
            story.extend([tab,Spacer(1,9)])
        elif is_formula:
            story.append(Paragraph(inline(chunk),ParagraphStyle('Equation',parent=body,leftIndent=20)))
        elif chunk.startswith('### Algorithm'):
            algorithm = Paragraph(inline(chunk[4:]),h3)
        elif chunk.startswith('#'):
            mark,label = chunk.split(' ',1)
            story.append(Paragraph(inline(label),heading[len(mark)]))
        else:
            story.append(Paragraph(inline(' '.join(chunk.split())),meta if i==1 else body))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(RULE)
        canvas.line(51,41,A4[0]-51,41)
        canvas.setFont('Text',9)
        canvas.setFillColor(BLUE)
        canvas.drawString(51,28,'Certified maximum alphabet partitioning  /  V46')
        canvas.drawRightString(A4[0]-51,28,str(doc.page))
        canvas.restoreState()

    document = SimpleDocTemplate(str(out),pagesize=A4,leftMargin=51,rightMargin=51,
                                 topMargin=55,bottomMargin=53,
                                 title='Certified Maximum Alphabet Partitioning with an Exact Interactive Teacher',
                                 author='Passive automata learning research project')
    document.build(story,onFirstPage=footer,onLaterPages=footer)


def qa(pdf, directory):
    directory.mkdir(exist_ok=True)
    raster = pypdfium2.PdfDocument(pdf)
    record = []
    with pdfplumber.open(pdf) as doc:
        for number,page in enumerate(doc.pages,1):
            words = page.extract_words()
            text = page.extract_text()
            assert words and '\ufffd' not in text and '(cid:' not in text
            assert min(w['x0'] for w in words)>45 and max(w['x1'] for w in words)<page.width-45
            assert max(w['bottom'] for w in words)<page.height-19
            image = raster[number-1].render(scale=1.6).to_pil()
            target = directory/f'page-{number:02}.png'
            image.save(target)
            record.append(dict(page=number, width=image.width,height=image.height,words=len(words),
                               first_line=text.splitlines()[0], sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    (directory/'layout.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(f'{len(record)} pages rendered to {directory}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fonts',type=Path,default=Path('C:/Windows/Fonts'))
    parser.add_argument('--pdf',type=Path,default=PDF)
    parser.add_argument('--render-dir',type=Path,default=HERE/'rendered')
    args = parser.parse_args()
    source = compose()
    (HERE/'article_complete.md').write_text(source+'\n',encoding='utf-8')
    render(source,args.pdf,args.fonts)
    qa(args.pdf,args.render_dir)


if __name__ == '__main__':
    main()
