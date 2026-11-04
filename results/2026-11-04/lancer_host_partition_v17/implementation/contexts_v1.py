"""Direct input-only local-context consistency; no host map or merge closure."""
import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import time

DEPTHS = (0, 1, 2, 4, 8, 'full')


def validate(observations):
    if not isinstance(observations, dict) or set(observations) != {'alphabet', 'traces'}:
        raise ValueError('observations must contain only alphabet and traces')
    alphabet = observations['alphabet']
    if not isinstance(alphabet, list) or any(not isinstance(x, str) for x in alphabet) or len(set(alphabet)) != len(alphabet):
        raise ValueError('alphabet must contain unique opaque string IDs')
    allowed = set(alphabet)
    files = set()
    for trace in observations['traces']:
        if set(trace) != {'file_id', 'events'} or type(trace['file_id']) is not int or trace['file_id'] in files:
            raise ValueError('invalid/duplicate file boundary')
        files.add(trace['file_id'])
        for event in trace['events']:
            if set(event) != {'id', 'outcome'} or event['id'] not in allowed or (event['outcome'] is not None and type(event['outcome']) is not bool):
                raise ValueError('invalid event or forbidden metadata')
    return allowed


def evaluate_block(observations, block_ids, depth, file_ids=None, deadline=None, max_examples=20):
    started = time.perf_counter()
    allowed = validate(observations)
    block = set(block_ids)
    if not block or not block <= allowed or depth not in DEPTHS or type(depth) is bool:
        raise ValueError('nonempty declared block and depth0/1/2/4/8/full required')
    chosen = None if file_ids is None else set(file_ids)
    records, conflicted, examples = {}, set(), []
    transitions = {}
    total = known = unknown = 0
    complete = True
    try:
        for trace in observations['traces']:
            if chosen is not None and trace['file_id'] not in chosen:
                continue
            history = deque(maxlen=depth if depth != 'full' else 0)
            prefix = 0
            local_index = 0
            for ei, event in enumerate(trace['events']):
                if deadline is not None and time.perf_counter() >= deadline:
                    raise TimeoutError
                if event['id'] not in block:
                    continue
                current = event['id']
                total += 1
                if depth == 'full':
                    transition = (prefix, current)
                    if transition not in transitions:
                        transitions[transition] = len(transitions) + 1
                    context = transitions[transition]
                    prefix = context
                else:
                    context = (tuple(history), current)
                reference = {'file_id': trace['file_id'], 'event_index': ei,
                             'local_index': local_index, 'event_id': current}
                label = event['outcome']
                if label is None:
                    unknown += 1
                else:
                    known += 1
                    if context not in records:
                        records[context] = (label, reference)
                    elif records[context][0] != label and context not in conflicted:
                        conflicted.add(context)
                        if len(examples) < max_examples:
                            examples.append({'first': records[context][1], 'first_outcome': records[context][0],
                                             'opposite': reference, 'opposite_outcome': label})
                if depth != 'full':
                    history.append(current)
                local_index += 1
    except TimeoutError:
        complete = False
    return {'complete': complete, 'consistent': not conflicted if complete else None,
            'depth': depth, 'block': sorted(block), 'file_ids': sorted(chosen) if chosen is not None else None,
            'events_in_block': total, 'labelled_events': known, 'unlabelled_events': unknown,
            'labelled_contexts': len(records), 'conflicting_contexts': len(conflicted),
            'conflict_examples': examples, 'full_prefix_trie_nodes': len(transitions),
            'seconds': time.perf_counter() - started,
            'semantics': 'previous d projected input IDs excluding current, then current; full means whole local prefix; outcomes never history inputs',
            'scope': 'finite-sample context agreement only; no physical independence/recovery or unseen-behavior guarantee'}


def check_partition(observations, blocks, depth, file_ids=None, deadline=None):
    allowed = validate(observations)
    flattened = [x for block in blocks for x in block]
    if not blocks or any(not b for b in blocks) or len(flattened) != len(set(flattened)) or set(flattened) != allowed:
        raise ValueError('partition must be nonempty disjoint blocks covering declared alphabet')
    profiles = [evaluate_block(observations, block, depth, file_ids, deadline) for block in blocks]
    complete = all(p['complete'] for p in profiles)
    return {'complete': complete, 'feasible': all(p['consistent'] for p in profiles) if complete else None,
            'profiles': profiles, 'pruning_or_merge_closure_assumed': False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('observations', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--block', nargs='+')
    group.add_argument('--top', type=int, help='select S by TRAIN-only event frequency, tie opaqueID')
    ap.add_argument('--split', choices=('train', 'validation', 'test', 'all'), default='train')
    ap.add_argument('--depths', nargs='+', choices=('0', '1', '2', '4', '8', 'full'), default=['0', '1', '2', '4', '8', 'full'])
    ap.add_argument('--seconds', type=float, default=60)
    args = ap.parse_args()
    started = time.perf_counter()
    if args.seconds <= 0 or not __import__('math').isfinite(args.seconds):
        ap.error('seconds must be finite and positive')
    raw = args.observations.read_bytes()
    data = json.loads(raw)
    validate(data)
    frequencies = Counter(e['id'] for t in data['traces'] if 1 <= t['file_id'] <= 60 for e in t['events'])
    if args.top is not None:
        if args.top < 1:
            ap.error('top must be positive')
        block = sorted(frequencies, key=lambda x: (-frequencies[x], x))[:args.top]
    else:
        block = args.block or data['alphabet']
    files = [t['file_id'] for t in data['traces'] if args.split == 'all' or
             (args.split == 'train' and 1 <= t['file_id'] <= 60) or
             (args.split == 'validation' and 61 <= t['file_id'] <= 80) or
             (args.split == 'test' and 81 <= t['file_id'] <= 100)]
    deadline = started + args.seconds
    profiles = [evaluate_block(data, block, 'full' if d == 'full' else int(d), files, deadline) for d in args.depths]
    args.out.mkdir(parents=True, exist_ok=False)
    result = {'input_sha256': hashlib.sha256(raw).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'split': args.split, 'selection': 'train_frequency' if args.top is not None else 'explicit_block_or_all',
              'training_frequencies': dict(frequencies), 'profiles': profiles,
              'warning': 'omitting other causal actions changes local history; no monotone coarsening/merge rule is assumed',
              'protected_truth_read': False}
    (args.out / 'profiles.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({'complete': all(p['complete'] for p in profiles), 'profiles': len(profiles)}))
    return 0 if all(p['complete'] for p in profiles) else 3


if __name__ == '__main__':
    raise SystemExit(main())
