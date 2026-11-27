"""Native offline AEFC fixtures and literal partition checks."""
import json
import os
from dataclasses import replace
from pathlib import Path
import unittest

from gateway import open_gateway

from ..feedback_aefc import Limits, prepare
from ..schema import canonical
from .test_roundtrip import response, tables


NAMED = dict(alphabet=list('abcd'), positive=[list('abcd')], negative=[list('abdc')])
CROSS = dict(alphabet=list('abcde'), positive=[list('abcd'), list('e')],
             negative=[list('abdce'), list('abdce'), list('abdc')])
STITCH = ([0, 0, 2, 3], [0, 1, 0, 3], [0, 1, 1, 3])


def history(raw, queries):
    ledger = open_gateway(raw)
    for event, (owner, failed) in enumerate(queries):
        request_id, attempt = f'q{event}', f'a{event}'
        request = ledger.register(owner, request_id, attempt)
        wire = canonical(response(request, 'PROJECTION_NO', f'offline-{event}',
                                  failed=failed, tables=tables(raw, request, failed)))
        if ledger.ingest(request_id, attempt, wire) != 'PROJECTION_NO':
            raise ValueError('offline observation rejected')
    return ledger


def owners(n):
    def visit(rgs, groups):
        if len(rgs) == n:
            minima = {group: rgs.index(group) for group in range(groups)}
            yield tuple(minima[group] for group in rgs)
            return
        for group in range(groups + 1):
            yield from visit((*rgs, group), max(group + 1, groups))
    yield from visit((), 0)


def literal_no(raw, owner):
    def projection(word, group):
        return tuple(a for a in word if owner[raw['alphabet'].index(a)] == group)
    return any(all(any(projection(y, group) == projection(x, group)
                       for x in raw['positive']) for group in set(owner))
               for y in raw['negative'])


