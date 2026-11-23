
"""Normalize optional witness IDs at the oracle boundary or during independent replay."""
from copy import deepcopy

from sample import read_sample
from verify import projection, verify


class Witnesses:
    def __init__(self, D, tick):
        _, self.positives, self.negatives = read_sample(D, tick)
        self.tick = tick
        self.cache = {}

    def find(self, block, i):
        if type(i) is not int or not 0 <= i < len(self.negatives):
            raise ValueError("invalid negative ID in table")
        if block not in self.cache:
            positives = {}
            for j, word in enumerate(self.positives):
                positives.setdefault(projection(word, block, self.tick), j)
            self.cache[block] = positives
        image = projection(self.negatives[i], block, self.tick)
        if image not in self.cache[block]:
            raise ValueError("advertised zero has no matching positive")
        return self.cache[block][image]

    def table(self, reply):
        for row in reply.get("tables", ()):
            normalized = []
            for i, *witness in row["zeros"]:
                if len(witness) > 1:
                    raise ValueError("invalid zero entry")
                j = witness[0] if witness and witness[0] is not None else self.find(row["block"], i)
                normalized.append([i, j])
            row["zeros"] = normalized
        return reply


def with_optional_witnesses(D, oracle, tick=lambda: None):
    """Resolve omitted witnesses only on blocks of a complete submitted partition."""
    lookup = Witnesses(D, tick)

    def query(partition, purpose):
        result = deepcopy(oracle(partition, purpose))
        if result.get("status") == "INCOMPLETE":
            return result
        if tuple(result["blocks"]) != partition or tuple(t["block"] for t in result["tables"]) != partition:
            raise ValueError("reply belongs to a different partition")
        return lookup.table(result)

    return query


def verify_compact(D, result):
    """Reconstruct omitted witnesses from raw traces before the ordinary replay."""
    try:
        normalized = deepcopy(result)
        lookup = Witnesses(D, lambda: None)
        log = normalized.get("transcript", {}).get("queries", [])
        for response in log:
            lookup.table(response)

        def restore(value):
            if isinstance(value, dict):
                if {"i", "source", "region"} <= value.keys() and value.get("j") is None:
                    i, region, source = value["i"], value["region"], value["source"]
                    logged = []
                    if type(source) is int and 0 <= source < len(log):
                        logged = [j for table in log[source]["tables"] if table["block"] == region
                                  for col, j in table["zeros"] if col == i]
                    value["j"] = logged[0] if logged else lookup.find(region, i)
                for item in value.values():
                    restore(item)
            elif isinstance(value, (tuple, list)):
                for item in value:
                    restore(item)

        if "certificate" in normalized:
            restore(normalized["certificate"])
        return verify(D, normalized)
    except (AttributeError, IndexError, KeyError, TypeError, ValueError) as exc:
        return {"status": "INVALID", "reason": str(exc)}
