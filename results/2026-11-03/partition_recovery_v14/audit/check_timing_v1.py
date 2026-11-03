import hashlib,itertools,json,statistics,sys,time
from pathlib import Path
import check_results_v1 as checker
import routing_witness_v1 as routing
A=Path(__file__).resolve().parent
def main():
    run=Path(sys.argv[1]);manifest=json.loads((A/'DATA_MANIFEST_V1.json').read_text());cases={c['case_id']:c for c in manifest['timing_cases']};oracles={c['case_id']:c for c in json.loads((A/'HELD_ORACLES_V1.json').read_text())['cases']};errors={};results=[];routing.deadline=time.perf_counter()+75
    for row in map(json.loads,(run/'ledger.jsonl').read_text().splitlines()):
        if row['kind']!='timing':continue
        out={**row}
        if 'attempt_id' not in row:
            assert row['status']=='budget_unstarted';results.append(out);continue
        try:
            p=A/'attempts'/row['attempt_id'];cap=json.loads((p/'result.json').read_text());assert cap['child_reaped'] and not cap.get('cleanup_error')
            for stream in ['stdout','stderr']:assert hashlib.sha256((p/(stream+'.bin')).read_bytes()).hexdigest()==cap[stream+'_sha256']
            manifest_capture=json.loads((p/'manifest.json').read_text())
            for source in manifest_capture['sources']:assert hashlib.sha256((A/source['snapshot']).read_bytes()).hexdigest()==source['sha256']
            out.update(cli_seconds=cap['subprocess_seconds'],output_bytes=cap['stdout_bytes'])
            if cap['execution_status']=='timed_out':out['status']='hard_timeout';results.append(out);continue
            r=json.loads((p/'stdout.bin').read_bytes())
            if not r.get('complete'):
                assert r['status'] in ['incomplete','unknown'] and r.get('partition_count') is None and r.get('partition_count_by_k') is None and r.get('pair_relations') is None
                out['status']='cooperative_incomplete';results.append(out);continue
            assert cap['exit_code']==0 and cap['execution_status']=='success'
            data=json.loads(Path(cases[row['case_id']]['path']).read_text());o=oracles[row['case_id']];assert o['exact_count_oracle']
            pairs=[{'symbols':[a,b],'same':o['same_pair_count'],'different':o['partition_count']-o['same_pair_count']} for a,b in itertools.combinations(o['alphabet'],2)];expected={**o,'pairs':pairs}
            if row['method']=='new':checker.compact(data,r,expected)
            else:
                assert r['partition_count']==o['partition_count'] and r['partition_count_by_k']==o['partition_count_by_k'] and r['k_max_compatible']==len(o['alphabet'])
                routing.evaluate({'alphabet':data['alphabet'],'positive':sorted(set(data['positive'])),'negative':sorted(set(data['negative']))},r['representative']['partition'],r['representative'])
                rows={tuple(x['symbols']):x for x in r['pair_relations']};assert len(rows)==len(pairs);cache={}
                for pair in pairs:
                    x=rows[tuple(pair['symbols'])];assert x['relation']=='ambiguous' and x['same_partition_count']==pair['same'] and x['different_partition_count']==pair['different']
                    i,j=map(o['alphabet'].index,pair['symbols'])
                    for f,want in [('same_partition_witness',True),('different_partition_witness',False)]:
                        part=x[f];key=checker.old.partition_rgs(part,o['alphabet'])
                        if key not in cache:cache[key]=routing.evaluate(data,part)
                        assert cache[key] and ((key[i]==key[j])==want)
            out.update(status='validated_complete',metrics=r['metrics']);results.append(out)
        except Exception as e:errors[str(row)]=repr(e)
    assert len(results)+len(errors)==24
    comparisons=[]
    for cid in cases:
        for method in ['baseline','new']:
            group=[r for r in results if r['case_id']==cid and r['method']==method];complete=[r for r in group if r['status']=='validated_complete']
            comparisons.append({'case_id':cid,'method':method,'statuses':[r['status'] for r in group],'median_three_complete_cli_seconds':statistics.median(r['cli_seconds'] for r in complete) if len(complete)==3 else None,'complete_output_bytes':[r['output_bytes'] for r in complete]})
    report={'status':'accepted_with_censoring' if not errors else 'rejected','errors':errors,'comparisons':comparisons,'rows':results,'output_contract_caveat':'C010 expands projection payloads; new unary branch uses compact witness IDs. Whole-CLI comparisons include this output difference, not equal-I/O speedups.','ownership_caveat':'All-partitions shortcut proves sample ambiguity, not physical recovery.'}
    with (run/'timing_report.json').open('x') as f:json.dump(report,f,indent=2)
    lines=['# ممیزی C014','',f"وضعیت زمان‌گیری: {report['status']}؛ خطاها: {len(errors)}.",'','خروجی C010 شامل تصاویر و شاهدهای بازشده است؛ روش جدید در شاخهٔ سریع گواهی فشرده می‌دهد. نسبت زمان کل CLI، برتری با هزینهٔ ورودی/خروجی یکسان نیست. حالت پیش‌فرض no-K است و شاخهٔ همهٔ افرازها به معنای بازیابی مالکیت فیزیکی نیست.','','| ورودی | روش | وضعیت سه تکرار | میانهٔ سه اجرای کامل |','|---|---|---|---:|']
    for c in comparisons:lines.append(f"| {c['case_id']} | {c['method']} | {c['statuses']} | {c['median_three_complete_cli_seconds']} |")
    lines+=['','صحت و بازیابی گراف در correctness_report.json ثبت شده‌اند. پرس‌وجوهای کالیبراسیون دسترسی اضافی به برچسب جهان مصنوعی هستند؛ یادگیری passive روی دادهٔ اصلی نامیده نمی‌شوند. نبود پوشش یا رفتار جابه‌جاپذیر، گواهی گراف را محدود می‌کند؛ نبود یال اثبات استقلال نیست.','']
    with (run/'AUDIT_REPORT_FA.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines))
    print(json.dumps({'status':report['status'],'errors':errors}));return 0 if not errors else 1
if __name__=='__main__':raise SystemExit(main())
