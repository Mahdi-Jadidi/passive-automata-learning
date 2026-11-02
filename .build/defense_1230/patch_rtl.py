from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import re,sys,xml.etree.ElementTree as ET
src,dst=map(Path,sys.argv[1:3])
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
for pre,url in ns.items():ET.register_namespace(pre,url)
def q(x):pre,tag=x.split(':');return '{'+ns[pre]+'}'+tag
with ZipFile(src) as zin,ZipFile(dst,'w',ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data=zin.read(item.filename)
        if re.match(r'ppt/(slides/slide\d+|notesSlides/notesSlide\d+)\.xml$',item.filename):
            root=ET.fromstring(data)
            for p in root.iter(q('a:p')):
                text=''.join(t.text or '' for t in p.iter(q('a:t')))
                if re.search(r'[\u0600-\u06ff]',text):
                    pp=p.find(q('a:pPr'))
                    if pp is None:pp=ET.Element(q('a:pPr'));p.insert(0,pp)
                    pp.set('rtl','1')
                    for r in p.findall(q('a:r')):
                        rp=r.find(q('a:rPr'))
                        if rp is None:rp=ET.Element(q('a:rPr'));r.insert(0,rp)
                        rp.set('lang','fa-IR')
                        cs=rp.find(q('a:cs'))
                        if cs is None:cs=ET.SubElement(rp,q('a:cs'))
                        cs.set('typeface','Tahoma')
            data=ET.tostring(root,encoding='utf-8',xml_declaration=True)
        zout.writestr(item,data)
print(dst)
