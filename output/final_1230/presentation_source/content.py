from pathlib import Path
import json
root=Path(__file__).parent
out=root.parents[1]/'output'/'final_1230'
F=lambda text,**kw:dict(kind='text',text=text,**kw)
E=lambda text,**kw:dict(kind='eq',text=text,**kw)
def T(headers,rows,widths,rowHeight=46):return dict(kind='table',headers=headers,rows=rows,widths=widths,rowHeight=rowHeight)
slides=[]
SOURCE='Research: research/Research_Proofs_EN.md and earlier bundled proofs. Fixed program: research/static_selector.py and research/rpni_work_reference.py. All cost claims use the declared W_ref event model.'
def add(title,blocks,notes,seconds=0,proof=''):
    slides.append(dict(title=title,blocks=blocks,notes=notes,seconds=seconds,proof=proof,source=SOURCE))

add('Split or Global RPNI?',[
 F('Cost certificates before learning'),F('Recognizable conditions and mathematically proved choices'),
 F('18-minute talk. Detailed proofs in the appendix.')],
'''مسئلهٔ ما این است که با افراز معلوم الفبا، قبل از یادگیری تشخیص بدهیم اجرای جداگانهٔ RPNI روی عوامل کم‌هزینه‌تر است یا اجرای جهانی. نتیجه را در دو سطح بیان می‌کنم: شرایط قابل بررسی برای صدور گواهی، و اثبات جهت هزینه برای ورودی‌ای که گواهی می‌گیرد. معیار هزینه و محدودیت دامنه در تمام ارائه صریح است. ابتدا نتیجهٔ اصلی را می‌گویم و بعد زنجیرهٔ اثبات را نشان می‌دهم.''',30,'Research §§1–7')

add('The research questions',[
 F('Q1. Can we recognize inputs that admit a proved decision before learning?',height=77),
 F('Q2. With a known partition, can we certify Split or Global as cheaper?',height=77),
 F('Yes on explicit certificate regions. Their membership tests are finite.'),
 F('New results include arbitrary-data bounds and an infinite two-trace family.'),
 F('Cheap exact selection for all unbounded inputs remains open.')],
'''سؤال اول دربارهٔ تشخیص ناحیهٔ تحت پوشش است: آیا خود الگوریتم قبل از یادگیری می‌فهمد که برای این داده گواهی دارد یا نه؟ سؤال دوم این است که وقتی گواهی داریم، آیا برندهٔ هزینه با اثبات معلوم است؟ پاسخ برای ناحیه‌های تعریف‌شده، بله است. این پاسخ، احتمال یا حدس مبتنی بر چند آزمایش نیست؛ نتیجهٔ نامساوی‌هایی است که تحت قرارداد برنامه ثابت می‌شوند. در گسترش تازه، یک کران پایین عمومی داریم که تلاش‌های ردشده را هم حساب می‌کند، کران بالای بهتری داریم و یک خانوادهٔ نامتناهیِ دو تریسی را از نامعلوم به سود خالص Split منتقل کرده‌ایم. با این حال انتخاب ارزان و دقیق برای تمام ورودی‌های با طول نامحدود هنوز نتیجهٔ اثبات‌شدهٔ ما نیست.''',60,'Research §§2–5,7')

add('Known partition and consistent local data',[
 E('Σ=B₁ ⊎ ··· ⊎ Bₖ,     Pᵢ=πᵢ(S⁺)'),
 F('Projection erases outside symbols and preserves order. Keep ε.'),
 E('V(w)={i : πᵢ(w)∉Pᵢ}'),
 F('An AND decomposition is feasible exactly when every negative has a witness.',height=77),
 F('Assign each negative only to max V(w). An empty V(w) means INFEASIBLE.',height=77)],
'''افراز مرتب الفبا را معلوم می‌گیریم. تصویر یک رشته روی بلوک، با حذف حروف بیرون آن و حفظ ترتیب ساخته می‌شود؛ رشتهٔ خالی نیز حذف نمی‌شود. پذیرش ترکیبی AND است. هر مثبت باید در تمام عوامل پذیرفته شود، ولی برای هر منفی فقط یک عاملِ ردکننده لازم است. مجموعهٔ تصویر مثبت‌ها در عامل i را Pi می‌نامیم. شاهد منفی، عاملی است که تصویر آن منفی جزو Pi نباشد. وجود شاهد برای تک‌تک منفی‌ها شرط لازم و کافی امکان‌پذیری نمونه است. ضرورت: اگر همهٔ تصویرها مثبتِ اجباری باشند، همهٔ عوامل منفی را می‌پذیرند. کفایت: خودِ مجموعهٔ متناهی Pi را زبان هر عامل بگیریم؛ هر مثبت پذیرفته و هر منفی در یک شاهد رد می‌شود. برنامه شاهد با بزرگ‌ترین اندیس را انتخاب می‌کند تا سیاست تخصیص ثابت باشد. نبود شاهد یک مسئلهٔ سازگاری است و آن را با باخت هزینه‌ای Split مخلوط نمی‌کنیم.''',80,'Research §1; Appendix 16')

add('The work contract',[
 F('Wref counts declared visits, candidate attempts and union scans.'),
 F('Partial DFAs reject undefined transitions. Ordering is fixed shortlex.'),
 E('Π=M+M⁻+k(p+2z)'),
 F('M,M⁻ are symbol volumes. p,z are distinct positive/negative word counts.'),
 F('Sorting, hashing, allocation and integer bit costs are excluded.'),
 F('Split includes Π. Explicit product construction is outside the count.')],
'''بهتر بودن را به تعداد رویدادهای تعریف‌شده در برنامهٔ مرجع محدود می‌کنیم. پیمایش حرف، حالت و یال، ساخت حالت و یال، تلاش ادغام، آزمون منفی و بازنگاشت قرمز شمرده می‌شوند. اتوماتا جزئی است و انتقال تعریف‌نشده رد می‌کند. ترتیب حروف و حالت‌ها ثابت است. در پیاده‌سازی اجتماع، هر اجتماع موفق همهٔ رکوردهای حالتِ همان تلاش را می‌پیماید؛ کران‌های ما از همین رفتار استفاده می‌کنند. هزینهٔ آماده‌سازی Split شامل تصویرسازی و تخصیص منفی است و فرمولش روی اسلاید آمده است. مرتب‌سازی، هش، نرمال‌سازی، کپی رشته، تخصیص حافظه، کنترل ثابت و حساب بیتی در این معیار رویداد جدا ندارند. خروجی Split مجموعهٔ عوامل است و ساخت محصول صریح و کمینه‌سازی حساب نشده‌اند. بنابراین این نتیجه ضمانت زمان واقعی روی هر کامپیوتر یا تمام نسخه‌های RPNI نیست؛ یک مقایسهٔ دقیق در قرارداد مشخص است.''',75,'Research §1; Appendix 15')

