# فهرست قابل پیگیری ادعاها و آزمون‌ها

تمام ردیف‌ها مشروط به قرارداد برنامهٔ مرجع، افراز معلوم، دادهٔ معتبر و سیاست ثابت تخصیص منفی‌اند. N تعداد پیشوندهای مثبت با ریشه، E=N−1، A پشتیبان حروف مثبت، Π هزینهٔ آماده‌سازی و H هزینهٔ اجرای انتخاب‌گر است. نام قواعد، همان rule در خروجی static_selector.py است. برای NET باید هزینهٔ H همان شاخهٔ واقعی پرداخت شود.

| شناسه | دسته و آزمون تشخیص | نتیجه و آزمون هزینه | محل اثبات |
|---|---|---|---|
| C01 | هر منفی w باید حداقل یک i با π_i(w)∉π_i(S⁺) داشته باشد | نبود شاهد: تجزیهٔ AND سازگار ناممکن؛ برندهٔ هزینه نام‌گذاری نمی‌شود | [Original_Proofs_EN.md](research/Original_Proofs_EN.md) §2؛ اسلایدهای 3 و 16 |
| C02 | یک بلوک؛ one_block_identity | WS−WG=Π؛ Global گران‌تر نیست؛ NET اگر H<Π | [Previous_Proofs_EN.md](research/Previous_Proofs_EN.md) §3 |
| C03 | مثبت‌ها تهی یا فقط ε؛ root_only_positives | g=3+[ε∈S⁺]؛ WG=g، WS=g+Π+(k−1)g؛ علامت شکاف و H را بررسی کن | [Previous_Proofs_EN.md](research/Previous_Proofs_EN.md) §4 |
| C04 | مثبت غیرخالی، k>1 و تمام حروف مشاهده‌شدهٔ مثبت و منفی در یک بلوک؛ single_active_block | Global برنده؛ شکاف Π+4(k−1)؛ NET اگر H از شکاف کمتر باشد | [Original_Proofs_EN.md](research/Original_Proofs_EN.md) §4 |
| C05 | پشتیبان مثبت فقط {a} با حداقل یک مثبت غیرخالی؛ هر منفی حرف بیرون از {a} دارد؛ unary_global_inert | Global برنده؛ K=Π+4(k−1)−D>0؛ NET اگر H<K | [Research_Proofs_EN.md](research/Research_Proofs_EN.md) §6؛ [Previous_Proofs_EN.md](research/Previous_Proofs_EN.md) §§5–6 |
| C06 | S⁺={a} و ε منفی، k>1؛ one_letter_positive_empty_negative | WG=25؛ WS=25+Π+4(k−1)؛ Global برنده؛ NET با مقایسهٔ شکاف و H | [Previous_Extension_Proofs_EN.md](research/Previous_Extension_Proofs_EN.md) §6 |
| C07 | الفبای دقیق {a,b}، بلوک‌های تک‌حرفی، بدون منفی، دو مثبت ba^n b^(n−1) و b a b^(n−1) a^(n−1)، n≥4 | NET Split؛ LG−H−WS=6n²−10n−51>0؛ در n=4: 99+170<274 | [Research_Proofs_EN.md](research/Research_Proofs_EN.md) §5؛ اسلایدهای 8–9 و 23–24 |
| C08 | بلوک‌های مرتب {a},{b},{c}؛ تنها منفی c؛ تمام مثبت‌ها دقیقاً n حرف a و n حرف b و تعدادشان binomial(2n,n)، n≥1؛ original_complete_balanced | NET Split برای این خانوادهٔ دقیق؛ حذف عضو یا تغییر منفی نیازمند قاعدهٔ دیگر است | [Original_Proofs_EN.md](research/Original_Proofs_EN.md) §§5–9 |
| C09 | منفی تهی و E=card(A)؛ درخت پیشوند برای هر حرف دقیقاً یک یال دارد؛ unique_edge_trie | WG=B(M,p,E)، WS=Π+ΣB(m_i,p_i,E_i)؛ B=m+p+(11E²+25E+6)/2؛ علامت WS−WG برنده یا تساوی را دقیق مشخص می‌کند؛ NET اگر abs(WS−WG)>H | [Coverage_Proofs_EN.md](research/Coverage_Proofs_EN.md) §§2–3؛ اسلاید 25 |
| C10 | یک مثبت بدون حرف تکراری و بدون منفی؛ single_distinct_word | زیرکلاس C09 با فرمول دقیق؛ ممکن است Global، Split یا تساوی باشد | [Previous_Proofs_EN.md](research/Previous_Proofs_EN.md) §6A |
| C11 | مثبت دلخواه؛ هر منفی دارای حرف خارج از پشتیبان مثبت | کران‌های تیزتر inert؛ برنده فقط در صورت جدایی بازه‌ها؛ تمام اعضای این دسته الزاماً تعیین تکلیف نمی‌شوند | [Research_Proofs_EN.md](research/Research_Proofs_EN.md) §4؛ اسلایدهای 7،20،21 |
| C12 | دادهٔ دلخواهِ معتبر و AND ممکن، شامل منفی اثرگذار | کران پایین و بالای عمومی؛ آزمون بازه‌ای زیر، وگرنه UNKNOWN | [Research_Proofs_EN.md](research/Research_Proofs_EN.md) §§2–3 و 8؛ اسلایدهای 5–6 و 17–19 |
| C13 | واژگان متناهی V و افراز ثابت، با جدول کامل قبلاً ساخته‌شده | مقایسهٔ دقیق یا تساوی/ناممکنی برای تمام ورودی‌های داخل V؛ بیرون V برابر OUT_OF_DOMAIN؛ هزینهٔ ساخت و بارگذاری جدا | [Coverage_Proofs_EN.md](research/Coverage_Proofs_EN.md) §§6–8؛ اسلایدهای 11 و 26 |

در C09، m_i و p_i پس از حذف تصاویر تکراری محلی محاسبه می‌شوند. شرط inert در C11 باید برای عوامل محلی نیز بعد از تخصیص منفی جدا بررسی شود. کلاس‌ها هم‌پوشانی دارند؛ ترتیب شاخه‌های برنامه و H آن‌ها را تغییر نده.

## آزمون نهایی گواهی

LG≤WG≤UG و LS≤WS≤US. اگر H+US<LG: NET Split. اگر H+UG<LS: NET Global. اگر فقط US<LG یا UG<LS برقرار است: برندهٔ PIPELINE داریم و لزوماً سود خالص نداریم. اگر هر دو هزینه دقیق و برابرند: TIE. در غیر این صورت UNKNOWN. تساوی صرفاً دو کران کافی نیست.

NET_*_COST ادعای برابری زبان دو خروجی ندارد. NET_*_EQUAL برابری را از یک استدلال مستقلِ معتبر نیز دارد. هیچ‌یک به‌تنهایی بازیابی زبان هدف را ثابت نمی‌کند.

## نمونه‌های قابل بازتولید

نمونهٔ دو تریسی در research/two_trace_example.json و گواهی‌های عددی در research/final_worked_examples.json هستند. مثال نقضِ تعمیم هزینه به برابری در research/quality_counterexample.json، quality_models.json و quality_global_trace.json نگه‌داری شده است. فایل static_selector.py مرجع اجرایی قواعد و [Research_Proofs_EN.md](research/Research_Proofs_EN.md) مرجع ریاضی جاری است. مسیر تمام گزارش‌های جدول نسبت به زیرپوشهٔ research است.
