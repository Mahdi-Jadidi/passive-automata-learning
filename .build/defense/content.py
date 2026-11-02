from pathlib import Path
import json

root=Path(__file__).parent
out=root.parents[1]/'output'/'defense'
F=lambda x:dict(kind='text',text=x)
E=lambda x:dict(kind='eq',text=x)
def T(headers,rows,widths):return dict(kind='table',headers=headers,rows=rows,widths=widths)
OWN='Self-contained proofs: Proofs_and_Audit_EN.md. Reference event model: rpni_work_reference.py. Pre-training selector: defense_selector.py. These are implementation-specific work guarantees.'
STD='Björklund, Björklund, Martens, Learning Algorithms, Section 4, Algorithms 6 and 7. https://www.theoinf.uni-bayreuth.de/pool/documents/Paper2011-15/Paper2011/Learning_Algorithms_paper.pdf . This supports the state-merging background, not our specific cost certificates.'
slides=[]
def add(title,blocks,notes,secs=0,proof='',source=OWN):
    slides.append(dict(title=title,blocks=blocks,notes=notes,seconds=secs,proof=proof,source=source))

add('Split or Global RPNI?',[
F('Certified choices before training'),
F('Known alphabet partitions and explicit work bounds'),
F('Main talk: 18 minutes. Full proofs follow in the appendix.')],
'''سؤال این بررسی این است که وقتی افراز الفبا را از قبل می‌دانیم، آیا می‌توانیم پیش از اجرای یادگیری تشخیص بدهیم اجرای جداگانهٔ مؤلفه‌ها کم‌هزینه‌تر است یا اجرای یکجای RPNI. من دو محور را دنبال می‌کنم: اول اینکه چه ساختاری از داده اجازهٔ صدور یک گواهی معتبر را می‌دهد؛ دوم اینکه بر اساس آن گواهی کدام مسیر را انتخاب کنیم. نتیجهٔ فعلی یک تصمیم‌گیر با شرایط کافی و فرض‌های روشن است. برای همهٔ ورودی‌ها پاسخ قطعی ادعا نمی‌کنم.''',30,'Sections 1 and 10')

add('The learning problem',[
E('Σ = B₁ ⊎ B₂ ⊎ ··· ⊎ Bₖ'),
F('The partition is known. Projection erases symbols outside a block.'),
F('Finite disjoint label sets, nonempty disjoint blocks. Keep ε.'),
E('π₁(abba)=aa,     π₂(abba)=bb     for B₁={a}, B₂={b}'),
F('Global runs once. Split projects the samples and learns one model per block.'),
F('AND acceptance: every local model must accept its projection.')],
'''افراز الفبا را ورودی مسئله فرض می‌کنیم؛ بنابراین کشف اینکه هر حرف متعلق به کدام مؤلفه است در این بررسی حل نمی‌شود. بلوک‌ها ناتهی، دوبه‌دو جدا و پوشانندهٔ الفبا هستند. تصویر یک تریس روی یک بلوک با حذف حروف بیرون آن ساخته می‌شود و ترتیب باقی‌مانده حفظ می‌شود. مثلاً تصویر abba روی بلوک a برابر aa و روی بلوک b برابر bb است. داده شامل مجموعهٔ مثبت و منفی بدون تناقض برچسب است؛ رشتهٔ خالی نیز اگر تولید شود حفظ می‌شود. در مسیر جهانی یک مدل می‌آموزیم؛ در مسیر تجزیه‌شده از دادهٔ تصویری برای هر بلوک یک مدل می‌سازیم. پذیرش نهایی را AND تعریف می‌کنیم. این فرض ضروری است، چون معنای ترکیب مؤلفه‌ها روی تمام اثبات‌ها اثر دارد.''',60,'Sections 1 and 2')

add('What better means',[
E('WG = Global work,     WS = Split work,     H = selection work'),
F('Wref counts declared loop events in one fixed sparse RPNI implementation.'),
F('Split work includes projection and negative allocation. Both pipelines are sequential.'),
F('A class union scans the full state map. Library internals are outside the count.'),
F('Split returns factors. Explicit product construction and minimization are excluded.')],
'''برای اینکه عبارت بهتر بودن مبهم نماند، معیار را دقیق می‌کنم. W مرجع تعداد رویدادهای مشخص حلقه‌های پیاده‌سازی ثابت ماست؛ مثل عبور از حالت، انتقال و حرف، ساخت حالت، آزمون منفی و تلاش ادغام. هزینهٔ تصویرسازی و تخصیص منفی‌ها در مسیر Split حساب می‌شود و هزینهٔ تشخیص ساختار هم H نام دارد. محاسبات هر دو مسیر در این مقایسه ترتیبی‌اند و زمان موازی را بررسی نمی‌کنیم. در این پیاده‌سازی، یکی‌سازی کلاس‌ها روی همهٔ رکوردهای حالت آن نامزد عبور می‌کند؛ این جزئیات برای کران پایین مهم است. هزینهٔ داخلی مرتب‌سازی، هش، کپی رشته و حساب بیتی جداگانه در این شمارنده نیست. بنابراین نتیجه، تضمین میلی‌ثانیه روی هر کامپیوتر نیست. در دو خانوادهٔ اصلی، برابری زبان خروجی را هم اثبات می‌کنیم تا کاهش هزینه را با تغییر نتیجه اشتباه نگیریم.''',60,'Section 1',OWN+' '+STD)

add('Can the partition explain the labels?',[
E('Pᵢ = πᵢ(S⁺),     V(w) = { i : πᵢ(w) ∉ Pᵢ }'),
E('A consistent AND model exists  ⇔  V(w) ≠ ∅ for every w ∈ S⁻'),
F('Necessity: a negative forced positive in every block must be accepted.'),
F('Sufficiency: choose Lᵢ=Pᵢ. Their AND product accepts S⁺ and rejects S⁻.'),
F('Assign each negative to its highest-index witness. Other projections stay unlabeled.'),
F('Local state sizes are unbounded. Special families imply feasibility without a separate scan.')],
'''اول باید بدانیم این افراز اصلاً با برچسب‌های داده قابل توضیح هست یا نه. برای هر مؤلفه، تصویر همهٔ مثبت‌ها تعهد مثبت ایجاد می‌کند و آن را P می‌نامیم. برای یک منفی، شاهد مؤلفه‌ای است که تصویر آن منفی جزو تعهدهای مثبتش نباشد. قضیه می‌گوید وجود دست‌کم یک شاهد برای هر منفی، هم لازم و هم کافی است. برای ضرورت، اگر هیچ شاهدی نباشد، همهٔ مؤلفه‌ها مجبورند تصویر آن منفی را قبول کنند و AND هم آن را می‌پذیرد. برای کفایت، زبان هر مؤلفه را دقیقاً همان مجموعهٔ متناهی مثبت‌های محلی می‌گیریم؛ هر منفی در شاهد خود رد می‌شود. پس وجود مدل سازگار ثابت است. برای اجرای یادگیری، هر منفی را فقط به شاهد با بزرگ‌ترین اندیس می‌دهیم. تصویرهای دیگر را خودکار منفی نمی‌کنیم. هر یادگیرندهٔ محلی سازگار با این قیود، محصولی سازگار با کل نمونه می‌دهد. این تخصیص، کشف علت واقعی رد شدن تریس نیست.''',90,'Theorem 1; Appendix 16')

