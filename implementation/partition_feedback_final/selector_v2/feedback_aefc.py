"""Read-only named AEFC producer for audited journal/2 snapshots."""
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from itertools import chain, combinations
from time import monotonic

from .core import Sample
from .schema import canonical, scope


@dataclass(frozen=True)
class Limits:
    journal_bytes: int = 16 << 20
    work: int = 2_000_000
    entries: int = 200_000
    seconds: float = 10
    blocks: int = 100_000
    paths: int = 200_000
    edges: int = 1_000_000
    sidecar_bytes: int = 16 << 20


class _Capped(Exception):
    pass


class _Budget:
    def __init__(self, limits):
        self.work = limits.work
        self.entries = limits.entries
        self.deadline = monotonic() + limits.seconds

    def spend(self, work=1, entries=0):
        self.work -= work
        self.entries -= entries
        if min(self.work, self.entries) < 0 or monotonic() >= self.deadline:
            raise _Capped


class _Forest:
    def __init__(self, budget):
        self.parent = {}
        self.size = {}
        self.links = defaultdict(list)
        self.budget = budget

    def root(self, node):
        while self.parent.get(node, node) != node:
            self.budget.spend()
            node = self.parent[node]
        return node

    def join(self, left, right, event, group):
        a, b = self.root(left), self.root(right)
        if a == b:
            return
        self.budget.spend(entries=2)
        if self.size.get(a, 1) < self.size.get(b, 1):
            a, b = b, a
        self.parent[b] = a
        self.size[a] = self.size.get(a, 1) + self.size.get(b, 1)
        self.links[left].append((right, event, group))
        self.links[right].append((left, event, group))

    def path(self, start, end, max_edges):
        previous = {start: None}
        stack = [start]
        while end not in previous:
            node = stack.pop()
            for neighbor, event, group in self.links[node]:
                self.budget.spend()
                if neighbor not in previous:
                    previous[neighbor] = (node, event, group)
                    stack.append(neighbor)
        path = []
        while end != start:
            self.budget.spend()
            if len(path) >= max_edges:
                raise _Capped
            node, event, group = previous[end]
            path.append(dict(event=event, group=group, **{'from': node, 'to': end}))
            end = node
        return path[::-1]


def _blocks(owner):
    blocks = defaultdict(set)
    for symbol, group in enumerate(owner):
        blocks[group].add(symbol)
    return blocks


def _index(events, budget):
    registrations = {}
    zeros = defaultdict(list)
    sources = []
    for event, item in enumerate(events):
        budget.spend()
        if item['event'] == 'REGISTER':
            request = item['registered']['request']
            registrations[request['attempt_id']] = request
        if item['event'] != 'OBSERVE' or item['status'] != 'PROJECTION_NO':
            continue
        request = registrations[item['attempt_id']]
        feedback = item['records'][0]['payload']['feedback']
        if (request['scope']['regime'] != 'UNRESTRICTED'
                or feedback['kind'] != 'UNRESTRICTED_COMPLETE'):
            continue
        budget.spend(len(request['owner']))
        regions = _blocks(request['owner'])
        for table in feedback['tables']:
            group = table['group']
            region = regions[group]
            edges = []
            for zero in table['named_zeros']:
                budget.spend(entries=2)
                negative = zero['negative']
                zeros[negative].append((region, event, group))
                edges.append((f'N{negative}', f'P{zero["positive"]}'))
            for negative in table['anonymous_zeros']:
                budget.spend(entries=1)
                zeros[negative].append((region, event, group))
            for free in table['free_groups']:
                for member in free[1:]:
                    budget.spend(entries=1)
                    edges.append((f'N{free[0]}', f'N{member}'))
            if edges:
                sources.append((region, event, group, edges))
    return zeros, sources


