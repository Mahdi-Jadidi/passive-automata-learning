"""Read-only prepublication inventory and credential-pattern checks, no values logged."""
from pathlib import Path
import hashlib,json,re,subprocess

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
patterns={
    'github_token':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
    'openai_key':re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b'),
    'aws_access_id':re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'slack_token':re.compile(rb'\bxox[baprs]-[A-Za-z0-9-]{20,}\b'),
    'private_key':re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----')}
text_ext={'.py','.js','.ts','.tsx','.jsx','.json','.jsonl','.md','.txt','.html','.css','.xml','.yaml','.yml','.toml','.ini','.cfg','.env','.ps1','.sh','.csv','.log','.svg'}
hits=[];names=[];files=[];large=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or '.git' in p.relative_to(ROOT).parts:continue
    rel=p.relative_to(ROOT).as_posix()
    if p.parent==OUT and p.name in {'PREFLIGHT.json','WORKSPACE_INVENTORY.json'}:continue
    size=p.stat().st_size
    files.append({'path':rel,'bytes':size,'sha256':sha(p)})
    if size>=100*1024*1024:large.append({'path':rel,'bytes':size})
    if p.name.startswith('.env') or p.name.lower() in {'credentials','credentials.json','id_rsa','id_ed25519','.npmrc','.pypirc'}:names.append(rel)
    if p.suffix.lower() in text_ext or p.name in {'.gitignore','.gitattributes'}:
        raw=p.read_bytes()
        for label,regex in patterns.items():
            if regex.search(raw):hits.append({'path':rel,'kind':label})

# Check every reachable Git blob, not just the current branch's working files.
objects=subprocess.check_output(['git','-c','core.longpaths=true','rev-list','--objects','--all'],cwd=ROOT)
oids=[]
for row in objects.splitlines():
    oid=row.split(b' ',1)[0]
    if oid not in oids:oids.append(oid)
metadata=subprocess.check_output(['git','cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)'],input=b'\n'.join(oids)+b'\n',cwd=ROOT)
history_hits=[];history_large=[];blob_count=0
proc=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,cwd=ROOT)
for row in metadata.splitlines():
    oid,kind,length=row.split();size=int(length)
    if kind!=b'blob':continue
    blob_count+=1
    if size>=100*1024*1024:history_large.append({'oid':oid.decode(),'bytes':size})
    proc.stdin.write(oid+b'\n');proc.stdin.flush()
    header=proc.stdout.readline();raw=proc.stdout.read(size);assert proc.stdout.read(1)==b'\n'
    for label,regex in patterns.items():
        if regex.search(raw):history_hits.append({'oid':oid.decode(),'kind':label})
proc.stdin.close();assert proc.wait()==0
report={'workspace_files':len(files),'workspace_bytes':sum(x['bytes'] for x in files),'suspected_sensitive_filenames':names,'pattern_hits':hits,'oversize_working_files':large,'history_blobs_checked':blob_count,'history_pattern_hits':history_hits,'oversize_history_blobs':history_large,'scope':'Pattern-based prepublication check, not a guarantee against all possible sensitive information; matching values are never logged.'}
for name,data in [('WORKSPACE_INVENTORY.json',files),('PREFLIGHT.json',report)]:
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(data,f,ensure_ascii=False,indent=2)
print(json.dumps(report,ensure_ascii=False))
