#!/usr/bin/env python3
"""Read-only C005 archive audit; writes only a unique checker snapshot and report."""
from __future__ import annotations
import argparse, hashlib, json, shutil
from pathlib import Path
from datetime import datetime, timezone

def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('output', help='new JSON report filename relative to delivery/ or absolute')
    a=ap.parse_args(); here=Path(__file__).resolve().parent; cycle=here.parent; root=cycle.parents[2]
    out=Path(a.output); out=out if out.is_absolute() else here/out
    if out.exists(): ap.error(f'refusing to overwrite: {out}')
    errors=[]; counts={'parent_manifest_files':0,'readiness_files':0,'readiness_runtime_hashes':0,
        'attempts':0,'raw_capture_files':0,'completion_records':0,'source_refs':0,'source_blobs':0}
    def check(p:Path,digest:str,label:str,byte_count=None):
        if not p.is_file(): errors.append(f'{label}: missing {p}'); return
        if sha(p).lower()!=str(digest).lower(): errors.append(f'{label}: sha256 mismatch {p}')
        if byte_count is not None and p.stat().st_size!=int(byte_count): errors.append(f'{label}: byte count mismatch {p}')
    pm=cycle/'coordination'/'parent_manifest.json'
    if pm.is_file():
        for e in json.loads(pm.read_text(encoding='utf-8')).get('files',[]):
            counts['parent_manifest_files']+=1; check(root/e['path'],e.get('sha256',''),'parent manifest',e.get('bytes'))
    else: errors.append(f'missing parent manifest: {pm}')
    for p in cycle.rglob('READINESS*.json'):
        counts['readiness_files']+=1
        try: d=json.loads(p.read_text(encoding='utf-8'))
        except Exception as ex: errors.append(f'invalid readiness JSON {p}: {ex}'); continue
        for key in ('artifact','provider'):
            if d.get(key) and d.get('sha256'):
                counts['readiness_runtime_hashes']+=1; check(cycle/d[key],d['sha256'],'readiness runtime')
        deps=d.get('dependencies',[])
        if isinstance(deps,dict): deps=[{'path':k,'sha256':v} for k,v in deps.items()]
        for dep in deps if isinstance(deps,list) else []:
            if isinstance(dep,dict) and dep.get('path') and dep.get('sha256'):
                counts['readiness_runtime_hashes']+=1; check(cycle/dep['path'],dep['sha256'],'readiness dependency')
    blobs=cycle/'evidence'/'source_blobs'
    for b in blobs.rglob('*') if blobs.exists() else []:
        if b.is_file():
            counts['source_blobs']+=1
            if len(b.name)!=64 or sha(b)!=b.name: errors.append(f'content-addressed blob mismatch: {b}')
            elif b.parent.name!=b.name[:2]: errors.append(f'blob shard mismatch: {b}')
    attempts=cycle/'evidence'/'attempts'
    for d in sorted(p for p in attempts.iterdir() if p.is_dir()) if attempts.exists() else []:
        counts['attempts']+=1; mp=d/'manifest.json'; rp=d/'result.json'
        if not mp.is_file(): errors.append(f'missing attempt manifest: {mp}'); continue
        try: m=json.loads(mp.read_text(encoding='utf-8'))
        except Exception as ex: errors.append(f'invalid manifest {mp}: {ex}'); continue
        for s in m.get('sources',[]):
            counts['source_refs']+=1; rel=s.get('snapshot'); digest=s.get('sha256'); size=s.get('bytes')
            if not rel or not digest: errors.append(f'incomplete source reference in {mp}'); continue
            snap=(cycle/'evidence'/rel).resolve()
            if cycle.resolve() not in snap.parents: errors.append(f'source snapshot escapes cycle: {snap}')
            else: check(snap,digest,'attempt source snapshot',size)
        if not rp.is_file(): errors.append(f'missing completion result record: {rp}'); continue
        counts['completion_records']+=1
        try: r=json.loads(rp.read_text(encoding='utf-8'))
        except Exception as ex: errors.append(f'invalid result record {rp}: {ex}'); continue
        for stream in ('stdout','stderr'):
            raw=d/(stream+'.bin'); counts['raw_capture_files']+=1
            if not raw.is_file(): errors.append(f'missing raw capture: {raw}'); continue
            expected=r.get(stream+'_sha256'); n=r.get(stream+'_bytes')
            if not expected: errors.append(f'missing {stream}_sha256 in {rp}')
            else: check(raw,expected,f'{stream} capture',n)
        if 'exit_code' not in r: errors.append(f'missing exit_code completion field: {rp}')
    # Snapshot this exact checker before creating the output report.
    source=Path(__file__).resolve(); selfhash=sha(source); snapdir=here/'.checker_snapshots'; snapdir.mkdir(exist_ok=True)
    snap=snapdir/(out.stem+'_'+selfhash+'.py')
    if snap.exists(): errors.append(f'checker snapshot already exists (non-unique run): {snap}')
    else:
        shutil.copyfile(source,snap)
        if sha(snap)!=selfhash: errors.append(f'checker snapshot verification failed: {snap}')
    report={'schema_version':1,'created_utc':datetime.now(timezone.utc).isoformat(),
      'checker':{'path':str(source.relative_to(cycle)),'sha256':selfhash,'snapshot':str(snap.relative_to(cycle))},
      'cycle':str(cycle),'counts':counts,'error_count':len(errors),'errors':errors,
      'status':'pass' if not errors else 'fail','scope_note':'Archive integrity only; no solver tests or performance runs.'}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8',newline='\n') as f: json.dump(report,f,ensure_ascii=False,indent=2); f.write('\n')
    print(json.dumps({'status':report['status'],'counts':counts,'error_count':len(errors),'report':str(out)},ensure_ascii=False))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
