"""Combined root-promotion CLI checks; invoke this driver only via capture.py."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLI = HERE / "public_cli_v1.py"
sample = HERE / "sanity_inputs_v1.json"
certificate_input = HERE / "public_cli_certificate_input_v1.json"
invalid = HERE / "sanity_invalid_v1.json"

def call(path, *args):
    process = subprocess.run([sys.executable, "-B", "-X", "utf8", str(CLI), str(path), *args],
                             cwd=HERE, capture_output=True, text=True, encoding="utf-8")
    return process.returncode, json.loads(process.stdout)

exact_code, exact = call(sample, "--max-solutions", "all")
cert_code, cert = call(certificate_input, "--mode", "certificate", "--q", "2")
abstain_code, abstain = call(sample, "--mode", "certificate", "--q", "2")
hybrid_code, hybrid = call(sample, "--mode", "hybrid", "--q", "2")
timeout_code, timeout = call(sample, "--mode", "hybrid", "--q", "2", "--timeout-seconds", "0")
invalid_q_code, invalid_q = call(sample, "--q", "0")
invalid_data_code, invalid_data = call(invalid)

assert exact_code == 0 and exact["complete"] and exact["search_exhausted"]
assert exact["model_class"] == "general_regular_product" and len(exact["solutions"]) == 6
assert cert_code == 0 and cert["status"] == "found" and cert["uniqueness"] == "unique"
assert abstain_code == 4 and abstain["status"] == "insufficient_coverage"
assert hybrid_code == 0 and hybrid["fallback_trigger"] == "insufficient_coverage"
assert hybrid["status"] == "found" and hybrid["complete"] and len(hybrid["solutions"]) == 1
assert timeout_code == 3 and timeout["status"] == "incomplete" and not timeout["complete"]
assert "fallback_trigger" not in timeout
assert invalid_q_code == 2 and invalid_q["status"] == "invalid_input"
assert invalid_data_code == 2 and invalid_data["status"] == "invalid_input"
print(json.dumps({
    "exact_all_unrestricted": {"code": exact_code, "count": len(exact["solutions"]),
                               "uniqueness": exact["uniqueness"]},
    "certificate_success": {"code": cert_code, "status": cert["status"],
                            "uniqueness": cert["uniqueness"]},
    "certificate_abstention": {"code": abstain_code, "status": abstain["status"]},
    "hybrid_fallback": {"code": hybrid_code, "status": hybrid["status"],
                         "trigger": hybrid["fallback_trigger"],
                         "count": len(hybrid["solutions"])},
    "hybrid_deadline": {"code": timeout_code, "status": timeout["status"],
                        "fallback": "none"},
    "invalid_q": {"code": invalid_q_code, "status": invalid_q["status"]},
    "invalid_data": {"code": invalid_data_code, "status": invalid_data["status"]}
}, ensure_ascii=False, sort_keys=True))
