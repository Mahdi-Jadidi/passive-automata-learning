"""Bounded exact singleton-deletion discovery for a checked failed negative."""
from itertools import chain

from .edr_cross import discover
from .edr_sparse import DEFAULT_JOIN_WORK


class _LocalCap(Exception):
    pass


class TargetedDiscovery:
    def __init__(self, sample, *, work_limit=DEFAULT_JOIN_WORK, fact_limit=256):
        if min(work_limit, fact_limit) < 0:
            raise ValueError("negative discovery limit")
        self.sample = sample
        self.work_limit = work_limit
        self.fact_limit = fact_limit
        self._facts = {}
        self._fact_count = 0

    def find(self, failed, budget, counters):
        """Return an existing cross-support witness, or a heuristic miss."""
        if failed.sample is not self.sample or failed.compatible or failed.negative_id is None:
            raise ValueError("expected failed compatibility from this scope")
        owner = failed.owner
        i = failed.negative_id
        y = self.sample.negative[i]
        used = 0

        def charge(units=1):
            nonlocal used
            if used + units > self.work_limit:
                raise _LocalCap
            budget.charge_work(units)
            used += units
            counters["target_work"] = counters.get("target_work", 0) + units

        def complement(word, group):
            for token in word:
                charge()
                if owner[token] != group:
                    yield token
            yield None

        def equal(x, group):
            counters["target_probes"] = counters.get("target_probes", 0) + 1
            return all(a == b for a, b in zip(complement(x, group), complement(y, group)))

        def candidates(x):
            for a, b in zip(x, y):
                charge()
                if a != b:
                    yield a
                    if owner[a] != owner[b]:
                        yield b
                    return
            if len(x) != len(y):
                yield (x if len(x) > len(y) else y)[min(len(x), len(y))]

        def fresh():
            for j, x in enumerate(self.sample.positive):
                charge()
                for token in candidates(x):
                    yield j, token, False

        first = None
        pending = []
        facts = self._facts.get(i, ())
        cached = ((j, token, True) for j, token in facts)
        try:
            # The cached original token is lifted through the current owner.
            # Recheck against the new deletion before the fact can emit a witness.
            for j, token, reused in chain(cached, fresh()):
                charge()
                group = owner[token]
                if first is not None and group == first[0]:
                    continue
                if reused:
                    counters["target_fact_rechecks"] = counters.get("target_fact_rechecks", 0) + 1
                if not equal(self.sample.positive[j], group):
                    continue
                fact = (j, token)
                if self._fact_count + len(pending) < self.fact_limit and not reused:
                    pending.append(fact)
                if first is None:
                    first = (group, j)
                    continue
                (s, js), (t, jt) = sorted((first, (group, j)))
                return dict(negative_id=f"N{i}", positive_s_id=f"P{js}",
                            positive_t_id=f"P{jt}", support_s=[s], support_t=[t])
        except _LocalCap:
            counters["target_local_caps"] = counters.get("target_local_caps", 0) + 1
        finally:
            if pending:
                self._facts.setdefault(i, []).extend(pending)
                self._fact_count += len(pending)
        return None

    def discover(self, failed, budget, counters):
        """Preserve the existing literal fallback and its caller's all-pairs path."""
        return self.find(failed, budget, counters) or discover(
            failed.owner, self.sample, budget, counters)
