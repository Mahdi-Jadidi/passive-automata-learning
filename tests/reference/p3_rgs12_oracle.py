"""Independent exhaustive RGS oracle for actual M2 small_choice (n <= 12).

Enumerates all original-alphabet partitions, including unused symbols. The
only memoization is literal compatibility of individual blocks, indexed by
original-ID subsets; it is independent of the producer and frontier verifier.
"""
import argparse
import json
import time


class Limit(Exception):
    pass


def oracle(raw, *, seconds=30, max_partitions=4213597, max_work=150000000,
           max_entries=100000):
    work = visited = 0
    def envelope(status, reason, result=None):
        out = dict(status=status, operational_status="INCOMPLETE", reason=reason,
                   visited=visited, work_units=work)
        if status == "VERIFIED":
            out["result"] = result
        return out
    try:
        if (type(seconds) not in (int, float) or not 0 <= seconds <= 3600 or
                any(type(v) is not int or v < 0 for v in
                    (max_partitions, max_work, max_entries))):
            raise ValueError("budget")
        deadline = time.monotonic() + seconds
        def debit(amount=1):
            nonlocal work
            work += amount
            if work > max_work or time.monotonic() >= deadline:
                raise Limit("work/deadline cap")
        debit(0)
        if type(raw) is not dict or set(raw) != {"alphabet", "positive", "negative"}:
            raise ValueError("raw fields")
        a = raw["alphabet"]
        if type(a) is not list or any(type(s) is not str or not s for s in a):
            raise ValueError("alphabet")
        n = len(a)
        if n > 12:
            raise Limit("alphabet cap: 12")
        ids = {s: i for i, s in enumerate(a)}
        if len(ids) != n:
            raise ValueError("duplicate symbol")
        def words(key):
            ws = raw[key]
            if type(ws) is not list:
                raise ValueError("traces")
            out = []
            for w in ws:
                debit()
                if type(w) is not list:
                    raise ValueError("trace")
                row = []
                for s in w:
                    debit()
                    if type(s) is not str or s not in ids:
                        raise ValueError("token")
                    row.append(1 << ids[s])
                out.append(tuple(row))
            return out
        X, Y = words("positive"), words("negative")
        target = (1 << len(Y)) - 1
        if (1 << n) > max_entries:
            raise Limit("block table cap")
        witness = [0] * (1 << n)
        def project(w, mask):
            debit(len(w) + 1)
            return tuple(t for t in w if t & mask)
        for mask in range(1, 1 << n):
            debit()
            px = {project(x, mask) for x in X}
            for i, y in enumerate(Y):
                py = project(y, mask)
                # Set membership uses exact tuple equality, not hash-only evidence.
                if py not in px:
                    witness[mask] |= 1 << i
        groups = []
        best = None
        winners = []
        def visit(i):
            nonlocal visited, best, winners
            debit()
            if i == n:
                if visited >= max_partitions:
                    raise Limit("partition cap")
                visited += 1
                covered = 0
                for mask in groups:
                    debit()
                    covered |= witness[mask]
                    if covered == target:
                        break
                if covered != target:
                    return
                cost = n - len(groups)
                if best is None or cost < best:
                    best, winners = cost, []
                if cost == best:
                    if len(winners) >= max_entries:
                        raise Limit("optima entry cap")
                    owner = [0] * n
                    for mask in groups:
                        rep = (mask & -mask).bit_length() - 1
                        while mask:
                            debit()
                            bit = mask & -mask
                            owner[bit.bit_length() - 1] = rep
                            mask ^= bit
                    winners.append(owner)
                return
            bit = 1 << i
            # Existing groups in order of first occurrence, then a new group:
            # exactly the restricted-growth-string recurrence, no pruning.
            for g in range(len(groups)):
                groups[g] |= bit
                visit(i + 1)
                groups[g] ^= bit
            groups.append(bit)
            visit(i + 1)
            groups.pop()
        visit(0)
        winners.sort()
        debit(0)
        return envelope("VERIFIED", None, dict(optimum=best, optima=winners))
    except (Limit, MemoryError, RecursionError, TimeoutError) as e:
        return envelope("INCOMPLETE", str(e))
    except (ValueError, TypeError, OverflowError) as e:
        return envelope("INVALID", str(e))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", required=True)
    p.add_argument("--seconds", type=float, default=30)
    p.add_argument("--max-partitions", type=int, default=4213597)
    p.add_argument("--max-work", type=int, default=150000000)
    p.add_argument("--max-entries", type=int, default=100000)
    p.add_argument("--max-raw-bytes", type=int, default=64*1024*1024)
    a = p.parse_args()
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError("duplicate JSON key")
            out[k] = v
        return out
    def nonfinite(s):
        raise ValueError("nonfinite JSON value")
    try:
        if a.max_raw_bytes < 0:
            raise ValueError("raw byte cap")
        with open(a.raw, "rb") as f:
            data = f.read(a.max_raw_bytes + 1)
        if len(data) > a.max_raw_bytes:
            raise Limit("raw byte cap")
        raw = json.loads(data.decode("utf-8"), object_pairs_hook=pairs,
                         parse_constant=nonfinite)
        out = oracle(raw, seconds=a.seconds, max_partitions=a.max_partitions,
                     max_work=a.max_work, max_entries=a.max_entries)
    except (Limit, MemoryError, RecursionError, FileNotFoundError) as e:
        out = dict(status="INCOMPLETE", operational_status="INCOMPLETE", reason=str(e))
    except (ValueError, OSError) as e:
        out = dict(status="INVALID", operational_status="INCOMPLETE", reason=str(e))
    print(json.dumps(out, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return {"VERIFIED": 0, "INVALID": 1, "INCOMPLETE": 2}[out["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
