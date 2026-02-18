"""P1-401~P1-404: 导出与产物登记（JSON / XLSX / PDF）。"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from pathlib import Path
import hashlib
import json
import zipfile


SUPPORTED_EXPORT_FORMATS = frozenset({"json", "xlsx", "pdf"})


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(snapshot: dict, target: Path) -> None:
    target.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")


def _xlsx_cell(value: str) -> str:
    safe = (value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"<c t=\"inlineStr\"><is><t>{safe}</t></is></c>"


def _write_xlsx(snapshot: dict, target: Path) -> None:
    rows = snapshot.get("topn", [])
    headers = list(rows[0].keys()) if rows else ["message"]
    if not rows:
        rows = [{"message": "no data"}]

    sheet_rows = [headers] + [[str(r.get(h, "")) for h in headers] for r in rows]
    row_xml = []
    for i, row in enumerate(sheet_rows, start=1):
        cells = "".join(_xlsx_cell(v) for v in row)
        row_xml.append(f"<row r=\"{i}\">{cells}</row>")

    sheet_data = "".join(row_xml)

    content_types = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">
  <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>
  <Default Extension=\"xml\" ContentType=\"application/xml\"/>
  <Override PartName=\"/xl/workbook.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml\"/>
  <Override PartName=\"/xl/worksheets/sheet1.xml\" ContentType=\"application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml\"/>
</Types>"""

    rels = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument\" Target=\"xl/workbook.xml\"/>
</Relationships>"""

    workbook = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">
  <sheets>
    <sheet name=\"report\" sheetId=\"1\" r:id=\"rId1\"/>
  </sheets>
</workbook>"""

    wb_rels = """<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">
  <Relationship Id=\"rId1\" Type=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet\" Target=\"worksheets/sheet1.xml\"/>
</Relationships>"""

    sheet = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">
  <sheetData>{sheet_data}</sheetData>
</worksheet>"""

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        zf.writestr("xl/worksheets/sheet1.xml", sheet)


def _write_pdf(snapshot: dict, target: Path) -> None:
    title = "ReportStudio Export"
    metric = snapshot.get("metrics", {})
    lines = [
        title,
        f"sum={metric.get('sum', '-')}",
        f"count={metric.get('count', '-')}",
        f"avg={metric.get('avg', '-')}",
    ]
    text = "\\n".join(lines)
    stream = f"BT /F1 12 Tf 72 740 Td ({text}) Tj ET"
    pdf = (
        "%PDF-1.4\n"
        "1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        "2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
        "3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n"
        "4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
        f"5 0 obj<</Length {len(stream)}>>stream\n{stream}\nendstream endobj\n"
        "xref\n0 6\n0000000000 65535 f \n"
        "0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n"
        "0000000243 00000 n \n0000000313 00000 n \n"
        "trailer<</Size 6/Root 1 0 R>>\nstartxref\n430\n%%EOF"
    )
    target.write_bytes(pdf.encode("latin-1", errors="ignore"))


def export_report(
    snapshot: dict,
    out_dir: Path,
    report_name: str = "report",
    fmt: str = "json",
    artifact_id: str | None = None,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    fmt = fmt.lower()
    if fmt not in SUPPORTED_EXPORT_FORMATS:
        raise ValueError(f"Unsupported export format: {fmt}")

    stamp = _utc_stamp()
    random_suffix = uuid4().hex
    unique_id = f"{artifact_id}_{random_suffix}" if artifact_id else random_suffix
    target = out_dir / f"{report_name}_{stamp}_{unique_id}.{fmt}"

    if fmt == "json":
        _write_json(snapshot, target)
    elif fmt == "xlsx":
        _write_xlsx(snapshot, target)
    else:
        _write_pdf(snapshot, target)

    return {
        "file": str(target),
        "sha256": _sha256(target),
        "format": fmt,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