add('The pre-training selector',[
 E('LG≤WG≤UG,     LS≤WS≤US,     H=selection work'),
 F('Extract static sample features and compute proved cost intervals.'),
 E('H+US<LG  ⇒  net Split'),
 E('H+UG<LS  ⇒  net Global'),
 F('Separated intervals without paying H give a pipeline-only choice.'),
 F('Overlapping intervals give UNKNOWN. Exact equal costs give TIE.')],
'''الگوریتم انتخاب‌گر خودش RPNI را اجرا نمی‌کند. از تریس‌ها، پیشوندها، تصویرها و شاهدهای منفی ویژگی می‌گیرد و برای هزینهٔ هر مسیر بازهٔ معتبر می‌سازد. اگر H به اضافهٔ کران بالای Split از کران پایین Global کمتر باشد، هزینهٔ واقعی انتخاب‌گر و Split نیز قطعاً از Global کمتر است. اثبات فقط یک زنجیرهٔ نامساوی است: هزینهٔ Split از کران بالایش بیشتر نیست و هزینهٔ Global از کران پایینش کمتر نیست. قاعدهٔ متقارن Global نیز همین‌طور است. اگر بازه‌ها جدا باشند اما شکاف، هزینهٔ انتخاب‌گر را نپردازد، فقط جهت هزینهٔ دو مسیر را اعلام می‌کنیم و سود خالص نمی‌گوییم. هم‌پوشانی بازه‌ها UNKNOWN می‌دهد. این یعنی روش فعلی گواهی کافی ندارد، نه اینکه هیچ روش دیگری نمی‌تواند پاسخ بدهد. تساوی دقیق نیز نتیجهٔ جداست. عضویت در ناحیهٔ همین قواعد با پیمایش‌ها و نامساوی‌های متناهی قبل از یادگیری تشخیص داده می‌شود.''',90,'Research §§3–8; Original interval proof')

add('A lower bound for arbitrary negatives',[
 F('For N>1: N=prefix states, E=N−1, s=positive labels, T=prefix pairs.'),
 E('I=M+p+2N−1,     J(n)=n(n+1)/2−1'),
 E('C(N,T)=NT+J(N−T)'),
 E('Lany=I+C(N,T)+4N+3E+3+s+δ'),
 F('δ=0 for no negatives, 1 if ε is negative, 2 otherwise.'),
 F('The potential q−|Red| charges both accepted and rejected attempts.')],
'''گسترش اصلیِ کران پایین، کنار گذاشتن فرض پذیرش همهٔ ادغام‌هاست. N تعداد پیشوندهای مثبت، با احتساب ریشه، و E برابر N منهای یک است. پتانسیل را تعداد حالت‌های فعلی منهای تعداد قرمزها می‌گیریم. در ادغام پذیرفته‌شده، این پتانسیل حداقل یک کم می‌شود. در ارتقای آبی به قرمز هم یک کم می‌شود، ولی پیش از ارتقا حداقل یک ادغام آزمایشی انجام شده و هزینه‌اش پرداخت شده است. با شارژ کردن رتبه‌های پتانسیل، کل پیمایش‌های ناشی از اجتماع حداقل J(N) می‌شود. اگر اولین ادغام حداقل T اجتماع اجباری داشته باشد، کران به C(N,T) تقویت می‌شود. سپس رویدادهای جداگانهٔ اولین بررسی، ساخت و بازسازی ادغام، تلاش اولیه، حداقل آزمون منفی و بررسی پایانی اضافه می‌شوند. این جمله‌ها دوباره‌شماریِ اجتماع‌ها نیستند. به این ترتیب یک کران پایین عمومی داریم که منفیِ واقعاً ردکنندهٔ ادغام را هم مجاز می‌داند. اثبات شارژ و همهٔ جمله‌های حساب در پیوست آمده است.''',95,'Research §§2–3; Appendices 18–19')

add('Bounds when negatives cannot reject a merge',[
 F('N>1. Every negative contains a label outside positive support A.',height=77),
 E('D=sum(1+j(w); w∈S⁻),     j(w)=first outside position'),
 E('B=M+p+(11E²+25E+6)/2'),
 E('Linert=Lany−δ+1+D,     Uinert=B−E+s+ED'),
 F('Accepted batches telescope. Repeated labels and branching are allowed.'),
 F('Check this premise separately for each factor after negative allocation.')],
'''حالت بدون منفی و حالت منفیِ دارای حرف تازه را می‌توان دقیق‌تر تحلیل کرد. اگر هر منفی حرفی خارج از حروف مثبت داشته باشد، هیچ فرضیه‌ای که فقط از ادغام درخت مثبت ساخته می‌شود آن حرف را ندارد؛ بنابراین هر منفی رد می‌شود و همهٔ ادغام‌های پیشنهادی پذیرفته می‌شوند. قرمز فقط ریشه می‌ماند و مدل نهایی یک حالت دارد. D هزینهٔ رسیدن تمام منفی‌ها تا اولین حرف خارج از پشتیبان مثبت است. در هر تلاش هزینهٔ آزمون از D بیشتر نیست و در تلاش آخر دقیقاً D است. برای کران پایین، حداقل قبلیِ آزمون اولیه را با آزمون آخر جایگزین و یک بازنگاشت قرمز اضافه می‌کنیم. برای کران بالا، هزینهٔ یک دستهٔ اجتماع را به اختلاف یک تابع پتانسیل کران می‌زنیم و اختلاف‌ها تلسکوپی جمع می‌شوند. این کران به یکتا بودن یالِ هر حرف یا متوازن بودن داده نیاز ندارد. شرط باید برای هر عامل جدا بررسی شود؛ خارج بودن یک حرف در منفی جهانی الزاماً تصویر منفیِ تخصیص‌یافتهٔ محلی را بی‌اثر نمی‌کند.''',90,'Research §4; Appendices 20–21')

add('A new infinite Split family',[
 F('Σ={a,b}, singleton blocks, no negatives, n≥4.'),
 E('S⁺={ b aⁿ bⁿ⁻¹,  b a bⁿ⁻¹ aⁿ⁻¹ }'),
 E('N=4n−1,     T=1,     H=20n+19'),
 E('WS=2n²+28n+26,     LG=8n²+38n−6'),
 E('LG−(H+WS)=6n²−10n−51>0'),
 F('Only two balanced traces. The previous selector returned UNKNOWN.')],
'''این خانواده نشان می‌دهد گسترش فقط اصلاح چند عدد آزمایشی نیست. دقیقاً دو مثبت داریم و منفی نداریم. هر مثبت n حرف a و n حرف b دارد، ولی فقط دو عضو از خانوادهٔ بزرگ درهم‌تنیدگی‌ها را دیده‌ایم. دو رشته دقیقاً پیشوند ba را مشترک دارند، پس تعداد حالت‌های درخت ۴n منهای یک است. چون هیچ پیشوندی با bb شروع نمی‌شود، اولین ادغام فقط یک جفت پیشوند اجباری در شمارش T دارد. قاعدهٔ قبلی برای تمام اعضای این خانواده نامعلوم می‌داد. در هر عامل، هر دو مثبت به یک رشتهٔ یکتای تک‌الفبایی تصویر می‌شوند؛ هزینهٔ محلی دقیقاً قابل محاسبه است. کران پایین عمومی تازه و حساب دقیق هزینهٔ انتخاب‌گر، اختلاف روی اسلاید را می‌دهند. در n برابر چهار اختلاف پنج است و افزایش آن از n به n بعدی، ۱۲n منهای چهار و مثبت است. بنابراین برای هر n حداقل چهار، سود خالص Split با اثبات داریم؛ این یک خانوادهٔ نامتناهیِ تازه در ناحیهٔ گواهی است.''',95,'Research §5; Appendices 23–24')

