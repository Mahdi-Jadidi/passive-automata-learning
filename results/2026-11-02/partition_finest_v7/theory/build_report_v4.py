"""Documentation-only report revision; does not execute scientific code."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TARGET = HERE / 'SCIENTIFIC_REPORT_CANDIDATE_FA_v4.md'
if TARGET.exists():
    raise FileExistsError(TARGET)
text = (HERE / 'SCIENTIFIC_REPORT_CANDIDATE_FA_v3.md').read_text(encoding='utf-8-sig')

def replace(old, new):
    global text
    if text.count(old) != 1:
        raise ValueError(f'Expected exactly one occurrence: {old[:90]!r}')
    text = text.replace(old, new)

replace('ویرایش سوم، پس از پذیرش v4 و scale ساختاریافته',
        'ویرایش چهارم، پس از پذیرش گیت اصلی، کنترل‌ها، مثال هدفمند و CLI')
replace('پذیرفته شده‌اند؛ الحاق هدفمند doubled-pairs، CLI ریشهٔ v4 و زمان‌گیری رسمی\nهنوز بازند. پیش‌نویس v1،',
        'پذیرفته شده‌اند؛ الحاق هدفمند doubled-pairs، CLI ریشهٔ v4 و کنترل‌های\nنسخهٔ v4 نیز مستقل پذیرفته‌اند. فقط پیوست زمان‌گیری رسمی باز است. پیش‌نویس v1،')
replace('هر JSON بدشکل. runtime اینجا تغییر نکرده است.',
        'هر JSON بدشکل. کنترل‌های هدفمند تازهٔ وقفه در بخش بعد آمده‌اند؛\nپذیرش آن نقاط مشخص، محدودیت‌های ایستای بالا را خودبه‌خود رفع نمی‌کند.\nruntime اینجا تغییر نکرده است.')
replace('این مثال CLIِ پیاده‌سازی است؛ پذیرشِ CLI ریشهٔ v4 هنوز در این گزارش باز\nاست و با گیت provider یکی گرفته نمی‌شود.',
        'این مثال CLIِ پیاده‌سازی است. wrapper ریشه نیز جداگانه با v4 پذیرفته\nشده است؛ دامنهٔ دقیق آن در بخش کنترل‌های تکمیلی آمده است.')
replace('در نظریه ریزترین ab|cd|ef و گراف قدیمیِ بی‌یال دارد؛ اما الحاقِ پذیرش\nprovider آن در این نسخه **هنوز باز است**. از گزارش oracle آن به‌تنهایی\nموفقیت runtime یا زمان‌گیری نمی‌سازیم. پذیرش سلول‌های مشخصِ بزرگ در بخش scale بالا آمده است؛ عملکرد رسمی\nهنوز باز است و سقف‌های هدفِ پروتکل به تضمین عمومی تبدیل نشده‌اند.',
        'ریزترین ab|cd|ef و گراف قدیمیِ بی‌یال دارد. اکنون الحاق مستقلِ\n`audit/targeted_empty_graph/provider_gate_v2.json` با status=accepted و\nfailures خالی، هر دو خروجی adaptive و reference و دو بازپخش مستقل گواه\nرا پذیرفته است. هر دو گواه از نوع complete_separator_cover هستند؛ پس\nاین موفقیت به میان‌بُرِ گراف قدیمی نسبت داده نمی‌شود. oracle تمام kها\nپنج افراز سازگار و سه جواب دوبخشی دارد و ریزترین آن همان سه بلوک جفتی\nاست. این پذیرش عملکرد runtime همین نمونه را تأیید می‌کند؛ ادعای سرعت\nیا شمار فراخوانی oracle از این خلاصه استخراج نمی‌شود. عملکرد رسمی\nهنوز باز است و سقف‌های هدفِ پروتکل به تضمین عمومی تبدیل نشده‌اند.')
replace('## منابع و مسیرهای ناموفق', '''## کنترل‌های تکمیلیِ پذیرفته‌شده

`audit/validation_v2/provider_controls_v4.json` با status=accepted و
failures خالی، شش کنترل ورودی نامعتبر در دو mode، رد mode نامعتبر،
deadline منقضی پیش از کار، توقف در مرحلهٔ swap و توقف/KeyboardInterrupt
پس از یک separator را ثبت می‌کند. در دو مورد اخیر یک عضو history حفظ
شده و خروجی جزئی فاقد finality است؛ موارد پیش از کار و swap تاریخچهٔ
تهی دارند. این‌ها کنترل نقاط مشخص‌اند؛ تضمین تحمل تمام لحظه‌های قطع
ناهمگام یا همهٔ ورودی‌های JSON بدشکل نیستند. کنترل‌ها runtime را تغییر
نداده‌اند و هیچ نتیجهٔ incomplete به یکتایی تبدیل نشده است.

`audit/root_cli_v2.json` نیز status=accepted و failures خالی دارد:
اجرای موفقِ wrapper ریشه، finest_unique دوبلوکی، دو یال forced بازپخش‌شده
و فرایند فرزندِ جمع‌آوری‌شده ثبت‌اند. هش provider و CLI با نسخهٔ منجمد
بخش v4 یکسان است. هش wrapper ریشه:
`d4d1644fa3144c68c626fc8daff818e9500a89453a21871df45ffb3e7b7232de`.
این گیتِ یک اجرای مشخصِ رابط است، نه پوشش همهٔ مسیرهای رابط و نه بنچمارک.

سه پذیرش تازه با بازبینی مستر تأیید شده‌اند. snapshot، هش منابع و رابطه
با ویرایش سوم در `theory/report_v4_evidence/MANIFEST.json` نگهداری می‌شوند؛
نسخه‌های قبلی و گزارش هدفمند v1 محفوظ‌اند. تهیهٔ این متن و بستهٔ شواهد،
خواندن/ثبت مستندات است و اجرای علمی جدیدی ندارد.

## منابع و مسیرهای ناموفق''')
replace('گیت v4 و scaleهای مشخص اکنون پذیرفته‌اند؛ الحاق هدفمند doubled-pairs،\nCLI ریشهٔ v4 و پیوست زمان‌گیری رسمی تا رسیدن شواهد واقعی باز می‌مانند. در تهیهٔ این ویرایش هیچ اجرا یا اصلاح runtime انجام نشد.',
        'گیت v4، scaleهای مشخص، الحاق هدفمند doubled-pairs، کنترل‌های هدفمند\nو CLI ریشهٔ v4 اکنون پذیرفته‌اند. فقط پیوست زمان‌گیری رسمی باز است؛\nاین گزارش ادعای کارایی رسمی ندارد. در تهیهٔ این ویرایش هیچ آزمایش\nعلمی یا اصلاح runtime انجام نشد.')
TARGET.write_text(text, encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

evidence = HERE / 'report_v4_evidence'
evidence.mkdir()
sources = [
    'coordination/CORRECTNESS_ACCEPTANCE_V4.json',
    'audit/validation_v2/provider_gate_v4.json',
    'audit/scale_v1/long_v4_replay_v1.json',
    'audit/scale_v1/scale_validation_v4.json',
    'audit/targeted_empty_graph/provider_gate_v2.json',
    'audit/root_cli_v2.json',
    'audit/validation_v2/provider_controls_v4.json',
    'theory/SCIENTIFIC_REPORT_CANDIDATE_FA_v3.md',
    'theory/report_v3_evidence/MANIFEST.json',
]
records = []
for rel in sources:
    source = ROOT / rel
    snap = evidence / rel.replace('/', '__')
    data = source.read_bytes()
    snap.write_bytes(data)
    assert digest(source) == digest(snap)
    records.append({'source': rel, 'snapshot': snap.name, 'sha256': digest(snap)})
manifest = {
    'id': 'C007-THEORY-REPORT-004',
    'report': '../' + TARGET.name,
    'report_sha256': digest(TARGET),
    'scientific_status': 'v4_main_gate_structured_scale_targeted_controls_and_root_cli_accepted',
    'evidence': records,
    'pending': ['official timing appendix'],
    'gate_distinct_inputs': 218, 'gate_mode_outputs': 436,
    'targeted_addendum_outputs': 2, 'targeted_independent_certificate_replays': 2,
    'targeted_all_k_partition_count': 5, 'targeted_binary_partition_count': 3,
    'root_cli_accepted_runs': 1,
    'controls_scope': 'six invalid-input checks across both modes; invalid mode; specified deadline and stop/interrupt points only',
    'official_timing_claim': False, 'new_experiments': 0,
    'runtime_or_git_edits': False,
    'internal_metric_caveat': 'fallback phase clocks are not disjoint; use whole-process time',
    'static_partial_output_limitations_preserved': True,
}
(evidence / 'MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
readiness = HERE / 'READINESS.json'
backup = HERE / 'READINESS_006.json'
if backup.exists():
    raise FileExistsError(backup)
backup.write_bytes(readiness.read_bytes())
ready = json.loads(readiness.read_text(encoding='utf-8-sig'))
ready.update({
    'id': 'C007-THEORY-READINESS-007',
    'scientific_status': manifest['scientific_status'],
    'report': TARGET.name,
    'report_evidence': 'report_v4_evidence/MANIFEST.json',
    'provider_gate': 'main 218 distinct inputs / 436 outputs accepted; targeted addendum and specified controls accepted',
    'v4_acceptance': 'master accepted main gate, specified structured scale, targeted doubled-pairs, root CLI and specified controls',
    'pending': manifest['pending'],
})
readiness.write_text(json.dumps(ready, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'report': str(TARGET), 'sha256': digest(TARGET), 'new_experiments': 0, 'pending': manifest['pending']}, ensure_ascii=False))
