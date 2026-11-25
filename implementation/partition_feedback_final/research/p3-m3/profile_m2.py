"""Read-only diagnostics for an existing canonical M2 certificate."""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
from time import perf_counter
from zipfile import ZipFile

# In sorted v1 output these keys start nodes and never start nested objects
# following another object in an array. The surrounding nodes array is framed
# separately. This reader is for known canonical artifacts, not proof replay.
BOUNDARY = re.compile(rb'}(?=,\{"(?:alternative_count|closure|edge)":)|}(?=\],"optima":)')
NODE_START = b'"nodes":['
CHUNK = 4 * 1024 * 1024


def records(stream, digest, root):
    data = stream.read(CHUNK)
    digest.update(data)
    start = data.index(NODE_START) + len(NODE_START)
    header = json.loads(data[:start] + b']}')
    yield header
    data = data[start:]
    offset = 0
    while data:
        for boundary in BOUNDARY.finditer(data):
            end = boundary.end()
            yield data[offset:end]
            if data[end:end + 1] == b"]":
                tail = data[end + 2:]
                while part := stream.read(CHUNK):
                    digest.update(part)
                    tail += part
                if tuple(json.loads(b"{" + tail)["root_owner"]) != root:
                    raise ValueError("certificate root differs from scope")
                return
            offset = end + 1
        part = stream.read(CHUNK)
        if not part:
            break
        digest.update(part)
        data = data[offset:] + part
        offset = 0
    raise ValueError("missing end of canonical node array")


def projection_counters(owner, positives, negatives, verifier):
    groups = sorted(set(owner))
    counts = Counter(calls=1)

    def project(word, group, label):
        counts[label + "_projections"] += 1
        counts["token_visits"] += len(word)
        return tuple(token for token in word if owner[token] == group)

    if verifier:
        for y in negatives:
            for group in groups:
                py = project(y, group, "negative")
                for x in positives:
                    counts["pair_comparisons"] += 1
                    if py == project(x, group, "positive"):
                        break
                else:
                    break
            else:
                return False, counts
        return True, counts

    remaining = list(negatives)
    for group in groups:
        if not remaining:
            break
        projected = {project(x, group, "positive") for x in positives}
        counts["set_lookups"] += len(remaining)
        remaining = [y for y in remaining if project(y, group, "negative") in projected]
    return not remaining, counts


def encoded_size(value):
    return len(json.dumps(value, ensure_ascii=True, separators=(",", ":"),
                          sort_keys=True, allow_nan=False))


def profile(stream, scope):
    started = perf_counter()
    digest = hashlib.sha256()
    root = tuple(scope["root_owner"])
    scanned = records(stream, digest, root)
    header = next(scanned)
    if (header["format"] != "p3-region-frontier/v1" or
            header["declared_status"] != "EXHAUSTED"):
        raise ValueError("expected exhausted v1 certificate and matching scope")
    words = tuple(tuple(tuple(row["tokens"]) for row in scope[label])
                  for label in ("positive", "negative"))

    kinds, closures, edge_counts, depth, fanout = (Counter() for _ in range(5))
    split_cost, exact_sources, sizes = Counter(), Counter(), Counter()
    checks = {"producer": Counter(), "verifier": Counter()}
    splits = []
    distinct = {"producer": set(), "verifier": set()}

    @lru_cache(maxsize=8192)
    def counted(owner, engine):
        return projection_counters(owner, *words, engine == "verifier")

    def record_check(owner, engine, source, expected):
        compatible, counters = counted(owner, engine)
        if compatible != expected:
            raise ValueError(f"unexpected compatibility in {engine}/{source}")
        exact_sources[f"{engine}/{source}"] += 1
        distinct[engine].add(owner)
        checks[engine].update(counters)

    incumbent = header["incumbent"]
    if incumbent is not None:
        record_check(tuple(incumbent["owner"]), "verifier", "incumbent", True)

    for raw_node in scanned:
        node = json.loads(raw_node)
        ident, parent, kind = node["id"], node["parent_id"], node["kind"]
        edge = node["edge"]["kind"]
        kinds[kind] += 1
        edge_counts[edge] += 1
        depth[ident.count("/")] += 1
        sizes["node_payloads"] += len(raw_node)
        if kind == "LEAF":
            reason = node["closure"]["reason"]
            closures[reason] += 1
            sizes["leaf_" + reason] += len(raw_node)
            if reason not in ("EXACT_NO", "FEASIBLE_MIN"):
                continue
        else:
            if kind != "SPLIT" or node["rule"] != "ALL_PAIRS_LEX_V1":
                raise ValueError("unexpected node kind or split rule")
            reason = "SPLIT"
            count = node["cursor"]
            if not (count == node["alternative_count"] == len(node["cursor_log"])
                    == len(node["children"])):
                raise ValueError("unresolved cursor in exhausted certificate")
            fanout[count] += 1
            sizes["split_payloads_including_arrays"] += len(raw_node)
            sizes["cursor_log_array"] += encoded_size(node["cursor_log"])
            sizes["children_array"] += encoded_size(node["children"])

        if parent is None:
            owner = root
        else:
            while splits and splits[-1][0] != parent:
                splits.pop()
            if not splits:
                raise ValueError("node table outside lexical parent order")
            owner = splits[-1][1]
            if edge == "CHILD":
                a, b = node["edge"]["pair"]
                owner = tuple(a if r == b else r for r in owner)

        if kind == "SPLIT":
            splits.append((ident, owner))
            split_cost[len(owner) - len(set(owner))] += 1
        if edge != "RESIDUAL":
            record_check(owner, "producer", reason, reason == "FEASIBLE_MIN")
        if kind == "LEAF":
            record_check(owner, "verifier", edge + "/" + reason, reason == "FEASIBLE_MIN")

    return {
        "sha256": digest.hexdigest(), "node_kind": kinds, "closures": closures,
        "edges": edge_counts, "depth": depth, "branch_factor_excluding_residual": fanout,
        "splits_by_base_cost": split_cost, "node_bytes": sizes,
        "cursor_records": sum(count * occurrences for count, occurrences in fanout.items()),
        "exact_sources": exact_sources, "projections": checks,
        "distinct_checked_owners": {engine: len(owners) for engine, owners in distinct.items()},
        "diagnostic_wall_s": perf_counter() - started,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path, help="expanded run ZIP or extracted directory")
    args = parser.parse_args()
    if args.artifact.is_dir():
        scope = json.loads((args.artifact / "trusted.json").read_bytes())
        path = args.artifact / "normal.json"
        with path.open("rb") as stream:
            stats = profile(stream, scope)
        size = path.stat().st_size
    else:
        with ZipFile(args.artifact) as archive:
            scope = json.loads(archive.read("trusted.json"))
            size = archive.getinfo("normal.json").file_size
            with archive.open("normal.json") as stream:
                stats = profile(stream, scope)
    stats["certificate_bytes"] = size
    stats["bytes_outside_node_payloads"] = size - stats["node_bytes"]["node_payloads"]
    print(json.dumps(stats, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
