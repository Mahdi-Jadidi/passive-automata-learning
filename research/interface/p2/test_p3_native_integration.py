"""Offline integration of actual P3 producer bytes, independent proof, and core ledger.

This test is intentionally invoked only by p3-native-integration.yml, which
supplies immutable producer-artifact and proof-source checkouts.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from gateway import open_gateway
from selector_v2.registered_ledger import RegisteredLedger


RAW_SHA256 = {
    "tiny_choice": "1c064aa4c7ce111ec8c403e8b6a05b64de5acdec2ef564861f06c2e2e2e42f23",
    "small_choice": "10b0c3534ddf42369db003bca6b323c9fdaa33cd36aa15031360c3428949931b",
}
CERT_PINS = {
    ("tiny_choice", "one"): (
        "91996d9bc6a3d7e88b5c89fc44158bc1cd89cf778256ec67839e1d38555e7ec8",
        "bce55d7db1ddbcf6140b2a841f74bb51dad8f2f0",
    ),
    ("tiny_choice", "all"): (
        "1be8394e233fe2c5a337766d73a1385145ab82b95d75273d5d548f60b2b781c0",
        "eafd651d28fc1f06f60bdbc4c0a4095a04dc390b",
    ),
    ("small_choice", "one"): (
        "dafa72f9e8ec4cc63330d4a7cd420cd478237dd7431c7e488267345ed810471e",
        "d1539a0a9ed03d208a88c515c51f6e6473126c3c",
    ),
    ("small_choice", "all"): (
        "9fb5f5bbc1c64e90bc955f73d2325a1d159224e91258e8a8758a34595102e2a7",
        "e2f00717be846336b1f3287a8dd58070272434fd",
    ),
}
FORBIDDEN_JOURNAL_KEYS = {
    "certificate", "certificate_digest", "proof", "proof_digest", "frontier",
}


def strict_loads(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError("nonfinite JSON number: " + value)))


def pins_file(path):
    path = Path(path)
    size = path.stat().st_size
    sha256 = hashlib.sha256()
    git_blob = hashlib.sha1(b"blob " + str(size).encode("ascii") + b"\0")
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            sha256.update(chunk)
            git_blob.update(chunk)
    return {
        "bytes": size,
        "sha256": sha256.hexdigest(),
        "git_blob_calculated": git_blob.hexdigest(),
    }


def contains_forbidden_key(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_JOURNAL_KEYS or contains_forbidden_key(child):
                return True
    elif isinstance(value, list):
        return any(contains_forbidden_key(child) for child in value)
    return False


def canonical_owner(owner, alphabet_size):
    if type(owner) is not list or len(owner) != alphabet_size:
        return False
    for index, representative in enumerate(owner):
        if type(representative) is not int or not 0 <= representative <= index:
            return False
        if owner[representative] != representative:
            return False
    return True


def invoke_verifier(verifier, raw_bytes, journal_bytes, trusted_bytes,
                    proof_path, optimized):
    """Write exact raw/journal/scope bytes unchanged, rebuild scope, then replay the certificate file."""
    with tempfile.TemporaryDirectory(prefix="p3-native-interface-") as directory:
        root = Path(directory)
        raw_path = root / "raw.json"
        journal_path = root / "journal.json"
        trusted_path = root / "trusted.json"
        rebuilt_path = root / "rebuilt-trusted.json"
        raw_path.write_bytes(raw_bytes)
        journal_path.write_bytes(journal_bytes)
        trusted_path.write_bytes(trusted_bytes)
        proof_path = Path(proof_path)
        if not proof_path.is_file():
            raise AssertionError("certificate file is missing: " + str(proof_path))

        prefix = [sys.executable]
        if optimized:
            prefix.append("-O")
        prefix.append("-B")

        builder = prefix + [
            str(verifier), "--make-trusted-scope",
            "--raw", str(raw_path), "--journal", str(journal_path),
            "--out", str(rebuilt_path), "--seconds", "30",
        ]
        built = subprocess.run(builder, capture_output=True, timeout=45, check=False)
        if built.returncode != 0:
            raise AssertionError(
                "independent trusted-scope builder failed: "
                + built.stderr.decode("utf-8", "replace")
            )
        if rebuilt_path.read_bytes() != trusted_bytes:
            raise AssertionError("published trusted-scope bytes differ from independent rebuild")

        command = prefix + [
            str(verifier),
            "--raw", str(raw_path),
            "--journal", str(journal_path),
            "--scope", str(trusted_path),
            "--proof", str(proof_path),
            "--seconds", "240",
            "--max-work", "4000000000",
            "--max-exact-checks", "200000000",
            "--max-nodes", "4000001",
            "--max-entries", "4000001",
            "--max-proof-bytes", str(2 * 1024 * 1024 * 1024),
        ]
        completed = subprocess.run(command, capture_output=True, timeout=270, check=False)
        result = strict_loads(completed.stdout)
        return completed.returncode, result


def verify_then_register(verifier, raw_bytes, journal_bytes, trusted_bytes,
                         proof_path, mode, optimized):
    """Fail closed: the only path to open_gateway/register follows VERIFIED."""
    return_code, result = invoke_verifier(
        verifier, raw_bytes, journal_bytes, trusted_bytes, proof_path, optimized
    )
    if result.get("status") != "VERIFIED" or return_code != 0:
        return return_code, result, None, []

    if result.get("operational_status") != "INCOMPLETE":
        raise AssertionError("structural verification must not imply operational acceptance")

    raw = strict_loads(raw_bytes)
    trusted = strict_loads(trusted_bytes)
    selector_scope = trusted["selector_scope"]
    sample_digest = selector_scope["sample_digest"]
    if trusted["journal2_digest"] != hashlib.sha256(journal_bytes).hexdigest():
        raise AssertionError("trusted scope does not bind exact journal/2 bytes")

    proof_result = result["result"]
    if mode == "one":
        owners = [proof_result.get("owner")]
    else:
        owners = proof_result.get("optima")
    if not owners or any(not canonical_owner(owner, len(raw["alphabet"])) for owner in owners):
        raise AssertionError("verifier did not return canonical original-alphabet owner arrays")
    if len({tuple(owner) for owner in owners}) != len(owners):
        raise AssertionError("duplicate candidate owner")
    if any(len(raw["alphabet"]) - len(set(owner)) != proof_result["optimum"]
           for owner in owners):
        raise AssertionError("registered owner cost differs from verified optimum")

    ledger = open_gateway(raw)
    if type(ledger) is not RegisteredLedger:
        raise AssertionError("open_gateway did not return the authoritative core RegisteredLedger")
    if ledger.export() != journal_bytes:
        raise AssertionError("core's empty journal/2 export differs from verifier input bytes")

    request_ids = []
    attempt_ids = []
    candidate_keys = set()
    for index, owner in enumerate(owners):
        request_id = "p3-" + mode + "-" + str(index) + "-" + sample_digest[:12]
        attempt_id = "attempt-p3-" + mode + "-" + str(index) + "-" + sample_digest[:12]
        if request_id == attempt_id:
            raise AssertionError("request and attempt IDs collapsed")
        request_ids.append(request_id)
        attempt_ids.append(attempt_id)
        key = (sample_digest, tuple(owner))
        if key in candidate_keys:
            raise AssertionError("candidate identity is not unique")
        candidate_keys.add(key)

        request = ledger.register(owner, request_id, attempt_id)
        if request["owner"] != owner or request["scope"] != selector_scope:
            raise AssertionError("registered candidate lost owner or trusted scope binding")
        if request["request_id"] != request_id or request["attempt_id"] != attempt_id:
            raise AssertionError("request and global attempt identities were rebound")
        if ledger.attempt_status(request_id, attempt_id) != "PENDING":
            raise AssertionError("newly registered candidate is not pending")

    if len(set(request_ids)) != len(request_ids) or len(set(attempt_ids)) != len(attempt_ids):
        raise AssertionError("duplicate request or global attempt ID")
    if not set(request_ids).isdisjoint(attempt_ids):
        raise AssertionError("request IDs and global attempt IDs share a namespace")
    if set(ledger.pending_candidates) != set(request_ids):
        raise AssertionError("candidate registration did not remain pending")

    journal_after = ledger.export()
    decoded = strict_loads(journal_after)
    if decoded["version"] != "selector-v2-journal/2":
        raise AssertionError("journal version changed")
    events = decoded["events"]
    if len(events) != len(owners) or any(event["event"] != "REGISTER" for event in events):
        raise AssertionError("unexpected journal transaction or duplicate ledger path")
    if any(not event["records"] or
           any(record.get("kind") != "REQUEST" for record in event["records"])
           for event in events):
        raise AssertionError("journal contains non-registration or proof records")
    if contains_forbidden_key(decoded):
        raise AssertionError("certificate/frontier material leaked into journal/2")
    proof_pin = pins_file(proof_path)
    if proof_pin["bytes"] <= len(journal_after):
        raise AssertionError("certificate is unexpectedly smaller than the journal export")
    if proof_pin["sha256"].encode() in journal_after:
        raise AssertionError("certificate digest leaked into journal/2")
    return return_code, result, ledger, owners


class NativeP3Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        evidence_value = os.environ.get("P3_EVIDENCE_ROOT")
        proof_value = os.environ.get("P3_PROOF_ROOT")
        if not evidence_value or not proof_value:
            raise RuntimeError("P3_EVIDENCE_ROOT and P3_PROOF_ROOT are required")
        cls.evidence_root = Path(evidence_value)
        cls.proof_root = Path(proof_value)
        cls.verifier = cls.proof_root / "tests" / "reference" / "p3_frontier_verifier.py"
        if not cls.verifier.is_file():
            raise RuntimeError("pinned independent verifier is missing: " + str(cls.verifier))
        cls.fixture_root = Path(__file__).parent / "fixtures" / "p3"
        cls.fixture_manifest = strict_loads((cls.fixture_root / "manifest.json").read_bytes())

    def artifact(self, case, mode):
        root = self.evidence_root / ("p3-m2-" + case + "-" + mode)
        if not root.is_dir():
            raise AssertionError("missing actual producer workflow artifact: " + str(root))
        return root

    def test_actual_certificates_verify_before_core_registration(self):
        optimized = sys.flags.optimize > 0
        requested = set(os.environ.get(
            "P3_CASE_MODES",
            "tiny_choice:one,tiny_choice:all,small_choice:one,small_choice:all",
        ).split(","))
        allowed = {"tiny_choice:one", "tiny_choice:all", "small_choice:one", "small_choice:all"}
        if "tiny_choice:one" not in requested or not requested <= allowed:
            raise RuntimeError("P3_CASE_MODES must include tiny_choice:one and contain only known case/modes")
        for case in ("tiny_choice", "small_choice"):
            for mode in ("one", "all"):
                if case + ":" + mode not in requested:
                    continue
                with self.subTest(case=case, mode=mode, optimized=optimized):
                    root = self.artifact(case, mode)
                    summary = strict_loads((root / "summary.json").read_bytes())
                    self.assertEqual(summary["case"], case)
                    self.assertEqual(summary["mode"], mode)
                    self.assertEqual(summary["structural_gate"], "PASS")
                    self.assertEqual(summary["operational_status"], "INCOMPLETE")
                    self.assertIs(summary["normal_optimized_equal"], True)
                    self.assertIs(summary["checkpoint_resume_equal"], True)

                    raw_bytes = (root / "raw.json").read_bytes()
                    journal_bytes = (root / "journal.json").read_bytes()
                    trusted_bytes = (root / "trusted.json").read_bytes()
                    certificate_path = root / "normal.json"
                    raw_pin = pins_file(root / "raw.json")
                    journal_pin = pins_file(root / "journal.json")
                    trusted_pin = pins_file(root / "trusted.json")
                    certificate_pin = pins_file(certificate_path)
                    self.assertEqual(
                        (certificate_pin["sha256"], certificate_pin["git_blob_calculated"]),
                        CERT_PINS[(case, mode)],
                    )
                    self.assertEqual(raw_pin, summary["raw"])
                    self.assertEqual(journal_pin, summary["journal"])
                    self.assertEqual(trusted_pin, summary["trusted_scope"])
                    self.assertEqual(certificate_pin, summary["phases"]["normal"]["certificate"])
                    self.assertEqual(summary["phases"]["normal"]["exit"], 0)
                    self.assertEqual(summary["phases"]["optimized"]["exit"], 0)
                    self.assertEqual(
                        summary["phases"]["normal"]["certificate"],
                        summary["phases"]["optimized"]["certificate"],
                    )
                    self.assertEqual(raw_pin["sha256"], RAW_SHA256[case])

                    fixture_path = self.fixture_root / (case + ".raw.json")
                    self.assertEqual(raw_bytes, fixture_path.read_bytes())
                    if (root / "optimized.json").exists():
                        self.assertEqual(pins_file(root / "optimized.json"), certificate_pin)

                    rc, result, ledger, owners = verify_then_register(
                        self.verifier, raw_bytes, journal_bytes, trusted_bytes,
                        certificate_path, mode, optimized,
                    )
                    self.assertEqual(rc, 0, result)
                    self.assertEqual(result["status"], "VERIFIED", result)
                    self.assertEqual(result["operational_status"], "INCOMPLETE")
                    self.assertIsNotNone(ledger)
                    self.assertTrue(owners)
                    self.assertEqual(len(ledger.pending_candidates), len(owners))

                    # A verified real candidate can still receive UNKNOWN; it
                    # remains pending and cannot become a structural closure.
                    unknown_ledger = open_gateway(strict_loads(raw_bytes))
                    owner = owners[0]
                    request_id = "unknown-" + case + "-" + mode
                    attempt_id = "unknown-attempt-" + case + "-" + mode
                    q = unknown_ledger.register(owner, request_id, attempt_id)
                    self.assertNotEqual(q["request_id"], q["attempt_id"])
                    self.assertEqual(unknown_ledger.ingest(request_id, attempt_id, b"{}"), "UNKNOWN")
                    self.assertEqual(unknown_ledger.attempt_status(request_id, attempt_id), "UNKNOWN")
                    self.assertIn(request_id, unknown_ledger.pending_candidates)

    def test_invalid_certificate_never_opens_or_registers_candidate(self):
        root = self.artifact("tiny_choice", "one")
        raw_bytes = (root / "raw.json").read_bytes()
        journal_bytes = (root / "journal.json").read_bytes()
        trusted_bytes = (root / "trusted.json").read_bytes()
        with tempfile.TemporaryDirectory(prefix="p3-invalid-proof-") as directory:
            invalid_path = Path(directory) / "invalid.json"
            invalid_path.write_bytes(b"not-json")
            rc, result, ledger, owners = verify_then_register(
                self.verifier, raw_bytes, journal_bytes, trusted_bytes,
                invalid_path, "one", sys.flags.optimize > 0,
            )
        self.assertEqual(rc, 1, result)
        self.assertEqual(result["status"], "INVALID", result)
        self.assertIsNone(ledger)
        self.assertEqual(owners, [])


if __name__ == "__main__":
    unittest.main()
