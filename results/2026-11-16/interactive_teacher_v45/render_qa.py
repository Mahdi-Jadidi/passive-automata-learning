"""Render every manuscript page and write text-boundary QA plus contact sheets."""
from pathlib import Path
import json
import pypdfium2 as pdfium
import pdfplumber
from PIL import Image, ImageOps, ImageDraw
from build_pdf import OUTPUT, HERE

def main():
    target=HERE/'rendered'
    target.mkdir(exist_ok=True)
    pdf=pdfium.PdfDocument(str(OUTPUT))
    thumbs=[]
    for i in range(len(pdf)):
        page=pdf[i]
        pic=page.render(scale=1.5).to_pil().convert('RGB')
        pic.save(target/f'page_{i+1:02}.png')
        thumb=ImageOps.contain(pic,(350,495))
        tile=Image.new('RGB',(370,525),'#dde2e6')
        tile.paste(thumb,((370-thumb.width)//2,10))
        ImageDraw.Draw(tile).text((12,507),f'Page {i+1}',fill='black')
        thumbs.append(tile)
    for start in range(0,len(thumbs),6):
        subset=thumbs[start:start+6]
        sheet=Image.new('RGB',(1110,525*((len(subset)+2)//3)),'white')
        for j,tile in enumerate(subset):sheet.paste(tile,((j%3)*370,(j//3)*525))
        sheet.save(target/f'contact_{start//6+1:02}.png')
    checks=[]
    with pdfplumber.open(OUTPUT) as doc:
        for i,page in enumerate(doc.pages):
            chars=page.chars
            out=[x['text'] for x in chars if x['x0']<40 or x['x1']>page.width-40 or x['top']<20 or x['bottom']>page.height-20]
            checks.append({'page':i+1,'characters':len(chars),'outside_safe_page_bounds':out,
                           'replacement_characters':page.extract_text().count('\ufffd')})
    assert all(x['characters']>50 and not x['outside_safe_page_bounds'] and not x['replacement_characters'] for x in checks)
    (HERE/'pdf_layout_qa.json').write_text(json.dumps({'pages':len(pdf),'checks':checks},indent=2)+'\n')
    print(json.dumps({'pages':len(pdf),'bounds_check':'PASS','rendered':str(target)}))

if __name__=='__main__':main()
