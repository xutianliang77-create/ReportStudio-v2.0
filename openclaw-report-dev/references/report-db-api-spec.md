# 数据库与 API 规范（精简版）

## 1) 核心数据表
- `workspaces`：空间与归属
- `reports`：报表主表
- `datasets`：数据集元信息与 Schema
- `templates`：模板结构与样式
- `report_versions`：版本快照与哈希
- `review_flows` / `comments`：评审与批注
- `schedules` / `subscribers`：调度与订阅
- `lineage_nodes` / `lineage_edges`：血缘图
- `permissions`：RBAC + 行级 + 脱敏策略
- `audit_logs`：全链路审计
- `exports` / `execution_logs`：导出与执行记录

## 2) API 设计原则
- 路径风格：`/api/v1/{module}/{resource}`
- 响应统一：`code/message/data/trace_id/timestamp`
- 错误统一：`error_code + suggestion`
- 所有写操作必须记录审计日志。

## 3) 关键 API 组
- Ingest: upload/paste/schema/preview/quality/clean/join/append
- Metrics: define/validate/compute/glossary/dependencies
- Analysis: groupby/pivot/time-agg/topn/contribution/anomaly/comparison
- Insight: generate/drilldown/forecast/feedback/watch-config
- Preview: session/edit/undo/redo/save/params/paged
- Export: submit/status/progress/download
- Collab: comment/review submit/approve/reject/withdraw/activity
- Scheduler: schedule CRUD/enable/disable/run/subscription/logs
- Version: list/save/diff/rollback/release
- Lineage: collect/upstream/downstream/graph/impact/export/health
- Workspace & ACL: workspace CRUD/member/permission set/check

## 4) 常见错误码建议
- `IE_FORMAT_UNSUPPORTED`
- `IE_FILE_TOO_LARGE`
- `ME_FIELD_NOT_FOUND`
- `ME_CIRCULAR_DEPENDENCY`
- `IN_INSUFFICIENT_HISTORY`
- `PS_SESSION_NOT_FOUND`
- `EX_EXPORT_FAILED`
- `RV_REVIEW_REQUIRED`
- `AC_PERMISSION_DENIED`


## 5) P1 API facade (implemented in scaffold)
- `reports.create`
- `renders.create`
- `artifacts.get`
- P1 API facade: reports.create / renders.create / artifacts.get


## 6) P1 deterministic command parsing
- `create report` -> `reports.create`
- `render json|xlsx|pdf` -> `renders.create`
- `download artifact` -> `artifacts.get`
