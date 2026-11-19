"""Exact goal-directed ownership gate; no physical truth or heuristic guesses."""
from functools import lru_cache
from collections import Counter
import math
import time

METHOD = 'C024-integrated-exact-search'
# <=64KiB of UTF-32 character payload per temporary chunk; headers/Counter
# entries are additional. ASCII synthetic inputs use <=16KiB per chunk.
COUNT_CHUNK_CHARS = 16 * 1024


class Halt(Exception):
    pass


class BadInput(Exception):
    pass


def solve(data, *, known_k=None, deadline=None):
    start = time.perf_counter()
    metrics = {'characters_counted': 0, 'projection_characters': 0,
               'swap_pairs': 0, 'search_nodes': 0, 'complete_candidates': 0,
               'block_masks_computed': 0, 'reject_cache_limit': 4096,
               'count_chunks': 0, 'counter_characters_processed': 0,
               'invalid_validation_characters': 0,
               'word_signatures': 0, 'graph_pair_universe': 0,
               'graph_pairs_filtered': 0,
               'projection_chunks': 0, 'deletion_tables_built': 0}
    assumptions = ['finite noiseless full-word labels', 'known disjoint symbol ownership',
                   'independent regular factors without a state bound',
                   'all component counts allowed' if known_k is None else 'externally trusted exact known_k']
    base = {'schema_version': 1, 'method': METHOD, 'known_k': known_k,
            'assumptions': assumptions, 'physical_truth_read': False, 'metrics': metrics}

    def poll():
        if deadline is not None and time.perf_counter() >= deadline:
            raise Halt('deadline')

    def emit(status, route, **fields):
        poll()
        return {**base, 'status': status,
                'findings': {'data_insufficient': status == 'ambiguous', 'computation_incomplete': False},
                'certificate': {'route': route, **fields}}

    def unique(route, witness, **proof):
        out = emit('certified_unique', route, witness=witness, **proof)
        out['partition'] = witness['blocks']
        return out

    def ambiguous(route, witnesses, **proof):
        if witnesses[0]['blocks'] == witnesses[1]['blocks']:
            raise AssertionError('ambiguity witnesses must differ')
        out = emit('ambiguous', route, **proof)
        out['alternatives'] = witnesses
        return out

    try:
        if deadline is not None and (isinstance(deadline, bool) or not isinstance(deadline, (int, float)) or
                                     isinstance(deadline, float) and not math.isfinite(deadline)):
            raise BadInput('deadline must be finite absolute perf_counter time or None')
        poll()
        if not isinstance(data, dict) or set(data) != {'alphabet', 'positive', 'negative'}:
            raise BadInput('input requires exactly alphabet, positive, negative; known_k is an explicit API/CLI argument')
        alphabet = data['alphabet']
        if not isinstance(alphabet, list) or not alphabet:
            raise BadInput('alphabet must be a nonempty list')
        seen = set()
        for a in alphabet:
            poll()
            if not isinstance(a, str) or len(a) != 1 or a in seen:
                raise BadInput('alphabet symbols must be distinct one-character strings')
            seen.add(a)
        alphabet = sorted(alphabet)
        m = len(alphabet)
        if known_k is not None and (type(known_k) is not int or not 1 <= known_k <= m):
            raise BadInput('known_k must be an explicit integer in 1..alphabet_size')
        if any(not isinstance(data[name], list) for name in ('positive', 'negative')):
            raise BadInput('positive and negative must be lists')
        P, N = data['positive'], data['negative']
        counts_seen = {a: set() for a in alphabet}
        presence = {a: 0 for a in alphabet}
        positives = {}
        unary_certificates = []
        unary = True
        contradiction = None
        universal = []
        positive_signatures, negative_signatures = [], []
        for label, words in (('positive', P), ('negative', N)):
            if label == 'negative':
                for a in alphabet:
                    poll()
                    if presence[a] == len(P):
                        universal.append(a)
            for wi, word in enumerate(words):
                poll()
                if not isinstance(word, str):
                    raise BadInput('words must be strings')
                counts = Counter()
                for offset in range(0, len(word), COUNT_CHUNK_CHARS):
                    poll()
                    chunk = word[offset:offset + COUNT_CHUNK_CHARS]
                    partial = Counter(chunk)
                    metrics['count_chunks'] += 1
                    metrics['counter_characters_processed'] += len(chunk)
                    invalid = False
                    for ch in partial:
                        poll()
                        if ch not in seen:
                            invalid = True
                            break
                    if invalid:
                        # Match baseline first-invalid-character error/metric
                        # semantics without doing this Python scan on valid data.
                        for i, ch in enumerate(chunk):
                            if i % 1024 == 0:
                                poll()
                            metrics['invalid_validation_characters'] += 1
                            if ch not in seen:
                                metrics['characters_counted'] += i
                                raise BadInput('word contains undeclared symbol')
                        raise AssertionError('invalid count key absent from chunk')
                    counts.update(partial)
                    metrics['characters_counted'] += len(chunk)
                    poll()
                poll()
                signature = (len(word), tuple(sorted(counts.items())))
                poll()
                metrics['word_signatures'] += 1
                if label == 'positive':
                    positive_signatures.append(signature)
                    positives.setdefault(word, wi)
                    for a, c in counts.items():
                        poll()
                        counts_seen[a].add(c)
                        presence[a] += 1
                else:
                    negative_signatures.append(signature)
                    if word in positives and contradiction is None:
                        contradiction = {'positive_index': positives[word], 'negative_index': wi}
                    reject = None
                    for a, c in counts.items():
                        poll()
                        if c not in counts_seen[a]:
                            reject = (a, c)
                            break
                    if reject is None:
                        for a in universal:
                            poll()
                            if a not in counts:
                                reject = (a, 0)
                                break
                    if reject is None:
                        unary = False
                    else:
                        unary_certificates.append({'negative_index': wi, 'symbol': reject[0], 'negative_count': reject[1]})
        if contradiction is not None:
            return emit('incompatible', 'contradictory_labels', **contradiction)

        def oneblock():
            rejects = []
            for ni in range(len(N)):
                poll()
                rejects.append({'negative_index': ni, 'rejected_by_block': 0})
            return {'blocks': [list(alphabet)], 'negative_rejections': rejects,
                    'local_language_rule': 'positive_projections_from_input'}

        def coarsenings(atoms, k):
            r = len(atoms)
            if k is None:
                return [list(alphabet)], [list(a) for a in atoms]
            split = r - k + 1
            first, second = [], []
            for i, atom in enumerate(atoms):
                poll()
                if i < split:
                    first.extend(atom)
                else:
                    second.append(list(atom))
            a = [sorted(first)] + second
            # Only used when 1 < k < r, hence split>=2 and second exists.
            merged = []
            for atom in atoms[:split - 1]:
                poll()
                merged.extend(atom)
            merged.extend(atoms[split])
            b = [sorted(merged), list(atoms[split - 1])] + [list(x) for x in atoms[split + 1:]]
            a.sort(); b.sort()
            return a, b

        def unary_witness(blocks):
            rejects = []
            owner = {}
            for bi, block in enumerate(blocks):
                poll()
                for a in block:
                    poll()
                    owner[a] = bi
            for cert in unary_certificates:
                poll()
                rejects.append({'negative_index': cert['negative_index'], 'rejected_by_block': owner[cert['symbol']]})
            return {'blocks': blocks, 'negative_rejections': rejects,
                    'local_language_rule': 'positive_projections_from_input'}

        if known_k == 1:
            return unique('known_k_one_consistent_labels', oneblock())
        if unary:
            atoms = [[a] for a in alphabet]
            proof = {'negative_count_certificates': unary_certificates,
                     'family': 'all_set_partitions' if known_k is None else 'all_set_partitions_with_exactly_known_k_blocks'}
            if m == 1 or known_k == m:
                return unique('unary_all_partitions', unary_witness(atoms), **proof)
            a, b = coarsenings(atoms, known_k)
            return ambiguous('unary_all_partitions', [unary_witness(a), unary_witness(b)], **proof)

        parent = {a: a for a in alphabet}
        def root(a):
            while parent[a] != a:
                poll()
                a = parent[a]
            return a
        edges = []
        negative_groups = {}
        for ni, n in enumerate(N):
            poll()
            negative_groups.setdefault(negative_signatures[ni], []).append((ni, n))
        metrics['graph_pair_universe'] = len(P) * len(N)
        for pi, p in enumerate(P):
            poll()
            bucket = negative_groups.get(positive_signatures[pi], ())
            metrics['graph_pairs_filtered'] += len(N) - len(bucket)
            for ni, n in bucket:
                poll()
                metrics['swap_pairs'] += 1
                if len(p) != len(n):
                    continue
                differences = []
                for i, (a, b) in enumerate(zip(p, n)):
                    if i % 1024 == 0:
                        poll()
                    if a != b:
                        differences.append(i)
                        if len(differences) > 2:
                            break
                if len(differences) != 2 or differences[1] != differences[0] + 1:
                    continue
                i, j = differences
                if p[i] != n[j] or p[j] != n[i] or p[i] == p[j]:
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
        graph_proof = {'forced_atoms': atoms, 'swap_forest': edges}
        if known_k is not None and known_k > r:
            return emit('incompatible', 'forced_atom_count_upper_bound', **graph_proof)
        all_rejected = (1 << len(N)) - 1

        def block_symbols(mask):
            block = []
            for i, atom in enumerate(atoms):
                poll()
                if mask >> i & 1:
                    block.extend(atom)
            return sorted(block)

        def project(word, deletion_table):
            out = []
            for offset in range(0, len(word), COUNT_CHUNK_CHARS):
                poll()
                chunk = word[offset:offset + COUNT_CHUNK_CHARS]
                out.append(chunk.translate(deletion_table))
                metrics['projection_characters'] += len(chunk)
                metrics['projection_chunks'] += 1
                poll()
            value = ''.join(out)
            poll()
            return value

        @lru_cache(maxsize=4096)
        def reject(mask):
            poll()
            allowed = set(block_symbols(mask))
            deletion_table = {}
            for symbol in alphabet:
                poll()
                if symbol not in allowed:
                    deletion_table[ord(symbol)] = None
            metrics['deletion_tables_built'] += 1
            language = set()
            for p in P:
                poll()
                language.add(project(p, deletion_table))
            result = 0
            for ni, n in enumerate(N):
                poll()
                if project(n, deletion_table) not in language:
                    result |= 1 << ni
            metrics['block_masks_computed'] += 1
            return result

        def witness(masks):
            metrics['complete_candidates'] += 1
            covered = 0
            rejections = []
            blocks = []
            for bi, mask in enumerate(masks):
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
            if covered != all_rejected:
                return None
            rejections.sort(key=lambda x: x['negative_index'])
            return {'blocks': blocks, 'negative_rejections': rejections,
                    'local_language_rule': 'positive_projections_from_input'}

        atom_masks = []
        for i in range(r):
            poll()
            atom_masks.append(1 << i)
        atom_witness = witness(atom_masks)
        if atom_witness is not None:
            if r == 1 or known_k == r:
                return unique('compatible_forced_atoms', atom_witness, **graph_proof)
            a, b = coarsenings(atoms, known_k)
            # Exact witness replay for both constructive coarsenings.
            symbol_to_atom = {a: i for i, atom in enumerate(atoms) for a in atom}
            candidates = []
            for part in (a, b):
                masks = []
                for block in part:
                    poll()
                    mask = 0
                    for symbol in block:
                        poll()
                        mask |= 1 << symbol_to_atom[symbol]
                    masks.append(mask)
                candidate = witness(masks)
                if candidate is None:
                    raise AssertionError('coarsening of compatible atoms must be compatible')
                candidates.append(candidate)
            return ambiguous('compatible_forced_atoms', candidates, **graph_proof)
        if known_k == r:
            return emit('incompatible', 'only_forced_atom_partition_rejected', **graph_proof)

        if known_k is None:
            # C006 PROOFS_v1.md T3: any nontrivial compatible coarsening
            # merges to a compatible bipartition. Atom zero stays in side0.
            full_mask = (1 << r) - 1
            split_count = 0
            for tail in range((1 << (r - 1)) - 1):
                poll()
                side0 = 1 | (tail << 1)
                side1 = full_mask ^ side0
                split_count += 1
                metrics['search_nodes'] += 1
                candidate = witness([side0, side1])
                if candidate is not None:
                    metrics['reject_cache_hits'] = reject.cache_info().hits
                    return ambiguous('two_block_search_witness', [oneblock(), candidate],
                                     search_exhausted=False, bipartitions_tested=split_count,
                                     proof_basis='C006-T3-coarsening-to-bipartitions', **graph_proof)
            metrics['reject_cache_hits'] = reject.cache_info().hits
            return unique('exhausted_forced_atom_bipartitions', oneblock(),
                          search_exhausted=True, bipartitions_tested=split_count,
                          proof_basis='C006-T3-coarsening-to-bipartitions', **graph_proof)

        solutions = []
        if known_k is not None:
            metrics['envelope_checks'] = 0
            metrics['envelope_prunes'] = 0
        envelope_proof = ({'envelope_rule': 'growing_blocks_union_remaining_plus_remaining_if_new_block_allowed',
                           'proof_basis': 'C020-exact-reject-monotonic-envelope'}
                          if known_k is not None else {})
        def dfs(pos, masks):
            poll()
            metrics['search_nodes'] += 1
            if len(solutions) == 2:
                return
            remaining = r - pos
            if known_k is not None and (len(masks) > known_k or len(masks) + remaining < known_k):
                return
            if pos == r:
                candidate = witness(masks)
                if candidate is not None:
                    solutions.append(candidate)
                return
            if known_k is not None:
                metrics['envelope_checks'] += 1
                unassigned = ((1 << r) - 1) ^ ((1 << pos) - 1)
                envelope = 0
                for mask in masks:
                    poll()
                    envelope |= reject(mask | unassigned)
                if len(masks) < known_k:
                    poll()
                    envelope |= reject(unassigned)
                if envelope != all_rejected:
                    metrics['envelope_prunes'] += 1
                    return
            bit = 1 << pos
            for i in range(len(masks)):
                poll()
                masks[i] |= bit
                dfs(pos + 1, masks)
                masks[i] ^= bit
                if len(solutions) == 2:
                    return
            masks.append(bit)
            dfs(pos + 1, masks)
            masks.pop()
        dfs(0, [])
        metrics['reject_cache_hits'] = reject.cache_info().hits
        if len(solutions) == 2:
            return ambiguous('two_exact_search_witnesses', solutions, **graph_proof)
        if len(solutions) == 1:
            return unique('exhausted_all_forced_atom_coarsenings', solutions[0], search_exhausted=True, **envelope_proof, **graph_proof)
        return emit('incompatible', 'exhausted_all_forced_atom_coarsenings', search_exhausted=True, **envelope_proof, **graph_proof)
    except BadInput as exc:
        return {**base, 'status': 'invalid_input', 'error': str(exc),
                'findings': {'data_insufficient': None, 'computation_incomplete': False}}
    except (Halt, KeyboardInterrupt, RecursionError, MemoryError) as exc:
        return {**base, 'status': 'unresolved', 'reason': type(exc).__name__,
                'findings': {'data_insufficient': None, 'computation_incomplete': True}}
    finally:
        metrics['solver_seconds'] = time.perf_counter() - start
