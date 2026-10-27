"""UNEXECUTED candidate: freeze 24 infinite-target coverage fixtures separately."""
import argparse
import hashlib
import json
from pathlib import Path
import random

SEED = 2026102604
SIZES = (4, 8, 16, 32, 64, 128)


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':')) + '\n').encode('utf-8')


def local_dfa(block, edges):
    """Token language (both orientations of path edges)*; singleton uses (aa)*."""
    allowed = {tuple(edge) for edge in edges} | {tuple(reversed(edge)) for edge in edges}
    if len(block) == 1:
        allowed.add((block[0], block[0]))
    pending = {a: 'pending:' + a for a in block}
    transitions = {'q0': {a: pending[a] for a in block},
                   'dead': {a: 'dead' for a in block}}
    for a in block:
        transitions[pending[a]] = {b: 'q0' if (a, b) in allowed else 'dead'
                                   for b in block}
    return dict(alphabet=sorted(block), states=list(transitions), start='q0',
                accepting=['q0'], transitions=transitions)


def fixtures():
    for m in SIZES:
        for variant in range(4):
            rng = random.Random(SEED + m * 10 + variant)
            alphabet = [chr(0x400 + i) for i in range(m)]
            order = alphabet[:]
            rng.shuffle(order)
            split = (m // 2, 1, m - 1, max(1, m // 3))[variant]
            blocks = [order[:split], order[split:]]
            trees = [[list(pair) for pair in zip(block, block[1:])] for block in blocks]
            positives = {''}
            for block, edges in zip(blocks, trees):
                for a, b in edges:
                    positives.add(a + b if rng.getrandbits(1) else b + a)
                if len(block) == 1:
                    positives.add(block[0] * 2)
            case_id = f'infinite_coverage_m{m:03d}_{variant:02d}'
            data = dict(alphabet=alphabet, positive=sorted(positives), negative=alphabet)
            truth = dict(case_id=case_id, blocks=[sorted(b) for b in blocks],
                         trees=trees, local_dfas=[local_dfa(b, e) for b, e in zip(blocks, trees)],
                         seed=SEED + m * 10 + variant,
                         interpretation='infinite local token-star targets; unrestricted partition uniqueness from sample coverage')
            yield dict(case_id=case_id, input=data), truth


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    inputs, truths = [], []
    for visible, hidden in fixtures():
        inputs.append(visible)
        truths.append(hidden)
    for name, records in [('inputs.jsonl', inputs), ('truths.jsonl', truths)]:
        (args.output / name).write_bytes(b''.join(canonical(r) for r in records))
    paths = [args.output / name for name in ('inputs.jsonl', 'truths.jsonl')]
    manifest = dict(family='C003_GENERAL_INFINITE_COVERAGE_V1', seed=SEED,
                    cases=len(inputs), cases_per_size=4, sizes=list(SIZES),
                    files={p.name: dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                                       bytes=p.stat().st_size) for p in paths},
                    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    truth_policy='Pass only visible input to solver; truths are audit-only.',
                    scientific_status='unvalidated_generated_fixture_pending_independent_audit')
    (args.output / 'manifest.json').write_bytes(canonical(manifest))
    print(json.dumps(manifest, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
