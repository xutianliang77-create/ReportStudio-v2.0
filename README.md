# ReportStudio-v2.0

OpenClaw 的企业级报表 Skill 仓库（ReportStudio v2.0）。

## Repository map

- `AGENTS.md`：仓库协作规则与变更同步要求。
- `CODEx_TODO.md`：当前交付与下一步实现任务清单。
- `openclaw-report-dev/`：可分发的 Skill 内容（SKILL.md / references / assets）。
- `reportstudio/`：技术实现脚手架（intent 路由、P1 基础实现、入口脚本）。
- `tests/`：基础单元测试（当前覆盖 intent 路由行为）。

## Skill references

- `openclaw-report-dev/SKILL.md`：Skill 主流程（需求澄清、14 模块映射、Intent 路由、技术方案与验收）。
- `openclaw-report-dev/references/reportstudio-v2-baseline.md`：产品基线与成功指标。
- `openclaw-report-dev/references/reportstudio-v2-technical-design.md`：技术架构、选型、安全、性能、里程碑。
- `openclaw-report-dev/references/report-module-implementation-blueprint.md`：14 模块实现蓝图。
- `openclaw-report-dev/references/report-db-api-spec.md`：数据库与 API 规范。

## Packaging

```bash
zip -r openclaw-report-dev.skill openclaw-report-dev
```

> Note: `*.skill` is a generated binary artifact and is intentionally ignored by git.

## Local check

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 reportstudio/scripts/report/create.py --input tests/fixtures/sales.csv --metric-field amount --dimension-field region
```