class AEFCTests(unittest.TestCase):
    def exercise(self, name, raw, queries, target):
        ledger = history(raw, queries)
        journal = ledger.export()
        status, snapshot = prepare(raw, journal)
        self.assertEqual(status, 'READY')
        self.assertEqual(snapshot.prove(target, containment_only=True), ('UNKNOWN', None))
        status, sidecar = snapshot.prove(target)
        self.assertEqual(status, 'PROVEN_NO')
        self.assertTrue(literal_no(raw, target))
        self.assertEqual(snapshot.prove(target), (status, sidecar))
        self.assertEqual(ledger.export(), journal)
        counts = dict(targets=0, literal_no=0, containment=0, named=0)
        for owner in owners(len(raw['alphabet'])):
            literal = literal_no(raw, owner)
            direct = snapshot.prove(owner, containment_only=True)[0] == 'PROVEN_NO'
            named = snapshot.prove(owner)[0] == 'PROVEN_NO'
            self.assertLessEqual(direct, named)
            self.assertLessEqual(named, literal)
            counts['targets'] += 1
            counts['literal_no'] += literal
            counts['containment'] += direct
            counts['named'] += named
        self.assertGreater(counts['named'], counts['containment'])
        print(name, counts, 'sidecar bytes', len(sidecar))
        directory = os.environ.get('AEFC_ARTIFACT_DIR')
        if directory:
            path = Path(directory) / name
            path.mkdir(parents=True, exist_ok=True)
            for filename, data in [('raw', canonical(raw)), ('journal', journal),
                                   ('target', canonical(target)), ('sidecar', sidecar)]:
                (path / f'{filename}.json').write_bytes(data)
        return snapshot, journal, json.loads(sidecar)

    def test_named_and_caps(self):
        target = [0, 0, 0, 3]
        snapshot, journal, proof = self.exercise('named', NAMED, [(q, 0) for q in STITCH], target)
        self.assertEqual(proof['blocks'][0]['kind'], 'ATOM_MATCH')
        for field in ('work', 'seconds', 'entries', 'paths', 'edges', 'sidecar_bytes', 'blocks'):
            self.assertEqual(snapshot.prove(target, limits=replace(Limits(), **{field: 0})),
                             ('UNKNOWN', None))
        self.assertEqual(prepare(NAMED, journal, limits=Limits(journal_bytes=1)), ('UNKNOWN', None))
        self.assertEqual(prepare(NAMED, journal + b' '), ('INVALID', None))
        self.assertEqual(snapshot.prove([0, 0, 0, True]), ('INVALID', None))
        self.assertEqual(snapshot.prove([0, 1, 2, 2]), ('UNKNOWN', None))

    def test_cross_id_with_duplicate_words(self):
        queries = [(STITCH[0] + [4], 1), (STITCH[1] + [4], 0),
                   (STITCH[2] + [4], 0), ([0, 0, 2, 3, 0], 2)]
        _, _, proof = self.exercise('cross-id', CROSS, queries, [0, 0, 0, 3, 4])
        self.assertEqual(proof['negative_id'], 'N0')
        pair = next(p for p in proof['blocks'][0]['paths'] if p['atom'] == [0, 1])
        self.assertEqual([e['to'] for e in pair['edges']], ['N1', 'P0'])

    def test_independent_positive_per_atom_is_insufficient(self):
        raw = dict(alphabet=list('abc'), positive=[[a] for a in 'abc'], negative=[[]])
        queries = [([0, 0, 2], 0), ([0, 1, 0], 0), ([0, 1, 1], 0)]
        status, snapshot = prepare(raw, history(raw, queries).export())
        self.assertEqual(status, 'READY')
        self.assertFalse(literal_no(raw, [0, 0, 0]))
        self.assertEqual(snapshot.prove([0, 0, 0]), ('UNKNOWN', None))

    def test_anonymous_zero_is_not_a_named_edge(self):
        raw = dict(alphabet=list('abcde'), positive=list(map(list, ('abcd', 'bace'))),
                   negative=list(map(list, ('abcde', 'abced'))))
        queries = [([0, 1, 0, 0, 4], 0), ([0, 1, 1, 1, 4], 0),
                   ([0, 1, 0, 3, 0], 0), ([0, 1, 1, 3, 1], 0),
                   ([0, 0, 2, 3, 4], 1)]
        status, snapshot = prepare(raw, history(raw, queries).export())
        self.assertEqual(status, 'READY')
        target = [0, 0, 0, 3, 4]
        self.assertTrue(literal_no(raw, target))
        self.assertEqual(snapshot.prove(target), ('UNKNOWN', None))

    def test_bounded_no_and_order_difference(self):
        raw = dict(alphabet=list('ab'), positive=[list('aba')], negative=[list('aab')])
        ledger = history(raw, [([0, 1], 0)])
        request = ledger.register([0, 0], 'bounded', 'bounded', capacities=[1])
        wire = canonical(response(request, 'BOUNDED_NO', 'bounded', exact=True))
        self.assertEqual(ledger.ingest('bounded', 'bounded', wire), 'BOUNDED_NO')
        status, snapshot = prepare(raw, ledger.export())
        self.assertEqual(status, 'READY')
        self.assertFalse(literal_no(raw, [0, 0]))
        self.assertEqual(snapshot.prove([0, 0]), ('UNKNOWN', None))

    def test_zero_regions_cannot_mix_negatives(self):
        raw = dict(alphabet=list('abcd'), positive=[list('abcd')],
                   negative=list(map(list, ('bacd', 'abdc'))))
        queries = [([0, 0, 2, 3], 1), ([0, 1, 2, 2], 0)]
        status, snapshot = prepare(raw, history(raw, queries).export())
        self.assertEqual(status, 'READY')
        target = [0, 0, 2, 2]
        self.assertFalse(literal_no(raw, target))
        self.assertEqual(snapshot.prove(target), ('UNKNOWN', None))
