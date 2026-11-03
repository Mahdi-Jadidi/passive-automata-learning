"""Bounded remote ZIP catalogue only; never extracts or runs archive code."""
import hashlib,json,struct,urllib.request
from pathlib import Path
from datetime import datetime,timezone
A=Path(__file__).resolve().parent;URL='https://zenodo.org/records/19828945/files/cas-artifact-cav2026.zip?download=1';TOTAL=244813827
def main():
    out=A/'zip_index_v1';out.mkdir(exist_ok=False);ledger=[]
    def fetch(start,end,name):
        row={'url':URL,'range':[start,end],'utc':datetime.now(timezone.utc).isoformat()};ledger.append(row)
        try:
            req=urllib.request.Request(URL,headers={'Range':f'bytes={start}-{end}','User-Agent':'Mozilla/5.0','Accept-Encoding':'identity'})
            with urllib.request.urlopen(req,timeout=30) as r:
                row.update(status=r.status,content_range=r.headers.get('Content-Range'),length=r.headers.get('Content-Length'))
                if r.status!=206:raise RuntimeError('server ignored Range; bulk payload not read')
                assert r.headers.get('Content-Range')==f'bytes {start}-{end}/{TOTAL}'
                raw=r.read(end-start+2);assert len(raw)==end-start+1
            (out/name).write_bytes(raw);row.update(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest());return raw
        except Exception as e:row['error']=repr(e);raise
        finally:(out/'range_access_ledger.json').write_text(json.dumps(ledger,indent=2))
    raw=fetch(TOTAL-65536,TOTAL-1,'zip_tail.bin');i=raw.rfind(b'PK\x05\x06');assert i>=0
    e=struct.unpack_from('<4s4H2LH',raw,i);count,size,offset=e[4],e[5],e[6]
    (out/'directory_metadata.json').write_text(json.dumps({'entries':count,'central_directory_bytes':size,'central_directory_offset':offset,'archive_size':TOTAL,'archive_full_checksum_not_verified':True},indent=2))
    assert count!=65535 and size<=8*1024*1024,'ZIP64 or index>8MiB requires separate review'
    cd=fetch(offset,offset+size-1,'central_directory.bin');entries=[];pos=0
    while pos<len(cd):
        f=struct.unpack_from('<4s6H3L5H2L',cd,pos);assert f[0]==b'PK\x01\x02';name=cd[pos+46:pos+46+f[10]].decode('utf-8' if f[3]&2048 else 'cp437')
        entries.append({'name':name,'flags':f[3],'compression':f[4],'crc32':f[7],'compressed_size':f[8],'uncompressed_size':f[9],'local_header_offset':f[16]});pos+=46+f[10]+f[11]+f[12]
    assert len(entries)==count
    (out/'entries.json').write_text(json.dumps(entries,indent=2));print(json.dumps({'entries':count,'directory_bytes':size,'raw_cage_candidates':[x for x in entries if 'cage2_raw_traces/' in x['name']][:3]}))
if __name__=='__main__':main()
