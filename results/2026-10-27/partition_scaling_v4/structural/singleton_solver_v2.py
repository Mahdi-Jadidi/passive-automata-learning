"""C004 S002 candidate: exact constrained-coloring fallback (Stage 2).

Prepared while awaiting Stage 1 acceptance; do not benchmark until master go.
Imports immutable singleton_solver_v1, which must also be capture-snapshotted.
"""
import time
from singleton_solver_v1 import solve as certificate_solve, check, validate, projections, Interrupted


def solve(data, *, k=None, deadline=None, max_solutions=1):
    """As v1, with exact canonical coloring on unsupported sparse graphs.

    max_solutions=None exhausts all partitions. A finite limit stops after that
    many solutions, conservatively leaving uniqueness/exhaustion unknown.
    No-positive cases remain insufficient_coverage under exactly-one semantics.
    """
    started = time.perf_counter()
    result = certificate_solve(data, k=k, deadline=deadline, max_solutions=max_solutions)
    result['method'] = 'singleton-opposition-v2'
    result['assumptions'] = [a for a in result['assumptions'] if a != 'certificate_only_stage1']
    result['assumptions'].append('exact_constrained_coloring_fallback')
    if result['status'] != 'insufficient_coverage' or not data['positive']:
        return result
    solutions = result['solutions']
    metrics = result['metrics']
    metrics.update(search_nodes=0, colorings_completed=0, negative_prunes=0)
    stopped = False
    try:
        alphabet, positive, negative, resolved_k = validate(data, k, deadline)
        adjacency = {a: set() for a in alphabet}
        for a, b in result['graph']['edges']:
            check(deadline)
            adjacency[a].add(b)
            adjacency[b].add(a)
        labels = []

        def search(highest):
            nonlocal stopped
            check(deadline)
            metrics['search_nodes'] += 1
            pos = len(labels)
            remaining = len(alphabet)-pos
            if highest+1+remaining < resolved_k:
                return
            if pos == len(alphabet):
                if highest+1 != resolved_k:
                    return
                metrics['colorings_completed'] += 1
                blocks = [[a for a, c in zip(alphabet, labels) if c == color]
                          for color in range(resolved_k)]
                owner = {a: c for a, c in zip(alphabet, labels)}
                words = projections(positive[0], owner, resolved_k, deadline)
                for word in positive:
                    metrics['positive_projection_checks'] += 1
                    if projections(word, owner, resolved_k, deadline) != words:
                        raise AssertionError('positive coloring equivalence violated')
                witnesses = []
                for word in negative:
                    metrics['negative_checks'] += 1
                    images = projections(word, owner, resolved_k, deadline)
                    unseen = [i for i in range(resolved_k) if images[i] != words[i]]
                    if not unseen:
                        metrics['negative_prunes'] += 1
                        return
                    i = unseen[0]
                    witnesses.append({'negative': word, 'block_index': i, 'projection': images[i],
                                      'all_unseen_block_indices': unseen})
                solutions.append({'blocks': blocks, 'local_words': words,
                                  'positive_projection_languages': [[w] for w in words],
                                  'negative_witnesses': witnesses})
                if max_solutions is not None and len(solutions) >= max_solutions:
                    stopped = True
                return
            a = alphabet[pos]
            for color in range(min(highest+1, resolved_k-1)+1):
                check(deadline)
                if any(labels[j] == color and alphabet[j] in adjacency[a] for j in range(pos)):
                    continue
                labels.append(color)
                search(max(highest, color))
                labels.pop()
                if stopped:
                    return

        search(-1)
        exhausted = not stopped
        result.update(status='found' if solutions else 'infeasible',
                      reason='exact_constrained_coloring', search_exhausted=exhausted,
                      decision_complete=bool(solutions) or exhausted,
                      uniqueness=('unique' if len(solutions) == 1 else 'multiple' if len(solutions)>1 else 'none')
                      if exhausted else ('multiple' if len(solutions)>1 else 'unknown'),
                      certificate={'kind': 'exact_coloring_exhaustion' if exhausted else 'solution_limit',
                                   'colorings_completed': metrics['colorings_completed']})
    except (Interrupted, KeyboardInterrupt):
        result.update(status='incomplete', reason='deadline_or_interruption',
                      search_exhausted=False, decision_complete=bool(solutions),
                      uniqueness='multiple' if len(solutions)>1 else 'unknown', certificate=None)
    metrics['provider_seconds'] = time.perf_counter()-started
    return result
