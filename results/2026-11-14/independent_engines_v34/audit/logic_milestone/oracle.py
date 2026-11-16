"""Independent finite-partition oracle for the V34 single-optimum audit.

Uses insertion of the next alphabet index into existing blocks or a new block.
It does not import a solver, checker, RGS generator, CNF builder, or old engine.
"""
from itertools import product


def partitions(indices):
    if not indices:
        yield ()
        return
    head, *tail = indices
    for rest in partitions(tail):
        yield ((head,),) + rest
        for i in range(len(rest)):
            yield rest[:i] + ((head,) + rest[i],) + rest[i + 1:]


def compatible(instance, partition):
    alphabet = instance['alphabet']
    positive, negative = instance['positive'], instance['negative']
    sets = [{alphabet[i] for i in block} for block in partition]
    def project(word, block):
        return tuple(item for item in word if item in block)
    positives = [{project(p, block) for p in positive} for block in sets]
    return all(any(project(n, block) not in images
                   for block, images in zip(sets, positives)) for n in negative)


def optimum(instance):
    feasible = [p for p in partitions(list(range(len(instance['alphabet']))))
                if compatible(instance, p)]
    return max(map(len, feasible)) if feasible else None


def witness_valid(instance, blocks):
    alphabet = instance['alphabet']
    if not isinstance(blocks, list) or any(not isinstance(b, list) or not b for b in blocks):
        return False
    flat = [x for b in blocks for x in b]
    if len(flat) != len(alphabet) or len(set(flat)) != len(flat) or set(flat) != set(alphabet):
        return False
    index = {x: i for i, x in enumerate(alphabet)}
    return compatible(instance, tuple(tuple(index[x] for x in b) for b in blocks))


def corpus():
    words = [[], ['a'], ['b']]
    for labels in product(range(3), repeat=len(words)):
        yield 'ternary_' + ''.join(map(str, labels)), {
            'alphabet': ['a', 'b'],
            'positive': [w for w, v in zip(words, labels) if v == 1],
            'negative': [w for w, v in zip(words, labels) if v == 2],
        }
    cases = [
        ('empty_feasible', {'alphabet': [], 'positive': [[]], 'negative': []}),
        ('empty_infeasible', {'alphabet': [], 'positive': [], 'negative': [[]]}),
        ('contradiction', {'alphabet': ['a'], 'positive': [['a']], 'negative': [['a']]}),
        ('empty_positive', {'alphabet': ['a', 'unused'], 'positive': [], 'negative': [[], ['a']]}),
        ('empty_negative', {'alphabet': ['a', 'b', 'c'], 'positive': [[]], 'negative': []}),
        ('repeated_ids', {'alphabet': ['a', 'b'], 'positive': [['a', 'a']], 'negative': [['a']]}),
        ('opaque_unused', {'alphabet': ['alpha', 'x y', 'unused'], 'positive': [[], ['alpha', 'x y']], 'negative': [['alpha']]}),
        ('duplicates', {'alphabet': ['a', 'b'], 'positive': [[], [], ['a']], 'negative': [['b'], ['b']]}),
        ('order_sensitive', {'alphabet': ['a', 'b'], 'positive': [['a', 'b', 'a']], 'negative': [['b', 'a', 'a']]}),
        ('atomic_ids', {'alphabet': ['a', 'aa'], 'positive': [['a', 'aa']], 'negative': [['aa', 'a']]}),
        ('unicode_distinct', {'alphabet': ["é", "é"], 'positive': [["é", "é"]], 'negative': [["é", "é"]]}),
        ('three_tie', {'alphabet': ['a', 'b', 'c'], 'positive': [[], ['a', 'b', 'c']], 'negative': [['a']]}),
    ]
    yield from cases