add('A certificate from two traces',[
 E('S⁺={baaaabbb, babbbaaa},     S⁻=∅'),
 T(['Selection H','Exact Split WS','Global lower LG'],[['99','170','274']],[1,1,1],52),
 E('99+170=269<274≤WG'),
 F('Each local sample is one unary word of length four.'),
 F('Prefix counts and charged selector loops give the certificate before learning.'),
 F('n=4 is sufficient for this bound. It is not a universal minimum length.')],
'''برای اینکه نتیجه قابل بررسی باشد، عضو n برابر چهار را کامل حساب می‌کنیم. مثبت‌ها همان دو رشتهٔ روی اسلایدند و منفی نداریم. تصویر هر دو روی a برابر aaaa و روی b برابر bbbb است، پس بعد از حذف تکرار، هر عامل فقط یک مثبت دارد. هزینهٔ دقیق هر یادگیری تک‌الفبایی ۷۵ است. آماده‌سازی ۲۰ رویداد دارد و جمع Split برابر ۱۷۰ می‌شود. درخت جهانی ۱۵ حالت و ۱۴ یال دارد؛ I برابر ۴۷ و J پانزده برابر ۱۱۹ است. با افزودن جمله‌های اجباری کران پایینِ حالت پذیرفته‌شدن همهٔ ادغام‌ها، ۲۷۴ به دست می‌آید. هزینهٔ انتخاب‌گر از پیمایش‌های خود برنامه دقیقاً ۹۹ است؛ ریز آن در پیوست آمده است. بنابراین پیش از یادگیری ثابت می‌کنیم ۲۶۹ از هزینهٔ Global کمتر است. اجرای بعدی برنامه فقط کنترلِ تطبیق این محاسبه است و مقدمهٔ اثبات نیست. چهار، حد کافیِ این کران برای این خانواده است؛ آن را کمینهٔ لازم برای همهٔ داده‌ها معرفی نمی‌کنیم.''',110,'Research §5; Appendices 22–24')

add('A Global region with varied negatives',[
 F('All positives use only a. At least one positive is nonempty.'),
 F('Every global negative contains another label. The partition is arbitrary.'),
 E('WG=V+D,     WS≥Π+V+4(k−1)'),
 E('K=Π+4(k−1)−D>0'),
 F('Global wins. A net certificate additionally needs H<K.'),
 E('S⁺={aa}, S⁻={bb,bbb}: H=16, WG=43, WS=60')],
'''برای تصمیم Global نیز یک خانوادهٔ عمومی داریم. همهٔ مثبت‌ها از a ساخته شده‌اند، با حداقل یک مثبت غیرخالی، و هر منفی جهانی یک حرف دیگر دارد. مثبت‌ها لازم نیست طول‌های کامل یا متوازن داشته باشند. هزینهٔ بدون منفیِ زنجیره را V می‌نامیم. اولین ادغام جهانی کل زنجیره را یکی می‌کند و همهٔ منفی‌ها در حرف تازه رد می‌شوند، پس هزینهٔ جهانی دقیقاً V به اضافهٔ D است. عامل محلیِ شامل a همان مثبت‌ها را دارد و حتی اگر منفی‌های تخصیص‌یافته بعضی ادغام‌هایش را رد کنند، هزینه‌اش حداقل V است؛ این نکته جدا ثابت شده است. هر عامل غیرفعال هزینهٔ چهار دارد. با افزودن آماده‌سازی، اختلاف پایین K حاصل می‌شود و با کران D، مثبت بودن آن ثابت می‌شود. برای سود خالص باید H از K کمتر باشد. در مثال، ۱۶ به اضافهٔ ۴۳ برابر ۵۹ است و از ۶۰ کمتر است. این قضیه جهت هزینه را می‌گوید؛ برابری عمومی زبان خروجی را از آن نتیجه نمی‌گیریم.''',95,'Research §6; Appendix 22')

add('Complete coverage on a finite domain',[
 E('Σ={a,b}, blocks {a},{b},     V=all words of length ≤2'),
 F('Seven possible words give 3⁷=2187 consistent labeled datasets.'),
 T(['Outcome','Count'],[['Global cheaper','754'],['Split cheaper','493'],['Tie','15'],['AND decomposition infeasible','925']],[3,1],44),
 F('Lookup runs no RPNI. Offline work=405921 and setup work=2215.',height=77)],
'''یک نتیجهٔ کامل هم برای دامنهٔ محدود داریم. هفت رشتهٔ ممکن شامل رشتهٔ خالی و همهٔ رشته‌های طول یک و دو روی a و b است. هر رشته می‌تواند غایب، مثبت یا منفی باشد؛ پس دقیقاً ۲۱۸۷ مجموعه‌دادهٔ بدون برچسب متناقض داریم. کامپایلر همهٔ آن‌ها را آفلاین بررسی کرده و جدول کامل ساخته است. هنگام پرس‌وجو فقط سطر متناظر خوانده می‌شود و هیچ RPNI اجرا نمی‌شود. تعداد هر نتیجه روی اسلاید آمده است. موارد ناممکن یعنی هیچ مدل AND با آن افراز برچسب‌ها را رعایت نمی‌کند، نه اینکه Split صرفاً گران‌تر باشد. این جدول داخل دامنه UNKNOWN ندارد، ولی ساختش یادگیرنده را اجرا کرده و هزینهٔ آن و بارگذاری باید حساب شود. جدولِ طول دو، رشتهٔ طول سه را پوشش نمی‌دهد. نتیجهٔ کاملِ یک دامنهٔ از پیش تعیین‌شده را با انتخاب‌گر ارزان برای تمام طول‌های نامحدود جابه‌جا نمی‌کنیم.''',70,'Research §7; Previous Coverage §§6–8; Appendix 26')