add('The certificate boundary',[
E('LG ≤ WG ≤ UG,     LS ≤ WS ≤ US'),
E('US < LG  ⇒  WS < WG'),
E('H + US < LG  ⇒  selection plus Split beats always Global'),
F('The symmetric test certifies Global. Bounds use sample features before any merge.'),
F('UNKNOWN means these tests do not decide. A better test may still exist.')],
'''مرز تصمیم ما با یک زنجیرهٔ نامساوی تعریف می‌شود. از ویژگی‌های داده کران پایین و بالای هزینهٔ هر مسیر را به دست می‌آوریم. اگر حتی کران بالای Split از کران پایین Global کمتر باشد، اجرای Split قطعاً کار کمتری انجام می‌دهد. اثباتش مستقیم است: هزینهٔ واقعی Split حداکثر کران بالای خودش و هزینهٔ واقعی Global حداقل کران پایین خودش است. اما برای سود کل انتخاب، H را هم اضافه می‌کنیم. اگر مجموع هزینهٔ انتخاب و بدترین هزینهٔ Split از کمترین هزینهٔ Global کمتر باشد، انتخاب‌گر واقعاً نسبت به همیشه جهانی اجرا کردن سود دارد. جهت مقابل مشابه است. این ویژگی‌ها پیش از ادغام محاسبه می‌شوند. اگر شرط‌ها جدا نشوند، خروجی نامعلوم است. این نامعلوم دربارهٔ قدرت همین گواهی است و به معنی تساوی هزینه‌ها یا ناممکن بودن هر روش تصمیم‌گیری نیست. در شاخهٔ عمومی، هزینهٔ کامل استخراج ویژگی‌ها هنوز گواهی خالص ندارد؛ تضمین خالص را فقط جایی اعلام می‌کنیم که H پوشش داده شده باشد.''',90,'Sections 3 and 10; Appendices 17 and 18')

add('A certified Global region',[
F('Assume k>1, at least one positive, and all observed symbols lie in one block.'),
F('The active local run equals Global. Each inactive factor costs four events.'),
E('WS − WG = Π + 4(k−1) > 0'),
F('Π is Split preparation work. Both output languages are identical.'),
E('A net Global certificate also requires H < Π + 4(k−1).')],
'''اولین ناحیهٔ روشن مربوط به داده‌ای است که همهٔ حروف مشاهده‌شده، چه مثبت و چه منفی، در یک بلوک باشند و دست‌کم یک مثبت داشته باشیم. روی بلوک فعال، تصویر همان تریس اصلی است. روی بلوک‌های دیگر، تنها مثبت محلی رشتهٔ خالی می‌شود و منفی‌ای هم نمی‌توان به آن‌ها داد، چون تصویر منفی آنجا همان رشتهٔ خالیِ مثبت است. پس اجرای عامل فعال دقیقاً همان اجرای Global است، با همان ترتیب و شمارش هزینه. هر عامل غیرفعال چهار رویداد هزینه دارد و تصویرسازی هم هزینهٔ جدا دارد؛ بنابراین اختلاف هزینه دقیقاً فرمول اسلاید است و مثبت است. زبان خروجی هم برابر است، چون Global حرفی خارج از دادهٔ مثبت اختراع نمی‌کند. بااین‌حال، برای سود خالص باید هزینهٔ تشخیص از همین اختلاف کمتر باشد. این شرط را حذف نمی‌کنیم. همچنین اگر پیاده‌سازی دیگری بلوک‌های غیرفعال را حذف کند، دیگر هزینهٔ همین مسیر را ندارد و باید جدا تحلیل شود.''',90,'Theorem 2; Appendix 19')

add('A certified Split family',[
E('B₁={a}, B₂={b}, B₃={c},     n≥1'),
F('Positives are exactly all words over {a,b} with n copies of each symbol.'),
E('S⁻={c},     P=|S⁺|=C(2n,n),     M=2nP'),
F('Recognition checks each positive histogram and the number of distinct positives.'),
F('Correct histograms plus P distinct words prove complete coverage.')],
'''برای ناحیهٔ Split یک خانوادهٔ ساختاری مشخص داریم. سه بلوک تک‌حرفی a، b و c را با همین ترتیب در نظر بگیرید. مثبت‌ها دقیقاً تمام رشته‌هایی‌اند که n حرف a و n حرف b دارند و فقط از همین دو حرف ساخته شده‌اند. تنها منفی c است و n دست‌کم یک است. تعداد مثبت‌های متمایز از انتخاب جایگاه‌های a در دو n جایگاه به دست می‌آید. مهم است که شرط، همهٔ ترتیب‌هاست؛ صرف تعداد زیاد کافی نیست. برای تشخیص این ساختار بدون یادگیری، شمار هر حرف و طول هر مثبت را بررسی می‌کنیم. اگر همه شرایط درست داشته باشند، مجموعهٔ ما زیرمجموعهٔ خانواده است. اگر تعداد اعضای متمایز نیز برابر تعداد کل اعضای ممکن باشد، به‌علت برابری اندازهٔ دو مجموعهٔ متناهی نتیجه می‌گیریم خانواده کامل است. این بررسی به اجرای RPNI یا ساخت درخت جهانی نیاز ندارد. اگر یک مثبت حذف یا رشته‌ای بیرون خانواده اضافه شود، این گواهی مشخص دیگر فرض‌های خود را ندارد.''',90,'Section 5; Appendix 20')

add('Forced work in the global run',[
E('N=C(2n+2,n+1)−1,     I=M+P+2N−1'),
F('The first candidate merges ε with the smaller balanced symbol, say a.'),
F('For every t with n−1 a symbols and n b symbols, congruence identifies t with at.'),
E('T=C(2n−1,n−1)=P/2   disjoint pairs'),
E('WG ≥ LG = I + NT')],
'''اکنون چرا می‌توانیم پیش از اجرا هزینهٔ زیادی را برای مسیر جهانی اجتناب‌ناپذیر بدانیم؟ تعداد حالت‌های درخت مثبت از شمارش پیشوندها به دست می‌آید؛ برای پیشوندی با i حرف a و j حرف b، تعداد ترتیب‌ها ضریب دوجمله‌ای مربوط است و جمع آن‌ها فرمول N را می‌دهد. هزینهٔ ساخت اولیه I نیز دقیق است. حال a را حرف کوچک‌تر فرض کنید؛ حالت آبی اول a است و با ریشه امتحان می‌شود. برای هر t که یک a کمتر و n حرف b دارد، هم t یک پیشوند معتبر است و هم at یک مثبت کامل. یکی شدن ریشه و a در یک ماشین قطعی مجبور می‌کند مقصد خواندن t از آن دو نیز یکی شود؛ یعنی حالت‌های t و at باید یکی شوند. این جفت‌ها سر مشترک ندارند، چون طول دو طرف متفاوت و نگاشت‌ها یک‌به‌یک است. بنابراین دست‌کم T کاهش کلاس لازم است. در پیاده‌سازی مرجع هر اجتماع روی تمام N رکورد عبور می‌کند، پس NT کار اجباری داریم. این دقیقاً بخش وابسته به پیاده‌سازی تخت است.''',90,'Section 6; Appendices 20 and 21')

