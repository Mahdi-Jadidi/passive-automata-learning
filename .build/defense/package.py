from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from xml.etree import ElementTree as ET
from docx import Document
import hashlib,json,re,sys

root=Path(__file__).parent
out=root.parents[1]/'output'/'defense'
sys.path.insert(0,str(out))
from defense_selector import select

examples={
 'example_split':dict(positive=['ab','ba'],negative=['c'],blocks=['a','b','c']),
 'example_global':dict(positive=['a','aa'],negative=['aaa'],blocks=['a','b']),
 'example_cost_only':dict(positive=[''],negative=[],blocks=['a','b']),
 'example_infeasible':dict(positive=['ab'],negative=['ba'],blocks=['a','b'])}
for name,x in examples.items():
    (out/(name+'.json')).write_text(json.dumps(x,indent=2),encoding='utf8')
    r=select(x['positive'],x['negative'],x['blocks'])
    (out/(name+'_certificate.json')).write_text(json.dumps(r,indent=2),encoding='utf8')

slides=json.loads((root/'slides.json').read_text(encoding='utf8'))
assert len(slides)==28 and all(x['seconds']>0 for x in slides[:14])
assert all(x['seconds']==0 for x in slides[14:])
assert sum(x['seconds'] for x in slides)==1080
notes=Document(out/'Speaker_Notes_FA.docx')
headings=[p.text for p in notes.paragraphs if p.style.name=='Heading 1' and p.text.startswith('Slide ')]
assert len(headings)==28
normalize=lambda s:' '.join(s.split())
doc_text=normalize(' '.join(p.text for p in notes.paragraphs))
for i,s in enumerate(slides,1):
    assert headings[i-1]==f'Slide {i} / 28    {s["title"]}'
    assert normalize(s['notes']) in doc_text,('Missing note text',i)
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with ZipFile(out/'RPNI_Defense_EN.pptx') as z:
    for i,s in enumerate(slides,1):
        xml=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        text=' '.join(t.text or '' for t in xml.findall('.//a:t',ns))
        assert s['title'] in text and f'{i} / 28' in text
        assert not re.search(r'[\u0600-\u06ff]',text),('Non-English visible text',i)
        note=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        nt=' '.join(t.text or '' for t in note.findall('.//a:t',ns))
        assert s['notes'] in nt,('Missing PowerPoint speaker notes',i)
        for block in s['blocks']:
            if block['kind']!='table':assert block['text'] in text,(i,block)
receipt=json.loads((root/'validation-v7.json').read_text(encoding='utf8'))
ppt_hash=hashlib.sha256((out/'RPNI_Defense_EN.pptx').read_bytes()).hexdigest()
assert ppt_hash==receipt['finalSha256']
results=json.loads((out/'audit_results.json').read_text(encoding='utf8'))
assert results['status']=='passed' and results['independent_candidate_checks']==14845
assert sum(results['decisions'].values())==2339
assert results['counts']['exhaustive_binary_samples']==2187
second=json.loads((out/'boundary_audit_results.json').read_text(encoding='utf8'))
assert second['status']=='passed' and second['valid_samples']==2216
assert second['independent_candidate_checks']==13650
for r in results['family_examples']:
    p=r['prediction'];assert p['selector_work']+p['split_upper']<p['global_lower']<=r['global']

(out/'slide_content.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf8')
files=sorted(p for p in out.iterdir() if p.is_file() and p.name not in ('manifest.json','Defense_Package.zip'))
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
with ZipFile(out/'Defense_Package.zip','w',ZIP_DEFLATED) as z:
    for p in files+[out/'manifest.json']:z.write(p,p.name)
with ZipFile(out/'Defense_Package.zip') as z:
    for name,digest in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==digest
print(json.dumps({'slides':28,'main_slides':14,'appendix_slides':14,'main_seconds':1080,
 'main_words':sum(len(s['notes'].split()) for s in slides[:14]),'audited_samples':2339,
 'independent_candidate_checks':14845,'ppt_sha256':ppt_hash,'package_entries':len(files)+1,
 'package_bytes':(out/'Defense_Package.zip').stat().st_size},indent=2))
