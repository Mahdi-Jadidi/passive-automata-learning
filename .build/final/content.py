from pathlib import Path
import json
root=Path(__file__).parent
out=root.parents[1]/'output'/'final'
F=lambda s:dict(kind='text',text=s)
E=lambda s:dict(kind='eq',text=s)
def T(headers,rows,widths):return dict(kind='table',headers=headers,rows=rows,widths=widths)
SOURCE='Proofs: proofs/Original_Proofs_EN.md and proofs/Extension_Proofs_EN.md. Programs: research/extended_selector.py and research/rpni_work_reference.py. Guarantees concern the declared W_ref event model.'
slides=[]
def add(title,blocks,notes,seconds=0,proof=''):
    slides.append(dict(title=title,blocks=blocks,notes=notes,seconds=seconds,proof=proof,source=SOURCE))

add('Split or Global RPNI?',[
F('Pre-training cost certificates'),
F('Recognizable input conditions and proved choices'),
F('Main talk: 18 minutes. Detailed proofs follow in the appendix.')],
'''مسئلهٔ ما انتخاب پیش از یادگیری است: وقتی افراز الفبا معلوم است، چه زمانی اجرای جداگانهٔ RPNI روی مؤلفه‌ها کار کمتری از اجرای جهانی دارد؟ دو محور اصلی داریم: تشخیص ورودی‌های دارای گواهی و انتخاب مسیر برای همان ورودی‌ها. نتیجهٔ فعلی، مجموعه‌ای از شرایط کافی با اثبات و پیاده‌سازی است. برابری زبان خروجی را در مواردی که ثابت شده ذکر می‌کنیم و گسترش آن را سؤال پژوهشی مرحلهٔ بعد نگه می‌داریم.''',30,'Original §1; Extension §1')

add('The two research questions',[
F('Q1. Can we recognize inputs that admit a proved cost decision before training?'),
F('Q2. With the partition known, can we certify Split or Global as cheaper?'),
F('Current answer: yes on explicit sufficient regions, including new incomplete samples.'),
F('The guarantee is deterministic under the stated algorithm and work contract.'),
F('We do not claim a winner for every possible input.')],
'''سؤال اول این است که آیا می‌توانیم از روی خودِ تریس‌ها و افراز معلوم تشخیص بدهیم چه ورودی‌ای تحت پوشش گواهی ماست. سؤال دوم این است که برای ورودی دارای گواهی، آیا برندهٔ هزینه را بدون اجرای یادگیرنده‌ها می‌دانیم. پاسخ فعلی به هر دو، برای ناحیه‌های مشخص، بله است. ابتدا فقط دو خانوادهٔ ساختاری داشتیم. اکنون شرطی مبتنی بر پیشوندهای واقعی ورودی هم داریم که مثبت‌های ناقص و بعضی منفی‌های اثرگذار را پوشش می‌دهد. نکتهٔ اصلی این است که انتخاب از آزمایش دو اجرا به دست نمی‌آید؛ از نامساوی‌های اثبات‌شده به دست می‌آید. اگر شرایط جداکننده برقرار نباشد، نامعلوم گزارش می‌کنیم. این نامعلوم، محدودیت گواهی فعلی است و ادعای ناممکن بودن هر روش دیگر نیست.''',60,'Original §10; Extension §§2–8')

add('Known partition and safe local samples',[
E('Σ=B₁ ⊎ ··· ⊎ Bₖ,     Pᵢ=πᵢ(S⁺)'),
F('Projection erases outside symbols and preserves order. Keep ε.'),
F('The local outputs are combined by AND. Labels are finite and consistent.'),
E('V(w)={i : πᵢ(w)∉Pᵢ}'),
F('Feasibility: every negative needs a witness. Assign it only to max V(w).'),
F('If a negative has no witness, the partition is infeasible for these labels.')],
'''افراز را ورودی معلوم مسئله می‌گیریم. تصویر روی یک بلوک با حذف حروف بیرون آن ساخته می‌شود و رشتهٔ خالی نیز حفظ می‌شود. پذیرش جهانی AND است؛ پس هر مثبت باید در همهٔ عوامل پذیرفته شود، ولی برای رد هر منفی کافی است یک عامل آن را رد کند. برای هر عامل، تصویر مثبت‌ها تعهد مثبت ایجاد می‌کند. شاهد یک منفی، عاملی است که تصویر آن منفی جزو این تعهدها نباشد. وجود شاهد برای تک‌تک منفی‌ها شرط لازم و کافی امکان‌پذیری نمونه است. ضرورت از اجبار پذیرش در همهٔ عوامل می‌آید؛ برای کفایت، خودِ مجموعهٔ متناهی مثبت‌های محلی را زبان عامل می‌گیریم. در برنامه، شاهد با بزرگ‌ترین اندیس انتخاب می‌شود تا سیاست ثابت باشد. اگر شاهد وجود نداشته باشد، مسئلهٔ هزینه را با تجزیهٔ ناممکن مخلوط نمی‌کنیم.''',60,'Original §2; Appendix 16')

add('What cheaper means',[
E('WG=Global work,     WS=Split work,     H=selection work'),
F('Wref counts declared loop events in one fixed sparse RPNI implementation.'),
F('Split includes projection and negative allocation. Both runs are sequential.'),
F('A successful union scans every retained state record of the candidate.'),
F('Library internals and explicit product construction are outside the count.'),
F('The cost guarantee concerns this contract. Target recovery is a separate question.')],
'''بهتر بودن را به تعداد رویدادهای مشخص در پیاده‌سازی مرجع محدود می‌کنیم. عبور روی حالت، انتقال و حرف، ایجاد حالت و انتقال، تلاش ادغام، آزمون منفی و بازنگاشت قرمز شمرده می‌شوند. در Split هزینهٔ تصویرسازی و تخصیص منفی نیز حساب می‌شود. هزینهٔ انتخاب‌گر H نام دارد و در گواهی سود خالص وارد می‌شود. یک جزئیات تعیین‌کننده این است که هر اجتماع موفق، همهٔ رکوردهای نگه‌داشته‌شدهٔ حالت را می‌پیماید؛ کران پایین ما به همین پیاده‌سازی تخت وابسته است. مرتب‌سازی، هش، کپی رشته، تخصیص حافظه، حساب بیتی و دیگر عملیات داخلی کتابخانه‌ها رویداد جدا ندارند. خروجی Split نیز مجموعهٔ عوامل است؛ ساخت محصول صریح و کمینه‌سازی در هزینه نیست. بنابراین تضمین زمانی روی هر کامپیوتر یا پیاده‌سازی دیگر از این نتیجه به دست نمی‌آید.''',75,'Original §1; Extension §1; Appendix 15')