add('Small local runs and explicit overhead',[
E('Local positives: {aⁿ}, {bⁿ}, {ε}'),
F('The marker negative goes to block 3. Each unary chain collapses in one attempt.'),
E('u(n)=2n²+17n+12'),
E('WS ≤ US = M+3P+4n²+34n+35'),
E('H=M+2P+12')],
'''بعد از تصویرسازی، تمام ترتیب‌های جهانی به یک کلمهٔ a به توان n در عامل اول و یک کلمهٔ b به توان n در عامل دوم تبدیل می‌شوند. مثبت عامل سوم هم رشتهٔ خالی است. طبق سیاست انتخاب بزرگ‌ترین شاهد، منفی c به عامل سوم می‌رود. دو عامل اول منفی ندارند. در یک زنجیرهٔ تک‌حرفی، ادغام اولین حالت با ریشه به‌دلیل قطعیت تمام زنجیره را در یک نامزد فرو می‌ریزد. با جمع هزینهٔ ساخت، دو بررسی مرز، یک تلاش، تا شدن و بازنگاشت، کران u را به دست می‌آوریم. عامل سوم بدون ادغام چهار رویداد هزینه دارد. هزینهٔ آماده‌سازی نیز حجم ورودی به‌اضافهٔ عبورهای بلوکی است؛ با دو کران تک‌حرفی جمع می‌شود و U مربوط به Split را می‌دهد. H از اعتبارسنجی الفبا، خواندن کلمات و حروف، آزمون بلوک فعال، بررسی شمار حروف هر مثبت و آزمون نهایی تعداد حاصل می‌شود. این هزینه را پنهان نکرده‌ایم و در نامساوی بعدی وارد می‌کنیم.''',90,'Sections 5 and 7; Appendix 22')

add('Net Split gain for every n≥1',[
F('For n≥3, use P≥2n² and N≥3P in the difference LG−H−US.'),
E('LG−H−US ≥ 6n⁴−4n³−34n−48 > 0'),
F('The positive lower bound follows for all n≥3, not only the tested values.'),
E('n=2:  H+US=209 < 258 ≤ WG'),
E('n=1:  H+WS=87 < 103=WG')],
'''تا اینجا فقط کران‌ها را داریم. برای نتیجهٔ نهایی باید ثابت کنیم کران بالای Split همراه H از کران پایین Global کمتر است. برای n سه به بعد اختلاف را به‌صورت نمادین باز می‌کنیم. تعداد ترتیب‌ها دست‌کم دو n مربع است؛ این با پایهٔ n سه و نسبت دو جملهٔ متوالی ضرایب دوجمله‌ای استقرایی ثابت می‌شود. N نیز دست‌کم سه برابر تعداد ترتیب‌هاست. با جایگذاری این دو کران و صعودی بودن عبارت درجه‌دو نسبت به P، اختلاف دست‌کم چندجمله‌ای روی اسلاید می‌شود. این چندجمله‌ای برای تمام nهای سه به بالا مثبت است؛ جزئیات جبری در پیوست آمده است. برای n دو، هزینه‌های اجباری بیشتری از اولین نامزد را به کران پایین اضافه می‌کنیم و به ۲۰۹ کمتر از ۲۵۸ می‌رسیم. برای n یک، شمارش مستقیم دو نامزد Global هزینهٔ ۱۰۳ و هزینهٔ Split برابر ۶۷ را می‌دهد؛ هزینهٔ تشخیص ۲۰ است. بنابراین ۸۷ کمتر از ۱۰۳ می‌شود. این سه بخش با هم تمام nهای مثبت را پوشش می‌دهند.''',90,'Sections 7 and 8; Appendices 23, 24 and 25')

add('Both methods return the same language',[
F('No global candidate can accept c, so every merge succeeds and no state is promoted.'),
F('The red set remains the root class. Termination leaves one reachable final state.'),
E('Global output = {a,b}*'),
E('Local outputs = a*, b*, {ε}.     Their AND product = {a,b}*'),
F('This proves equal outputs on all words. It does not prove target recovery.')],
'''برای مقایسهٔ کیفیت، صرف چک کردن چند رشته کافی نیست. اینجا اثبات زبان کامل داریم. هیچ نامزد جهانی انتقال c ندارد، پس همهٔ نامزدها منفی را رد می‌کنند و هیچ حالت آبی‌ای ارتقا نمی‌یابد. مجموعهٔ قرمز فقط کلاس ریشه می‌ماند. اگر هنگام پایان حالت قابل دسترس دیگری وجود داشت، اولین خروج مسیر از ریشه یک آبی ایجاد می‌کرد و الگوریتم هنوز تمام نشده بود. پس تنها یک حالت قابل دسترس داریم که به‌علت پذیرش مثبت، نهایی است. انتقال‌های a و b نیز حلقه می‌شوند و c تعریف نشده است؛ بنابراین زبان خروجی دقیقاً a و b ستاره است. دو عامل تک‌حرفی نیز a ستاره و b ستاره و عامل سوم فقط رشتهٔ خالی را می‌پذیرند. AND این تصویرها دقیقاً همان زبان جهانی است. بنابراین دو خروجی روی تمام رشته‌ها برابرند؛ اما ممکن است هر دو نسبت به هدف واقعی بیش‌تعمیم بدهند.''',60,'Section 9; Appendix 26')

add('Concrete decisions before training',[
T(['Sample','Pre-run evidence','Net choice'],[
['One active block','WS−WG=18, H=15','Global'],
['Balanced n=1','20+67 < 103','Split'],
['Balanced n=2','48+161 < 258','Split']], [300,530,280]),
F('Global example: S⁺={a,aa}, S⁻={aaa}, blocks {a},{b}.'),
F('Split n=1: S⁺={ab,ba}, S⁻={c}, blocks {a},{b},{c}.')],
'''این جدول نشان می‌دهد انتخاب‌گر دقیقاً چه اطلاعاتی را پیش از آموزش استفاده می‌کند. در مثال اول مثبت‌های a و aa و منفی aaa را روی دو بلوک داریم. همهٔ داده در یک بلوک است. آماده‌سازی ۱۴ و عامل غیرفعال چهار واحد است، پس Global هجده واحد از Split کم‌هزینه‌تر است. H پانزده واحد است و از اختلاف کمتر است؛ بنابراین سود خالص Global گواهی می‌گیرد. برای این تصمیم لازم نیست عدد کامل اجرای Global را بدانیم. در سطر دوم، مثبت‌های ab و ba و منفی c کوچک‌ترین عضو خانوادهٔ Split هستند. از اثبات ساختار ثابت می‌دانیم Split شصت‌وهفت و Global صدوسه واحد هزینه دارند؛ با بیست واحد تشخیص، مجموع هشتادوهفت است. سطر سوم از کران‌ها استفاده می‌کند و نه هزینهٔ واقعی اجرا: چهل‌وهشت به‌علاوهٔ صدوشصت‌ویک از حداقل دویست‌وپنجاه‌وهشت کمتر است. در هر سه سطر، داده و فرمول‌ها برای تصمیم کافی‌اند و اجرای یادگیری برای تولید تصمیم لازم نیست.''',90,'Sections 4 and 8')

add('Limits established by counterexamples',[
F('Equal positive and negative counts can have opposite winners.'),
F('For blocks {a},{b}, take S⁺={ε} and S⁻=∅.'),
E('WG=4, WS=10, H=7, so H+WG=11>10'),
F('Equal learned languages can both differ from the true target.'),
F('The marker c never rejects a candidate in the Split family.'),
F('Different merge implementations or output requirements need new cost proofs.')],
'''چند تعمیم ظاهراً طبیعی را عمداً با مثال نقض رد کرده‌ایم. اول، تعداد مثبت و منفی به‌تنهایی تعیین‌کننده نیست: می‌توان دو مجموعه با تعداد برابر ساخت که یکی Split و دیگری Global را ترجیح دهد؛ حتی در اندازه‌های بدون کران. دوم، کم‌هزینه‌تر بودن خودِ Global الزاماً سودمند بودن انتخاب‌گر را ثابت نمی‌کند. اگر تنها مثبت رشتهٔ خالی باشد، Global چهار، Split ده و تشخیص هفت واحد هزینه دارد؛ پس انتخاب به‌علاوهٔ Global یازده می‌شود و از ده بدتر است. در این حالت فقط برندهٔ مسیر را می‌دانیم، نه سود خالص را. سوم، برابری خروجی‌ها بازیابی هدف نیست؛ مثلاً هدف واقعی می‌تواند فقط ab و ba باشد، ولی دو خروجی ما حتی رشتهٔ خالی را قبول می‌کنند. همچنین منفی c در خانوادهٔ اثبات‌شده هیچ ادغامی را رد نمی‌کند؛ پس نتیجه را به همهٔ داده‌های دارای منفی اثرگذار تعمیم نمی‌دهیم. تغییر الگوریتم ادغام یا ساخت محصول صریح هم قرارداد هزینه را عوض می‌کند.''',90,'Sections 4, 9 and 11; Appendix 27')

