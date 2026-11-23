
"""Build fixed development and disjoint evaluation samples from LogHub HDFS_v1."""
import argparse
import csv
from hashlib import sha256
from heapq import nsmallest
from io import TextIOWrapper
import json
from pathlib import Path
from zipfile import ZipFile


def prepare(archive, out):
    with ZipFile(archive) as z:
        def records(name):
            member, = [entry for entry in z.namelist() if entry.rsplit("/", 1)[-1] == name]
            with z.open(member) as stream:
                yield from csv.DictReader(TextIOWrapper(stream, encoding="utf-8-sig"))

        labels = {row["BlockId"]: row["Label"] for row in records("anomaly_label.csv")}
        alphabet = set()
        by_label = {"Normal": [], "Anomaly": []}
        seen = set()
        for row in records("Event_traces.csv"):
            block = row["BlockId"]
            if block in seen:
                raise ValueError("duplicate BlockId")
            seen.add(block)
            text = row["Features"].strip()
            word = [symbol.strip() for symbol in text[1:-1].split(",")] if text[1:-1] else []
            if not text.startswith("[") or not text.endswith("]") or any(
                not symbol.startswith("E") or not symbol[1:].isdigit() for symbol in word
            ):
                raise ValueError("invalid input event")
            alphabet.update(word)
            by_label[labels[block]].append((sha256(block.encode()).hexdigest(), word))

    groups = {label: nsmallest(2048, rows) for label, rows in by_label.items()}
    if any(len(rows) != 2048 for rows in groups.values()):
        raise ValueError("insufficient traces")
    inputs, provenance = {}, {}
    for start, sizes in ((0, (16, 64, 128, 512, 1024)), (1024, (128, 512, 1024))):
        for size in sizes:
            name = f"hdfs_{'holdout_' if start else ''}{size}"
            p, n = (groups[label][start:start+size] for label in ("Normal", "Anomaly"))
            inputs[name] = dict(alphabet=sorted(alphabet), positive=[w for _, w in p], negative=[w for _, w in n])
            provenance[name] = {"normal": [h for h, _ in p], "anomaly": [h for h, _ in n],
                                "offset": start, "per_label": size}
    with archive.open("rb") as handle:
        digest = sha256()
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    out.mkdir(exist_ok=True)
    (out / "hdfs_cases.json").write_text(json.dumps(inputs, separators=(",", ":")), encoding="utf-8")
    (out / "hdfs_provenance.json").write_text(json.dumps({
        "source": "https://zenodo.org/records/8196385/files/HDFS_v1.zip?download=1",
        "archive_sha256": digest.hexdigest(), "cases": provenance,
    }, indent=2), encoding="utf-8")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive", type=Path)
    p.add_argument("--out", type=Path, default=Path("evidence"))
    a = p.parse_args()
    prepare(a.archive, a.out)
