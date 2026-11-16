# تعیین دقیق alphabet partition از traceهای positive و negative با تعداد نامعلوم componentها

## چکیده

یک مسئلهٔ دقیق partitioning بر پایهٔ finite sample را برای regular factorهای مستقل و مجزا، تحت پذیرش conjunctive برای full-word، بررسی می‌کنیم. ورودی شامل یک alphabet متناهی و مرتب است که صریحاً اعلام شده، به‌همراه فهرست‌های متناهی traceهای positive و negative؛ نه تعداد componentها و نه state bound داده می‌شود. یک partition زمانی compatible است که بتوان روی هر block یک regular language داشت که همهٔ positive projectionها را بپذیرد و conjunction آن‌ها همهٔ negativeها را رد کند. یک projection criterion دقیق را اثبات می‌کنیم، factor witnessهای متناهی ارائه می‌دهیم و با enumeration کانونی restricted-growth stringها، همهٔ compatible partitionها را می‌شماریم، بیشترین تعداد ممکن blockها را می‌یابیم، تعداد حالت‌های برابر در این بیشینه را می‌شماریم و witnessهای مرتب و بازتولیدپذیر برمی‌گردانیم. completeness، invariantهای انتخاب و termination متناهی الگوریتم baseline را با فرض منابع کافی، از جمله برای empty alphabet، اثبات می‌کنیم. دو extension اختیاری که جداگانه مشخص شده‌اند، از full-family certificate در صورت singleton-compatible بودن و از block-rejection cache محدود به هر فراخوانی استفاده می‌کنند. هیچ‌کدام قرارداد نتیجهٔ کامل را تغییر نمی‌دهد یا تضمین polynomial عمومی فراهم نمی‌کند. auditهای مستقل متناهی و timingهای محدود همراه با دامنهٔ اعتبارشان گزارش می‌شوند؛ این‌ها correctness را برای همهٔ ورودی‌ها اثبات نمی‌کنند و یک سامانهٔ فیزیکی مولد را شناسایی نمی‌کنند. این کار هیچ ادعایی دربارهٔ novelty یا پذیرش انتشار ندارد.

## 1. مقدمه و دستاوردها

یک trace ممکن است شامل eventهای متعلق به چند subsystem ناشناخته باشد. می‌پرسیم کدام partitionهای alphabet اعلام‌شدهٔ آن با observationهای متناهی و بدون نویزِ membership سازگار می‌مانند، وقتی پذیرش به این معناست که هر factor مستقل، projection خودش را بپذیرد. چون تعداد componentها، K، داده نشده است، باید compatible partitionهای دارای همهٔ تعدادهای ممکن block بررسی شوند. بیشترین تعداد compatible blockها را به‌عنوان یک objective بازتولیدپذیر مبتنی بر sample انتخاب می‌کنیم. این قرارداد شاهدی نیست که تعداد یا blockهای حاصل همان موارد فیزیکی باشند.

روش baseline ابتدا وجود language را به یک آزمون متناهی projection تقلیل می‌دهد و سپس هر partition از alphabet را به ترتیب canonical، enumerate می‌کند. خروجی آن تعداد کل compatible partitionها را از تعداد مواردی که به بیشینه می‌رسند متمایز می‌کند و certificateهای متناهی regular-factor ارائه می‌دهد. برای criterion، enumeration، loop invariantها، witnessها، completeness و termination اثبات‌های صریح می‌آوریم. دو optimization اختیاری با حفظ قرارداد کامل، مستقل از هم تحلیل می‌شوند. در پایان، به‌جای فرض کردن کارایی عملی بر اساس یک اثبات، محدودیت‌های identifiability، آزمون‌های موجود correctness و timing اندازه‌گیری‌شده را توصیف می‌کنیم.

نتایج برای مدل بیان‌شدهٔ Boolean، full-word، مستقل، با factorهای مجزا و AND معتبرند. این نتایج به‌طور خودکار به labelهای نویزی، سیستم‌های prefix-closed، process logهای دلخواه، factorهای bounded-state، observationهای جزئی، streamهای نامتناهی یا factorهای coupled تعمیم نمی‌یابند. هیچ تضمینی دربارهٔ membershipِ wordهای مشاهده‌نشده داده نمی‌شود. تکمیل ریاضی به منابع کافی نیاز دارد؛ یک deadline متناهی از آن نتیجه نمی‌شود.

## 2. ورودی، semantics و objective

فرض کنید alphabet یک دنبالهٔ متناهی مرتب از شناسه‌های اتمی متمایز باشد: `Σ=(a₁,…,aₘ)`. ترتیب ورودی آن، و نه مرتب‌سازی متن شناسه‌ها، ترتیب canonical را تعیین می‌کند. یک word مانند w دنباله‌ای متناهی روی Σ است؛ ε دنبالهٔ تهی است. P و N مجموعه‌های متناهی حاصل از فهرست‌های positive و negative، با deduplication همراه با حفظ نخستین occurrence، هستند. برای `B⊆Σ`، projectionِ `π_B(w)` هر event بیرون از B را حذف می‌کند و ترتیب و تکرار eventهای داخل B را حفظ می‌کند. برای `B⊆D`، projectionهای متوالی رابطهٔ `π_B(π_D(w))=π_B(w)` را دارند.

یک partition مانند Π مجموعه‌ای از blockهای ناتهیِ دو‌به‌دو disjoint است که اجتماعشان Σ باشد. روی `Σ=∅`، تنها partition برابر ∅ است. برای هر `B∈Π`، فرض کنید `F_B⊆B*` یک regular factor language باشد. global language القاشده عبارت است از

    L(Π,(F_B)) = {w∈Σ* : ∀B∈Π, π_B(w)∈F_B}.                         (1)

