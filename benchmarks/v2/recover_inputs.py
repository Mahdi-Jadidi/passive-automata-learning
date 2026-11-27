"""Recover authorized original archives into input-only and reference-only trees."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from harness import LEGACY_BLOBS, pinned_source

ARCHIVES = {
    'partition-planted-benchmark.zip': '5d2dae2ca718cc65d48e5fbcb62480baeae0da35d37edb9184ba2b61d91e1dc4',
    'partition-scale-handoff-a3a4afba.zip': '79791dea6e84370ef852709edd6680bb8d371299f2a84bea58e0d4ad4efc6541',
    'partition-scale-improved.zip': '595f928ef085f8decc9533404eeb3a8b458ff4e82e527e80d889c20fa55946ca',
}
BUNDLES = {'hdfs_1024':'d34d4dd85b751d716fcabc5a66a1150a6784770d',
           'hdfs_holdout_1024_uncapped':'13af0aef0bd603a287f5246f2dbe1170b6862895',
           'cover_path_8':'6d273e2e7874a4470bf1f0f5874c44cfd1dc3d25'}
SCALE_BLOB = '33b1210e495db29b22333053fe5ad077e345b8e1'


def sha(b): return hashlib.sha256(b).hexdigest()


def exact(b, expected):
    for candidate in (b, b.replace(b'\r\n', b'\n')):
        if hashlib.sha1(b'blob '+str(len(candidate)).encode()+b'\0'+candidate).hexdigest()==expected:
            return candidate
    raise ValueError('no exact committed blob match: '+expected)


def recover(source, output):
    for name, digest in ARCHIVES.items():
        if sha((source/name).read_bytes()) != digest:
            raise ValueError('archive checksum mismatch: '+name)
    output.mkdir(parents=True,exist_ok=False)
    for name in ('legacy','pinned-inputs','pinned-refs','planted-inputs','planted-refs'):
        (output/name).mkdir()
    with ZipFile(source/'partition-scale-handoff-a3a4afba.zip') as z:
        for name,digest in LEGACY_BLOBS.items():
            (output/'legacy'/name).write_bytes(exact(z.read(name),digest))
        pinned_source(output/'legacy',True)
        for name,digest in BUNDLES.items():
            b=exact(z.read('evidence/'+name+'.json'),digest)
            d=json.loads(b); x=d.pop('input')
            if set(x)!={'alphabet','positive','negative'}: raise ValueError('bad input schema')
            (output/'pinned-inputs'/(name+'.json')).write_text(json.dumps(x,separators=(',',':'))+'\n')
            (output/'pinned-refs'/(name+'.json')).write_text(json.dumps(d)+'\n')
        (output/'pinned-inputs'/'scale-1000-original.json').write_bytes(exact(z.read('evidence/synthetic_10000_traces_1000_symbols.json'),SCALE_BLOB))
    rows=[]
    with ZipFile(source/'partition-planted-benchmark.zip') as z:
        for member in sorted(z.namelist()):
            if not member.endswith('/input.json'): continue
            b=z.read(member); refmember=member.removesuffix('input.json')+'reference.json'; ref=z.read(refmember)
            d=json.loads(b); name=member.split('/')[-2]
            if set(d)!={'alphabet','positive','negative'}: raise ValueError('bad input schema')
            for dir_,raw in [('planted-inputs',b),('planted-refs',ref)]:
                p=output/dir_/(name+'.json')
                if p.exists() and p.read_bytes()!=raw: raise ValueError('different duplicate: '+name)
                p.write_bytes(raw)
            rows.append([member,sha(b),refmember,sha(ref),len(d['alphabet']),len(d['positive']),len(d['negative'])])
    with (output/'planted-manifest.csv').open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['input_member','input_sha256','reference_member','reference_sha256','alphabet','positives','negatives']); w.writerows(rows)
    print(json.dumps({'records':len(rows),'unique_input_bytes':len({r[1] for r in rows}),'manifest_sha256':sha((output/'planted-manifest.csv').read_bytes())}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('archives',type=Path); p.add_argument('output',type=Path); a=p.parse_args(); recover(a.archives,a.output)
