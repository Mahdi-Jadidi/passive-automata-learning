# متن همراه ارائه

زمان پیشنهادی بخش اصلی:۲۰دقیقه. اسلایدهای۱۷تا۱۹ پشتیبان‌اند.

## 1. افراز الفبا از تریس‌های درهم‌تنیده

این ارائه برای حدود ۲۰ دقیقه تنظیم شده است؛ اسلایدهای ۱ تا ۱۶ بخش اصلی و سه اسلاید آخر پشتیبان پرسش‌ها هستند. انگیزهٔ اولیه، جداکردن رفتار مؤلفه‌ها پیش از یادگیری اتوماتای محلی بود. امروز فقط بخش افراز الفبا، شرایط قطعیت و ارزیابی حل‌گر دقیق را گزارش می‌کنیم. اثر انتهابه‌انتهای این مرحله بر RPNI هنوز آزمایش نشده است. می‌خواهم در طول ارائه روشن بماند چه چیزی قضیه است، چه چیزی نتیجهٔ آزمایش است و چه چیزی هنوز سؤال پژوهشی است. تصویر جلد مفهومی و تولیدشده با هوش مصنوعی است؛ داده یا تصویر سامانهٔ واقعی نیست.



## 2. مسئله و دستاورد فعلی

مسئلهٔ فعلی این است که آیا نمونه‌های مثبت و منفی، تحت فرض‌های صریح، فقط یک افراز از نمادها باقی می‌گذارند. انگیزه، جلوگیری از آمیختن رفتار مؤلفه‌ها پیش از یادگیری محلی است؛ اما کاهش هزینه یا فضای حالت RPNI در این بسته نتیجهٔ تجربی نیست. آنچه اکنون قابل دفاع است، صورت‌بندی سازگاری، معیار لازم و کافیِ وجود عوامل منظم، گواه‌های بررسی‌پذیر، حل‌گر دقیق و دو بهینه‌سازی همراه ممیزی است. این فهرست، ادعای تقدم علمی نیست؛ تازگی نسبت به تمام ادبیات هنوز بررسی و احراز نشده است.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md

## 3. مدل و فرض‌های پژوهش

الفبای اعلام‌شده معلوم است و هر نماد دقیقاً یک مالک دارد؛ نمادهای مشاهده‌نشده هم باید در افراز قرار بگیرند. مالکیت نمادها مجهول است و عوامل، زبان‌های منظم مستقل و بدون کران حالت دارند. پذیرش کل یعنی تصویر کلمه روی همهٔ بلوک‌ها پذیرفته شود. این مدل با برچسب موفقیت آخرین رویداد یکسان نیست. مثبت و منفی برچسب کل کلمه‌اند؛ نبودن یک تریس در لاگ، آن را منفی نمی‌کند. اگر K را وارد کنیم، تعداد دقیق و مورد اعتمادِ بیرونی است؛ صحت آن از همین دادهٔ متناهی اثبات نمی‌شود.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md
منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md

## 4. تصویر تریس روی یک بلوک

تصویر روی بلوک B یعنی تمام نمادهای خارج B را حذف کنیم و ترتیب بقیه را نگه داریم. در مثال اسلاید، بلوک ab تفاوت ترتیب مثبت و منفی را نگه می‌دارد، ولی بلوک ac ممکن است همان تصویر را در هر دو ببیند. بنابراین از شباهت کلی رشته‌ها یا تعداد تکرار نمادها به‌تنهایی تصمیم نمی‌گیریم. باید بلوک‌هایی پیدا کنیم که همهٔ برچسب‌ها را هم‌زمان توضیح بدهند. تصویرگیری، ابزار اتصال مشاهدهٔ سراسری به رفتار فرضیِ محلی است و تعریف آن در قضیه و پیاده‌سازی دقیقاً یکسان باقی می‌ماند.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/docs/ALGORITHM_TUTORIAL_FA.md

## 5. شرط لازم و کافیِ سازگاری

