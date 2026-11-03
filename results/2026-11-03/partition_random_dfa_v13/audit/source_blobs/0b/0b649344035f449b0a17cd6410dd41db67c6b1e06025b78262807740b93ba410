"""Seeded complete hidden DFA worlds and bounded, conditioned observations."""
import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import random
import time


def rng_for(seed, purpose):
    digest = hashlib.sha256(f'{seed}:{purpose}'.encode()).digest()
    return random.Random(int.from_bytes(digest, 'big'))


def connected(table, alphabet, n):
    for root in range(n):
        seen, pending = {root}, [root]
        while pending:
            state = pending.pop()
            for ch in alphabet:
                nxt = table[state][ch]
                if nxt not in seen:
                    seen.add(nxt)
                    pending.append(nxt)
        if len(seen) != n:
            return False
    return True


def build_world(seed, k, m):
    rng = rng_for(seed, f'world:{k}:{m}')
    # One Unicode code point per symbol; alphabet size 40 remains ASCII.
    alphabet = [chr(0x100 + i) for i in range(m)]
    if m <= 62:
        alphabet = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'[:m])
    shuffled = list(alphabet)
    rng.shuffle(shuffled)
    groups = [[] for _ in range(k)]
    for i, ch in enumerate(shuffled):
        groups[i % k].append(ch)
    devices, ownership = [], {}
    for device_id, group in enumerate(groups):
        group.sort()
        n = rng.randint(2, 4)
        for attempts in range(1, 10001):
            table = [{ch: rng.randrange(n) for ch in group} for _ in range(n)]
            if connected(table, group, n):
                break
        else:
            raise RuntimeError('strong-connectivity sampling exhausted')
        # Uniform nonempty rejecting subset of states 1..n-1.
        rejecting_mask = rng.randrange(1, 1 << (n - 1))
        accepting = [s for s in range(n) if s == 0 or not (rejecting_mask >> (s - 1) & 1)]
        devices.append({'id': device_id, 'states': list(range(n)), 'start': 0,
                        'accepting': accepting, 'alphabet': group,
                        'transitions': table, 'transition_table_attempts': attempts})
        ownership.update({ch: device_id for ch in group})
    return {'schema_version': 1, 'seed': seed, 'true_devices': k,
            'alphabet': alphabet, 'ownership': ownership, 'devices': devices,
            'world_rng_purpose': f'world:{k}:{m}'}


def replay(word, world):
    states = [d['start'] for d in world['devices']]
    for ch in word:
        i = world['ownership'][ch]
        states[i] = world['devices'][i]['transitions'][states[i]][ch]
    accepted = all(s in d['accepting'] for s, d in zip(states, world['devices']))
    return accepted, states


def shortest(device, start, want_accept):
    queue = deque([(start, '')])
    seen = {start}
    while queue:
        state, path = queue.popleft()
        if (state in device['accepting']) == want_accept:
            return path
        for ch in device['alphabet']:
            nxt = device['transitions'][state][ch]
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, path + ch))
    raise AssertionError('strongly connected DFA lacks target state')


def prefix_limit(length, k, reserve):
    lo, hi = 0, length
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid + min(k, mid) * reserve <= length:
            lo = mid
        else:
            hi = mid - 1
    return lo


def interleave(paths, rng):
    # Select each next device proportional to remaining symbols: uniform
    # over labelled order-preserving interleavings of these fixed paths.
    offsets = [0] * len(paths)
    remaining = sum(map(len, paths))
    out = []
    while remaining:
        ticket = rng.randrange(remaining)
        for i, path in enumerate(paths):
            size = len(path) - offsets[i]
            if ticket < size:
                out.append(path[offsets[i]])
                offsets[i] += 1
                remaining -= 1
                break
            ticket -= size
    return ''.join(out)


def random_word(world, size, rng, profile):
    devices = world['devices']
    total = len(devices) + 3 if profile == 'skewed' else len(devices)
    out = []
    for _ in range(size):
        ticket = rng.randrange(total)
        i = (0 if ticket < 4 else ticket - 3) if profile == 'skewed' else ticket
        out.append(rng.choice(devices[i]['alphabet']))
    return ''.join(out)


def candidate(world, length, mode, rng, desired, repair_rng, length_rng, profile):
    k = world['true_devices']
    reserve = max(len(d['states']) - 1 for d in world['devices'])
    limit = prefix_limit(length, k, reserve)
    b = limit if mode == 'near-max' else length_rng.randrange(limit + 1)
    if b == 0:
        # Short-cap fallback; no assertion that either label is attainable.
        size = length if mode == 'near-max' else length_rng.randrange(length + 1)
        word = random_word(world, size, rng, profile)
        label, states = replay(word, world)
        return word, label, states, {'prefix_length': size, 'repair_length': 0,
                                    'active_devices': len({world['ownership'][c] for c in word}),
                                    'strategy': 'bounded_direct_short_cap'}
    prefix = random_word(world, b, rng, profile)
    _, states = replay(prefix, world)
    active = sorted({world['ownership'][c] for c in prefix})
    reject_device = None if desired else repair_rng.choice(active)
    paths = [shortest(world['devices'][i], states[i], i != reject_device) for i in active]
    suffix = interleave(paths, repair_rng)
    word = prefix + suffix
    label, final = replay(word, world)
    if len(word) > length or label != desired:
        raise AssertionError('repair violated length or target label')
    return word, label, final, {'prefix_length': b, 'repair_length': len(suffix),
                               'active_devices': len(active), 'reject_device': reject_device,
                               'strategy': 'prefix_bfs_repair'}


