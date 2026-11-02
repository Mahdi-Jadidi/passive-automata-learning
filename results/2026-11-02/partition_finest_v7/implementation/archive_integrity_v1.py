#!/usr/bin/env python3
"""Read-only C007 archive integrity audit; writes a unique checker snapshot/report.

Run only after coordination/runtime_final.json exists, for example:
  python -B -X utf8 archive_integrity_v1.py FINAL_INTEGRITY_2026-11-02.json

The checker does not execute providers, verifiers, corpus drivers, or benchmarks.
It checks the immutable C006 parent manifest, C007 final runtime manifest,
readiness/final-target hash references, content-addressed evidence source blobs,
every attempt's source references and raw stdout/stderr bytes, and completion
records. Output is refused if it already exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def reference_path(raw: str, *, origin: Path, cycle: Path, workspace: Path,
                   owner_scope: Path | None = None) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path.resolve()
    # File references are first interpreted relative to the JSON document that
    # declares them (not the checker). This covers readiness files such as
    # theory/READINESS.json -> PROOFS_v1.md and implementation readiness files
    # -> solver_vN.py. Keep every interpretation inside the workspace.
    origin_candidate = (origin / path).resolve()
    if within(origin_candidate, workspace) and origin_candidate.exists():
        return origin_candidate
    # Historical readiness snapshots may retain a short file reference while
    # explicitly naming their owning C006 folder (for example scope=implementation/).
    # Use only that declared location; never search by basename or hash.
    if owner_scope is not None:
        scoped_candidate = (owner_scope / path).resolve()
        if within(scoped_candidate, cycle) and scoped_candidate.exists():
            return scoped_candidate
    cycle_candidate = (cycle / path).resolve()
    if within(cycle_candidate, workspace) and cycle_candidate.exists():
        return cycle_candidate
    workspace_candidate = (workspace / path).resolve()
    if within(workspace_candidate, workspace) and workspace_candidate.exists():
        return workspace_candidate
    # Return a deterministic in-scope candidate so check() can report the
    # missing file at the closest declaring location.
    if within(origin_candidate, workspace):
        return origin_candidate
    if within(cycle_candidate, workspace):
        return cycle_candidate
    return workspace_candidate


def scan_hash_references(value, prefix="$"):
    """Collect nested {path|file, sha256, optional bytes} records."""
    found = []
    if isinstance(value, dict):
        raw_path = value.get("path", value.get("file"))
        digest = value.get("sha256", value.get("hash"))
        if isinstance(raw_path, str) and isinstance(digest, str) and len(digest) == 64:
            found.append((raw_path, digest, value.get("bytes"), prefix))
        # Readiness records use paired keys such as api_file/api_sha256 and
        # legacy artifact/provider + sha256. Accept those without special cases
        # tied to a specific worker's JSON schema.
        for path_key, raw in value.items():
            if not isinstance(raw, str) or not (path_key.endswith("_file") or path_key.endswith("_path")):
                continue
            stem = path_key.rsplit("_", 1)[0]
            paired_hash = value.get(stem + "_sha256")
            if isinstance(paired_hash, str) and len(paired_hash) == 64:
                found.append((raw, paired_hash, value.get(stem + "_bytes"), prefix + "." + path_key))
        for legacy_key in ("artifact", "provider"):
            raw = value.get(legacy_key)
            if isinstance(raw, str) and isinstance(digest, str) and len(digest) == 64:
                found.append((raw, digest, value.get("bytes"), prefix + "." + legacy_key))
        # Some manifests use {"files": {"relative/path": "<sha256>"}}.
        files = value.get("files")
        if isinstance(files, dict):
            for raw, item in files.items():
                if isinstance(raw, str) and isinstance(item, str) and len(item) == 64:
                    found.append((raw, item, None, prefix + ".files." + raw))
                elif isinstance(raw, str) and isinstance(item, dict):
                    item_hash = item.get("sha256", item.get("hash"))
                    item_path = item.get("path", item.get("file", raw))
                    if isinstance(item_path, str) and isinstance(item_hash, str) and len(item_hash) == 64:
                        found.append((item_path, item_hash, item.get("bytes"), prefix + ".files." + raw))
        for key, child in value.items():
            if isinstance(child, (dict, list)):
                found.extend(scan_hash_references(child, prefix + "." + str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            if isinstance(child, (dict, list)):
                found.extend(scan_hash_references(child, prefix + f"[{index}]"))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", help="new report filename relative to implementation/ or absolute")
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    cycle = here.parent
    workspace = cycle.parents[2]
    output = Path(args.output)
    output = output.resolve() if output.is_absolute() else (here / output).resolve()
    if output.exists():
        parser.error(f"refusing to overwrite existing report: {output}")

    errors = []
    counts = {
        "parent_manifest_files": 0,
        "runtime_final_files": 0,
        "readiness_files": 0,
        "readiness_references": 0,
        "attempts": 0,
        "completion_records": 0,
        "raw_streams": 0,
        "source_references": 0,
        "source_blobs": 0,
        "referenced_source_blobs": 0,
    }

    def check(path: Path, expected_hash: str, label: str, expected_bytes=None):
        if not path.is_file():
            errors.append(f"{label}: missing file: {path}")
            return False
        actual_hash = sha256(path)
        valid = True
        if actual_hash.lower() != str(expected_hash).lower():
            errors.append(f"{label}: SHA-256 mismatch: {path}")
            valid = False
        if expected_bytes is not None:
            try:
                expected_size = int(expected_bytes)
            except (TypeError, ValueError):
                errors.append(f"{label}: invalid byte count {expected_bytes!r}: {path}")
                valid = False
            else:
                if path.stat().st_size != expected_size:
                    errors.append(f"{label}: byte count mismatch: {path}")
                    valid = False
        return valid

    def check_manifest_refs(manifest_path: Path, label: str, base: Path):
        try:
            data = load_json(manifest_path)
        except Exception as exc:
            errors.append(f"{label}: invalid JSON {manifest_path}: {exc}")
            return
        refs = scan_hash_references(data)
        if not refs:
            errors.append(f"{label}: no path/hash file entries in {manifest_path}")
        for raw, digest, byte_count, location in refs:
            counts["runtime_final_files"] += label == "runtime final"
            candidate = reference_path(raw, origin=base, cycle=cycle, workspace=workspace)
            if not (within(candidate, cycle) or within(candidate, workspace)):
                errors.append(f"{label}: path escapes workspace at {location}: {candidate}")
                continue
            check(candidate, digest, f"{label} {location}", byte_count)

    # Immutable baseline files from C006. Paths are relative to the workspace.
    parent_manifest = cycle / "coordination" / "parent_manifest.json"
    if not parent_manifest.is_file():
        errors.append(f"missing C006 parent manifest: {parent_manifest}")
    else:
        try:
            entries = load_json(parent_manifest).get("files", [])
            if not isinstance(entries, list) or not entries:
                errors.append("C006 parent manifest has no file list")
            for entry in entries:
                counts["parent_manifest_files"] += 1
                if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
                    errors.append("malformed C006 parent manifest entry")
                    continue
                target = (workspace / entry["path"]).resolve()
                if not within(target, workspace):
                    errors.append(f"C006 parent path escapes workspace: {target}")
                    continue
                check(target, entry.get("sha256", ""), "C006 parent manifest", entry.get("bytes"))
        except Exception as exc:
            errors.append(f"invalid C006 parent manifest {parent_manifest}: {exc}")

    # Runtime final is generated by the master after promoting the exact public files.
    runtime_final = cycle / "coordination" / "runtime_final.json"
    if not runtime_final.is_file():
        errors.append(f"missing final runtime manifest: {runtime_final}")
    else:
        check_manifest_refs(runtime_final, "runtime final", runtime_final.parent)

    # Readiness and final target documents may reference runtime/dependency hashes.
    for readiness in sorted(list(cycle.rglob("READINESS*.json"))
                            + list(cycle.rglob("FINAL_TARGET*.json"))):
        counts["readiness_files"] += 1
        try:
            readiness_data = load_json(readiness)
            refs = scan_hash_references(readiness_data)
        except Exception as exc:
            errors.append(f"invalid readiness/final-target JSON {readiness}: {exc}")
            continue
        owner_scope = None
        scope_value = readiness_data.get("scope") if isinstance(readiness_data, dict) else None
        if isinstance(scope_value, str):
            declared_scope = (cycle / scope_value).resolve()
            if not within(declared_scope, cycle):
                errors.append(f"readiness scope escapes C007 cycle: {readiness}:{scope_value}")
            elif declared_scope.is_dir():
                owner_scope = declared_scope
            else:
                pass  # scope may describe a mission, rather than name an owner folder
        for raw, digest, byte_count, location in refs:
            counts["readiness_references"] += 1
            target = reference_path(raw, origin=readiness.parent, cycle=cycle,
                                    workspace=workspace, owner_scope=owner_scope)
            if not (within(target, cycle) or within(target, workspace)):
                errors.append(f"readiness path escapes workspace at {location}: {target}")
                continue
            check(target, digest, f"readiness reference {readiness.name}:{location}", byte_count)

    evidence = cycle / "evidence"
    blob_root = evidence / "source_blobs"
    blob_hashes = set()
    for blob in sorted(blob_root.rglob("*") if blob_root.exists() else []):
        if not blob.is_file():
            continue
        counts["source_blobs"] += 1
        digest = sha256(blob)
        if len(blob.name) != 64 or digest != blob.name:
            errors.append(f"content-addressed source blob mismatch: {blob}")
        elif blob.parent.name != blob.name[:2]:
            errors.append(f"source blob shard mismatch: {blob}")
        blob_hashes.add(blob.name)

    attempts_root = evidence / "attempts"
    attempt_dirs = sorted(p for p in attempts_root.iterdir() if p.is_dir()) if attempts_root.exists() else []
    for attempt in attempt_dirs:
        counts["attempts"] += 1
        manifest_path, result_path = attempt / "manifest.json", attempt / "result.json"
        if not manifest_path.is_file():
            errors.append(f"missing attempt manifest: {manifest_path}")
            continue
        try:
            manifest = load_json(manifest_path)
        except Exception as exc:
            errors.append(f"invalid attempt manifest {manifest_path}: {exc}")
            continue
        if manifest.get("attempt_id") != attempt.name:
            errors.append(f"attempt id does not match directory: {attempt}")
        sources = manifest.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"attempt has no snapshotted sources: {manifest_path}")
            sources = []
        for source in sources:
            counts["source_references"] += 1
            if not isinstance(source, dict):
                errors.append(f"malformed source reference in {manifest_path}")
                continue
            rel, digest, byte_count = source.get("snapshot"), source.get("sha256"), source.get("bytes")
            if not isinstance(rel, str) or not isinstance(digest, str):
                errors.append(f"incomplete source reference in {manifest_path}")
                continue
            target = (evidence / rel).resolve()
            if not within(target, cycle):
                errors.append(f"source reference escapes C007 cycle: {target}")
                continue
            if check(target, digest, "attempt source snapshot", byte_count):
                counts["referenced_source_blobs"] += 1
                if target.name not in blob_hashes:
                    errors.append(f"source reference does not resolve to indexed source blob: {target}")

        if not result_path.is_file():
            errors.append(f"missing completion record for attempt: {result_path}")
            continue
        counts["completion_records"] += 1
        try:
            result = load_json(result_path)
        except Exception as exc:
            errors.append(f"invalid completion record {result_path}: {exc}")
            continue
        if result.get("attempt_id") != attempt.name:
            errors.append(f"completion attempt id does not match directory: {result_path}")
        if "execution_status" not in result or "scientific_status" not in result or "exit_code" not in result:
            errors.append(f"completion record lacks status/exit fields: {result_path}")
        for stream in ("stdout", "stderr"):
            raw = attempt / (stream + ".bin")
            counts["raw_streams"] += 1
            check(raw, result.get(stream + "_sha256", ""), f"raw {stream}", result.get(stream + "_bytes"))

    # Record and snapshot this exact checker before writing the report.
    source = Path(__file__).resolve()
    self_hash = sha256(source)
    snapshot_dir = here / ".checker_snapshots"
    snapshot_dir.mkdir(exist_ok=True)
    snapshot = snapshot_dir / f"{output.stem}_{uuid.uuid4().hex}_{self_hash}.py"
    shutil.copyfile(source, snapshot)
    if sha256(snapshot) != self_hash:
        errors.append(f"checker snapshot verification failed: {snapshot}")
    report = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "checker": {"path": str(source.relative_to(cycle)), "sha256": self_hash,
                    "snapshot": str(snapshot.relative_to(cycle))},
        "cycle": str(cycle),
        "counts": counts,
        "error_count": len(errors),
        "errors": errors,
        "status": "pass" if not errors else "fail",
        "scope_note": "Archive integrity only; no solver, verifier, corpus, or performance code was executed.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"status":report["status"], "counts":counts,
                      "error_count":len(errors), "report":str(output)}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

