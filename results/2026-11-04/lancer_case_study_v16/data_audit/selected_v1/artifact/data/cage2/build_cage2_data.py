#!/usr/bin/env python3
"""End-to-end cage2 data pipeline: raws → converted traces → per-trial training/eval dirs."""
import argparse
import ast
import os
import shutil
import sys
from multiprocessing import Pool, cpu_count

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from convert_traces import convert_trace

RAW_DIR_DEFAULT = os.path.join(SCRIPT_DIR, 'cage2_raw_traces')
CONVERTED_DIR_DEFAULT = os.path.join(SCRIPT_DIR, 'cage2_converted_traces')
TESTS_DIR_DEFAULT = os.path.join(SCRIPT_DIR, 'tests')
SHUFFLES_DIR_DEFAULT = os.path.join(SCRIPT_DIR, 'shuffles')

EXP1_LENGTHS = [30, 50, 100]
EXP1_NUM_TRIALS = 5
EXP1_TRAIN_PER_TRIAL = 900
EXP1_EVAL_PER_TRIAL = 100

EXP2_LENGTH = 30
EXP2_NUM_TRIALS = 3
EXP2_TRAIN_PER_TRIAL = 4500
EXP2_EVAL_PER_TRIAL = 500


def _convert_one(args):
    idx, raw_path, dst_path = args
    try:
        result = convert_trace(raw_path, episode_num=1)
        if result is None:
            return idx, False, 'convert_trace returned None'
        with open(dst_path, 'w') as f:
            f.write(repr(result))
        return idx, True, None
    except Exception as e:
        return idx, False, str(e)


def step_convert(raw_dir, converted_dir, cpus, force, limit):
    os.makedirs(converted_dir, exist_ok=True)
    raws = []
    for i in range(1, limit + 1):
        src = os.path.join(raw_dir, f'raw_{i}.yaml')
        if not os.path.exists(src):
            sys.exit(f'missing raw input: {src}')
        dst = os.path.join(converted_dir, f'output_{i}.txt')
        if os.path.exists(dst) and not force:
            continue
        raws.append((i, src, dst))

    if not raws:
        print(f'[convert] all 5000 output files already present in {converted_dir} (use --force to redo)')
        return

    print(f'[convert] converting {len(raws)} raw traces with {cpus} worker(s)...', flush=True)
    ok = fail = 0
    with Pool(cpus) as pool:
        for i, success, err in pool.imap_unordered(_convert_one, raws):
            if success:
                ok += 1
            else:
                fail += 1
                print(f'  raw_{i}: {err}', file=sys.stderr)
            done = ok + fail
            if done % 500 == 0 or done == len(raws):
                print(f'  {done}/{len(raws)} (ok={ok}, fail={fail})', flush=True)
    if fail:
        sys.exit(f'[convert] {fail} conversions failed')


def parse_shuffle(path):
    perm = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            _, name = line.split(':', 1)
            perm.append(name.strip())
    return perm


def _truncate_and_write(args):
    src_path, dst_path, n_steps = args
    with open(src_path) as f:
        trace = ast.literal_eval(f.read())
    trace[0] = trace[0][:n_steps]
    with open(dst_path, 'w') as f:
        f.write(str(trace))


def _build_trial(tasks, cpus, label):
    print(f'[trials] {label}: {len(tasks)} files', flush=True)
    if cpus > 1:
        with Pool(cpus) as pool:
            for i, _ in enumerate(pool.imap_unordered(_truncate_and_write, tasks), start=1):
                if i % 2000 == 0 or i == len(tasks):
                    print(f'  {label}: {i}/{len(tasks)}', flush=True)
    else:
        for i, task in enumerate(tasks, start=1):
            _truncate_and_write(task)
            if i % 2000 == 0 or i == len(tasks):
                print(f'  {label}: {i}/{len(tasks)}', flush=True)


