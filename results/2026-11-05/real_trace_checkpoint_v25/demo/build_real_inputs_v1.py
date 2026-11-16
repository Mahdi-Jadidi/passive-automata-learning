"""Reconstruct the seven fixed training inputs without running inference."""
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKPOINT = HERE.parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    records = []
    for arm in read(CHECKPOINT / "audit/ACTUAL_FREEZE_V3.json")["arms"]:
        source = Path(arm["path"])
        assert hashlib.sha256(source.read_bytes()).hexdigest() == arm["sha256"]
        data = read(source)
        train = data["traces"][:4] if arm["id"] != "BGL" else [
            {"file_id": 0, "events": data["traces"][0]["events"][:1400]}]
        frequency = Counter(e["id"] for t in train for e in t["events"])
        selected = sorted(frequency, key=lambda a: (-frequency[a], a))[:8]
        actual = read(CHECKPOINT / "audit" / ("ACTUAL_" + arm["id"] + "_V1.json"))
        assert selected == actual["selected"]
        payload = {"alphabet": sorted(selected), "traces": [
            {"file_id": t["file_id"], "events": [e for e in t["events"] if e["id"] in selected]}
            for t in train]}
        raw = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
        output = HERE / (arm["id"] + "_train.json")
        if output.exists():
            assert output.read_bytes() == raw, "existing input differs; use a new version"
        else:
            output.write_bytes(raw)
        records.append(dict(arm=arm["id"], path=output.name,
                            sha256=hashlib.sha256(raw).hexdigest(), source_sha256=arm["sha256"],
                            events=sum(len(t["events"]) for t in payload["traces"]),
                            types=len(payload["alphabet"])))
    (HERE / "REAL_INPUT_MANIFEST_V1.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(json.dumps(dict(training_inputs=len(records), selection_matches_frozen_results=True)))


if __name__ == "__main__":
    main()