empty conjunction درست است؛ بنابراین برای `Σ=∅`، language آن `{ε}` است. یک partition، sample-compatible است اگر چنین regular factorهایی با `P⊆L` و `N∩L=∅` وجود داشته باشند. خانوادهٔ متناهی compatible partitionها را با `𝒱(P,N)` نشان می‌دهیم. اگر ناتهی باشد، تعریف می‌کنیم

    C=|𝒱(P,N)|,   k*=max{ |Π| : Π∈𝒱(P,N) },
    O=|{Π∈𝒱(P,N) : |Π|=k*}|.                                           (2)

recommendation، نخستین maximum-block partition از نظر lexicographic در encoding کانونیِ تعریف‌شده در ادامه است. C همهٔ compatible partitionها را می‌شمارد و O تعداد optimal partitionها را؛ هیچ‌کدام تعداد automata یا probabilityها را نمی‌شمارد. وقتی 𝒱 تهی باشد، `C=O=0` و `k*` و recommendation تعریف‌نشده‌اند.

ورودی مشخص، یک record با دقیقاً کلیدهای `alphabet`، `positive` و `negative` است. alphabet یک array از string IDهای ناتهی و دو‌به‌دو متمایز است؛ هر word یک array از IDهای کامل alphabet است. بنابراین `[]` همان ε است و `["ab","c"]` و `["a","bc"]`، token sequenceهای متمایزند. stringها می‌توانند Unicode، نشانه‌گذاری یا فاصله داشته باشند. برابری دقیق است: هیچ splitting، case-folding یا Unicode normalization انجام نمی‌شود. wordهای تکراری درون هر label جداگانه حذف می‌شوند و نخستین occurrence حفظ می‌شود. کلیدهای مفقود یا اضافی، typeهای نادرست، alphabet IDهای تهی یا تکراری و word IDهای ناشناخته، malformed هستند. در مقابل، wordی که هم در P و هم در N نرمال‌شده باشد، تناقضی با encoding معتبر است.

**Lemma 1 دربارهٔ normalization و تناقض.** deduplication درون هر label خانوادهٔ compatible را تغییر نمی‌دهد؛ اگر `P∩N` ناتهی باشد، هیچ compatible partitionی وجود ندارد.

*اثبات.* compatibility بر membership در هر مجموعهٔ label کمیت‌گذاری می‌کند؛ پس تکرار یک word الزام تازه‌ای نمی‌افزاید. اگر w در هر دو مجموعه باشد، هر language القاشده باید هم‌زمان w را در خود داشته باشد و از خود حذف کند. ∎

## 3. projection criterion و regular certificateها

برای هر block مانند B تعریف می‌کنیم

    H_B={π_B(p):p∈P},     R(B)={n∈N: π_B(n)∉H_B}.                      (3)

`H_B` متناهی است و ممکن است تهی باشد. این یک regular language روی B است: یک deterministic trie بسازید که stateهای آن prefixهای wordهای `H_B`، شامل empty prefix، به‌همراه یک rejecting sink باشند. از هر prefix، اگر prefix بسط‌یافته در trie وجود داشت، labeled edge را دنبال کنید و در غیر این صورت وارد sink شوید؛ همهٔ transitionهای sink در همان‌جا می‌مانند. دقیقاً prefixهایی را accepting علامت بزنید که خود wordهایی در `H_B` هستند. بنابراین ε دقیقاً وقتی پذیرفته می‌شود که root علامت خورده باشد. اگر `H_B` تهی باشد، یک rejecting state با self-loopها کافی است.

**Theorem 1 دربارهٔ compatibility criterion دقیق.** یک partition مانند Π، compatible است اگر و تنها اگر

    ∀n∈N  ∃B∈Π  ∀p∈P: π_B(n)≠π_B(p),
    equivalently  ⋃_{B∈Π} R(B)=N.                                       (4)

*اثبات.* فرض کنید compatible factorهای `F_B` وجود دارند. هر positive مانند p به‌وسیلهٔ conjunction پذیرفته می‌شود؛ در نتیجه برای هر B داریم `π_B(p)∈F_B` و `H_B⊆F_B`. هر negative مانند n به‌وسیلهٔ conjunction رد می‌شود؛ پس دست‌کم یک B، `π_B(n)` را رد می‌کند و در نتیجه این projection نمی‌تواند با هیچ عضو `H_B` برابر باشد. این رابطهٔ (4) را ثابت می‌کند. برعکس، برای هر B بگیرید `F_B=H_B`. languageِ `H_B` متناهی و بنابراین regular است، از جمله وقتی `H_B=∅`. هر positive توسط هر factor پذیرفته می‌شود. طبق (4)، هر negative یک block دارد که projection آن در language نیست و به‌وسیلهٔ conjunction رد می‌شود. برای `Π=∅`، رابطهٔ (4) دقیقاً وقتی درست است که `N=∅`؛ این با قرارداد empty-conjunction مطابقت دارد. ∎

quantifierهای (4) را نمی‌توان جابه‌جا کرد. برای `Σ={a,b}`، `P={a,b}` و `N={ab}`، negativeِ ab با هر positive روی یک singleton تفاوت دارد، اما روی `{a}` با positiveِ a و روی `{b}` با positiveِ b مطابق است. بنابراین `{a}|{b}`، incompatible است، هرچند `∀p∈P ∃B π_B(ab)≠π_B(p)`. one-block partition، compatible است.

