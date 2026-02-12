# Report Delivery Checklist (OpenClaw)

## 1) Requirement Freeze
- [ ] Audience and decision use case confirmed.
- [ ] Required KPIs and dimensions confirmed.
- [ ] Refresh schedule and data latency accepted.

## 2) Metric Contract
- [ ] Every KPI has a formula and aggregation rule.
- [ ] Inclusion/exclusion criteria documented.
- [ ] Default filters and date range documented.

## 3) Dataset Readiness
- [ ] SQL runs successfully.
- [ ] Join keys and cardinality validated.
- [ ] Duplicate prevention strategy documented.

## 4) Visualization Readiness
- [ ] Chart type aligns with analytical intent.
- [ ] Sorting, labels, and units are consistent.
- [ ] Drill path and interaction behavior documented.

## 5) Quality & Reconciliation
- [ ] Totals reconciled with trusted source.
- [ ] Edge cases tested (nulls, zeros, no data, date boundaries).
- [ ] Known limitations and risk notes included.

## 6) Handoff
- [ ] Final spec delivered with SQL and metric dictionary.
- [ ] Open questions and follow-up tasks listed.
- [ ] Version tag/date/owner documented.
