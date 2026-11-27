"""Tests for the benchmark adapter, isolation and fail-closed reporting only."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from argparse import Namespace

import p3_harness as h


COUNTERS = {
    "generated_regions": 7, "expanded_regions": 5, "exact_checks": 11,
    "pruned_regions": 2, "frontier_size": 0, "work_units": 13, "entry_count": 7,
}
VCOUNTERS = {"regions_replayed": 7, "exact_checks": 11, "frontier_size": 0}


class P3HarnessTests(unittest.TestCase):
    def test_raw_only_schema_preserves_original_order_and_empty_words(self):
        raw = json.dumps({"alphabet": ["z", "a", "unused"], "positive": [["z", "a"], []], "negative": [["a", "z"]]}, separators=(",", ":")).encode()
        data = h.validate_raw_input(raw)
        self.assertEqual(data["alphabet"], ["z", "a", "unused"])
        self.assertEqual(data["positive"], [["z", "a"], []])

    def test_extra_reference_fields_are_rejected(self):
        raw = b'{"alphabet":["a"],"positive":[],"negative":[],"optimum":0}'
        with self.assertRaises(h.HarnessError):
            h.validate_raw_input(raw)

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaises(h.HarnessError):
            h.load_json_bytes(b'{"alphabet":[],"alphabet":[],"positive":[],"negative":[]}')

    def test_invalid_trace_symbol_is_rejected(self):
        raw = b'{"alphabet":["a"],"positive":[["b"]],"negative":[]}'
        with self.assertRaises(h.HarnessError):
            h.validate_raw_input(raw)

    def test_solver_and_verifier_counter_envelopes_are_strict(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            s = root / "solver.json"
            v = root / "verifier.json"
            s.write_text(json.dumps({"schema": h.SOLVER_SCHEMA, "status": "COMPLETE_CANDIDATE", "counters": COUNTERS}))
            v.write_text(json.dumps({"schema": h.VERIFIER_SCHEMA, "status": "VERIFIED", "counters": VCOUNTERS}))
            self.assertEqual(h.validate_solver_result(s)["status"], "COMPLETE_CANDIDATE")
            self.assertEqual(h.validate_verifier_result(v)["status"], "VERIFIED")
            bad = dict(COUNTERS, generated_regions=True)
            s.write_text(json.dumps({"schema": h.SOLVER_SCHEMA, "status": "COMPLETE_CANDIDATE", "counters": bad}))
            with self.assertRaises(h.HarnessError):
                h.validate_solver_result(s)

    def test_command_template_drops_optional_resume_token(self):
        spec = {"argv": ["python", "--input", "{input}", "{resume_flag}"]}
        values = {"input": "/tmp/in.json", "resume_flag": ""}
        self.assertEqual(h.render_argv(spec, values), ["python", "--input", "/tmp/in.json"])
        values["resume_flag"] = "--resume"
        self.assertEqual(h.render_argv(spec, values)[-1], "--resume")

    def test_complete_search_is_independently_verified_and_restartable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            input_dir = root / "inputs"
            input_dir.mkdir()
            raw = b'{"alphabet":["a","b"],"positive":[["a"]],"negative":[["b"]]}\n'
            (input_dir / "tiny.json").write_bytes(raw)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([{"case": "tiny", "input_sha256": hashlib.sha256(raw).hexdigest()}]))
            solver = root / "fake_solver.py"
            solver.write_text('''import argparse, hashlib, json\nfrom pathlib import Path\np=argparse.ArgumentParser(); p.add_argument("--input"); p.add_argument("--certificate"); p.add_argument("--checkpoint"); p.add_argument("--result"); p.add_argument("--work-cap",type=int); p.add_argument("--entry-cap",type=int); p.add_argument("--seconds"); p.add_argument("--memory-mib"); p.add_argument("--resume",action="store_true"); a=p.parse_args()\nif a.work_cap < 5 and not a.resume:\n Path(a.checkpoint).write_text("pending")\n status="INCOMPLETE"\nelse:\n Path(a.certificate).write_bytes(b"CERT:"+hashlib.sha256(Path(a.input).read_bytes()).hexdigest().encode())\n status="COMPLETE_CANDIDATE"\nc={"generated_regions":7,"expanded_regions":5,"exact_checks":11,"pruned_regions":2,"frontier_size":0,"work_units":13,"entry_count":7}\nPath(a.result).write_text(json.dumps({"schema":"p3-benchmark-solver/1","status":status,"counters":c},sort_keys=True))\n''')
            verifier = root / "fake_verifier.py"
            verifier.write_text('''import argparse, json\nfrom pathlib import Path\np=argparse.ArgumentParser(); p.add_argument("--input"); p.add_argument("--certificate"); p.add_argument("--result"); a=p.parse_args()\nstatus="VERIFIED" if Path(a.certificate).read_bytes().startswith(b"CERT:") else "INVALID"\nc={"regions_replayed":7,"exact_checks":11,"frontier_size":0}\nPath(a.result).write_text(json.dumps({"schema":"p3-benchmark-verifier/1","status":status,"counters":c},sort_keys=True))\n''')
            config = root / "config.json"
            config.write_text(json.dumps({
                "schema": "p3-benchmark-adapter/1",
                "solver": {"argv": [sys.executable, str(solver), "--input", "{input}", "--certificate", "{certificate}", "--checkpoint", "{checkpoint}", "--result", "{result}", "--work-cap", "{work_cap}", "--entry-cap", "{entry_cap}", "--seconds", "{seconds}", "--memory-mib", "{memory_mib}", "{resume_flag}"], "resume_flag": "--resume"},
                "verifier": {"argv": [sys.executable, str(verifier), "--input", "{input}", "--certificate", "{certificate}", "--result", "{result}"]},
            }))
            args = Namespace(
                output=root / "run", case="tiny", manifest=manifest, input_dir=input_dir,
                config=config, python_mode="normal", seconds=5.0, memory_mib=512,
                work_cap=100, entry_cap=100, repeat=2, restart_probe=True, restart_work_cap=1,
            )
            summary = h.run_case(args)
            self.assertEqual(summary["status"], "VERIFIED")
            self.assertEqual(summary["deterministic_replay_status"], "PASS")
            self.assertEqual(summary["restartability_status"], "PASS")
            self.assertEqual(len(summary["solver_runs"]), 2)
            self.assertEqual(len(summary["verifier_runs"]), 2)
            self.assertFalse(summary["evaluation_references_read"])
            self.assertEqual(summary["solver_runs"][0]["result"]["counters"]["generated_regions"], 7)
            self.assertIsNotNone(summary["solver_peak_rss_kib_max"])
            self.assertIsNotNone(summary["verifier_peak_rss_kib_max"])

    def test_missing_original_input_is_not_run_not_incomplete(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            raw = b'{"alphabet":["a"],"positive":[],"negative":[]}\n'
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([{"case": "missing", "input_sha256": hashlib.sha256(raw).hexdigest()}]))
            args = Namespace(
                output=root / "run", case="missing", manifest=manifest,
                input_dir=root / "inputs", config=root / "missing-config.json",
                python_mode="normal", seconds=1.0, memory_mib=512, work_cap=10,
                entry_cap=10, repeat=1, restart_probe=False, restart_work_cap=1,
            )
            summary = h.run_case(args)
            self.assertEqual(summary["status"], "NOT RUN")
            self.assertEqual(summary["not_run_reason"], "raw input file unavailable")

    def test_fixture_hash_mismatch_is_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            input_dir = root / "inputs"
            input_dir.mkdir()
            raw = b'{"alphabet":["a"],"positive":[],"negative":[]}\n'
            (input_dir / "case.json").write_bytes(raw)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([{"case": "case", "input_sha256": "0" * 64}]))
            args = Namespace(
                output=root / "run", case="case", manifest=manifest,
                input_dir=input_dir, config=root / "missing-config.json",
                python_mode="normal", seconds=1.0, memory_mib=512, work_cap=10,
                entry_cap=10, repeat=1, restart_probe=False, restart_work_cap=1,
            )
            summary = h.run_case(args)
            self.assertEqual(summary["status"], "INVALID")
            self.assertIn("SHA-256", summary["input_error"])


if __name__ == "__main__":
    unittest.main()
