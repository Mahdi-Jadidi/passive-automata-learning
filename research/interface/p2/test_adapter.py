import copy
import json
import unittest
from pathlib import Path
from adapter import Ledger, canonical, digest, encode_sample, id_map, request, validate

RAW = {'alphabet': ['β', 'a', '未'], 'positive': [['β', 'a'], []], 'negative': [['a', 'β'], ['a', 'β'], ['a', 'β', 'β']]}
Q = request(RAW, [0, 1, 2], 'q', 'a1')

def table(block, zeros, free):
    return {'block': block, 'kind': 'UNRESTRICTED_BASE', 'complete': True, 'zeros': [{'negative': i, 'positive': j} for i, j in zeros], 'free': free}


def envelope(q, status, **extra):
    return {'version': 'selector-v2/1', 'request': copy.deepcopy(q), 'origin': 'SIMULATOR', 'status': status, 'complete': True, 'receipt': 'fixture', **extra}


NO = envelope(Q, 'PROJECTION_NO', failed=0, tables=[table(0, [(0, 0), (1, None)], [[2]]), table(1, [(0, 0), (1, None), (2, None)], []), table(2, [(0, 1), (1, None), (2, None)], [])])
AQ = request(RAW, [0, 0, 2], 'q2', 'a2')
# DFA recognizes epsilon and βa; all other strings go to sink.
D = {'block': 0, 'states': 4, 'initial': 0, 'accepting': [0, 2], 'transitions': [[0, 0, 1], [0, 1, 3], [1, 0, 3], [1, 1, 2], [2, 0, 3], [2, 1, 3], [3, 0, 3], [3, 1, 3]]}
U = {'block': 2, 'states': 1, 'initial': 0, 'accepting': [0], 'transitions': [[0, 2, 0]]}
YES = envelope(AQ, 'ACCEPT', dfas=[D, U])


