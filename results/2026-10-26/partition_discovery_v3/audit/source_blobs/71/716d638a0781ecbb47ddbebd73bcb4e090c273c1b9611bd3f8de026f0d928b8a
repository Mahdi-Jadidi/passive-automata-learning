"""UNEXECUTED independent fixture/output checker. No solver imports/calls."""
import argparse
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def projection(word, block):
    return ''.join(a for a in word if a in block)


def accepts(dfa, word):
    state = dfa['start']
    for a in word:
        state = dfa['transitions'][state][a]
    return state in dfa['accepting']


def canonical_blocks(blocks):
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def check_fixture(visible, truth):
    require(visible['case_id'] == truth['case_id'], 'case ID mismatch')
    data = visible['input']
    alphabet = data['alphabet']
    sigma = set(alphabet)
    require(len(alphabet) >= 2 and len(sigma) == len(alphabet), 'alphabet invalid')
    require(all(isinstance(a, str) and len(a) == 1 for a in alphabet), 'symbols invalid')
    blocks = [set(b) for b in truth['blocks']]
    require(len(blocks) == 2 and all(blocks) and not (blocks[0] & blocks[1])
            and blocks[0] | blocks[1] == sigma, 'target partition invalid')
    require(len(truth['local_dfas']) == len(truth['trees']) == 2, 'target count invalid')
    positive, negative = data['positive'], data['negative']
    require(len(set(positive)) == len(positive) and '' in positive, 'positive coverage invalid')
    require(negative == sorted(sigma), 'must include exactly every unary negative')
    require(all(len(w) <= 2 and set(w) <= sigma for w in positive), 'positive shape invalid')
    require(not (set(positive) & set(negative)), 'contradictory labels')
    for side, block in enumerate(blocks):
        dfa = truth['local_dfas'][side]
        require(set(dfa['alphabet']) == block, 'DFA alphabet mismatch')
        require(set(dfa['states']) == set(dfa['transitions']), 'DFA states mismatch')
        require(len(dfa['states']) <= len(block) + 2, 'state bound exceeded')
        require(dfa['accepting'] == ['q0'] and dfa['start'] == 'q0', 'start/accepting invalid')
        expected_pairs = set()
        for edge in truth['trees'][side]:
            require(len(edge) == 2 and edge[0] != edge[1] and set(edge) <= block, 'tree edge invalid')
            expected_pairs.update((tuple(edge), tuple(reversed(edge))))
        if len(block) == 1:
            a = next(iter(block))
            expected_pairs.add((a, a))
        for state, transitions in dfa['transitions'].items():
            require(set(transitions) == block and set(transitions.values()) <= set(dfa['states']), 'DFA incomplete')
        # Independently verify the exact deterministic token-star construction.
        for a in block:
            pending = 'pending:' + a
            require(dfa['transitions']['q0'][a] == pending, 'first token transition invalid')
            for b in block:
                wanted = 'q0' if (a, b) in expected_pairs else 'dead'
                require(dfa['transitions'][pending][b] == wanted, 'second token transition invalid')
            require(dfa['transitions']['dead'][a] == 'dead', 'dead state not absorbing')
        require(bool(expected_pairs), 'infinite-target token missing')
    for label, words in ((True, positive), (False, negative)):
        for word in words:
            got = all(accepts(dfa, projection(word, blocks[s]))
                      for s, dfa in enumerate(truth['local_dfas']))
            require(got == label, 'target label mismatch')
    # Derive the sample rescue graph independently; no candidate graph helper.
    neighbors = {a: set() for a in sigma}
    for word in positive:
        if len(word) == 2 and word[0] != word[1]:
            a, b = word
            neighbors[a].add(b)
            neighbors[b].add(a)
    components, unseen = [], set(sigma)
    while unseen:
        pending, component = [min(unseen)], set()
        while pending:
            a = pending.pop()
            if a not in component:
                component.add(a)
                pending.extend(neighbors[a] - component)
        unseen -= component
        components.append(component)
    require(len(components) == 2 and canonical_blocks(components) == canonical_blocks(blocks),
            'sample graph does not certify the planted partition')
    return dict(case_id=visible['case_id'], graph_components=2,
                unique_scope='unrestricted_regular_product_partition',
                infinite_local_languages=True, labels_checked=len(positive)+len(negative))


def check_result(data, truth, result):
    require(result['model_class'] == 'general_regular_product', 'wrong model scope')
    require(result['status'] == 'found' and result['decision_complete'], 'partition not found')
    require(result['search_exhausted'] and result['uniqueness'] == 'unique', 'missing expected exact uniqueness')
    require(len(result['solutions']) == 1, 'wrong solution count')
    record = result['solutions'][0]
    require(canonical_blocks(record['blocks']) == canonical_blocks(truth['blocks']), 'wrong partition')
    blocks = [set(b) for b in record['blocks']]
    langs = [sorted({projection(p, b) for p in data['positive']}) for b in blocks]
    require(record['positive_projection_languages'] == langs, 'positive languages invalid')
    witnesses = record['negative_witnesses']
    require([w['negative'] for w in witnesses] == sorted(set(data['negative'])), 'negative witness coverage invalid')
    for w in witnesses:
        unseen = [s for s in (0, 1) if projection(w['negative'], blocks[s]) not in langs[s]]
        require(bool(unseen) and w['all_unseen_block_indices'] == unseen, 'unseen sides invalid')
        require(w['block_index'] in unseen and w['projection'] == projection(w['negative'], blocks[w['block_index']]),
                'chosen witness invalid')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inputs', type=Path)
    parser.add_argument('truths', type=Path)
    parser.add_argument('--results', type=Path, help='JSONL {case_id,result}; optional, generated externally')
    args = parser.parse_args()
    read = lambda p: [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s]
    visible, hidden = read(args.inputs), read(args.truths)
    require(len(visible) == len(hidden) == 24, 'expected 24 paired cases')
    require(len({r['case_id'] for r in visible}) == 24, 'duplicate case ID')
    truth = {r['case_id']: r for r in hidden}
    require(len(truth) == 24 and set(truth) == {r['case_id'] for r in visible}, 'truth coverage mismatch')
    results = None
    if args.results:
        records = read(args.results)
        results = {r['case_id']: r['result'] for r in records}
        require(len(records) == len(results) == 24 and set(results) == set(truth), 'result coverage mismatch')
    counts = {}
    for row in visible:
        report = check_fixture(row, truth[row['case_id']])
        m = len(row['input']['alphabet'])
        counts[m] = counts.get(m, 0) + 1
        if results is not None:
            check_result(row['input'], truth[row['case_id']], results[row['case_id']])
        print(json.dumps(report), flush=True)
    require(counts == {m: 4 for m in (4, 8, 16, 32, 64, 128)}, 'size coverage mismatch')
    print(json.dumps(dict(checked=24, output_results_checked=results is not None)), flush=True)


if __name__ == '__main__':
    main()