add('Q1: Recognizing the certified cost region',[
F('Check a proved structural rule, or compute sound static cost intervals.'),
E('LG≤WG≤UG,     LS≤WS≤US'),
E('H+US<LG  or  H+UG<LS'),
F('The net-certified region contains exactly the inputs passing a net guard.'),
F('All checks use input features before learning. UNKNOWN is an explicit outcome.'),
F('This is a sufficient certificate boundary, not the boundary of all true winners.')],
'''پاسخ دقیق محور اول این است که عضویت در ناحیهٔ صدور گواهیِ همین الگوریتم قابل تشخیص است. ابتدا قواعد ساختاری اثبات‌شده بررسی می‌شوند. اگر جواب ندادند، از پیشوندها و نمونه‌های محلی، کران‌های معتبر هزینه را می‌سازیم و هزینهٔ همین استخراج ویژگی را هم می‌شماریم. اگر یکی از دو نامساوی سخت برقرار باشد، گواهی خالص صادر می‌شود. تمام این بررسی‌ها متناهی‌اند و هیچ ادغامی برای یادگیری انجام نمی‌شود. بنابراین می‌توانیم دقیقاً بگوییم این ورودی از آزمون‌های گواهی ما عبور می‌کند یا خیر. ولی ناحیهٔ حاصل بزرگ‌ترین ناحیهٔ ممکن نیست. اگر کران‌ها هم‌پوشانی داشته باشند یا هزینهٔ تشخیص سود را بپوشاند، ممکن است برندهٔ واقعی وجود داشته باشد و گواهی فعلی آن را پیدا نکند. چنین ورودی‌ای نامعلوم است، نه اثباتاً غیرقابل تصمیم.''',75,'Original §10; Extension §§2–5,8')

add('Q2: A proved choice before training',[
E('H+US<LG  ⇒  H+WS≤H+US<LG≤WG'),
F('Choose Split. Selection plus Split beats always running Global.'),
E('H+UG<LS  ⇒  H+WG≤H+UG<LS≤WS'),
F('Choose Global. Selection plus Global beats always running Split.'),
F('A pipeline-only certificate omits H and makes a weaker claim.'),
F('Sample consistency is guaranteed; equal output languages need a separate proof.')],
'''محور دوم با زنجیرهٔ نامساوی پاسخ می‌گیرد. اگر بدترین کران Split، همراه با هزینهٔ تشخیص، از کمترین کار اجتناب‌ناپذیر Global کمتر باشد، هزینهٔ واقعی Split هم همراه H قطعاً از Global کمتر است. جهت مقابل دقیقاً مشابه است. پس لازم نیست هزینهٔ دقیق دو اجرای کامل را از پیش حساب کنیم؛ جدایی کران‌ها کافی است. خودِ برنده بودن یک مسیر با سودمند بودن انتخاب‌گر تفاوت دارد و گواهی‌های ضعیف‌تر را جدا گزارش می‌کنیم. در دامنهٔ امکان‌پذیر، هر دو خروجی با برچسب‌های نمونه سازگارند. ادعای اصلی فعلی انتخاب برندهٔ هزینه است. در بعضی خانواده‌ها برابری زبان خروجی نیز اثبات شده و آن را به‌عنوان نتیجهٔ اضافی مشخص می‌کنیم؛ در تمام موارد تازه این نتیجه برقرار نیست. گسترش شرط برابری، سؤال مرحلهٔ بعد خواهد بود.''',90,'Extension §§3–4; Appendix 17')

add('Two certified Global families',[
F('Old rule: all observed symbols lie in one block, with at least one positive.'),
E('WS−WG=Π+4(k−1);     net gain requires H<Π+4(k−1)'),
F('New rule: S⁺={a}, ε∈S⁻; further consistent negatives may use other blocks.'),
E('WG=25,     WS=25+Π+4(k−1)'),
F('Example: blocks {a},{b}; S⁺={a}, S⁻={ε,b}.'),
E('H+WG=12+25=37<41=WS')],
'''برای Global دو خانوادهٔ روشن داریم. در قاعدهٔ قبلی، همهٔ حروف مشاهده‌شده در یک بلوک‌اند. اجرای عامل فعال عین Global است و عوامل غیرفعال فقط رشتهٔ خالی را می‌آموزند؛ هزینهٔ هر کدام چهار واحد است. آماده‌سازی و این عوامل، اختلاف دقیق روی اسلاید را می‌دهند. در خانوادهٔ جدید، تنها مثبت یک حرف است و رشتهٔ خالی منفی است. اولین ادغام ریشه و حالت بعد از آن حرف، ریشه را نهایی می‌کند و منفیِ رشتهٔ خالی بلافاصله آن را رد می‌کند. حالت آبی ارتقا می‌یابد و اجرا تمام می‌شود؛ هزینهٔ Global دقیقاً بیست‌وپنج است. در Split نیز رشتهٔ خالی به عامل فعال اختصاص می‌یابد و همان اتفاق می‌افتد. منفی‌های دیگر می‌توانند از بلوک‌های دیگر باشند. برای مثال، دوازده به‌اضافهٔ بیست‌وپنج از چهل‌ویک کمتر است. این خانواده هم منفی اثرگذار دارد و هم خروجی برابر؛ اثباتش در پیوست است.''',90,'Original §4; Extension §6; Appendices 25–26')

add('Split certificates with incomplete positives',[
F('Cn contains all words with n copies of a and n copies of b.'),
F('Start with Cn, remove positives, and use the prefixes that actually remain.'),
E('Q=positive prefixes,     N=|Q|,     T=|{t∈Q : xt∈Q}|'),
F('Here x is the first blue symbol. Merging ε with x forces every pair t,xt.'),
F('These pairs form a forest. The first candidate needs at least T unions.'),
F('Each union visits N records. This lower bound also survives a rejected candidate.')],
'''برای Split دیگر تعداد پیشوندها را فقط از خانوادهٔ کامل فرض نمی‌کنیم؛ پیشوندهای دادهٔ باقی‌مانده را می‌سازیم. x کوچک‌ترین حرفی است که مثبت با آن شروع می‌شود و اولین حالت آبی خواهد بود. اگر ریشه و x یکی شوند، هر دو مسیر t که از این دو مبدأ تعریف شده‌اند باید مقصد یکسانی بدهند. بنابراین پیشوندهای t و xt مجبور به یکی شدن‌اند. گراف این جفت‌ها دور ندارد: هر رأس حداکثر یک امتدادِ اضافه کردن x در ابتدا و یک پیشین دارد و طول در جهت امتداد زیاد می‌شود. پس تعداد یال‌ها کران پایین تعداد کاهش کلاس‌هاست. هر اجتماع N رکورد را می‌بیند و حداقل NT کار داریم. نکتهٔ مهم این است که خارج‌قسمت پیش از آزمون منفی ساخته می‌شود؛ حتی اگر منفی آن را رد کند، هزینه قبلاً پرداخت شده است. این کران به کامل بودن یا متوازن بودن داده وابسته نیست؛ خانوادهٔ متوازن فقط برای بیان قضیهٔ حذف استفاده می‌شود.''',90,'Extension §2, Theorem A; Appendices 18–19')

