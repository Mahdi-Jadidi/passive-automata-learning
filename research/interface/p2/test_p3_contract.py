"""P3 selector-side boundary regressions; no search engine or transport."""
import copy
import itertools
import json
from pathlib import Path
import unittest

from adapter import canonical
from gateway import open_gateway
from selector_v2.core import Sample, PartitionRef
from selector_v2.registered_ledger import RegisteredLedger
from selector_v2.schema import identity


RAW = {'alphabet': ['b', 'a', 'unused'],
       'positive': [['b', 'a'], [], ['b', 'a']],
       'negative': [['a', 'b'], ['a', 'b'], ['a', 'b', 'b']]}
SINGLE = [0, 1, 2]
MERGED = [0, 0, 2]
PMAP = [['same', 0], ['empty', 1], ['p-copy', 2]]
NMAP = [['same', 0], ['n-copy', 1], ['long', 2]]


def table(root, zeros, free):
    return dict(block=root, kind='UNRESTRICTED_BASE', complete=True,
                zeros=[dict(negative=i, positive=j) for i, j in zeros], free=free)


def reply(q, status, **extra):
    return dict(version='selector-v2/1', request=copy.deepcopy(q),
                origin='SIMULATOR', status=status, complete=True,
                receipt='fixture-only', **extra)


def projection_no(q):
    return reply(q, 'PROJECTION_NO', failed=1, tables=[
        table(0, [(0, None), (1, 2)], [[2]]),
        table(1, [(0, None), (1, 0), (2, None)], []),
        table(2, [(0, None), (1, 1), (2, None)], [])])


def accept(q):
    d = dict(block=0, states=4, initial=0, accepting=[0, 2],
             transitions=[[0, 0, 1], [0, 1, 3], [1, 0, 3], [1, 1, 2],
                          [2, 0, 3], [2, 1, 3], [3, 0, 3], [3, 1, 3]])
    u = dict(block=2, states=1, initial=0, accepting=[0], transitions=[[0, 2, 0]])
    return reply(q, 'ACCEPT', dfas=[d, u], joint_row=[[1, 1, 1], [0, 0, 0]])


def events(g):
    journal = json.loads(g.export())
    if journal['version'] != 'selector-v2-journal/2':
        raise ValueError('wrong journal version')
    return journal['events']


def register(g, owner=SINGLE, rid='r', aid='a', **kw):
    return g.register(owner, rid, aid, **kw)


