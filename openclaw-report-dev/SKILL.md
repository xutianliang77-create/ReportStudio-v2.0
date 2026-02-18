---
name: openclaw-report-dev
description: Build and iterate OpenClaw ReportStudio workflows with engineering-ready outputs. Use for report create/analyze/preview/render/export/download capabilities, intent routing, ACL/security/masking, versioning, scheduling, and scaffold troubleshooting. This skill requires design + implementation alignment (not design-only docs).
---

# OpenClaw ReportStudio v2.0 Skill

本 skill 用于把“报表需求”转换为**可实现、可测试、可交付**的结果。

## 1) 适用范围（What to use this for）

优先用于以下任务：

- 报表制作、分析、预览、渲染、导出、下载流程设计与实现。
- Intent 路由设计、脚手架代码变更、测试补齐。
- 安全能力：ACL/RBAC、脱敏、审计日志。
- 版本能力：report/template 版本、回滚、可追溯变更。
- 现有流程排障与一致性修复（文档-代码-测试三者一致）。

## 2) 当前仓库能力焦点（Align with scaffold）

按以下能力优先映射与交付：

1. Report / Render 基础流程（create/render/get）
2. Preview Session（create/get/patch/replay）
3. Export（json/xlsx/pdf/docx）与 Artifact 下载
4. ACL/RBAC（E4001/E4002）
5. Masking 与审计日志
6. 版本管理与回滚（report/template）

## 3) 执行顺序（Execution workflow）

1. Clarify Scope
   - 明确目标、输入输出、约束、验收标准。
2. Map to Modules + Intents
   - 映射模块、路由、脚本入口。
3. Design + Implement Together
   - 方案与代码同步，不做“只写文档”或“只改代码”。
4. Validate
   - 运行对应测试与必要检查。
5. Deliver
   - 输出变更摘要、验证结果、风险与后续项。

## 4) 强制工程规则（Must follow）

- Keep skill documentation and implementation scaffold in sync.
- 变更 Intent 时，必须同步更新：
  - `openclaw-report-dev/references/report-intent-catalog.md`
  - `reportstudio/config/intent_routes.json`
- 优先小而可测的 Python 模块（`reportstudio/`）。
- 路由/校验行为变更必须补测试（`tests/`）。
- 导出流程应复用中间产物，禁止导出阶段重算上游 pipeline。
- 安全相关能力必须给出错误码与审计日志。
- 技能内容改动后需重新打包 `openclaw-report-dev.skill`。

## 5) 默认交付结构（Output contract）

每次交付默认按以下结构输出：

1. Goal & Scope
2. Affected Modules / Routes
3. Data Contracts / Error Codes
4. Implementation Changes
5. Validation (tests/checks)
6. Risks / Open Questions

## 6) 参考资料按需加载（Load on demand）

- Intent catalog: `references/report-intent-catalog.md`
- DB/API spec: `references/report-db-api-spec.md`
- Module blueprint: `references/report-module-implementation-blueprint.md`
- Technical baseline: `references/reportstudio-v2-technical-design.md`
- Security compliance: `references/report-security-compliance.md`
- Acceptance checklist: `references/report-acceptance-checklist.md`
- Delivery template: `assets/report-design-spec-template.md`

仅加载当前任务所需文件，避免上下文膨胀。
