"""Separate single-trial Windows process-peak measurements (not allocations)."""
from pathlib import Path
import ctypes,json,subprocess,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def peak():
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(name,ctypes.c_size_t) for name in ['peak','working','qpp','qp','qpnp','qnp','page','peakpage']]
    values=Counters();values.cb=ctypes.sizeof(values)
    api=ctypes.windll.psapi.GetProcessMemoryInfo;api.argtypes=[ctypes.c_void_p,ctypes.POINTER(Counters),ctypes.c_ulong]
    process=ctypes.windll.kernel32.GetCurrentProcess;process.restype=ctypes.c_void_p
    if not api(process(),ctypes.byref(values),values.cb):raise ctypes.WinError()
    return values.peak

def main():
    if len(sys.argv)>1:
        method=sys.argv[1];D=json.loads(sys.argv[2])
        sys.path.insert(0,str(HERE if method=='v45' else HERE.parent/'exact_optimizer_v43'))
        from optimizer import solve_optimal
        from verify import verify_optimal
        result=solve_optimal(D,{'timeout_seconds':1})
        checked=verify_optimal(D,result,{'timeout_seconds':1}) if result['status'] in ('OPTIMAL','INFEASIBLE') else None
        print(json.dumps({'method':method,'status':result['status'],'checked':checked,'peak_working_set_bytes':peak(),'limit_seconds':1}))
        return
    cases=[json.loads(line) for line in (ROOT/'results/2026-11-13/exact_candidates_v33/audit/timing_cases.jsonl').read_text().splitlines()]
    with (HERE/'memory_raw.jsonl').open('x',encoding='utf-8') as out:
        for case in cases:
            for method in ('v43','v45'):
                run=subprocess.run([sys.executable,str(Path(__file__).resolve()),method,json.dumps(case['input'])],capture_output=True,text=True,timeout=12,check=True)
                row=json.loads(run.stdout);row['case']=case.get('name',case.get('case'));row['repetitions']=1
                out.write(json.dumps(row)+'\n');out.flush()
    print('20 separate process-peak records saved')
if __name__=='__main__':main()