add('The two answers we can defend',[
F('A recognizable structural region can support a rigorous pre-training certificate.'),
F('With the known partition, the certificate chooses the lower-work fixed pipeline.'),
F('Net decisions include selection work and equal output languages in the admitted families.'),
F('Outside the certified region, return UNKNOWN or a clearly labeled cost-only result.'),
F('The result is conditional on the explicit Wref implementation contract.')],
'''پاسخ محور اول این است که می‌توانیم ناحیه‌هایی با شرط‌های روشن و قابل بررسی روی داده تعریف کنیم که صدور گواهی در آن‌ها ممکن است. این ناحیه صرفاً حداقل تعداد تریس نیست؛ محتوای تریس و پوشش ساختاری نقش دارد. پاسخ محور دوم این است که وقتی افراز معلوم و شرط‌های قضیه برقرار باشد، گواهی می‌تواند پیش از آموزش مشخص کند کدام اجرای ثابت کار کمتری انجام می‌دهد. در خانواده‌های اصلی، برابری زبان خروجی نیز اثبات شده و برای اعلام سود خالص، هزینهٔ تشخیص هم پرداخت شده است. خارج از این شرایط، نامعلوم یا صرفاً گواهی هزینه را صریح برمی‌گردانیم و هیچ تضمین اضافه‌ای القا نمی‌کنیم. این نتیجه را تحت قرارداد دقیق پیاده‌سازی و شمارش عملیات ارائه می‌کنیم. اثبات‌های تفصیلی در پیوست همین پاورپوینت و گزارش همراه هستند و بررسی‌های متناهی فقط تطبیق کد با آن اثبات‌ها را کنترل می‌کنند.''',60,'Sections 1 and 10')

# Fourteen proof-appendix slides.
add('Appendix: the exact algorithm and cost',[
F('Positive partial trie. Missing transitions reject. Initial red set is {ε}.'),
F('Least shortlex blue state, then red states in shortlex order. Final classes use OR.'),
F('Keep a quotient iff all negatives reject. Promote blue only after all red candidates fail.'),
F('Charge input, created states/edges, fringes, candidates, folds, negative scans and red remaps.'),
F('Flat relabel scans retain all q original records during a candidate. Sparse labels only.'),
F('Library internals, diagnostics, product construction and elapsed time are outside Wref.')],
'''قرارداد کامل در بخش یک گزارش آمده است. حالت‌ها با پیشوند نام‌گذاری می‌شوند؛ نمایندهٔ هر کلاس کوچک‌ترین نام در ترتیب طول و سپس واژه‌نامه است. در هر دور حالت آبی کوچک‌تر انتخاب می‌شود و قرمزها به همین ترتیب امتحان می‌شوند. کلاس ادغام‌شده نهایی است اگر دست‌کم یک عضو نهایی داشته باشد. فقط نامزدی نگه داشته می‌شود که تمام منفی‌ها را رد کند. هر اجتماع موفق در نگاشت تخت q رکورد اولیهٔ همان نامزد را پیمایش می‌کند و رکوردها تا بازسازی حذف نمی‌شوند. کار انتخاب‌گر و یادگیرنده از رویدادهای پیمایش تعریف‌شده شمرده می‌شود؛ مرتب‌سازی، هش، ساخت مجموعه، کپی رشته، تخصیص حافظه و حساب بیتی هزینهٔ رویداد جدا ندارند. خروجی یک ماشین پراکنده یا مجموعهٔ عوامل است و ساخت محصول و کمینه‌سازی در هزینه نیست. این محدودیت‌ها برای تفسیر درست تمام اعداد لازم‌اند.''',proof='Section 1',source=OWN+' '+STD)

add('Appendix: feasibility in both directions',[
E('Pᵢ=πᵢ(S⁺),     V(w)={i: πᵢ(w)∉Pᵢ}'),
F('Any product accepting S⁺ must have Pᵢ⊆Lᵢ in every factor.'),
F('If V(w)=∅, every factor accepts πᵢ(w). The negative w must then be accepted.'),
F('If every V(w) is nonempty, choose finite regular Lᵢ=Pᵢ. Each negative fails a witness.'),
F('Assign w to max V(w). Its assigned projection lies outside local positives.'),
F('Any consistent local learners then yield a sample-consistent AND product. Empty words stay.')],
'''برای ضرورت، هر مثبت جهانی باید در تمام عوامل پذیرفته شود، پس تمام P_i در زبان عامل i قرار می‌گیرد. منفی‌ای که تصویرش در همهٔ P_iها باشد دیگر قابل رد نیست و تناقض می‌دهد. برای کفایت، خودِ مجموعهٔ متناهی P_i را زبان عامل می‌گیریم؛ منظم بودن آن روشن است و هر منفی در یک شاهد رد می‌شود. این استدلال مثبت یا منفی تهی و رشتهٔ خالی را نیز پوشش می‌دهد. برای تخصیص، تصویر یک منفی فقط در عامل شاهد منفی می‌شود و بنا بر تعریف شاهد با P_i تداخل ندارد. هر یادگیرندهٔ محلی سازگار با این داده‌ها همهٔ مثبت‌های جهانی را می‌پذیرد و برای هر منفی، عامل تخصیص‌یافته رد ایجاد می‌کند. همچنین محصول زبان‌های P_i زیرمجموعهٔ هر محصول پذیرندهٔ مثبت‌هاست؛ این کمینگی به شمول است، نه به تعداد حالت.''',proof='Section 2')

add('Appendix: termination and candidate bound',[
E('N=initial states, q=current states, r=red classes. Initially q−r=N−1.'),
F('Promotion decreases q−r by one. A kept blue/red merge decreases it by at least one.'),
F('Extra red/red identifications reduce q and r equally. Other identifications cannot increase q−r.'),
E('Iterations ≤ N−1,     fringe computations ≤ N'),
E('At iteration t: r≤t+1. Summing gives A≤N(N−1)/2, also zero for N=1.'),
F('Positive paths survive every quotient. Kept candidates explicitly reject all negatives.')],
'''تابع پتانسیل q منهای r نامنفی است. ارتقای آبی تعداد قرمزها را یکی زیاد می‌کند و تعداد حالت را تغییر نمی‌دهد. در ادغام موفق حتماً یک کلاس غیرقرمز با قرمز یکی می‌شود و پتانسیل کم می‌شود. یکی شدن دو قرمز هر دو شمار را یکسان کم می‌کند؛ ادغام‌های دیگر هم پتانسیل را زیاد نمی‌کنند. پس حداکثر N منهای یک دور اصلی و یک بررسی مرز نهایی داریم. در دور t که از صفر شماره می‌زنیم تعداد قرمزها حداکثر t به‌اضافهٔ یک است و همین تعداد نامزد بیشتر امتحان نمی‌شود. جمع این کران در دورها عدد مثلثی را می‌دهد. مسیرهای مثبت و نهایی بودن مقصدشان در خارج‌قسمت حفظ می‌شوند؛ درخت اولیه منفی‌ها را به‌علت نبود تناقض برچسب رد می‌کند و هر نامزد نگه‌داشته‌شده این رد را کنترل می‌کند. بنابراین خاتمه و سازگاری یادگیرنده هر دو برقرارند.''',proof='Section 3')

