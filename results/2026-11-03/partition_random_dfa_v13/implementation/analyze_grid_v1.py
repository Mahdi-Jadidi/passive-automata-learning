"""Read frozen C013 audit artifacts; write a fresh descriptive analysis only."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import uuid

CAPS = [8, 64, 512, 4096, 65536, 1000000]
CATEGORIES = ['complete_ambiguous', 'unique_recovery', 'cooperative_unknown',
              'hard_timeout', 'error', 'unstarted']


class Reader:
    def __init__(self, root):
        self.root = root
        self.sources = {}
        self.cache = {}

    def path(self, value):
        p = Path(value)
        return p.resolve() if p.is_absolute() else (self.root / p).resolve()

    def read(self, path):
        path = self.path(path)
        raw = path.read_bytes()
        h = hashlib.sha256(raw).hexdigest()
        if str(path) in self.sources and self.sources[str(path)] != h:
            raise ValueError(f'input changed during analysis: {path}')
        self.sources[str(path)] = h
        return raw

    def obj(self, path):
        path = self.path(path)
        if str(path) not in self.cache:
            self.cache[str(path)] = json.loads(self.read(path))
        return self.cache[str(path)]

    def stable(self):
        for path, expected in self.sources.items():
            h = hashlib.sha256(Path(path).read_bytes()).hexdigest()
            if h != expected:
                raise ValueError(f'input changed before finalization: {path}')


def key(row):
    return (row['K'], row['max_length'], row['samples_per_label'], row['rep'], row['kind'])


def planned():
    return [(k, cap, n, rep, 'broad') for cap in CAPS for n in (2, 8)
            for k in range(1, 21) for rep in (1, 2, 3)] + [
                (k, 1000000, 8, 1, 'confirmation') for k in (1, 20)]


def capture_info(reader, attempt):
    folder = reader.root / 'attempts' / attempt
    cap = reader.obj(folder / 'result.json')
    manifest = reader.obj(folder / 'manifest.json')
    return folder, cap, manifest


def write_csv(path, rows):
    fields = sorted({k for row in rows for k in row})
    with path.open('x', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                         for k, v in row.items()} for row in rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--audit', type=Path, required=True)
    ap.add_argument('--ledger', type=Path, nargs='+', required=True)
    ap.add_argument('--ledger-sha256', nargs='+', required=True)
    ap.add_argument('--validation', type=Path, required=True)
    ap.add_argument('--preparation-ledger', type=Path, nargs='*', default=[])
    ap.add_argument('--input-map', type=Path)
    ap.add_argument('--out', type=Path, required=True, help='analysis parent outside audit tree')
    args = ap.parse_args(argv)
    audit = args.audit.resolve()
    if args.out.resolve() == audit or audit in args.out.resolve().parents:
        ap.error('analysis output must be outside the read-only audit tree')
    if len(args.ledger) != len(args.ledger_sha256):
        ap.error('one expected SHA256 is required per final ledger')
    reader = Reader(audit)
    ledger_rows = {}
    for path, expected in zip(args.ledger, args.ledger_sha256):
        raw = reader.read(path)
        if hashlib.sha256(raw).hexdigest() != expected.lower():
            raise ValueError(f'final ledger hash mismatch: {path}')
        for line in raw.decode('utf-8-sig').splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            k = key(row)
            if k in ledger_rows:
                raise ValueError(f'duplicate slot; do not combine historical ledgers: {k}')
            if k not in planned():
                raise ValueError(f'unplanned grid slot: {k}')
            ledger_rows[k] = row
    validation = reader.obj(args.validation)
    validated = {key(row): row for row in validation.get('rows', [])}
    mapping = reader.obj(args.input_map).get('entries', {}) if args.input_map else {}
    preparations = defaultdict(list)
    for path in args.preparation_ledger:
        for line in reader.read(path).decode('utf-8-sig').splitlines():
            if line.strip():
                row = json.loads(line)
                preparations[(row['K'], row['max_length'])].append(row)
    metrics_cache = {}
    generation_rows = []

    def sample_metrics(k, cap, n, row):
        entry = mapping.get(f'{k}:{cap}', {})
        directory = (reader.path(row['input']).parent if row.get('input') else
                     reader.path(entry['directory']) if entry.get('directory') else
                     audit / 'data' / 'grid' / f'K{k}_M40_L{cap}')
        cache_key = str(directory)
        if cache_key not in metrics_cache:
            result = {'directory': str(directory)}
            genpath = directory / 'generation.json'
            if genpath.is_file():
                gen = reader.obj(genpath)
                world = reader.obj(directory / 'world.json')
                valid = reader.obj(directory / 'validation.json')
                result.update(world_sha256=reader.sources[str((directory / 'world.json').resolve())],
                              true_K=world['true_devices'], profile=gen.get('event_profile'),
                              samples=gen.get('samples', []))
                gr = {'K': k, 'cap': cap, 'directory': str(directory),
                      'shared_parent_sample_count': gen.get('samples_per_label'),
                      'world_internal_seconds': valid.get('world_generation_seconds'),
                      'sample_internal_seconds': gen.get('generation_seconds'),
                      'independent_replay_seconds': valid.get('independent_label_replay_seconds'),
                      'preparation_internal_wall_seconds': valid.get('wall_preparation_seconds'),
                      'attempts': []}
                for prep in preparations[(k, cap)]:
                    if prep.get('attempt_id'):
                        _, captured, _ = capture_info(reader, prep['attempt_id'])
                        gr['attempts'].append({'attempt_id': prep['attempt_id'],
                            'execution_status': captured.get('execution_status'),
                            'capture_wall_seconds': captured.get('duration_seconds'),
                            'subprocess_wall_seconds': captured.get('subprocess_seconds')})
                    else:
                        gr['attempts'].append({'status': prep.get('status')})
                generation_rows.append(gr)
            metrics_cache[cache_key] = result
        meta = metrics_cache[cache_key]
        samples = [s for s in meta.get('samples', []) if s['index'] < n]
        return {'actual_T': sum(s['length'] for s in samples) if 'samples' in meta else None,
                'actual_lengths': [s['length'] for s in samples],
                'actual_sample_count': len(samples) if 'samples' in meta else None,
                'world_sha256': meta.get('world_sha256'), 'true_K': meta.get('true_K'),
                'profile': meta.get('profile'), 'data_directory': meta['directory']}

    def safe_metrics(k, cap, n, row):
        try:
            return sample_metrics(k, cap, n, row)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return {'actual_T': None, 'actual_lengths': [], 'actual_sample_count': None,
                    'world_sha256': None, 'true_K': None, 'profile': None,
                    'data_directory': None, 'metadata_error': str(exc)}

    rows = []
    for k, cap, n, rep, kind in planned():
        slot = (k, cap, n, rep, kind)
        original = ledger_rows.get(slot, {})
        row = {'K': k, 'cap': cap, 'n': n, 'rep': rep, 'kind': kind,
               'cooperative_budget_seconds': 20 if kind == 'confirmation' else 5,
               'category': 'unstarted', 'ledger_status': original.get('status', 'absent_from_final_ledger'),
               'attempt_id': original.get('attempt_id'), **safe_metrics(k, cap, n, original)}
        if original.get('attempt_id'):
            try:
                folder, captured, manifest = capture_info(reader, original['attempt_id'])
                command = manifest['command_argv']
                budget = float(command[command.index('--seconds') + 1])
                if budget != row['cooperative_budget_seconds']:
                    raise ValueError('budget differs from preregistered kind')
                row.update(capture_wall_seconds=captured.get('duration_seconds'),
                           subprocess_wall_seconds=captured.get('subprocess_seconds'),
                           output_bytes=captured.get('stdout_bytes'), exit_code=captured.get('exit_code'))
                if not captured.get('child_reaped') or captured.get('cleanup_error'):
                    raise ValueError('capture supervision failed')
                for stream in ('stdout', 'stderr'):
                    content = reader.read(folder / (stream + '.bin'))
                    if hashlib.sha256(content).hexdigest() != captured[stream + '_sha256']:
                        raise ValueError(stream + ' hash mismatch')
                if captured['execution_status'] == 'timed_out':
                    row['category'] = 'hard_timeout'
                else:
                    raw = reader.read(folder / 'stdout.bin')
                    if hashlib.sha256(raw).hexdigest() != captured['stdout_sha256']:
                        raise ValueError('stdout hash mismatch')
                    result = json.loads(raw)
                    row['solver_status'] = result.get('status')
                    if captured.get('execution_status') not in ('success', 'program_error'):
                        raise ValueError('capture supervision or environment failure')
                    if captured.get('exit_code') == 3 and result.get('complete') is False and result.get('status') == 'unknown':
                        row['category'] = 'cooperative_unknown'
                    elif captured.get('exit_code') == 0 and result.get('complete') is True:
                        check = validated.get(slot, {})
                        expected = 'unique_recovery' if result.get('partition_count') == 1 else 'completed_ambiguous'
                        if check.get('status') != expected or not check.get('truth_compatible'):
                            raise ValueError('complete output lacks matching independent validation')
                        if check.get('total') != result.get('partition_count') or row.get('true_K') not in (None, k):
                            raise ValueError('validation count or saved true K mismatch')
                        row.update(category='unique_recovery' if expected == 'unique_recovery' else 'complete_ambiguous',
                                   partition_count=result['partition_count'], truth_compatible=True)
                    else:
                        raise ValueError('unrecognized result or failed process')
            except (OSError, ValueError, KeyError, TypeError) as exc:
                row.update(category='error', analysis_error=str(exc))
        rows.append(row)

    cells = []
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row['K'], row['cap'], row['n'], row['kind'])].append(row)
    completed = {'complete_ambiguous', 'unique_recovery'}
    for (k, cap, n, kind), group in sorted(grouped.items()):
        all3 = (kind == 'broad' and len(group) == 3 and
                all(r['category'] in completed for r in group) and
                len({(r['actual_T'], r['world_sha256']) for r in group}) == 1)
        cells.append({'K': k, 'cap': cap, 'n': n, 'kind': kind,
                      'categories': {name: sum(r['category'] == name for r in group) for name in CATEGORIES},
                      'actual_T': group[0]['actual_T'], 'true_K': group[0]['true_K'],
                      'world_sha256': group[0]['world_sha256'],
                      'profile': group[0]['profile'], 'all_three_complete': all3,
                      'median_subprocess_seconds': statistics.median(r['subprocess_wall_seconds'] for r in group) if all3 else None,
                      'median_capture_seconds': statistics.median(r['capture_wall_seconds'] for r in group) if all3 else None})
    fits = []
    fit_groups = defaultdict(list)
    for cell in cells:
        if cell['kind'] == 'broad':
            fit_groups[(cell['K'], cell['n'], cell['world_sha256'], cell['profile'])].append(cell)
    for (k, n, world, profile), group in fit_groups.items():
        usable = [c for c in group if c['all_three_complete'] and
                  c['actual_T'] and c['median_subprocess_seconds'] > 0]
        if len({c['cap'] for c in usable}) < 3 or len({c['actual_T'] for c in usable}) < 3:
            continue
        x = [math.log(c['actual_T']) for c in usable]
        y = [math.log(c['median_subprocess_seconds']) for c in usable]
        xm, ym = statistics.mean(x), statistics.mean(y)
        slope = sum((a-xm)*(b-ym) for a,b in zip(x,y)) / sum((a-xm)**2 for a in x)
        fits.append({'K': k, 'n': n, 'world_sha256': world, 'profile': profile,
                     'slope_log_time_log_actual_T': slope, 'caps': [c['cap'] for c in usable],
                     'excluded_caps': [c['cap'] for c in group if c not in usable],
                     'interpretation': 'descriptive within fixed world/count/profile, selected complete lengths only; no asymptotic or censored regression claim'})
    generation_keys = {(g['K'], g['cap']) for g in generation_rows}
    for k in range(1, 21):
        for cap in CAPS:
            if (k, cap) not in generation_keys:
                attempts = []
                for prep in preparations[(k, cap)]:
                    item = {'attempt_id': prep.get('attempt_id'), 'status': prep.get('status')}
                    if prep.get('attempt_id'):
                        try:
                            _, captured, _ = capture_info(reader, prep['attempt_id'])
                            item.update(capture_wall_seconds=captured.get('duration_seconds'),
                                        subprocess_wall_seconds=captured.get('subprocess_seconds'))
                        except (OSError, ValueError, KeyError) as exc:
                            item['metadata_error'] = str(exc)
                    attempts.append(item)
                generation_rows.append({'K': k, 'cap': cap, 'status': 'missing_generation_metadata', 'attempts': attempts})
    reader.stable()
    out = args.out.resolve() / ('analysis_' + uuid.uuid4().hex)
    out.mkdir(parents=True, exist_ok=False)
    payload = {'slots': rows, 'cells': cells, 'generation_shared_parents': generation_rows,
               'descriptive_fits': fits, 'validation_status': validation.get('status'),
               'source_hashes': reader.sources, 'analysis_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out / 'analysis.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    write_csv(out / 'slots.csv', rows)
    write_csv(out / 'cells.csv', cells)
    write_csv(out / 'generation.csv', generation_rows)
    text = ['# تحلیل توصیفی شبکهٔ C013', '',
            'هر ردیف CSV یک جایگاه برنامه‌ریزی‌شده است؛ نبودن اجرا نیز ثبت شده است. ',
            'تأییدهای ۲۰ثانیه‌ای مستقل از شبکهٔ ۵ثانیه‌ای گزارش می‌شوند. ',
            'میانه فقط برای خانه‌هایی محاسبه شده که هر سه تکرارشان کامل و مستقل تأیید شده‌اند.', '',
            '| نوع | جایگاه‌ها | وضعیت‌ها |', '|---|---:|---|']
    for kind in ('broad', 'confirmation'):
        subset = [r for r in rows if r['kind'] == kind]
        text.append(f'| {kind} | {len(subset)} | {json.dumps(dict(Counter(r["category"] for r in subset)),ensure_ascii=False)} |')
    text += ['', 'زمان تولید برای والد مشترک n=8 گزارش شده و برای خانه‌های n=2 و n=8 دوباره جمع نمی‌شود.',
             'زمان داخلی تولید، بازپخش مستقل و زمان خارجی فرایند/ثبت جدا هستند. ',
             'actual_T مجموع طول نمونه‌های واقعی همان n است؛ سقف طول جای آن استفاده نشده است.',
             f'تعداد برازش‌های مجاز: {len(fits)}. هر شیب فقط توصیف طول‌های کامل در جهان/K/n ثابت است؛ سانسور و انتخاب طول‌ها مانع ادعای کران مجانبی است.',
             'سازگاری حقیقت با نمونه، بازیابی یکتای مالکیت نیست؛ دستهٔ unique_recovery فقط با خروجی دقیق و تأیید مستقل ثبت می‌شود.']
    text += ['', '| K در برنامه | K واقعی ذخیره‌شده | سقف طول | n هر برچسب | نوع | وضعیت تکرارها | میانهٔ ثانیهٔ فرایند (فقط ۳ کامل) |',
             '|---:|---:|---:|---:|---|---|---:|']
    for cell in cells:
        text.append(f'| {cell["K"]} | {cell["true_K"]} | {cell["cap"]} | {cell["n"]} | {cell["kind"]} | {json.dumps(cell["categories"])} | {cell["median_subprocess_seconds"]} |')
    (out / 'SUMMARY_FA.md').write_text('\n'.join(text) + '\n', encoding='utf-8')
    print(json.dumps({'analysis_directory': str(out), 'slots': len(rows), 'fits': len(fits)}))


if __name__ == '__main__':
    main()
