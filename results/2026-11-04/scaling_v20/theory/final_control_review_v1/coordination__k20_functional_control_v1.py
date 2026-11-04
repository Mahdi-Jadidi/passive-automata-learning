"""Separate post-benchmark functional control, never a benchmark row."""
from pathlib import Path
import hashlib,json,sys,time
R=Path(__file__).resolve().parents[1]
A=R/"audit"
sys.path.insert(0,str(A))
import capture
from certificate_replay_c015_v2 import canonical,witness
def read(p):return json.loads(Path(p).read_bytes())
def main():
    run=A/"benchmark_runs/20261104T120316.506188Z"
    assert read(run/"validation_report.json")["status"]=="accepted_with_censoring"
    assert read(run/"closure.json")["status"]=="validation_success"
    source=R/"implementation/candidate_c2_v1/gate_v1.py"
    assert hashlib.sha256(source.read_bytes()).hexdigest()=="5331a1787a9ff74afe1afcbea1668dbe9ee69ef1f7121fec14c7281caa2d8680"
    item=next(x for x in read(A/"FIXTURE_MANIFEST_V1.json")["inputs"] if x["case_id"]=="C")
    input_path=Path(item["input"])
    assert hashlib.sha256(input_path.read_bytes()).hexdigest()==item["input_sha256"]
    out=R/"coordination/k20_functional_control_v1"
    out.mkdir(exist_ok=False)
    cli=source.with_name("partition_gate_v1.py")
    command=[sys.executable,"-B","-X","utf8",str(cli),str(input_path),"--known-k","20","--seconds","20"]
    (out/"started.json").write_text(json.dumps({"command":command,"not_benchmark":True}),encoding="utf8")
    cap=capture.capture("c020_k20_functional_control_v1",command,cwd=R,timeout_seconds=25,source_paths=[Path(__file__),source,cli,input_path,R/"coordination/K20_FUNCTIONAL_CONTROL_PLAN_V1.json"])
    assert cap["execution_status"]=="success" and cap["exit_code"]==0 and cap["child_reaped"]
    result=read(A/"attempts"/cap["attempt_id"]/"stdout.bin")
    assert result["status"]=="certified_unique" and result["known_k"]==20 and result["physical_truth_read"] is False
    data=read(input_path)
    cert=result["certificate"]
    assert cert["route"]=="compatible_forced_atoms"
    parent={x:x for x in data["alphabet"]}
    def root(x):
        while x!=parent[x]:x=parent[x]
        return x
    for e in cert["swap_forest"]:
        p,n=data["positive"][e["positive_index"]],data["negative"][e["negative_index"]]
        i,j=e["positions"]
        assert j==i+1 and 0<=i<j<len(p) and p[i]!=p[j]
        assert e["symbols"]==[p[i],p[j]] and n==p[:i]+p[j]+p[i]+p[j+1:]
        a,b=root(p[i]),root(p[j])
        assert a!=b
        parent[b]=a
    groups={}
    for x in sorted(parent):groups.setdefault(root(x),[]).append(x)
    atoms=sorted(groups.values())
    assert len(atoms)==20 and atoms==cert["forced_atoms"]
    key=canonical(atoms,sorted(data["alphabet"]))
    assert result["partition"]==cert["witness"]["blocks"]
    assert witness(data,cert["witness"],[20],{key})==key
    report={"status":"accepted","not_benchmark":True,"no_accuracy_rate_claim":True,"attempt_id":cap["attempt_id"],"input_sha256":item["input_sha256"],"known_k":20,"minimal_states_per_device":1024,"partition":result["partition"],"subprocess_seconds":cap["subprocess_seconds"],"pipeline_seconds":result["input_and_solver_seconds"],"proof":"20 independently replayed forced components and feasible exact witness under trustedK20"}
    (out/"result.json").write_text(json.dumps(report,indent=2),encoding="utf8")
    print(json.dumps({k:v for k,v in report.items() if k!="partition"}))
if __name__=="__main__":main()