add('Appendix: fold and static work bounds',[
E('F(q,e)=qe+q²+3q+e'),
F('Here p=|S⁺|, M=positive symbol volume, N=trie states. A fold has ≤q−1 unions and ≤q closure passes.'),
F('Initialization and reconstruction add 2q+e. Hence fold work ≤F(q,e).'),
E('I=M+p+2N−1, E=N−1, D=∑ (|w|+1) over S⁻, B=N(N−1)/2'),
E('I ≤ Wref ≤ U=I+N(3N+E)+B(1+F(N,E)+D)'),
F('Fringes contribute N(2N+E), red remaps at most N². General extraction overhead is extra.')],
'''هر اجتماع موفق تعداد کلاس‌ها را کم می‌کند، پس حداکثر q منهای یک اجتماع داریم و هر کدام q رکورد را می‌پیماید. هر دور مولد بستن قطعیت دست‌کم یک اجتماع تازه دارد و یک دور نهایی بی‌تغییر هم داریم؛ q دور کران امن است. نگاشت اولیه و بازسازی حالت‌ها دو q و بازسازی انتقال‌ها e هزینه دارد. جمع این‌ها حتی از F نوشته‌شده کمی کوچک‌تر است. در اجرای کامل، تعداد حالت و انتقال با ادغام زیاد نمی‌شود. ساخت درخت اولیه دقیقاً I است. حداکثر N مرز هرکدام دو N و E، حداکثر N مربع بازنگاشت قرمز و حداکثر B نامزد با یک تلاش، یک F و حداکثر D آزمون منفی داریم. جمع همان U را می‌دهد. این‌ها کران هزینهٔ مسیرها هستند؛ ساخت ویژگی‌ها هزینهٔ جدا دارد. در شاخهٔ عمومی هنوز آن هزینه کامل کران نخورده و برابری زبان دو خروجی هم ادعا نمی‌شود.''',proof='Section 3')

add('Appendix: Global equality and net condition',[
F('Active projection is identity. Here p,z count positive/negative words and M,M⁻ count their symbols.'),
F('Every inactive block has Pᵢ={ε}. A negative cannot be assigned there.'),
F('The active run equals Global. Each inactive run costs 2 initialization + 2 fringe events.'),
E('Π=M+M⁻+k(p+2z),     WS−WG=Π+4(k−1)'),
E('H=|Σ|+2k+p+z+M+M⁻.     Net gain requires H<WS−WG.'),
F('Global introduces no outside label. Inactive ε factors impose exactly the same restriction.')],
'''مثبت غیرتهی تضمین می‌کند روی هر بلوک غیرفعال دقیقاً مجموعهٔ مثبت رشتهٔ خالی داریم. تصویر منفی نیز آنجا رشتهٔ خالی است و شاهد نمی‌شود. روی بلوک فعال، تصویر هویت است و چون مثبت و منفی اصلی جدا هستند، هر منفی شاهد فعال دارد. اگر منفی نداریم این جمله تهی است و مشکلی ندارد. اجرای عامل فعال از نظر داده، ترتیب و هزینه با Global یکی است؛ حروف استفاده‌نشده در پیاده‌سازی پراکنده هزینهٔ اضافی ایجاد نمی‌کنند. هر عامل غیرفعال چهار رویداد دارد. جمع آماده‌سازی و این عوامل اختلاف دقیق هزینه را می‌دهد. فرمول H از عبور روی k بلوک و اندازهٔ الفبا، تمام کلمات و حروف و دوباره k آزمون بلوک فعال حاصل می‌شود. سود خالص فقط با شرط H کوچک‌تر از اختلاف اعلام می‌شود. برای زبان، Global فقط از حروف بلوک فعال انتقال دارد و عوامل رشتهٔ خالی دقیقاً همین محدودیت را اعمال می‌کنند.''',proof='Section 4')

add('Appendix: count all positive prefixes',[
F('A prefix with i copies of a and j copies of b has C(i+j,i) distinct schedules.'),
F('Every such prefix with 0≤i,j≤n extends to a positive word.'),
E('N = ∑ over i=0..n and j=0..n of C(i+j,i)'),
E('∑ over j=0..n of C(i+j,i) = C(i+n+1,i+1)'),
E('N = C(2n+2,n+1)−1'),
F('C(m,r) counts r chosen positions among m. Both equalities use hockey-stick sums.')],
'''یک پیشوند را با تعداد حروف مصرف‌شده از دو کلمهٔ a به توان n و b به توان n مشخص می‌کنیم. اگر i و j مصرف شده باشد، با انتخاب جایگاه‌های a تعداد ترتیب‌ها ضریب دوجمله‌ای نوشته‌شده می‌شود. این رشته‌ها متمایزند و هر کدام با اضافه کردن باقی‌ماندهٔ حروف به یک مثبت کامل می‌رسند. پس همه و فقط حالت‌های درخت مثبت را شمرده‌ایم. جمع داخلی روی j با هویت چوب‌هاکی برابر ضریب دوجمله‌ای سطر بعد است. برای جمع روی i هم همان هویت را به‌کار می‌بریم؛ جملهٔ i منهای یک را اضافه و بعد یک واحد کم می‌کنیم. نتیجه فرمول بستهٔ N است. شمارش شامل ریشه است. روی هر عامل تک‌حرفی فقط زنجیرهٔ پیشوندهای یک کلمهٔ طول n را داریم، یعنی n به‌اضافهٔ یک حالت.''',proof='Sections 5 and 6')

add('Appendix: the forced unions lower bound',[
F('Choose a as the smaller balanced symbol. The first merge identifies ε with a.'),
F('For each t with n−1 copies of a and n copies of b, states t and at both exist.'),
F('Deterministic congruence forces their identification along the defined t paths.'),
F('The T=P/2 pairs have disjoint endpoints. A class containing s pairs needs ≥2s−1≥s reductions.'),
E('At least T unions each scan N retained records. Thus WG≥I+NT.'),
F('No c edge exists, so this candidate rejects c and is kept.')],
'''فرض a کوچک‌تر بودن بدون از دست رفتن کلیت است، چون دو حرف نقش متقارن دارند. هر t با n منهای یک a و n حرف b یک پیشوند معتبر است و با اضافه کردن a تکمیل می‌شود؛ از طرف دیگر at مثبت کامل است. وقتی ریشه با a یکی شود، خاصیت قطعیت روی مسیرهای t که هر دو در درخت تعریف شده‌اند مقصدها را یکی می‌کند. تعداد tها نصف تعداد مثبت‌هاست. دو سر هیچ دو جفتی مشترک نیست، چون رشته‌های t هم‌طول و متمایزند، رشته‌های at هم متمایزند و طول دو طرف متفاوت است. ممکن است یک کلاس چند جفت را در خود جمع کند؛ این ایراد کران را از بین نمی‌برد. کلاس دارای s جفت، دست‌کم دو s عضو دارد و دست‌کم دو s منهای یک کاهش کلاس می‌خواهد که از s کمتر نیست. جمع این کران روی کلاس‌ها دست‌کم T اجتماع می‌دهد. هر اجتماع N رکورد نگه‌داشته‌شدهٔ نامزد را می‌بیند. این هزینه با I مشترک نیست.''',proof='Section 6')

