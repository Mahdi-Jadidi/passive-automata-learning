"""Opt-in compatibility evaluator with a reusable literal singleton index."""
from array import array
from dataclasses import dataclass

from .edr_sparse import DEFAULT_INDEX_BYTES, _Scratch


@dataclass(frozen=True)
class Compatibility:
    compatible: bool
    negative_id: int | None
    owner: tuple[int, ...]
    sample: object


class CompactProjections:
    """One instance per immutable sample and search scope."""

    def __init__(self, sample, index_bytes=DEFAULT_INDEX_BYTES):
        self.sample = sample
        self.index_bytes = index_bytes
        self._singleton = None

    def check(self, owner, budget, counters):
        sample = self.sample
        positives, negatives = sample.positive, sample.negative
        size = len(owner)
        if size != len(sample.alphabet):
            raise ValueError("partition universe mismatch")
        budget.charge_work()
        if not negatives:
            return Compatibility(True, None, owner, sample)
        if not size:
            return Compatibility(False, 0, owner, sample)
        if not positives:
            return Compatibility(True, None, owner, sample)

        scratch = _Scratch(self.index_bytes, counters, "compact")
        if self._singleton is None:
            scratch.admit(1024 + 9 * size, retain=True)
            presence = array("Q", [0]) * size
            ones = bytearray(size)
            repeated = set()
            for word in positives:
                budget.charge_work(1 + 3 * len(word))
                temporary = 256 + 160 * len(word)
                scratch.admit(temporary)
                counts = {}
                for token in word:
                    counts[token] = counts.get(token, 0) + 1
                for token, count in counts.items():
                    presence[token] += 1
                    if count == 1:
                        ones[token] = 1
                    else:
                        key = (count, token)
                        if key not in repeated:
                            scratch.admit(256 + temporary)
                            scratch.admit(256, retain=True)
                            repeated.add(key)
            self._singleton = (presence, ones, repeated, scratch.retained)
            counters["singleton_builds"] = counters.get("singleton_builds", 0) + 1
        presence, ones, repeated, retained = self._singleton
        if not scratch.retained:
            scratch.admit(retained, retain=True)

        scratch.admit(size + 128, retain=True)
        merged = bytearray(size)
        has_merges = False
        for token, group in enumerate(owner):
            budget.charge_work()
            if token != group:
                merged[group] = 1
                has_merges = True

        merged_projections = set()
        merged_presence = {}
        if has_merges:
            for word in positives:
                budget.charge_work(1 + 4 * len(word))
                temporary = 256 + 192 * len(word)
                scratch.admit(temporary)
                groups = {}
                for token in word:
                    group = owner[token]
                    if merged[group]:
                        groups.setdefault(group, []).append(token)
                for group, tokens in groups.items():
                    if group not in merged_presence:
                        scratch.admit(192 + temporary)
                        scratch.admit(192, retain=True)
                    merged_presence[group] = merged_presence.get(group, 0) + 1
                    key = tuple(tokens)
                    if key not in merged_projections:
                        scratch.admit(192 + 8 * len(tokens) + temporary)
                        scratch.admit(192 + 8 * len(tokens), retain=True)
                        merged_projections.add(key)

        total = len(positives)
        universal = 0
        for token, count in enumerate(presence):
            budget.charge_work()
            if merged[token]:
                universal += merged_presence.get(token, 0) == total
            else:
                universal += owner[token] == token and count == total

        for i, word in enumerate(negatives):
            budget.charge_work(1 + 4 * len(word))
            scratch.admit(256 + 192 * len(word))
            groups = {}
            for token in word:
                groups.setdefault(owner[token], []).append(token)
            touched_universal = 0
            for group, tokens in groups.items():
                if merged[group]:
                    if tuple(tokens) not in merged_projections:
                        break
                    touched_universal += merged_presence.get(group, 0) == total
                else:
                    count = len(tokens)
                    if not (ones[group] if count == 1 else (count, group) in repeated):
                        break
                    touched_universal += presence[group] == total
            else:
                if touched_universal == universal:
                    return Compatibility(False, i, owner, sample)
        return Compatibility(True, None, owner, sample)
