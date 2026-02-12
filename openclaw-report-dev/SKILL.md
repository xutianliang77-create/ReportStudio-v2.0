---
name: openclaw-report-dev
description: 为 OpenClaw 生成和迭代 ReportStudio v2.0 企业级报表方案与技术设计，覆盖14模块能力、31个Intent、技能目录拆分、脚本路由、数据库与API规范、安全权限、性能优化、部署运维与分期里程碑。用于创建/修改报表产品方案、输出技术设计文档、定义实现计划、排查链路问题并沉淀可复用标准模板。
---

# OpenClaw ReportStudio v2.0 Skill

## 工作方式

按以下顺序产出，确保“可实现 + 可验收 + 可运维”：

1. 需求澄清
   - 明确角色与场景（运营、管理层、财务、分析师、主管）。
   - 明确目标指标（成功率、性能、转化、安全）。
2. 产品与技术双映射
   - 先映射 14 个产品模块与 31 个 Intent。
   - 再映射 Skill 技术架构：`SKILL.md + scripts/ + references/ + assets/`。
3. Intent 与脚本路由设计
   - 为每个关键 Intent 明确入口脚本、输入参数、权限前置、失败处理。
4. 技术方案深化
   - 输出目录结构、核心模块实现、数据库模型、API 规范、安全合规、性能策略、部署方案。
5. 验证与收口
   - 按验收清单逐项自检。
   - 明确阻塞项、风险与灰度发布建议。

## 强制输出结构

处理报表产品或技术方案任务时，按以下顺序输出：

1. **目标与范围**
2. **用户场景与角色映射**
3. **功能设计（14 模块）**
4. **Intent 列表与脚本路由**
5. **Skill 架构与目录拆分**
6. **核心数据结构 / 数据库设计**
7. **API 设计与错误码约定**
8. **安全与合规策略**
9. **非功能性指标与性能优化**
10. **部署运维与里程碑计划**
11. **验收用例与风险缓解**

## 规则与护栏

- 不只出“产品需求”，必须给出“可执行技术方案”。
- 不只定义“功能点”，必须给出“脚本入口与路由责任”。
- 不只定义“模块能力”，必须给出“DB/API/权限/审计可落地约束”。
- 不只“可运行”，必须绑定性能目标（P50/P99）和安全边界。
- 若需求冲突，优先遵循 `references/reportstudio-v2-baseline.md` 与 `references/reportstudio-v2-technical-design.md`。

## 资源使用指引

- 产品基线：`references/reportstudio-v2-baseline.md`
- 技术设计：`references/reportstudio-v2-technical-design.md`
- 模块实现蓝图：`references/report-module-implementation-blueprint.md`
- 数据库与 API 规范：`references/report-db-api-spec.md`
- Intent 清单：`references/report-intent-catalog.md`
- 验收门禁：`references/report-acceptance-checklist.md`
- 安全与合规模板：`references/report-security-compliance.md`
- 标准交付模板：`assets/report-design-spec-template.md`
- P1 交付状态：`references/report-p1-delivery-status.md`
