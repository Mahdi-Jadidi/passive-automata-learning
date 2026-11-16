"""Reproducible projection-only timing; creates, never overwrites, JSONL."""
import hashlib
import json
from pathlib import Path
import random
import time

from projections import ProjectionStore

OUTPUT = Path(__file__).with_name('projection_benchmark.jsonl')
SEED = 481937
REPEATS = 3


def corpus(size):
    rng = random.Random(SEED + size)
    sigma = tuple(chr(97 + i) for i in range(size))
    prefixes = [tuple(rng.choice(sigma) for _ in range(32)) for _ in range(16)]
    words = [p + tuple(rng.choice(sigma) for _ in range(12))
             for p in prefixes for _ in range(8)]
    return sigma, words[::2], words[1::2]


def naive(sigma, positive, negative):
    cache = {}
    def entry(mask):
        if mask not in cache:
            keep = {s for i, s in enumerate(sigma) if mask & (1 << i)}
            project = lambda word: tuple(s for s in word if s in keep)
            pos, neg = [project(w) for w in positive], [project(w) for w in negative]
            first = {}
            for i, word in enumerate(pos):
                first.setdefault(word, i)
            reject = sum(1 << i for i, word in enumerate(neg) if word not in first)
            cache[mask] = {'positive': pos, 'negative': neg,
                           'positive_witness': first, 'rejection_mask': reject}
        return cache[mask]
    return entry


def digest_update(hasher, mask, entry):
    # Include every projected word and first-witness index, not just rejection.
    data = [mask, entry['positive'], entry['negative'], entry['rejection_mask'],
            sorted((list(word), index) for word, index in entry['positive_witness'].items())]
    hasher.update(json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode())


def run(size, workload, repeat):
    sigma, pos, neg = corpus(size)
    corpus_bytes = json.dumps([sigma, pos, neg], ensure_ascii=False, separators=(',', ':')).encode()
    rng = random.Random(SEED + 1000 + size)
    masks = list(range(1 << size))
    rng.shuffle(masks)
    unique = masks[:min(64, len(masks))]
    queries = unique if workload == 'distinct' else (unique[:min(8, len(unique))] * 8)[:64]
    records = []
    for method in ('naive_cached', 'projection_store'):
        start = time.perf_counter()
        if method == 'naive_cached':
            entry = naive(sigma, pos, neg)
            store = None
        else:
            store = ProjectionStore(sigma, pos, neg, lambda: None)
            entry = store.entry
        built = time.perf_counter()
        digest = hashlib.sha256()
        rejection_digest = hashlib.sha256()
        for mask in queries:
            result = entry(mask)
            digest_update(digest, mask, result)
            rejection_digest.update(f"{mask}:{result['rejection_mask']};".encode())
        end = time.perf_counter()
        records.append({'method': method, 'alphabet_size': size, 'seed': SEED,
                        'corpus_sha256': hashlib.sha256(corpus_bytes).hexdigest(),
                        'positive_count': len(pos), 'negative_count': len(neg),
                        'workload': workload, 'repeat': repeat, 'mask_queries': queries,
                        'build_seconds': built - start, 'query_seconds': end - built,
                        'total_seconds': end - start, 'result_sha256': digest.hexdigest(),
                        'rejection_sha256': rejection_digest.hexdigest(),
                        'counters': dict(store.stats) if store else {'cached_masks': len(set(queries))}})
    assert records[0]['result_sha256'] == records[1]['result_sha256']
    assert records[0]['rejection_sha256'] == records[1]['rejection_sha256']
    return records


def main():
    # Exclusive creation prevents accidentally replacing previous evidence.
    with OUTPUT.open('x', encoding='utf-8', newline='\n') as output:
        for size in (4, 8):
            for workload in ('distinct', 'repeated'):
                for repeat in range(REPEATS):
                    for record in run(size, workload, repeat):
                        output.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + '\n')
                        output.flush()
    print(f'Wrote {OUTPUT}')


if __name__ == '__main__':
    main()