add('Guaranteed deletion budgets',[
F('Ordered blocks {a},{b},{c}; the only negative is c. Remove any r members of Cn.'),
T(['n','Complete positives','Any deletions up to','Positives remaining'],[
['3','20','2','18'],['4','70','7','63'],['5','252','22','230'],['6','924','71','853']],[100,310,340,350]),
F('Every subset within these budgets has a net Split certificate and equal outputs.'),
F('These are sufficient worst-case budgets. Actual-prefix checks can cover more.')],
'''این جدول یک نتیجهٔ بدترین حالت است و صرفاً خلاصهٔ آزمایش نیست. از خانوادهٔ بیست عضوی می‌توان هر یک یا هر دو مثبت را حذف کرد و همچنان سود خالص Split را تضمین کرد. برای هفتاد عضو، هر مجموعهٔ حداکثر هفت عضوی قابل حذف است؛ دو ردیف بعد نیز همین معنا را دارند. فرض‌های جدول دقیق‌اند: سه بلوک تک‌حرفی با نشانگر در بلوک آخر، منفی فقط c، و مثبت‌های باقی‌مانده زیرمجموعهٔ همان خانواده. اثبات می‌گوید حذف r تریس حداکثر دو n r پیشوند و حداکثر چهار n r یال از جنگل جفت‌ها را حذف می‌کند. با این زیان، هنوز کران پایین Global از هزینهٔ Split و تشخیص بیشتر می‌ماند. در این خانواده برابری خروجی نیز حفظ می‌شود. تعدادهای جدول حداکثر واقعی حذف مجاز نیستند؛ شرایط کافی محافظه‌کارانه‌اند. برای ورودی مشخص، شمارش پیشوندهای واقعی می‌تواند خیلی بیشتر از این مقدار را گواهی کند.''',90,'Extension §5, Theorem C; Appendices 22–24')

add('A five-of-six positive example',[
E('S⁺={abab, abba, baab, baba, bbaa},     S⁻={c}'),
F('The complete n=2 family is missing aabb. Blocks are {a},{b},{c}.'),
E('N=16,     T=6,     H=142'),
E('WS=124,     WG≥269'),
E('H+WS=266<269≤WG'),
F('The decision is made before training. Subsequent Global work is 458.')],
'''برای اینکه تصمیم روی دادهٔ ناقص ملموس باشد، از شش تریس n دو، aabb را حذف کنید. پنج مثبت روی اسلاید باقی می‌مانند. تعداد پیشوندها شانزده و تعداد جفت‌های اجباری شش است. تمام هزینهٔ بررسی ساختار و استخراج ویژگی صد‌وچهل‌ودو واحد می‌شود. هزینهٔ Split با دو عامل تک‌حرفی و عامل نشانگر دقیقاً صدوبیست‌وچهار است. از هزینه‌های جدا و اجباریِ ساخت، اولین نامزد، مرز پایانی و بازنگاشت، کران پایین دویست‌وشصت‌ونه برای Global به دست می‌آید. پس حتی بدون اجرای Global، دویست‌وشصت‌وشش کمتر از دویست‌وشصت‌ونه است. بعداً اجرای مرجع هزینهٔ چهارصد‌وپنجاه‌وهشت را نشان می‌دهد؛ این فقط کنترل تطابق است. اگر به عدد واقعی اجرا برای انتخاب وابسته می‌شدیم، دیگر تصمیم پیش از یادگیری نبود. در این مثال برابری زبان دو خروجی هم از شرط منفی نشانگر نتیجه می‌شود.''',90,'Extension §§2–5; incomplete_net_equal_certificate.json')

add('Split cost with effective negatives',[
F('Use all 20 positives in C3 and negatives {ε,c}.'),
F('The negative ε rejects merges that make the root final.'),
E('H=530,     WS≤594,     WG≥3109'),
E('H+WS≤1124<3109≤WG'),
F('The quotient-cost lower bound is paid even when a candidate is rejected.'),
F('This is a net cost certificate. Equal output languages are not asserted here.')],
'''اکنون منفی‌ای اضافه می‌کنیم که واقعاً جلوی بعضی ادغام‌ها را می‌گیرد: رشتهٔ خالی. مثبت‌ها تمام بیست عضو خانوادهٔ n سه هستند و c هم منفی باقی می‌ماند. هزینهٔ تشکیل نامزدها پیش از تست منفی پرداخت می‌شود، بنابراین کران مبتنی بر پیشوندها هنوز معتبر است. برای عوامل دارای منفی، به‌جای فرض فروپاشی یک‌مرحله‌ای، کران عمومی تعداد نامزدها و هزینهٔ ادغام را استفاده می‌کنیم. انتخاب‌گر پانصدوسی واحد کار می‌کند، کران بالای Split پانصدونودوچهار و کران پایین Global سه‌هزاروصدونه است. پس سود خالص ثابت می‌شود. این نمونه نشان می‌دهد قاعدهٔ هزینه از منفیِ بی‌اثر فراتر رفته است. ولی از این نامساوی، برابری دو زبان به دست نمی‌آید. آن ادعا را جدا نگه می‌داریم؛ حتی اگر برای یک نمونهٔ آزموده‌شده خروجی‌ها برابر باشند، بدون قضیهٔ مناسب تعمیم نمی‌دهیم.''',90,'Extension §§2–3,7; Appendix 27')

