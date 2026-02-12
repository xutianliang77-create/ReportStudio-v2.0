"""P1-101~P1-107: 简化数据接入与质量检测。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import json

from .infrastructure import ReportStudioError


@dataclass
class Dataset:
    rows: list[dict]
    schema: dict
    quality: dict


def _read_csv(path: Path) -> list[dict]:
    # Use utf-8-sig to automatically strip UTF-8 BOM (common in Excel-exported CSVs).
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames:
            reader.fieldnames = [name.lstrip("\ufeff") if isinstance(name, str) else name for name in reader.fieldnames]
        return [
            {(
                k.lstrip("\ufeff") if isinstance(k, str) else k
            ): v for k, v in row.items()}
            for row in reader
        ]


def _read_json(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    raise ReportStudioError("IE_JSON_SHAPE", "JSON must be a list of objects")


def load_rows(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _read_csv(path)
    if suffix == ".json":
        return _read_json(path)
    raise ReportStudioError("IE_FORMAT_UNSUPPORTED", f"Unsupported file format: {suffix}")


def infer_schema(rows: list[dict]) -> dict:
    if not rows:
        raise ReportStudioError("IE_EMPTY", "Dataset is empty")
    sample = rows[0]
    fields = []
    for key, value in sample.items():
        ftype = "text"
        try:
            float(value)
            ftype = "numeric"
        except (TypeError, ValueError):
            pass
        fields.append({"name": key, "type": ftype})
    return {"fields": fields}


def quality_report(rows: list[dict], schema: dict) -> dict:
    total_rows = len(rows)
    missing = {}
    for field in schema["fields"]:
        name = field["name"]
        miss = sum(1 for r in rows if r.get(name) in (None, ""))
        if miss:
            missing[name] = miss
    return {
        "total_rows": total_rows,
        "missing_values": missing,
        "overall_score": max(0, 100 - len(missing) * 5),
    }


def ingest_file(path: Path) -> Dataset:
    rows = load_rows(path)
    schema = infer_schema(rows)
    quality = quality_report(rows, schema)
    return Dataset(rows=rows, schema=schema, quality=quality)
