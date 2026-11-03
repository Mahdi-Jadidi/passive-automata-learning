"""Read saved artifacts only; report coverage and limits without refitting winners."""
import collections,csv,hashlib,json,statistics
from pathlib import Path
A=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    mapping=json.loads((A/'GRID_INPUT_MAP_V4.json').read_text());ledger=list(map(json.loads,(A/'grid_inference_ledger_v4.jsonl').read_text().splitlines()));audit=json.loads((A/'GRID_VALIDATION_V3.json').read_text())
    validated={r['attempt_id']:r for r in audit['rows'] if 'attempt_id' in r};rows=[];world_hashes=collections.defaultdict(set);generation=collections.Counter();allnest=True
    for key,entry in mapping['entries'].items():
        k,L=map(int,key.split(':'));d=Path(entry['directory']);data8=json.loads((d/'input8.json').read_text());data2=json.loads((d/'input2.json').read_text());v=json.loads((d/'validation.json').read_text());g=json.loads((d/'generation.json').read_text());world=json.loads((d/'world.json').read_text())
        assert set(data8)==set(data2)=={'alphabet','positive','negative'}
        assert all(data2[label]==data8[label][:2] and set(data2[label])<=set(data8[label]) for label in ['positive','negative'])
        assert sha(d/'input8.json')==entry['input8_sha256'] and sha(d/'input2.json')==entry['input2_sha256'] and sha(d/'world.json')==entry['world_sha256']
        world_hashes[k].add(entry['world_sha256']);generation.update({f:v[f] for f in ['world_generation_seconds','sample_generation_seconds','independent_label_replay_seconds']})
        for n,data in [(2,data2),(8,data8)]:
            lengths=list(map(len,data['positive']+data['negative']));records=[r for r in g['samples'] if r['index']<n]
            attempts=[r for r in ledger if r['kind']=='broad' and r['K']==k and r['max_length']==L and r['samples_per_label']==n]
            assert len(attempts)==3 and len({r['rep'] for r in attempts})==3
            states=[];timings=[];totals=[];sizes=[];metrics=[]
            for r in attempts:
                state=r['status']
                if 'attempt_id' in r:
                    cap=json.loads((A/'attempts'/r['attempt_id']/'result.json').read_text());rcheck=validated.get(r['attempt_id']);state=rcheck['status'] if rcheck else 'validation_not_completed'
                    if rcheck and 'total' in rcheck:
                        timings.append(cap['subprocess_seconds']);totals.append(rcheck['total']);sizes.append(cap['stdout_bytes'])
                        result=json.loads((A/'attempts'/r['attempt_id']/'stdout.bin').read_bytes());metrics.append(result['metrics'])
                states.append(state)
            if totals:assert len(set(totals))==1
            T=sum(lengths);median=statistics.median(timings) if len(timings)==3 else None
            rows.append({'K':k,'max_length':L,'samples_per_label':n,'world_sha256':entry['world_sha256'],'input_sha256':entry[f'input{n}_sha256'],'T':T,'actual_lengths':lengths,'actual_min_length':min(lengths),'actual_max_length':max(lengths),'actual_mean_length':statistics.mean(lengths),'total_runs':sum(r['run_count'] for r in records),'observed_alphabet':sorted(set(''.join(data['positive']+data['negative']))),'states':states,'completed_repetitions':len(timings),'individual_complete_cli_seconds':timings,'median_three_complete_cli_seconds':median,'seconds_per_actual_input_character':median/T if median is not None and T else None,'exact_count_reported_by_C010':totals[0] if totals else None,'large_full_family_independently_proved':False,'stdout_bytes_complete_calls':sizes,'dp_states_complete_calls':[m['dp_states'] for m in metrics],'repair_lengths':[r['repair_length'] for r in records]})
    assert len(rows)==240 and all(len(h)==1 for h in world_hashes.values())
    rows.sort(key=lambda r:(r['max_length'],r['samples_per_label'],r['K']))
    coverage=collections.Counter(state for r in rows for state in r['states']);firstpass=sum('attempt_id' in r for r in ledger if r['kind']=='broad' and r['rep']==1)
    confirmations=[r for r in ledger if r['kind']=='confirmation']
    receipts=[json.loads(p.read_text()) for p in A.glob('*_active_budget_v2.json')]
    result={'status':'closed_after_bounded_grid','independent_validation_status':audit['status'],'validation_errors':audit['errors'],'validation_budget_censored':audit.get('validation_budget_censored',[]),'solver_cells':240,'first_pass_attempted':firstpass,'broad_slots':720,'broad_status_counts':dict(coverage),'cells_three_complete_repetitions':sum(r['completed_repetitions']==3 for r in rows),'all_240_nested_sample_derivations_verified':allnest,'all_worlds_same_across_cap_and_count':True,'unique_worlds':20,'preparation_components_seconds':dict(generation),'active_phase_receipts':receipts,'optional_confirmation_ledger_rows':confirmations,'cells':rows,'raw_validation_report_sha256':sha(A/'GRID_VALIDATION_V3.json'),'inference_ledger_sha256':sha(A/'grid_inference_ledger_v4.jsonl'),'input_map_sha256':sha(A/'GRID_INPUT_MAP_V4.json'),'evidence_limits':['Saved truth compatibility and witness replay do not constitute a full-family oracle on alphabet40.','No-K trueK>1 necessarily permits coarsenings; ambiguity is not a classification error.','All timing curves fix K/world/count/profile and use actual input characters T; nominal max length is only a cap.','No global/asymptotic slope is fitted to completed winners.','The initial preparation720s ceiling censored K12/L1m; successful V3 cells were reused and only outstanding cases resumed under resource GO.','Initial control validator order bug and all diagnostics/rejections remain preserved.']}
    with (A/'GRID_SUMMARY_V4.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    fields=['K','max_length','samples_per_label','T','actual_min_length','actual_max_length','actual_mean_length','total_runs','completed_repetitions','median_three_complete_cli_seconds','seconds_per_actual_input_character','exact_count_reported_by_C010','states']
    with (A/'GRID_TIMINGS_V4.csv').open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in rows)
    lines=['# ممیزی مستقل C013: جهان‌های DFA تصادفی با K پنهان','',f"۲۴۰ ورودی معتبر ساخته و بازپخش شدند؛ {firstpass} سلول تلاش نخست inference را دریافت کردند. وضعیت ممیزی: {audit['status']}. موارد خطا/ناتمامی اعتبارسنجی در JSON محفوظ‌اند.",'','فقط مرجع دقیق C010 و مدل no-K اجرا شدند. K فیزیکی، جدول انتقال‌ها و مالکیت نمادها در ورودی حل‌گر قرار نگرفتند. داده‌ها حاصل جهان‌های شرطیِ قویاً همبند و نمونه‌های اصلاح‌شده با BFS هستند؛ توزیع یکنواخت همهٔ DFAها یا همهٔ تریس‌ها ادعا نمی‌شود.','','| سقف طول | تعداد نمونهٔ هر برچسب | سلول‌های دارای سه پاسخ کامل | تعداد پاسخ کامل در همهٔ تکرارها |','|---:|---:|---:|---:|']
    for L in [8,64,512,4096,65536,1000000]:
        for n in [2,8]:
            group=[r for r in rows if r['max_length']==L and r['samples_per_label']==n]
            lines.append(f"| {L} | {n} | {sum(r['completed_repetitions']==3 for r in group)}/20 | {sum(r['completed_repetitions'] for r in group)}/60 |")
    lines+=['',f"وضعیت ۷۲۰ جایگاه تکرار: {dict(coverage)}.",'','جدول کامل ۲۴۰ سلول در GRID_TIMINGS_V4.csv و JSON است. محور اندازه، مجموع واقعی نویسه‌های ورودی T است؛ طول واقعی، تعداد ران و طول اصلاح نیز ثبت شده‌اند. میانهٔ سه‌تکراری تنها برای سه اجرای کامل گزارش شده؛ timeout و جایگاه شروع‌نشده حذف یا جایگزین نشده‌اند. هزینهٔ تولید نمونه و ارزیابی مستقل برچسب جدا از زمان کامل CLI ثبت شده است.','','در مدل no-K، ادغام مؤلفه‌های واقعی همچنان سازگار است؛ برای K واقعی بزرگ‌تر از یک، ابهام انتظار نظری است. سازگاری حقیقت ذخیره‌شده با داده به معنای بازیابی یکتای مالکیت نیست. شاهدها و روابط اجباری با داده و مالکیت واقعی بررسی شده‌اند، اما صحت کل شمارش خانواده در الفبای۴۰ فقط از این بازپخش نتیجه نمی‌شود. کنترل‌های الفبای حداکثر۸ با کل خانوادهٔ مستقل RGS مقایسه شدند.','','توقف آماده‌سازی V3 در سقف۷۲۰ثانیه، نمونهٔ ناقص K12/L1m و ادامهٔ منابع V4 همگی حفظ شده‌اند. فقط موارد باقی‌مانده در مسیرهای تازه ساخته شدند؛ هیچ موفقیت قبلی بازتولید نشد. خطای اولیهٔ validator در ترتیب شاهدها نیز با نسخهٔ اصلاح‌شده و بدون تکرار provider رفع و مستند شد.','','از این شبکهٔ محدود و نتایج سانسورشده، مرتبهٔ مجانبی عمومی یا بازیابی دستگاه‌های فیزیکی استنتاج نمی‌شود.']
    with (A/'AUDIT_REPORT_FA_V4.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    print(json.dumps({'status':result['independent_validation_status'],'first_pass_attempted':firstpass,'broad_status_counts':dict(coverage),'three_complete_cells':result['cells_three_complete_repetitions']}))
if __name__=='__main__':main()