def step_trials(converted_dir, tests_dir, shuffles_dir, cpus, force,
                lengths=None, trials=None, skip_exp2=False):
    master_shuffle = os.path.join(shuffles_dir, 'exp1_master.txt')
    if not os.path.exists(master_shuffle):
        sys.exit(f'missing Exp 1 master shuffle: {master_shuffle}')
    master_perm = parse_shuffle(master_shuffle)
    if len(master_perm) < 5000:
        sys.exit(f'master shuffle has only {len(master_perm)} entries, expected >=5000')

    exp1_lengths = lengths if lengths else EXP1_LENGTHS
    exp1_trials  = trials  if trials  else list(range(1, EXP1_NUM_TRIALS + 1))
    exp2_trials  = trials  if trials  else list(range(1, EXP2_NUM_TRIALS + 1))

    for length in exp1_lengths:
        for trial in exp1_trials:
            train_dst = os.path.join(tests_dir, f'{length}_steps', f'trial{trial}', 'training_traces')
            eval_dst = os.path.join(tests_dir, f'{length}_steps', f'trial{trial}', 'eval_traces')
            if os.path.isdir(train_dst) and os.listdir(train_dst) and not force:
                print(f'[trials] skip existing Exp1 {length}steps trial{trial} (use --force to rebuild)')
                continue
            os.makedirs(train_dst, exist_ok=True)
            os.makedirs(eval_dst, exist_ok=True)
            offset = (trial - 1) * 1000
            tasks = []
            for i in range(EXP1_TRAIN_PER_TRIAL):
                src = os.path.join(converted_dir, master_perm[offset + i])
                dst = os.path.join(train_dst, f'output_{i + 1}.txt')
                tasks.append((src, dst, length))
            for i in range(EXP1_EVAL_PER_TRIAL):
                src = os.path.join(converted_dir, master_perm[offset + EXP1_TRAIN_PER_TRIAL + i])
                dst = os.path.join(eval_dst, f'trace{i + 1}.txt')
                tasks.append((src, dst, length))
            _build_trial(tasks, cpus, f'Exp1 {length}steps trial{trial}')

    if skip_exp2:
        return

    for trial in exp2_trials:
        trial_dir = os.path.join(tests_dir, '30_steps_large', f'trial{trial}')
        shuffle_path = os.path.join(shuffles_dir, f'exp2_trial{trial}.txt')
        if not os.path.exists(shuffle_path):
            sys.exit(f'missing Exp 2 trial{trial} shuffle: {shuffle_path}')
        perm = parse_shuffle(shuffle_path)
        if len(perm) < 5000:
            sys.exit(f'Exp 2 trial{trial} shuffle has only {len(perm)} entries')

        train_dst = os.path.join(trial_dir, 'training_traces')
        eval_dst = os.path.join(trial_dir, 'eval_traces')
        if os.path.isdir(train_dst) and os.listdir(train_dst) and not force:
            print(f'[trials] skip existing Exp2 trial{trial} (use --force to rebuild)')
            continue
        os.makedirs(train_dst, exist_ok=True)
        os.makedirs(eval_dst, exist_ok=True)
        tasks = []
        for i in range(EXP2_TRAIN_PER_TRIAL):
            src = os.path.join(converted_dir, perm[i])
            dst = os.path.join(train_dst, f'output_{i + 1}.txt')
            tasks.append((src, dst, EXP2_LENGTH))
        for i in range(EXP2_EVAL_PER_TRIAL):
            src = os.path.join(converted_dir, perm[EXP2_TRAIN_PER_TRIAL + i])
            dst = os.path.join(eval_dst, f'trace{i + 1}.txt')
            tasks.append((src, dst, EXP2_LENGTH))
        _build_trial(tasks, cpus, f'Exp2 trial{trial}')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw-dir', default=RAW_DIR_DEFAULT)
    ap.add_argument('--converted-dir', default=CONVERTED_DIR_DEFAULT)
    ap.add_argument('--tests-dir', default=TESTS_DIR_DEFAULT)
    ap.add_argument('--shuffles-dir', default=SHUFFLES_DIR_DEFAULT)
    ap.add_argument('--step', choices=['convert', 'trials', 'all'], default='all')
    ap.add_argument('--cpus', type=int, default=cpu_count())
    ap.add_argument('--force', action='store_true', help='overwrite existing outputs')
    ap.add_argument('--limit', type=int, default=5000, help='convert only first N raws (convert step only)')
    ap.add_argument('--lengths', nargs='+', type=int, default=None,
                    help='Exp 1 trace lengths to build (default: 30 50 100)')
    ap.add_argument('--trials', nargs='+', type=int, default=None,
                    help='trial numbers to build (applies to Exp 1 and Exp 2)')
    ap.add_argument('--skip-exp2', action='store_true',
                    help='skip Exp 2 (30_steps_large) trial building')
    args = ap.parse_args()

    if args.step in ('convert', 'all'):
        step_convert(args.raw_dir, args.converted_dir, args.cpus, args.force, args.limit)
    if args.step in ('trials', 'all'):
        step_trials(args.converted_dir, args.tests_dir, args.shuffles_dir, args.cpus, args.force,
                    lengths=args.lengths, trials=args.trials, skip_exp2=args.skip_exp2)
    print('done')


if __name__ == '__main__':
    main()