add('Limits of counts and certificates',[
 F('UNKNOWN means overlapping current bounds, not an impossibility proof.'),
 F('Same partition {a},{b}, p=2, z=0, M=16. Opposite pipeline winners:'),
 E('S⁺={a⁷,a⁹}:     WG=208<232=WS'),
 E('S⁺={baaaabbb,babbbaaa}:     WS=170<274≤WG'),
 F('Individual lengths and prefix structures differ. Counts alone are insufficient.'),
 F('Cost certificates do not establish general output equality or target recovery.')],
'''برای جلوگیری از تعمیم اشتباه، دو نمونه را کنار هم می‌گذاریم. افراز هر دو، دو بلوک تک‌حرفی a و b است؛ هر دو دو مثبت، بدون منفی و مجموع طول مثبت ۱۶ دارند. در نمونهٔ a به توان هفت و a به توان نه، فرمول تک‌الفبایی هزینهٔ Global را ۲۰۸ می‌دهد و آماده‌سازی و عامل غیرفعال هزینهٔ Split را به ۲۳۲ می‌رسانند؛ پس Global برنده است. در خانوادهٔ دو تریسی تازه، Split برابر ۱۷۰ و Global حداقل ۲۷۴ است؛ پس جهت برعکس می‌شود. طول تک‌تک رشته‌ها و ساختار پیشوندها یکسان نیست و چنین چیزی ادعا نمی‌کنیم. نتیجه فقط این است که تعداد مثبت، تعداد منفی و مجموع طول به‌تنهایی برندهٔ همهٔ داده‌ها را مشخص نمی‌کنند. همچنین هزینهٔ کمتر، سازگاری با نمونه و برابری زبان خروجی گزاره‌های جدا هستند. حتی برابری دو خروجی نیز بدون فرض‌های شناسایی، بازیابی هدف واقعی را ثابت نمی‌کند.''',70,'Research §§5–7; Appendix 27')

add('Answers to the two research questions',[
 F('Q1: Explicit predicates and interval tests recognize our certificate region.',height=77),
 F('Q2: Every certified winner follows from a proved inequality or exact cost.',height=77),
 F('Net claims pay for H. Pipeline claims compare the learner pipelines.'),
 F('Coverage now includes general bounds and a new infinite Split family.'),
 F('Cheap exact selection for every unbounded input remains open.')],
'''اکنون پاسخ دو محور را دقیق جمع می‌کنم. برای محور اول، ناحیهٔ گواهی را به صورت شرط‌های صریح و نامساوی‌های محاسبه‌پذیر داریم. برنامه قبل از اجرای یادگیرنده بررسی می‌کند آیا همین شرایط برای ورودی برقرارند یا نه. برای محور دوم، هر پاسخ جهت‌دار با کران‌های اثبات‌شده یا هزینهٔ دقیق پشتیبانی می‌شود. اگر سود خالص گفته باشیم، H نیز پرداخت شده است. پوشش از خانواده‌های محدود اولیه به کران‌هایی برای مثبت‌های دلخواه و منفی‌های اثرگذار گسترش یافته؛ علاوه بر آن، یک خانوادهٔ نامتناهیِ دو تریسی که قبلاً همیشه نامعلوم بود اکنون گواهی سود خالص دارد. در دامنهٔ متناهیِ جدول نیز همهٔ موارد تعیین تکلیف می‌شوند، با حساب صریح پیش‌محاسبه. آنچه باقی است، انتخاب دقیق و ارزان برای هر ورودی بدون کران است؛ نه حل آن را اعلام می‌کنیم و نه ناممکن بودنش را. تضمین نتایج فعلی ریاضی و مشروط به قرارداد روشن است.''',80,'Research §§1–9')

add('Next research question',[
 F('When do Global and Split learn the same language?'),
 E('L(Global) = ⋂ᵢ πᵢ⁻¹(L(Localᵢ)) ?'),
 F('Seek additional conditions for incomplete positives and effective negatives.',height=77),
 F('Cost and sample consistency alone do not establish this equality.'),
 F('Actual runtime and target recovery require separate analysis.')],
'''سؤال مرحلهٔ بعد را برابری زبان خروجی نگه می‌داریم: برای مثبت‌های ناقص و منفی‌هایی که بعضی ادغام‌ها را رد می‌کنند، چه شرطِ قابل بررسیِ پیش از اجرا کافی است تا زبان Global و ترکیب عوامل برابر شوند؟ در خانواده‌هایی مثل حالت بدون منفی، برابری جداگانه ثابت شده، ولی تعمیم آن به تمام ناحیهٔ هزینه درست نیست. ادامهٔ پژوهش هزینه به حل این سؤال وابسته نیست؛ گواهی صرفاً هزینه را با همان دامنهٔ ادعا نگه می‌داریم. اینجا مسیر اصلی ارائه تمام می‌شود و اسلایدهای بعد برای اثبات‌ها و پرسش‌ها هستند.''',40,'Research §§5–7; Appendix 28')

add('Reference algorithm and charged events',[
 F('Positive prefix trie. Root initially red. Partial transitions reject.'),
 F('Choose the least shortlex blue state and test red states in shortlex order.'),
 F('A flat parent map canonically merges the two classes and closes conflicts.',height=77),
 F('Each union scans q retained records. Each closure pass scans e edges.'),
 F('Rebuild states/finals/edges. Keep only if all negatives reject. Remap red.',height=77),
 F('Failed trials keep the old model. If all trials fail, promote blue.')],
'''قرارداد مرجع به طور کامل این است: درخت پیشوند مثبت‌ها ساخته می‌شود و فقط ریشه قرمز است. آبی‌ها مقصد یال از قرمز به غیرقرمز هستند. کمترین آبی در ترتیب طول و سپس واژه‌نامه‌ای انتخاب می‌شود و قرمزها هم به همان ترتیب آزموده می‌شوند. برای هر تلاش، نگاشت والد تخت روی تمام حالت‌های جاری ساخته می‌شود. اجتماع دو کلاس با نمایندهٔ کمینه انجام می‌شود و هر اجتماع همهٔ q رکورد را می‌پیماید. بستار قطعی با پیمایش یال‌ها و یکسان کردن مقصدهای متعارض ادامه پیدا می‌کند تا یک دور بدون اجتماع جدید بگذرد. سپس حالت‌ها، نهایی‌ها با OR و یال‌ها بازسازی می‌شوند. منفی‌ها به ترتیب ثابت آزموده می‌شوند؛ انتقال ناموجود رد می‌کند و اولین منفی پذیرفته‌شده تلاش را رد می‌کند. اگر همه رد شوند، مدل نگه داشته و تمام قرمزهای قبلی بازنگاشت می‌شوند. رد تلاش هیچ تغییری در مدل اصلی نمی‌دهد. اگر همهٔ قرمزها برای آن آبی شکست بخورند، آبی قرمز می‌شود. این دقیقاً الگوریتمی است که تمام شمارش‌ها دربارهٔ آن‌اند.''',proof='Research §1; rpni_work_reference.py')

