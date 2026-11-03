# دور چهاردهم: بازیابی گواهی‌شده و میان‌بُر دقیق

پایان: ۲۰۲۶/۱۱/۰۴ تهران؛ پوشهٔ شروع دور حفظ شده است.

الگوریتم در سه نمونهٔ کنترل‌شده با ۲، ۳ و ۴ دستگاه، افراز واقعی را درست و یکتا برگرداند. شرط صریح: تعداد دستگاه‌ها معتبر و معلوم باشد، شاهدهای تمایزدهنده کافی باشند و افراز مؤلفه‌های اجباری با نمونه سازگار باشد. این تضمین بازیابی هر لاگ واقعی یا رفع ابهام داده‌های C013 نیست.

## اجرای بازیابی

python -B results/2026-11-03/partition_recovery_v14/audit/recovery_certificate_v2.py INPUT.json --known-k 2

ورودی فقط alphabet، positive و negative است؛ تعداد با آرگومان صریح داده می‌شود. حل‌گر فایل حقیقت را نمی‌خواند. زوج مثبت/منفی که فقط جابه‌جایی دو نماد مجاور فرق دارند، هم‌مالکی آن دو نماد را اثبات می‌کند. مؤلفه‌های گراف ساخته و سازگاری افراز آن‌ها بررسی می‌شود. اگر تعداد مؤلفه‌ها برابر K معلوم باشد، هر جواب باید همین افراز باشد: ادغام تعداد بلوک‌ها را کاهش می‌دهد. بدون K، تنها ریزترین افراز سازگار و خانوادهٔ ادغام‌ها گواهی می‌شوند.

مثال: مثبت‌های ε،ab،cd و منفی‌های ba،dc روی الفبای abcd، هم‌مالکی ab و cd را لازم می‌کنند. با K=2 فقط ab|cd باقی می‌ماند؛ بدون K، abcd نیز ممکن است.

سه نمونهٔ دارای پوشش کامل، ab|cd، ab|cd|ef و ab|cd|ef|gh را یکتا بازیابی کردند. شش کنترل پوشش ناقص یا جهان جابه‌جاپذیر، certificate_not_established دادند؛ این وضعیت اثبات ناممکن‌بودن افراز نیست. K معلوم به‌تنهایی کافی نیست. کل خانوادهٔ افرازهای این نمونه‌ها مستقل با RGS بررسی شد.

تریس‌های کالیبراسیون با پرسش از جهان مصنوعی جمع‌آوری شده‌اند. این دسترسی اضافی به برچسب است و یادگیری صرفاً غیرفعال روی لاگ اولیه نامیده نمی‌شود. پوشش گراف نسبت به حقیقت در ارزیابی بررسی می‌شود؛ نبود یال، اثبات استقلال نیست. دستگاه‌های کالیبراسیون لزوماً فرض همبندی قوی مولد C013 را ندارند.

## اجرای دقیق روی تریس بلند

python -B results/2026-11-03/partition_recovery_v14/implementation/solve_v1.py INPUT.json --seconds 5

ابتدا شمارش تنک نمادها بررسی می‌شود. اگر هر منفی یک نماد با شمارش دیده‌نشده در تمام مثبت‌ها داشته باشد، همهٔ افرازها سازگارند و شمارش Bell/Stirling، روابط زوج‌ها و گواه‌های فشرده مستقیم ساخته می‌شوند. وگرنه همان C010 دقیق اجرا می‌شود. این میان‌بُر اثبات‌شده است؛ C011 و حدس استفاده نشده است.

۴۵۲ نتیجهٔ صحت/بازیابی مستقل بررسی شد: صفر اختلاف. شامل هشت کنترل C013، دویست نمونهٔ تصادفی کوچک، نه کالیبراسیون برای هر دو حل‌گر و هجده اجرای گواه بازیابی است. چهار ورودی میلیون‌رویدادی قبلی بدون تغییر، برای هر روش سه بار در فرایند تازه اجرا شدند.

