# reportstudio scaffold

This folder is a lightweight technical scaffold aligned with the `openclaw-report-dev` skill docs.

## Structure
- `router.py`: intent-to-script resolver.
- `config/intent_routes.json`: canonical route table for core intents.
- `scripts/`: script entrypoints.
- `p1/`: P1 baseline implementation modules (infra/ingest/metrics/charts/export/dispatch).

## Usage
```bash
python3 -m reportstudio.router report.create
python3 reportstudio/scripts/report/create.py --input tests/fixtures/sales.csv --metric-field amount --dimension-field region
python3 reportstudio/scripts/export/export.py --input tests/fixtures/sales.csv --metric-field amount --dimension-field region --format json
python3 reportstudio/scripts/export/export.py --input tests/fixtures/sales.csv --metric-field amount --dimension-field region --format xlsx
python3 reportstudio/scripts/export/export.py --input tests/fixtures/sales.csv --metric-field amount --dimension-field region --format pdf
# then use output artifact path with:
python3 reportstudio/scripts/export/download.py --file <artifact_path>
# API simulator endpoints:
python3 reportstudio/scripts/preview/serve.py reports.create --input tests/fixtures/sales.csv
python3 reportstudio/scripts/preview/serve.py renders.create --input tests/fixtures/sales.csv --format xlsx
python3 reportstudio/scripts/preview/serve.py artifacts.get --file <artifact_path>
# deterministic command parsing:
python3 reportstudio/scripts/preview/serve.py --command "create report" --input tests/fixtures/sales.csv
python3 reportstudio/scripts/preview/serve.py --command "render pdf" --input tests/fixtures/sales.csv --format pdf
python3 reportstudio/scripts/preview/serve.py --command "download artifact" --file <artifact_path>
```