add('Proof of AND feasibility',[
 E('Pᵢ=πᵢ(S⁺),     V(w)={i:πᵢ(w)∉Pᵢ}'),
 F('Necessity: accepting every positive forces Pᵢ⊆Lᵢ.'),
 F('If V(w)=∅, every factor accepts its projection. The negative is accepted.',height=77),
 F('Sufficiency: choose finite regular languages Lᵢ=Pᵢ. Each witness rejects.',height=77),
 F('Allocating a negative to max V(w) makes every local labeled sample consistent.',height=77),
 F('Any consistent local learners then produce a sample-consistent AND model.')],
'''برای ضرورت، اگر محصول تصویرها هر مثبت جهانی را قبول کند، هر زبان محلی باید تمام تصویر مثبت‌ها را داشته باشد. منفی‌ای که همهٔ تصویرهایش در این مجموعه‌ها باشند، در تمام عوامل پذیرفته می‌شود و تناقض ایجاد می‌کند. برای کفایت، زبان هر عامل را خودِ مجموعهٔ متناهی تصویر مثبت‌ها می‌گیریم. هر منفی شاهد دارد و تصویر آن در زبان شاهد نیست، پس محصول آن را رد می‌کند. زبان‌های متناهی منظم‌اند و محدودیت تعداد حالت محلی نداریم، پس این یک ساخت معتبر است. تخصیص به بزرگ‌ترین شاهد فقط یکی از انتخاب‌های ممکن است، ولی برای مقایسهٔ هزینه ثابت نگه داشته شده است. چون تصویر انتخاب‌شده خارج از مثبت همان عامل است، برچسب محلی متناقض نمی‌شود. پس هر یادگیرندهٔ محلی سازگار، مثبت‌ها را قبول و منفی‌های تخصیص‌یافته را رد می‌کند؛ در نتیجه محصول با دادهٔ جهانی سازگار است. تمام استدلال رشتهٔ خالی و مجموعه‌های تهی را هم شامل می‌شود.''',proof='Research §1; Original feasibility theorem')

add('Termination and a general upper bound',[
 E('I=M+p+2N−1, E=N−1, d=sum(|w|+1; w∈S⁻)'),
 F('q−|Red| decreases each iteration. There are at most N−1 iterations.'),
 F('At iteration j, |Red|≤j. Attempts and total red remaps are each ≤C=N(N−1)/2.',height=77),
 E('Fold≤q²+q+qe'),
 E('Uany=I+N(2N+E)+C(2+N²+N+NE+d)'),
 F('At most N fringes. For N=1, the exact cost is I+2.')],
'''هر تکرار غیرپایانی پتانسیل تعداد حالت منهای تعداد قرمز را کم می‌کند. ارتقا، قرمز را یک زیاد می‌کند؛ ادغام پذیرفته‌شده در اولین اجتماع یک غیرقرمز را به قرمز وصل می‌کند، پس کاهش حالت‌ها از کاهش تعداد تصویرهای قرمز حداقل یک بیشتر است. بنابراین حداکثر N منهای یک تکرار و N بررسی مرز داریم. پیش از تکرار j، تعداد قرمز از j بیشتر نیست، چون فقط ارتقا آن را یک زیاد می‌کند. جمع تلاش‌ها و جمع بازنگاشت‌های قرمز هر کدام حداکثر C است. در یک تلاش u حداکثر q منهای یک اجتماع داریم. اولین اجتماع پیش از بستار انجام می‌شود؛ هر دور غیرپایانی بستار یک اجتماع تازه مصرف می‌کند، پس تعداد دورها حداکثر u است. هزینهٔ دقیقِ برحسب این دو شمارنده، دو q به اضافهٔ q ضربدر u و e ضربدر تعداد دور به اضافهٔ یک است. با جایگذاری، کران q مربع به اضافهٔ q و q ضربدر e حاصل می‌شود. هر آزمون منفی از d بیشتر نیست. کران مرزها، تلاش‌ها، بستارها و بازنگاشت‌ها جدا جمع می‌شوند و فرمول عمومی به دست می‌آید. N برابر یک مستقیماً با فرمول دقیق حل می‌شود.''',proof='Research §§2,8')

add('Universal union charges',[
 F('v=q−|Red|, u=fold unions, h=loss of distinct red images.'),
 E('Kept: d=u−h, 0≤h≤u−1.     Promotion: d=1.'),
 E('qu≥(v+1)d≥sum(j+1; j=v−d+1,…,v)'),
 F('On promotion, at least one rejected trial still pays qu≥v+1.'),
 E('Total union-record visits ≥ sum(j+1; j=1,…,N−1)=J(N)'),
 F('Reachability and a red root imply that no blue state means v=0.')],
'''این اثبات مستقل از پذیرش منفی‌هاست. از یک وضعیت با پتانسیل v شروع کنید. اگر ادغام نگه داشته شود و u اجتماع کلاس انجام دهد، تعداد حالت u کم می‌شود. افت تعداد تصویرهای قرمز را h بگیرید. اولین اجتماع قرمز با غیرقرمز است و تصویر قرمز را کم نمی‌کند؛ پس h بین صفر و u منهای یک است. افت پتانسیل d برابر u منهای h و بین یک و u است. هزینهٔ اجتماع‌های همین تلاش q ضربدر u است و چون q حداقل v به اضافهٔ یک است، می‌تواند همهٔ رتبه‌های از v منهای d به اضافهٔ یک تا v را، با وزن رتبه به اضافهٔ یک، بپردازد. اگر به جای آن ارتقا انجام شود، حداقل یک تلاش ردشده با یک اجتماع داشته‌ایم و همان وزن v به اضافهٔ یک پرداخت شده است. رتبه‌های مصرف‌شده در تکرارها هم‌پوشانی ندارند و از N منهای یک تا صفر را می‌پوشانند. در پایان هیچ غیرقرمزِ دسترس‌پذیری نمی‌ماند؛ وگرنه اولین یال خروج از قرمز روی مسیرش یک آبی می‌ساخت. بنابراین جمع شارژها دقیقاً J(N) است. همین استدلال از هر وضعیت میانی با پتانسیل v، کران J(v به اضافهٔ یک) را می‌دهد.''',proof='Research §2, Theorem 1')

add('First-fold refinement and mandatory work',[
 F('N>1. Q=positive prefixes. First blue x: T counts t,xt∈Q; root~x forces t~xt.'),
 F('The T obligation edges form a forest, so the first fold makes u≥T unions.',height=77),
 E('Kept: Nu+J(N−u)≥NT+J(N−T)=C(N,T)'),
 F('Rejected: promotion leaves potential N−2, giving Nu+J(N−1)≥C(N,T).',height=77),
 E('Lany=I+C(N,T)+4N+3E+3+s+δ'),
 F('4N+3E: first fringe/map/rebuild. Add candidate 1, terminal 2+s and δ.',height=77)],
'''اگر t و xt هر دو پیشوند باشند، مسیر t از ریشه و از حالت x تعریف شده است. ادغام ریشه و x در هر خارج‌قسمت قطعی، مقصد این مسیرها یعنی t و xt را یکی می‌کند. یال‌های بین t و xt در گراف تعهدها، هر کدام حداکثر یک پیشین و پسین دارند و طول روی جهتشان زیاد می‌شود؛ پس جنگل‌اند و T یال به حداقل T کاهش کلاس نیاز دارد. برای تقویت شارژ، اگر اولین تلاش با u اجتماع پذیرفته شود، قرمز همچنان فقط ریشه است و کار اجتماعِ باقیمانده حداقل J(N منهای u) می‌شود. تابع N ضربدر u به اضافهٔ همین J، با افزایش صحیح u یک مقدار u زیاد می‌شود، پس کمینه برای u برابر T است. اگر تلاش رد شود، فقط یک قرمز اولیه داشتیم و ارتقا انجام می‌شود؛ پتانسیل N منهای دو و کار بعدی حداقل J(N منهای یک) است، که باز کران مورد نظر را پوشش می‌دهد. به کار اجتماع‌ها، اولین مرز دو N به اضافهٔ E، ساخت نگاشت و بازسازی حالت دو N، حداقل یک دور و بازسازی یال دو E، تلاش یک، حداقل آزمون δ و مرز پایانی دو به اضافهٔ s را اضافه می‌کنیم. این دسته‌ها جدا هستند و فرمول پایین حاصل می‌شود.''',proof='Research §§2–3')

