# CODEx TODO

## Delivered in this iteration
- [x] P1-001 ~ P1-007 基础设施（`reportstudio/p1/infrastructure.py`）
- [x] P1-101 ~ P1-107 Ingest（`reportstudio/p1/ingest.py`）
- [x] P1-201 ~ P1-204 Metrics + Analysis（`reportstudio/p1/metrics_analysis.py`）
- [x] P1-301 ~ P1-303 Charts + Layout（`reportstudio/p1/charts_layout.py`）
- [x] P1-401 ~ P1-404 Export + Artifact（`reportstudio/p1/export_artifact.py`）
- [x] P1-501 ~ P1-502 Dispatch & E2E（`reportstudio/p1/dispatch.py`, `reportstudio/scripts/report/create.py`）
- [x] Added tests for ingest/metrics/e2e pipeline (`tests/test_p1_pipeline.py`)
- [x] Add dedicated download metadata helper (`reportstudio/scripts/export/download.py`)

## Next steps
- [ ] Upgrade ingest to support XLSX/Markdown and encoding fallback.
- [ ] Add DSL parser/validator in `reportstudio/scripts/metrics/`.
- [ ] Replace JSON export placeholder with PDF/XLSX concrete exporters.
- [ ] Add CI workflow for unit tests and lint checks.
