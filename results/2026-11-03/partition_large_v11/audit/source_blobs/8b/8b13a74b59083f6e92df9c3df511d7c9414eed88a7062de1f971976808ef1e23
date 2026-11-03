"""Provider-independent semantic replay and captured-byte integrity."""
import hashlib, importlib.util, itertools, json, statistics, sys
from pathlib import Path
A=Path(__file__).resolve().parent; R=A.parent
CHECK=R.parent.parent/'2026-11-02/partition_unrestricted_v10/audit/validate_provider_v2.py'
s=importlib.util.spec_from_file_location('independent',CHECK); old=importlib.util.module_from_spec(s); s.loader.exec_module(old)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main(run):
    freeze=json.loads((A/'PERFORMANCE_FREEZE_V1.json').read_text())
    cells={c['case_id']:c for c in json.loads((A/'PERFORMANCE_MANIFEST_V2.json').read_text())['cells']}
    certs={c['case_id']:c for c in json.loads((A/'PERFORMANCE_FAMILY_CERTIFICATES_V3.json').read_text())['certificates']}
    plan=json.loads((run/'plan.json').read_text()); ledger=list(map(json.loads,(run/'ledger.jsonl').read_text().splitlines()))
    assert len(plan)==64 and len(ledger)==64
    errors={}; rows=[]; feasibility={}; refs=0; cert_count=0; integrity=0
    def validate(data,res,cid,method):
        nonlocal refs,cert_count
        alphabet=sorted(data['alphabet']); m=len(alphabet); cert=certs[cid]
        if 'compatible_rgs' in cert:
            family=list(map(tuple,cert['compatible_rgs'])); total=len(family); spectrum=cert['partition_count_by_k']; kmax=max(max(x)+1 for x in family)
            def count(i,j): return sum(x[i]==x[j] for x in family)
        else:
            total=cert['expected_partition_count']; spectrum=cert['expected_partition_count_by_k']; kmax=cert['atom_count']
            owners={x:k for k,g in enumerate(cert['atoms']) for x in g}
            def count(i,j): return total if owners[alphabet[i]]==owners[alphabet[j]] else cert['same_count_across_atoms']
        assert res['complete'] is True and res['alphabet']==alphabet
        assert res['status']==('identified_unique_partition' if total==1 else 'partial_ownership_identification')
        assert res['partition_count']==total and res['partition_count_by_k']==spectrum and res['k_max_compatible']==kmax
        assert res['enumerated_partitions'] is None
        atoms=res['atom_partition']; atomkey=old.partition_rgs(atoms,alphabet)
        assert kmax<=res['k_max_upper_bound']<=len(atoms)<=m
        def feasible(part):
            key=old.partition_rgs(part,alphabet); cachekey=(cid,key)
            if cachekey not in feasibility: feasibility[cachekey]=old.feasible(data,part)
            return feasibility[cachekey]
        assert res['atom_projection_feasible'] is feasible(atoms)
        old.check_witness(data,res['representative']); assert feasible(res['representative']['partition'])
        pairs=res['pair_relations']; assert len(pairs)==m*(m-1)//2
        pairmap={tuple(x['symbols']):x for x in pairs}; assert len(pairmap)==len(pairs)
        for i,j in itertools.combinations(range(m),2):
            row=pairmap[(alphabet[i],alphabet[j])]; same=count(i,j); diff=total-same
            assert row['same_partition_count']==same and row['different_partition_count']==diff
            assert row['relation']==('forced_same' if diff==0 else 'ambiguous')
            for field,want,exists in [('same_partition_witness',True,same>0),('different_partition_witness',False,diff>0)]:
                part=row[field]; assert (part is not None)==exists
                if part is not None:
                    refs+=1; key=old.partition_rgs(part,alphabet); assert feasible(part) and ((key[i]==key[j])==want)
        for edge in res['swap_edge_witnesses']:
            p,n=edge['positive'],edge['negative']; i,j=edge['positions']; pair=edge['symbols']
            assert p in data['positive'] and n in data['negative'] and j==i+1 and 0<=i<j<len(p) and len(p)==len(n)
            chars=list(p); chars[i],chars[j]=chars[j],chars[i]
            assert p[i]!=p[j] and ''.join(chars)==n and pair==[p[i],p[j]]
            assert atomkey[alphabet.index(pair[0])]==atomkey[alphabet.index(pair[1])]; cert_count+=1
        if method=='candidate': assert isinstance(res['binary_interval_must_link_certificates'],list)
        for edge in res.get('binary_interval_must_link_certificates',[]):
            p,n=edge['positive'],edge['negative']; lo,hi=edge['interval']; pair=edge['symbols']
            assert p in data['positive'] and n in data['negative'] and p!=n and len(p)==len(n) and 0<=lo<hi<=len(p)
            assert p[:lo]==n[:lo]==edge['left'] and p[hi:]==n[hi:]==edge['right']
            assert len(set(pair))==2 and set(p[lo:hi])==set(n[lo:hi])==set(pair)
            assert {x:p[lo:hi].count(x) for x in pair}=={x:n[lo:hi].count(x) for x in pair}==edge['counts']
            assert atomkey[alphabet.index(pair[0])]==atomkey[alphabet.index(pair[1])]; cert_count+=1
    for expected,row in zip(plan,ledger):
        key=f"{row['kind']}:{row['method']}:{row['case_id']}:{row['rep']}"
        try:
            assert all(row[k]==v for k,v in expected.items())
            if 'attempt_id' not in row:
                assert row['status']=='budget_censored_before_launch'; rows.append({**expected,'status':row['status']}); continue
            attempt=A/'attempts'/row['attempt_id']; cap=json.loads((attempt/'result.json').read_text()); manifest=json.loads((attempt/'manifest.json').read_text())
            assert cap['child_reaped'] and not cap.get('cleanup_error') and not cap.get('capture_error')
            for stream in ['stdout','stderr']:
                assert sha(attempt/(stream+'.bin'))==cap[stream+'_sha256']; integrity+=1
            source_map={v['path']:v for v in manifest['sources']}
            for p,h in freeze['sources'].items():
                assert sha(Path(p))==h and source_map[p]['sha256']==h
                assert sha(A/source_map[p]['snapshot'])==h; integrity+=1
            out={**expected,'attempt_id':row['attempt_id'],'subprocess_seconds':cap['subprocess_seconds'],'capture_seconds':cap['duration_seconds'],'stdout_bytes':cap['stdout_bytes']}
            if cap['execution_status']=='timed_out': out['status']='timed_out'; rows.append(out); continue
            payload=json.loads((attempt/'stdout.bin').read_bytes())
            if row['kind']=='memory':
                assert cap['execution_status']=='success' and cap['exit_code']==0
                side=Path(row['sidecar']['path']); assert sha(side)==row['sidecar']['sha256']==payload['result_sha256']; integrity+=1
                res=json.loads(side.read_bytes()); out['peak_python_bytes']=payload['tracemalloc_peak_bytes']; assert out['peak_python_bytes']>=payload['tracemalloc_current_bytes']>=0
                assert payload['serialized_default_output_bytes']==side.stat().st_size
                assert payload['input_sha256']==cells[row['case_id']]['input_sha256']
                method_solver=(R/'implementation/unrestricted_solver_v3.py' if row['method']=='candidate' else CHECK.parent.parent/'implementation/unrestricted_solver_v2.py')
                assert payload['solver_sha256']==sha(method_solver)
                out['serialized_output_bytes']=side.stat().st_size
            else: res=payload
            if res.get('complete') is False:
                assert res['status'] in ['unknown','incomplete'] and all(res.get(f) is None for f in ['partition_count','partition_count_by_k','pair_relations','representative','enumerated_partitions'])
                out['status']='cooperative_incomplete'; rows.append(out); continue
            assert cap['exit_code']==0 and cap['execution_status']=='success'
            data=json.loads((A/cells[row['case_id']]['path']).read_text())
            validate(data,res,row['case_id'],row['method']); out['status']='validated_complete'
            out['metrics']=res['metrics']; rows.append(out)
        except Exception as e: errors[key]=repr(e)
    used=json.loads((run/'budget.json').read_text()); assert all(0<=v<=900 for v in used.values())
    comparisons=[]
    for cid in cells:
        entry={'case_id':cid}
        for method in ['baseline','candidate']:
            timing=[r for r in rows if r['case_id']==cid and r['method']==method and r['kind']=='timing']; memory=[r for r in rows if r['case_id']==cid and r['method']==method and r['kind']=='memory']
            valid=[r for r in timing if r['status']=='validated_complete']
            entry[method]={'timing_statuses':[r['status'] for r in timing],'median_cli_seconds':statistics.median(r['subprocess_seconds'] for r in valid) if len(valid)==3 else None,'median_stdout_bytes':statistics.median(r['stdout_bytes'] for r in valid) if len(valid)==3 else None,'memory_status':memory[0]['status'] if memory else 'missing','peak_python_bytes':memory[0].get('peak_python_bytes') if memory and memory[0]['status']=='validated_complete' else None}
        comparisons.append(entry)
    report={'status':'accepted_with_censoring' if not errors and any(r['status']!='validated_complete' for r in rows) else 'accepted' if not errors else 'rejected','errors':errors,'planned_jobs':len(plan),'ledger_jobs':len(ledger),'validated_complete':sum(r['status']=='validated_complete' for r in rows),'censored_jobs':[r for r in rows if r['status']!='validated_complete'],'pair_witness_references':refs,'distinct_partition_feasibility_evaluations':len(feasibility),'certificates_replayed':cert_count,'integrity_checks':integrity,'used_method_capture_seconds':used,'comparisons':comparisons,'rows':rows,'limits':['Whole CLI timings include Python startup, input, preprocessing, witness construction and JSON output.','Peak memory is traced Python allocation from before input read/import through solve and serialization, not RSS.','Memory output sidecar is written after tracing stops.','Performance timings have balanced alternating order; memory probes follow timings.','No speed claim is supported for censored cells.']}
    with (run/'summary.json').open('x',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
    lines=['# گزارش مستقل ممیزی کارایی C011','',f"وضعیت: {report['status']}. تعداد خروجی کامل و تأییدشده: {report['validated_complete']} از ۶۴؛ خطاهای ممیزی: {len(errors)}.",'','زمان‌ها شامل کل فرایند CLI هستند. حافظه به تخصیص‌های قابل ردیابی Python محدود است و RSS نیست. موارد ناتمام حفظ شده‌اند؛ برای آن‌ها ادعای برتری نمی‌شود.','','| ورودی | baseline زمان میانه (ثانیه) | candidate زمان میانه (ثانیه) | baseline حافظه (بایت) | candidate حافظه (بایت) |','|---|---:|---:|---:|---:|']
    for c in comparisons: lines.append(f"| {c['case_id']} | {c['baseline']['median_cli_seconds']} | {c['candidate']['median_cli_seconds']} | {c['baseline']['peak_python_bytes']} | {c['candidate']['peak_python_bytes']} |")
    lines+=['',f"تعداد ارجاع شاهد زوجی بررسی‌شده: {refs}؛ تعداد محاسبه مستقل سازگاری افرازهای متمایز: {len(feasibility)}؛ تعداد گواهی بازپخش‌شده: {cert_count}.",'','هش جریان‌های stdout/stderr، snapshot منابع و ورودی‌ها بررسی شد. ledger و summary.json مسیر هر تلاش و وضعیت سانسور را نگه می‌دارند.','', 'این نمونه‌های ساختاری و محدود، نتیجه‌ای دربارهٔ همهٔ توزیع‌های داده یا حد پیچیدگی کل حل‌گر نمی‌دهند.']
    with (run/'AUDIT_REPORT_FA.md').open('x',encoding='utf-8') as f: f.write('\n'.join(lines)+'\n')
    print(json.dumps({k:report[k] for k in ['status','errors','planned_jobs','validated_complete','integrity_checks']}))
    return 1 if errors else 0
if __name__=='__main__': sys.exit(main(Path(sys.argv[1])))
