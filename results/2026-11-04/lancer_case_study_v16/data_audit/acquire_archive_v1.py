"""Authorized public archive acquisition into non-bundle cache; no execution."""
import hashlib,json,time,urllib.request,urllib.error
from datetime import datetime,timezone
from pathlib import Path
A=Path(__file__).resolve().parent;WORK=A.parents[3]
URL='https://zenodo.org/records/19828945/files/cas-artifact-cav2026.zip?download=1';SIZE=244813827;MD5='8390b436e7e2378b447558586d82d185'
def main():
    cache=(WORK/'.cache/lancer').resolve();assert WORK.resolve() in cache.parents;cache.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');out=cache/f'cas-artifact-cav2026_{stamp}.zip.part';log=A/f'archive_access_{stamp}.json';record={'url':URL,'expected_bytes':SIZE,'expected_md5':MD5,'cache_path':str(out),'status':'starting','started_utc':datetime.now(timezone.utc).isoformat(),'downloaded_bytes':0}
    def write():log.write_text(json.dumps(record,indent=2))
    write();started=time.perf_counter()
    try:
        request=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0 (research metadata audit)','Accept-Encoding':'identity','Referer':'https://zenodo.org/records/19828945'})
        with urllib.request.urlopen(request,timeout=45) as response:
            record.update(http_status=response.status,final_url=response.url,content_length=response.headers.get('Content-Length'))
            assert response.status==200 and int(response.headers.get('Content-Length',SIZE))==SIZE
            h=hashlib.sha256();m=hashlib.md5();count=0;record['status']='downloading';write()
            with out.open('xb') as f:
                while True:
                    chunk=response.read(1024*1024)
                    if not chunk:break
                    count+=len(chunk);assert count<=SIZE;f.write(chunk);h.update(chunk);m.update(chunk);record['downloaded_bytes']=count;write()
            assert count==SIZE and m.hexdigest()==MD5
            final=out.with_suffix('');out.rename(final);record.update(status='verified_archive_downloaded',cache_path=str(final),sha256=h.hexdigest(),md5=m.hexdigest())
    except urllib.error.HTTPError as e:
        body=e.read(4096);error=A/f'archive_HTTP_error_{stamp}.txt';error.write_bytes(body);record.update(status='access_failed',error=repr(e),http_status=e.code,error_body_path=str(error))
    except Exception as e:record.update(status='download_failed',error=repr(e))
    finally:record['elapsed_seconds']=time.perf_counter()-started;write()
    print(json.dumps(record));return 0 if record['status']=='verified_archive_downloaded' else 1
if __name__=='__main__':raise SystemExit(main())
