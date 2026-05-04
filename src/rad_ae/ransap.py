"""Readers for RanSAP-style public storage access traces.

The reader intentionally keeps the canonical event schema small: timestamp,
operation, LBA, transfer size, and optional write entropy. RanSAP and RanSMAP
both expose this storage subset even though RanSMAP has additional memory CSVs.
"""

from __future__ import annotations

import csv
import io
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


@dataclass(frozen=True)
class IoEvent:
    timestamp: float
    op: str
    lba: int
    size: int
    entropy: float | None = None


@dataclass(frozen=True)
class TraceSource:
    """A single run with ata_read.csv and/or ata_write.csv."""

    run_id: str
    label: str
    container: Path
    kind: str
    read_path: Path | None = None
    write_path: Path | None = None
    zip_path: Path | None = None
    read_member: str | None = None
    write_member: str | None = None


DEFAULT_LABEL_RULES: tuple[dict[str, object], ...] = (
    {
        "label": "attack",
        "patterns": (
            r"(?i)ransom",
            r"(?i)wannacry",
            r"(?i)cerber",
            r"(?i)locky",
            r"(?i)gandcrab",
            r"(?i)revil",
            r"(?i)sodinokibi",
            r"(?i)conti",
            r"(?i)teslacrypt",
            r"(?i)crypt",
        ),
    },
    {
        "label": "benign",
        "patterns": (
            r"(?i)benign",
            r"(?i)normal",
            r"(?i)chrome",
            r"(?i)firefox",
            r"(?i)edge",
            r"(?i)office",
            r"(?i)word",
            r"(?i)excel",
            r"(?i)powerpoint",
            r"(?i)explorer",
            r"(?i)copy",
            r"(?i)7zip",
            r"(?i)vlc",
        ),
    },
)


def infer_label(run_id: str, label_rules: Sequence[dict[str, object]] | None = None) -> str:
    """Infer a coarse benign/attack label from configured path patterns."""

    rules = label_rules or DEFAULT_LABEL_RULES
    for rule in rules:
        label = str(rule["label"])
        patterns = rule.get("patterns", ())
        if isinstance(patterns, str):
            patterns = (patterns,)
        for pattern in patterns:
            if re.search(str(pattern), run_id):
                return label
    return "unknown"


def discover_trace_sources(
    dataset_root: Path | str,
    label_rules: Sequence[dict[str, object]] | None = None,
    include_unknown: bool = False,
) -> list[TraceSource]:
    """Discover RanSAP-style run sources in directories or zip archives.

    The function supports both unzipped trees containing ata_read.csv and
    ata_write.csv, and zip files that contain those CSV names somewhere inside.
    It does not extract public raw data into the repository.
    """

    root = Path(dataset_root)
    sources: dict[str, TraceSource] = {}

    parents: set[Path] = set()
    for csv_path in root.rglob("ata_read.csv"):
        parents.add(csv_path.parent)
    for csv_path in root.rglob("ata_write.csv"):
        parents.add(csv_path.parent)

    for parent in sorted(parents):
        read_path = parent / "ata_read.csv"
        write_path = parent / "ata_write.csv"
        run_id = parent.relative_to(root).as_posix() if parent != root else parent.name
        label = infer_label(run_id, label_rules)
        if label == "unknown" and not include_unknown:
            continue
        sources[f"dir:{run_id}"] = TraceSource(
            run_id=run_id,
            label=label,
            container=parent,
            kind="directory",
            read_path=read_path if read_path.exists() else None,
            write_path=write_path if write_path.exists() else None,
        )

    for zip_path in sorted(root.rglob("*.zip")):
        try:
            with zipfile.ZipFile(zip_path) as zf:
                members = zf.namelist()
        except zipfile.BadZipFile:
            continue
        grouped: dict[str, dict[str, str]] = {}
        for member in members:
            name = Path(member).name
            if name not in {"ata_read.csv", "ata_write.csv"}:
                continue
            parent = str(Path(member).parent)
            grouped.setdefault(parent, {})[name] = member
        for parent, files in grouped.items():
            rel_zip = zip_path.relative_to(root).as_posix()
            run_id = f"{rel_zip}:{parent}"
            label = infer_label(run_id, label_rules)
            if label == "unknown" and not include_unknown:
                continue
            sources[f"zip:{run_id}"] = TraceSource(
                run_id=run_id,
                label=label,
                container=zip_path,
                kind="zip",
                zip_path=zip_path,
                read_member=files.get("ata_read.csv"),
                write_member=files.get("ata_write.csv"),
            )

    return sorted(sources.values(), key=lambda source: source.run_id)


def read_trace_events(source: TraceSource) -> list[IoEvent]:
    """Read and timestamp-sort one trace source."""

    events: list[IoEvent] = []
    events.extend(_read_operation(source, "read"))
    events.extend(_read_operation(source, "write"))
    events.sort(key=lambda event: event.timestamp)
    return events


def _read_operation(source: TraceSource, op: str) -> Iterator[IoEvent]:
    if source.kind == "directory":
        path = source.read_path if op == "read" else source.write_path
        if path is None:
            return iter(())

        def from_file() -> Iterator[IoEvent]:
            with path.open("r", encoding="utf-8", newline="") as handle:
                yield from _read_csv_rows(handle, op)

        return from_file()

    member = source.read_member if op == "read" else source.write_member
    if source.zip_path is None or member is None:
        return iter(())

    def from_zip() -> Iterator[IoEvent]:
        with zipfile.ZipFile(source.zip_path) as zf:
            with zf.open(member, "r") as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8", newline="")
                yield from _read_csv_rows(text, op)

    return from_zip()


def _read_csv_rows(handle: Iterable[str], op: str) -> Iterator[IoEvent]:
    reader = csv.reader(handle)
    for row in reader:
        if len(row) < 4:
            continue
        try:
            sec = float(row[0].strip())
            nsec = float(row[1].strip())
            lba = int(float(row[2].strip()))
            size = int(float(row[3].strip()))
        except ValueError:
            continue
        entropy = None
        if op == "write" and len(row) >= 5:
            try:
                parsed = float(row[4].strip())
                entropy = parsed if parsed >= 0.0 else None
            except ValueError:
                entropy = None
        yield IoEvent(timestamp=sec + nsec / 1_000_000_000.0, op=op, lba=lba, size=size, entropy=entropy)
