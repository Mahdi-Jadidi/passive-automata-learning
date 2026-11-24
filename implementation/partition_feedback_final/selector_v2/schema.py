"""Versioned selector-side JSON schema; not the external wire protocol."""
import json
from hashlib import sha256
from .core import PartitionRef, Sample, digest

VERSION = 'selector-v2/1'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fields(obj, *names):
    require(type(obj) is dict and set(obj) == set(names), 'invalid fields')


def integer(x, n):
    require(type(x) is int and 0 <= x < n, 'invalid ID')
    return x


def token(x):
    require(type(x) is str and bool(x), 'invalid token')
    return x


def hex_digest(x):
    require(type(x) is str and len(x) == 64 and all(c in '0123456789abcdef' for c in x), 'invalid digest')
    return x


def canonical(obj):
    return json.dumps(obj, ensure_ascii=True, separators=(',', ':'), sort_keys=True, allow_nan=False).encode('utf-8')


def identity(obj):
    return sha256(canonical(obj)).hexdigest()


def sample_id(sample):
    actual = digest(('sample-v2', sample.alphabet, sample.positive, sample.negative))
    require(actual == sample.sample_digest, 'stale sample digest')
    return actual


def owner_ref(sample, owner):
    require(type(owner) is list, 'owner must be JSON array')
    p = PartitionRef(tuple(owner))
    p.validate_sample(sample)
    return p


def scope(sample, regime='UNRESTRICTED', capacity_digest=None):
    s = dict(version=VERSION, sample_digest=sample_id(sample), regime=regime,
             family='ALL_PARTITIONS', capacity_digest=capacity_digest)
    validate_scope(sample, s)
    return s


def validate_scope(sample, obj):
    fields(obj, 'version', 'sample_digest', 'regime', 'family', 'capacity_digest')
    require(obj['version'] == VERSION and obj['sample_digest'] == sample_id(sample), 'scope mismatch')
    require(obj['family'] == 'ALL_PARTITIONS', 'unsupported family')
    require(obj['regime'] in ('UNRESTRICTED', 'BOUNDED'), 'unsupported regime')
    if obj['regime'] == 'UNRESTRICTED':
        require(obj['capacity_digest'] is None, 'unexpected capacity')
    else:
        hex_digest(obj['capacity_digest'])


def request(sample, sc, partition, request_id, attempt_id):
    obj = dict(version=VERSION, scope=sc, owner=list(partition.owner), request_id=request_id,
               attempt_id=attempt_id, negative_ids=list(range(len(sample.negative))))
    validate_request(sample, obj)
    return obj


def validate_request(sample, obj):
    fields(obj, 'version', 'scope', 'owner', 'request_id', 'attempt_id', 'negative_ids')
    require(obj['version'] == VERSION and bool(sample.alphabet), 'invalid request version or empty alphabet')
    validate_scope(sample, obj['scope'])
    owner_ref(sample, obj['owner'])
    token(obj['request_id']); token(obj['attempt_id'])
    ids = obj['negative_ids']
    require(type(ids) is list and all(type(i) is int for i in ids) and ids == list(range(len(sample.negative))), 'negative order mismatch')


def raw_record(sample, kind, payload):
    return dict(version=VERSION, origin='RAW', sample_digest=sample_id(sample), kind=kind, payload=payload)