**Lemma 2 دربارهٔ certificate.** برای partitionی که (4) را برآورده کند، block languageهای `H_B` و، برای هر `n∈N`، یک block مانند B با `π_B(n)∉H_B`، یک certificate متناهی با قابلیت replay مستقل تشکیل می‌دهند.

*اثبات.* languageهای نشان‌داده‌شده regular هستند و بنا به ساخت، هر positive projection را می‌پذیرند. block ذخیره‌شده، negative projection متناظر را کنار می‌گذارد؛ بنابراین global conjunction آن negative را رد می‌کند. خود partition را نیز می‌توان از نظر blockهای disjoint و ناتهی که Σ را می‌پوشانند بررسی کرد. ∎

witness record مشخص دارای `rgs`، `blocks`، `factors` و `negative_rejected_by` است. blockها بر اساس canonical label مرتب می‌شوند؛ `factors[i]`، arrayهای یکتای projected positive word را با ترتیب نخستین occurrence برای `blocks[i]` فهرست می‌کند. برای هر normalized negative به ترتیب نخستین occurrence، `negative_rejected_by[j]`، zero-based indexِ نخستین rejecting block در ترتیب labelها را ذخیره می‌کند. raw wordهای تکراری تحت پوشش همان normalized entry قرار می‌گیرند. در نبود negative، فهرست تهی است؛ برای یک compatible empty partition، هر چهار array تهی‌اند. این factorها consistency را نشان می‌دهند، نه reconstructionِ machineهای اصلیِ ناشناخته را.

## 4. enumeration کانونی partitionها

برای `m>0`، یک restricted-growth string یا RGS، tupleای به‌صورت `s=(s₁,…,sₘ)` است که

    s₁=0,   0≤sᵢ≤1+max{s₁,…,sᵢ₋₁}   for 2≤i≤m.                       (5)

برای `m=0` تنها RGS، empty tuple است. به هر block یک partition، بر اساس ترتیبی که یکی از symbolهای آن برای نخستین‌بار در alphabet اعلام‌شده ظاهر می‌شود، label بدهید. برعکس، preimage هر label استفاده‌شده در یک RGS یک block است.

**Lemma 3 دربارهٔ bijection.** first-appearance labeling، partitionهای Σ را به‌صورت bijective به RGSهای طول m نگاشت می‌کند؛ از جمله unique empty partition و empty RGS برای `m=0`.

*اثبات.* block مربوط به نخستین symbol، label صفر می‌گیرد. هرگاه یک block جدید نخستین‌بار ظاهر شود، label آن دقیقاً یک واحد بیشتر از بیشینهٔ قبلی است؛ بنابراین tuple حاصل (5) را برآورده می‌کند. برعکس، (5) الزام می‌کند که labelهای استفاده‌شده از صفر و پیاپی باشند؛ هر label یک preimage ناتهی دارد، preimageها disjoint هستند و در مجموع همهٔ positionهای alphabet را می‌پوشانند. first-appearance labelingِ این preimageها همان RGS اصلی را برمی‌گرداند. حالت تهی بدیهی است. ∎

**Lemma 4 دربارهٔ تولید کامل lexicographic.** خطوط 1 تا 7 از Algorithm 1 هر RGS را دقیقاً یک‌بار به ترتیب lexicographic تولید می‌کنند.

*اثبات.* برای `m=0`، خط 2 دقیقاً empty string را yield می‌کند. برای `m>0`، خط 3 از تنها first label مجاز استفاده می‌کند. در هر prefix با بیشینهٔ فعلی q، خطوط 6 تا 7 دقیقاً next labelهای `0,…,q+1` را به ترتیب افزایشی بازدید می‌کنند. استقرا روی طول باقی‌مانده نشان می‌دهد که هر continuation معتبر یک‌بار ظاهر می‌شود و همهٔ stringهای زیرِ یک next label کوچک‌تر، پیش از stringهای زیرِ next label بزرگ‌تر می‌آیند. بنابراین تولید، complete، unique و lexicographic است. ∎

## 5. Algorithm 1 و baseline دقیق exhaustive

pseudocode ریاضی زیر هر candidate را در برابر همهٔ positiveها و negativeهای نرمال‌شده بررسی می‌کند. countهای arbitrary-precision را نگه می‌دارد و از هر خانوادهٔ مشخص‌شده حداکثر دو witness حفظ می‌کند. نتیجه‌های `INCOMPATIBLE`، count صفر و فاقد recommendation هستند؛ invalid input، محاسبهٔ incomplete و replay failure، mathematical result field ندارند. قواعد external interruption در بخش 7 بیان شده‌اند.

{{PSEUDOCODE}}

در اینجا `witness`، فهرست‌های factor و rejection-index توصیف‌شده در بخش 3 را می‌سازد. پیاده‌سازی منبع، RGSهای انتخاب‌شده را حین loop ذخیره می‌کند و witnessها را پس از آن می‌سازد؛ هم‌ارزی آن‌ها در بخش 6 اثبات می‌شود. بررسی‌ها روی arrayهایی از IDهای کامل انجام می‌شوند، نه روی raw concatenationها.

**Lemma 5 دربارهٔ correctnessِ CHECK.** برای هر RGS تولیدشده، خطوط 8 تا 16 دقیقاً وقتی FAIL برمی‌گردانند که partition نمایش‌داده‌شده incompatible باشد؛ در غیر این صورت یک certificate معتبر با ترتیب canonical blockها و negativeها برمی‌گردانند.