برای هر بلوک B، مجموعهٔ H(B) را از تصاویر تمام مثبت‌ها می‌سازیم. ضرورت قضیه روشن است: عامل سازگار باید همهٔ این تصاویر را بپذیرد؛ پس هر منفی باید روی دست‌کم یک بلوک تصویری بیرون این مجموعه داشته باشد. برای کفایت، خود H(B) را زبان عامل قرار می‌دهیم؛ متناهی و در نتیجه منظم است. این فقط شاهد وجود است و زبان واقعی عامل را بازیابی نمی‌کند. ترتیب کمیت‌گذارها مهم است: برای هر منفی، یک بلوک باید آن را از تمام مثبت‌ها جدا کند. با کران حالت، این اثبات کفایت به‌تنهایی کافی نخواهد بود.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md

## 6. مثالِ افراز یکتا با تعداد معلوم

در این مثال تنها مثبت abcd است. منفی bacd با تعویض مجاور a و b به دست آمده است. اگر این دو نماد مالکان متفاوت داشته باشند، تصویر هر بلوک در مثبت و منفی یکسان می‌ماند؛ پس هیچ عامل مثبت‌پذیر نمی‌تواند منفی را رد کند. بنابراین a و b هم‌مالک‌اند. منفی abdc همین استدلال را برای c و d می‌دهد. با K برابر ۲، فقط ab|cd باقی می‌ماند و خودش نیز سازگار است. بدون K، تک‌بلوک abcd هم سازگار است؛ در این مثال، یکتایی به اطلاع معتبرِ تعداد وابسته است.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md

## 7. پیش‌آزمونِ گواه‌دار پیش از جست‌وجوی کامل

گراف تعویض، فقط رابطه‌های هم‌مالکیتِ لازم را ثبت می‌کند. مؤلفه‌های همبند آن اتم هستند و هیچ جواب سازگاری نمی‌تواند یک اتم را بشکند. اگر r کمتر از K باشد، جواب نداریم. اگر r برابر K باشد، فقط یک نامزد داریم؛ باید سازگاری همان نامزد را نیز بررسی کنیم. اگر افراز اتم‌ها سازگار باشد، تمام ادغام‌های آن سازگارند؛ برای ۱<K<r تعداد آن‌ها S(r,K) است و ابهام داریم. اگر اتم‌ها ناسازگار باشند و K<r، این پیش‌آزمون تصمیم نمی‌گیرد و جست‌وجوی دقیق لازم است. K برابر ۱ مستقیماً بررسی می‌شود.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md

## 8. یکتا، مبهم و ناتمام معنای متفاوت دارند

این وضعیت‌ها را باید جدا نگه داریم. یکتایی به گواه ساختاری یا پایان جست‌وجوی دقیق نیاز دارد؛ یافتن یک جواب کافی نیست. دو افراز متفاوت با شاهد سازگاری، ابهام را ثابت می‌کنند. ناسازگاری یعنی با اثبات کامل، هیچ جوابی باقی نمانده باشد. پایان مهلت فقط unresolved است و دربارهٔ کافی‌بودن اطلاعات نتیجه نمی‌دهد. بدون K، هر دادهٔ متناهی با P∩N تهی، توضیح تک‌بلوکی با زبان P دارد. پس اگر توضیح چندبلوکی هم باشد، ابهام داریم؛ البته بدون K ممکن است فقط همان تک‌بلوک باقی بماند.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md
منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md

## 9. الگوریتم دقیقِ فعلی

ابتدا ساختار ورودی، نمادها، شمارش‌ها و تناقض برچسب‌ها بررسی می‌شود. اگر هر منفی روی یک نماد شمارشی داشته باشد که در هیچ مثبت دیده نشده، همهٔ افرازها سازگارند و میان‌بُر دقیق داریم. سپس گراف تعویض و اتم‌ها ساخته می‌شوند. برای هر بلوک، ماسک منفی‌های قابل رد محاسبه می‌شود. در صورت بی‌نتیجه‌بودن گواه، DFS ادغام‌های اتم‌ها را بدون تکرار نام بلوک‌ها می‌پیماید؛ تعداد بلوک‌ها هرس ایمن می‌دهد. حافظهٔ نهان ماسک‌ها سقف ۴۰۹۶ دارد. با دو شاهد توقف می‌کنیم؛ این نسخه همهٔ جواب‌ها را فهرست نمی‌کند. پایان بودجه، خروجی ناتمام می‌دهد.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/implementation/candidate_c2_v1/gate_v1.py