add('Inert-negative upper bound proof',[
 F('All negatives have an outside label. Every first candidate keeps.'),
 F('A fold has u unions, at most u closure passes, and moves q to q−u.'),
 E('c(q,u)=4q+qu+E(u+2)+2+D'),
 E('F(q)=sum(5r+3E+2+D; r=2,…,q),     F(1)=0'),
 E('F(q)−F(q−u)−c(q,u)=(u−1)(4q−5u/2+2E+2+D)≥0'),
 F('q≥u+1. The differences telescope over all kept batches.')],
'''در فرض حرف تازه، هیچ منفی نمی‌تواند ادغام را رد کند؛ بنابراین هر بار اولین تلاش با قرمزِ ریشه نگه داشته می‌شود. اگر q حالت و e یال فعلی داریم و u اجتماع صورت می‌گیرد، ساخت نگاشت و بازسازی حالت دو q، اجتماع‌ها q ضربدر u و دورهای بستار و بازسازی یال حداکثر e ضربدر u به اضافهٔ یک هزینه دارند. مرز، تلاش و بازنگاشت و آزمون منفی را اضافه می‌کنیم و e را با E اولیه کران می‌زنیم تا c به دست آید. تابع F را جمع هزینه‌های تک‌اجتماعیِ پوشاننده تعریف می‌کنیم. تفاضل F(q) و F(q منهای u) منهای هزینهٔ دسته، دقیقاً عبارت غیرمنفی اسلاید است؛ چون u حداقل یک و q حداقل u به اضافهٔ یک است. بنابراین هزینهٔ هر دسته از کاهش F بیشتر نیست. پس با جمع دسته‌ها، عبارت‌های میانی حذف می‌شوند و فقط F(N) می‌ماند. این استدلال هیچ محدودیتی بر تکرار حروف یا شاخه‌زنی درخت مثبت ندارد.''',proof='Research §4, Theorem 3 upper proof')

add('Closed bounds and edge cases',[
 E('D=sum(1+j(w); w∈S⁻),     B=M+p+(11E²+25E+6)/2'),
 E('I+F(N)+2+s=B−E+s+ED'),
 F('The last candidate has one final state and all positive-label loops.'),
 E('Linert=I+C(N,T)+4N+3E+4+s+D'),
 F('Charge the last negative scan D once, replacing the first-scan minimum δ.',height=77),
 F('N=1: exact I+2. Empty negative sets have D=0. Check local premises separately.',height=77)],
'''بسط جبری جمع F و مقداردهی اولیه و مرز نهایی، کران بالای بسته را می‌دهد. در پایان همهٔ حالت‌ها به ریشهٔ نهایی تبدیل شده‌اند و تمام حروف مثبت حلقه دارند. پس هر منفی دقیقاً تا اولین حرف خارج از مجموعه خوانده و رد می‌شود و مجموع هزینهٔ آزمون آخر D است. برای کران پایین، از شارژ کل اجتماع‌ها و هزینه‌های اجباری اولین مرز و بازسازی استفاده می‌کنیم؛ یک بازنگاشت قرمز اضافه می‌کنیم و به جای حداقل δ در آزمون اول، کل آزمون آخر D را می‌شماریم. δ و D را با هم جمع نمی‌کنیم تا دوباره‌شماری رخ ندهد. اگر N یک باشد اصلاً تلاشی نداریم و هزینهٔ دقیق I به اضافهٔ دو است؛ حتی اگر منفی داشته باشیم آزمون منفی در اجرای یادگیرنده رخ نمی‌دهد. برای منفی تهی D صفر است. این فرمول‌ها برای هر عامل هم معتبرند، به شرط بررسی مستقلِ فرض روی منفی‌های واقعاً تخصیص‌یافتهٔ همان عامل.''',proof='Research §§3–4')

add('Unary work and the Global proof',[
 E('V=m+p+r²+(9+dᵣ)r+10, dᵣ=1 if r=1, else 2'),
 F('r≥1 is the maximum positive length. First fold: r unions, dᵣ passes.'),
 F('Without negatives, direct event summation gives V. With any negatives, W≥V.',height=77),
 F('Keeping pays remap+terminal=4. Rejecting pays the next fringe 3r+2≥5.',height=77),
 E('WG=V+D, WS≥Π+V+4(k−1)'),
 E('K≥M+kp+(2k−1)z+4(k−1)>0.     Net Global if H<K.')],
'''r بیشترین طول مثبت تک‌الفبایی است و حداقل یک است. درخت، کل زنجیرهٔ طول r را دارد، حتی اگر بعضی طول‌ها مثبت نباشند. ادغام ریشه با a همهٔ زنجیره را مجبور به یکی شدن می‌کند. r اجتماع داریم؛ برای r یک، دور اول بستار پایدار است و در غیر آن یک دور مولد و یک دور پایدار داریم. هزینهٔ بستار r مربع به اضافهٔ چهار به اضافهٔ تعداد دور، ضربدر r، به اضافهٔ دو است. با مقداردهی اولیه، مرز اولیه، تلاش، یک بازنگاشت و مرز پایانی، V حاصل می‌شود. همهٔ کار تا پایان اولین بستار V منهای چهار است. اگر منفی باعث رد شود، فقط یک قرمز بوده، ارتقا انجام و مرز بعدی روی درخت تغییرنکرده با هزینهٔ سه r به اضافهٔ دو اجرا می‌شود که حداقل پنج است. اگر ادغام پذیرفته شود، بازنگاشت و مرز پایانی چهار است. پس با هر منفی سازگار هزینه حداقل V است. در خانوادهٔ Global، منفی جهانی حرف تازه دارد و هزینهٔ واقعی V به اضافهٔ D است. عامل فعال حداقل V و بقیه چهار دارند. چون D از حجم منفی به اضافهٔ تعدادشان بیشتر نیست، K به عبارت مثبت اسلاید کران می‌خورد. این اثبات با منفیِ محلی اثرگذار هم معتبر است.''',proof='Research §6')

