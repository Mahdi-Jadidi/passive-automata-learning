from pathlib import Path
import json,hashlib,shutil,zipfile
root=Path.cwd();src=root/'output/final_1230';dst=root/'results/2026-10-24'
if dst.exists(): raise SystemExit('Dated snapshot already exists; refusing overwrite')
source_manifest=json.loads((src/'manifest.json').read_text(encoding='utf8'))
for name,digest in source_manifest.items():
 assert hashlib.sha256((src/name).read_bytes()).hexdigest()==digest,name
dst.mkdir(parents=True)
for p in src.rglob('*'):
 if p.is_file() and p.suffix!='.zip' and p.name!='manifest.json':
  target=dst/p.relative_to(src);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
(dst/'provenance').mkdir()
shutil.copy2(src/'manifest.json',dst/'provenance/source_manifest_2026-10-22.json')
(dst/'README_FA.md').rename(dst/'Delivery_README_FA.md')
(dst/'README_FA.md').write_text('''# راهنمای شروع و پیگیری پژوهش Split یا Global RPNI

نسخهٔ ثبت نتایج: ۲۰۲۶/۱۰/۲۴. محتوای علمی و ارائه از نسخهٔ نهایی ۲۰۲۶/۱۰/۲۲ کپی شده‌اند؛ در این ثبت، قضیه یا نتیجهٔ پژوهشی تازه‌ای اضافه نشده است. گزارش‌های آزمون، نتایج اجراهای قبلی‌اند. تمام فایل‌های مبدأ با manifest همان نسخه تطبیق داده شدند.

## مسیر مطالعه

۱. ابتدا [وضعیت فعلی و کار بعدی](CURRENT_STATUS_FA.md) را بخوان.
۲. سپس [فهرست دسته‌ها، آزمون‌ها و محل اثبات هر ادعا](CLAIMS_FA.md) را ببین.
۳. برای ارائه، [پاورپوینت انگلیسی](RPNI_Final_1230_EN.pptx) و [متن گفتاری فارسی](Speaker_Notes_FA.docx) را باز کن. متن فارسی [نسخهٔ Markdown](Speaker_Notes_FA.md) هم دارد. اسلایدهای ۱ تا ۱۴ برای حدود ۱۸ دقیقه و اسلایدهای ۱۵ تا ۲۸ پیوست اثبات‌اند. talk_timing.json زمان هر بخش و slide_content.json متن و یادداشت‌های هماهنگ را نگه می‌دارند.
۴. اثبات جاری در [Research_Proofs_EN.md](research/Research_Proofs_EN.md) است. گزارش‌های Original، Previous و Coverage پشتوانهٔ ادعاهای قبلیِ ارجاع‌شده‌اند؛ آمار تاریخی آن‌ها را با آمار نسخهٔ نهایی یکی نکن.
۵. [راهنمای تحویل قبلی](Delivery_README_FA.md) و [راهنمای پژوهش](research/README_FA.md) جزئیات بازتولید را دارند.

## اجرای نمونه و کنترل سلامت

در این پوشه با Python 3 اجرا کن:

```text
python -X utf8 -B verify_snapshot.py
python -X utf8 -B research/static_selector.py research/two_trace_example.json
```

فرمان اول هش فایل‌ها، پنج گزارش ممیزی و نمونهٔ عددی جاری را بررسی می‌کند؛ آزمون‌های گسترده را دوباره اجرا نمی‌کند. فرمان دوم انتخاب‌گر را بدون اجرای یادگیرنده فراخوانی می‌کند. کد پژوهش به کتابخانهٔ استاندارد Python نیاز دارد. ساخت دوبارهٔ PPTX/DOCX نیازمند ابزارهای ارائه و سندِ محیط سازنده است؛ فایل‌های نهایی برای استفاده به آن‌ها نیاز ندارند.

## تکرار ممیزی‌های کامل

برای حفظ این نسخهٔ ثابت، ابتدا پوشه را در محل دیگری کپی کن. از زیرپوشهٔ research نسخهٔ کپی‌شده اجرا کن:

```text
python -X utf8 -B audit_static.py
python -X utf8 -B audit_regressions.py
python -X utf8 -B audit_tree_bounds.py
python -X utf8 -B audit_compiled.py
python -X utf8 -B audit_amortized.py
```

این فرمان‌ها فایل نتایج را بازنویسی می‌کنند. فایل verify_package.py قدیمیِ داخل research نیز بسته و manifest مربوط به همان زیرپوشه را تولید می‌کند. برای کنترل بدون تغییر این snapshot، verify_snapshot.py در ریشه را به کار ببر.

## نظم نسخه‌ها

این پوشه snapshot ثابت است. ادامهٔ پژوهش باید در پوشهٔ تاریخ‌دار تازه انجام شود. برای ادامه، [یادداشت تحویل و ادامه](RESUME_FA.md) را به پژوهشگر یا دستیار بعدی بده. INTEGRITY_SHA256.json هش فایل‌ها را دارد و provenance منشأ این نسخه را ثبت می‌کند. هش، ابزار تشخیص تغییر فایل است؛ صحت ریاضی را اثبات نمی‌کند.
''',encoding='utf8')
(dst/'CURRENT_STATUS_FA.md').write_text('''# وضعیت پژوهش و مسائل باز

## مسئله و قرارداد

با افراز معلوم و مرتب الفبا، می‌خواهیم پیش از اجرای یادگیرنده بگوییم RPNI جهانی یا مجموعهٔ RPNIهای محلی هزینهٔ کمتری دارد. پذیرش ترکیبی AND است؛ رشتهٔ خالی حفظ و هر منفی فقط به شاهد دارای بزرگ‌ترین اندیس تخصیص داده می‌شود. معیار W_ref رویدادهای مشخصِ پیاده‌سازی sparse با نگاشت والد تخت و ترتیب shortlex است. هزینهٔ Split شامل آماده‌سازی و اجرای ترتیبی عوامل است؛ محصول صریح، کمینه‌سازی، زمان واقعی، عملیات داخلی کتابخانه و هزینهٔ بیتی جزو شمارش نیستند.

## پاسخ دو محور اصلی

۱. عضویت در ناحیهٔ گواهیِ روش فعلی با شرط‌های ساختاری و آزمون‌های بازه‌ای قبل از یادگیری قابل تشخیص است. این ناحیه مجموعهٔ همهٔ ورودی‌های قابل تصمیم با هر روش ممکن نیست.
۲. هر برندهٔ گواهی‌دار در این ناحیه از نامساوی اثبات‌شده یا هزینهٔ دقیق نتیجه می‌شود. NET هزینهٔ انتخاب‌گر H را نیز پرداخت می‌کند؛ PIPELINE فقط هزینهٔ دو مسیر را مقایسه می‌کند.

## پیشرفت مهم نسخهٔ نهایی

کران پایین عمومی با پتانسیل q−|Red| هزینهٔ تلاش‌های پذیرفته و ردشده را می‌پوشاند. کران بالای عمومی با شمارش دقیق‌تر بستار و بازنگاشت قرمزها بهبود یافته است. برای منفی‌های دارای حرف بیرون از پشتیبان مثبت، کران استهلاکی تیزتر و معتبر برای مثبت‌های دلخواه داریم.

خانوادهٔ دو مثبت ba^n b^(n−1) و b a b^(n−1) a^(n−1)، بدون منفی و با الفبای دقیق {a,b} و دو بلوک تک‌حرفی، برای تمام n≥4 گواهی سود خالص Split می‌گیرد. در n=4: H=99، WS=170 و LG=274، پس 269<274≤WG. مقدار واقعیِ کنترل‌شدهٔ WG=466 مقدمهٔ گواهی نیست. n≥4 شرط کافی این گواهی است، نه حداقل عمومی نمونه یا طول.

خانواده‌های Global، خانوادهٔ کامل متوازن و مقایسهٔ دقیق درخت‌های دارای یک یال برای هر حرف نیز حفظ شده‌اند. برای تمام ۲۱۸۷ برچسب‌گذاریِ واژگان دودویی طول حداکثر دو، جدول آفلاین کامل داریم: Global=754، Split=493، تساوی=15، AND ناممکن=925. ساخت جدول 405921 و بارگذاری 2215 رویداد دارد. این جدول حل ارزان ورودی‌های نامحدود نیست.

## شواهد کنترل

پنج گزارشِ ثبت‌شده جمعاً 55624 اجرای مورد آزمون و 174998 کنترل مستقلِ خارج‌قسمت ادغام دارند. شمارش‌ها شامل ورودی‌های تکراری‌اند و درصد پوشش همهٔ ورودی‌ها نیستند. یک خطای ادغام کران‌ها در حالت تک‌ریشه کشف و اصلاح و ممیزی‌ها پس از اصلاح تکرار شدند. آزمون متناهی جای اثبات را نمی‌گیرد؛ ادعاها proof-assistant certified یا داوری‌شده معرفی نمی‌شوند.

## مسائل باز و اولویت ادامه

۱. کاهش UNKNOWN با کران‌های تیزتر یا خانواده‌های تازه، بدون اجرای مخفیِ یادگیرنده. هزینهٔ هر ویژگی تازه باید در H منظور شود.
۲. پیدا کردن شرایط کافیِ پیش از اجرا برای برابری زبان Global و ترکیب عوامل، خصوصاً مثبت‌های ناقص و منفی‌های اثرگذار. این سؤال در پایان بخش اصلی و پایان پاورپوینت آمده است.
۳. تحلیل زمان واقعی و هزینهٔ ساخت محصول، فقط در یک شاخهٔ جدا با قرارداد جدید.

هیچ قضیهٔ «انتخاب ارزان و دقیق برای تمام ورودی‌های با طول نامحدود» ثابت نشده است. UNKNOWN اثبات ناممکنی نیست. total_selector در موارد حل‌نشده هر دو مسیر را واقعاً اجرا می‌کند و بنابراین پاسخ عمومی آن گواهی صرفه‌جوییِ پیش از اجرا نیست. هزینهٔ کمتر، سازگاری نمونه، برابری زبان دو خروجی و بازیابی هدف واقعی چهار گزارهٔ جدا هستند.
''',encoding='utf8')
(dst/'CLAIMS_FA.md').write_text('''# فهرست قابل پیگیری ادعاها و آزمون‌ها

تمام ردیف‌ها مشروط به قرارداد برنامهٔ مرجع، افراز معلوم، دادهٔ معتبر و سیاست ثابت تخصیص منفی‌اند. N تعداد پیشوندهای مثبت با ریشه، E=N−1، A پشتیبان حروف مثبت، Π هزینهٔ آماده‌سازی و H هزینهٔ اجرای انتخاب‌گر است. نام قواعد، همان rule در خروجی static_selector.py است. برای NET باید هزینهٔ H همان شاخهٔ واقعی پرداخت شود.

| شناسه | دسته و آزمون تشخیص | نتیجه و آزمون هزینه | محل اثبات |
|---|---|---|---|
| C01 | هر منفی w باید حداقل یک i با π_i(w)∉π_i(S⁺) داشته باشد | نبود شاهد: تجزیهٔ AND سازگار ناممکن؛ برندهٔ هزینه نام‌گذاری نمی‌شود | Original_Proofs_EN.md §2؛ اسلایدهای 3 و 16 |
| C02 | یک بلوک؛ one_block_identity | WS−WG=Π؛ Global گران‌تر نیست؛ NET اگر H<Π | Previous_Proofs_EN.md §3 |
| C03 | مثبت‌ها تهی یا فقط ε؛ root_only_positives | g=3+[ε∈S⁺]؛ WG=g، WS=g+Π+(k−1)g؛ علامت شکاف و H را بررسی کن | Previous_Proofs_EN.md §4 |
| C04 | مثبت غیرخالی، k>1 و تمام حروف مشاهده‌شدهٔ مثبت و منفی در یک بلوک؛ single_active_block | Global برنده؛ شکاف Π+4(k−1)؛ NET اگر H از شکاف کمتر باشد | Original_Proofs_EN.md §4 |
| C05 | پشتیبان مثبت فقط {a} با حداقل یک مثبت غیرخالی؛ هر منفی حرف بیرون از {a} دارد؛ unary_global_inert | Global برنده؛ K=Π+4(k−1)−D>0؛ NET اگر H<K | Research_Proofs_EN.md §6؛ Previous_Proofs_EN.md §§5–6 |
| C06 | S⁺={a} و ε منفی، k>1؛ one_letter_positive_empty_negative | WG=25؛ WS=25+Π+4(k−1)؛ Global برنده؛ NET با مقایسهٔ شکاف و H | Previous_Extension_Proofs_EN.md §6 |
| C07 | الفبای دقیق {a,b}، بلوک‌های تک‌حرفی، بدون منفی، دو مثبت ba^n b^(n−1) و b a b^(n−1) a^(n−1)، n≥4 | NET Split؛ LG−H−WS=6n²−10n−51>0؛ در n=4: 99+170<274 | Research_Proofs_EN.md §5؛ اسلایدهای 8–9 و 23–24 |
| C08 | بلوک‌های مرتب {a},{b},{c}؛ تنها منفی c؛ تمام مثبت‌ها دقیقاً n حرف a و n حرف b و تعدادشان binomial(2n,n)، n≥1؛ original_complete_balanced | NET Split برای این خانوادهٔ دقیق؛ حذف عضو یا تغییر منفی نیازمند قاعدهٔ دیگر است | Original_Proofs_EN.md §§5–9 |
| C09 | منفی تهی و E=|A|؛ درخت پیشوند برای هر حرف دقیقاً یک یال دارد؛ unique_edge_trie | WG=B(M,p,E)، WS=Π+ΣB(m_i,p_i,E_i)؛ B=m+p+(11E²+25E+6)/2؛ علامت WS−WG برنده یا تساوی را دقیق مشخص می‌کند؛ NET اگر |WS−WG|>H | Coverage_Proofs_EN.md §§2–3؛ اسلاید 25 |
| C10 | یک مثبت بدون حرف تکراری و بدون منفی؛ single_distinct_word | زیرکلاس C09 با فرمول دقیق؛ ممکن است Global، Split یا تساوی باشد | Previous_Proofs_EN.md §6A |
| C11 | مثبت دلخواه؛ هر منفی دارای حرف خارج از پشتیبان مثبت | کران‌های تیزتر inert؛ برنده فقط در صورت جدایی بازه‌ها؛ تمام اعضای این دسته الزاماً تعیین تکلیف نمی‌شوند | Research_Proofs_EN.md §4؛ اسلایدهای 7،20،21 |
| C12 | دادهٔ دلخواهِ معتبر و AND ممکن، شامل منفی اثرگذار | کران پایین و بالای عمومی؛ آزمون بازه‌ای زیر، وگرنه UNKNOWN | Research_Proofs_EN.md §§2–3 و 8؛ اسلایدهای 5–6 و 17–19 |
| C13 | واژگان متناهی V و افراز ثابت، با جدول کامل قبلاً ساخته‌شده | مقایسهٔ دقیق یا تساوی/ناممکنی برای تمام ورودی‌های داخل V؛ بیرون V برابر OUT_OF_DOMAIN؛ هزینهٔ ساخت و بارگذاری جدا | Coverage_Proofs_EN.md §§6–8؛ اسلایدهای 11 و 26 |

در C09، m_i و p_i پس از حذف تصاویر تکراری محلی محاسبه می‌شوند. شرط inert در C11 باید برای عوامل محلی نیز بعد از تخصیص منفی جدا بررسی شود. کلاس‌ها هم‌پوشانی دارند؛ ترتیب شاخه‌های برنامه و H آن‌ها را تغییر نده.

## آزمون نهایی گواهی

LG≤WG≤UG و LS≤WS≤US. اگر H+US<LG: NET Split. اگر H+UG<LS: NET Global. اگر فقط US<LG یا UG<LS برقرار است: برندهٔ PIPELINE داریم و لزوماً سود خالص نداریم. اگر هر دو هزینه دقیق و برابرند: TIE. در غیر این صورت UNKNOWN. تساوی صرفاً دو کران کافی نیست.

NET_*_COST ادعای برابری زبان دو خروجی ندارد. NET_*_EQUAL برابری را از یک استدلال مستقلِ معتبر نیز دارد. هیچ‌یک به‌تنهایی بازیابی زبان هدف را ثابت نمی‌کند.

## نمونه‌های قابل بازتولید

نمونهٔ دو تریسی در research/two_trace_example.json و گواهی‌های عددی در research/final_worked_examples.json هستند. مثال نقضِ تعمیم هزینه به برابری در research/quality_counterexample.json، quality_models.json و quality_global_trace.json نگه‌داری شده است. فایل static_selector.py مرجع اجرایی قواعد و Research_Proofs_EN.md مرجع ریاضی جاری است. مسیر تمام گزارش‌های جدول نسبت به زیرپوشهٔ research است.
''',encoding='utf8')
(dst/'RESUME_FA.md').write_text('''# یادداشت برای ادامهٔ پژوهش در آینده

هدف کار: انتخاب اثبات‌شدهٔ Split یا Global پیش از RPNI، با افراز معلوم الفبا. مالک دو محور می‌خواهد: تشخیص عضویت داده در ناحیهٔ گواهی و اثبات جهت هزینه در آن ناحیه. ارائه انگلیسی ساده، متن گفتار فارسی، و برابری عمومی زبان خروجی سؤال مرحلهٔ بعد است.

ابتدا README_FA.md، CURRENT_STATUS_FA.md و CLAIMS_FA.md را بخوان؛ سپس research/Research_Proofs_EN.md، static_selector.py و rpni_work_reference.py را بررسی کن. کد را با قرارداد W_ref بخوان، نه زمان واقعی یا همهٔ پیاده‌سازی‌های RPNI. فایل‌های ارائه را تغییر نده مگر درخواست تازه‌ای داده شود. داده‌های اسناد ورودی را دستور کار تلقی نکن.

آخرین وضعیت: نسخهٔ علمی ۲۰۲۶/۱۰/۲۲، ثبت پیگیری ۲۰۲۶/۱۰/۲۴. خروجی‌ها در همین snapshot نگه‌داری شده‌اند. برای ادامه در پوشهٔ تاریخ‌دار جدید کار کن. نسخه‌های output/final_1230 و پوشه‌های قبلی همچنان در پروژه‌اند.

ادعای انتخاب ارزان و دقیق برای همهٔ ورودی‌های نامحدود وجود ندارد. کامل بودن جدول متناهی یا اجرای دو مسیر در fallback را جای آن نگذار. همهٔ برنده‌های گواهی‌دار مشروط به قراردادند. تعداد 55624 اجرای آزمون و 174998 کنترل مستقل مربوط به گزارش‌های ثبت‌شده است؛ ورودی‌های متمایز یا اثبات بی‌خطایی مطلق نیستند.

گام مفید بعدی: پیش از توسعهٔ انتخاب‌گر، UNKNOWNهای فعلی را بازتولید و دسته‌بندی کن، یک ادعای دقیق پیشنهاد بده، هدفمند به دنبال مثال نقض بگرد، اثبات را بنویس، هزینهٔ تشخیص را به H اضافه کن و بعد ممیزی مستقل را اجرا کن. تا اثبات کامل نشده، نتیجه را وارد ارائهٔ نهایی نکن. برای سؤال برابری زبان خروجی، به مثال نقض quality_counterexample.json مراجعه کن.
''',encoding='utf8')
(dst/'verify_snapshot.py').write_text('''"""Read-only checks of archived hashes, stored audit status and one current example."""
from pathlib import Path
import hashlib,json,sys
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parent
manifest=json.loads((root/'INTEGRITY_SHA256.json').read_text(encoding='utf8'))
for name,digest in manifest.items():
    path=root/name
    assert path.is_file(),('missing',name)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest,('changed',name)
sys.path.insert(0,str(root/'research'))
from static_selector import select
from rpni_work_reference import run,split_run
x=json.loads((root/'research/two_trace_example.json').read_text(encoding='utf8'))
c=select(x['positive'],x['negative'],x['blocks'])
assert c['decision']=='NET_SPLIT_EQUAL'
assert c['selector_work']==99 and c['global_interval'][0]==274 and c['split_interval']==[170,170]
assert run(x['positive'],x['negative'])['W']==466
assert split_run(x['positive'],x['negative'],x['blocks'])['W']==170
names=['audit_results.json','extension_audit_results.json','tree_audit_results.json','compiled_audit_results.json','amortized_audit_results.json']
r=[json.loads((root/'research'/n).read_text(encoding='utf8')) for n in names]
assert all(a['status']=='passed' for a in r)
assert sum(a['independent_candidate_checks'] for a in r)==174998
cases=r[0]['valid_case_executions']+r[1]['valid_case_executions']+r[2]['case_executions']+r[3]['all_domain_inputs_checked']+r[4]['case_executions']
assert cases==55624
print(json.dumps(dict(status='passed',files_checked=len(manifest),stored_case_executions=cases,stored_independent_candidate_checks=174998,example='99+170=269<274<=WG; reference WG=466',full_audits_rerun=False),indent=2))
''',encoding='utf8')
inputs=[]
for name in ['RPNI_Alphabet_Decomposition_Presentation_FA.pdf','exact_decision_results (1).csv','EXACT_DECISION_README (1).md','main (1).pdf','speaker_notes.tex','LIPIcs.CONCUR.2024.10.Passive Learning of Regular Data Languages in Polynomial Time and Data.pdf']:
 p=Path('C:/Users/Mahdi/Downloads')/name
 inputs.append(dict(name=name,path=str(p),available=p.is_file(),sha256=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None))