## 10. دو بهینه‌سازی با حفظ جواب دقیق

C1 از شمارش‌های مرحلهٔ اعتبارسنجی، امضای دقیق طول و شمارش مرتب نمادها را نگه می‌دارد. تعویض مجاور این امضا را تغییر نمی‌دهد، پس جفت‌های با امضای متفاوت نمی‌توانند یال معتبر بسازند. آزمون دقیق روی جفت‌های باقی‌مانده اجرا می‌شود و کل داده در قیود باقی می‌ماند. C2 پس از اعتبارسنجی کامل، نمادهای خارج بلوک را با str.translate در قطعات ۱۶۳۸۴ کدپوینتی حذف می‌کند. اتصال قطعات به همان ترتیب، دقیقاً تصویر است. برخورد هش معیار صحت نیست و برابری دقیق بررسی می‌شود. این تغییرها هزینهٔ اجرا را کم می‌کنند؛ بدترین حالت ترکیبی جست‌وجو باقی است.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/theory/SOURCE_REVIEW_C1_V1.md
منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/theory/SOURCE_REVIEW_C2_V1.md

## 11. مجموعهٔ ارزیابی و شیوهٔ تولید

چهار ورودی و شش حالت زمان‌گیری از پیش ثابت بودند. دادهٔ پایهٔ A، B و C به‌ترتیب ۵۱۲، ۱۲۸ و ۱۶ کلمه در هر برچسب دارد؛ سپس یک مثبت و K منفیِ شاهد افزوده شده است. مولدها چرخهٔ کامل a، جایگشت تصادفیِ ناجابجاپذیر b و فقط حالت صفرِ پذیرنده دارند. چرخه، دسترس‌پذیری و تمایز حالت‌ها را تضمین می‌کند؛ همهٔ حالت‌ها در دادهٔ پایه بازدید شده‌اند. تولید شامل ادامهٔ ترمیمی و لنگرهای عمدی است، نه نمونه‌گیری طبیعیِ بدون شرط. D عوامل متناهی با زبان {ε,a^128b^128}، تعداد ۲۵۸ حالت کمینه و گراف تعویض خالی دارد. اطلاعات پنهان مولد به حل‌گر داده نمی‌شود.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/audit/FIXTURE_AUDIT_V1.json
منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/audit/PROTOCOL_V1.md

## 12. کاهش زمان روی ورودی A

این نمودار فقط اجراهای کامل A را نشان می‌دهد؛ هر عدد میانهٔ سه فرایند تازه است و زمان خواندن، پیش‌پردازش، حل و خروجی را در بر می‌گیرد. با K برابر ۴، زمان پایه 6.4033247، زمان C1 برابر 5.6533418 و زمان C2 برابر 0.6578987 ثانیه است؛ نسبت پایه به C2 حدود 9.73299 می‌شود. بدون K، زمان‌ها به‌ترتیب 8.5326166، 7.107165 و 0.6479559 ثانیه‌اند و نسبت حدود 13.1685 است. پاسخ بدون K به‌درستی مبهم است. این اعداد را با پروفایل یا میانگین تمام ورودی‌ها یکی نمی‌گیریم.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md

## 13. تکمیل اجراهای بزرگ و بازیابی ۲۰ دستگاه

مهلت نرم ۲۰ و مهلت سخت ۲۵ ثانیه بود. در B با K برابر ۸، پایه و C1 در هر سه تکرار ناتمام ماندند؛ C2 هر سه بار یکتا شد و میانهٔ آن 3.1736438 ثانیه بود. در C بدون K نیز پایه و C1 ناتمام و C2 هر سه بار مبهم شد؛ میانهٔ C2 برابر 7.9419305 ثانیه بود. برای زمان‌های سانسورشده ضریب سرعت نمی‌سازیم. کنترل جداگانه و ازپیش‌ثبت‌شدهٔ C با K برابر ۲۰، در یک اجرا و 5.2844308 ثانیه یکتا شد؛ میانه یا جزئی از ۵۴ زمان‌گیری نیست. بیست مؤلفهٔ اجباری، K معتبر و بازپخش سازگاری گواه بودند.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md
منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/coordination/k20_functional_control_v1/result.json