{'case_id': 'held_million_K1_n2', 'method': 'baseline', 'statuses': ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'], 'median_three_complete_cli_seconds': None, 'complete_output_bytes': []}

{'case_id': 'held_million_K1_n2', 'method': 'new', 'statuses': ['validated_complete', 'validated_complete', 'validated_complete'], 'median_three_complete_cli_seconds': 2.4691988999998102, 'complete_output_bytes': [200106, 200107, 200108]}

{'case_id': 'held_million_K1_n8', 'method': 'baseline', 'statuses': ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'], 'median_three_complete_cli_seconds': None, 'complete_output_bytes': []}

{'case_id': 'held_million_K1_n8', 'method': 'new', 'statuses': ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'], 'median_three_complete_cli_seconds': None, 'complete_output_bytes': []}

{'case_id': 'held_million_K20_n2', 'method': 'baseline', 'statuses': ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'], 'median_three_complete_cli_seconds': None, 'complete_output_bytes': []}

{'case_id': 'held_million_K20_n2', 'method': 'new', 'statuses': ['cooperative_incomplete', 'validated_complete', 'validated_complete'], 'median_three_complete_cli_seconds': None, 'complete_output_bytes': [200105, 200105]}

{'case_id': 'held_million_K20_n8', 'method': 'baseline', 'statuses': ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'], 'median_three_complete_cli_seconds': None, 'complete_output_bytes': []}

{'case_id': 'held_million_K20_n8', 'method': 'new', 'statuses': ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'], 'median_three_complete_cli_seconds': None, 'complete_output_bytes': []}

K1,n2 در نسخهٔ جدید هر سه بار کامل شد؛ میانه ۲٫۴۷ ثانیه، در حالی که مرجع هر سه بار با مهلت ۵ثانیه ناتمام ماند. K20,n2 دو اجرای کامل و یک ناتمام داشت؛ میانهٔ سه کامل یا ضریب سرعت ساختگی نمی‌دهیم. هیچ اجرای n8 در این بودجه کامل نشد. پاسخ‌های کاملِ این ورودی‌های بلند مبهم‌اند و مالکیت واقعی را تعیین نکردند.

خروجی جدید فشرده و خروجی C010 بازشده است؛ این مقایسهٔ هزینهٔ کل CLI است، نه برتری با خروجی هم‌اندازه. همهٔ شمارش‌ها و گواه‌های کامل مستقلاً بررسی شدند. پیش‌بررسی برای الفبای ثابت و هش معمول، خطی در مجموع نویسه‌ها و واژه‌هاست؛ حساب اعداد بزرگ، مرتب‌سازی و خروجی جدا هزینه دارند. fallback همچنان می‌تواند نسبت به تعداد اتم‌ها نمایی/ترکیبی باشد. جست‌وجوی گواه گراف نیز همهٔ زوج‌های مثبت/منفی را می‌بیند و الگوریتم عمومیِ سریع برای هر نمونه نیست.

## شواهد و محدودیت‌ها

ممیزی در ۲۵۶٫۹۸ ثانیه از بودجهٔ ۶۰۰ تمام شد. گزارش‌های مستقل در audit/runs/، اثبات‌ها در theory/PROOFS_v1.md و بازبینی کدها در theory/SOURCE_REVIEW_V1.md و implementation/RECOVERY_STATIC_REVIEW_V1.md هستند.

مستر به‌دلیل پاسخ‌ندادن ابزار هماهنگی، همان اسکریپت منجمد ممیزی را مستقیم اجرا کرد؛ جریان‌های خام و یادداشت در coordination محفوظ‌اند. اشکال descriptor پیش‌نویس بازیابی اصلاح شد. منشأ نسخهٔ بازسازی‌شده و موجودنبودن هش اولیه صریحاً در RECOVERY_DRAFT_ATTEMPT_V1.json ثبت است؛ آن را نسخهٔ بایت‌به‌بایت اولیه یا لاگ اجرای واقعی معرفی نمی‌کنیم.

نتیجهٔ مثبت: بازیابی افراز یکتا تحت شرط روشن و بهبود واقعی روی بخشی از تریس‌های بلند. نتیجهٔ منفی: بازیابی عمومیِ مالکیت از دادهٔ مبهم و سرعت عمومی تضمین نشده است. ادامهٔ علمی باید روی کسب شاهدهای تمایزدهنده و گسترش گواه‌ها متمرکز شود؛ نتیجه‌ای برای کار اجرا‌نشده ادعا نمی‌شود.
