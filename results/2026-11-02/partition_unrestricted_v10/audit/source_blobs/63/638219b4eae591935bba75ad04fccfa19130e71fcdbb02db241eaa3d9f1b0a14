"""Read-only integrity check for the C010 bundle and frozen readiness files."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parents[2]
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


def load_json(path: Path):
    with path.open("r", encoding="utf-8-sig") as stream:
        return json.load(stream)


def inside(path: Path, base: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(base.resolve(strict=True))
        return True
    except (OSError, ValueError):
        return False


def check_file(path: Path, digest: object, byte_count: object | None,
               label: str, errors: list[str]) -> bool:
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        errors.append(f"{label}: invalid sha256")
        return False
    if not path.is_file():
        errors.append(f"{label}: missing file {path}")
        return False
    raw_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if raw_hash.lower() != digest.lower():
        errors.append(f"{label}: sha256 mismatch {path}")
        return False
    if byte_count is not None:
        if isinstance(byte_count, bool) or not isinstance(byte_count, int):
            errors.append(f"{label}: invalid byte count")
            return False
        if path.stat().st_size != byte_count:
            errors.append(f"{label}: byte count mismatch {path}")
            return False
    return True


def check_manifest(path: Path, *, base: Path,
                   require_bytes: bool, errors: list[str]) -> int:
    try:
        manifest = load_json(path)
    except Exception as exc:
        errors.append(f"{path.name}: missing or unreadable: {exc!r}")
        return 0
    entries = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(entries, list):
        errors.append(f"{path.name}: files must be a list")
        return 0
    checked = 0
    for index, item in enumerate(entries):
        label = f"{path.name}[{index}]"
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append(f"{label}: malformed file entry")
            continue
        rel = Path(item["path"])
        if rel.is_absolute():
            errors.append(f"{label}: expected relative path")
            continue
        target = (base / rel).resolve(strict=False)
        if not inside(target, base):
            errors.append(f"{label}: path escapes its root")
            continue
        if require_bytes and "bytes" not in item:
            errors.append(f"{label}: missing byte count")
            continue
        check_file(target, item.get("sha256"), item.get("bytes"), label, errors)
        checked += 1
    return checked


def main() -> int:
    errors: list[str] = []
    parent_manifest = ROOT / "coordination" / "parent_manifest.json"
    parent_count = check_manifest(parent_manifest, base=WORKSPACE,
                                  require_bytes=False,
                                  errors=errors)

    bundle_manifest = ROOT / "coordination" / "bundle_manifest.json"
    bundle_present = bundle_manifest.is_file()
    bundle_count = 0
    if bundle_present:
        bundle_count = check_manifest(bundle_manifest, base=ROOT,
                                      require_bytes=True,
                                      errors=errors)

    readiness_path = ROOT / "implementation" / "READINESS_V3.json"
    readiness_count = 0
    try:
        readiness = load_json(readiness_path)
        files = readiness.get("files") if isinstance(readiness, dict) else None
        if not isinstance(files, dict):
            errors.append("READINESS_V3.json: files must be an object")
        else:
            for name, entry in files.items():
                label = f"READINESS_V3.json[{name}]"
                if not isinstance(name, str) or not isinstance(entry, dict):
                    errors.append(f"{label}: malformed readiness entry")
                    continue
                target = (ROOT / "implementation" / name).resolve(strict=False)
                if not inside(target, ROOT):
                    errors.append(f"{label}: path escapes C010 root")
                    continue
                check_file(target, entry.get("sha256"), entry.get("bytes"),
                           label, errors)
                readiness_count += 1
    except Exception as exc:
        errors.append(f"READINESS_V3.json: missing or unreadable: {exc!r}")

    report = {
        "status": "pass" if not errors else "fail",
        "error_count": len(errors),
        "errors": errors,
        "counts": {
            "parent_manifest_files_checked": parent_count,
            "bundle_manifest_present": bundle_present,
            "bundle_manifest_files_checked": bundle_count,
            "readiness_files_checked": readiness_count,
        },
        "scope": "Read-only path, SHA-256, and byte-count verification; no runtime or scientific validation.",
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