class SearchBoundary(unittest.TestCase):
    def assert_observation(self, g, q, expected, raw):
        self.assertEqual(g.ingest(q['request_id'], q['attempt_id'], raw), expected)
        self.assertEqual(g.attempt_status(q['request_id'], q['attempt_id']), expected)
        e = events(g)[-1]
        p = e['records'][0]['payload']
        self.assertEqual(p['request_digest'], identity(q))
        self.assertEqual(p['status'], expected)
        self.assertIn(q['request_id'], g.pending_candidates)
        if expected == 'UNKNOWN':
            self.assertEqual(e['event'], 'QUARANTINE')
            self.assertIsNone(p['feedback'])
            self.assertIsNone(p['receipt_digest'])
        else:
            self.assertEqual(e['event'], 'OBSERVE')
            normalized = json.loads(bytes.fromhex(e['normalized_hex']))
            self.assertIs(normalized['operational'], False)
            self.assertEqual(normalized['scope'], 'NONE')
        if expected != 'PROJECTION_NO':
            self.assertIsNone(p['feedback'])
        return p

    def test_complete_minimum_owner_domain(self):
        # Independent literal oracle for the five partitions of three symbols.
        legal = {(0, 0, 0), (0, 0, 2), (0, 1, 0), (0, 1, 1), (0, 1, 2)}
        g = open_gateway(RAW)
        self.assertIs(type(g), RegisteredLedger)
        for i, owner in enumerate(itertools.product(range(3), repeat=3)):
            with self.subTest(owner=owner):
                before = g.export()
                if owner in legal:
                    q = register(g, list(owner), str(i), str(i))
                    self.assertEqual(q['owner'], list(owner))
                    part = PartitionRef(owner)
                    part.validate_sample(Sample.from_input(RAW))
                    self.assertEqual(part.cost, 3 - len(set(owner)))
                else:
                    with self.assertRaises(ValueError):
                        register(g, list(owner), str(i), str(i))
                    self.assertEqual(g.export(), before)
        self.assertEqual(len(g.records), len(legal))
        for owner in ([], [0, 0], [0, 1, 2, 3], [False, 1, 2],
                      [0, 1.0, 2], [0, 1, -1], {'b': 0, 'a': 1}):
            with self.subTest(owner=owner):
                before = g.export()
                with self.assertRaises(ValueError):
                    register(g, owner, 'bad', 'bad')
                self.assertEqual(g.export(), before)

    def test_empty_alphabet_is_local_only(self):
        raw = dict(alphabet=[], positive=[[]], negative=[])
        sample = Sample.from_input(raw)
        PartitionRef(()).validate_sample(sample)
        g = open_gateway(raw)
        before = g.export()
        with self.assertRaises(ValueError):
            register(g, [])
        self.assertEqual(g.export(), before)

    def test_partition_and_scope_identity(self):
        g = open_gateway(RAW)
        q = register(g, MERGED)
        retry = register(g, MERGED, aid='b')
        same = register(g, MERGED, rid='other', aid='c')
        diff = register(g, SINGLE, rid='diff', aid='d')
        bounded = register(g, MERGED, rid='bounded', aid='e', capacities=[4, 1])
        def key(r):
            return (r['scope']['sample_digest'], tuple(r['owner']))
        self.assertEqual(key(q), key(retry))
        self.assertEqual(key(q), key(same))
        self.assertEqual(key(q), key(bounded))
        self.assertNotEqual(key(q), key(diff))
        self.assertNotEqual(identity(q), identity(retry))
        self.assertNotEqual(identity(q), identity(same))
        self.assertEqual(q['scope'], dict(version='selector-v2/1',
            sample_digest=Sample.from_input(RAW).sample_digest, regime='UNRESTRICTED',
            family='ALL_PARTITIONS', capacity_digest=None))
        self.assertEqual(bounded['scope']['regime'], 'BOUNDED')
        self.assertEqual(bounded['scope']['capacity_digest'],
                         identity(['capacity-v2', [[0, 4], [2, 1]]]))
        before = g.export()
        for owner, caps in ((SINGLE, None), (MERGED, [4, 1])):
            with self.assertRaises(ValueError):
                register(g, owner, aid='rebound', capacities=caps)
            self.assertEqual(g.export(), before)
        q['owner'][1] = 1
        self.assertEqual(events(g)[0]['registered']['request']['owner'], MERGED)

    def test_original_ids_and_immutable_maps(self):
        g = open_gateway(RAW)
        pm, nm = copy.deepcopy(PMAP), copy.deepcopy(NMAP)
        q = register(g, positive_map=pm, negative_map=nm)
        self.assertEqual(q['negative_ids'], [0, 1, 2])
        for label, mapping in (('positive', PMAP), ('negative', NMAP)):
            for wire, original in mapping:
                self.assertEqual(g.original_id('r', 'a', label, wire), original)
        pm[0][0] = 'mutated'; nm.reverse()
        self.assertEqual(g.original_id('r', 'a', 'positive', 'same'), 0)
        self.assertEqual(g.original_id('r', 'a', 'negative', 'n-copy'), 1)
        before = g.export()
        for bad in (NMAP[:2], list(reversed(NMAP)), [['x', 0], ['x', 1], ['z', 2]],
                    [['x', False], ['y', 1], ['z', 2]]):
            with self.assertRaises(ValueError):
                register(g, rid='bad', aid='bad', negative_map=bad)
            self.assertEqual(g.export(), before)
        with self.assertRaises(ValueError):
            register(g, aid='b', positive_map=PMAP, negative_map=nm)
        with self.assertRaises(ValueError):
            g.original_id('r', 'a', 'negative', 'p-copy')
        p = self.assert_observation(g, q, 'PROJECTION_NO', canonical(projection_no(q)))
        self.assertEqual(p['feedback']['failed_negative'], 1)
        self.assertEqual(p['feedback']['tables'][0]['named_zeros'], [{'negative': 1, 'positive': 2}])
        self.assertEqual(p['feedback']['tables'][0]['anonymous_zeros'], [0])
        self.assertEqual(p['feedback']['tables'][0]['free_groups'], [[2]])

    def test_sample_and_response_binding(self):
        for changed in ('alphabet', 'positive', 'negative'):
            raw = copy.deepcopy(RAW)
            raw[changed] = raw[changed][1:] + raw[changed][:1]
            g = open_gateway(raw)
            q = register(g)
            original = register(open_gateway(RAW))
            self.assertNotEqual(q['scope']['sample_digest'], original['scope']['sample_digest'])
            self.assert_observation(g, q, 'UNKNOWN', canonical(projection_no(original)))
        for mutate in (
                lambda p: p['request']['scope'].update(family='REGION'),
                lambda p: p['request']['scope'].update(regime='BOUNDED'),
                lambda p: p['request'].update(owner=MERGED),
                lambda p: p['request']['negative_ids'].reverse(),
                lambda p: p['request'].update(attempt_id='stale'),
                lambda p: p['request'].update(request_id='other')):
            g = open_gateway(RAW); q = register(g)
            p = projection_no(q); mutate(p)
            self.assert_observation(g, q, 'UNKNOWN', canonical(p))

    def test_accept_projection_and_bounded_are_distinct(self):
        g = open_gateway(RAW)
        q = register(g)
        self.assert_observation(g, q, 'PROJECTION_NO', canonical(projection_no(q)))
        q = register(g, MERGED, 'accept', 'b')
        self.assert_observation(g, q, 'ACCEPT', canonical(accept(q)))
        q = register(g, MERGED, 'bounded', 'c', capacities=[1, 1])
        self.assert_observation(g, q, 'BOUNDED_NO', canonical(reply(q, 'BOUNDED_NO', exact=True)))
        q = register(g, SINGLE, 'bounded-projection', 'd', capacities=[1, 1, 1])
        self.assert_observation(g, q, 'PROJECTION_NO', canonical(projection_no(q)))
        self.assertEqual(set(g.pending_candidates), {'r', 'accept', 'bounded', 'bounded-projection'})
        for owner, caps, make in (
                (MERGED, None, lambda q: reply(q, 'BOUNDED_NO', exact=True)),
                (MERGED, [1, 1], accept),
                (MERGED, [1, 1], lambda q: reply(q, 'BOUNDED_NO', exact=False)),
                (SINGLE, None, lambda q: reply(q, 'NO')),
                (SINGLE, None, lambda q: reply(q, 'UNKNOWN'))):
            h = open_gateway(RAW); q = register(h, owner, capacities=caps)
            self.assert_observation(h, q, 'UNKNOWN', canonical(make(q)))

    def test_partial_or_false_witnesses_are_unknown(self):
        for mutate in (lambda p: p.update(complete=False),
                       lambda p: p['tables'].pop(),
                       lambda p: p['tables'][0]['zeros'][1].update(positive=None),
                       lambda p: p['tables'][0]['free'][0].append(1),
                       lambda p: p['tables'][0]['zeros'][1].update(positive=1),
                       lambda p: p['tables'][0].update(kind='CONDITIONED')):
            g = open_gateway(RAW); q = register(g)
            p = projection_no(q); mutate(p)
            self.assert_observation(g, q, 'UNKNOWN', canonical(p))
        for mutate in (lambda p: p['dfas'][0]['transitions'].pop(),
                       lambda p: p['dfas'][0]['accepting'].append(3),
                       lambda p: p['joint_row'][0].__setitem__(1, 0)):
            g = open_gateway(RAW); q = register(g, MERGED)
            p = accept(q); mutate(p)
            self.assert_observation(g, q, 'UNKNOWN', canonical(p))

    def test_unknown_retry_and_late_isolation(self):
        g = open_gateway(RAW); q = register(g)
        self.assertEqual(g.ingest('wrong', 'a', None), 'UNKNOWN')
        self.assertEqual(g.attempt_status('r', 'a'), 'PENDING')
        self.assertEqual(events(g)[-1]['records'], [])
        self.assert_observation(g, q, 'UNKNOWN', None)
        before = g.records
        self.assertEqual(g.ingest('r', 'a', canonical(projection_no(q))), 'UNKNOWN')
        self.assertEqual(g.records, before)
        with self.assertRaises(ValueError):
            register(g, rid='different')
        retry = register(g, aid='retry')
        self.assert_observation(g, retry, 'PROJECTION_NO', canonical(projection_no(retry)))
        self.assertEqual(g.attempt_status('r', 'a'), 'UNKNOWN')

    def test_external_labels_are_not_operational_authority(self):
        # No endpoint; both envelopes are local test fixtures.
        for auth, expected in ((None, 'UNKNOWN'), (lambda *_: True, 'ACCEPT')):
            g = open_gateway(RAW, authenticate=auth)
            q = register(g, MERGED, origin='EXTERNAL')
            p = accept(q); p['origin'] = 'EXTERNAL'
            self.assert_observation(g, q, expected, canonical(p))


    def test_late_response_cannot_cross_sample_scope(self):
        # Reuse the same global attempt token in two independent ledgers but
        # bind it to different request IDs and different original samples.
        source = open_gateway(RAW)
        source_q = register(source, MERGED, rid='source-scope', aid='shared-attempt')
        small_path = Path(__file__).parent / 'fixtures' / 'p3' / 'small_choice.raw.json'
        small_raw = json.loads(small_path.read_bytes())
        target = open_gateway(small_raw)
        target_q = register(target, list(range(len(small_raw['alphabet']))),
                            rid='target-scope', aid='shared-attempt')
        self.assertNotEqual(source_q['scope']['sample_digest'],
                            target_q['scope']['sample_digest'])
        self.assertNotEqual(source_q['request_id'], source_q['attempt_id'])
        self.assertNotEqual(target_q['request_id'], target_q['attempt_id'])

        # A late source-scope response collides on attempt_id but not on the
        # registered request/scope pair. It must be quarantined without
        # changing the unrelated target attempt or its pending candidate.
        late = canonical(projection_no(source_q))
        self.assertEqual(target.ingest(source_q['request_id'],
                                       source_q['attempt_id'], late), 'UNKNOWN')
        self.assertEqual(target.attempt_status(target_q['request_id'],
                                               target_q['attempt_id']), 'PENDING')
        self.assertEqual(target.pending_candidates, ('target-scope',))
        self.assertEqual(events(target)[-1]['event'], 'QUARANTINE')
        self.assertEqual(events(target)[-1]['records'], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
