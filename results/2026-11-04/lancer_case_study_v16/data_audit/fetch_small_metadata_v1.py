"""Read-only public metadata retrieval; never executes downloaded content."""
import hashlib,json,time,urllib.request
from datetime import datetime,timezone
from pathlib import Path
A=Path(__file__).resolve().parent
URLS=[('zenodo_record.json','https://zenodo.org/api/records/19828945'),('zenodo_README.md','https://zenodo.org/records/19828945/files/README.md?download=1'),('zenodo_LICENSE','https://zenodo.org/records/19828945/files/LICENSE?download=1'),('zenodo_record.html','https://zenodo.org/records/19828945'),('crossref.json','https://api.crossref.org/works/10.1007/978-3-032-32519-8_25')]
def main():
    directory=A/'metadata_v1';directory.mkdir(exist_ok=False);ledger=[]
    for name,url in URLS:
        row={'url':url,'started_utc':datetime.now(timezone.utc).isoformat()};started=time.perf_counter()
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (research metadata audit)','Accept':'application/json,text/plain,text/html;q=0.8'})
            with urllib.request.urlopen(req,timeout=25) as response:
                row.update(http_status=response.status,final_url=response.url,headers=dict(response.headers));raw=response.read(2*1024*1024+1)
                if len(raw)>2*1024*1024:raise RuntimeError('metadata exceeded2MiB; no bulk download authorized here')
            with (directory/name).open('xb') as f:f.write(raw)
            row.update(status='downloaded',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),saved_path=str(directory/name))
        except Exception as e:row.update(status='access_failed',error=repr(e))
        row['elapsed_seconds']=time.perf_counter()-started;ledger.append(row)
        with (directory/'access_ledger.json').open('w') as f:json.dump(ledger,f,indent=2)
        print(json.dumps(row),flush=True)
if __name__=='__main__':main()