add('Appendix: local work and recognition work',[
E('Ilocal=3n+2,     F(n+1,n)=2n²+7n+4'),
E('u(n)=(3n+2)+2(3n+2)+1+F(n+1,n)+(n+1)'),
E('u(n)=2n²+17n+12'),
E('Π=M+1+3(P+2)=M+3P+7'),
E('US=Π+2u(n)+4=M+3P+4n²+34n+35'),
E('H=6+(M+P+2)+3+P+1=M+2P+12')],
'''در عامل تک‌حرفی n به‌اضافهٔ یک حالت و n انتقال داریم. ادغام اولین a با ریشه تمام زنجیره را به‌علت قطعیت می‌خواباند و چون منفی‌ای نداریم اولین نامزد نگه داشته می‌شود. بنابراین یک نامزد، دو بررسی مرز و یک بازنگاشت داریم. هر مرز را با سه n به‌اضافهٔ دو کران می‌زنیم و بازنگاشت را با n به‌اضافهٔ یک؛ این‌ها با I و F جمع می‌شوند و u را می‌دهند. عامل سوم فقط مثبت رشتهٔ خالی و منفی c دارد؛ نامزد ندارد و چهار رویداد می‌پردازد. آماده‌سازی یک عبور روی M به‌اضافهٔ یک حرف ورودی، سه بلوک برای هر مثبت و دو عبور سه‌بلوکی برای منفی است. برای H، شش بازدید اعتبارسنجی افراز، بازدید کلمات و حروف ورودی، سه آزمون بلوک فعال، P بررسی شمارش مثبت و یک آزمون نهایی تعداد داریم. عملیات داخلی کتابخانه و حساب اعداد مطابق قرارداد هزینهٔ مجزا ندارند.''',proof='Sections 5 and 7')

add('Appendix: prove the inequality for all n≥3',[
E('LG−H−US=P(N/2−2n−4)+2N−4n²−34n−48'),
F('Induction: P(3)=20≥18, P(n+1)/P(n)≥3 and 3n²≥(n+1)².'),
E('N=(4−2/(n+1))P−1 ≥ 3P'),
E('LG−H−US ≥ 3P²/2−(2n−2)P−4n²−34n−48'),
E('≥ 6n⁴−4n³−34n−48'),
E('≥ n(14n²−34)−48 ≥ 3·92−48 > 0')],
'''ابتدا اختلاف را با T برابر P روی دو به‌طور دقیق بسط می‌دهیم. برای P دست‌کم دو n مربع، پایهٔ n سه بیست در برابر هجده است. نسبت جملهٔ بعد P به فعلی دو ضرب در دو n به‌اضافهٔ یک تقسیم بر n به‌اضافهٔ یک است که دست‌کم سه می‌شود؛ و سه n مربع برای n حداقل دو از n به‌اضافهٔ یک به توان دو کمتر نیست، پس استقرا کامل است. برای N، ضریب چهار منهای دو روی n به‌اضافهٔ یک در n حداقل سه دست‌کم سه‌ونیم است و P دست‌کم بیست، پس پس از کم کردن یک هنوز حداقل سه P می‌ماند. عبارت درجه‌دو حاصل نسبت به P در ناحیهٔ P حداقل دو n مربع صعودی است؛ مشتقش سه P منهای دو n به‌اضافهٔ دو مثبت است. جایگذاری، چندجمله‌ای درجه‌چهار را می‌دهد. دو جملهٔ اول آن برابر دو n مکعب ضرب در سه n منهای دو و دست‌کم چهارده n مکعب است. ادامهٔ نامساوی روی اسلاید مثبت بودن را برای تمام nهای سه به بالا ثابت می‌کند.''',proof='Section 7')

add('Appendix: the sharper bound covers n=2',[
F('Beyond the NT union visits, the first candidate initializes and rebuilds N records.'),
F('Closure and edge reconstruction contribute at least 2E. Initial fringe adds 2N+E.'),
F('Attempt, negative word/symbol and red remap add four events. These terms do not overlap.'),
E('L′G=I+NT+4N+3E+4=LG+7N+1'),
E('n=2: P=6, M=24, N=19, I=67, T=3'),
E('H+US=48+161=209 < 67+57+134=258 ≤ WG')],
'''کران اولیه فقط I و بازدیدهای اجتماع را حساب می‌کرد. در اولین نامزد، نگاشت اولیه یک N و بازسازی حالت‌ها یک N دیگر دارد. حداقل یک عبور بستن و یک عبور بازسازی هر کدام E انتقال را می‌بینند. مرز اولیه نیز دو N به‌اضافهٔ E دارد. یک تلاش، یک بازدید کلمهٔ منفی، یک بازدید نماد c برای انتقال تعریف‌نشده و یک بازنگاشت قرمز چهار واحد اضافه می‌کنند. اولین نامزد قطعاً نگه داشته می‌شود چون c هیچ انتقالی ندارد. این اجزا با I و پیمایش اجتماع‌ها هم‌پوشانی ندارند، پس جمعشان مجاز است. با E برابر N منهای یک، افزایش کران هفت N به‌اضافهٔ یک می‌شود. برای n دو مقادیر روی اسلاید را جایگذاری می‌کنیم؛ کران پایین دویست‌وپنجاه‌وهشت و مجموع کران بالا و H دویست‌ونه است. بنابراین این مورد نیز سود خالص دارد.''',proof='Sections 6 and 8')

add('Appendix: exact accounting for n=1',[
T(['Fold','q, e, unions, passes','2q + uq + de + e'],[
['First','5, 4, 2, 2','32'],['Second','3, 3, 2, 2','21']],[180,460,470]),
E('WG=15+(14+9+4)+32+21+8=103'),
E('Unary=5+8+8+2=23.     WS=17+23+23+4=67'),
E('H=20,     H+WS=87<103')],
'''درخت اولیه پنج حالت و چهار انتقال دارد. اولین ادغام، کلاس‌های ریشه و a، کلاس b و ab و کلاس ba را می‌دهد. گذر اول انتقال‌ها b و ab را یکی می‌کند و گذر دوم بی‌تغییر است. ادغام بعدی کلاس ریشه و b را یکی می‌کند و تضاد مقصد a، کلاس ba را نیز به آن می‌پیوندد؛ باز یک گذر مولد و یک گذر بدون تغییر داریم. پس جدول تعداد حالت، انتقال، اجتماع و گذر هر نامزد را دقیق می‌دهد. هزینهٔ تا شدن برابر دو q برای نگاشت و بازسازی، u ضربدر q برای اجتماع‌ها، d ضربدر e برای بستن و e برای بازسازی انتقال است. سه مرز چهارده، نه و چهار؛ ساخت اولیه پانزده؛ و دو تلاش، چهار بازدید منفی و دو بازنگاشت هشت واحدند. هر عامل تک‌حرفی پنج واحد ساخت، هشت مرز، هشت تا شدن و دو تلاش و بازنگاشت دارد. با هفده آماده‌سازی و چهار عامل نشانگر، هزینه‌ها کامل جمع شده‌اند. این یک اثبات مستقیم برای ساختار ثابت است؛ انتخاب‌گر در زمان تصمیم فقط آن ساختار را می‌شناسد و از ثابت‌های اثبات‌شده استفاده می‌کند.''',proof='Section 8')

