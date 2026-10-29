"""C004-QOP001 prepared: known-k, at-most-q local-word certificate.

Not singleton opposition: an edge requires >q different positive binary
projections. Graph certificate forces ownership; full block cap and negative
checks are still mandatory. Sibling v1 helpers have no model-specific tests.
"""
import math
import time
from singleton_solver_v1 import (validate, check, projections, pair_projections,
                                 certificate_partition, Interrupted)


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
        return {'method':'bounded-q-opposition-v1', 'model_class':'bounded_finite_projection_languages',
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
        blocks,kind = certificate_partition(alphabet,adjacency,resolved_k,deadline)
        if blocks is None:
            return result('insufficient_coverage','no_supported_unique_q_opposition_coloring')
        owner = {a:i for i,block in enumerate(blocks) for a in block}
        languages = [set() for _ in blocks]
        metrics['candidate_checks'] += 1
        certificate = {'kind':'q_'+kind, 'q':q, 'blocks':blocks,
                       'unique_q_opposition_coloring':True}
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
