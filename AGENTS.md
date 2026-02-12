# AGENTS.md

## Repository intent
This repository contains the OpenClaw ReportStudio v2.0 skill package and an implementation scaffold.

## Development rules
- Keep skill documentation and implementation scaffold in sync.
- When adding a new intent, update both:
  - `openclaw-report-dev/references/report-intent-catalog.md`
  - `reportstudio/config/intent_routes.json`
- Prefer small, testable Python modules under `reportstudio/`.
- Add/adjust tests in `tests/` for any routing or validation behavior changes.

## Packaging
- Rebuild `openclaw-report-dev.skill` after skill content changes.