add('Appendix: equality on every word',[
F('No quotient invents a c edge. Every candidate rejects c and succeeds.'),
F('No blue state is promoted. The red set remains the image of the single root.'),
F('Every quotient class is reachable by an image of its original trie path.'),
F('A reachable nonroot state would give a first exit from the root to a blue state at termination.'),
F('Thus one final state remains, with a and b loops and no c transition.'),
E('L(Global)={a,b}*=π₁⁻¹(a*) ∩ π₂⁻¹(b*) ∩ π₃⁻¹({ε})')],
'''ابتدا چون هیچ یال c در درخت مثبت نیست و ادغام برچسب تازه نمی‌سازد، هیچ منفی‌ای پذیرفته نمی‌شود. بنابراین همهٔ نامزدهای مطرح‌شده نگه داشته می‌شوند و هیچ ارتقایی نداریم؛ قرمز فقط تصویر ریشه است. هر کلاس خارج‌قسمت قابل دسترس باقی می‌ماند، زیرا مسیر پیشوند اصلی آن با نگاشت کلاس‌ها یک مسیر از ریشه به آن کلاس می‌دهد. اگر در پایان کلاس دیگری وجود داشت، یک مسیر کوتاه‌ترین به آن انتخاب می‌کردیم. اولین خروج از ریشه، یالی از قرمز به غیرقرمز ایجاد می‌کرد که هدفش آبی است؛ این با پایان الگوریتم تناقض دارد. یک حالت قابل دسترس داریم که نهایی است، چون مثبت غیرتهی مجموعه‌ای داریم و مسیر مثبت باید به یک حالت نهایی برسد. انتقال‌های a و b به‌علت حضور در مثبت‌ها حفظ شده‌اند و روی همان حالت حلقه می‌شوند. عوامل محلی با استدلال زنجیره، a ستاره و b ستاره و رشتهٔ خالی‌اند. معکوس تصویر AND آن‌ها دقیقاً رشته‌های بدون c است و همان زبان جهانی می‌شود.''',proof='Section 9')

add('Appendix: counterexamples to broader claims',[
F('Equal counts: compare the complete balanced family with positives a,…,aᴾ and negative aᴾ⁺¹.'),
F('Both have P positives and one negative. Split wins the first, Global wins the second.'),
F('For blocks {a},{b}, S⁺={ε}, S⁻=∅ gives H+WG=7+4=11>WS=10.'),
F('Target recovery: {ab,ba} is a decomposed target, but both learned outputs accept ε.'),
F('A failed family recognizer or overlapping bounds does not prove fundamental impossibility.')],
'''برای تعداد برابر، n حداقل سه و P برابر ضریب دوجمله‌ای خانواده را بگیرید. دادهٔ اول طبق قضیهٔ Split سود خالص دارد. دادهٔ دوم فقط حرف a دارد و طبق قانون تک‌بلوک Global کم‌هزینه‌تر است. افراز و تعداد مثبت و منفی یکسان است، پس تابعی که فقط این شمارها را ببیند نمی‌تواند هر دو برنده را درست برگرداند. اندازهٔ P بدون کران است. ادعای برابر بودن طول‌ها یا تمام ویژگی‌های ایستا نداریم. مثال H نشان می‌دهد برندهٔ مسیر الزاماً برندهٔ فرایند انتخاب نیست. مثال کیفیت هم واقعاً یک هدف تجزیه‌پذیر دارد: زبان عوامل a و b هر کدام فقط همان حرف و عامل c فقط رشتهٔ خالی است؛ محصول دقیقاً ab و ba را می‌پذیرد. دادهٔ آموزشی با آن سازگار است ولی خروجی هر دو روش ستاره است و رشتهٔ خالی را هم می‌پذیرد. این‌ها محدودهٔ ادعا را مشخص می‌کنند و به معنی نقص در قضیهٔ محدودشده نیستند.''',proof='Sections 4, 9, 10 and 11')

add('Appendix: sources and verification evidence',[
F('RPNI background: Björklund, Björklund and Martens, Learning Algorithms, Section 4.'),
F('Full statements, dependencies and proofs: Proofs_and_Audit_EN.md.'),
F('Finite audit: 2,339 labeled samples and 14,845 independently checked candidate quotients.'),
F('Set-partition oracle and exact language-product checks supplement the mathematical proofs.'),
F('Reproduce with audit_defense.py. No universal runtime or target-recovery guarantee is claimed.')],
'''مرجع آموزشی فقط پیش‌زمینهٔ RPNI و ادغام حالت‌ها را پشتیبانی می‌کند؛ قضیه‌های هزینهٔ خاص را از آن نقل نمی‌کنیم و اثبات‌هایشان در گزارش همراه آمده است. ممیزی فعلی ۲۳۳۹ نمونهٔ برچسب‌خورده دارد: تمام ۲۱۸۷ حالت کوچک دودویی، خانواده‌های تغییرنام‌یافته، زیرمجموعه‌ها و تغییرات منفی و مثبت، مثال هزینهٔ انتخاب و مثال‌های تعداد برابر. پنج ورودی نامعتبر و یک مثال بازیابی هدف نیز جدا کنترل شده‌اند. در ۱۴۸۴۵ نامزد، خارج‌قسمت با بررسی‌کننده‌ای مبتنی بر مجموعهٔ کلاس‌ها و بستن تعهد انتقال مقایسه شد؛ این ساختار با نگاشت تخت کد مرجع متفاوت است. همچنین یادگیرندهٔ دوم و بررسی دقیق حاصل‌ضرب زبان‌ها به‌کار رفته‌اند. این عددها شواهد متناهی تطابق کد و اثبات‌اند، نه جایگزین استدلال برای همهٔ nها یا تأیید داوری علمی.''',proof='Section 12',source=OWN+' '+STD)