add('Cost and output equality are separate',[
F('Current task: certify the lower-work pipeline under the Wref contract.'),
F('Some certificates also prove equal languages. Cost-only certificates do not.'),
F('Counterexample: remove aaabbb from C3; negatives are {bbb,c}.'),
F('Global accepts ε, while Split rejects ε. Both remain sample-consistent.'),
F('Equality for broader incomplete samples with effective negatives remains future work.')],
'''در جمع‌بندی ادعاها باید دقت کنیم که مسئلهٔ فعلی ما هزینه است. اگر گواهی فقط هزینه را ثابت کرده باشد، همان را اعلام می‌کنیم. یک مثال نقض مشخص نشان می‌دهد اضافه کردن ادعای عمومیِ برابری غلط است: از خانوادهٔ n سه، aaabbb را حذف کنید و منفی‌ها را bbb و c بگیرید. گواهی هزینهٔ Split برقرار است، ولی خروجی Global رشتهٔ خالی را می‌پذیرد و خروجی Split رد می‌کند. این تناقض با سازگاری نمونه نیست، چون رشتهٔ خالی در این نمونه برچسب نخورده است. منفی bbb در عامل a تصویر رشتهٔ خالی ایجاد می‌کند و آن عامل باید آن را رد کند. متفاوت بودن زبان‌ها هم به‌تنهایی ثابت نمی‌کند کدام به هدف واقعی نزدیک‌تر است. بنابراین برابری را شرط اجباری ادامهٔ پژوهش هزینه نمی‌گذاریم؛ آن را یک سؤال مستقل برای مرحلهٔ بعد می‌گذاریم، در کنار نتایج برابری‌ای که قبلاً برای خانواده‌های خاص ثابت شده‌اند.''',75,'Extension §7; quality_counterexample_models.json')

add('Progress on the two original questions',[
F('Q1 achieved: an explicit, executable boundary for our sufficient certificates.'),
F('Q2 achieved: sound pre-training cost choices on every input that passes a guard.'),
F('Coverage now includes incomplete positives and some merge-rejecting negatives.'),
F('Still open: overlapping bounds, uncovered structures, and selection overhead.'),
F('Next cost work: tighten bounds and enlarge the certified region.'),
F('There is no justified percentage of all possible inputs covered.')],
'''از دو محور اصلی چه مقدار جلو رفته‌ایم؟ محور اول برای ناحیهٔ گواهی‌های خودمان انجام شده است: ورودی را بررسی می‌کنیم و دقیقاً می‌گوییم آیا گواهی قابل اعمال است. محور دوم هم داخل همین ناحیه انجام شده است: جهت هزینه را پیش از یادگیری با اثبات تعیین می‌کنیم و برای سود خالص هزینهٔ تشخیص را می‌پردازیم. دامنه از خانوادهٔ کامل به برخی زیرمجموعه‌ها، مثبت‌های نامتوازن و منفی‌های اثرگذار گسترش یافته است. اما همهٔ ورودی‌ها حل نشده‌اند. کران‌های هم‌پوشان، ساختارهای پوشش‌نداده و هزینهٔ زیاد انتخاب‌گر هنوز نامعلوم تولید می‌کنند. درصدی برای پوشش تمام ورودی‌های ممکن نمی‌دهیم، چون توزیع یا فضای محدودِ مشخصی برای چنین درصدی تعریف نکرده‌ایم. کار لازم در محور هزینه، دقیق‌تر کردن کران‌ها و استخراج ویژگی ارزان‌تر است. ممیزی مستقل هم تطبیق برنامه و اثبات را کنترل می‌کند؛ جای اثبات را نمی‌گیرد.''',90,'Original §10; Extension §8')

add('Next research question: output equality',[
F('For incomplete positives and effective negatives, which input conditions ensure'),
E('L(Global)= ⋂ᵢ πᵢ⁻¹(Lᵢ)?'),
F('Find conditions that can be checked before training, then prove their sufficiency.'),
F('Use the unequal-output counterexample to identify the missing assumptions.'),
F('Continue cost certification independently; equality is an additional research goal.')],
'''سؤال پژوهشی مرحلهٔ بعد را اینجا نگه می‌داریم: برای مثبت‌های ناقص و منفی‌های اثرگذار، چه شرطی روی خودِ ورودی کافی است تا زبان خروجی Global و محصول مدل‌های محلی برابر شود؟ جواب باید پیش از یادگیری قابل بررسی باشد و اثبات کافی بودن داشته باشد. از مثال نقض شروع می‌کنیم تا بفهمیم کدام فرض در تعمیم قبلی کم بوده است. از طرف دیگر، پژوهش انتخاب برندهٔ هزینه ادامه پیدا می‌کند و منتظر حل عمومی برابری نمی‌ماند. اگر یک ورودی فقط گواهی هزینه داشته باشد، همان ادعا را شفاف گزارش می‌کنیم. پس نتیجهٔ ارائه این است که برای دو محور اولیه یک چارچوب عملی و اثبات‌شدهٔ مشروط داریم، پوشش آن را بزرگ‌تر کرده‌ایم، و دو مسیر بعدی روشن‌اند: گسترش پوشش هزینه و بررسی مستقل شرط‌های برابری خروجی.''',75,'Extension §7; research question, no general theorem claimed')

# Proof appendix, outside the 18-minute main talk.
add('Appendix: exact algorithm and work contract',[
F('Positive partial trie; missing transitions reject; initial red set {ε}.'),
F('Least shortlex blue state, then shortlex red states. Final classes use OR.'),
F('Keep a quotient iff every negative rejects; promote only after all candidates fail.'),
F('Count input, states/edges, fringes, candidates, folds, negative scans and remaps.'),
F('H additionally counts prefix/projection/attribution/local-feature loops.'),
F('Library internals, diagnostics, explicit products and elapsed time are excluded.')],
'''پیاده‌سازی با درخت مثبتِ جزئی شروع می‌کند؛ انتقال تعریف‌نشده رد می‌کند. نمایندهٔ کلاس کوچک‌ترین پیشوند در ترتیب طول و سپس واژه‌نامه است. آبی و قرمز با همین ترتیب انتخاب می‌شوند و نهایی بودن کلاس OR اعضاست. فقط خارج‌قسمتی نگه داشته می‌شود که تمام منفی‌ها را رد کند. هر اجتماع، همهٔ رکوردهای اولیهٔ همان نامزد را می‌بیند و تا بازسازی رکوردی حذف نمی‌شود. شمارندهٔ H تمام حلقه‌های استخراج ویژگیِ واقعاً طی‌شده را حساب می‌کند. هزینه‌های داخلی کتابخانه، تشخیص‌های آزمایشی و ساخت محصول صریح در قرارداد نیستند. این فرض‌ها برای اعتبار همهٔ کران‌ها قابل مشاهده و لازم‌اند.''',proof='Original §1; Extension §1')

