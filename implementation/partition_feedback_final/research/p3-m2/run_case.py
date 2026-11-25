"""Run actual pinned raw fixtures, record bytes and independent replay separately."""
import argparse
import hashlib
import json
from pathlib import Path
import os
import resource
import shutil
import subprocess
import sys
import time

EXPECTED={
    "tiny_choice":"1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23",
    "small_choice":"10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b",
}


def pins(path):
    size=path.stat().st_size
    s=hashlib.sha256()
    g=hashlib.sha1(("blob "+str(size)+"\\0").encode().replace(b"\\0",b"\0"))
    with path.open("rb") as f:
        while True:
            b=f.read(1024*1024)
            if not b: break
            s.update(b);g.update(b)
    return dict(bytes=size,sha256=s.hexdigest(),git_blob_calculated=g.hexdigest())


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--case",choices=EXPECTED,required=True)
    p.add_argument("--mode",choices=["one","all"],required=True)
    p.add_argument("--proof-root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--seconds",type=int,default=240)
    p.add_argument("--memory-mib",type=int,default=5120)
    p.add_argument("--entries",type=int,default=4000000)
    a=p.parse_args()
    out=a.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    here=Path(__file__).resolve().parent
    raw=out/"raw.json"
    shutil.copyfile(here/"inputs"/(a.case+".json"),raw)
    if pins(raw)["sha256"]!=EXPECTED[a.case]: raise RuntimeError("raw hash mismatch")
    ref=(a.proof_root/"tests/reference").resolve()
    sys.path.insert(0,str(ref))
    from independent_replay import sample_data
    from p3_frontier_verifier import canonical
    journal=out/"journal.json"
    journal.write_bytes(canonical(dict(version="selector-v2-journal/2",
                        sample_digest=sample_data(json.loads(raw.read_bytes()))[3],events=[])))
    scope=out/"trusted.json"
    verifier=str(ref/"p3_frontier_verifier.py")
    base=[sys.executable,"-B"]
    sc_args=["--raw",str(raw),"--journal",str(journal)]
    env=dict(os.environ,PYTHONPATH=str(here.parent.parent)+os.pathsep+str(ref))
    stats={}
    def limit():
        limit=a.memory_mib*1024*1024
        resource.setrlimit(resource.RLIMIT_AS,(limit,limit))
    def run(name,argv,wall):
        logfile=out/(name+".log")
        t=time.monotonic()
        with logfile.open("wb") as f:
            try:
                proc=subprocess.run(["/usr/bin/time","-v",*argv],stdout=f,stderr=subprocess.STDOUT,
                                    env=env,timeout=wall,preexec_fn=limit)
                code=proc.returncode
            except subprocess.TimeoutExpired:
                code=124
        stats[name]=dict(command=argv,exit=code,elapsed=time.monotonic()-t,log=pins(logfile))
        print(name,stats[name],flush=True)
        return code
    if run("trusted",base+[verifier,"--make-trusted-scope",*sc_args,"--out",str(scope)],60)!=0:
        raise RuntimeError("trusted scope builder failed")
    def producer(name,optimized=False,entries=None,resume=None):
        cert=out/(name+".json")
        cmd=base+(["-O"] if optimized else [])+["-m","selector_v2.edr_search",
             "--raw",str(raw),"--scope",str(scope),"--mode",a.mode,"--out",str(cert),
             "--metrics",str(out/(name+".metrics.json")),"--seconds",str(a.seconds),
             "--entries",str(a.entries if entries is None else entries)]
        if resume: cmd += ["--resume",str(resume)]
        run(name,cmd,a.seconds+180)
        if cert.exists(): stats[name]["certificate"]=pins(cert)
        return cert
    def verify(name,cert,optimized=False):
        if not cert.exists(): return None
        cmd=base+(["-O"] if optimized else [])+[verifier,*sc_args,"--scope",str(scope),
            "--proof",str(cert),"--seconds",str(a.seconds),"--max-nodes",str(a.entries+1),
            "--max-entries",str(a.entries+1),"--max-proof-bytes",str(2*1024**3),
            "--max-work","4000000000","--max-exact-checks","200000000"]
        return run(name,cmd,a.seconds+90)
    first=producer("normal")
    first_hash=pins(first)["sha256"] if first.exists() else None
    normal_status=verify("normal.verify",first)
    repeat=producer("optimized",True)
    optimized_status=verify("optimized.verify",repeat,True)
    same=first_hash is not None and repeat.exists() and pins(repeat)["sha256"]==first_hash
    # Do not retain duplicate huge certificates, but record exact pins first.
    if same: repeat.unlink()
    part=producer("partial",entries=1)
    partial_status=verify("partial.verify",part)
    resumed=producer("resumed",resume=part) if part.exists() else out/"resumed.json"
    resume_same=first_hash is not None and resumed.exists() and pins(resumed)["sha256"]==first_hash
    if resume_same: resumed.unlink()
    ok=(normal_status==0 and optimized_status==0 and partial_status==2 and same and resume_same)
    summary=dict(case=a.case,mode=a.mode,raw=pins(raw),journal=pins(journal),trusted_scope=pins(scope),
                 phases=stats,normal_optimized_equal=same,checkpoint_resume_equal=resume_same,
                 structural_gate="PASS" if ok else "NOT_ACCEPTED",operational_status="INCOMPLETE")
    (out/"summary.json").write_bytes(canonical(summary))
    print("M2_CASE_SUMMARY",canonical(summary).decode(),flush=True)
    return 0 if ok else 1


if __name__=="__main__":
    raise SystemExit(main())