*اثبات.* خطوط 9 تا 10، blockها و هر `H_B` را می‌سازند. برای هر normalized negative، خطوط 12 تا 14 یک block می‌خواهند که projection آن بیرون از کل `H_B` باشد. Theorem 1 می‌گوید دقیقاً همین شرط لازم و کافی است. اگر وجود داشته باشد، خط 13 نخستین مورد را انتخاب می‌کند و خط 15، index آن را ثبت می‌کند. خط 16، positive projectionها را به ترتیب نخستین occurrence می‌سازد و certificate توجیه‌شده با Lemma 2 را برمی‌گرداند. ∎

**Lemma 6 دربارهٔ prefix invariant.** پس از هر prefix از iteration روی RGSها، C تعداد compatible candidateهای دیده‌شده است و `all_witnesses` نخستین `min(2,C)` مورد آن‌ها را به ترتیب lexicographic در خود دارد. اگر `C>0`، best بیشترین block count آن‌هاست، O تعداد مواردی است که به best می‌رسند و `opt_witnesses` نخستین `min(2,O)` مورد از این candidateها را به ترتیب lexicographic در خود دارد.

*اثبات.* در ابتدا `C=O=0` است و فهرست‌ها تهی‌اند، پس invariant به‌صورت vacuous برقرار است. طبق Lemma 5، check ناموفق compatible نیست و خط 24، invariant را بدون تغییر باقی می‌گذارد. در غیر این صورت، RGS تازه بازدیدشده طبق Lemma 4، compatible و unique است؛ خطوط 25 تا 27 آن را می‌شمارند و فقط اگر کمتر از دو compatible witness قبلی وجود داشته باشد، آن را حفظ می‌کنند. اگر block count آن، k، از best بیشتر باشد، همهٔ optimal candidateهای قبلی برای این prefix دیگر optimal نیستند؛ خط 29 قرار می‌دهد `best=k` و `O=1` و witnessهای آن‌ها را با candidate فعلی جایگزین می‌کند. اگر `k=best`، خط 31 مقدار O را افزایش می‌دهد و خط 32 فقط وقتی کمتر از دو مورد وجود داشته باشد، آن را اضافه می‌کند. اگر `k<best`، نه optimum value و نه witnessهای آن تغییر می‌کنند. چون enumeration، lexicographic است، witnessهای حفظ‌شده همان دو مورد نخست‌اند. استقرا، invariant را ثابت می‌کند. ∎

**Theorem 2 دربارهٔ soundness، completeness و optimum.** با ورودی متناهی well-formed و منابع کافی، اگر enumeration کامل شود و witness replay موفق باشد، Algorithm 1 دقیقاً وقتی INCOMPATIBLE برمی‌گرداند که هیچ compatible partitionی وجود نداشته باشد. در غیر این صورت C، best، O، status، recommendation و هر دو witness list برابر کمیت‌های مشخص‌شده در (2) هستند و recommendation، نخستین مورد optimal از نظر lexicographic است.

*اثبات.* validation و normalization طبق Lemma 1 مجموعه‌های ورودی را حفظ می‌کنند؛ early return برای labelهای متناقض نیز طبق همان Lemma، sound است. در غیر این صورت Lemma 4 هر partition را یک‌بار بازدید می‌کند و Lemma 5 دقیقاً compatible partitionها را علامت می‌زند. بنابراین در پایان loop، prefix invariantِ Lemma 6 کل خانواده را توصیف می‌کند. اگر `C=0`، خط 33 به‌درستی incompatibility را اعلام می‌کند. اگر `C>0`، best و O معنای global لازم را دارند، `opt_witnesses[0]` نخستین optimal RGS است و هر دو فهرست دقیقاً نخستین `min(2,count)` candidateها را در خود دارند. Lemma 2، finite-factor witnessها را معتبر می‌کند. خطوط 34 تا 37 خروجی کامل مشخص‌شده را برمی‌گردانند. اگر replay شکست بخورد، به‌جای آن ERROR برگردانده می‌شود و فرض successful-replay در Theorem برقرار نیست. ∎

**Corollary 1 دربارهٔ status و tieها.** در خروجی feasible و کامل‌شده، UNIQUE_COMPATIBLE دقیقاً وقتی برقرار است که `C=1` و AMBIGUOUS دقیقاً وقتی که `C≥2`. مقدار `optimal_unique` به معنای `O=1` است و گزاره‌ای جداگانه است.

*اثبات.* statusها همهٔ حالت‌های ممکنِ اندازهٔ دقیق خانواده، C، را پوشش می‌دهند؛ optimal flag از maximum subset که جداگانه شمرده شده محاسبه می‌شود. برای مثال `Σ={a,b}`، `P={ε}` و `N={a}` را در نظر بگیرید: هر دو `{a,b}` و `{a}|{b}`، compatible هستند، در حالی که فقط دومی دو block دارد. بنابراین `C=2` و `O=1` و unique optimum مستلزم unique compatibility نیست. ∎

### وابستگی اثبات‌ها به خطوط

