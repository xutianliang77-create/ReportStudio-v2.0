---
name: openclaw-report-dev
description: Build and iterate OpenClaw ReportStudio v2.0 solutions end-to-end: requirement clarification, 14-module capability mapping, intent-to-script routing, technical design (architecture/DB/API/security/performance), implementation planning, and delivery validation. Use when users ask to create or revise report platforms, implement report pipelines, define/report intents, troubleshoot report workflows, or produce reusable report specs and engineering handoff artifacts, including report creation, analysis, export and download workflows.
---

# OpenClaw ReportStudio v2.0 Skill

Use this skill to convert report requirements into **implementable** and **verifiable** outputs for OpenClaw.

## Execute in This Order

1. Clarify target
   - Confirm business scenario, target users, and success criteria.
   - Confirm scope boundaries (in-scope / out-of-scope).
2. Map capabilities
   - Map needs to the 14 ReportStudio modules.
   - Map requested actions to intents and script entrypoints.
3. Produce design
   - Produce product design + technical design together.
   - Include architecture, data model, APIs, security controls, and performance goals.
4. Produce implementation plan
   - Break down into milestones and testable tasks.
   - Mark dependencies and risks.
5. Validate delivery
   - Run acceptance checklist.
   - Output unresolved questions and launch blockers.

## Required Output Format

Always output sections in this sequence:

1. Goal and Scope
2. User Roles and Scenarios
3. Module Design (14 modules)
4. Intents and Script Routing
5. Architecture and Repository Structure
6. Data Model / Database Design
7. API Contracts and Error Codes
8. Security and Compliance Controls
9. Performance Targets and Optimization Plan
10. Delivery Milestones and Validation Plan
11. Risks, Mitigations, and Open Issues

## Routing and Implementation Rules

- Route each actionable request to a clear intent and script path.
- Ensure report creation/analysis/export/download flows are all covered by intents and scripts.
- Keep skill docs and scaffold code aligned.
- If adding or changing intents, update both:
  - `openclaw-report-dev/references/report-intent-catalog.md`
  - `reportstudio/config/intent_routes.json`
- Prefer small, testable Python modules under `reportstudio/`.
- Add or update tests for routing/validation behavior changes.

## Resource Loading Guide

Load only the references needed for the current task:

- Product baseline: `references/reportstudio-v2-baseline.md`
- Technical baseline: `references/reportstudio-v2-technical-design.md`
- Module blueprint: `references/report-module-implementation-blueprint.md`
- DB/API spec: `references/report-db-api-spec.md`
- Intent catalog: `references/report-intent-catalog.md`
- Acceptance gates: `references/report-acceptance-checklist.md`
- Security controls: `references/report-security-compliance.md`
- Delivery template: `assets/report-design-spec-template.md`
- P1 delivery status: `references/report-p1-delivery-status.md`
