#!/usr/bin/env python3
"""Independently validate the C007 v4 public root-wrapper CLI smoke."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTEMPT_ID = "20261102T065015.502299Z_d228a8b4c4"
EXPECTED = {
    "wrapper": "d4d1644fa3144c68c626fc8daff818e9500a89453a21871df45ffb3e7b7232de",
    "cli": "46642a86c315b95de7b784eb614af4000b52fa96ce55c965f1bbb3de1d15e879",
    "provider": "c6c803da1088450d352d56bc1a208d6fa7c0d19416bd702255d866052e454fff",
    "protocol": "74ee1895c49e40abc5cc1c328bc1fad006e06dde397963dc1779c7266a2a06bd",
    "readiness": "cff6e5e5156d1c8abe8069cde7182195742762a387817ea465ccdb66adbe5ef9",
    "input": "ca187bb056c25c027c6278d296bcb320e6505b42e0832383305adcfb917484f6",
    "capture": "68ee700f391fb6a1cf135e4b55a11a247b45f25164553c917d1664f6fc4a31cf",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return digest(path.read_bytes())


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def normalize(partition):
    return tuple(sorted((tuple(sorted(block)) for block in partition), key=lambda block: block[0]))


def project(word, block):
    members = set(block)
    return "".join(char for char in word if char in members)


def direct_witness(data, partition):
    blocks = [set(block) for block in partition]
    positive = sorted(set(data["positive"]))
    negative = sorted(set(data["negative"]))
    languages = [{project(word, block) for word in positive} for block in blocks]
    for word in negative:
        projections = [project(word, block) for block in blocks]
        if all(projections[index] in languages[index] for index in range(len(blocks))):
            return None
    return {
        "partition": [sorted(block) for block in blocks],
        "positive_projection_languages": [sorted(language) for language in languages],
        "positive_witnesses": [
            {"word": word, "projections": [project(word, block) for block in blocks]}
            for word in positive
        ],
        "negative_witnesses": [
            {"word": word,
             "projections": [project(word, block) for block in blocks],
             "rejected_by_blocks": [index for index, block in enumerate(blocks)
                                    if project(word, block) not in languages[index]]}
            for word in negative
        ],
    }


def valid_swap_edge(edge, data):
    if not isinstance(edge, dict):
        return False
    pair = edge.get("symbols")
    witness = edge.get("witness")
    if not isinstance(pair, list) or len(pair) != 2 or pair[0] == pair[1]:
        return False
    if not isinstance(witness, dict) or witness.get("rule") != "adjacent_swap":
        return False
    positive, negative = set(data["positive"]), set(data["negative"])
    word, pos = witness.get("positive"), witness.get("position")
    if word not in positive or witness.get("negative") not in negative:
        return False
    if isinstance(pos, bool) or not isinstance(pos, int) or not 0 <= pos < len(word) - 1:
        return False
    if word[pos:pos + 2] not in (pair[0] + pair[1], pair[1] + pair[0]):
        return False
    swapped = word[:pos] + word[pos + 1] + word[pos] + word[pos + 2:]
    return swapped == witness["negative"]


def components(alphabet, edges):
    parent = {symbol: symbol for symbol in alphabet}

    def find(item):
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    for edge in edges:
        a, b = edge["symbols"]
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    groups = {}
    for symbol in alphabet:
        groups.setdefault(find(symbol), []).append(symbol)
    return sorted((sorted(group) for group in groups.values()), key=lambda block: block[0])


def main() -> int:
    attempt = ROOT / "evidence" / "attempts" / ATTEMPT_ID
    manifest = json.loads((attempt / "manifest.json").read_text(encoding="utf-8"))
    captured = json.loads((attempt / "result.json").read_text(encoding="utf-8"))
    stdout_path, stderr_path = attempt / "stdout.bin", attempt / "stderr.bin"
    wrapper = ROOT / "solver.py"
    cli = ROOT / "implementation" / "finest_cli_v2.py"
    provider = ROOT / "implementation" / "finest_solver_v4.py"
    protocol = ROOT / "implementation" / "PROTOCOL_V5.md"
    readiness = ROOT / "implementation" / "READINESS_V4.json"
    input_path = ROOT / "implementation" / "example_swap_fastpath_v1.json"
    capture_script = ROOT / "evidence" / "capture.py"
    required = {wrapper: EXPECTED["wrapper"], cli: EXPECTED["cli"], provider: EXPECTED["provider"],
                protocol: EXPECTED["protocol"], readiness: EXPECTED["readiness"],
                input_path: EXPECTED["input"], capture_script: EXPECTED["capture"]}
    source_by_path = {source["path"]: source for source in manifest.get("sources", [])}
    failures = []
    for path, expected_hash in required.items():
        source = source_by_path.get(str(path.resolve()))
        if source is None or source.get("sha256") != expected_hash:
            failures.append("required_source_missing_or_drifted:" + path.name)
    for source in manifest.get("sources", []):
        blob = ROOT / "evidence" / source.get("snapshot", "")
        if not blob.is_file() or file_digest(blob) != source.get("sha256"):
            failures.append("source_snapshot_invalid:" + Path(source.get("path", "unknown")).name)

    if captured.get("execution_status") != "success" or captured.get("exit_code") != 0 or captured.get("child_reaped") is not True:
        failures.append("root_cli_capture_not_clean_success")
    if captured.get("stdout_sha256") != file_digest(stdout_path):
        failures.append("stdout_hash_mismatch")
    if captured.get("stderr_bytes") != 0 or stderr_path.stat().st_size != 0:
        failures.append("stderr_not_empty")
    argv = manifest.get("command_argv", [])
    if (len(argv) < 6 or Path(argv[4]).resolve() != wrapper.resolve()
            or Path(argv[5]).resolve() != input_path.resolve()
            or "--mode" not in argv or "adaptive" not in argv):
        failures.append("root_wrapper_or_input_not_invoked")

    data = json.loads(input_path.read_text(encoding="utf-8"))
    output = json.loads(stdout_path.read_text(encoding="utf-8").strip())
    expected_partition = [["a", "b"], ["c", "d"]]
    if (data != {"alphabet": ["a", "b", "c", "d"], "positive": ["ab", "cd"],
                "negative": ["ba", "dc"]}):
        failures.append("root_cli_input_changed")
    if output.get("status") != "finest_unique" or output.get("complete") is not True or output.get("decision_complete") is not True:
        failures.append("root_cli_result_not_complete_unique_finest")
    certificate = output.get("finality_certificate", {})
    edges = certificate.get("must_link_edges", [])
    if certificate.get("kind") != "must_link_components_compatible" or len(edges) != 2:
        failures.append("root_cli_missing_fastpath_certificate")
    if any(not valid_swap_edge(edge, data) for edge in edges):
        failures.append("root_cli_invalid_forced_swap_edge")
    if normalize(components(data["alphabet"], edges)) != normalize(expected_partition):
        failures.append("root_cli_forced_components_mismatch")
    if normalize(certificate.get("components", [])) != normalize(expected_partition):
        failures.append("root_cli_certificate_components_mismatch")
    witness = direct_witness(data, expected_partition)
    if witness is None or output.get("finest_witness") != witness:
        failures.append("root_cli_direct_projection_witness_mismatch")
    if output.get("method") != "c007-unknown-k-finest-v4-staged-swap":
        failures.append("wrong_provider_method")

    report = {
        "schema_version": 2,
        "status": "accepted" if not failures else "rejected",
        "capture_attempt_id": ATTEMPT_ID,
        "root_wrapper_sha256": file_digest(wrapper),
        "cli_sha256": file_digest(cli),
        "provider_sha256": file_digest(provider),
        "input_sha256": file_digest(input_path),
        "stdout_sha256": file_digest(stdout_path),
        "stdout_bytes": stdout_path.stat().st_size,
        "execution_status": captured.get("execution_status"),
        "child_reaped": captured.get("child_reaped"),
        "provider_status": output.get("status"),
        "blocks": len(expected_partition),
        "forced_edges_replayed": len(edges),
        "failures": failures,
    }
    report_path = ROOT / "audit" / "root_cli_v2.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
