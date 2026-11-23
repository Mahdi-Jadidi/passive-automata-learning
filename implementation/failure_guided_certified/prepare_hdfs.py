"""Convert LogHub HDFS_v1 BlockId-labeled event sequences to two fixed samples."""
import argparse
import csv
from hashlib import sha256
from heapq import nsmallest
from io import TextIOWrapper
import json
from pathlib import Path
from zipfile import ZipFile

SOURCE = "https://zenodo.org/records/8196385/files/HDFS_v1.zip?download=1"


def prepare(archive, output):
    with ZipFile(archive) as source:
        def rows(name):
            member, = [m for m in source.namelist() if m.rsplit("/", 1)[-1] == name]
            with source.open(member) as stream:
                yield from csv.DictReader(TextIOWrapper(stream, encoding="utf-8-sig"))
        labels = {row["BlockId"]: row["Label"] for row in rows("anomaly_label.csv")}
        alphabet = set()

        def labeled_rows():
            seen = set()
            for row in rows("Event_traces.csv"):
                key = row["BlockId"]
                label = labels[key]
                if key in seen or label not in {"Normal", "Anomaly"}:
                    raise ValueError("unexpected HDFS label or duplicate BlockId")
                seen.add(key)
                field = row["Features"].strip()
                sequence = [a.strip() for a in field[1:-1].split(",")] if field[1:-1] else []
                if not (field.startswith("[") and field.endswith("]")) or any(
                    not (a.startswith("E") and a[1:].isdigit()) for a in sequence):
                    raise ValueError("expected event IDs in order")
                alphabet.update(sequence)
                yield label, (sha256(key.encode()).hexdigest(), key, sequence)

        # Each heap sees the full ordered dataset. Both selections are fixed before solving.
        normal_rows = nsmallest(64, (row for label, row in labeled_rows() if label == "Normal"))
        anomaly_rows = nsmallest(64, (row for label, row in labeled_rows() if label == "Anomaly"))
    if min(len(normal_rows), len(anomaly_rows)) != 64:
        raise ValueError("insufficient rows for fixed HDFS samples")
    cases = {}
    provenance = {}
    for n in (16, 64):
        positives = normal_rows[:n]
        negatives = anomaly_rows[:n]
        key = f"hdfs_{n}"
        cases[key] = dict(alphabet=sorted(alphabet), positive=[w for _, _, w in positives],
                          negative=[w for _, _, w in negatives])
        provenance[key] = dict(normal_sha256=[digest for digest, _, _ in positives],
                               anomaly_sha256=[digest for digest, _, _ in negatives],
                               cross_label_equal_words=len({tuple(w) for _, _, w in positives} &
                                                           {tuple(w) for _, _, w in negatives}))
    with archive.open("rb") as raw:
        archive_sha256 = sha256()
        for block in iter(lambda: raw.read(1024 * 1024), b""):
            archive_sha256.update(block)
    output.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    output.with_name("hdfs_provenance.json").write_text(json.dumps(
        dict(source=SOURCE, archive_sha256=archive_sha256.hexdigest(), cases=provenance),
        indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--output", type=Path, default=Path("hdfs_cases.json"))
    args = parser.parse_args()
    prepare(args.archive, args.output)
