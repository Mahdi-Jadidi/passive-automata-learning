"""Exact sample-compatible maximum-block recommendation; no physical K inference."""
from functools import lru_cache
import math
import time

METHOD = 'C026-max-blocks-v1'


class Halt(Exception):
    pass


class BadInput(Exception):
    pass


def solve(data, *, deadline=None, memo_limit=100000):
    start = time.perf_counter()
    metrics = {'dp_entries': 0, 'dp_calls': 0, 'block_masks_computed': 0,
               'reject_cache_limit': 4096}
    incumbent = None
    one = None
    upper = None
    proof = {}

    def poll():
        if deadline is not None and time.perf_counter() >= deadline:
            raise Halt('deadline')

    def result(status, complete=False, optimal=None, error=None):
        rec = None
        if incumbent is not None:
            count = len(incumbent['blocks'])
            rec = {'objective': 'max_blocks', 'partition': incumbent['blocks'],
                   'witness': incumbent, 'block_count': count, 'lower_bound': count,
                   'upper_bound': count if optimal is not None else upper,
                   'optimality_proved': optimal is not None,
                   'tie_status': ('multiple' if len(optimal) > 1 else 'unique') if optimal is not None else 'unresolved',
                   'optimal_witnesses': optimal if optimal is not None else []}
        out = {'schema_version': 1, 'method': METHOD, 'status': status,
               'physical_truth_read': False,
               'findings': {'data_insufficient': True if status == 'ambiguous' else False if status in ('certified_unique', 'incompatible') else None,
                            'computation_incomplete': not complete},
               'recommendation': rec, 'certificate': proof, 'metrics': metrics}
        if status == 'ambiguous':
            out['alternatives'] = [one, incumbent]
        if error is not None:
            out['error' if status == 'invalid_input' else 'reason'] = error
        metrics['solver_seconds'] = time.perf_counter() - start
        return out

    try:
        if deadline is not None and (isinstance(deadline, bool) or not isinstance(deadline, (int, float)) or not math.isfinite(deadline)):
            raise BadInput('deadline must be finite absolute perf_counter time or None')
        if type(memo_limit) is not int or memo_limit <= 0:
            raise BadInput('memo_limit must be a positive integer')
        poll()
        if not isinstance(data, dict) or set(data) != {'alphabet', 'positive', 'negative'}:
            raise BadInput('input requires exactly alphabet, positive, negative')
        alphabet = data['alphabet']
        if not isinstance(alphabet, list) or not alphabet:
            raise BadInput('alphabet must be a nonempty list')
        symbols = set()
        for a in alphabet:
            poll()
            if not isinstance(a, str) or len(a) != 1 or a in symbols:
                raise BadInput('alphabet symbols must be distinct one-character strings')
            symbols.add(a)
        alphabet = sorted(alphabet)
        P, N = data['positive'], data['negative']
        if not isinstance(P, list) or not isinstance(N, list):
            raise BadInput('positive and negative must be lists')
        positives = set()
        contradiction = False
        for label, words in ((True, P), (False, N)):
            for word in words:
                poll()
                if not isinstance(word, str):
                    raise BadInput('words must be strings')
                for i, ch in enumerate(word):
                    if i % 1024 == 0:
                        poll()
                    if ch not in symbols:
                        raise BadInput('word contains undeclared symbol')
                if label:
                    positives.add(word)
                elif word in positives:
                    contradiction = True
        poll()
        if contradiction:
            proof['route'] = 'contradictory_labels'
            return result('incompatible', True)
        rejects = []
        for ni in range(len(N)):
            poll()
            rejects.append({'negative_index': ni, 'rejected_by_block': 0})
        one = {'blocks': [alphabet.copy()], 'negative_rejections': rejects,
               'local_language_rule': 'positive_projections_from_input'}
        upper = len(alphabet)
        incumbent = one

        # A labelled adjacent transposition across different owners preserves
        # every projection, so the two symbols must share an owner (C024).
        parent = {a: a for a in alphabet}
        def root(a):
            while parent[a] != a:
                poll()
                a = parent[a]
            return a
        edges = []
        for pi, p in enumerate(P):
            for ni, n in enumerate(N):
                poll()
                if len(p) != len(n):
                    continue
                diff = []
                for i, (a, b) in enumerate(zip(p, n)):
                    if i % 1024 == 0:
                        poll()
                    if a != b:
                        diff.append(i)
                        if len(diff) > 2:
                            break
                if len(diff) != 2 or diff[1] != diff[0] + 1:
                    continue
                i, j = diff
                if p[i] != n[j] or p[j] != n[i]:
                    continue
                a, b = root(p[i]), root(p[j])
                if a != b:
                    parent[max(a, b)] = min(a, b)
                    edges.append({'positive_index': pi, 'negative_index': ni,
                                  'positions': [i, j], 'symbols': [p[i], p[j]]})
        groups = {}
        for a in alphabet:
            poll()
            groups.setdefault(root(a), []).append(a)
        atoms = sorted(groups.values())
        r = len(atoms)
        upper = r
        full = (1 << r) - 1
        target = (1 << len(N)) - 1
        proof.update(forced_atoms=atoms, swap_forest=edges)

        def block_symbols(mask):
            block = []
            for i, atom in enumerate(atoms):
                poll()
                if mask & (1 << i):
                    block.extend(atom)
            return sorted(block)

        def project(word, allowed):
            chunks = []
            for offset in range(0, len(word), 1024):
                poll()
                chunks.append(''.join(ch for ch in word[offset:offset + 1024] if ch in allowed))
            poll()
            return ''.join(chunks)

        @lru_cache(maxsize=4096)
        def reject(mask):
            poll()
            allowed = set(block_symbols(mask))
            language = set()
            for p in P:
                poll()
                language.add(project(p, allowed))
            bits = 0
            for ni, n in enumerate(N):
                poll()
                if project(n, allowed) not in language:
                    bits |= 1 << ni
            metrics['block_masks_computed'] += 1
            return bits

        def witness(part):
            covered = 0
            rejections, blocks = [], []
            for bi, mask in enumerate(part):
                poll()
                rejected = reject(mask)
                new = rejected & ~covered
                while new:
                    poll()
                    bit = new & -new
                    rejections.append({'negative_index': bit.bit_length() - 1, 'rejected_by_block': bi})
                    new ^= bit
                covered |= rejected
                blocks.append(block_symbols(mask))
            if covered != target:
                return None
            rejections.sort(key=lambda item: item['negative_index'])
            poll()
            return {'blocks': blocks, 'negative_rejections': rejections,
                    'local_language_rule': 'positive_projections_from_input'}

        singles = tuple(1 << i for i in range(r))
        atom_witness = witness(singles)
        if atom_witness is not None:
            incumbent = atom_witness
            proof['route'] = 'compatible_forced_atoms'
            return result('ambiguous' if r > 1 else 'certified_unique', True, [atom_witness])
        upper = r - 1

        def key(part):
            owner = {}
            for bi, mask in enumerate(part):
                for a in block_symbols(mask):
                    poll()
                    owner[a] = bi
            return tuple(owner[a] for a in alphabet if a in owner)

        memo = {}
        def dp(remaining, uncovered):
            nonlocal incumbent
            poll()
            metrics['dp_calls'] += 1
            state = (remaining, uncovered)
            if state in memo:
                return memo[state]
            if metrics['dp_entries'] >= memo_limit:
                raise Halt('memo_limit')
            metrics['dp_entries'] += 1  # Includes reserved in-flight entries.
            if not remaining:
                answer = (0, [()]) if not uncovered else (-1, [])
            elif not uncovered:
                part = tuple(1 << i for i in range(r) if remaining & (1 << i))
                answer = (len(part), [part])
            elif uncovered & ~reject(remaining):
                answer = (-1, [])
            else:
                anchor = remaining & -remaining
                tail = remaining ^ anchor
                sub = tail
                best, choices = -1, []
                while True:
                    poll()
                    block = sub | anchor
                    value, children = dp(remaining ^ block, uncovered & ~reject(block))
                    if value >= 0:
                        value += 1
                        if value > best:
                            best, choices = value, []
                        if value == best:
                            for child in children:
                                poll()
                                part = (block,) + child
                                choices.append(part)
                                if state == (full, target) and len(part) > len(incumbent['blocks']):
                                    candidate = witness(part)
                                    if candidate is None:
                                        raise AssertionError('DP produced infeasible partition')
                                    incumbent = candidate
                            choices.sort(key=key)
                            choices = choices[:2]
                    if sub == 0:
                        break
                    sub = (sub - 1) & tail
                answer = (best, choices)
            memo[state] = answer
            return answer

        value, parts = dp(full, target)
        optimal = []
        for part in parts:
            poll()
            candidate = witness(part)
            if candidate is None:
                raise AssertionError('invalid optimum')
            optimal.append(candidate)
        poll()
        if not optimal or value < 1:
            raise AssertionError('consistent data always has one-block witness')
        incumbent = optimal[0]
        proof['route'] = 'completed_anchored_max_dp'
        return result('ambiguous' if value > 1 else 'certified_unique', True, optimal)
    except BadInput as exc:
        return result('invalid_input', True, error=str(exc))
    except (Halt, KeyboardInterrupt, RecursionError, MemoryError) as exc:
        ambiguous = incumbent is not None and len(incumbent['blocks']) > 1
        return result('ambiguous' if ambiguous else 'unresolved', error=str(exc) or type(exc).__name__)