@dataclass(frozen=True)
class Snapshot:
    """Immutable input binding. Construct via prepare; reuse for multiple targets."""
    sample_digest: str
    journal_sha256: str
    alphabet_size: int
    positives: int
    negatives: int
    _zeros: tuple
    _sources: tuple

    def prove(self, owner, *, containment_only=False, limits=Limits()):
        """Return (PROVEN_NO, canonical sidecar bytes), UNKNOWN or INVALID."""
        try:
            return self._prove(owner, containment_only, limits)
        except (_Capped, MemoryError):
            return 'UNKNOWN', None

    def _prove(self, owner, containment_only, limits):
        budget = _Budget(limits)
        if type(owner) not in (list, tuple) or len(owner) != self.alphabet_size:
            return 'INVALID', None
        budget.spend(len(owner), len(owner))
        owner = tuple(owner)
        for symbol, group in enumerate(owner):
            if type(group) is not int or not 0 <= group <= symbol or owner[group] != group:
                return 'INVALID', None
        blocks = _blocks(owner)
        if not blocks or len(blocks) > min(limits.blocks, 100_000):
            return 'UNKNOWN', None
        forests = {}
        for negative in range(self.negatives):
            budget.spend()
            start = f'N{negative}'
            entries = []
            paths_left = min(limits.paths, 200_000)
            edges_left = min(limits.edges, 1_000_000)
            for group, block in blocks.items():
                direct = None
                for region, event, source_group in self._zeros[negative]:
                    budget.spend()
                    if len(block) <= len(region):
                        budget.spend(len(block))
                        if block <= region:
                            direct = dict(group=group, kind='ZERO_CONTAINMENT',
                                          event=event, source_group=source_group)
                            break
                if direct is not None:
                    entries.append(direct)
                    continue
                count = len(block) * (len(block) + 1) // 2
                if containment_only or count > paths_left:
                    break
                symbols = sorted(block)
                budget.spend(count, count)
                atoms = tuple(chain(combinations(symbols, 1), combinations(symbols, 2)))
                for atom in atoms:
                    if atom not in forests:
                        forests[atom] = self._forest(atom, budget)
                for positive in range(self.positives):
                    budget.spend()
                    end = f'P{positive}'
                    if all(self._connected(forests[atom], start, end, budget) for atom in atoms):
                        paths = []
                        for atom in atoms:
                            edges = forests[atom].path(start, end, edges_left)
                            edges_left -= len(edges)
                            paths.append(dict(atom=atom, edges=edges))
                        entries.append(dict(group=group, kind='ATOM_MATCH',
                                            positive_id=end, paths=paths))
                        paths_left -= count
                        break
                else:
                    break
            else:
                budget.spend()
                sidecar = canonical(dict(format='feedback-aefc-named/v1',
                                         sample_digest=self.sample_digest,
                                         journal_sha256=self.journal_sha256,
                                         owner=owner, negative_id=start, blocks=entries))
                budget.spend()
                if len(sidecar) <= min(limits.sidecar_bytes, 16 << 20):
                    return 'PROVEN_NO', sidecar
        return 'UNKNOWN', None

    @staticmethod
    def _connected(forest, start, end, budget):
        budget.spend()
        return forest.root(start) == forest.root(end)

    def _forest(self, atom, budget):
        forest = _Forest(budget)
        for region, event, group, edges in self._sources:
            budget.spend()
            if all(symbol in region for symbol in atom):
                for left, right in edges:
                    budget.spend()
                    forest.join(left, right, event, group)
        return forest


def prepare(raw, journal, *, limits=Limits()):
    """Return (READY, snapshot), INVALID or UNKNOWN from immutable export bytes.

    Requires the pinned independent journal replay dependencies on the import
    path. Run replay in a process with a hard time/address-space limit for
    untrusted inputs; the existing replay routine has no cooperative deadline.
    """
    from journal_v2_replay import InvalidProof, strict_bytes, verify_journal

    try:
        budget = _Budget(limits)
        if type(journal) is not bytes:
            return 'INVALID', None
        if len(journal) > limits.journal_bytes:
            return 'UNKNOWN', None
        budget.spend()
        raw = strict_bytes(canonical(raw))
        sample = Sample.from_input(raw)
        verification = verify_journal(raw, scope(sample), journal,
                                      max_journal_bytes=limits.journal_bytes)
        if verification['status'] != 'VERIFIED':
            return ('INVALID' if verification['status'] == 'INVALID' else 'UNKNOWN'), None
        budget.spend()
        zeros, sources = _index(strict_bytes(journal)['events'], budget)
        frozen_regions = {}
        def freeze(region):
            key = id(region)
            if key not in frozen_regions:
                budget.spend(len(region), len(region))
                frozen_regions[key] = frozenset(region)
            return frozen_regions[key]

        budget.spend(len(raw['negative']), len(raw['negative']))
        zero_index = tuple(tuple((freeze(region), event, group)
                                 for region, event, group in zeros.get(negative, ()))
                           for negative in range(len(raw['negative'])))
        edge_index = tuple((freeze(region), event, group, tuple(edges))
                           for region, event, group, edges in sources)
        budget.spend()
        return 'READY', Snapshot(sample.sample_digest, sha256(journal).hexdigest(),
                                 len(raw['alphabet']), len(raw['positive']),
                                 len(raw['negative']), zero_index, edge_index)
    except (InvalidProof, ValueError, TypeError, KeyError, RecursionError):
        return 'INVALID', None
    except (_Capped, MemoryError):
        return 'UNKNOWN', None
