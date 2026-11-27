"""Combined-tree admission checks for opt-in sparse v2 and unapproved v3."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

import test_p3_m3_integration as m3


class SparseAdmission(m3.M3Integration):
    def produce(self, paths, mode, output, *options):
        if not options:
            return super().produce(paths, mode, output)
        process = subprocess.run(
            [sys.executable, *m3.FLAGS, "-m", "selector_v2.edr_m4",
             "--raw", str(paths["raw"]), "--scope", str(paths["scope"]),
             "--mode", mode, "--out", str(output), "--seconds", "30",
             "--sparse", *options],
            capture_output=True, timeout=45,
        )
        self.assertEqual(process.returncode, 0, process.stderr.decode(errors="replace"))
        stats = m3.strict_loads(process.stdout)
        self.assertEqual(stats["operational_status"], "INCOMPLETE")
        return stats

    def replay(self, case, mode, paths, fresh, checkpoint, resumed, *, comparison=None):
        comparison = fresh if comparison is None else comparison
        normal, optimized = (comparison, fresh) if sys.flags.optimize else (fresh, comparison)
        inputs = {**paths, "normal": normal, "optimized": optimized,
                  "checkpoint": checkpoint, "resumed": resumed}
        args = [arg for name, path in inputs.items() for arg in ("--" + name, str(path))]
        process = subprocess.run(
            [sys.executable, *m3.FLAGS, str(self.proof / "p3_m3_artifact_replay.py"),
             "--case", "nonempty_journal" if case == "journal_root" else case,
             "--mode", mode, "--seconds", "120", "--proof-cap", "65536",
             "--sparse-exact", *args],
            cwd=self.proof, env=self.independent_env, capture_output=True, timeout=135,
        )
        self.assertTrue(process.stdout, process.stderr.decode(errors="replace"))
        report = m3.strict_loads(process.stdout)
        self.assertEqual(process.returncode,
                         {"VERIFIED": 0, "INVALID": 1, "INCOMPLETE": 2}[report["status"]],
                         report)
        return report

    def test_v3_has_no_registration_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            ledger, paths = self.inputs(directory, "journal_root")
            before = ledger.export()
            proof = m3.strict_loads(self.retained("journal_root", "one.cert.json"))
            proof["format"] = "p3-region-frontier/v3"
            path = directory / "v3.json"
            path.write_bytes(json.dumps(proof).encode("ascii"))
            with patch.object(ledger, "register", wraps=ledger.register) as register:
                report, count = self.admit(
                    ledger, "journal_root", "one", paths, path, path, path,
                )
                self.assertEqual((report["status"], count), ("INVALID", 0), report)
                self.assertNotIn("result", report)
                register.assert_not_called()
            self.assertEqual(ledger.export(), before)