| خطوط | واقعیت موردنیاز |
|---|---|
| 1–7 | Lemmaهای 3 و 4 تولید unique، مرتب و completeِ RGS را، از جمله برای m=0، برقرار می‌کنند. |
| 8–16 | Theorem 1 و Lemma 5، projection checking دقیق و ساخت witness متناهی را برقرار می‌کنند. |
| 17–20 | Lemma 1 و whole-record validation، ساختار نامعتبر را از labelهای متناقض متمایز می‌کنند. |
| 21–27 | Lemma 6، all-compatible countها و دو witness نخست را برای prefix پردازش‌شده برقرار می‌کند. |
| 28–32 | Lemma 6، max reset، optimal tie count و optimal witnessهای lexicographic را اثبات می‌کند. |
| 33–37 | Theorem 2 و Corollary 1، statusهای کامل‌شده، خروجی دقیق و replay error handling را برقرار می‌کنند. |
| بیرون از loop | بخش 7 رفتار bounded-computation و uncatchable-termination را تعریف می‌کند؛ کار incomplete هیچ ادعای دقیقی ندارد. |

## 6. refinement به پیاده‌سازی frozen

recursive generator مفهومی است. کد منبع frozen در Python از یک iterative lexicographic successor استفاده می‌کند: با RGS تمام‌صفر آغاز کنید؛ راست‌ترین position را انتخاب کنید که label آن با رعایت prefix بدون تغییر بتواند افزایش یابد، آن را یک واحد افزایش دهید و suffix را صفر کنید. اگر هیچ positionی قابل افزایش نیست، توقف کنید.

**Lemma 7 دربارهٔ generator و witness refinement.** iterative source generator دقیقاً همان RGS sequence خطوط 1 تا 7 را yield می‌کند و deferred witness materialization روی ورودی normalized ثابت، همان witnessهای conceptual eager materialization را تولید می‌کند.

*اثبات.* هر string بزرگ‌تر از نظر lexicographic باید برای نخستین‌بار در positionی تفاوت کند که با حفظ prefix خود قابل افزایش باشد. انتخاب راست‌ترین چنین positionی باعث می‌شود prefix تغییریافته تا حد ممکن دیر، و بنابراین تا حد ممکن کوچک باشد؛ افزایش یک‌واحدی، minimal است و یک suffix تمام‌صفر، کمترین legal completion از نظر lexicographic است. بنابراین successor توصیف‌شده دقیقاً RGS معتبر بعدی است. اگر هیچ positionی نتواند افزایش یابد، RGS بزرگ‌تری وجود ندارد. هر دو generator با تمام‌صفر شروع می‌کنند و در نتیجه همان sequence را enumerate می‌کنند، از جمله empty string که جداگانه رسیدگی می‌شود. ساخت witness در RGS انتخاب‌شده و P,N نرمال‌شدهٔ ثابت، deterministic است. بنابراین چه در زمان انتخاب و چه پس از enumeration فراخوانی شود، همان factor listها و rejecting indexها را تولید می‌کند. ∎

internal verifier واقعی، block coverage، تطابق canonical RGS، برابری factorها به‌صورت set، پذیرش positiveها و رد شدن توسط هر block ارجاع‌شده را بررسی می‌کند. این verifier مستقلاً ترتیب serializationِ positive-projection یا این‌که block ارجاع‌شده نخستین rejecting block باشد را بررسی نمی‌کند. این ویژگی‌های ترتیب از source constructor نتیجه می‌شوند و جداگانه در independent audit بررسی شده‌اند. این تمایز بخشی از ادعای پیاده‌سازی است.

## 7. termination، complexity و error semantics

**Theorem 3 دربارهٔ termination متناهی رویهٔ ریاضی.** برای هر ورودی متناهی well-formed، الگوریتم با منابع نامحدود با یک نتیجهٔ دقیق یا نتیجهٔ incompatibility دارای توجیه ریاضی خاتمه می‌یابد.

*اثبات.* alphabet تعداد متناهی partition دارد؛ طبق Lemma 4، generator هر کدام را یک‌بار تولید می‌کند و پایان می‌یابد. هر projection، مقایسهٔ set، عمل validation، به‌روزرسانی count، ساخت certificate و replay، اشیای متناهی را مقایسه می‌کند و با منابع کافی خاتمه می‌یابد. contradiction check می‌تواند زودتر تمام شود. Theorem 2 نتیجهٔ کامل‌شده را می‌دهد. ∎

تعداد partitionها `Bell(m)` است و `Bell(0)=1` [1]. یک اجرای exhaustive baseline بدون تناقض، دقیقاً `Bell(m)` candidate را ارزیابی می‌کند. هر ارزیابی نسبت به اندازهٔ صریح ورودی، کار polynomial می‌برد؛ بنابراین یک bound محافظه‌کارانه برابر `Bell(m)` ضرب‌در یک polynomial factor است که representationِ identifierها و arbitrary-precision arithmetic را نیز شامل می‌شود. این تضمین polynomial-time برای m متغیر نیست. candidate witnessهای حفظ‌شده و iterative RGS state متناهی‌اند؛ دو exact count می‌توانند تا `Bell(m)` رشد کنند و به `O(log Bell(m))` بیت نیاز داشته باشند. یک ورودی متناهیِ به‌اندازهٔ کافی بزرگ ممکن است از زمان یا حافظهٔ موجود فراتر رود، هرچند فرایند ریاضی خاتمه می‌یابد.

whole-record validation پیش از هر نتیجه‌گیری ریاضی انجام می‌شود. `INVALID_INPUT` به معنای representation بدساخت یا IDهای نامعتبر است، نه دادهٔ متناقض. یک word معتبر که هم در P و هم در N باشد، `INCOMPATIBLE` است؛ اگر پس از تکمیل exhaustive هیچ compatible partitionی یافت نشود، همان status طبق Theorem 2 توجیه می‌شود. برای `m>0` و `P∩N=∅`، oneblock همواره compatible است، چون projection آن همان word اصلی است؛ برای `m=0`، compatibility دقیقاً وقتی برقرار است که `N=∅`، و در این صورت `C=O=1` و `best=0`. حالت‌های `P=∅`، `N=∅`، ε، declared symbolهای استفاده‌نشده، wordهای تکراری و traceهای دارای طول متناهی دلخواه، به هیچ data truncation ویژه‌ای نیاز ندارند.