class Audit(unittest.TestCase):
    def reject(self, payload=NO, q=Q, raw=RAW, capacities=None):
        l = Ledger(raw)
        self.assertEqual(l.ingest(q, payload, capacities), 'UNKNOWN')
        self.assertEqual(l.records, ())
        self.assertEqual(len(l.quarantine), 1)

    def test_golden(self):
        vectors = json.loads(Path(__file__).with_name('golden.json').read_text())
        for v in vectors:
            with self.subTest(v=v['name']):
                s = encode_sample(v['raw'])
                self.assertEqual(canonical(s).decode(), v['canonical'])
                self.assertEqual(digest(s), v['sha256'])
        self.assertNotEqual(vectors[0]['sha256'], vectors[1]['sha256'])
        core = {'alphabet':['β','a','😀'],'positive':[['β','β'],[],['β','β']],'negative':[['a','😀']]}
        self.assertEqual(digest(encode_sample(core)), '7ddb11d457a25ee2b1d273529cf3f3e2064054dc154ebc901acb796b08708bbb')
        self.assertEqual(digest(request(core,[0,1,1],'r1','a1')), '1f43bbcd2081c20e84469b2220928c7a5f61674ce9a7d4bfec84e7e55285ee72')

    def test_request_mutations(self):
        for name, mutate in [
            ('family', lambda q: q['scope'].update(family='RESTRICTED')),
            ('digest', lambda q: q['scope'].update(sample_digest='0'*64)),
            ('regime', lambda q: q['scope'].update(regime='BOUNDED')),
            ('capacity', lambda q: q['scope'].update(capacity_digest='x')),
            ('order', lambda q: q['negative_ids'].reverse()),
            ('bool ID', lambda q: q['negative_ids'].__setitem__(0, False)),
            ('owner', lambda q: q.update(owner=[0, 1])),
            ('schema', lambda q: q.update(version='v9')),
        ]:
            with self.subTest(name=name):
                q = copy.deepcopy(Q); mutate(q)
                p = copy.deepcopy(NO); p['request'] = copy.deepcopy(q)
                self.reject(p, q)
        raw = copy.deepcopy(RAW); raw['positive'][0].reverse()
        self.reject(raw=raw)

    def test_symbol_policy(self):
        for a in ['', 0, False, None]:
            with self.subTest(a=a), self.assertRaises(ValueError):
                encode_sample({'alphabet': [a], 'positive': [], 'negative': []})
        raw = {'alphabet': [], 'positive': [[]], 'negative': []}
        self.assertEqual(encode_sample(raw), ['sample-v2', [], [[]], []])
        with self.assertRaises(ValueError): request(raw, [], 'r', 'a')

    def test_id_mapping(self):
        self.assertEqual(id_map([['n9', 0], ['n2', 1], ['n5', 2]], 3), {'n9': 0, 'n2': 1, 'n5': 2})
        for pairs in [[['n', 0], ['n', 1]], [['a', 1], ['b', 0]], [['a', False], ['b', 1]], [['a', 0]]]:
            with self.subTest(pairs=pairs), self.assertRaises(ValueError): id_map(pairs, 2)

    def test_atomic_and_immutable(self):
        l = Ledger(RAW); p = copy.deepcopy(NO)
        p['tables'][-1]['zeros'].pop()
        self.assertEqual(l.ingest(Q, p), 'UNKNOWN'); self.assertEqual(l.records, ())
        p = copy.deepcopy(NO)
        self.assertEqual(l.ingest(Q, p), 'PROJECTION_NO')
        before = l.records; p['tables'][0]['zeros'].clear()
        self.assertEqual(l.records, before)
        self.assertEqual(l.ingest(Q, NO), 'UNKNOWN'); self.assertEqual(l.records, before)
        self.assertFalse(json.loads(before[0])['operational'])

    def test_projection_corruption(self):
        for name, mutate in [
            ('unknown', lambda p: p.update(status='NO')),
            ('incomplete', lambda p: p.update(complete=False)),
            ('attempt', lambda p: p['request'].update(attempt_id='old')),
            ('request', lambda p: p['request'].update(request_id='other')),
            ('table', lambda p: p['tables'].pop()),
            ('conditioned', lambda p: p['tables'][0].update(kind='CONDITIONED')),
            ('anonymous failed', lambda p: p['tables'][0]['zeros'][0].update(positive=None)),
            ('wrong witness', lambda p: p['tables'][0]['zeros'][0].update(positive=1)),
            ('duplicate', lambda p: p['tables'][0]['free'][0].append(2)),
            ('false zero', lambda p: p['tables'][0]['zeros'].append({'negative': 2, 'positive': None})),
            ('bool ID', lambda p: p.update(failed=False)),
            ('extra field', lambda p: p.update(debug=True)),
            ('tuple', lambda p: p.update(tables=tuple(p['tables']))),
        ]:
            with self.subTest(name=name):
                p = copy.deepcopy(NO); mutate(p); self.reject(p)
        self.reject(None)

    def test_accept_and_auth(self):
        l = Ledger(RAW); self.assertEqual(l.ingest(AQ, YES), 'ACCEPT')
        self.assertFalse(json.loads(l.records[0])['operational'])
        p = copy.deepcopy(YES); p['origin'] = 'EXTERNAL'; self.reject(p, AQ)
        seen = []
        def auth(q, p):
            seen.append((q, p)); return True
        r = validate(RAW, AQ, p, authenticate=auth)
        self.assertEqual(seen, [(canonical(AQ), canonical(p))]); self.assertFalse(r['operational'])
        for name, mutate in [('missing', lambda p: p['dfas'].pop()), ('transition', lambda p: p['dfas'][0]['transitions'].pop()), ('positive', lambda p: p['dfas'][0].update(accepting=[2])), ('negative', lambda p: p['dfas'][0]['accepting'].append(3)), ('bool', lambda p: p['dfas'][0].update(initial=False)), ('row', lambda p: p.update(joint_row=[[1, 0, 1], [0, 0, 0]]))]:
            with self.subTest(name=name):
                p = copy.deepcopy(YES); mutate(p); self.reject(p, AQ)

    def test_bounded(self):
        q = request(RAW, [0, 0, 2], 'b', 'a3', [1, 1])
        p = envelope(q, 'BOUNDED_NO', exact=True)
        r = validate(RAW, q, p, [1, 1]); self.assertEqual(r['scope'], 'NONE')
        self.reject(p, q, capacities=[2, 1]); self.reject(envelope(AQ, 'BOUNDED_NO', exact=True), AQ)
        self.reject(envelope(q, 'ACCEPT', dfas=[D, U]), q, capacities=[1, 1])
        q = request(RAW, [0, 0, 2], 'b', 'a4', [4, 1])
        p = envelope(q, 'ACCEPT', dfas=[D, U], joint_row=[[1, 1, 1], [0, 0, 0]])
        self.assertEqual(validate(RAW, q, p, [4, 1])['status'], 'ACCEPT')

if __name__ == '__main__': unittest.main(verbosity=2)
