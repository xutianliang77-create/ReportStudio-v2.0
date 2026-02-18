---
name: openclaw-report-dev
description: Design and implement OpenClaw ReportStudio workflows with executable routing and verifiable outputs. Use when users ask for report creation, analysis, preview editing, render/export/download, ACL/security, masking, versioning, scheduling, or troubleshooting report pipelines. This skill is for engineering-ready plan + scaffold implementation alignment (not only high-level product copy).
---

# OpenClaw ReportStudio v2.0 Skill

Use this skill when the task needs **可实现、可测试、可交付**的报表能力设计与实现对齐。

## Skill Positioning

- 本 skill 面向 OpenClaw 的报表能力研发与迭代。
- 输出必须同时覆盖：
  - 业务方案（目标、场景、验收）
  - 技术方案（路由、数据结构、API、安全、性能）
  - 代码落地（脚手架改动、测试、可验证结果）
- 对于“报表制作、分析、下载/导出”相关需求，必须给出可执行路径，而不是仅概念描述。

## Current Scaffold Capability Focus (align with repository)

在当前仓库实现语义下，优先按以下能力组织回答与变更：

1. Report/Render 基础流程（create/render/get）
2. Preview Session（create/get/patch/replay）
3. Export 能力（json/xlsx/pdf/docx）
4. Artifact 下载与签名链接
5. ACL/RBAC 与鉴权拒绝码（E4001/E4002）
6. 脱敏（masking）与审计日志
7. 版本管理与回滚（report/template）

## Execution Workflow

按以下顺序执行：

1. **Clarify Scope**
   - 明确目标能力、输入输出、是否涉及 API/路由/数据模型。
2. **Map to Modules + Intents**
   - 将需求映射到模块、路由和脚本入口。
3. **Design + Implement Together**
   - 文档与代码同步更新，避免“文档说有、代码没有”。
4. **Validate**
   - 至少运行对应测试与必要静态检查。
5. **Deliver**
   - 输出改动摘要、测试结果、风险与后续项。

## Mandatory Engineering Rules

- Keep skill docs and implementation scaffold in sync.
- 当新增/修改 intent 时，必须同时更新：
  - `openclaw-report-dev/references/report-intent-catalog.md`
  - `reportstudio/config/intent_routes.json`
- 优先小而可测的 Python 模块（`reportstudio/` 下）。
- 路由或校验行为变更必须补测试（`tests/`）。
- 导出类能力应复用中间产物，禁止导出阶段重算上游 pipeline。
- 安全相关能力（ACL/脱敏/下载）必须有错误码与审计日志。

## Required Output Contract

每次交付默认按以下结构输出：

1. Goal & Scope
2. Affected Modules / Routes
3. Data Contracts / Error Codes
4. Implementation Changes
5. Validation (tests/checks)
6. Risks / Open Questions

## Resource Loading (load on demand)

- Intent catalog: `references/report-intent-catalog.md`
- DB/API spec: `references/report-db-api-spec.md`
- Module blueprint: `references/report-module-implementation-blueprint.md`
- Technical baseline: `references/reportstudio-v2-technical-design.md`
- Security compliance: `references/report-security-compliance.md`
- Acceptance checklist: `references/report-acceptance-checklist.md`
- Delivery template: `assets/report-design-spec-template.md`

仅加载当前任务需要的文件，避免无关上下文膨胀。
