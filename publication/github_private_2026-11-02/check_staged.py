"""Check full staged archive coverage and token patterns without logging values."""
from pathlib import Path
from collections import Counter
import io,json,re,subprocess,zipfile

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
patterns={
    'github_token':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
    'openai_key':re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b'),
    'aws_access_id':re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'slack_token':re.compile(rb'\bxox[baprs]-[A-Za-z0-9-]{20,}\b'),
    'private_key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')}
index=subprocess.check_output(['git','-c','core.longpaths=true','ls-files','--stage','-z'],cwd=ROOT)
blobs={};paths=set();groups=Counter()
for row in index.split(b'\0'):
    if not row:continue
    fields,path=row.split(b'\t',1);mode,oid,stage=fields.split()
    assert stage==b'0', 'unmerged index entry'
    name=path.decode('utf-8');paths.add(name);groups[name.split('/')[0]]+=1
    blobs.setdefault(oid,[]).append(name)
missing=[];actual_count=0
for p in ROOT.rglob('*'):
    if not p.is_file() or '.git' in p.relative_to(ROOT).parts:continue
    name=p.relative_to(ROOT).as_posix();actual_count+=1
    if name not in paths:missing.append(name)
assert subprocess.run(['git','-c','core.longpaths=true','diff','--quiet'],cwd=ROOT).returncode==0,'working changes after staging'
hits=[];large=[];total=0;office=0
proc=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,cwd=ROOT)
for oid,names in blobs.items():
    proc.stdin.write(oid+b'\n');proc.stdin.flush()
    header=proc.stdout.readline().split();assert header[1]==b'blob'
    size=int(header[2]);raw=proc.stdout.read(size);assert proc.stdout.read(1)==b'\n'
    total+=size
    if size>=100*1024*1024:large.append({'path':names[0],'bytes':size})
    for kind,pattern in patterns.items():
        if pattern.search(raw):hits.append({'path':names[0],'kind':kind})
    if any(n.lower().endswith(('.docx','.pptx','.xlsx')) for n in names):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            for member in z.namelist():
                if member.endswith('.xml'):
                    content=z.read(member)
                    for kind,pattern in patterns.items():
                        if pattern.search(content):hits.append({'path':names[0],'member':member,'kind':kind})
        office+=1
proc.stdin.close();assert proc.wait()==0
report={'status':'pass' if not missing and not hits and not large else 'needs_review','indexed_files':len(paths),'existing_workspace_files':actual_count,'unique_staged_blobs':len(blobs),'unique_blob_bytes':total,'office_archives_inspected':office,'top_level_indexed_file_counts':dict(groups),'missing_working_files':missing,'credential_pattern_hits':hits,'oversize_files':large,'scope':'Complete workspace except .git; initial history checked separately in PREFLIGHT.json. Newly generated check report is staged after this pass. Pattern scan is not a universal privacy guarantee.'}
with (OUT/'STAGED_CHECK.json').open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False))
assert report['status']=='pass'
