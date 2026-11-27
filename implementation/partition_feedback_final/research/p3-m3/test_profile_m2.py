"""Check canonical artifact framing across read chunks without running search."""
import hashlib
import io
import json
import unittest
from unittest.mock import patch

import profile_m2


class ArtifactFramingTests(unittest.TestCase):
    def setUp(self):
        self.root = (0, 1, 2)
        self.nodes = [
            {
                "id": "root", "kind": "SPLIT", "edge": {"kind": "ROOT"},
                "parent_id": None, "alternative_count": 3,
                "cursor_log": [{"from": 0, "to": 1, "child_id": "root/c0", "pair": [0, 1]},
                               {"from": 1, "to": 2, "child_id": "root/c1", "pair": [0, 2]}],
            },
            {
                "id": "root/c0", "kind": "LEAF",
                "edge": {"index": 0, "kind": "CHILD", "pair": [0, 1]},
                "closure": {"reason": "COST"}, "parent_id": "root",
            },
            {
                "id": "root/c1", "kind": "OPEN",
                "edge": {"index": 1, "kind": "CHILD", "pair": [0, 2]},
                "reason": "USER_STOP", "parent_id": "root",
            },
        ]
        self.cert = {"nodes": self.nodes, "optima": [], "root_owner": self.root}
        self.raw = json.dumps(self.cert, sort_keys=True, separators=(",", ":")).encode()

    def test_chunk_boundaries_preserve_records_and_digest(self):
        for chunk_size in range(13, 2 * len(self.raw)):
            digest = hashlib.sha256()
            with patch.object(profile_m2, "CHUNK", chunk_size):
                records = list(profile_m2.records(io.BytesIO(self.raw), digest, self.root))
            self.assertEqual([json.loads(row) for row in records[1:]], self.nodes)
            self.assertEqual(digest.digest(), hashlib.sha256(self.raw).digest())

    def test_truncation_or_mismatched_root_fails(self):
        with self.assertRaises(ValueError):
            list(profile_m2.records(io.BytesIO(self.raw[:-1]), hashlib.sha256(), self.root))
        with self.assertRaises(ValueError):
            list(profile_m2.records(io.BytesIO(self.raw), hashlib.sha256(), (0, 0, 2)))


if __name__ == "__main__":
    unittest.main()