(dst/'provenance/origins.json').write_text(json.dumps(dict(snapshot_date='2026-10-24',timezone='Asia/Tehran',scientific_baseline_date='2026-10-22',source=str(src),source_file_hashes_checked=len(source_manifest),input_files=inputs,inputs_copied=False),ensure_ascii=False,indent=2),encoding='utf8')
files=sorted(p for p in dst.rglob('*') if p.is_file())
manifest={p.relative_to(dst).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(dst/'INTEGRITY_SHA256.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
index=root/'START_HERE_FA.md'
if index.exists(): raise SystemExit('Root index already exists; snapshot complete, refusing overwrite')
index.write_text('''# شروع و ادامهٔ پژوهش یادگیری غیرفعال اتوماتا

آخرین ثبت قابل پیگیری: **۲۰۲۶/۱۰/۲۴**. نسخهٔ علمی مبنا: **۲۰۲۶/۱۰/۲۲**.

- [راهنمای بستهٔ جاری](results/2026-10-24/README_FA.md)
- [نتایج فعلی، مرز ادعا و مسائل باز](results/2026-10-24/CURRENT_STATUS_FA.md)
- [دسته‌های قابل تصمیم، آزمون و ارجاع اثبات](results/2026-10-24/CLAIMS_FA.md)
- [پاورپوینت نهایی انگلیسی](results/2026-10-24/RPNI_Final_1230_EN.pptx)
- [متن گفتاری فارسی](results/2026-10-24/Speaker_Notes_FA.docx)
- [اثبات‌های جاری](results/2026-10-24/research/Research_Proofs_EN.md)
- [انتخاب‌گر بدون اجرای یادگیرنده](results/2026-10-24/research/static_selector.py)
- [یادداشت ادامهٔ کار](results/2026-10-24/RESUME_FA.md)

پوشهٔ results/2026-10-24 یک نسخهٔ ثابت شامل ارائه، اثبات‌ها، کد، مثال‌ها، گزارش‌های ممیزی و منشأ فایل‌هاست. نسخه‌های پیشین در output حفظ شده‌اند. برای توسعه، نسخهٔ تاریخ‌دار تازه بساز. برای کنترل سلامت این ثبت، از پوشهٔ پروژه اجرا کن:

```text
python -X utf8 -B results/2026-10-24/verify_snapshot.py
```

این کنترل، ممیزی‌های کامل را دوباره اجرا نمی‌کند و صحت ریاضی را از هش فایل نتیجه نمی‌گیرد. نتیجهٔ عمومیِ انتخاب ارزان برای تمام ورودی‌های نامحدود هنوز اثبات نشده است.
''',encoding='utf8')
print(json.dumps(dict(snapshot=str(dst),source_hashes_verified=len(source_manifest),snapshot_files=len(manifest)),indent=2))
