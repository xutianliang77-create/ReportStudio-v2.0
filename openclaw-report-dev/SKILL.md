---
name: openclaw-report-dev
description: Build and iterate OpenClaw ReportStudio v2.0 workflows with engineering-ready outputs: requirement clarification, 14-module capability mapping, intent-to-script routing, technical design (architecture/DB/API/security/performance), implementation planning, and delivery validation. Use for report create/analyze/preview/render/export/download, ACL/security/masking, versioning, scheduling, and scaffold troubleshooting.
---

# OpenClaw ReportStudio v2.0 Skill

本 skill 用于把“报表需求”转换为**可实现、可测试、可交付**的结果（设计与实现并重）。

## Execute in This Order

1. Clarify Scope
   - 明确目标、输入输出、约束、验收标准。
2. Map to Modules + Intents
   - 将需求映射到 14 模块、路由和脚本入口。
3. Design + Implement Together
   - 输出方案并同步落地到脚手架，不做“只写文档”或“只改代码”。
4. Validate
   - 运行对应测试与必要检查。
5. Deliver
   - 输出改动摘要、验证结果、风险与后续项。

## Current Scaffold Capability Focus

优先覆盖以下能力：

1. Report / Render 基础流程（create/render/get）
2. Preview Session（create/get/patch/replay）
3. Export（json/xlsx/pdf/docx）与 Artifact 下载
4. ACL/RBAC（E4001/E4002）
5. Masking 与审计日志
6. 版本管理与回滚（report/template）

## Required Output Format

默认按以下结构交付：

1. Goal & Scope
2. User Roles / Scenarios
3. Module Mapping & Intent Routing
4. Architecture / Repository Touchpoints
5. Data Contracts & Error Codes
6. Implementation Changes
7. Validation (tests/checks)
8. Risks / Open Questions

## Mandatory Engineering Rules

- Keep skill documentation and implementation scaffold in sync.
- 变更 Intent 时，必须同步更新：
  - `openclaw-report-dev/references/report-intent-catalog.md`
  - `reportstudio/config/intent_routes.json`
- 优先小而可测的 Python 模块（`reportstudio/`）。
- 路由/校验行为变更必须补测试（`tests/`）。
- 导出流程应复用中间产物，禁止导出阶段重算上游 pipeline。
- 安全相关能力必须给出错误码与审计日志。
- 技能内容改动后需重新打包 `openclaw-report-dev.skill`。

## Resource Loading Guide (load on demand)

- Product baseline: `references/reportstudio-v2-baseline.md`
- Technical baseline: `references/reportstudio-v2-technical-design.md`
- Module blueprint: `references/report-module-implementation-blueprint.md`
- DB/API spec: `references/report-db-api-spec.md`
- Intent catalog: `references/report-intent-catalog.md`
- Acceptance checklist: `references/report-acceptance-checklist.md`
- Security compliance: `references/report-security-compliance.md`
- Delivery template: `assets/report-design-spec-template.md`
- P1 delivery status: `references/report-p1-delivery-status.md`

仅加载当前任务所需文件，避免上下文膨胀。
