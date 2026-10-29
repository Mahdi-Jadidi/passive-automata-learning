"""C004 S001: known-k singleton products; certificate-only Stage 1.

No target queries, truth sidecars, or non-standard imports. Sparse evidence is
unresolved rather than infeasible. deadline is absolute time.perf_counter().
"""
import math
import time


class Interrupted(Exception):
    pass


def check(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise Interrupted()


def projections(word, owner, count, deadline):
    buckets = [[] for _ in range(count)]
    for pos, a in enumerate(word):
        if pos % 256 == 0:
            check(deadline)
        buckets[owner[a]].append(a)
    return [''.join(x) for x in buckets]


def pair_projections(word, incidence, pairs, deadline, metrics):
    buckets = {p: [] for p in pairs}
    for pos, a in enumerate(word):
        if pos % 256 == 0:
            check(deadline)
        for p in incidence[a]:
            buckets[p].append(a)
        metrics['pair_bucket_appends'] += len(incidence[a])
    out = {}
    for p, value in buckets.items():
        check(deadline)
        out[p] = ''.join(value)
    return out


def validate(data, k, deadline):
    if not isinstance(data, dict):
        raise ValueError('data must be an object')
    alphabet = data.get('alphabet')
    if (not isinstance(alphabet, list) or not alphabet or
            any(not isinstance(a, str) or len(a) != 1 for a in alphabet) or
            len(set(alphabet)) != len(alphabet)):
        raise ValueError('alphabet must list distinct one-character strings')
    alphabet = sorted(alphabet)
    k = data.get('k', 2) if k is None else k
    if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= len(alphabet):
        raise ValueError('k must be an integer from 1 through alphabet size')
    allowed = set(alphabet)
    classes = []
    for key in ['positive', 'negative']:
        words = data.get(key)
        if not isinstance(words, list):
            raise ValueError(key + ' must list words')
        for word in words:
            check(deadline)
            if not isinstance(word, str):
                raise ValueError(key + ' must list words')
            for i, a in enumerate(word):
                if i % 256 == 0:
                    check(deadline)
                if a not in allowed:
                    raise ValueError('symbol outside alphabet')
        classes.append(sorted(set(words)))
    if set(classes[0]) & set(classes[1]):
        raise ValueError('conflicting labels')
    return alphabet, classes[0], classes[1], k


def certificate_partition(alphabet, adjacency, k, deadline):
    # Complement components are candidates for multipartite blocks. Verify all
    # pairs explicitly; connected complement components alone are insufficient.
    remaining = set(alphabet)
    blocks = []
    while remaining:
        root = min(remaining)
        remaining.remove(root)
        component, queue = [root], [root]
        for a in queue:
            check(deadline)
            others = [b for b in sorted(remaining) if b not in adjacency[a]]
            for b in others:
                remaining.remove(b)
                component.append(b)
                queue.append(b)
        blocks.append(sorted(component))
    owner = {a: i for i, block in enumerate(blocks) for a in block}
    complete = len(blocks) == k
    for i, a in enumerate(alphabet):
        check(deadline)
        for b in alphabet[i+1:]:
            if (b in adjacency[a]) != (owner[a] != owner[b]):
                complete = False
    if complete:
        return blocks, 'complete_k_partite_opposition'
    if k != 2:
        return None, None
    colors, queue = {alphabet[0]: 0}, [alphabet[0]]
    for a in queue:
        check(deadline)
        for b in sorted(adjacency[a]):
            if b not in colors:
                colors[b] = 1 - colors[a]
                queue.append(b)
            elif colors[b] == colors[a]:
                return None, None
    if len(colors) == len(alphabet) and set(colors.values()) == {0, 1}:
        return [[a for a in alphabet if colors[a] == c] for c in [0, 1]], 'connected_bipartite_opposition'
    return None, None


def solve(data, *, k=None, deadline=None, max_solutions=1):
    """Certify at most one partition. max_solutions positive int or None.

    No-positive samples return insufficient_coverage: singleton-exactly-one
    semantics require factors which are not determined by observed positives.
    """
    if max_solutions is not None and (isinstance(max_solutions, bool) or
            not isinstance(max_solutions, int) or max_solutions < 1):
        raise ValueError('max_solutions must be positive integer or None')
    if deadline is not None and (isinstance(deadline, bool) or
            not isinstance(deadline, (int, float)) or not math.isfinite(deadline)):
        raise ValueError('deadline must be finite perf_counter time')
    started = time.perf_counter()
    metrics = {'pair_bucket_appends': 0, 'pair_tests': 0, 'candidate_checks': 0,
               'search_nodes': 0, 'positive_projection_checks': 0, 'negative_checks': 0}
    graph = {'symbols': [], 'edges': [], 'edge_positive_indices': [], 'construction_complete': False}
    solutions = []
    resolved_k = k

    def result(status, reason, exhausted=False, decision=False, unique='unknown', certificate=None):
        if status != 'incomplete':
            check(deadline)
        return {'method': 'singleton-opposition-v1', 'model_class': 'fixed_word_product',
                'k': resolved_k, 'status': status, 'reason': reason, 'solutions': solutions,
                'search_exhausted': exhausted, 'decision_complete': decision,
                'uniqueness': unique, 'uniqueness_scope': 'unordered_exactly_k_nonempty_blocks_singleton_word_factors',
                'assumptions': ['known_k_disjoint_nonempty_alphabet_blocks',
                                'exactly_one_word_per_local_language', 'complete_positive_words',
                                'exact_noise_free_labels', 'certificate_only_stage1'],
                'graph': graph, 'certificate': certificate,
                'metrics': dict(metrics, provider_seconds=time.perf_counter()-started)}
    try:
        check(deadline)
        alphabet, positive, negative, resolved_k = validate(data, k, deadline)
        metrics.update(alphabet_size=len(alphabet), positive_count=len(positive), negative_count=len(negative),
                       total_input_length=sum(map(len, positive))+sum(map(len, negative)))
        graph['symbols'] = alphabet
        graph['positive_order'] = 'sorted unique input words'
        graph['reference_positive_index'] = 0
        if not positive:
            return result('insufficient_coverage', 'no_positive_word_determines_local_words')
        owner = {a: i for i, a in enumerate(alphabet)}
        reference_counts = projections(positive[0], owner, len(alphabet), deadline)
        for i, word in enumerate(positive[1:], 1):
            counts = projections(word, owner, len(alphabet), deadline)
            if counts != reference_counts:
                return result('infeasible', 'positive_symbol_count_inconsistency', True, True,
                              certificate={'kind': 'count_inconsistency', 'positive_indices': [0, i]})
        pairs = [(a, b) for i, a in enumerate(alphabet) for b in alphabet[i+1:]]
        incidence = {a: [] for a in alphabet}
        for p in pairs:
            check(deadline)
            for a in p:
                incidence[a].append(p)
        reference = pair_projections(positive[0], incidence, pairs, deadline, metrics)
        adjacency = {a: set() for a in alphabet}
        for index, word in enumerate(positive[1:], 1):
            other = pair_projections(word, incidence, pairs, deadline, metrics)
            for p in pairs:
                check(deadline)
                metrics['pair_tests'] += 1
                if other[p] != reference[p] and p[1] not in adjacency[p[0]]:
                    a, b = p
                    adjacency[a].add(b)
                    adjacency[b].add(a)
                    graph['edges'].append([a, b])
                    graph['edge_positive_indices'].append(index)
        graph['construction_complete'] = True
        metrics['opposition_seconds'] = time.perf_counter()-started
        blocks, kind = certificate_partition(alphabet, adjacency, resolved_k, deadline)
        if blocks is None:
            return result('insufficient_coverage', 'no_supported_unique_coloring_certificate')
        metrics['candidate_checks'] += 1
        block_owner = {a: i for i, block in enumerate(blocks) for a in block}
        local_words = projections(positive[0], block_owner, resolved_k, deadline)
        certificate = {'kind': kind, 'blocks': blocks, 'local_words': local_words,
                       'unique_positive_partition': True}
        for word in positive:
            metrics['positive_projection_checks'] += 1
            if projections(word, block_owner, resolved_k, deadline) != local_words:
                return result('infeasible', 'unique_candidate_positive_conflict', True, True,
                              certificate=certificate)
        witnesses = []
        for word in negative:
            metrics['negative_checks'] += 1
            images = projections(word, block_owner, resolved_k, deadline)
            unseen = [i for i in range(resolved_k) if images[i] != local_words[i]]
            if not unseen:
                certificate['accepted_negative'] = word
                return result('infeasible', 'unique_candidate_accepts_negative', True, True,
                              certificate=certificate)
            i = unseen[0]
            witnesses.append({'negative': word, 'block_index': i, 'projection': images[i],
                              'all_unseen_block_indices': unseen})
        solutions.append({'blocks': blocks, 'local_words': local_words,
                          'positive_projection_languages': [[w] for w in local_words],
                          'negative_witnesses': witnesses})
        return result('found', 'unique_partition_certified', True, True, 'unique', certificate)
    except (Interrupted, KeyboardInterrupt):
        return result('incomplete', 'deadline_or_interruption', decision=bool(solutions))
