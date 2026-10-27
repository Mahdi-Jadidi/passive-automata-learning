"""C003 graph-quotient continuing search; no optional dependencies."""
import importlib.util
from pathlib import Path
import time


class Interrupted(Exception):
    pass


def check(deadline):
    if deadline is not None and time.perf_counter() >= deadline:
        raise Interrupted()


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('input must be an object')
    alphabet = data.get('alphabet')
    if (not isinstance(alphabet, list) or len(alphabet) < 2
            or any(not isinstance(a, str) or len(a) != 1 for a in alphabet)
            or len(set(alphabet)) != len(alphabet)):
        raise ValueError('alphabet must contain at least two distinct one-character strings')
    sigma = set(alphabet)
    samples = []
    for name in ('positive', 'negative'):
        words = data.get(name)
        if not isinstance(words, list) or any(not isinstance(w, str) for w in words):
            raise ValueError(name + ' must be a list of strings')
        if any(set(w) - sigma for w in words):
            raise ValueError(name + ' contains unknown symbols')
        samples.append(sorted(set(words)))
    if set(samples[0]) & set(samples[1]):
        raise ValueError('contradictory labels')
    return sorted(alphabet), *samples


def project(word, block):
    return ''.join(a for a in word if a in block)


def graph(alphabet, positive, negative):
    path = Path(__file__).resolve().parents[2] / 'partition_constraints_v2/baseline/partition_solver.py'
    spec = importlib.util.spec_from_file_location('c003_readonly_graph', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.witness_graph(alphabet, positive, negative)


def direct(blocks, positive, negative, deadline):
    matches = [{}, {}]
    for side in (0, 1):
        for p in positive:
            check(deadline)
            matches[side].setdefault(project(p, blocks[side]), p)
    witnesses = []
    for n in negative:
        check(deadline)
        projections = [project(n, block) for block in blocks]
        unseen = [s for s in (0, 1) if projections[s] not in matches[s]]
        if not unseen:
            return None, (n, matches[0][projections[0]], matches[1][projections[1]])
        witnesses.append(dict(negative=n, block_index=unseen[0],
                              projection=projections[unseen[0]],
                              all_unseen_block_indices=unseen))
    return dict(blocks=[sorted(b) for b in blocks],
                positive_projection_languages=[sorted(m) for m in matches],
                negative_witnesses=witnesses), None


def family(alphabet, owner, n, p, deadline):
    terms = set()
    differing = {a for a in alphabet if n.count(a) != p.count(a)}
    for a in differing:
        terms.add((owner[a],))
    for i, a in enumerate(alphabet):
        check(deadline)
        for b in alphabet[i+1:]:
            if a in differing or b in differing:
                continue
            if project(n, {a, b}) != project(p, {a, b}):
                terms.add(tuple(sorted({owner[a], owner[b]})))
    return tuple(sorted(terms))


def cut_value(cut, prefix):
    unknown = False
    for side, terms in enumerate(cut):
        for term in terms:
            values = [prefix[i] if i < len(prefix) else -1 for i in term]
            if all(value == side for value in values):
                return True
            if all(value in (-1, side) for value in values):
                unknown = True
    return None if unknown else False


def search(data, *, deadline=None, max_solutions=1, learn=True):
    started = time.perf_counter()
    alphabet, positive, negative = validate(data)
    if max_solutions is not None and (isinstance(max_solutions, bool)
            or not isinstance(max_solutions, int) or max_solutions < 1):
        raise ValueError('max_solutions must be a positive integer or None')
    metrics = dict(graph_components=None, nodes=0, leaves=0, cuts=0,
                   pruned_nodes=0, preprocessing_seconds=0.0,
                   separation_seconds=0.0, cut_generation_seconds=0.0)
    solutions, cuts, cached = [], [], {}
    components, edges, stack = [], [], []
    interrupted, exhausted = False, False
    try:
        check(deadline)
        components, edges = graph(alphabet, positive, negative)
        check(deadline)
        metrics['graph_components'] = len(components)
        owner = {a: i for i, block in enumerate(components) for a in block}
        metrics['preprocessing_seconds'] = time.perf_counter() - started
        stack = [(0,)]
        while stack:
            check(deadline)
            prefix = stack.pop()
            metrics['nodes'] += 1
            rejected = False
            for cut in cuts:
                check(deadline)
                if cut_value(cut, prefix) is False:
                    rejected = True
                    break
            if rejected:
                metrics['pruned_nodes'] += 1
                continue
            if len(prefix) < len(components):
                stack.append(prefix + (1,))
                stack.append(prefix + (0,))
                continue
            if 1 not in prefix:
                continue
            metrics['leaves'] += 1
            blocks = [{a for a in alphabet if prefix[owner[a]] == s} for s in (0, 1)]
            clock = time.perf_counter()
            record, offending = direct(blocks, positive, negative, deadline)
            metrics['separation_seconds'] += time.perf_counter() - clock
            if record is not None:
                solutions.append(record)
                if max_solutions is not None and len(solutions) >= max_solutions:
                    exhausted = not stack
                    break
            elif learn:
                clock = time.perf_counter()
                n, p0, p1 = offending
                terms = []
                for p in (p0, p1):
                    check(deadline)
                    if (n, p) not in cached:
                        cached[n, p] = family(alphabet, owner, n, p, deadline)
                    terms.append(cached[n, p])
                cut = tuple(terms)
                if cut_value(cut, prefix) is not False:
                    raise AssertionError('learned cut does not exclude its source candidate')
                cuts.append(cut)
                metrics['cuts'] += 1
                metrics['cut_generation_seconds'] += time.perf_counter() - clock
        else:
            exhausted = True
    except (Interrupted, KeyboardInterrupt):
        interrupted = True
    if not metrics['preprocessing_seconds']:
        metrics['preprocessing_seconds'] = time.perf_counter() - started
    metrics['provider_seconds'] = time.perf_counter() - started
    return dict(method='general' if learn else 'fair-reference',
                model_class='general_regular_product',
                status='incomplete' if interrupted else 'found' if solutions else 'infeasible',
                solutions=solutions, search_exhausted=exhausted,
                decision_complete=bool(solutions) or exhausted,
                uniqueness='ambiguous' if len(solutions) >= 2 else 'unique' if exhausted and len(solutions) == 1 else 'unknown',
                uniqueness_scope='sample_feasible_partitions_in_general_regular_product',
                assumptions=['exact labels', 'two nonempty disjoint alphabet blocks',
                             'unrestricted regular local factors'],
                alphabet=alphabet, max_solutions=max_solutions,
                graph=dict(components=components, edges=edges), metrics=metrics)