## 14. صحت مستقل و نتیجهٔ منفیِ کارایی

برای هر یک از سه ارائه‌دهنده، ۱۷۱۰ حالت بررسی شد؛ در مجموع ۵۱۳۰ بررسی مستقل با صفر اختلاف. مرجع کامل برای نمونه‌های کوچک و بازپخش گواه برای اجراهای کامل استفاده شد. همچنین ۵۴ زمان‌گیری و ۶ اجرای حافظه داریم؛ این‌ها نرخ دقت روی دادهٔ واقعی نیستند. نتیجهٔ منفی را هم نگه داشتیم: در D با K برابر ۴، زمان کل از 0.8118161 به 0.9735871 ثانیه رسید، حدود ۱۹٫۹۳ درصد افزایش. زمان درون خط لوله از 0.247363 به 0.0695816 کاهش یافت؛ علت اختلاف بیرونی معلوم نیست. حافظهٔ tracemalloc از ۱٬۸۶۸٬۶۶۴ به ۱٬۹۶۷٬۹۲۳ بایت افزایش یافت؛ این RSS نیست. برای A نسبت حافظهٔ کامل نداریم، چون پایه و C1 ناتمام‌اند.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md
منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/audit/benchmark_runs/20261104T120316.506188Z/validation_report.json

## 15. مرتبهٔ زمانی و مرز مقیاس‌پذیری

T حجم کل رویدادها، m اندازهٔ الفبا، r تعداد اتم‌ها و Lmax طول بلندترین کلمه است. خواندن ورودی حداقل خطی در حجم آن است. در بدترین حالتِ امضاهای برابر، فیلتر شمارش هیچ جفتی را حذف نمی‌کند و اسکن تعویض تا O(P*N*Lmax) می‌رود. هر تصویرگیری همچنان خطی در حجم پردازش‌شده است. تعداد نامزدها بدون K برابر Bell(r) و در لایهٔ K برابر S(r,K) است؛ این شمار، کل هزینهٔ زمانی برنامه نیست. در A و B و C گواه کافی بود و DFS صفر گره داشت. پس این نمونه‌ها شاهد حل جست‌وجوی سخت نیستند؛ تعداد حالت مولد با سختی جست‌وجوی افراز یکی نیست.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md
منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/theory/EXACT_SCALING_PROPOSAL_v1.md

## 16. مسیر پژوهش برای تصمیم استاد

نتیجهٔ قابل ارائه، معیار سازگاری، گواه‌های مشروط به مدل، حل‌گر دقیق با وضعیت ناتمام صادقانه و بهینه‌سازی‌های ممیزی‌شده است. اصالت نسبت به تمام ادبیات هنوز احراز نشده است. تصمیم پژوهشیِ جلسه می‌تواند انتخاب تمرکز میان شناسایی‌پذیری، کاهش هزینهٔ جست‌وجو و کاربرد روی لاگ طبیعی باشد. هر آزمایش بعدی دربارهٔ RPNI باید خط پایهٔ همسان داشته باشد و اثر افراز را واقعاً اندازه بگیرد؛ شاهد طبیعی هم باید از لنگر عمدی جدا ثبت شود. مدل برچسب مقالهٔ LANCER با پذیرش AND فعلی یکسان نیست؛ آن خط مقاله فعلاً به درخواست کاربر متوقف است. این‌ها پیشنهاد ادامه‌اند، نه نتایج انجام‌شده.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md

## 17. پشتیبان: ترتیب کمیت‌گذارها

