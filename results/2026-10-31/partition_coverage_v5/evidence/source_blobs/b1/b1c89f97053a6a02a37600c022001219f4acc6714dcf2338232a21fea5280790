"""CLI-level status and exit-code checks. Run the driver only via capture.py."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
provider = HERE / "known_k_qexact_v2.py"
valid_input = HERE / "sanity_inputs_v1.json"
invalid_input = HERE / "sanity_invalid_v1.json"

def call(*args):
    process = subprocess.run([sys.executable, "-B", "-X", "utf8", str(provider), *map(str, args)],
                             cwd=HERE, capture_output=True, text=True, encoding="utf-8")
    return process.returncode, json.loads(process.stdout)

found_code, found = call(str(valid_input), "--local-word-cap", "2", "--max-solutions", "1")
deadline_code, deadline = call(str(valid_input), "--deadline-seconds", "0")
invalid_code, invalid = call(str(invalid_input))
assert found_code == 0 and found["status"] == "found" and not found["complete"]
assert deadline_code == 3 and deadline["status"] == "incomplete" and not deadline["complete"]
assert invalid_code == 2 and invalid["status"] == "invalid_input"
print(json.dumps({"found_limit_exit": found_code, "found_limit_status": found["status"],
                  "immediate_deadline_exit": deadline_code,
                  "immediate_deadline_status": deadline["status"],
                  "invalid_input_exit": invalid_code,
                  "invalid_input_status": invalid["status"]}, sort_keys=True))