def generate(world, length, count, seed, mode, retries, profile):
    words = {True: [], False: []}
    seen = set()
    records, attempts = [], {}
    frequency = Counter()
    started = time.perf_counter()
    for desired in (True, False):
        tried = rejected = duplicate = 0
        impossible = not desired and length == 0
        while not impossible and len(words[desired]) < count and tried < retries:
            tried += 1
            purpose = f'candidate:{world["true_devices"]}:{len(world["alphabet"])}:{desired}:{tried}:{profile}'
            word, label, states, detail = candidate(
                world, length, mode, rng_for(seed, purpose + ':prefix'), desired,
                rng_for(seed, purpose + ':repair'), rng_for(seed, purpose + ':length'), profile)
            if label != desired:
                rejected += 1
                continue
            if word in seen:
                duplicate += 1
                continue
            # Replay from complete saved transitions is the label authority.
            verified, final = replay(word, world)
            if verified != desired or final != states:
                raise AssertionError('label replay mismatch')
            seen.add(word)
            index = len(words[desired])
            words[desired].append(word)
            frequency.update(word)
            records.append({'label': 'positive' if desired else 'negative', 'index': index,
                            'candidate_index': tried, 'rng_purpose': purpose,
                            'length': len(word), 'final_states': final,
                            'run_count': sum(i == 0 or ch != word[i - 1] for i, ch in enumerate(word)),
                            **detail})
        attempts['positive' if desired else 'negative'] = {
            'attempts': tried, 'wrong_label_attempts': rejected, 'duplicate_attempts': duplicate,
            'requested': count, 'generated': len(words[desired]),
            'shortfall': count - len(words[desired])}
    return {'alphabet': world['alphabet'], 'positive': words[True], 'negative': words[False]}, {
        'max_length': length, 'length_mode': mode, 'samples_per_label': count,
        'event_profile': profile,
        'device_probabilities': ([4 / (world['true_devices'] + 3)] +
                                 [1 / (world['true_devices'] + 3)] * (world['true_devices'] - 1)
                                 if profile == 'skewed' else [1 / world['true_devices']] * world['true_devices']),
        'max_attempts_per_label': retries, 'attempts': attempts, 'samples': records,
        'event_frequencies': dict(sorted(frequency.items())), 'observed_alphabet': sorted(frequency),
        'generation_seconds': time.perf_counter() - started,
        'complete': all(len(words[x]) == count for x in (True, False)),
        'impossibility': 'negative label impossible at max_length=0 (all starts accept)' if length == 0 and count else None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--devices', type=int)
    choice.add_argument('--allowed-devices', type=int, nargs='+')
    parser.add_argument('--alphabet-size', type=int)
    parser.add_argument('--max-length', type=int, required=True)
    parser.add_argument('--samples-per-label', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--length-mode', choices=['near-max', 'uniform'], default='near-max')
    parser.add_argument('--event-profile', choices=['uniform', 'skewed'], default='uniform')
    parser.add_argument('--max-attempts-per-label', type=int)
    args = parser.parse_args(argv)
    allowed = sorted(set(args.allowed_devices or [args.devices]))
    if any(k < 1 for k in allowed) or args.max_length < 0 or args.samples_per_label < 0:
        parser.error('devices must be positive; length and sample count nonnegative')
    k = rng_for(args.seed, 'device-count').choice(allowed)
    m = args.alphabet_size if args.alphabet_size is not None else 2 * k
    if m < 2 * k or m > 10000:
        parser.error('alphabet-size must be between 2*selected_devices and 10000')
    retries = args.max_attempts_per_label if args.max_attempts_per_label is not None else max(100, args.samples_per_label * 100)
    if retries < 1:
        parser.error('max-attempts-per-label must be positive')
    args.out.mkdir(parents=True, exist_ok=True)
    if any((args.out / name).exists() for name in ('world.json', 'solver_input.json')):
        parser.error('output files already exist; choose a fresh output directory')
    world = build_world(args.seed, k, m)
    data, stats = generate(world, args.max_length, args.samples_per_label, args.seed, args.length_mode, retries, args.event_profile)
    world['allowed_device_counts_for_world_selection'] = allowed
    world['generation'] = stats
    world['distribution'] = 'random complete tables conditioned on strong connectivity; accepting start, uniform nonempty rejecting subset; observations conditioned by prefix/BFS repair and uniqueness'
    for name, payload in (('world.json', world), ('solver_input.json', data)):
        (args.out / name).write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2), encoding='utf-8')
    print(json.dumps({'complete': stats['complete'], 'out': str(args.out), 'attempts': stats['attempts']}))
    return 0 if stats['complete'] else 3


if __name__ == '__main__':
    raise SystemExit(main())
