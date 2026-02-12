# ReportStudio v2.0 技术设计基线（OpenClaw Skill）

## 1) 技术定位
- ReportStudio v2.0 以 OpenClaw Skill 形态运行，不是独立 SaaS。
- 采用 AgentSkills 规范：`SKILL.md + scripts/ + references/ + assets/`。
- 通过自然语言触发 Intent，再路由到脚本执行。

## 2) 架构总览
- 接入层：OpenClaw Gateway / Agent Runtime。
- Skill 层：入口路由（SKILL.md）+ 执行脚本（scripts）+ 知识引用（references）。
- 核心服务层：Ingest / Metrics / Analysis / Insight / Chart / Layout / Preview / Export / Collab / Scheduler / Version / Lineage / Workspace。
- 存储层：SQLite 或 PostgreSQL + 文件系统或对象存储。

## 3) 关键技术选型
- 主语言：Python 3.11+
- 辅助语言：Node.js 20 LTS（DOCX/PPTX 辅助构建）
- 数据：pandas + pyarrow
- Web：FastAPI + WebSocket（Preview）
- 异步：Celery + Redis
- 图表：matplotlib/plotly（静态）+ ECharts（交互）
- 导出：WeasyPrint/openpyxl/python-pptx

## 4) Intent 路由原则
- 每个 Intent 必须绑定脚本入口。
- 每个入口定义：输入参数、权限前置、副作用、错误码、降级策略。
- 先判权限，再做重计算，再写审计日志。

## 5) 安全与治理
- RBAC + 行级过滤 + 字段脱敏。
- 下载链接签名（HMAC-SHA256）与过期控制。
- 关键操作审计全留痕（TraceID 贯穿）。

## 6) 性能目标（建议）
- 小数据上传解析 P50 <= 3s
- 指标计算（<=1万行、<=20指标）P50 <= 5s
- Preview 编辑响应 P50 <= 2s
- 洞察生成 P50 <= 5s
- 导出 PDF P50 <= 30s
- 血缘查询（深度<=5）P50 <= 1.5s

## 7) 分期里程碑
- M1（4周）：Ingest + Metrics + Analysis + Chart + Layout + Export 核心闭环。
- M2（3周）：Insight + Preview + 模板与自动暂存。
- M3（3周）：Collab + Version + Lineage + ACL + Scheduler。
- M4（2周）：性能优化、安全加固、评估用例与发布。