add('Appendix: feasibility and negative allocation',[
E('Pᵢ=πᵢ(S⁺),     V(w)={i:πᵢ(w)∉Pᵢ}'),
F('Necessity: Pᵢ⊆Lᵢ. If V(w)=∅, every factor must accept the negative projection.'),
F('Sufficiency: choose finite regular Lᵢ=Pᵢ. A witness rejects every negative.'),
F('Assign each negative to max V(w). Its assigned projection is outside local positives.'),
F('Any consistent local learners then produce a sample-consistent AND product.'),
F('The theorem allows empty sample sets and ε, with unbounded local state sizes.')],
'''هر زبان عامل که مثبت‌های جهانی را بپذیرد، مجبور است P_i را در خود داشته باشد. اگر تصویر یک منفی در تمام P_iها باشد، رد شدن آن ناممکن می‌شود و ضرورت ثابت است. اگر برای هر منفی شاهد داریم، انتخاب زبان متناهی P_i برای هر عامل همهٔ مثبت‌ها را می‌پذیرد و هر منفی در شاهد خود رد می‌شود؛ این کفایت است. تخصیص به بزرگ‌ترین شاهد با مثبت محلی تداخل ندارد. هر یادگیرندهٔ محلیِ سازگار، تمام مثبت‌های جهانی را در همهٔ عوامل قبول و هر منفی را در عامل تخصیص‌یافته رد می‌کند. برای تعداد حالت محلی کران نگذاشته‌ایم. منفی کردن همهٔ تصویرهای یک منفی از این اثبات نتیجه نمی‌شود.''',proof='Original §2; Extension §1')

add('Appendix: termination and general upper bounds',[
F('Potential q−r decreases on promotion and every kept blue/red merge.'),
E('Iterations≤N−1,     fringes≤N,     attempts≤N(N−1)/2'),
E('I=M+p+2N−1,     E=N−1,     D=∑w∈S⁻(|w|+1)'),
E('F(N,E)=NE+N²+3N+E'),
E('I≤W≤U=I+N(3N+E)+N(N−1)[1+F(N,E)+D]/2'),
F('A fold has ≤N−1 unions, ≤N closure passes and 2N+E reconstruction work.')],
'''اگر q تعداد حالت‌های فعلی و r تعداد کلاس‌های قرمز باشد، پتانسیل q منهای r ابتدا N منهای یک است. ارتقا آن را یک واحد کم می‌کند؛ ادغام آبی با قرمز هم حداقل یک واحد کم می‌کند و اجتماع‌های اضافی آن را زیاد نمی‌کنند. پس تعداد دور و مرز کران می‌خورد. در دور صفرمبنا t تعداد قرمز حداکثر t به‌اضافهٔ یک است، بنابراین جمع تعداد نامزدها عدد مثلثی است. هر اجتماع حداکثر N رکورد را می‌بیند و تعداد اجتماع‌ها حداکثر N منهای یک است. هر دور مولد بستن قطعیت دست‌کم یک اجتماع دارد؛ با دور پایانی، N گذر کران امن است. جمع نگاشت و بازسازی هم دو N و E است. کران F عمداً محافظه‌کارانه است. مرزها، بازنگاشت قرمز و آزمون منفی‌ها را جدا اضافه می‌کنیم و U به دست می‌آید. برای N یک، هزینه دقیقاً I به‌اضافهٔ دو است.''',proof='Original §3; Extension §3')

add('Appendix: the prefix-pair forest proof',[
E('Q=positive prefixes; x=min first symbols; T=|{t∈Q:xt∈Q}|'),
F('The first candidate merges ε and x. Defined paths t force t~xt.'),
F('Each pair extends length by one. Each vertex has at most one predecessor and successor.'),
F('The obligation graph is a forest with T edges, requiring T class reductions.'),
F('Any coarser deterministic quotient needs at least as many reductions.'),
E('First-candidate union visits ≥ NT, even if the negative test rejects it')],
'''برای هر t شمرده‌شده، مسیر t از ریشه به حالت t و از حالت x به حالت xt در درخت تعریف شده است. یکی شدن مبدأها در خارج‌قسمت قطعی، یکی شدن مقصدها را اجبار می‌کند. هر یال گراف جفت‌ها، یک x به ابتدای کلمه اضافه می‌کند. طول زیاد می‌شود و هر رأس حداکثر یک پیشین و یک پسین دارد؛ پس مؤلفه‌ها مسیر و گراف جنگل است. جنگلی با T یال برای یکی شدن دو سر همهٔ یال‌ها، T کاهش کلاس لازم دارد. خارج‌قسمت قطعی ممکن است اجتماع بیشتری بخواهد، ولی کمتر نمی‌تواند. چون اولین نامزد از N کلاس مجزا شروع می‌کند، حداقل T اجتماع موفق و NT بازدید رکورد دارد. آزمون منفی بعد از ساخت خارج‌قسمت است و رد شدن نامزد این هزینه را پس نمی‌گیرد.''',proof='Extension §2, Theorem A')

add('Appendix: disjoint mandatory Global events',[
E('δ=0 if S⁻=∅; δ=1 if ε∈S⁻; otherwise δ=2'),
F('Initial fringe: 2N+E. Fold map/rebuild: 2N+2E. Candidate: 1. Negatives: ≥δ.'),
E('L₀=I+NT+4N+3E+1+δ'),
F('A distinct terminal fringe costs ≥2+|A|, where A is positive symbol support.'),
E('LG=L₀+2+|A|≤WG'),
F('Add one red-remap event only when the first candidate is proved kept.')],
'''این جمع فقط هزینه‌های جدا را کنار هم می‌گذارد. ساخت اولیه I با مرز و تا شدن هم‌پوشانی ندارد. در اولین نامزد، NT مربوط به اجتماع‌هاست؛ نگاشت اولیه و بازسازی حالت‌ها دو N دیگر و حداقل یک گذر بستن به‌اضافهٔ بازسازی انتقال‌ها دو E دیگر دارند. مرز اولیه نیز دو N و E است. تلاش یک واحد و اولین بازدید منفی حداقل دلتا هزینه دارد. اگر منفی تهی باشد، فقط کلمه را تضمین می‌کنیم؛ وگرنه حداقل یک حرف هم دیده می‌شود. چون اولین مرز آبی داشته، مرز پایانی رویدادی جداست. تمام برچسب‌های مثبت در دست‌کم یک یال باقی می‌مانند و دست‌کم یک حالت داریم؛ پس هزینهٔ پایانی حداقل دو به‌اضافهٔ اندازهٔ پشتیبان الفباست. بازنگاشت قرمز فقط با اثبات نگه‌داشته شدن نامزد مجاز است.''',proof='Extension §2, Equation (1)')