implementation argument اختیاریِ `max_candidates` تعداد candidate inspectionها را محدود می‌کند، نه K یا model stateها را. با تمام شدن candidate budget، یک keyboard interruption گرفته‌شده یا memory exhaustion گرفته‌شده، پیاده‌سازی `INCOMPLETE` با mathematical fieldهای null برمی‌گرداند؛ هیچ partial count یا maximum تأیید نمی‌شود. اگر replay شکست بخورد، `ERROR` با mathematical fieldهای null برمی‌گرداند. فرایندی که hard-kill شده یا شکستی که حتی ساخت error را ناممکن کند، ممکن است هیچ پاسخی ندهد. به‌ویژه، محاسبهٔ غایب یا timed-out شاهدی برای incompatible بودن داده‌ها نیست.

## 8. exact optimization اختیاری A با full-family certificate

پس از validation و رسیدگی به تناقض، اگر candidate budget صریحی وجود ندارد، singleton partitionِ S را بررسی کنید. اگر compatible نیست، بدون نتیجه‌گیری به baseline برگردید. اگر compatible است، از یک full-family certificate استفاده کنید.

**Lemma 8 دربارهٔ coarsening monotonicity.** اگر `B⊆D` و `n∈R(B)`، آنگاه `n∈R(D)`. در نتیجه، هر coarseningِ یک compatible partition، compatible است.

*اثبات.* اگر برای positiveای مانند p داشته باشیم `π_D(n)=π_D(p)`، projection هر دو طرف روی B می‌دهد `π_B(n)=π_B(p)` که با `n∈R(B)` تناقض دارد. بنابراین `R(B)⊆R(D)`. هر block مانند B در یک compatible partition، در یک block مانند D از یک coarsening قرار دارد؛ rejecting block هر negative، در block دربرگیرندهٔ خود همچنان rejecting باقی می‌ماند. ∎

**Corollary 2 دربارهٔ پیامد oneblock.** برای alphabet ناتهی و P,N مجزا، oneblock، compatible است. اگر هر compatible partitionی بیش از یک block داشته باشد، `C≥2`. بنابراین UNIQUE_COMPATIBLE فقط می‌تواند برای oneblock partition برقرار باشد. عکس آن نمی‌گوید که یک unique optimum دارای unique compatibility است.

*اثبات.* full-alphabet projection، identity است؛ بنابراین oneblock factorِ P، positiveها را می‌پذیرد و negativeهای disjoint را کنار می‌گذارد. هر compatible multiblock partition از oneblock متمایز است؛ هر دو در C شمرده می‌شوند. اگر `C=1`، آن تنها partition همان oneblock است. مثال Corollary 1 یک unique two-block optimum و یک compatible oneblock partition متمایز دارد. ∎

**Theorem 4 دربارهٔ certificate، exact countها و witness order.** اگر S، compatible باشد، همهٔ partitionهای Σ، compatible هستند. تعداد کل آن‌ها `Bell(m)` است، maximum block count برابر m است و unique maximum همان S است. نخستین RGS آن‌ها از نظر lexicographic برابر `0^m` است؛ برای `m≥2`، دومین مورد `0^(m−1)1` است. برای `m=0` یا 1، partition دومی وجود ندارد.

*اثبات.* هر partition یک coarsening از S است؛ پس Lemma 8، compatibility همه را ثابت می‌کند. برای `m=0` این همان تنها empty partition است؛ شرط certificate آن به `N=∅` نیاز دارد. تعداد partitionها `Bell(m)` است. یک partition از m عنصر فقط وقتی می‌تواند m block ناتهی داشته باشد که هر block یک singleton باشد؛ بنابراین S، unique optimum است، از جمله برای `m=0`. RGS تمام‌صفر از نظر lexicographic نخستین است؛ میان همهٔ RGSهای معتبر دیگر، به‌تأخیر انداختن نخستین nonzero label تا آخرین position و استفاده از labelِ 1، مقدار `0^(m−1)1` را می‌دهد که اگر و تنها اگر `m≥2` وجود دارد. ∎

`Bell(m)` را به‌طور دقیق با `S(0,0)=1`، `S(i,k)=S(i−1,k−1)+kS(i−1,k)` و `Bell(m)=Σ_k S(m,k)` محاسبه کنید و S خارج از محدوده را صفر بگیرید [1,2]. recurrence بر اساس این‌که آخرین عنصر یک singleton تشکیل می‌دهد یا به یکی از k block موجود می‌پیوندد، partition می‌کند. این روش به `O(m²)` عمل arithmetic و `O(m)` مقدار arbitrary-precision ذخیره‌شده نیاز دارد؛ هزینهٔ این عمل‌ها و نمایش integerهای بزرگ ثابت نیست. یک pure Python result تضمین نمی‌کند که تبدیل جداگانهٔ JSON/decimal بتواند از integer-string limit تنظیم‌شدهٔ host فراتر رود. certificate، witnessها را با قواعد baseline می‌سازد و verify می‌کند؛ هرگز ادعا نمی‌کند که `Bell(m)` candidate evaluation انجام شده است. با هر `max_candidates` صریح، از جمله صفر، A کنار گذاشته می‌شود و مرزهای budgetِ baseline حفظ می‌شوند.

