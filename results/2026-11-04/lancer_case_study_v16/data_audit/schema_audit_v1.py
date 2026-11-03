"""Own bounded data inspection; no imported artifact modules or YAML constructors."""
import ast, collections, hashlib, json, pathlib, urllib.request, datetime
R=pathlib.Path(__file__).resolve().parent
manifest=json.loads((R/'selected_manifest_v1.json').read_text())
rows=[]
for f in manifest['files']:
    p=R/f['local_path']; b=p.read_bytes()
    assert hashlib.sha256(b).hexdigest()==f['sha256']
    if '/one_host_network_validity_only/' not in f['archive_path']: continue
    assert len(b)<100000
    x=ast.literal_eval(b.decode())
    events=[e for episode in x for pair in episode for e in pair]
    rows.append(dict(path=f['archive_path'],episodes=len(x),steps=[len(v) for v in x],events=len(events),keys=sorted({k for e in events for k in e}),success_counts=dict(collections.Counter(e['success'] for e in events)),agents_by_pair=sorted({tuple(e['agent'] for e in pair) for ep in x for pair in ep}),first_pair=x[0][0]))
(R/'schema_actual_samples_v1.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
out=R/'upstream_license_v1';out.mkdir(exist_ok=False)
ledger=[]
url='https://api.github.com/repos/cage-challenge/cage-challenge-2/license'
row=dict(url=url,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
try:
    req=urllib.request.Request(url,headers={'User-Agent':'Research-data-provenance-audit','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req,timeout=25) as response:
        b=response.read(2*1024*1024+1);assert len(b)<=2*1024*1024
        row.update(http_status=response.status,final_url=response.url)
    (out/'github_license.json').write_bytes(b)
    row.update(status='downloaded',bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    data=json.loads(b)
    import base64
    text=base64.b64decode(data['content'])
    (out/'LICENSE.original').write_bytes(text)
    row.update(license_spdx=data.get('license',{}).get('spdx_id'),license_path=data['path'],license_sha256=hashlib.sha256(text).hexdigest(),github_content_sha=data['sha'],source_html_url=data['html_url'])
except Exception as e: row.update(status='access_failed',error=repr(e))
(out/'access_ledger.json').write_text(json.dumps([row],indent=2),encoding='utf8')
print(json.dumps(dict(samples=rows,license=row),indent=2))
