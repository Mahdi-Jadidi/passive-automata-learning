"""C005 sparse known-k finite-q certificate. Stdlib only.
Helper functions adapted verbatim from C004 singleton_solver_v1.py;
solve adapted from C004 bounded_certificate_v1.py. All dependencies in this file.
No general regular-language inference: local_word_cap must be a finite integer.
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



def graph_certificate(adjacency, k, deadline=None):
    """Return a replayable unique-color certificate, or None (abstention).

    Input is a simple undirected adjacency dictionary. A bounded greedy anchor
    search is deliberately incomplete: try each vertex as root, then greedily
    extend by highest remaining degree. Anchor failure is never infeasibility.
    """
    vertices = sorted(adjacency)
    if isinstance(k, bool) or not isinstance(k, int) or not 1 <= k <= len(vertices):
        raise ValueError('k out of range')
    for a in vertices:
        check(deadline)
        if a in adjacency[a] or any(b not in adjacency or a not in adjacency[b] for b in adjacency[a]):
            raise ValueError('adjacency must be simple and undirected')
    anchor = None
    for root in sorted(vertices, key=lambda a: (-len(adjacency[a]), a)):
        check(deadline)
        chosen, remaining = [root], set(adjacency[root])
        while len(chosen) < k and remaining:
            check(deadline)
            nxt = min(remaining, key=lambda a: (-len(adjacency[a] & remaining), a))
            chosen.append(nxt)
            remaining.intersection_update(adjacency[nxt])
        if len(chosen) == k:
            anchor = chosen
            break
    if anchor is None:
        return None
    colors = {a:i for i,a in enumerate(anchor)}
    steps = []
    while len(colors) < len(vertices):
        progress = False
        for a in vertices:
            check(deadline)
            if a in colors:
                continue
            witnesses = {}
            for b in sorted(adjacency[a]):
                if b in colors:
                    witnesses.setdefault(colors[b], b)
            if len(witnesses) == k - 1:
                color = next(c for c in range(k) if c not in witnesses)
                colors[a] = color
                steps.append({'vertex':a,'color':color,
                              'neighbor_by_excluded_color':{str(c):b for c,b in sorted(witnesses.items())}})
                progress = True
        if not progress:
            return None
    # Contradictory forced assignments do not become positive certificates.
    if any(colors[a] == colors[b] for a in vertices for b in adjacency[a]):
        return None
    blocks = sorted([sorted(a for a in vertices if colors[a] == c) for c in range(k)])
    return {'kind':'k_clique_anchor_forced_colors','anchor':anchor,'steps':steps,
            'blocks':blocks,'unique_q_opposition_coloring':True}


def certificate_partition(alphabet, adjacency, k, deadline):
    cert = graph_certificate(adjacency, k, deadline)
    return (None, None) if cert is None else (cert['blocks'], cert['kind'])

def solve(data, *, k=None, local_word_cap=2, deadline=None, max_solutions=1):
    """Certificate-only bounded finite-language solve; no-positive unresolved.

    local_word_cap is an integer >=1; this is AT MOST q, so empty languages
    are allowed. max_solutions is a positive integer or None; at most one
    certified solution is emitted. deadline is absolute perf_counter time.
    """
    if (isinstance(local_word_cap, bool) or not isinstance(local_word_cap, int)
            or local_word_cap < 1):
        raise ValueError('local_word_cap must be a positive integer')
    if max_solutions is not None and (isinstance(max_solutions, bool) or
            not isinstance(max_solutions, int) or max_solutions < 1):
        raise ValueError('max_solutions must be a positive integer or None')
    if deadline is not None:
        if isinstance(deadline, bool) or not isinstance(deadline, (int,float)):
            raise ValueError('deadline must be finite perf_counter time')
        try:
            finite = math.isfinite(deadline)
        except OverflowError:
            finite = False
        if not finite:
            raise ValueError('deadline must be finite perf_counter time')
    started = time.perf_counter()
    q = local_word_cap
    resolved_k = k
    solutions = []
    graph = {'symbols':[], 'edges':[], 'edge_witnesses':[], 'construction_complete':False,
             'edge_rule':'strictly_more_than_q_distinct_positive_pair_projections', 'q':q,
             'positive_order':'sorted unique input words'}
    metrics = {'pair_bucket_appends':0, 'pair_tests':0, 'candidate_checks':0,
               'positive_projection_checks':0, 'negative_checks':0,
               'stored_pair_projection_values':0}

    def result(status, reason, exhausted=False, decision=False, uniqueness='unknown', certificate=None):
        if status != 'incomplete':
            check(deadline)
        return {'method':'sparse-q-opposition-v1', 'model_class':'bounded_finite_projection_languages',
                'k':resolved_k, 'local_word_cap':q, 'status':status, 'reason':reason,
                'solutions':solutions, 'search_exhausted':exhausted, 'decision_complete':decision,
                'uniqueness':uniqueness,
                'uniqueness_scope':'unordered_exactly_k_nonempty_blocks_at_most_q_local_words',
                'assumptions':['known_k_disjoint_nonempty_alphabet_blocks', 'at_most_q_local_words',
                               'complete_positive_words', 'exact_noise_free_labels',
                               'q_opposition_unique_coloring_certificate'],
                'graph':graph, 'certificate':certificate,
                'metrics':dict(metrics,provider_seconds=time.perf_counter()-started)}
    try:
        check(deadline)
        alphabet, positive, negative, resolved_k = validate(data,k,deadline)
        graph['symbols'] = alphabet
        metrics.update(alphabet_size=len(alphabet),positive_count=len(positive),
                       negative_count=len(negative),total_input_length=sum(map(len,positive))+sum(map(len,negative)))
        if not positive:
            return result('insufficient_coverage','no_positive_q_opposition_evidence')
        # Unary counts are images of local words; >q counts refute every owner.
        unary_owner = {a:i for i,a in enumerate(alphabet)}
        unary_values = {a:{} for a in alphabet}
        for index, word in enumerate(positive):
            unary = projections(word,unary_owner,len(alphabet),deadline)
            for a in alphabet:
                check(deadline)
                unary_values[a].setdefault(len(unary[unary_owner[a]]),index)
                if len(unary_values[a]) > q:
                    return result('infeasible','more_than_q_positive_unary_counts',True,True,'none',
                                  {'kind':'unary_q_violation','symbol':a,
                                   'counts':list(unary_values[a]),
                                   'positive_indices':list(unary_values[a].values())})
        pairs = [(a,b) for i,a in enumerate(alphabet) for b in alphabet[i+1:]]
        incidence = {a:[] for a in alphabet}
        for p in pairs:
            check(deadline)
            for a in p:
                incidence[a].append(p)
        # Each per-pair dictionary has at most q+1 entries, retaining the first
        # positive index for a checkable edge. No threshold-one test is used.
        values = {p:{} for p in pairs}
        adjacency = {a:set() for a in alphabet}
        for index, word in enumerate(positive):
            images = pair_projections(word,incidence,pairs,deadline,metrics)
            for p in pairs:
                check(deadline)
                metrics['pair_tests'] += 1
                observed = values[p]
                if len(observed) > q:
                    continue
                observed.setdefault(images[p],index)
                if len(observed) > q:
                    a,b = p
                    adjacency[a].add(b)
                    adjacency[b].add(a)
                    graph['edges'].append([a,b])
                    graph['edge_witnesses'].append({'symbols':[a,b],
                        'positive_indices':list(observed.values()),
                        'pair_projections':list(observed)})
        graph['construction_complete'] = True
        metrics['stored_pair_projection_values'] = sum(map(len,values.values()))
        metrics['opposition_seconds'] = time.perf_counter()-started
        graph_cert = graph_certificate(adjacency,resolved_k,deadline)
        blocks,kind = (None,None) if graph_cert is None else (graph_cert['blocks'],graph_cert['kind'])
        if blocks is None:
            return result('insufficient_coverage','no_complete_anchor_forcing_certificate')
        owner = {a:i for i,block in enumerate(blocks) for a in block}
        languages = [set() for _ in blocks]
        metrics['candidate_checks'] += 1
        certificate = dict(graph_cert, **{'q':q})
        certificate.update({'kind':'q_'+kind, 'q':q, 'blocks':blocks,
                       'unique_q_opposition_coloring':True})
        for index,word in enumerate(positive):
            images = projections(word,owner,resolved_k,deadline)
            metrics['positive_projection_checks'] += 1
            for side,image in enumerate(images):
                check(deadline)
                languages[side].add(image)
                if len(languages[side]) > q:
                    certificate.update(offending_block_index=side,
                                       distinct_positive_projections=sorted(languages[side]))
                    return result('infeasible','forced_candidate_exceeds_q_full_block_words',
                                  True,True,'none',certificate)
        witnesses = []
        for word in negative:
            metrics['negative_checks'] += 1
            images = projections(word,owner,resolved_k,deadline)
            unseen = [i for i in range(resolved_k) if images[i] not in languages[i]]
            if not unseen:
                certificate['accepted_negative'] = word
                return result('infeasible','forced_candidate_accepts_negative',True,True,'none',certificate)
            i = unseen[0]
            witnesses.append({'negative':word,'block_index':i,'projection':images[i],
                              'all_unseen_block_indices':unseen})
        solutions.append({'blocks':blocks,'positive_projection_languages':[sorted(x) for x in languages],
                          'negative_witnesses':witnesses})
        return result('found','unique_bounded_language_partition_certified',True,True,'unique',certificate)
    except (Interrupted,KeyboardInterrupt):
        return result('incomplete','deadline_or_interruption',decision=bool(solutions))

if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('--k', type=int)
    parser.add_argument('--local-word-cap', type=int, default=2)
    parser.add_argument('--seconds', type=float)
    parser.add_argument('--max-solutions', type=int, default=2)
    args = parser.parse_args()
    with open(args.input, encoding='utf-8-sig') as handle:
        data = json.load(handle)
    deadline = None if args.seconds is None else time.perf_counter() + args.seconds
    print(json.dumps(solve(data,k=args.k,local_word_cap=args.local_word_cap,
                           deadline=deadline,max_solutions=args.max_solutions),ensure_ascii=False))