## 9. exact optimization اختیاری B با bounded block memo

برای هر normalized negative مانند `n_j` و block مانند B، Boolean vector entry را تعریف کنید

    V_B[j] = true  iff  π_B(n_j)∉H_B.                                   (6)

یک least-recently-used cache محدود به هر invocation، با حداکثر 256 block vector، از یک tuple از IDهای کامل با ترتیب اعلام‌شده به‌عنوان key استفاده می‌کند. هنگام miss، همهٔ entryها را از ورودی normalized ثابت محاسبه کنید؛ هنگام eviction فقط cached data را حذف کنید. یک candidate partition دقیقاً وقتی پذیرفته می‌شود که هر negative index در دست‌کم یکی از block vectorهای آن یک true entry داشته باشد.

**Theorem 5 دربارهٔ memo equivalence.** جایگزین کردن compatibility evaluationِ baseline با bounded memo test، خروجی کامل‌شده را حفظ می‌کند، شامل C، best، O، all-compatible status، canonical RGS و هر دو ordered witness family، برای همان ورودی و budget، مشروط به این‌که resource interruption رخ ندهد.

*اثبات.* برای P,N نرمال‌شدهٔ ثابت و B، رابطهٔ (6) دقیقاً membership در `R(B)` از (3) است و به blockهای دیگر یا enumeration history وابسته نیست. hit همان vector محاسبهٔ تازه را برمی‌گرداند؛ miss یا eviction همان vector را دوباره محاسبه می‌کند. بنابراین union coverageِ negative indexها با (4) هم‌ارز است، از جمله حالت vacuousِ `N=∅` و `Π=∅`. برای هر candidate در ترتیب RGS بدون تغییر، همان Boolean decision گرفته می‌شود؛ پس prefix induction در Lemma 6 مقادیر یکسان C، best، O و retained RGSها را می‌دهد. سپس deterministic witness constructor و verifier بدون تغییر، همان serialized witnessها را می‌دهند. budget checkها در همان candidate boundary انجام می‌شوند. ∎

یک budget صریح A را کنار می‌گذارد؛ B همچنان می‌تواند بدون تغییر inspected candidate prefix استفاده شود. A و B می‌توانند جداگانه یا با هم فعال شوند. cache، local به یک solve است و نمی‌تواند factهایی از sample قبلی وارد کند. سقف 256-entry آن، vectorهای حفظ‌شده را محدود می‌کند، نه تعداد input symbolها یا candidateها را؛ blockهای evictشده را می‌توان دوباره محاسبه کرد. یک full vector ممکن است نسبت به early-negative exit در baseline به کار بیشتری نیاز داشته باشد و هر دو optimization می‌توانند memory یا runtime overhead اضافه کنند. resource failureهای گرفته‌شده همچنان INCOMPLETE با mathematical fieldهای null هستند؛ پیاده‌سازی‌های متفاوت الزاماً در نقطهٔ فیزیکی یکسانی شکست نمی‌خورند.

## 10. identifiability و محدودیت‌ها

maximum یک recommendation دقیق تحت sample criterion است، نه certificateای برای decomposition فیزیکی اصلی. برای `Σ={a,b}`، هم یک universal factor منفردِ `Σ*` و هم دو singleton universal factorِ `a*` و `b*`، complete languageِ `Σ*` را تولید می‌کنند. partitionهای متفاوت آن‌ها حتی با همهٔ membership observationهای ممکن نیز indistinguishable هستند، مگر این‌که فرض‌های بیشتری یکی را کنار بگذارد. اگر یک actual generator متعلق به مدل مقرر باشد، با labelها مطابقت داشته باشد و دقیقاً یک partition، compatible باشد، آنگاه partition آن باید با همان یک partition برابر باشد؛ این نتیجهٔ مشروط، factor implementationها، نام deviceها یا labelها را تعیین نمی‌کند. طبق Corollary 1، `O=1` به‌تنهایی ضعیف‌تر از `C=1` است.

این روش فقط برای ورودی‌های متناهی با symbolهای مشخص و full-word Boolean labelها دقیق است. physical K را infer نمی‌کند، unobserved behavior را bound نمی‌کند، هر trace آینده را پیش‌بینی نمی‌کند یا تضمین نمی‌کند که هر اجرای interrupted بتواند تمام شود. بدون مدل‌سازی و اثبات‌های جداگانه، به noise، state-minimality، prefix closure، synchronization میان ownership blockهای هم‌پوشان یا real logهای دلخواه نمی‌پردازد. هیچ polynomial runtime برای optimization عمومیِ variable-alphabet ادعا نمی‌شود.

## 11. validation و رفتار اندازه‌گیری‌شده

C028 baseline با یک set-insertion partition oracle که مستقل نوشته شده و از RGS generator آن متمایز است، audit شد. audit پس از clarification، در 2,187 ternary labelingِ exhaustive از هفت word با طول حداکثر دو روی یک two-symbol alphabet، تعداد 60 seeded case با 3 تا 8 symbol، تعداد 19 edge record، تعداد 11 malformed-schema control و سه withheld-DFA sample control موفق بود. آزمون‌های metamorphic، witness replay و budget موفق بودند. یک control با 1,200 ID عمداً پس از یک candidate متوقف شد؛ این یک large-alphabet exhaustive solve کامل‌شده نبود. یک audit checker اولیه به‌اشتباه از raw duplicate-negative positionها به‌جای normalized indexها استفاده کرده بود. آن failure حفظ شد، serialization convention روشن شد و baseline بدون تغییر دوباره اجرا شد. این finite audit، شاهدی برای پیاده‌سازی است، نه اثباتی برای هر ورودی متناهی.

