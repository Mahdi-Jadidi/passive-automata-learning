import hashlib,json
from pathlib import Path
A=Path(__file__).resolve().parent
RUN=A/'performance_runs_v2/20261103T080554.862063Z'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    s=json.loads((RUN/'summary.json').read_text()); assert s['status']=='accepted_with_censoring' and not s['errors']
    cells=json.loads((A/'PERFORMANCE_MANIFEST_V2.json').read_text())['cells']; previous={}; comparisons=[]
    for cell,c in zip(cells,s['comparisons']):
        assert cell['case_id']==c['case_id']; out={**cell,'methods':{}}
        for method in ['baseline','candidate']:
            v=c[method]; t=v['median_cli_seconds']; old=previous.get((cell['family'],method))
            out['methods'][method]={**v,'seconds_per_input_character':t/cell['total_characters'] if t is not None else None,'relative_to_previous_length':{'length_ratio':cell['length']/old[0],'time_ratio':t/old[1]} if old and t is not None else None}
            if t is not None:previous[(cell['family'],method)]=(cell['length'],t)
        out['baseline_over_candidate_cli_ratio']=c['baseline']['median_cli_seconds']/c['candidate']['median_cli_seconds']; comparisons.append(out)
    result={'status':s['status'],'timing_complete':36,'memory_complete':1,'memory_censored':3,'errors':s['errors'],'comparisons':comparisons,'capture_integrity_checks':s['integrity_checks'],'pair_witness_references':s['pair_witness_references'],'distinct_partition_feasibility_evaluations':s['distinct_partition_feasibility_evaluations'],'certificates_replayed':s['certificates_replayed'],'method_capture_seconds':s['used_method_capture_seconds'],'anchors':{str(p.relative_to(A)):sha(p) for p in [RUN/'summary.json',RUN/'ledger.jsonl',RUN/'plan.json',RUN/'validation_capture.json',A/'PERFORMANCE_FREEZE_V1.json']},'limits':['Six fixed structural inputs only; no asymptotic inference.','Compare methods within this paired suite; cross-cycle wall times can differ with host load.','Memory timeouts are censored; no peak estimate or lower bound inferred.','Report postprocessing did not rerun a provider or integrity suite.']}
    with (A/'LENGTH_SCALING_SUMMARY_V1.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    lines=['# ممیزی مستقل مقیاس طول C012','','هر ۳۶ اجرای CLI کامل و مستقل تأیید شد. از چهار سنجش حافظه، یک اجرا کامل و سه اجرا در سقف ۲۰ ثانیه ناتمام ماند؛ هر سه حفظ شده‌اند. هیچ خطای معنایی یا اختلاف در شمارش خانواده/زوج‌ها یافت نشد.','','الفبا ۸ نماد و داده شامل چهار مثبت و چهار منفی است. چهار جابه‌جایی مخالف‌برچسب، چهار زوج را به هم متصل می‌کنند؛ افراز این چهار زوج نیز همهٔ منفی‌ها را رد می‌کند. بنابراین تمام و فقط ۱۵ درشت‌سازی این چهار اتم سازگارند. گواهی پیش از زمان‌گیری با اجرا و ثبت مستقل تولید شد.','','| خانواده | طول هر واژه | ران‌های واقعی ۸ واژه | مجموع نویسه‌ها | baseline ثانیه | candidate ثانیه | خروجی baseline بایت | خروجی candidate بایت |','|---|---:|---|---:|---:|---:|---:|---:|']
    for c in comparisons:
        b=c['methods']['baseline'];v=c['methods']['candidate'];lines.append(f"| {c['family']} | {c['length']} | {c['run_counts']} | {c['total_characters']} | {b['median_cli_seconds']:.6f} | {v['median_cli_seconds']:.6f} | {b['median_stdout_bytes']} | {v['median_stdout_bytes']} |")
    lines+=['','زمان‌ها میانهٔ سه فرایند تازه‌اند و خواندن ورودی، آغاز Python، پیش‌پردازش، ساخت شاهدها و سریال‌سازی خروجی کامل را در بر می‌گیرند. ترتیب هر تکرار میان دو روش جابه‌جا شد.','','| خانواده و روش | نسبت طول نسبت به نقطهٔ قبلی | نسبت زمان نسبت به نقطهٔ قبلی |','|---|---:|---:|']
    for c in comparisons:
        for method,v in c['methods'].items():
            q=v['relative_to_previous_length']
            if q:lines.append(f"| {c['family']} L={c['length']} {method} | {q['length_ratio']:.3f} | {q['time_ratio']:.3f} |")
    lines+=['','کاندید در هر شش ورودی از baseline کندتر بود. در کم‌ران، با افزایش طول از ۱۰۰هزار به یک‌میلیون، زمان کاندید از حدود ۲٫۹۴ به ۲۵٫۳۸ ثانیه رسید. در پرران، طول ۱۰۰هزار برای کاندید حدود ۱۱٫۵۷ ثانیه گرفت. این‌ها مشاهدات همین شش ورودی و همین میزبان‌اند؛ مرتبهٔ مجانبی از آن‌ها نتیجه نمی‌شود.','','حافظهٔ قابل ردیابی Python تنها در baseline پرران ۱۰۰هزار کامل اندازه‌گیری شد: ۶٬۵۲۵٬۱۴۹ بایت. سنجش هر دو روش در کم‌ران یک‌میلیون و کاندید در پرران ۱۰۰هزار timeout شد. این نتیجه تخمین اوج حافظهٔ آن‌ها نیست. tracing پیش از خواندن ورودی و import آغاز شد و پس از solve و سریال‌سازی پایان یافت؛ RSS اندازه‌گیری نشد.','',f"ممیزی {s['pair_witness_references']} ارجاع شاهد زوجی، {s['certificates_replayed']} گواهی و {s['integrity_checks']} بررسی هش منابع/جریان‌ها را ثبت کرد. ledger مسیر هر capture و وضعیت آن را حفظ می‌کند. summary.json دادهٔ خام زمان/خروجی/حافظه و فایل LENGTH_SCALING_SUMMARY_V1.json طول‌ها، ران‌ها، نسبت‌ها و هش تحویل‌ها را نگه می‌دارند.",'','هیچ حل‌گر یا اثباتی تغییر نکرد؛ پس از این مقایسهٔ محدود اجرای مجددی انجام نشد.']
    with (A/'LENGTH_SCALING_AUDIT_FA_V1.md').open('x',encoding='utf-8') as f:f.write('\n'.join(lines)+'\n')
    print(json.dumps({'status':result['status'],'timing_complete':36,'memory_censored':3,'report_sha256':sha(A/'LENGTH_SCALING_AUDIT_FA_V1.md'),'summary_sha256':sha(A/'LENGTH_SCALING_SUMMARY_V1.json')}))
if __name__=='__main__':main()
