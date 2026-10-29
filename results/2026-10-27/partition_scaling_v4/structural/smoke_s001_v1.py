"""Deterministic correctness smoke, not an official performance experiment."""
import itertools
import json
import random
import time
from singleton_solver_v1 import solve


def partitions(alphabet, k):
    def visit(labels, highest):
        if len(labels) == len(alphabet):
            if highest + 1 == k:
                yield [[a for a, c in zip(alphabet, labels) if c == i] for i in range(k)]
            return
        for c in range(min(highest + 1, k - 1) + 1):
            yield from visit(labels + [c], max(highest, c))
    yield from visit([0], 0)


def oracle(data, k):
    out = []
    for blocks in partitions(data['alphabet'], k):
        words = [[ ''.join(a for a in w if a in block) for block in blocks]
                 for w in data['positive']]
        if any(x != words[0] for x in words):
            continue
        if any([''.join(a for a in w if a in block) for block in blocks] == words[0]
               for w in data['negative']):
            continue
        out.append(blocks)
    return out


def main():
    rng = random.Random(44001)
    records = []
    path = {'alphabet': list('abcd'), 'positive': ['abcd','bacd','acbd','abdc'], 'negative': []}
    cases = [('connected_k3_counterexample', path, 3)]
    for m in range(2, 8):
        alphabet = list('abcdefg'[:m])
        for k in range(1, m+1):
            for sample in range(3):
                positive = [''.join(alphabet)]
                for _ in range(sample+1):
                    shuffled = list(alphabet)
                    rng.shuffle(shuffled)
                    positive.append(''.join(shuffled))
                cases.append((f'random_{m}_{k}_{sample}',
                              {'alphabet': alphabet, 'positive': positive, 'negative': ['']}, k))
            blocks = [alphabet[i::k] for i in range(k)]
            words = [''.join(b) for b in blocks]
            for suffix, negative in [('good', ['']), ('bad', [''.join(words)])]:
                if suffix == 'bad':
                    # Use a third shuffle accepted by the blocks, not a duplicate positive label.
                    negative = [''.join(''.join(x) for x in itertools.zip_longest(*words, fillvalue=''))]
                    if negative[0] in [''.join(words), ''.join(reversed(words))]:
                        continue
                cases.append((f'certificate_{m}_{k}_{suffix}', {'alphabet': alphabet,
                    'positive': [''.join(words), ''.join(reversed(words))], 'negative': negative}, k))
    cases.extend([('epsilon', {'alphabet': list('ab'), 'positive': [''], 'negative': ['a']}, 2),
                  ('counts', {'alphabet': list('ab'), 'positive': ['a','aa'], 'negative': []}, 2)])
    failures = []
    for name, data, k in cases:
        truth = oracle(data, k)
        result = solve(data, k=k, max_solutions=None)
        record = {'name': name, 'data': data, 'k': k, 'oracle': truth, 'result': result}
        print(json.dumps(record, ensure_ascii=False), flush=True)  # raw before assertion
        records.append(record)
        returned = [x['blocks'] for x in result['solutions']]
        if result['status'] == 'found' and (returned != truth or len(truth) != 1):
            failures.append(name)
        if result['status'] == 'infeasible' and truth:
            failures.append(name)
    empty = solve({'alphabet': list('ab'), 'positive': [], 'negative': ['']}, k=2)
    expired = solve(path, k=3, deadline=time.perf_counter()-1)
    print(json.dumps({'empty': empty, 'expired': expired, 'failures': failures,
                      'case_count': len(records)}, ensure_ascii=False), flush=True)
    assert len(oracle(path, 3)) == 3
    assert not failures
    assert empty['status'] == 'insufficient_coverage'
    assert expired['status'] == 'incomplete' and not expired['search_exhausted']


if __name__ == '__main__':
    main()
