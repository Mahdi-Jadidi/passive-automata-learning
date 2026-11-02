"""Documentation-only C009 report revision. No solver/test execution."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
target = HERE / 'REPORT_CANDIDATE_FA_v2.md'
if target.exists():
    raise FileExistsError(target)
text = (HERE / 'REPORT_CANDIDATE_FA_v1.md').read_text(encoding='utf-8-sig')

def replace(old, new):
    global text
    if text.count(old) != 1:
        raise ValueError('Expected one replacement: ' + old[:100])
    text = text.replace(old, new)

replace('# C009 — شناسایی کامل و جزئی مالکیت، مشروط به مجموعهٔ مجاز تعداد مؤلفه‌ها',
        '# C009 — گزارش نهایی علمی، ویرایش دوم: شناسایی کامل و جزئی مالکیت')
replace('**وضعیت این ویرایش:** گیت اصلیِ صحت پذیرفته شده است؛ کنترل‌های تکمیلی و\nچهار مورد مقیاس هنوز منتظر شواهد پذیرفته‌شده‌اند. این گزارش دادهٔ واقعی\nجدیدی، دقت بازیابی سامانه‌های واقعی یا برتری عمومی سرعت را ادعا نمی‌کند.\nتهیهٔ این متن اجرای علمی تازه‌ای ندارد.',
        '**وضعیت نهایی این ویرایش:** گیت اصلیِ صحت، نه کنترل تکمیلی و کنترل\nرابط ریشه پذیرفته شده‌اند. سه مورد مقیاس خروجی کامل و دقیق داده‌اند؛\nمورد ۱۴نمادی در مهلت تعاونی ناتمام مانده و موفقیت بازیابی محسوب نمی‌شود.\nپذیرش مقیاس از نوع accepted_with_censoring است. نسخهٔ اول محفوظ است.\nاین گزارش دادهٔ واقعی جدید، دقت بازیابی سامانه‌های واقعی یا برتری عمومی\nسرعت را ادعا نمی‌کند. تهیهٔ این متن اجرای علمی تازه‌ای ندارد.')
replace('اطلاع مورد اعتماد k≥2 تعداد\nرا دقیقاً دو می‌کند و مالکیت همچنان مبهم می‌ماند. اثبات و مرزهای این',
        'اطلاع مورد اعتماد k≥2 تعداد\nرا دقیقاً دو می‌کند و مالکیت همچنان مبهم می‌ماند. کنترل مستقلِ افزوده\nو اجرای wrapper ریشه نیز همین دو جواب را تأیید کرده‌اند: ab و ac مبهم\nو bc قطعاً جداست. پس شناسایی جزئی می‌تواند جداییِ قطعی بدهد بدون آنکه\nکل افراز یکتا باشد؛ این‌جا K={2} است و مدل تک‌بلوکی مجاز نیست. اثبات و مرزهای این')
replace('درخواست `--enumerate` کل جواب‌ها را می‌خواهد؛ قطع در تولید آن، نتیجه را\nناقص می‌کند و فهرست ناقص به‌عنوان کامل معرفی نمی‌شود. اگر K ناسازگار با\nنمونه باشد، وضعیت `model_inconsistent` با ورودی نامعتبر و `unknown` ناشی\nاز قطع تفاوت دارد. تأیید این رفتارها در کنترل‌های اجراییِ تکمیلی هنوز\nدر این ویرایش باز است؛ توصیف رابط جای آن ممیزی را نمی‌گیرد.',
        'درخواست `--enumerate` کل جواب‌ها را می‌خواهد؛ قطع در تولید آن، نتیجه را\nناقص می‌کند و فهرست ناقص به‌عنوان کامل معرفی نمی‌شود. اگر K ناسازگار با\nنمونه باشد، وضعیت `model_inconsistent` با ورودی نامعتبر و `unknown` ناشی\nاز قطع تفاوت دارد. کنترل‌های اجراییِ مشخص در بخش بعد پذیرفته شده‌اند؛\nاین پذیرش به همهٔ لحظه‌های وقفه یا تمام ورودی‌های ممکن تعمیم داده نمی‌شود.')
start = text.index('## پیوست باز: کنترل‌ها و چهار مورد مقیاس')
text = text[:start] + '''## کنترل‌ها و رابط ریشه: پذیرش با دامنهٔ مشخص

`audit/controls_validation_v3.json` با وضعیت accepted_independent_controls_audit
نه کنترل را پذیرفته است: هفت ورودی نامعتبر، یک deadline منقضی و یک وقفه
در بخش حفاظت‌شده. نامعتبرها شامل الفبای تهی/تکراری، برچسب متناقض، نماد
خارج الفبا و allowed_k تهی/صفر/بزرگ‌تر از اندازهٔ الفبا هستند. deadline
به unknown و complete=false بدون نتیجهٔ قطعی رسیده است. در کنترل وقفه،
پس از سه فراخوانی projection تکمیل‌شده و محاسبهٔ یک ماسک بلوک، SIGINT
به API تزریق شده؛ خروجی unknown بدون شمارش، روابط یا شاهد نهایی بوده است.
این همان مسیرِ حفاظت‌شده است، نه آزمایش وقفه در تمام سطرهای برنامه.

`audit/addenda/validation_v2.json` دو افراز ab|c و ac|b را برای نمونهٔ
abc بخش kmax مستقلاً تأیید کرده است. `audit/root_wrapper_validation_v1.json`
نیز اجرای واقعیِ wrapper ریشه را با دو جواب و روابط ab/ac مبهم و bc
قطعاً جدا پذیرفته است. این کنترل افزوده جایگزین یا افزایشِ ساختگیِ عدد
۱۲۹ ورودیِ گیت اصلی نیست. هش wrapper بررسی‌شده:
`543a020f690e0403f21799f2875df08aa9546688bccb65119499bff09a9b57a2`.

## چهار مورد مقیاس: سه کامل و یک ناتمامِ حفظ‌شده

منبع `audit/scale_validation_v1.json` با وضعیت accepted_with_censoring
و mismatches خالی است. پروندهٔ اجرا `audit/scale_provider_ledger_v1.jsonl`
زمان‌های کل فرایند زیر را ثبت کرده است. این‌ها **تک‌مشاهدهٔ صحت با سقف
زمان** هستند؛ بنچمارک تکرارشده، مقایسهٔ روش‌ها یا برتری عمومی سرعت نیستند.

| مورد | K | شمار مستقل مرجع | خروجی provider | زمان تک‌مشاهده، ثانیه |
|---|---|---:|---|---:|
| ۱۰ نماد، پنج اتم جفتی | {2,4} | ۲۵ | کامل؛ کل مجموعه و زوج‌ها دقیق | ۰٫۷۸۴۸۲۴۳ |
| ۱۲ نماد، شش اتم جفتی | {3,5} | ۱۰۵ | کامل؛ کل مجموعه و زوج‌ها دقیق | ۵٫۰۹۱۸۳۳۲ |
| ۱۴ نماد، هفت اتم جفتی | {2,4} | ۴۱۳، فقط مرجع | unknown؛ شمار provider تهی | ۲۷٫۳۴۵۲۰۱۹ |
| ۴ نماد، واژهٔ طول ۴۰۹۶ | {2} | ۳ | کامل؛ کل مجموعه و زوج‌ها دقیق | ۰٫۴۹۲۷۹۰۹ |

سه مورد اتمی از خانوادهٔ ساختاریافته با هم‌مالکیت اجباری جفت‌ها هستند؛
مرجع مستقل افرازهای اتم‌ها را کامل بررسی کرده و زوج‌ها را با شمارش‌های
استرلینگ تطبیق داده است. این روشِ ساخت، ظرفیت تضمینی برای دادهٔ دلخواه
با همان اندازهٔ الفبا نیست. مورد واژهٔ بلند نیز یک ورودی مشخص است.

در مورد ۱۴نمادی، تمام ۱۶٬۳۸۳ ماسک بلوک پیش‌محاسبه شد و ۶۱٬۶۶۴ حالت و
۱٬۴۶۸٬۴۱۴ شاخه ثبت شد؛ اما خروجی پس از مهلت تعاونی ۲۷ثانیه‌ای
complete=false، status=unknown و partition_count=null داشت. عدد ۴۱۳
از مرجع مستقل است، **نه پاسخ به‌دست‌آمدهٔ حل‌گر**. هیچ مجموعهٔ کامل یا
رابطهٔ مالکیت برای provider این مورد پذیرفته نشده است. capture آن
`20261102T111433.912999Z_bf0e87526a`، با exit=3، در طبقه‌بندی عمومیِ
اجرا program_error است؛ تفسیر علمیِ درست، سانسورِ مهلت با خروجی ناقص
است، نه خطای قضیه، نبود مدل یا شمارش نادرستِ یک پاسخ کامل. فرزند جمع‌آوری
شده و تلاش ناتمام حفظ شده است؛ مهلت یا اجرا برای تبدیل نتیجه به موفقیت
تکرار نشده است.

## اصلاح دامنهٔ ممیزی و مسیر همهٔ شکست‌ها

[گزارش مستقل ممیزی](../audit/FINAL_AUDIT_REPORT_FA.md) حفظ شده و هفت رخداد
ابزار/اجراگر را با شناسه‌های capture و مسیر شواهد شرح می‌دهد؛ شکست snapshot
خروجیِ هنوزساخته‌نشده، خطای شرط شاهد ممیز، دفتر باینری، مسیر import،
فرض نادرست manifest در کنترل deadline، خطای نوع Path در گزارش ممیز و
ردِ بازنویسی کورپس از جملهٔ آن‌ها هستند. این متن traceback تازه نمی‌سازد؛
جزئیات واقعی در همان گزارش، attempts و orchestration_failure_v1.json
باقی‌اند. شکست‌های ابزار به خطای حل‌گر یا رد اثبات تبدیل نشده‌اند.

اصلاحیهٔ مستر `coordination/AUDIT_SCOPE_ERRATUM.json` عبارت بیش‌ازحدکلیِ
«تعداد مؤلفهٔ مجهول در این دور آزموده نشد» را تصحیح می‌کند: پیش‌فرض
allowed_k=همهٔ تعدادها و مجموعه‌های چندعضوی واقعاً در گیت ثابت ۱۲۹موردی
پوشش داده شده‌اند. آنچه ادعا نمی‌شود **بازیابی بی‌قیدِ تعداد واقعیِ
فیزیکی** است. نویز، نماد مشترک و اتصال به RPNI در دامنهٔ آزمایش این دور
نیستند. گزارش اصلی بدون حذف تاریخی همراه این اصلاحیه خوانده می‌شود.

## تصمیم علمی و ادامهٔ مشخص

این دور، شناسایی مالکیت را از گواه محدود r=k به شمارش دقیق افرازها برای
K دلخواه و شناسایی جزئیِ زوج‌ها گسترش می‌دهد. صحت روی گیت اصلی، کنترل‌های
مشخص، رابط ریشه و سه سلول کامل تأیید شده؛ سلول ۱۴نمادی حد عملی همین
اجرای محدود را با سانسور نشان می‌دهد. هیچ پذیرش اجراییِ وعده‌داده‌شده‌ای
در این ویرایش معلق معرفی نشده است؛ محدودیت‌ها و نتیجهٔ ناتمام بخشی از
تحویل نهایی‌اند.

یک لمِ هرس برای آینده در `theory/FUTURE_PRUNE_v1.md` جدا ثبت است:
برای B⊆S، ماسک R(B)⊆R(S)؛ پس اگر covered OR R(rem) همهٔ منفی‌ها را
نپوشاند، تکمیل ناممکن است. این لم **در provider v1 پیاده‌سازی، فعال یا
اندازه‌گیری نشده** و به آن هیچ نتیجهٔ سرعت یا رفع سانسور نسبت داده
نمی‌شود. تغییر بعدی باید نسخه و ممیزی مستقل خودش را داشته باشد.

اسنپ‌شات و هش منابع همین گزارش در `theory/report_v2_evidence/MANIFEST.json`
ثبت‌اند. نسخهٔ اول، اثبات‌ها، بازبینی منبع، شکست‌ها و خروجی ناتمام حفظ
شده‌اند. هیچ دادهٔ واقعیِ ارائه‌نشده، شناسهٔ دستگاه، تضمین بازیابی از هر
تریس متناهی، بهبود عمومی سرعت یا رفع مسئلهٔ نویز/نماد مشترک به نتیجه
افزوده نمی‌شود. تضمین مالکیت و روابط اجباری همچنان دقیقاً مشروط به
سامانهٔ مستقل منظمِ واقعی، برچسب‌های درست و K مورد اعتماد است.
'''
target.write_text(text, encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

directory = HERE / 'report_v2_evidence'
directory.mkdir()
sources = [
    'audit/provider_gate_validation_v1.json',
    'coordination/CORRECTNESS_ACCEPTANCE.json',
    'audit/controls_validation_v3.json',
    'audit/root_wrapper_validation_v1.json',
    'audit/addenda/validation_v2.json',
    'audit/scale_validation_v1.json',
    'audit/scale_provider_ledger_v1.jsonl',
    'audit/FINAL_AUDIT_REPORT_FA.md',
    'coordination/AUDIT_SCOPE_ERRATUM.json',
    'audit/orchestration_failure_v1.json',
    'theory/REPORT_CANDIDATE_FA_v1.md',
    'theory/report_v1_evidence/MANIFEST.json',
    'theory/FUTURE_PRUNE_v1.md',
    'theory/PEER_REVIEW_PROVIDER_V1.md',
]
records = []
for source_name in sources:
    source = ROOT / source_name
    snapshot = directory / source_name.replace('/', '__')
    snapshot.write_bytes(source.read_bytes())
    if digest(source) != digest(snapshot):
        raise ValueError('snapshot mismatch')
    records.append({'source': source_name, 'snapshot': snapshot.name, 'sha256': digest(snapshot)})

manifest = {
    'id': 'C009-THEORY-REPORT-002',
    'report': '../' + target.name,
    'report_sha256': digest(target),
    'scientific_status': 'main_controls_root_addendum_accepted_scale_accepted_with_censoring',
    'evidence': records,
    'main_unique_inputs': 129,
    'main_provider_calls': 129,
    'complete_partition_sets_matched': 129,
    'projection_witness_replays': 15394,
    'controls_accepted': 9,
    'invalid_controls': 7,
    'deadline_controls': 1,
    'protected_interrupt_controls': 1,
    'scale_complete_exact': 3,
    'scale_censored': 1,
    'm14_provider_count': None,
    'm14_oracle_count': 413,
    'pending': [],
    'future_prune_implemented': False,
    'official_performance_claim': False,
    'new_experiments': 0,
    'provider_changes': False,
    'v1_preserved': True,
}
(directory / 'MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
ready = {
    'id': 'C009-THEORY-REPORT-READINESS-002',
    'report': target.name,
    'sha256': digest(target),
    'evidence': 'report_v2_evidence/MANIFEST.json',
    'status': manifest['scientific_status'],
    'pending': [],
    'new_experiments': 0,
    'v1_preserved': True,
}
(HERE / 'REPORT_READINESS_v2.json').write_text(json.dumps(ready, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps(ready, ensure_ascii=False))