این اسلاید پشتیبان دام کمیت‌گذار است. در P={bacd,abdc} و N={abcd} با K برابر ۲، تعویض‌ها ab و cd را اجبار می‌کنند. اما تصویر منفی روی ab برابر تصویر مثبت abdc است؛ روی cd نیز برابر تصویر مثبت bacd است. پس هیچ بلوک، منفی را از تمام مثبت‌ها جدا نمی‌کند و تنها افراز مجاز ناسازگار است. برای هر مثبت جداگانه می‌توان تفاوتی یافت، اما این ترتیبِ نادرستِ کمیت‌گذارها معیار ما نیست.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md
منبع: results/2026-11-04/preflight_certificates_v19/theory/GRAPH_CERTIFICATE_LIMITS_v1.md

## 18. پشتیبان: تعداد نمونه تضمین یکتایی نیست

برای هر p و q مثبت، کلمات مثبت a^(2i)bcd و منفی a^(2j+1)bcd همهٔ نمادها را دارند. تعداد a در مثبت‌ها زوج و در منفی‌ها فرد است؛ بنابراین هر هفت افراز دوبلوکیِ abcd سازگار است. افزودن توان زوج مشترک، همهٔ کلمات را دلخواه بلند می‌کند. پس حداقل تعداد و طول، تضمین عمومی یکتایی نیست. مثال فشرده نیز با P={abcd} و منفی‌های bacd,abdc یکتاست؛ با منفی‌های bacd,badc سه جواب ab|cd، abc|d و abd|c دارد، با همان خلاصه‌های عددی.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md
منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/preflight_certificates_v19/theory/MATCHED_SUMMARY_COUNTEREXAMPLE_v1.md

## 19. منابع و جایگاه در پیشینه

چهار مرجع ثبت‌شده برای جایگاه بحث عبارت‌اند از Oncina و García، ۱۹۹۲، دربارهٔ RPNI؛ Gold، ۱۹۶۷، دربارهٔ شناسایی در حد؛ Angluin، ۱۹۸۷، دربارهٔ یادگیری با پرسش و مثال نقض؛ و Jecker، Mazzocchi و Wolf، ۲۰۲۱، دربارهٔ تجزیهٔ اتوماتای جایگشتی. مدل پرسش فعال یا تجزیهٔ یک DFA داده‌شده با مسئلهٔ فعلی یکسان نیست. این فهرست، مرور جامع نوآوری نیست. مسیر دقیق مشخصات و پیوندها audit/SOURCES_V1.json است؛ منابع پروژه نیز پشتوانهٔ اثبات و آزمایش‌اند، نه جایگزین مرور ادبیات.

منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/scaling_v20/RESEARCH_REPORT_FA.md
منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/results/2026-11-04/preflight_certificates_v19/theory/PREFLIGHT_PROOFS_FA_v1.md
منبع: https://github.com/Mahdi-Jadidi/passive-automata-learning/blob/main/docs/ALGORITHM_TUTORIAL_FA.md
منبع مشخصات چهار مرجع: results/2026-11-04/advisor_package_v21/audit/SOURCES_V1.json

José Oncina, Pedro García (1992). Inferring regular languages in polynomial update time. https://doi.org/10.1142/9789812797902_0004
Introduces the RPNI passive state-merging context for inferring a DFA consistent with positive and negative examples; this project instead reasons over ownership partitions and does not learn component DFAs.

E. Mark Gold (1967). Language identification in the limit. https://www.sciencedirect.com/science/article/pii/S0019995867911655
Foundational identification-in-the-limit results distinguish positive-only text from labeled informants and motivate why finite observations require explicit assumptions and coverage conditions; it is not a direct theorem about this partition solver.

Dana Angluin (1987). Learning Regular Sets from Queries and Counterexamples. https://homepages.math.uic.edu/~lreyzin/papers/angluin87.pdf
Defines the active teacher/query setting for regular-language learning, useful as a contrast with the static labeled sample here; the paper's oracle access is not assumed by this project.

Ismaël Jecker, Nicolas Mazzocchi, Petra Wolf (2021). Decomposing Permutation Automata. https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CONCUR.2021.18
Studies decomposition of a given DFA language into intersections of smaller DFA languages, a neighboring compositionality problem; its input, decomposition target, and hypotheses differ from inferring a disjoint alphabet partition from positive/negative words.