add('Two-trace counts and selector work',[
 E('n≥2: p=2, M=4n, N=4n−1, E=4n−2, T=1'),
 F('The two words share exactly ba. No positive prefix starts with bb.'),
 T(['Charged selector group','Events'],[
  ['Configuration, input, active scan','4n+8'],['Singleton gate and global prefixes','4n'],
  ['Projection and prefix-pair tests','8n+5'],['Local features','4n+6'],['Total H','20n+19']],[3,1],43),
 F('Each local positive set is one word, aⁿ or bⁿ. Duplicated images count once.')],
'''برای n حداقل دو، رشتهٔ اول در حرف سوم a و رشتهٔ دوم در حرف سوم b دارد؛ بنابراین پیشوند مشترک دقیقاً ba است. تعداد پیشوندهای دو رشته برابر یک به اضافهٔ دو طول، منهای دو پیشوند مشترک، یعنی ۴n منهای یک می‌شود. همهٔ پیشوندهای غیرخالی با b و بعد، در صورت طول کافی، با ba شروع می‌شوند. اگر bt با t غیرخالی بخواهد پیشوند باشد باید با bb شروع شود که نداریم؛ فقط t خالی شمرده می‌شود و T یک است. جدول هزینهٔ انتخاب‌گر، همان حلقه‌های برنامه را گروه‌بندی می‌کند. پیکربندی و پیمایش اول ۴n به اضافهٔ هشت است؛ دروازهٔ تک‌مثبت و ایجاد پیشوندها مجموعاً ۴n است؛ تصویرسازی و آزمون جفت‌های پیشوند ۸n به اضافهٔ پنج؛ ویژگی‌های محلی ۴n به اضافهٔ شش. جمع ۲۰n به اضافهٔ نوزده است. هیچ شاخهٔ زودهنگام دیگری این ورودی را نمی‌گیرد و بررسی خانوادهٔ نشانگر، چون منفی نداریم، وارد پیمایش رکورد نمی‌شود. تصویرهای تکراری به یک عضو مثبت محلی تبدیل می‌شوند.''',proof='Research §5, event table')

add('Net Split proof for every n≥4',[
 E('v(n)=n²+12n+11,     Π=4n+4'),
 E('WS=Π+2v(n)=2n²+28n+26'),
 E('LG=8n²+38n−6,     H=20n+19'),
 E('LG−H−WS=6n²−10n−51'),
 F('At n=4 the margin is 5. Its next increment is 12n−4>0.'),
 F('All n≥4 receive net Split. Earlier LG−WS=−2(n−4)²≤0 gave UNKNOWN.')],
'''هزینهٔ دقیق یک مثبت تک‌الفبایی طول n از فرمول قبلی، n مربع به اضافهٔ ۱۲n و یازده است. دو عامل داریم و آماده‌سازی ۴n به اضافهٔ چهار است، پس فرمول Split حاصل می‌شود. در کران پایینِ همه‌ادغام‌پذیر، I برابر ۱۲n منهای یک، C(N,1) برابر J(۴n منهای یک)، و s دو و D صفر است. جایگذاری، ۸n مربع به اضافهٔ ۳۸n منهای شش را می‌دهد. H را کم و سپس هزینهٔ Split را کم می‌کنیم؛ عبارت چندجمله‌ای اسلاید حاصل می‌شود. مقدار آن برای چهار پنج است و افزایش صحیح آن ۱۲n منهای چهار است؛ پس برای تمام n حداقل چهار مثبت می‌ماند. کران پایین قبلی ۴۴n منهای شش بود که اختلافش با هزینهٔ Split منفیِ دو برابر مربع n منهای چهار است؛ هرگز جدایی لازم را نمی‌داد. دیگر شاخه‌های قبلی نیز به این خانواده نمی‌خوردند. بنابراین این گسترش برای بی‌نهایت ورودی ثابت شده است. چون منفی نداریم، در هر دو مسیر همهٔ تلاش‌ها نگه داشته، قرمز ریشه می‌ماند و با دسترس‌پذیری در پایان فقط یک حالت نهایی با حلقه‌های پشتیبان مثبت داریم؛ در این خانواده هر دو زبان دقیقاً ستارهٔ a و b هستند.''',proof='Research §5')

add('Exact costs for a broader positive class',[
 F('A positive trie has one edge per observed label exactly when E=|A|.'),
 F('Projection preserves this property, including shared prefixes and terminals.',height=77),
 E('No negatives: W=B(m,p,E)=m+p+(11E²+25E+6)/2'),
 F('Each fold has one union and one stable pass. All E iterations keep.'),
 E('W=I+sum(5q+3E+2; q=2,…,E+1)+2+E'),
 F('Apply the same exact formula to deduplicated local samples and add Π.')],
'''هر حرف دیده‌شده حداقل یک یال در درخت پیشوند دارد، پس برابری تعداد یال‌ها و حروف معادل این است که هر حرف فقط روی یک یال باشد. اگر یال یکتای a از پیشوند u به ua باشد، تمام وقوع‌های مثبت a همان پیشوند u را دارند؛ پس بعد از تصویرسازی، همه از همان تصویر u به تصویر u سپس a می‌روند و یال a در عامل هم یکتا می‌ماند. در هر خارج‌قسمت، چون یک یال با هر حرف داریم، تعارض دو مقصد هم‌حرف رخ نمی‌دهد؛ هر تلاش دقیقاً یک اجتماع و یک دور پایدار بستار دارد. با منفی تهی همه پذیرفته می‌شوند و E تکرار داریم، با q از E به اضافهٔ یک تا دو. هزینهٔ هر تکرار پنج q به اضافهٔ سه E و دو است و مقداردهی اولیه و مرز نهایی هم جدا اضافه می‌شوند. جمع بسته همان B است. بنابراین برای کل این کلاس مثبت‌های چندتایی، هزینهٔ هر دو مسیر دقیق است. برای E صفر فرمول p به اضافهٔ سه می‌شود و نمونهٔ تهی یا فقط رشتهٔ خالی را هم درست حساب می‌کند.''',proof='Previous Coverage §§2–3')

add('Complete finite-domain lookup proof',[
 F('Fix a finite vocabulary V of d words and an ordered partition.'),
 E('key=Σᵢ labelᵢ·3ⁱ,     labelᵢ∈{0,1,2}'),
 F('Absent, positive, negative give exactly 3ᵈ keys. Compilation fills every key.',height=77),
 F('Reference termination and the witness test give an exact cost/status row.'),
 E('Total saving versus Global needs Σⱼ(WG,j−Wchosen,j)>Coffline+Ssetup+ΣⱼQj'),
 F('Outside V means OUT_OF_DOMAIN. No finite V covers all unbounded strings.')],
'''برای هر رشتهٔ واژگان دقیقاً یکی از سه وضعیت داریم. نمایش مبنای سه، نگاشت یک‌به‌یک این برچسب‌گذاری‌ها به عددهای صفر تا سه به توان d منهای یک است. کامپایلر برای هر برچسب‌گذاری، شاهدهای منفی را بررسی می‌کند، Global و در صورت امکان عوامل را با برنامهٔ خاتمه‌پذیر اجرا و هزینه را ثبت می‌کند. پس هیچ کلید خالی نمی‌ماند. پرس‌وجو همان کلید را می‌سازد و سطر را می‌خواند؛ کد خواندن جدول هیچ یادگیرنده‌ای وارد یا اجرا نمی‌کند. این اثبات کامل بودن روی دامنهٔ ثابت است، با فرض درستی برنامهٔ مرجع و کامپایلر که مستقل بررسی شده‌اند. هزینهٔ آفلاین C، آماده‌سازی S و کار هر پرس‌وجو Q است. با تفریق هزینهٔ کل روش از همیشه اجرای Global، شرط سود خالص روی اسلاید حاصل می‌شود. در مثال جدول، آفلاین ۴۰۵۹۲۱ و آماده‌سازی ۲۲۱۵ است. ذخیره‌سازی همین روش سه به توان d سطر می‌خواهد؛ این را کران پایین همهٔ روش‌های ممکن معرفی نمی‌کنیم. واژهٔ خارج از دامنه را حدس نمی‌زنیم و هیچ دامنهٔ متناهی همهٔ طول‌های نامحدود را شامل نمی‌شود.''',proof='Research §7; Previous Coverage §§6–8')

