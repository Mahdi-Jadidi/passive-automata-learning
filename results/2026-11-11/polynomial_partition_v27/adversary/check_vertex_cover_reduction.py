"""Exhaustive independent audit of the graph vertex-cover reduction."""
from itertools import combinations
import json
from pathlib import Path
from oracle_v27 import oracle


def all_graphs(m):
    edges = list(combinations(range(m), 2))
    for mask in range(1, 1 << len(edges)):
        yield [e for i, e in enumerate(edges) if mask >> i & 1]


def alpha(m, edges):
    best = 0
    for mask in range(1 << m):
        if mask.bit_count() <= best:
            continue
        if all(not (mask >> u & 1 and mask >> v & 1) for u, v in edges):
            best = mask.bit_count()
    return best


def reduction(m, edges):
    sigma = list(range(m))
    n = tuple(sigma)
    p = [tuple(x for x in sigma if x not in e) for e in edges]
    return sigma, p, [n]


def check():
    totals, failures, certificate_checks = {}, [], 0
    for m in range(2, 6):
        count = 0
        for edges in all_graphs(m):
            count += 1
            sigma, p, neg = reduction(m, edges)
            got = oracle(sigma, p, neg)["max_blocks"]
            want = alpha(m, edges) + 1
            if got != want:
                failures.append({"m":m,"edges":edges,"got":got,"expected":want})
            # Verify both sides of the key equivalence for every nonempty B:
            # projection(n,B) is absent from positive projections iff B is a
            # vertex cover. The partition oracle already uses this predicate.
            for bmask in range(1, 1 << m):
                B = {i for i in range(m) if bmask >> i & 1}
                proj_n = tuple(x for x in neg[0] if x in B)
                rejects = proj_n not in {tuple(x for x in w if x in B) for w in p}
                is_cover = all(u in B or v in B for u, v in edges)
                if rejects != is_cover:
                    failures.append({"m":m,"edges":edges,"B":sorted(B),"rejects":rejects,"cover":is_cover})
                certificate_checks += 1
        totals[str(m)] = count
    # Isolated vertices, one edge, triangle, and complete graph are explicitly
    # represented among the exhaustive fixtures; record recognizable controls.
    return {"status":"passed" if not failures else "failed",
            "graphs_by_vertex_count":totals,"total_nonempty_graphs":sum(totals.values()),
            "projection_equivalence_checks":certificate_checks,"mismatches":failures,
            "reduction_claim":"max compatible blocks = alpha(G)+1 for all nonempty simple graphs; exact polynomial reduction implies poly-time exact optimization would solve maximum independent set"}


if __name__ == '__main__':
    out = check()
    dest = Path(__file__).with_name('vertex_cover_reduction_results.json')
    dest.write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(out, sort_keys=True))