slides[2]['notes']=slides[2]['notes'].replace('در دو خانوادهٔ اصلی، برابری زبان خروجی را هم اثبات می‌کنیم تا کاهش هزینه را با تغییر نتیجه اشتباه نگیریم.','خروجی Split به‌صورت عوامل باقی می‌ماند؛ ساخت محصول صریح و کمینه‌سازی جزو این هزینه نیست.')
slides[3]['notes']+=' این قضیه برای زبان‌های منظم محلی بدون کران تعداد حالت است. در دو خانوادهٔ خاص، شرط امکان‌پذیری از ساختار خانواده نتیجه می‌شود و آزمون عمومی جداگانه‌ای پیش از آن‌ها اجرا نمی‌کنیم.'
slides[17]['notes']='در این اسلاید p تعداد مثبت‌ها، M مجموع طول مثبت‌ها و N تعداد حالت‌های درخت مثبت با ریشه است. '+slides[17]['notes']
slides[0]['blocks'][0]=F('Two questions: a certified region and the right choice')
slides[4].update(title='Q1: Can we recognize a certified region?',blocks=[
F('Yes. Define the certified region C = G ∪ S by exact input conditions.'),
F('G: one active block, with the strict net-gain condition on slide 6.'),
F('S: the complete balanced family with the last-block marker on slide 7.'),
F('Membership uses only the traces and known partition. No RPNI run is needed.'),
F('These conditions are sufficient. They do not characterize every cheaper input.'),
F('Outside C, this two-region theorem gives no net-choice guarantee.')],notes='''سؤال اول را صریح پاسخ می‌دهم: آیا می‌توانیم مرز مشخصی روی خود داده بگذاریم؟ بله، ناحیهٔ C را اجتماع دو مجموعهٔ G و S تعریف می‌کنیم. G داده‌ای است که همهٔ حروف مشاهده‌شده در یک بلوک قرار دارند، دست‌کم یک مثبت داریم و شرط دقیق سود خالص برقرار است. S خانوادهٔ کامل تریس‌های متوازن با منفی نشانگر در آخرین بلوک است. در دو اسلاید بعد، شرایط عضویت را کاملاً مشخص می‌کنم. تشخیص عضویت فقط ورودی و افراز را می‌خواند و هیچ یادگیرنده‌ای اجرا نمی‌کند. برای G یک نامساوی عددی دقیق داریم. برای S نیز شمار حروف و برابری تعداد اعضای متمایز با اندازهٔ خانواده، کامل بودن را اثبات می‌کند. پس عضویت در همین ناحیه با قطعیت قابل تشخیص است. ادعای ما این نیست که هر دادهٔ بیرون C غیرقابل تصمیم است؛ فقط این قضیه برای آن داده تضمین سود خالص نمی‌دهد. ناحیهٔ قابل گواهی را دقیق مشخص کرده‌ایم، بدون ادعای پیدا کردن بزرگ‌ترین ناحیهٔ ممکن.''',proof='Section 10, Two-region theorem; Appendices 19–25')
slides[5]['blocks']=[
F('Assume k>1, p=|S⁺|>0, and all observed symbols lie in one block.'),
F('The active run equals Global. Each inactive factor costs four events.'),
E('WS − WG = Π + 4(k−1) > 0'),
F('Both output languages are equal. Region G adds the exact net condition:'),
E('(k−1)p + (2k−1)z + 2k−4 > |Σ|'),
F('Here z=|S⁻|. This inequality is exactly H < Π + 4(k−1).')]
slides[5]['notes']+=' با کم کردن فرمول H از اختلاف هزینه، حجم حروف حذف می‌شود و شرط نهایی به تعداد مثبت و منفی، تعداد بلوک‌ها و اندازهٔ الفبا تبدیل می‌شود. نامساوی اسلاید دقیقاً همین شرط است؛ تساوی کافی نیست. این یک شرط لازم و کافی برای سود خالص همین شاخه در خانوادهٔ تک‌بلوک است، نه برای همهٔ داده‌ها.'
slides[6]['title']='Region S: a certified Split family'
slides[13].update(title='Q2: Can we choose correctly inside C?',blocks=[
F('Yes. In G choose Global; in S choose Split, before training.'),
E('x ∈ G  ⇒  H + WG < WS'),
E('x ∈ S  ⇒  H + WS < WG'),
F('In both regions, the output languages are equal on every word.'),
F('The guarantee is deterministic under the stated Wref algorithm and cost contract.'),
F('Outside C, no net winner is asserted by this theorem. UNKNOWN is allowed.')],notes='''سؤال دوم: حالا برای دادهٔ داخل مرز و افراز معلوم، آیا انتخاب درست را پیش از اجرا می‌دانیم؟ بله. در G مسیر Global را انتخاب می‌کنیم و در S مسیر Split را. در اولی، هویت اختلاف هزینه و شرط عضویت مستقیماً می‌گوید H به‌علاوهٔ Global از Split کمتر است. در دومی، اثبات کران‌ها برای n حداقل سه و حساب جداگانهٔ n یک و دو همین نامساوی را در جهت Split ثابت می‌کند. در هر دو ناحیه، برابری زبان خروجی روی تمام رشته‌ها نیز اثبات شده است. بنابراین این انتخاب احتمالی یا مبتنی بر حدس نیست؛ نتیجهٔ منطقی فرض‌های دقیق قضیه است. دو پاسخ ارائه روشن‌اند: مرز قابل بررسی داریم؛ و داخل آن مرز، انتخاب پیش از یادگیری با تضمین هزینه و برابری خروجی داریم. خارج از مرز، گواهی عمومی هزینه ممکن است موجود باشد ولی تضمین این دو ناحیه را تعمیم نمی‌دهیم. تضمین ما به الگوریتم و شمارش رویداد تعریف‌شده مربوط است؛ زمان واقعی و بازیابی هدف از آن نتیجه نمی‌شود.''',proof='Section 10, Two-region theorem; Sections 4–9')
slides[18]['notes']+=' برای تبدیل شرط به ویژگی مستقیم داده، اختلاف منهای H برابر است با k منهای یک ضربدر تعداد مثبت‌ها، به‌اضافهٔ دو k منهای یک ضربدر تعداد منفی‌ها، به‌اضافهٔ دو k منهای چهار، منهای اندازهٔ الفبا. حجم حروف دقیقاً حذف می‌شود. مثبت بودن این عبارت لازم و کافی برای سود خالص همین شاخه است؛ صفر یعنی تساوی پس از هزینهٔ انتخاب، و منفی یعنی انتخاب‌گر مزیت مسیر را جبران کرده است.'
slides[18]['blocks']=[
F('Active projection is identity. Here p,z count positive/negative words and M,M⁻ count their symbols.'),
F('Inactive factors have Pᵢ={ε}, no assigned negatives, and cost 4. The active run equals Global.'),
E('Π=M+M⁻+k(p+2z),     WS−WG=Π+4(k−1)'),
E('H=|Σ|+2k+p+z+M+M⁻'),
E('WS−WG−H=(k−1)p+(2k−1)z+2k−4−|Σ|'),
F('Global has no outside label. Inactive ε factors impose exactly the same restriction.')]
slides[11]['seconds']=75
slides[12]['seconds']=75
slides[13]['seconds']=90
slides[27]['blocks'][4]=F('Second audit: 2,216 further cases and 13,650 independent candidate checks. Proofs remain essential.')
slides[27]['notes']+=' در دور دوم، ۲۲۱۶ مورد دیگر با ۱۳۶۵۰ بررسی مستقل نامزد کنترل شد: بلوک فعال چندحرفی، الفبای استفاده‌نشده با اندازه‌های مختلف، همهٔ ترتیب‌های بلوک‌ها، تغییر نام حروف و مرز سخت نامساوی. ۱۴۶ مورد نیز دقیقاً روی تساوی سود خالص قرار گرفتند و به‌درستی گواهی خالص نگرفتند. رابط ارائه فقط دو خانوادهٔ واقعاً اثبات‌شده در این ارائه را وارد وضعیت خالص می‌کند.'
assert len(slides)==28 and sum(s['seconds'] for s in slides)==1080
(root/'slides.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf8')
timing=[{'slide':i+1,'title':s['title'],'seconds':s['seconds'],'persian_words':len(s['notes'].split())} for i,s in enumerate(slides)]
(out/'talk_timing.json').write_text(json.dumps({'main_seconds':1080,'main_minutes':18,'main_words':sum(t['persian_words'] for t in timing[:14]),'slides':timing},ensure_ascii=False,indent=2),encoding='utf8')
text='# متن ارائه انتخاب مسیر یادگیری\n\n۱۴ اسلاید اول مسیر اصلی ۱۸ دقیقه‌ای هستند. اسلایدهای ۱۵ تا ۲۸ پیوست پاسخ به پرسش‌ها و اثبات‌های تفصیلی‌اند و در زمان اصلی محاسبه نشده‌اند. زمان‌ها پیشنهادی‌اند؛ خواندن واقعی باید تمرین شود.\n\n'
elapsed=0
for i,s in enumerate(slides,1):
    if i<=14:
        end=elapsed+s['seconds'];label=f'{elapsed//60:02}:{elapsed%60:02} تا {end//60:02}:{end%60:02}';elapsed=end
    else:label='پیوست خارج از زمان اصلی'
    text+=f"## اسلاید {i} — {s['title']}\n\nزمان: {label}\n\n{s['notes']}\n\nارجاع اثبات: {s['proof']}\n\n"
(out/'Speaker_Notes_FA.md').write_text(text,encoding='utf8')
print('28 slides; main minutes=18; main Persian words=',sum(t['persian_words'] for t in timing[:14]))
