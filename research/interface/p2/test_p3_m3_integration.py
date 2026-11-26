"""Opt-in offline replay and admission of the pinned native M3 fixtures."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from gateway import open_gateway
from selector_v2.component_closure import component_closure
from selector_v2.core import Sample
from selector_v2.registered_ledger import RegisteredLedger
from test_p3_native_integration import canonical_owner, contains_forbidden_key, pins_file, strict_loads


CASES = {
    # Literal RGS census size, optimum cost, number of optima.
    "tiny_choice": (203, 2, 4),
    "small_choice": (4213597, 4, 16),
    "mixed_path": (52, 1, 3),
    "journal_root": (203, 2, 2),
}
MANIFESTS = {
    "normal/manifest.json": ("8179a80dcd4d93844a86d2cfb19b0e87dcc2a79d", False),
    "optimized-manifest.json": ("d91c253634dd988b990be1f073705e0e8989ffe6", True),
}
V1 = "p3-region-frontier/v1"
V2 = "p3-region-frontier/v2"
CROSS = "CROSS_SUPPORT_LEX_V1"
FLAGS = ["-B"] + ["-O"] * bool(sys.flags.optimize)


class M3Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = Path(os.environ["P3_M3_EVIDENCE"]).resolve()
        cls.proof = Path(os.environ["P3_M3_PROOF"]).resolve()
        cls.independent_env = os.environ.copy()
        cls.independent_env.pop("PYTHONPATH", None)
        cls.independent_env["PYTHONNOUSERSITE"] = "1"
        cls.manifests = []
        for name, (blob, optimized) in MANIFESTS.items():
            path = cls.evidence / name
            if pins_file(path)["git_blob_calculated"] != blob:
                raise ValueError(f"retained manifest blob mismatch: {name}")
            manifest = strict_loads(path.read_bytes())
            if manifest["python"] != "3.13.5" or manifest["optimized"] is not optimized:
                raise ValueError(f"unexpected retained interpreter: {name}")
            cls.manifests.append(manifest["cases"])
        if sys.version_info[:3] != (3, 13, 5):
            raise RuntimeError("CPython 3.13.5 required")
        print(f"M3_RUNTIME {sys.version.split()[0]} optimized={bool(sys.flags.optimize)}", flush=True)

    def retained(self, case, name):
        path = self.evidence / "normal" / case / name
        data = path.read_bytes()
        pin = dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        for manifest in self.manifests:
            self.assertEqual(pin, manifest[case]["files"][name], (case, name))
        return data

    def inputs(self, directory, case):
        raw = self.retained(case, "raw.json")
        ledger = open_gateway(strict_loads(raw))
        self.assertIs(type(ledger), RegisteredLedger)
        if case == "journal_root":
            closure = component_closure(Sample.from_input(strict_loads(raw)))
            self.assertEqual(closure["state"], "FIXPOINT")
            ledger.append_raw(closure["records"])
        journal = ledger.export()
        self.assertEqual(journal, self.retained(case, "journal.json"))
        self.assertEqual(ledger.pending_candidates, ())
        inputs = {
            "raw": raw,
            "journal": journal,
            "scope": self.retained(case, "trusted.json"),
        }
        paths = {}
        for name, data in inputs.items():
            paths[name] = directory / f"{name}.json"
            paths[name].write_bytes(data)
        return ledger, paths

    def produce(self, paths, mode, output, *options):
        process = subprocess.run(
            [sys.executable, *FLAGS, "-m", "selector_v2.edr_m3",
             "--raw", str(paths["raw"]), "--scope", str(paths["scope"]),
             "--mode", mode, "--out", str(output), "--seconds", "30", *options],
            capture_output=True, timeout=45,
        )
        self.assertEqual(process.returncode, 0, process.stderr.decode(errors="replace"))
        stats = strict_loads(process.stdout)
        self.assertEqual(stats["operational_status"], "INCOMPLETE")
        return stats

    def replay(self, case, mode, paths, fresh, checkpoint, resumed, *, comparison=None):
        proof_case = "nonempty_journal" if case == "journal_root" else case
        # The other interpreter's manifest pins the retained comparison bytes.
        # Each matrix job still executes both producer paths in its own interpreter.
        comparison = fresh if comparison is None else comparison
        normal, optimized = (comparison, fresh) if sys.flags.optimize else (fresh, comparison)
        flags = {
            **paths, "normal": normal, "optimized": optimized,
            "checkpoint": checkpoint, "resumed": resumed,
        }
        args = [arg for name, path in flags.items() for arg in ("--" + name, str(path))]
        process = subprocess.run(
            [sys.executable, *FLAGS, str(self.proof / "p3_m3_artifact_replay.py"),
             "--case", proof_case, "--mode", mode, "--seconds", "120",
             "--proof-cap", "65536", *args],
            cwd=self.proof, env=self.independent_env, capture_output=True, timeout=135,
        )
        self.assertTrue(process.stdout, process.stderr.decode(errors="replace"))
        report = strict_loads(process.stdout)
        self.assertEqual(process.returncode, {"VERIFIED": 0, "INVALID": 1, "INCOMPLETE": 2}[report["status"]],
                         report)
        return report

    def admit(self, ledger, case, mode, paths, fresh, checkpoint, resumed, *, comparison=None):
        report = self.replay(case, mode, paths, fresh, checkpoint, resumed, comparison=comparison)
        if report["status"] != "VERIFIED":
            return report, 0

        self.assertEqual(report["operational_status"], "INCOMPLETE")
        self.assertEqual(report["complete"]["operational_status"], "INCOMPLETE")
        self.assertEqual(report["completed_resume_status"], "VERIFIED")
        for name, status in (("checkpoint", "INCOMPLETE"), ("false_exhausted", "INVALID"),
                             ("byte_cap", "INCOMPLETE")):
            self.assertEqual(report["controls"][name]["status"], status)
            self.assertNotIn("result", report["controls"][name])

        raw = strict_loads(paths["raw"].read_bytes())
        census, optimum, optima_count = CASES[case]
        truth = report["census"]["result"]
        self.assertEqual((report["census"]["visited"], truth["optimum"], len(truth["optima"])),
                         (census, optimum, optima_count))
        expected_root = [0, 0, 2, 3, 4, 5] if case == "journal_root" else list(range(len(raw["alphabet"])))
        self.assertEqual(report["root_owner"], expected_root)
        trusted = strict_loads(paths["scope"].read_bytes())
        before = ledger.export()
        before_transactions = ledger.journal
        self.assertEqual(before, paths["journal"].read_bytes())
        self.assertEqual(hashlib.sha256(before).hexdigest(), trusted["journal2_digest"])
        before_events = strict_loads(before)["events"]
        self.assertEqual([event["event"] for event in before_events],
                         ["RAW"] if case == "journal_root" else [])
        scope = trusted["selector_scope"]

        verified = report["complete"]["result"]
        owners = verified["optima"] if mode == "all" else [verified["owner"]]
        self.assertEqual(len(owners), optima_count if mode == "all" else 1)
        self.assertEqual(len({tuple(owner) for owner in owners}), len(owners))
        for owner in owners:
            self.assertTrue(canonical_owner(owner, len(raw["alphabet"])))
            self.assertEqual(len(owner) - len(set(owner)), optimum)
            self.assertTrue(all(owner[i] == owner[root] for i, root in enumerate(expected_root)))
        requests = []
        for index, owner in enumerate(owners):
            request_id = f"p3-m3-{case}-{mode}-{index}"
            attempt_id = f"attempt-{request_id}"
            registered = ledger.register(owner, request_id, attempt_id)
            self.assertEqual((registered["owner"], registered["scope"]), (owner, scope))
            self.assertEqual((registered["request_id"], registered["attempt_id"]),
                             (request_id, attempt_id))
            self.assertEqual(ledger.attempt_status(request_id, attempt_id), "PENDING")
            requests.append((request_id, attempt_id))

        candidate_ids = {request for request, _ in requests}
        self.assertEqual(set(ledger.pending_candidates), candidate_ids)
        after = strict_loads(ledger.export())
        self.assertEqual(ledger.journal[:len(before_transactions)], before_transactions)
        self.assertEqual(after["version"], "selector-v2-journal/2")
        self.assertEqual(after["events"][:len(before_events)], before_events)
        delta = after["events"][len(before_events):]
        self.assertEqual(len(delta), len(owners))
        for event in delta:
            self.assertEqual(event["event"], "REGISTER")
            self.assertEqual([record["kind"] for record in event["records"]], ["REQUEST"])
        self.assertFalse(contains_forbidden_key(after))
        proof_digest = report["byte_pins"]["normal"]["sha256"].encode()
        self.assertNotIn(proof_digest, ledger.export())

        request_id, attempt_id = requests[0]
        self.assertEqual(ledger.ingest(request_id, attempt_id, b"{}"), "UNKNOWN")
        self.assertEqual(ledger.attempt_status(request_id, attempt_id), "UNKNOWN")
        self.assertEqual(set(ledger.pending_candidates), candidate_ids)
        final_bytes = ledger.export()
        final = strict_loads(final_bytes)
        self.assertEqual(final["events"][:-1], after["events"])
        quarantine = final["events"][-1]
        self.assertEqual(quarantine["event"], "QUARANTINE")
        observation, = quarantine["records"]
        self.assertEqual(observation["kind"], "OBSERVATION")
        self.assertEqual(observation["payload"]["status"], "UNKNOWN")
        self.assertIsNone(observation["payload"]["feedback"])
        self.assertFalse(contains_forbidden_key(final))
        self.assertNotIn(proof_digest, final_bytes)
        return report, len(delta)

    def test_all_native_modes(self):
        counts = {}
        for case in CASES:
            for mode in ("one", "all"):
                with self.subTest(case=case, mode=mode), tempfile.TemporaryDirectory() as tmp:
                    directory = Path(tmp)
                    ledger, paths = self.inputs(directory, case)
                    fresh = directory / "fresh.json"
                    checkpoint = directory / "partial.json"
                    resumed = directory / "resumed.json"
                    complete = self.produce(paths, mode, fresh, "--split-rule", CROSS)
                    self.assertEqual(complete["status"], "EXHAUSTED")
                    partial = self.produce(paths, mode, checkpoint, "--split-rule", CROSS, "--entries", "1")
                    self.assertEqual((partial["status"], partial["stop_reason"]), ("PARTIAL", "ENTRY_CAP"))
                    self.assertEqual(fresh.read_bytes(), self.retained(case, f"{mode}.cert.json"))
                    self.assertEqual(checkpoint.read_bytes(), self.retained(case, f"{mode}.partial.json"))
                    restart = self.produce(paths, mode, resumed, "--split-rule", CROSS, "--resume", str(checkpoint))
                    self.assertEqual(restart["status"], "EXHAUSTED")
                    self.assertGreater(restart["resumed_nodes"], 0)
                    self.assertEqual(resumed.read_bytes(), self.retained(case, f"{mode}.resumed.json"))
                    self.assertEqual(resumed.read_bytes(), fresh.read_bytes())
                    comparison = self.evidence / "normal" / case / f"{mode}.cert.json"
                    report, count = self.admit(
                        ledger, case, mode, paths, fresh, checkpoint, resumed, comparison=comparison,
                    )
                    self.assertEqual(report["status"], "VERIFIED", report)
                    counts[case, mode] = count
                    print("M3_CASE_PASS " + json.dumps(dict(
                        case=case, mode=mode, registrations=count,
                        root_owner=report["root_owner"], pins=report["byte_pins"],
                        replay={key: report["complete"][key] for key in
                                ("status", "nodes_checked", "work_units", "exact_checks")},
                        controls={name: control["status"] for name, control in report["controls"].items()},
                        rgs=report["census"], unknown_pending=True, journal_version="selector-v2-journal/2",
                        pre_registration_events=["RAW"] if case == "journal_root" else [],
                    ), sort_keys=True), flush=True)
        self.assertEqual(len(counts), 8)
        self.assertEqual(sum(counts.values()), 29)
        print(f"M3_MODE_PASS optimized={bool(sys.flags.optimize)} cases=8 registrations=29", flush=True)

    def test_rejected_proofs_cannot_register(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            case, mode = "journal_root", "one"
            ledger, paths = self.inputs(directory, case)
            before = ledger.export()
            partial = self.retained(case, "one.partial.json")
            unapproved = strict_loads(self.retained(case, "one.cert.json"))
            unapproved["format"] = "p3-region-frontier/unapproved"
            scenarios = (
                ("partial", partial, "INCOMPLETE", "unresolved frontier"),
                ("malformed", b"{", "INVALID", None),
                ("unapproved-format", json.dumps(unapproved).encode(), "INVALID", "format"),
                ("wrong-mode", self.retained(case, "all.cert.json"), "INVALID", "unexpected mode"),
            )
            for name, data, status, reason in scenarios:
                with self.subTest(probe=name), patch.object(ledger, "register", wraps=ledger.register) as register:
                    proof = directory / "probe.json"
                    proof.write_bytes(data)
                    result, count = self.admit(ledger, case, mode, paths, proof, proof, proof)
                    self.assertEqual(result["status"], status, result)
                    self.assertNotIn("result", result)
                    if reason is not None:
                        self.assertIn(reason, result["reason"])
                    self.assertEqual(count, 0)
                    register.assert_not_called()
                    self.assertEqual(ledger.export(), before)
                    self.assertEqual(ledger.pending_candidates, ())
                    print(f"M3_REJECTED probe={name} status={status} registrations=0", flush=True)

    def test_default_producer_and_reader_still_use_v1(self):
        # The independent verifier CLI leaves expected_format/mode optional.
        # Exercise the pinned API guards in the isolated proof process.
        verifier_command = """
