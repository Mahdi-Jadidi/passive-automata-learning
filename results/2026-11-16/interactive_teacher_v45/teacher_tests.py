import unittest
import random
from itertools import product
from copy import deepcopy

from teacher_main import MainTeacher


def images(blocks, positive, negative):
    return {b: {'positive': [tuple(x for x in w if x in b) for w in positive],
                'negative': [tuple(x for x in w if x in b) for w in negative]}
            for b in blocks}


class TeacherTests(unittest.TestCase):
    def test_accept_and_witness(self):
        blocks = [('a',), ('b',)]
        data = images(blocks, [('a', 'b')], [('a',), ('b',)])
        teacher = MainTeacher(lambda: None)
        result = teacher.check(blocks, data)
        self.assertEqual(result['status'], 'ACCEPT')
        self.assertEqual(result['metrics']['cycle_bits'], 0)
        for i in range(2):
            self.assertTrue(any(result['rows'][b][i] for b in blocks))
        for b in blocks:
            dfa = result['witness'][b]
            for word, expected in [(w, True) for w in data[b]['positive']] + [
                (w, not result['rows'][b][i]) for i, w in enumerate(data[b]['negative'])]:
                state = 0
                for c in word:
                    state = dfa['transitions'][state * len(b) + b.index(c)]
                self.assertEqual(state in dfa['accepting'], bool(expected))
        self.assertEqual(teacher.check(blocks, data)['metrics']['cache_hits'], 2)

    def test_reject_forced_zeros(self):
        blocks = [('a',), ('b',)]
        data = images(blocks, [('a', 'b')], [('b', 'a')])
        self.assertEqual(MainTeacher(lambda: None).check(blocks, data)['status'], 'REJECT')

    def test_cycle_and_duplicate_columns(self):
        blocks = [('a',), ('b',)]
        data = images(blocks, [], [('a', 'b'), ('a', 'b')])
        result = MainTeacher(lambda: None).check(blocks, data)
        self.assertEqual(result['status'], 'ACCEPT')
        self.assertEqual(result['metrics']['cycle_bits'], 1)
        for row in result['rows'].values():
            self.assertEqual(row[0], row[1])

    def test_empty_positive_bound_and_no_negatives(self):
        blocks = [('a',)]
        result = MainTeacher(lambda: None).check(blocks, images(blocks, [], []))
        self.assertEqual(result['status'], 'ACCEPT')
        self.assertEqual(result['metrics']['dfa_representations'], 2)

    def test_interrupt_does_not_cache_partial_table(self):
        class Deadline(Exception):
            pass
        count = [0]
        def tick():
            count[0] += 1
            if count[0] == 5:
                raise Deadline()
        teacher = MainTeacher(tick)
        blocks = [('a',)]
        with self.assertRaises(Deadline):
            teacher.check(blocks, images(blocks, [('a',)], []))
        self.assertEqual(teacher.cache, {})
        self.assertEqual(teacher.stats['completed_checks'], 0)

    def test_seeded_raw_join_comparison(self):
        rng = random.Random(4516)
        blocks = [('a',), ('b',)]
        words = [(), ('a',), ('b',), ('a', 'b'), ('b', 'a')]
        teacher = MainTeacher(lambda: None)
        saw_cycle = saw_forced = saw_forest = False
        for _ in range(30):
            positives = rng.sample(words, rng.randrange(3))
            negatives = rng.sample(words, rng.randrange(4))
            data = images(blocks, positives, negatives)
            result = teacher.check(blocks, data)
            original = deepcopy(teacher.cache)
            local = []
            for b in blocks:
                pos = tuple(data[b]['positive'])
                neg = tuple(data[b]['negative'])
                prefixes = {w[:j] for w in pos for j in range(len(w) + 1)} | {()}
                bound = len(prefixes) + 1 if pos else 1
                local.append(teacher.cache[(b, pos, neg, bound)])
            possible = any(all(any(row[i] for row in rows)
                               for i in range(len(negatives)))
                           for rows in product(*local))
            self.assertEqual(result['status'] == 'ACCEPT', possible)
            self.assertEqual(original, teacher.cache)
            self.assertEqual(teacher.check(blocks, data)['status'], result['status'])
            self.assertEqual(original, teacher.cache)
            saw_cycle |= result['metrics']['cycle_bits'] > 0
            saw_forest |= result['metrics']['cycle_bits'] == 0
            saw_forced |= any(w in data[b]['positive'] for b in blocks
                              for w in data[b]['negative'])
            if result['status'] == 'ACCEPT':
                for i in range(len(negatives)):
                    self.assertTrue(any(result['rows'][b][i] for b in blocks))
                for b in blocks:
                    dfa = result['witness'][b]
                    def accept(word):
                        state = 0
                        for symbol in word:
                            state = dfa['transitions'][state * len(b) + b.index(symbol)]
                        return state in dfa['accepting']
                    self.assertTrue(all(accept(w) for w in data[b]['positive']))
                    self.assertEqual(tuple(int(not accept(w)) for w in data[b]['negative']),
                                     result['rows'][b])
        self.assertTrue(saw_cycle and saw_forest and saw_forced)
        self.assertEqual(teacher.completed_checks, 60)


if __name__ == '__main__':
    unittest.main()
