"""P1-401~P1-404: 导出与产物登记。"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import uuid


_SAFE_TOKEN_RE = re.compile(r"[^A-Za-z0-9_-]+")


def _safe_token(value: object | None) -> str:
    if value is None:
        return ""
    return _SAFE_TOKEN_RE.sub("", str(value))


def export_report(snapshot: dict, out_dir: Path, report_name: str = "report") -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    trace_token = _safe_token(snapshot.get("trace_id"))
    entropy = trace_token or uuid.uuid4().hex
    file_name = f"{report_name}_{stamp}_{entropy}.json"
    target = out_dir / file_name
    target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    return {"file": str(target), "sha256": digest, "generated_at": datetime.now(timezone.utc).isoformat()}
