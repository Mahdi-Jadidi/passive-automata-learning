#!/usr/bin/env python3
"""Reproduce Table 3 of the paper: traces to 100% accuracy, chaos vs heuristic, 4 trace lengths, 3 trials."""
import argparse
import json
import os
import shutil
import statistics
import sys
import tempfile
from multiprocessing import Pool

ARTIFACT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ARTIFACT_ROOT)

from sim_learn.learn_automata import SimulatorLearner
from evaluation.evaluator import DFAEvaluator
from aalpy.utils import save_automaton_to_file


AGENTS = ['random', 'heuristic']
LENGTHS = [15, 50, 100, 200]
TRIALS = [1, 2, 3]


def find_convergence(training_dir, eval_dir, step, max_traces, scratch_dir, label):
    for n in range(step, max_traces + 1, step):
        files = [os.path.join(training_dir, f'output_{i}.txt') for i in range(1, n + 1)]
        if any(not os.path.exists(f) for f in files):
            print(f'[{label}] n={n}: ran out of training traces, aborting', flush=True)
            return None

        learner = SimulatorLearner()
        learner.learn_logs(files)
        dfa = learner.get_dfa_sim()

        dot_path = os.path.join(scratch_dir, f'{label}_n{n}.dot')
        save_automaton_to_file(dfa, path=dot_path)
        ev = DFAEvaluator(dot_path)

        accs = []
        i = 0
        while True:
            i += 1
            p = os.path.join(eval_dir, f'trace{i}.txt')
            if not os.path.exists(p):
                break
            try:
                accs.append(ev.evaluate_trace(p, debug=False)['accuracy'])
            except Exception:
                continue

        acc = sum(accs) / len(accs) if accs else 0.0
        print(f'[{label}] n={n:5d}  acc={acc:.4f}  states={len(dfa.states)}', flush=True)

        if acc >= 1.0 - 1e-9:
            return n
    return None


def run_one(args):
    agent, length, trial, data_dir, eval_dir, step, max_traces, out_dir = args
    label = f'{agent}_{length}steps_trial{trial}'
    training_dir = os.path.join(data_dir, f'trial_{trial}', f'{agent}_{length}steps', 'training_traces')
    scratch = tempfile.mkdtemp(prefix=f'table3_{label}_')
    try:
        n = find_convergence(training_dir, eval_dir, step, max_traces, scratch, label)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    result = {'agent': agent, 'length': length, 'trial': trial, 'convergence_n': n}
    with open(os.path.join(out_dir, f'{label}.json'), 'w') as f:
        json.dump(result, f, indent=2)
    return result


def aggregate(results):
    table = {}
    for agent in AGENTS:
        for length in LENGTHS:
            ns = [r['convergence_n'] for r in results
                  if r['agent'] == agent and r['length'] == length and r['convergence_n'] is not None]
            if not ns:
                table[(agent, length)] = None
                continue
            m = statistics.mean(ns)
            s = statistics.stdev(ns) if len(ns) > 1 else 0.0
            table[(agent, length)] = {'mean': m, 'std': s, 'values': ns}
    return table


def print_table(table):
    print()
    print('=' * 58)
    print('Table 3: Number of traces required for 100% accuracy')
    print('=' * 58)
    print(f'{"Agent":<18} {"Trace Length":<14} {"Mean":>8} {"Std Dev":>10}')
    print('-' * 58)
    agent_display = {'random': 'Chaos (Random)', 'heuristic': 'Heuristic'}
    for agent in AGENTS:
        for length in LENGTHS:
            entry = table.get((agent, length))
            if entry is None:
                print(f'{agent_display[agent]:<18} {f"{length}-step":<14} {"-":>8} {"-":>10}')
            else:
                print(f'{agent_display[agent]:<18} {f"{length}-step":<14} {entry["mean"]:>8.1f} {entry["std"]:>10.1f}')
    print('=' * 58)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data-dir', default=os.path.join(ARTIFACT_ROOT, 'data', 'one_host_network_validity_only'))
    ap.add_argument('--eval-subdir', default='eval_50steps',
                    help='subdir of {data-dir}/eval_traces to use as held-out set (default: eval_50steps, matching paper §A.2)')
    ap.add_argument('--output-dir', default=os.path.join(ARTIFACT_ROOT, 'results', 'table3'))
    ap.add_argument('--step', type=int, default=10, help='training-trace increment between checkpoints')
    ap.add_argument('--max-traces', type=int, default=5000, help='safety cap on checkpoints')
    ap.add_argument('--cpus', type=int, default=1, help='run configs in parallel on N workers')
    ap.add_argument('--agents', nargs='+', default=AGENTS, choices=AGENTS)
    ap.add_argument('--lengths', nargs='+', type=int, default=LENGTHS, choices=LENGTHS)
    ap.add_argument('--trials', nargs='+', type=int, default=TRIALS, choices=TRIALS)
    args = ap.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    eval_dir = os.path.join(args.data_dir, 'eval_traces', args.eval_subdir)
    if not os.path.isdir(eval_dir):
        sys.exit(f'eval dir not found: {eval_dir}')

    jobs = [(agent, length, trial, args.data_dir, eval_dir, args.step, args.max_traces, args.output_dir)
            for agent in args.agents for length in args.lengths for trial in args.trials]
    print(f'Running {len(jobs)} configurations with {args.cpus} worker(s)...', flush=True)

    if args.cpus > 1:
        with Pool(args.cpus) as pool:
            results = list(pool.imap_unordered(run_one, jobs))
    else:
        results = [run_one(j) for j in jobs]

    table = aggregate(results)
    print_table(table)

    summary = {
        'config': {'eval_subdir': args.eval_subdir, 'step': args.step, 'max_traces': args.max_traces},
        'per_run': sorted(results, key=lambda r: (r['agent'], r['length'], r['trial'])),
        'table': {f'{a}_{l}steps': v for (a, l), v in table.items()},
    }
    out_path = os.path.join(args.output_dir, 'table3_summary.json')
    with open(out_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f'\nWrote {out_path}')


if __name__ == '__main__':
    main()