from pathlib import Path
import sys
from p3_frontier_verifier import verify_frontier, canonical
raw, journal, scope, v1, v2 = (Path(p).read_bytes() for p in sys.argv[1:])
def verify(proof):
    return verify_frontier(raw, journal, scope, proof,
                           expected_format="p3-region-frontier/v1", expected_mode="one")
print(canonical([verify(v1), verify(v2)]).decode("ascii"))
"""
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            case = "tiny_choice"
            _, paths = self.inputs(directory, case)
            v1 = directory / "v1.json"
            self.assertEqual(self.produce(paths, "one", v1)["status"], "EXHAUSTED")
            self.assertEqual(strict_loads(v1.read_bytes())["format"], V1)
            v2 = directory / "v2.json"
            v2.write_bytes(self.retained(case, "one.cert.json"))
            self.assertEqual(strict_loads(v2.read_bytes())["format"], V2)
            process = subprocess.run(
                [sys.executable, *FLAGS, "-c", verifier_command, *map(str, paths.values()), str(v1), str(v2)],
                cwd=self.proof, env=self.independent_env, capture_output=True, timeout=45,
            )
            self.assertEqual(process.returncode, 0, process.stderr.decode(errors="replace"))
            accepted, rejected = strict_loads(process.stdout)
            retained_truth = strict_loads(self.retained(case, "rgs.json"))["result"]
            self.assertEqual(accepted["status"], "VERIFIED", accepted)
            self.assertEqual(accepted["result"]["optimum"], retained_truth["optimum"])
            self.assertIn(accepted["result"]["owner"], retained_truth["optima"])
            self.assertEqual(rejected["status"], "INVALID", rejected)
            self.assertEqual(rejected["reason"], "unexpected format")
            self.assertNotIn("result", rejected)
            print("M3_V1_REGRESSION default=VERIFIED v2_without_opt_in=INVALID", flush=True)
