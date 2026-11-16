"""Controlled developer checks; this is not the independent audit."""
import itertools
import json
from pathlib import Path
import random
import time
from recommend_v1 import solve


def partitions(alphabet):
    def visit(i, blocks):
        if i == len(alphabet):
            yield [b[:] for b in blocks]
            return
        for b in blocks:
            b.append(alphabet[i])
            yield from visit(i + 1, blocks)
            b.pop()
        blocks.append([alphabet[i]])
        yield from visit(i + 1, blocks)
        blocks.pop()
    return visit(0, [])


def feasible(data, blocks):
    def projection(w, block):
        return ''.join(c for c in w if c in block)
    return all(any(projection(n, b) not in {projection(p, b) for p in data['positive']}
                   for b in blocks) for n in data['negative'])


def rgs(alphabet, blocks):
    return tuple(next(i for i, b in enumerate(blocks) if a in b) for a in alphabet)


def run():
    fixtures = [
        {'alphabet': list('a'), 'positive': ['a'], 'negative': ['']},
        {'alphabet': list('ab'), 'positive': ['ab'], 'negative': ['ba']},
        {'alphabet': list('abcd'), 'positive': ['', 'aabb', 'ccdd'], 'negative': ['bbaa', 'ddcc']},
        {'alphabet': list('abc'), 'positive': [], 'negative': ['abc', '']},
        {'alphabet': list('abc'), 'positive': ['abc'], 'negative': []},
    ]
    rng = random.Random(2601)
    words = [''] + [''.join(w) for k in (1, 2, 3) for w in itertools.product('abcd', repeat=k)]
    for _ in range(24):
        chosen = rng.sample(words, 12)
        fixtures.append({'alphabet': list('abcd'), 'positive': chosen[:6], 'negative': chosen[6:]})
    records = []
    for data in fixtures:
        valid = [p for p in partitions(sorted(data['alphabet'])) if feasible(data, p)]
        maximum = max(map(len, valid))
        optimal = sorted([p for p in valid if len(p) == maximum], key=lambda p: rgs(sorted(data['alphabet']), p))
        out = solve(data)
        rec = out['recommendation']
        assert out['status'] == ('ambiguous' if len(valid) > 1 else 'certified_unique')
        assert rec['optimality_proved'] and rec['block_count'] == maximum
        assert rec['partition'] == optimal[0]
        assert rec['tie_status'] == ('multiple' if len(optimal) > 1 else 'unique')
        assert [w['blocks'] for w in rec['optimal_witnesses']] == optimal[:2]
        for w in rec['optimal_witnesses']:
            assert feasible(data, w['blocks'])
            assert len(w['negative_rejections']) == len(data['negative'])
        records.append({'input': data, 'status': out['status'], 'maximum': maximum,
                        'tie_status': rec['tie_status']})
    assert solve(fixtures[0], deadline=time.perf_counter() - 1)['status'] == 'unresolved'
    assert solve({'alphabet': ['a'], 'positive': ['a'], 'negative': ['a']})['status'] == 'incompatible'
    assert solve({'alphabet': ['a'], 'positive': ['a'], 'negative': ['a', 'b']})['status'] == 'invalid_input'
    for bad in (0, -1, True, 1.5):
        assert solve(fixtures[0], memo_limit=bad)['status'] == 'invalid_input'
    quota_data = fixtures[2]
    quota = solve(quota_data, memo_limit=1)
    assert quota['findings']['computation_incomplete']
    assert quota['recommendation']['lower_bound'] == 1
    assert not quota['recommendation']['optimality_proved']
    records.append({'control': 'quota', 'output': quota})
    Path(__file__).with_name('developer_smoke_results_v1.json').write_text(
        json.dumps({'developer_only': True, 'passed': True, 'records': records}, indent=2), encoding='utf-8')
    print('developer smoke passed: 29 oracle fixtures and validation/deadline/quota controls')


if __name__ == '__main__':
    run()
