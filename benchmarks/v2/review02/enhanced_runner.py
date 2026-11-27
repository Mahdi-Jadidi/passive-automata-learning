"""Invoke unchanged archived enhanced baseline using the existing harness wrapper."""
import hashlib, sys
from pathlib import Path
import harness
ARCHIVE_SHA='595f928ef085f8decc9533404eeb3a8b458ff4e82e527e80d889c20fa55946ca'
from zipfile import ZipFile
archive=Path(__file__).resolve().parent.parent/'recovered/partition-scale-improved.zip'
if hashlib.sha256(archive.read_bytes()).hexdigest()!=ARCHIVE_SHA: raise ValueError('archive mismatch')
with ZipFile(archive) as z:
    harness.LEGACY_BLOBS={n:hashlib.sha1(b'blob '+str(len(z.read(n))).encode()+b'\0'+z.read(n)).hexdigest() for n in harness.LEGACY_BLOBS}
harness.PIN='enhanced-archive-sha256:'+ARCHIVE_SHA
harness.__file__=__file__
import argparse
p=argparse.ArgumentParser(); p.add_argument('input',type=Path); p.add_argument('output',type=Path); p.add_argument('--engine',default='legacy'); p.add_argument('--repo',type=Path,required=True); p.add_argument('--legacy-mode',default='hybrid'); p.add_argument('--verified-snapshot',action='store_true'); p.add_argument('--seconds',type=float,default=5); p.add_argument('--memory',type=int,default=512); p.add_argument('--stage'); p.add_argument('--proof',type=Path); p.add_argument('--events',type=Path)
a=p.parse_args(); harness.worker(a) if a.stage else harness.run(a)