C030 candidate audit جداگانه است: هر یک از A-only، B-only و A+B روی 2,271 unlimited record با independent oracle، و برای هر variant روی هشت explicit-budget check و نه invalid-schema/budget check با baseline مطابق بود؛ این بررسی‌ها complete outputها را مقایسه و witnessها را replay کردند. یک nine-ID diagnostic، تعداد 366 مورد LRU eviction و 111 reinsertion بعدی مشاهده کرد. در یک early-failure diagnostic، baseline از 6 projection call و B از 10 مورد استفاده کرد و decision یکسان بود. نخستین C030 run در یک fixture assertion که فقط مربوط به harness بود شکست خورد؛ failure حفظ شد، یک diagnostic اصلاح‌شده مستقلاً بازبینی شد و candidate source بدون تغییر، rerun را گذراند. legacy audit JSON fieldِ `candidate_calls: 0` یک baseline-mode artifact است؛ counterهای per-variant مقایسه‌های واقعی candidate را ثبت می‌کنند.

پس از correctness، یک timing matrix هشت‌موردیِ baseline در برابر حالت combined، برای هر solver و input از سه fresh process با unlimited budget یکسان استفاده کرد: همهٔ 48 اجرا کامل شدند و full-output checkها را گذراندند. process startup نیز لحاظ شد. combined median در سه مورد از هشت مورد بیشتر و در پنج مورد کمتر بود؛ با فقط سه observation در هر cell و variability قابل‌توجه، این اندازه‌گیری‌ها یک speedup عمومی را اثبات نمی‌کنند یا اثر هر optimization را جدا نمی‌کنند. A-only و B-only جداگانه time نشدند و memory اندازه‌گیری نشد. C028 baseline بدون تغییر همچنان recommended default است؛ C030 variantها experimental هستند. raw timingها، failureها، exact inputها، commandها و hashها در Appendix A مشخص شده‌اند.

## 12. ارتباط با کارهای پیشین

projection obstruction ارتباط نزدیکی با کار Henry و همکاران دربارهٔ compositional automata-learning دارد: [3, §4.1, Proposition 5; §6.1, Corollary 12]، incompatibility را از طریق یک negative observation مشخص می‌کند که projectionهای آن روی همهٔ local alphabetها با positive observationها مطابق‌اند. آن کار دربارهٔ active learningِ labeled transition systemهاست و overlapping distributionها و synchronization را مجاز می‌داند؛ کل problem formulation آن با این passive disjoint-factor optimization یکسان نیست. برای criterion ادعای novelty نمی‌شود. lexicographic generationِ set partitionها در combinatorial literature تثبیت شده است [4] و Bell/Stirling counting استاندارد است [1,2]. Moerman [5]، active learningِ Moore machineها با decomposable outputها را بررسی می‌کند، نه objective کنونیِ sample-compatible alphabet partition. الگوریتم‌های exact-cover و counting مرتبط در settingهای گسترده‌تر وجود دارند [6]، اما به‌طور خودکار این exact family countها، دو labeled witness نخست و interruption semantics را فراهم نمی‌کنند. این مقایسهٔ محدود، یک novelty search جامع یا تضمین publication-acceptance نیست.

## 13. نتیجه‌گیری

compatibility criterion دقیق و exhaustive canonical enumeration، مسئلهٔ finite sample مشخص‌شده با K نامعلوم را، وقتی منابع اجازه دهند، حل می‌کنند. اثبات‌ها، exact countها، canonical optimum، witness order و finite regular realizationها را توجیه می‌کنند؛ certificate و memo اختیاری نیز تحت شرایط بیان‌شدهٔ خود همان قرارداد را حفظ می‌کنند. نه finite testing و نه optimizationِ sample objective، به‌طور عمومی physical ownership را بازیابی نمی‌کند. ادعاهای بیشتر به فرض‌های اضافی، literature review گسترده‌تر، experimental evidence مناسب و independent peer assessment نیاز دارند.

## Appendix A. بازتولیدپذیری و provenance

frozen baseline در `results/2026-11-11/exact_foundations_v28/implementation/reference.py` است، با SHA-256 برابر `5f60b27447b37ec07f1fd6bce75be6199b898573d4b32e90413e900e3a615a94`. specification کامل، proof، serialization amendmentها و pseudocode آن زیر `exact_foundations_v28/theory/` و در `PSEUDOCODE.md` قرار دارند. independent test evidence آن، `exact_foundations_v28/audit/AUDIT_REPORT_V2.md` و `AUDIT_MANIFEST_V2.json` است.

optional candidate در `results/2026-11-11/review_optimization_v30/optimization/candidate_v1.py` است، با SHA-256 برابر `7501901c6de5d7bb78ffc60f152b818733e3bd4460c9a655b8d783f384e8fc2b`. proposal proof، source verdict، final report و audit آن در `review_optimization_v30/optimization/`، `review/`، `REPORT_EN.md` و `audit/AUDIT_REPORT_V2.md` قرار دارند. frozen manifestِ v2 audit، commandها، executable versionها، corpus hashها، retained failure و همهٔ source hashها را ثبت می‌کند؛ `timing_results.json` هر raw timing و complete solver result را ثبت می‌کند. proof reviewerها، source reviewerها و auditor، AI agentهای هماهنگ‌شده بودند، نه human referee یا formal proof assistant. هیچ old source یا public entry point برای optimization تغییر نکرد.

## منابع

{{REFERENCES}}
