"""Artifact export service for intermediate-driven exports."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib

from reportstudio.core.export.docx import build_docx, load_intermediate
from reportstudio.core.render.job_service import append_audit_log


class ExportDocxError(RuntimeError):
    code = "E3003"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_presigned_url(artifact_id: str, ext: str) -> str:
    # Scaffold URL; in production this should be signed and expiring.
    return f"https://example.local/artifacts/{artifact_id}.{ext}?token=stub-presigned"


def export_docx_artifact(*, render_id: str, intermediate_dir: Path, out_dir: Path, title: str = "Report") -> dict:
    try:
        intermediate = load_intermediate(intermediate_dir)
        out_file = out_dir / f"{render_id}.docx"
        build_docx(out_file, title=title, intermediate=intermediate)
        size = out_file.stat().st_size
        if size <= 0:
            raise ExportDocxError("empty docx artifact")

        sha = _sha256(out_file)
        append_audit_log(
            render_id,
            "export.docx",
            {
                "status": "succeeded",
                "artifact_file": str(out_file),
                "size": size,
            },
        )
        return {
            "artifact_id": render_id,
            "format": "docx",
            "file": str(out_file),
            "size": size,
            "sha256": sha,
            "generated_at": _now(),
            "download_url": create_presigned_url(render_id, "docx"),
        }
    except Exception as exc:  # noqa: BLE001
        append_audit_log(
            render_id,
            "export.docx",
            {
                "status": "failed",
                "error_code": "E3003",
                "error_message": str(exc),
            },
        )
        err = ExportDocxError(str(exc))
        raise err
