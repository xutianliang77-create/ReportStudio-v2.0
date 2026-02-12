"""DOCX export from intermediate artifacts.

Inputs are loaded from intermediate files:
- kpis.json
- tables.json
- images/*.png
- glossary.json
"""

from __future__ import annotations

from pathlib import Path
import json
import zipfile


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def load_intermediate(intermediate_dir: Path) -> dict:
    kpis_file = intermediate_dir / "kpis.json"
    tables_file = intermediate_dir / "tables.json"
    glossary_file = intermediate_dir / "glossary.json"
    images_dir = intermediate_dir / "images"

    if not kpis_file.exists() or not tables_file.exists() or not glossary_file.exists():
        raise FileNotFoundError("missing required intermediate files")

    kpis = json.loads(kpis_file.read_text(encoding="utf-8"))
    tables = json.loads(tables_file.read_text(encoding="utf-8"))
    glossary = json.loads(glossary_file.read_text(encoding="utf-8"))
    images = sorted(images_dir.glob("*.png")) if images_dir.exists() else []

    return {
        "kpis": kpis,
        "tables": tables,
        "glossary": glossary,
        "images": images,
    }


def _paragraph(text: str, *, heading: bool = False) -> str:
    if heading:
        return (
            '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
            f'<w:r><w:t>{_xml_escape(text)}</w:t></w:r></w:p>'
        )
    return f'<w:p><w:r><w:t>{_xml_escape(text)}</w:t></w:r></w:p>'


def _table(rows: list[dict]) -> str:
    if not rows:
        return _paragraph("(no table rows)")
    headers = list(rows[0].keys())

    def row_xml(values: list[str]) -> str:
        tcs = "".join(
            f"<w:tc><w:p><w:r><w:t>{_xml_escape(v)}</w:t></w:r></w:p></w:tc>" for v in values
        )
        return f"<w:tr>{tcs}</w:tr>"

    body = [row_xml(headers)]
    for row in rows:
        body.append(row_xml([str(row.get(h, "")) for h in headers]))
    return "<w:tbl>" + "".join(body) + "</w:tbl>"


def build_docx(out_file: Path, *, title: str, intermediate: dict) -> Path:
    kpis = intermediate.get("kpis", {})
    tables = intermediate.get("tables", {})
    glossary = intermediate.get("glossary", {})
    images: list[Path] = intermediate.get("images", [])

    kpi_lines = [f"{k}: {v}" for k, v in kpis.items()]
    rows = tables.get("rows", []) if isinstance(tables, dict) else []

    glossary_lines: list[str]
    if isinstance(glossary, dict):
        glossary_lines = [f"{k}: {v}" for k, v in glossary.items()]
    elif isinstance(glossary, list):
        glossary_lines = [str(x) for x in glossary]
    else:
        glossary_lines = [str(glossary)]

    parts: list[str] = []
    parts.append(_paragraph(title, heading=True))
    parts.append(_paragraph("摘要（KPI）", heading=True))
    for line in kpi_lines or ["(no kpi)"]:
        parts.append(_paragraph(line))

    parts.append(_paragraph("图表", heading=True))
    for img in images or []:
        # Keep editable Word document structure simple in scaffold;
        # image file list is included as figure references.
        parts.append(_paragraph(f"插图: {img.name}"))

    parts.append(_paragraph("汇总表", heading=True))
    parts.append(_table(rows if isinstance(rows, list) else []))

    parts.append(_paragraph("口径与数据说明", heading=True))
    for line in glossary_lines or ["(no glossary)"]:
        parts.append(_paragraph(line))

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{''.join(parts)}</w:body>"
        "</w:document>"
    )

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)
    return out_file
