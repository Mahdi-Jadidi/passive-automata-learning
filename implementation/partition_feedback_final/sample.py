"""Shared input and deadline conventions for the standalone example."""

from math import isfinite
from time import perf_counter


class DeadlineExpired(Exception):
    pass


def deadline(seconds):
    if seconds is not None and (
        type(seconds) not in (int, float) or not isfinite(seconds) or seconds < 0
    ):
        raise ValueError("seconds must be finite and nonnegative")
    stop = None if seconds is None else perf_counter() + seconds

    def tick():
        if stop is not None and perf_counter() >= stop:
            raise DeadlineExpired

    return tick


def read_sample(D, tick):
    if type(D) is not dict or set(D) != {"alphabet", "positive", "negative"}:
        raise ValueError("expected alphabet, positive, and negative")
    Sigma = D["alphabet"]
    if type(Sigma) is not list or any(type(a) is not str or not a for a in Sigma):
        raise ValueError("alphabet must be a list of nonempty string symbols")
    index = {a: i for i, a in enumerate(Sigma)}
    if len(index) != len(Sigma):
        raise ValueError("alphabet contains duplicate symbols")

    def encode(words):
        if type(words) is not list:
            raise ValueError("each label class must be a list of traces")
        encoded = []
        for word in words:
            tick()
            if type(word) is not list:
                raise ValueError("each trace must be a list of symbols")
            trace = []
            for a in word:
                tick()
                if type(a) is not str or a not in index:
                    raise ValueError("trace contains a symbol outside alphabet")
                trace.append(index[a])
            encoded.append(tuple(trace))
        return tuple(encoded)

    return Sigma, encode(D["positive"]), encode(D["negative"])

