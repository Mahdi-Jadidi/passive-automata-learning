# ممیزی C014

وضعیت زمان‌گیری: accepted_with_censoring؛ خطاها: 0.

خروجی C010 شامل تصاویر و شاهدهای بازشده است؛ روش جدید در شاخهٔ سریع گواهی فشرده می‌دهد. نسبت زمان کل CLI، برتری با هزینهٔ ورودی/خروجی یکسان نیست. حالت پیش‌فرض no-K است و شاخهٔ همهٔ افرازها به معنای بازیابی مالکیت فیزیکی نیست.

| ورودی | روش | وضعیت سه تکرار | میانهٔ سه اجرای کامل |
|---|---|---|---:|
| held_million_K1_n2 | baseline | ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'] | None |
| held_million_K1_n2 | new | ['validated_complete', 'validated_complete', 'validated_complete'] | 2.4691988999998102 |
| held_million_K1_n8 | baseline | ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'] | None |
| held_million_K1_n8 | new | ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'] | None |
| held_million_K20_n2 | baseline | ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'] | None |
| held_million_K20_n2 | new | ['cooperative_incomplete', 'validated_complete', 'validated_complete'] | None |
| held_million_K20_n8 | baseline | ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'] | None |
| held_million_K20_n8 | new | ['cooperative_incomplete', 'cooperative_incomplete', 'cooperative_incomplete'] | None |

صحت و بازیابی گراف در correctness_report.json ثبت شده‌اند. پرس‌وجوهای کالیبراسیون دسترسی اضافی به برچسب جهان مصنوعی هستند؛ یادگیری passive روی دادهٔ اصلی نامیده نمی‌شوند. نبود پوشش یا رفتار جابه‌جاپذیر، گواهی گراف را محدود می‌کند؛ نبود یال اثبات استقلال نیست.
