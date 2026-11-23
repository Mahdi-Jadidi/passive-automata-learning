
"""Replay an optimality certificate using the raw sample and no selector code."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from sample import DeadlineExpired, deadline, read_sample


def require(condition, message):
    if not condition:
        raise ValueError(message)


def valid_mask(mask, alphabet):
    return type(mask) is int and mask > 0 and mask & alphabet == mask


def elements(mask):
    return frozenset(i for i in range(mask.bit_length()) if mask & (1 << i))


def partition(raw, alphabet):
    blocks = tuple(raw)
    seen = 0
    for b in blocks:
        require(valid_mask(b, alphabet) and not b & seen, "invalid partition")
        seen |= b
    require(seen == alphabet, "incomplete partition")
    return tuple(sorted(blocks, key=lambda b: b & -b))


def at(sequence, index):
    require(type(index) is int and 0 <= index < len(sequence), "invalid trace ID")
    return sequence[index]


def projection(word, block, tick):
    result = []
    allowed = elements(block)
    for a in word:
        tick()
        if a in allowed:
            result.append(a)
    return tuple(result)


class Replay:
    def __init__(self, positives, negatives, alphabet, tick):
        self.pos, self.neg = positives, negatives
        self.full = alphabet
        self.tick = tick
        self.validated = set()
        self.logs = None

    def fact(self, item, i):
        require(type(item["i"]) is int and item["i"] == i, "mixed negatives in one deduction")
        r, j, source = item["region"], item["j"], item["source"]
        require(type(r) is int and r >= 0 and r & self.full == r, "region outside alphabet")
        x, y = at(self.pos, j), at(self.neg, i)
        require(source == "raw" or (type(source) is int and source >= 0), "invalid evidence reference")
        if self.logs is not None and source != "raw":
            tables = at(self.logs, source)["tables"]
            require(any(t["block"] == r and [i, j] in t["zeros"] for t in tables),
                    "reference does not contain witness")
        key = i, j, r
        if key not in self.validated:
            require(projection(x, r, self.tick) == projection(y, r, self.tick), "false projection witness")
            self.validated.add(key)
        return r

    def region(self, proof, current, active):
        region = partition(proof["blocks"], active)
        i = proof["i"]
        at(self.neg, i)
        facts = proof["facts"]
        require(len(facts) == len(region), "missing block witness")
        for b, item in zip(proof["blocks"], facts):
            require(self.fact(item, i) & b == b, "witness does not contain block")
        require(all(any(b & a == a for b in region) for a in current), "region must coarsen current partition")
        return region

    def lower(self, facts, current, overlapping):
        union = set()
        result = 0
        ids = set()
        require(bool(facts), "missing lower-bound evidence")
        for record in facts:
            i = record["i"]
            require(i not in ids, "repeated negative in lower bound")
            ids.add(i)
            edges = set()
            for item in record["facts"]:
                region = self.fact(item, i)
                edge = frozenset(b for b in current if region & b != b)
                require(edge and edge not in edges, "empty or repeated hitting obligation")
                edges.add(edge)
            require(bool(edges), "missing hitting obligations")
            remaining = set(edges)
            support = set()
            d = 0
            while remaining:
                self.tick()
                component = [remaining.pop()]
                reached = set(component[0])
                while True:
                    neighbors = {edge for edge in remaining if reached.intersection(edge)}
                    if not neighbors:
                        break
                    remaining -= neighbors
                    component.extend(neighbors)
                    reached.update(*neighbors)
                degree = max(Counter(atom for edge in component for atom in edge).values())
                d += (len(component) + degree - 1) // degree
                support.update(reached)
            require(d >= 2, "claimed support proves no positive cost")
            overlap = len(union & support)
            require(overlapping or overlap == 0, "disjoint bound overlaps")
            primitive = d - 1
            result = max(result, primitive, result + primitive - max(0, overlap - 1))
            union.update(support)
        return result

    def answer(self, blocks):
        missing = set(range(len(self.neg)))
        for b in blocks:
            positives = {projection(x, b, self.tick) for x in self.pos}
            missing = {i for i in missing if projection(self.neg[i], b, self.tick) in positives}
        require(not missing, "answer is incompatible")

    def transcript(self, proof):
        self.logs = proof["queries"]
        seen = set()
        for number, query in enumerate(self.logs):
            self.tick()
            require(type(query["id"]) is int and query["id"] == number, "misordered queries")
            # The oracle always receives the declared alphabet.
            blocks = tuple(query["blocks"])
            mask = 0
            for b in blocks:
                mask |= b
            require(mask == self.full and partition(blocks, self.full) == blocks
                    and blocks not in seen, "invalid or duplicate query")
            seen.add(blocks)
            require(tuple(t["block"] for t in query["tables"]) == blocks, "misordered query tables")
            covered = set()
            for row in query["tables"]:
                b = row["block"]
                positives = {projection(x, b, self.tick) for x in self.pos}
                groups = {}
                zeros = set()
                for i, y in enumerate(self.neg):
                    local = projection(y, b, self.tick)
                    if local in positives:
                        zeros.add(i)
                    else:
                        groups.setdefault(local, []).append(i)
                reported = row["zeros"]
                require(len(reported) == len(zeros) and {i for i, _ in reported} == zeros,
                        "table fixed-zero columns differ from the sample")
                for i, j in reported:
                    self.fact({"i": i, "j": j, "region": b, "source": "raw"}, i)
                require(sorted(map(tuple, row["free"])) == sorted(map(tuple, groups.values())),
                        "false grouping of free columns")
                covered.update(i for group in groups.values() for i in group)
            failed = query["failed"]
            if query["status"] == "ACCEPT":
                require(failed is None and len(covered) == len(self.neg), "false ACCEPT")
            else:
                require(query["status"] == "NO" and type(failed) is int
                        and 0 <= failed < len(self.neg) and failed not in covered, "false NO")

    def tree(self, proof, answer):
        unused = proof["unused"]
        unused_mask = 0
        used_symbols = set(a for w in (*self.pos, *self.neg) for a in w)
        for bit in unused:
            require(valid_mask(bit, self.full) and bit.bit_count() == 1 and not bit & unused_mask
                    and elements(bit).isdisjoint(used_symbols) and bit in answer, "invalid unused symbol")
            unused_mask |= bit
        active = self.full ^ unused_mask
        require(active or not self.full, "cannot remove every declared symbol")
        root = tuple(1 << a for a in sorted(elements(active)))
        for step in proof["contractions"]:
            self.tick()
            i = step["i"]
            at(self.neg, i)
            mandatory = set()
            for item in step["items"]:
                a = item["block"]
                require(type(a) is int and a in root and a not in mandatory, "invalid mandatory atom")
                complement = active ^ a
                require(self.fact(item["fact"], i) & complement == complement,
                        "missing complement witness")
                mandatory.add(a)
            require(len(mandatory) >= 2, "contraction must merge at least two atoms")
            root = partition([*set(root).difference(mandatory), sum(mandatory)], active)
        require(tuple(proof["root"]) == root, "wrong root")
        active_answer = tuple(b for b in answer if b not in unused)
        require(all(any(a & b == a for b in active_answer) for a in root), "answer splits mandatory atom")
        threshold = len(active_answer)
        records = {}
        for entry in proof["records"]:
            key = partition(entry["blocks"], active)
            require(key not in records and len(key) > threshold, "duplicate or extraneous coverage record")
            records[key] = entry
        pending, seen = [root] if len(root) > threshold else [], set()
        while pending:
            self.tick()
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            require(current in records, "missing reachable partition")
            record = records.pop(current)
            kind = record["kind"]
            if kind in ("overlap", "disjoint"):
                lower = self.lower(record["facts"], current, overlapping=kind == "overlap")
                require(len(current) - lower <= threshold, "lower bound does not close branch")
                continue
            region = self.region(record["region"], current, active)
            if kind == "unit":
                require(len(current) - 1 <= threshold, "unit bound does not close branch")
                continue
            require(kind == "branch", "unknown proof step")
            if len(current) - 1 > threshold:
                for left, right in combinations(current, 2):
                    self.tick()
                    if not any(left & b == left and right & b == right for b in region):
                        rest = [a for a in current if a not in (left, right)]
                        pending.append(partition([*rest, left | right], active))
        require(not records, "unreachable coverage records")


def verify(D, result, *, seconds=None):
    tick = deadline(seconds)
    try:
        tick()
        Sigma, positives, negatives = read_sample(D, tick)
        status = result["status"]
        fields = ("max_devices", "blocks")
        if status == "INCOMPLETE":
            require(not any(k in result for k in (*fields, "certificate")), "incomplete output makes a claim")
            return {"status": "INCOMPLETE"}
        proof = result["certificate"]
        digest = sha256(json.dumps(D, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
        require(proof["digest"] == digest.hexdigest(), "certificate belongs to a different sample")
        full = (1 << len(Sigma)) - 1
        replay = Replay(positives, negatives, full, tick)
        if "transcript" in result:
            replay.transcript(result["transcript"])
        if status == "INFEASIBLE":
            require(not any(k in result for k in fields), "infeasible result contains an answer")
            y = at(negatives, proof["i"])
            if proof["kind"] == "A01":
                require(y == at(positives, proof["j"]), "opposite labels differ")
            else:
                require(proof["kind"] == "A02" and not full, "invalid infeasibility proof")
        else:
            require(status == "OPTIMAL" and proof["kind"] == "partition-v1", "unknown certificate type")
            require(type(result["max_devices"]) is int and result["max_devices"] == len(result["blocks"]),
                    "incorrect answer size")
            index = {a: 1 << i for i, a in enumerate(Sigma)}
            blocks = []
            for block in result["blocks"]:
                require(len(block) == len(set(block)), "repeated symbol in block")
                blocks.append(sum(index[a] for a in block))
            answer = partition(blocks, full)
            replay.answer(answer)
            replay.tree(proof, answer)
        tick()
    except DeadlineExpired:
        return {"status": "INCOMPLETE"}
    except (AttributeError, IndexError, KeyError, TypeError, ValueError) as exc:
        return {"status": "INVALID", "reason": str(exc)}
    return {"status": "VERIFIED"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", type=Path)
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    D, result = [json.loads(p.read_text(encoding="utf-8-sig")) for p in (args.sample, args.result)]
    verdict = verify(D, result)
    print(json.dumps(verdict))
    return 0 if verdict["status"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