add('Appendix: exact unary and Split work',[
E('dᵣ=1 for r=1; dᵣ=2 for r≥2'),
E('Fold=2(r+1)+r(r+1)+dᵣr+r=r²+(4+dᵣ)r+2'),
E('V(m,s,r)=m+s+r²+(9+dᵣ)r+10'),
E('v(1)=23;     v(n)=n²+12n+11 for n≥2'),
E('Π=M+M⁻+k(p+2z),     WS=Π+∑ᵢWi'),
F('Use exact unary/no-candidate cases; use the general upper bound for other local runs.')],
'''در عامل تک‌حرفی بدون منفی، بیشترین طول مثبت r است و درخت زنجیره‌ای r به‌اضافهٔ یک حالت دارد. اولین ادغام تمام زنجیره را می‌خواباند. در r یک، گذر بستن فقط تأیید می‌کند. برای r حداقل دو، یک گذر مولد در ترتیب طول همهٔ تضادهای زنجیره را حل و گذر دوم نبود تضاد را تأیید می‌کند. r اجتماع، هر کدام روی r به‌اضافهٔ یک رکورد داریم. هزینهٔ ساخت، مرز اولیه و پایانی، یک نامزد و یک بازنگاشت را اضافه می‌کنیم تا V دقیق به دست آید. این فرمول مجموعه‌های مثبت تک‌حرفی با چند طول و رشتهٔ خالی را هم پوشش می‌دهد. در عامل دارای منفی اثرگذار، این فرمول را بی‌دلیل استفاده نمی‌کنیم و سراغ کران عمومی می‌رویم. آماده‌سازی Split یک گذر حرفی، یک گذر بلوکی برای هر کلمه و یک گذر بلوکی اضافی برای هر منفی دارد.''',proof='Extension §3, Equations (2)–(4)')

add('Appendix: existing equality certificate',[
F('If every assigned local negative contains a symbol outside local positive support Ai,'),
F('then every global negative also contains a symbol outside positive support A.'),
F('No quotient invents labels. Every candidate is kept globally and locally.'),
F('No promotion occurs; red remains the root. A reachable nonroot state would create blue.'),
E('Global=A*,     local i=Ai*,     ⋂ᵢπᵢ⁻¹(Ai*)=A*'),
F('This covers incomplete marker families. It is not a theorem for all effective negatives.')],
'''این یک نتیجهٔ اضافیِ موجود است و با سؤال بازِ مرحلهٔ بعد فرق دارد. فرض کنید هر منفی محلیِ اختصاص‌یافته حرفی بیرون پشتیبان مثبت همان عامل داشته باشد. چون بلوک‌ها جدا هستند، آن حرف در مثبت‌های جهانی هم نیست. هیچ ادغامی برچسب تازه نمی‌سازد؛ پس همهٔ نامزدها منفی‌ها را رد می‌کنند و نگه داشته می‌شوند. ارتقا نداریم و قرمز فقط کلاس ریشه است. هر کلاس همچنان قابل دسترس است. اگر در پایان کلاس غیرریشه‌ای باقی بماند، اولین یال خروجی از ریشه در مسیر رسیدن به آن، آبی ایجاد می‌کند؛ تناقض. بنابراین یک حالت نهایی و حلقه‌های دقیقاً حروف دیده‌شده داریم. هر مجموعهٔ مثبت محلی ناتهی است چون مثبت جهانی ناتهی است. ستارهٔ پشتیبان‌های محلی در محصول دقیقاً ستارهٔ پشتیبان جهانی می‌شود. اگر مثبت جهانی تهی باشد، هر دو خروجی زبان تهی‌اند و جدا بررسی می‌شود.''',proof='Extension §4, Theorem B')

add('Appendix: deletion losses',[
E('P=C(2n,n), N₀=C(2n+2,n+1)−1, T₀=C(2n+1,n)−1'),
F('N₀ sums all balanced prefixes; T₀ sums prefixes with one fewer x capacity.'),
F('Deleting r words removes at most 2nr prefix nodes and at most 4nr forest edges.'),
E('NL=max(2n+1,N₀−2nr)≤N≤NU=N₀−r'),
E('TL=max(1,T₀−4nr)≤T'),
F('Every removed word loses its full-length leaf. A remaining word preserves 2n+1 prefixes.')],
'''برای خانوادهٔ کامل، تعداد پیشوندها جمع ضرایب دوجمله‌ای روی شمار a و b از صفر تا n است. دو بار هویت چوب هاکی N صفر را می‌دهد. برای جفت‌ها، شمار x در t حداکثر n منهای یک است؛ همان جمع با این محدودیت T صفر را می‌دهد. هر تریس حذف‌شده حداکثر دو n پیشوند ناتهی دارد، بنابراین زیان کل پیشوندها حداکثر دو n r است. هر رأس در جنگل حداکثر درجهٔ دو دارد؛ پس حداکثر چهار n r یال از بین می‌رود. دست‌کم یک مثبت باقی مانده و طول آن دو n است، بنابراین دو n به‌اضافهٔ یک پیشوند داریم و جفت ریشه و اولین حرف هم باقی است. هر مثبت حذف‌شده نیز برگ متمایز طول کاملش را از دست می‌دهد و کران بالای N را می‌دهد. تقارن دو حرف باعث می‌شود تغییر اولین حرف آبی پس از حذف، این کران را خراب نکند.''',proof='Extension §5, Theorem C')

add('Appendix: deletion overhead and cost bounds',[
F('Proper nonempty subset: p=P−r and M=2np. The failed full-family test is charged.'),
E('H=2M+6p+2N+4n+32≤HU=2M+6p+2NU+4n+32'),
E('WS=M+3p+11+2v(n)'),
E('LB=M+p+2NL−1+NL·TL+7NL+5≤WG'),
E('HU+WS<LB  ⇒  net Split for every such subset'),
F('The marker condition gives equal outputs and permits the first red-remap event.')],
'''برای زیرمجموعهٔ ناتهی و درست، ابتدا اعتبارسنجی و آزمون خانوادهٔ کامل انجام شده و هزینهٔ شکست آن آزمون هم پرداخت می‌شود. جمع دقیق H شامل ساخت پیشوندهای جهانی، تصویرسازی کلمه و حرف و بلوک، انتخاب شاهد، شمارش جفت‌ها و ساخت ویژگی‌های عوامل است. مثبت‌های محلی همچنان فقط a به توان n، b به توان n و رشتهٔ خالی هستند؛ بنابراین هزینهٔ Split دقیق است. در کران پایین Global، N و T را با کران‌های پایینشان جایگزین می‌کنیم و برای H از کران بالای N استفاده می‌کنیم. ضریب اضافهٔ پنج در LB از مرز پایانی با حداقل چهار رویداد و اولین بازنگاشت قرمز است؛ منفی نشانگر نگه داشتن اولین نامزد را تضمین می‌کند. اگر نامساوی آخر برقرار باشد، همهٔ زیرمجموعه‌های با همان n و r پوشش داده می‌شوند، نه فقط مسیر حذف آزموده‌شده.''',proof='Extension §5, Equations (5)–(9)')

