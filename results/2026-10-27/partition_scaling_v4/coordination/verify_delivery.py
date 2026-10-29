"""Byte-integrity checks of frozen references and captured evidence; no solvers."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import shutil
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parents[2]
RUN = ROOT/'coordination/integrity_runs'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'_'+uuid4().hex[:8])
RUN.mkdir(parents=True,exist_ok=False)
shutil.copyfile(__file__,RUN/'verify_delivery.py')
checks,errors=[],[]


def digest(path):
    h=sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def check(path,wanted,kind):
    actual=digest(path) if path.is_file() else None
    checks.append(dict(path=str(path),kind=kind,expected=wanted,actual=actual,matches=actual==wanted))


try:
    parent=read(ROOT/'coordination/parent_manifest.json')
    for item in parent['files']:
        check(WORKSPACE/item['path'],item['sha256'],'immutable_parent')
    for name in ['runtime_stage1.json','STAGE2_GO.json','runtime_stage2_r2.json','runtime_final.json']:
        path=ROOT/'coordination'/name
        if path.exists():
            for item in read(path)['files']:
                check(ROOT/item['path'],item['sha256'],name)
    for path in (ROOT/'audit/corpora').rglob('*freeze*.json'):
        data=read(path)
        for item in data.get('files',[]):
            if isinstance(item,dict) and 'path' in item and 'sha256' in item:
                check(path.parent/item['path'],item['sha256'],'corpus_freeze')
    for path in ROOT.rglob('*'):
        if not path.is_file():
            continue
        if 'source_blobs' in path.parts and len(path.name)==64:
            check(path,path.name,'captured_content_addressed_source')
        if path.name=='result.json':
            data=read(path)
            for stream in ['stdout','stderr']:
                if stream+'_sha256' in data:
                    check(path.parent/(stream+'.bin'),data[stream+'_sha256'],'captured_raw_stream')
except Exception as error:
    errors.append(repr(error))
failed=[x for x in checks if not x['matches']]
report=dict(at_utc=datetime.now(timezone.utc).isoformat(),run_id=RUN.name,
    command=[sys.executable,'-B','-X','utf8',*sys.argv],cwd=str(Path.cwd()),
    python=sys.version,platform=platform.platform(),script_sha256=digest(Path(__file__)),
    checks=checks,check_count=len(checks),failure_count=len(failed),errors=errors,
    all_match=not failed and not errors,scientific_status='byte_integrity_only_not_a_proof')
(RUN/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(run_dir=str(RUN),checks=len(checks),failures=len(failed),errors=errors,all_match=report['all_match'])))
raise SystemExit(0 if report['all_match'] else 1)
