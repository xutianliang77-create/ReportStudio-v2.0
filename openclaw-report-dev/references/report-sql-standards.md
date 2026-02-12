# Report SQL Standards (OpenClaw)

## Query Structure
- Use layered CTEs in this order: `base` -> `standardized` -> `aggregated` -> `final`.
- Keep business logic out of the final SELECT when possible.
- Use explicit column lists; avoid `SELECT *`.

## Naming
- Facts: `fact_<domain>`.
- Dimensions: `dim_<subject>`.
- Derived fields: `<metric>_<window>` (example: `revenue_mtd`).
- Boolean flags: `is_<state>`.

## Time Handling
- Convert event timestamps to the reporting timezone before bucketing.
- Provide both `date_key` and `week_key`/`month_key` when reporting period is configurable.

## Data Quality Guards
- Deduplicate with deterministic priority (updated_at desc, ingestion_time desc).
- Exclude canceled/invalid rows using documented status mapping.
- Handle null amounts with explicit `coalesce` rules and explain implications.

## Performance Baseline
- Filter partitions in `base` CTE.
- Aggregate as early as correctness allows.
- Cap high-cardinality dimensions unless required for drill-down.

## Validation
- Compare total row count and 2-3 key sums with trusted source.
- Validate boundary dates (month-end, leap day, timezone cutover).
- Validate at least one empty-result scenario (no data in range).