add('Appendix: uniform deletion budget proof',[
E('D(r)=C+[−4nN₀−2nT₀−14n+10]r+8n²r²'),
E('C=N₀T₀+7N₀−(4n+8)P−4n−39−2v(n)'),
F('Within the unclamped range, D(r)=LB−HU−WS.'),
E('r≤T₀/(4n) ⇒ D′(r)≤2nT₀−4nN₀−14n+10<0'),
F('Thus D(R)>0 proves every 1≤r≤R. Check the unclamped premises at R.'),
E('D(2)=426 for n=3; D(7)=2085 for n=4')],
'''ممکن است سؤال شود چرا بررسی انتهای بازه برای همهٔ حذف‌های کمتر کافی است. وقتی کران‌های پایین هنوز با تابع ماکسیمم قطع نشده‌اند، اختلاف LB منهای HU و هزینهٔ Split دقیقاً چندجمله‌ای درجه‌دو روی اسلاید است. در r حداکثر T صفر تقسیم بر چهار n، مشتق از عبارت نمایش‌داده‌شده بیشتر نیست. چون T صفر از N صفر کمتر است و n مثبت است، این عبارت منفی است. پس اختلاف در کل بازه نزولی است. برای بودجه‌های جدول، در انتهای بازه هم N پایین و T پایین هنوز در ناحیهٔ خطی‌اند و اختلاف مثبت است؛ بنابراین تمام rهای کوچکتر نیز اختلاف مثبت دارند. جایگذاری صحیح اعداد برای n سه و دو حذف، چهارصدوبیست‌وشش و برای n چهار و هفت حذف، دوهزاروهشتادوپنج می‌دهد. دو ردیف بعد به همین روش است و محاسبات بازتولیدپذیر همراه بسته‌اند.''',proof='Extension §5; deletion_budget.py')

add('Appendix: the original Global rule',[
F('k>1, S⁺ nonempty, all observed symbols in one block Bj.'),
F('Active projection is identity. Inactive positives are {ε}, with no assigned negatives.'),
E('WS−WG=Π+4(k−1)'),
E('H=|Σ|+2k+p+z+M+M⁻'),
E('WS−WG−H=(k−1)p+(2k−1)z+2k−4−|Σ|'),
F('The active run equals Global; inactive ε factors impose its same outside-label restriction.')],
'''روی بلوک فعال تصویر هویت است. در هر بلوک غیرفعال، مثبت فقط رشتهٔ خالی است و تصویر هر منفی هم رشتهٔ خالی می‌شود، پس شاهد نیست. هر منفی فقط در عامل فعال شاهد دارد، چون برچسب‌های اصلی جدا هستند. در نتیجه داده، ترتیب و هزینهٔ عامل فعال عین Global است. هر عامل غیرفعال دو واحد ساخت و دو واحد مرز دارد؛ چهار واحد. با آماده‌سازی اختلاف دقیق هزینه به دست می‌آید. H از یک عبور روی بلوک‌ها و حروف الفبا، کلمات و حروف ورودی و دوباره آزمون بلوک‌های فعال حاصل می‌شود. کم کردن H از اختلاف، شرط عددی مستقیم را می‌دهد؛ مثبت بودن آن دقیقاً سود خالص همین شاخه است. Global برچسب خارج از مثبت‌ها اختراع نمی‌کند و عوامل رشتهٔ خالی همان محدودیت را اعمال می‌کنند، پس زبان‌ها برابرند.''',proof='Original §4')

add('Appendix: the new effective-negative Global rule',[
F('S⁺={a}, ε∈S⁻, k>1; all labels are consistent. Other negatives are unrestricted.'),
F('Merge root/a: ε becomes accepted, so the first shortlex negative rejects it.'),
E('WG=5 initialization +10 fringes +8 fold +1 candidate +1 negative=25'),
F('ε has a unique active-factor witness. That run also costs 25; inactive runs cost 4.'),
E('WS=25+Π+4(k−1),     L(Global)=L(Split)={a}'),
E('New-branch net guard: (2k−1)z+3k−6>|Σ|')],
'''درخت جهانی فقط ریشه و حالت نهایی a دارد. اولین ادغام هر دو را یکی و ریشه را نهایی می‌کند. رشتهٔ خالی اولین منفی در ترتیب طول است و بلافاصله نامزد را رد می‌کند؛ هیچ منفی دیگری در آن تلاش دیده نمی‌شود. آبی ارتقا می‌یابد و مرز بعدی پایان می‌دهد. جدول جمع هزینه روی اسلاید کامل است. در Split، رشتهٔ خالی فقط در عامل فعال شاهد است، چون در عوامل دیگر مثبت است. آن عامل نیز همان نامزد را با همان اولین منفی رد می‌کند. عوامل غیرفعال مثبت رشتهٔ خالی و منفی‌های ناتهی دارند؛ نامزدی امتحان نمی‌کنند و هرکدام چهار هزینه دارند. زبان هر دو مسیر دقیقاً تک‌عضوی a است. وقتی شاخهٔ جدید برسد، H نسبت به اسکن اولیه یک آزمون تک‌عضوی اضافه دارد. جایگذاری در شرط H کمتر از اختلاف، نامساوی آخر را می‌دهد. اگر شاخهٔ قبلی زودتر جواب دهد، هزینهٔ آزمون اضافی پرداخت نمی‌شود.''',proof='Extension §6, Theorem D')