add('Counterexamples and independent checks',[
 F('Misapplying the inert bound: S⁺={a}, S⁻={ε} gives 24, but W=25.',height=77),
 F('A cheaper pipeline may not pay for selection: S⁺={ε}, S⁻=∅, two singleton blocks.',height=77),
 E('WG=4, WS=10, H=7.     H+WG=11>10'),
 F('Same counts and volume can have opposite winners. Exact ties also occur.'),
 F('55624 case executions. 174998 independently checked candidate quotients.'),
 F('Finite checks supplement proofs. Counts may include repeated inputs.')],
'''اولین مثال نشان می‌دهد کران بالای حالت بی‌اثر را نمی‌توان به منفی دلخواه تعمیم داد. برای مثبت a و منفی خالی، ادغام ریشه و a پذیرفتن خالی را ایجاد می‌کند و رد می‌شود؛ هزینهٔ واقعی ۲۵ است، ولی استفادهٔ نادرست از فرمول بی‌اثر با یک رویداد منفی، ۲۴ می‌دهد. مثال دوم، مثبتِ فقط رشتهٔ خالی بدون منفی و دو بلوک تک‌حرفی است. Global چهار و Split ده هزینه دارد، اما انتخاب‌گر فعلی هفت هزینه دارد؛ پس برنده بودن به تنهایی سود خالص نیست. برای ناکافی بودن شمار و حجم، دو نمونهٔ اسلاید دوازده با اثبات مستقل کافی‌اند و تساوی هم در مثبت‌های a و b با دو بلوک رخ می‌دهد. پنج بررسی بازتولیدپذیر در مجموع ۵۵۶۲۴ اجرای مورد آزمون و ۱۷۴۹۹۸ کنترل مستقل ادغام دارند. تمام زیرمجموعه‌های مثبتِ رشته‌های دودویی تا طول سه و نمونه‌های منفی اثرگذار نیز بررسی شده‌اند. بستار با اشباع مستقلِ افراز حالت‌ها و مدل‌ها با یادگیرندهٔ مستقل تطبیق داده شده‌اند. این کنترل‌ها جای اثبات نامتناهی را نمی‌گیرند و مصونیت مطلق کد را ثابت نمی‌کنند.''',proof='Research §§4–9; all audit result files')

add('Next question: output-language equality',[
 E('L(Global) = ⋂ᵢ πᵢ⁻¹(L(Localᵢ)) ?'),
 F('Find additional pre-training conditions for incomplete data and effective negatives.',height=77),
 F('Special equal-output families are proved. General cost certificates stay separate.',height=77),
 F('Further cost work: reduce UNKNOWN without simulating the learner.'),
 F('Current guarantee: exact mathematical claims under the stated reference contract.')],
'''سؤال بازِ برابری را در آخر کل پاورپوینت هم نگه می‌داریم. برای نمونه‌های بدون منفی و بعضی منفی‌های بی‌اثر، استدلال یک حالت نهایی با حلقه‌های پشتیبان، برابری را روی تمام رشته‌ها ثابت می‌کند. ولی ناحیهٔ گواهی هزینه با منفی‌های اثرگذار بزرگ‌تر است. نمونهٔ مشخصی با شش مثبت aabb، abab، abba، baab، baba و bbaa و منفی‌های bbb و c، برای بلوک‌های تک‌حرفی a و b و c گواهی هزینه دارد و خروجی‌ها متفاوت‌اند. اجرای مرجع جهانی سه حالت دارد که همه نهایی‌اند: از ریشه با a به ریشه و با b به حالت b می‌رود؛ از b با a به ریشه و با b به bb؛ از bb با a به ریشه و یال b ندارد. عامل a حلقهٔ نهایی a دارد، عامل b دو حالت با تناوب b و فقط حالت آغازین نهایی دارد و عامل c فقط خالی را می‌پذیرد. بنابراین رشتهٔ b در Global پذیرفته و در محصول رد می‌شود. ترتیب شش تلاش جهانی به صورت ادغام ریشه با a، ریشه با b، ریشه با ba، ریشه با bb، b با bb و ریشه با bba است و وضعیت نگهداری آن‌ها به ترتیب بله، خیر، بله، خیر، خیر، بله است؛ جدول‌ها و ردهای مستقل همراه گزارش‌اند. پس سؤال مرحلهٔ بعد، پیدا کردن فرض‌های اضافهٔ کافی است، نه تعمیم بی‌قید برابری به همهٔ ناحیهٔ هزینه. انتخاب ارزان برای همهٔ ورودی‌های بدون کران نیز در ادامهٔ مستقل پژوهش هزینه باقی می‌ماند.''',proof='Research §7; research/quality_models.json and quality_global_trace.json')

assert len(slides)==28
assert sum(s['seconds'] for s in slides)==1080
out.mkdir(parents=True,exist_ok=True)
(root/'slides.json').write_text(json.dumps(slides,indent=2,ensure_ascii=False),encoding='utf8')
(out/'slide_content.json').write_text(json.dumps(slides,indent=2,ensure_ascii=False),encoding='utf8')
elapsed=0;timing=[];md=['# متن ارائه انتخاب Split یا Global پیش از RPNI','',
'اسلایدهای ۱ تا ۱۴ مسیر اصلی ۱۸ دقیقه‌ای‌اند. پیوست‌ها خارج از این زمان‌اند. زمان‌ها برنامهٔ ارائه‌اند و باید با صدای بلند تمرین شوند.','']
for i,s in enumerate(slides,1):
    md+=['## اسلاید '+str(i)+' '+s['title'],'']
    if s['seconds']:
        timing.append(dict(slide=i,start=elapsed,end=elapsed+s['seconds'],seconds=s['seconds']))
        md+=['زمان: '+f'{elapsed//60:02}:{elapsed%60:02} تا {(elapsed+s["seconds"])//60:02}:{(elapsed+s["seconds"])%60:02}','']
        elapsed+=s['seconds']
    else:md+=['پیوست خارج از زمان اصلی','']
    md += [s['notes'],'','مرجع اثبات: '+s['proof'],'']
(out/'Speaker_Notes_FA.md').write_text('\n'.join(md),encoding='utf8')
(out/'talk_timing.json').write_text(json.dumps(dict(total_seconds=elapsed,main_words=sum(len(s['notes'].split()) for s in slides[:14]),slides=timing),indent=2),encoding='utf8')
print(json.dumps(dict(slides=len(slides),seconds=elapsed,main_words=sum(len(s['notes'].split()) for s in slides[:14]))))
