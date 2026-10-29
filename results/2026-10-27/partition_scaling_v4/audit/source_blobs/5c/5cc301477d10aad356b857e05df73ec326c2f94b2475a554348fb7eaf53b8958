"""C004 S003 v4: unknown-k certificate, preserving base interruption status.

infer_k=False delegates to v2. infer_k=True requires a nonempty positive set
and a clique on contextual-swap must-link components. Otherwise unresolved.
Every imported source (v1,v2,v3) must be capture-snapshotted.
"""
import time
from singleton_solver_v1 import solve as certificate_solve, check, projections, Interrupted
from singleton_solver_v2 import solve as known_solve


def solve(data, *, k=None, deadline=None, max_solutions=1, infer_k=False):
    if not isinstance(infer_k, bool):
        raise ValueError('infer_k must be boolean')
    if not infer_k:
        return known_solve(data, k=k, deadline=deadline, max_solutions=max_solutions)
    if k is not None:
        raise ValueError('explicit k and infer_k are mutually exclusive')
    started = time.perf_counter()
    # Reuse validated inputs/count checks/opposition extraction. k=1 is only a
    # preprocessing request; no conclusion from its certificate is transferred.
    result = certificate_solve(data, k=1, deadline=deadline, max_solutions=max_solutions)
    base_interrupted = result['status'] == 'incomplete'
    result.update(method='singleton-opposition-v4-unknown-k', k=None, solutions=[],
                  status='insufficient_coverage', reason='unknown_k_certificate_unresolved',
                  search_exhausted=False, decision_complete=False, uniqueness='unknown',
                  uniqueness_scope='unordered_partitions_any_positive_k_singleton_word_factors',
                  certificate=None)
    result['assumptions'] = ['disjoint_nonempty_alphabet_blocks', 'exactly_one_word_per_local_language',
                             'complete_positive_words', 'exact_noise_free_labels',
                             'contextual_adjacent_swap_must_links_and_quotient_opposition_clique']
    metrics = result['metrics']
    metrics.update(swap_pair_checks=0, must_link_edges=0)
    if base_interrupted:
        result.update(status='incomplete', reason='deadline_or_interruption')
        metrics['provider_seconds'] = time.perf_counter()-started
        return result
    try:
        check(deadline)
        alphabet = result['graph']['symbols']
        positive = sorted(set(data['positive']))
        negative = sorted(set(data['negative']))
        if not positive or not result['graph']['construction_complete']:
            # Incomplete construction includes count conflict, checked afresh
            # so an unfinished preprocessing stage never certifies infeasibility.
            if positive:
                owner = {a:i for i,a in enumerate(alphabet)}
                counts = projections(positive[0], owner, len(alphabet), deadline)
                for i, word in enumerate(positive[1:], 1):
                    if projections(word, owner, len(alphabet), deadline) != counts:
                        result.update(status='infeasible', reason='positive_symbol_count_inconsistency',
                                      search_exhausted=True, decision_complete=True,
                                      uniqueness='none', certificate={'kind':'count_inconsistency',
                                                                     'positive_indices':[0,i]})
                        return result
            return result
        parent = {a:a for a in alphabet}

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        links = []
        for pi, p in enumerate(positive):
            for ni, n in enumerate(negative):
                check(deadline)
                metrics['swap_pair_checks'] += 1
                if len(p) != len(n):
                    continue
                differing = []
                for pos, (a,b) in enumerate(zip(p,n)):
                    if pos % 256 == 0:
                        check(deadline)
                    if a != b:
                        differing.append(pos)
                        if len(differing)>2:
                            break
                if (len(differing) != 2 or differing[1] != differing[0]+1):
                    continue
                j = differing[0]
                if p[j] != n[j+1] or p[j+1] != n[j]:
                    continue
                a,b = p[j:j+2]
                ra,rb = find(a),find(b)
                if ra != rb:
                    parent[max(ra,rb)] = min(ra,rb)
                links.append({'symbols':[a,b], 'positive_index':pi, 'negative_index':ni,
                              'swap_position':j})
        metrics['must_link_edges'] = len(links)
        components = {}
        for a in alphabet:
            components.setdefault(find(a),[]).append(a)
        blocks = sorted(components.values())
        owner = {a:i for i,block in enumerate(blocks) for a in block}
        quotient = set()
        for a,b in result['graph']['edges']:
            check(deadline)
            i,j = owner[a],owner[b]
            if i == j:
                result.update(status='infeasible', reason='opposition_inside_forced_component',
                              search_exhausted=True, decision_complete=True, uniqueness='none',
                              certificate={'kind':'must_link_opposition_conflict', 'must_links':links,
                                           'components':blocks, 'opposition_edge':[a,b]})
                return result
            quotient.add(tuple(sorted((i,j))))
        c = len(blocks)
        certificate = {'kind':'must_link_quotient_clique', 'must_links':links, 'components':blocks,
                       'positive_order':'sorted unique input words',
                       'negative_order':'sorted unique input words',
                       'quotient_edges':[list(x) for x in sorted(quotient)]}
        result['certificate'] = certificate
        if len(quotient) != c*(c-1)//2:
            return result
        words = projections(positive[0],owner,c,deadline)
        for word in positive:
            check(deadline)
            if projections(word,owner,c,deadline) != words:
                result.update(status='infeasible', reason='forced_partition_positive_conflict',
                              search_exhausted=True, decision_complete=True, uniqueness='none')
                return result
        witnesses = []
        for word in negative:
            images = projections(word,owner,c,deadline)
            unseen = [i for i in range(c) if images[i] != words[i]]
            if not unseen:
                certificate['accepted_negative'] = word
                result.update(status='infeasible', reason='forced_partition_accepts_negative',
                              search_exhausted=True, decision_complete=True, uniqueness='none')
                return result
            i = unseen[0]
            witnesses.append({'negative':word, 'block_index':i, 'projection':images[i],
                              'all_unseen_block_indices':unseen})
        result.update(k=c, status='found', reason='unique_unknown_k_singleton_partition_certified',
                      search_exhausted=True, decision_complete=True, uniqueness='unique',
                      solutions=[{'blocks':blocks, 'local_words':words,
                                  'positive_projection_languages':[[w] for w in words],
                                  'negative_witnesses':witnesses}])
        check(deadline)
    except (Interrupted, KeyboardInterrupt):
        result.update(status='incomplete', reason='deadline_or_interruption', search_exhausted=False,
                      decision_complete=bool(result['solutions']), uniqueness='unknown', certificate=None)
    finally:
        metrics['provider_seconds'] = time.perf_counter()-started
    return result
