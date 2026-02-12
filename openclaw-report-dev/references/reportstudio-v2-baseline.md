# ReportStudio v2.0 基线（OpenClaw）

## 1. 目标闭环
数据接入 -> 指标计算 -> 自动分析 -> 智能洞察 -> 图表生成 -> 模板排版 -> 交互预览 -> 协作评审 -> 文件导出 -> 模板复用 -> 调度订阅 -> 安全审计。

## 2. 关键成功指标（上线 30 天）
- 报表生成成功率 >= 99%
- 首次预览 P50 <= 8s
- 编辑渲染 P50 <= 2s
- 导出成功率 >= 99%
- 模板复用率 >= 30%
- 预览到导出转化 >= 80%
- 自动暂存成功率 >= 99.9%
- 权限/数据安全事故 = 0

## 3. 角色
- 运营：周期报表制作与订阅
- 管理层：KPI 与摘要阅读、审批
- 财务：对账与差异分析
- 数据分析师：DSL 指标、自定义分析、血缘追溯
- 团队主管：评审、模板治理、权限管理

## 4. 模块清单（14）
1) Ingest Engine
2) Metrics Engine
3) Analysis Engine
4) Insight Engine
5) Chart Engine
6) Layout Engine
7) Preview Studio
8) Export Engine
9) Collaboration Engine
10) Scheduler Engine
11) Version Control
12) Lineage Tracker
13) Workspace & ACL
14) Artifact Store

## 5. 关键新增能力（V2.0）
- Insight Engine：异常、归因、关键发现、趋势预测
- Preview Studio：所见即所得编辑、撤销重做、自动暂存
- Collaboration Engine：评审状态机、批注、签核
- Scheduler Engine：cron 调度、失败重试、多渠道分发
- Version Control：版本快照、Diff、回滚
- Lineage Tracker：正反向血缘、影响分析、断链检测
- Workspace & ACL：工作空间隔离、RBAC、行列级权限

## 6. 默认报表结构
1. 封面
2. 智能摘要
3. KPI 卡片
4. 趋势分析
5. 结构分析
6. 明细表
7. 口径说明

## 7. 关键状态机
草稿 -> 待审核 -> 已通过/驳回修改 -> 已定稿。

## 8. 架构依赖（简版）
Ingest -> Metrics -> Analysis <-> Insight -> Chart -> Layout -> Preview -> Export -> Scheduler
                              \-> Collaboration / Version / ACL / Lineage（全链路治理）