add('Appendix: effective negatives and verification',[
E('C3, S⁻={ε,c}: N=69, T=34, H=530, LG=3109, US=594'),
E('H+US=1124<3109≤WG'),
F('Equality counterexample: C3 without aaabbb, negatives {bbb,c}; witness ε.'),
F('Extension audit: 3,119 case executions; 13,425 independent candidate checks.'),
F('Set-partition quotient oracle, independent learner, exact completed-product equivalence.'),
F('Finite checks supplement proofs. Full reports and reproducible code accompany the deck.')],
'''این نمونهٔ منفی اثرگذار با نامساوی پیش از اجرا گواهی هزینه می‌گیرد. اگر رشتهٔ خالی منفی باشد، در کران اولین اسکن فقط یک رویداد کلمه را تضمین می‌کنیم و بازنگاشت قرمز را بدون اثبات قبول نامزد اضافه نمی‌کنیم. همین احتیاط در مقدار سه‌هزاروصدونه رعایت شده است. مثال نقض برابری نیز ورودی و مدل‌های نهایی کامل در بسته دارد؛ شاهد فقط رشتهٔ خالی است. در ممیزی توسعه، ۳۱۱۹ اجرای مورد آزمون و ۱۳۴۲۵ نامزد مستقل کنترل شد. تمام ۲۱۸۷ برچسب‌گذاری کوچک دودویی، همهٔ زیرمجموعه‌های n دو، همهٔ حذف‌های یک و دو عضو در n سه، مسیرهای حذف و تغییرات منفی حضور دارند. پنج ورودی نامعتبر هم جدا رد شدند. این‌ها شواهد تطابق برنامه و اثبات‌اند؛ قضیه‌های نامتناهی از استدلال‌های ریاضی بخش‌های قبل می‌آیند، نه از تعداد آزمون‌ها.''',proof='Extension §§7–8; extension_audit_results.json')

add('Future work: equality beyond current families',[
F('Open question: which pre-training conditions ensure equal output languages'),
F('for incomplete positives together with effective negatives?'),
F('Find a sufficient structural condition and attack it with counterexamples.'),
F('Prove the condition without running either learner as part of selection.'),
F('Cost research continues: tighter bounds, cheaper feature extraction, fewer UNKNOWN cases.'),
F('No general equality result is claimed for the newly cost-certified region.')],
'''این آخرین اسلاید، سؤال پژوهشی مرحلهٔ بعد را صریح نگه می‌دارد: برای مثبت‌های ناقص همراه با منفی‌های اثرگذار، چه ویژگی قابل بررسیِ پیش از یادگیری، برابری زبان خروجی را تضمین می‌کند؟ کار بعدی یافتن یک شرط ساختاری کافی، حمله با مثال نقض و سپس اثبات است. این سؤال را با نتیجهٔ فعلی اشتباه نمی‌گیریم؛ برای تمام ناحیهٔ تازهٔ هزینه، برابری اثبات نشده است. در کنار آن، دو محور اصلی هزینه ادامه دارند: کران‌های دقیق‌تر و استخراج ویژگی کم‌هزینه‌تر تا تعداد نامعلوم‌ها کم شود. بنابراین پایان ارائه هم پیشرفت فعلی را حفظ می‌کند و هم مسئلهٔ باز را به‌روشنی از قضیه‌های اثبات‌شده جدا می‌کند.''',proof='Future research question; Extension §7')

slides[6]['blocks'][0]=F('Assume k>1. Single-block rule: all observed symbols lie in one block; S⁺≠∅.')
slides[6]['blocks'][2]=F('Effective-negative rule: S⁺={a}, ε∈S⁻; other consistent negatives are unrestricted.')
slides[7]['blocks'][0]=F('Cn (n≥1) contains all words with n copies of a and n copies of b.')
slides[7]['blocks'][1]=F('Take a nonempty subset of Cn and use the prefixes that actually remain.')
slides[16]['blocks'][0]=F('With q current states and r red classes, q−r decreases on promotion and kept merges.')
slides[16]['blocks'][2]=E('p=|S⁺|, M=∑w∈S⁺|w|; I=M+p+2N−1; E=N−1; D=∑w∈S⁻(|w|+1)')
slides[16]['blocks'][5]=F('Folds: ≤N−1 unions, ≤N passes, 2N+E extra work. Positive paths survive; kept models reject negatives.')
slides[16]['notes']='در این اسلاید p تعداد مثبت‌ها و M مجموع طول مثبت‌هاست؛ N تعداد حالت‌های درخت مثبت با ریشه است. '+slides[16]['notes']
slides[17]['blocks'][0]=E('Q=positive prefixes including ε; N>1; x=min first symbols; T=|{t∈Q:xt∈Q}|')
slides[18]['blocks'][0]=E('N>1; δ=0 if S⁻=∅; δ=1 if ε∈S⁻; otherwise δ=2')
slides[19]['blocks'][0]=F('Unary positives, no negatives, r≥1: m=volume, s=count, r=max length; dᵣ=1 if r=1, else 2.')
slides[19]['blocks'][5]=F('M,M⁻ are positive/negative volumes; p,z count their words. Other local runs use the general bound.')
slides[19]['notes']='در V، m مجموع طول مثبت‌های محلی، s تعداد آن‌ها و r بیشترین طول مثبت محلی است. '+slides[19]['notes']
slides[20]['blocks'][0]=F('Assume S⁺≠∅. Every assigned local negative contains a symbol outside local positive support Ai.')
slides[21]['blocks'][2]=F('For 1≤r<P, deleting r words loses at most 2nr prefix nodes and 4nr forest edges.')
slides[23]['blocks'][5]=E('n=3: D(2)=426; n=4: D(7)=2085; n=5: D(22)=12597; n=6: D(71)=17263')
assert len(slides)==28 and sum(s['seconds'] for s in slides)==1080
(root/'slides.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf8')
(out/'slide_content.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf8')
elapsed=0;text='# متن فارسی ارائه انتخاب Split یا Global\n\nاسلایدهای ۱ تا ۱۴ مسیر اصلی ۱۸ دقیقه‌ای‌اند. اسلایدهای ۱۵ تا ۲۸ پیوست اثبات‌اند. سؤال برابری زبان خروجی، کار پژوهشی مرحلهٔ بعد است و در پایان بخش اصلی و پایان کل پاورپوینت آمده است. زمان‌ها پیشنهادی‌اند و نیاز به تمرین دارند.\n\n'
timing=[]
for i,s in enumerate(slides,1):
    if i<=14:
        end=elapsed+s['seconds'];label=f'{elapsed//60:02}:{elapsed%60:02} تا {end//60:02}:{end%60:02}';elapsed=end
    else:label='پیوست خارج از زمان اصلی'
    timing.append(dict(slide=i,title=s['title'],seconds=s['seconds'],persian_words=len(s['notes'].split())))
    text+=f"## اسلاید {i} — {s['title']}\n\nزمان: {label}\n\n{s['notes']}\n\nارجاع اثبات: {s['proof']}\n\n"
(out/'Speaker_Notes_FA.md').write_text(text,encoding='utf8')
(out/'talk_timing.json').write_text(json.dumps(dict(main_seconds=1080,main_minutes=18,main_words=sum(t['persian_words'] for t in timing[:14]),slides=timing),ensure_ascii=False,indent=2),encoding='utf8')
print('Slides=28; main minutes=18; main Persian words=',sum(t['persian_words'] for t in timing[:14]))
