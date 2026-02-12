# ReportStudio Intent Catalog（v2.0）

## 报表核心
- `report.create`：创建报表
- `report.preview`：快速预览
- `report.preview.edit`：编辑预览
- `report.preview.switch`：切换预览模式（quick/edit/paged/mobile）
- `report.preview.undo` / `report.preview.redo`
- `report.preview.save`
- `report.update`
- `report.explain`
- `report.export`（支持 json/xlsx/pdf 导出）
- `report.download`

## 模板
- `report.template.save`
- `report.template.apply`

## 洞察
- `report.insight.generate`
- `report.insight.drilldown`
- `report.insight.configure`

## 协作评审
- `report.review.submit`
- `report.review.approve`
- `report.review.reject`
- `report.comment.add`

## 调度订阅
- `report.schedule.create`
- `report.schedule.pause`
- `report.schedule.trigger`
- `report.subscribe`

## 版本管理
- `report.version.list`
- `report.version.compare`
- `report.version.restore`

## 数据血缘
- `report.lineage.trace`
- `report.lineage.impact`

## 空间权限
- `workspace.switch`
- `report.permission.set`
- `report.permission.check`

## Intent 输出建议字段
每个 Intent 设计建议至少包含：
- `intent`
- `input`
- `preconditions`（权限、数据可用性）
- `side_effects`（是否创建版本/审计日志）
- `error_codes`
- `fallback`
