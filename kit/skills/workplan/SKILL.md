---
name: workplan
description: Plan substantial projects with dependencies, scope, cost and evidence gates. Use for new projects or changed scope.
---

# WORKPLAN

Input: request, current project and analysis. Output: revised WORKPLAN.md, stable task IDs and next bounded action.
1. Read existing state and plan; classify BUILD, RESUME, REVIEW, MIGRATE, RETIRE. Identify user outcome, non-goals and tangible acceptance evidence.
2. Split work into deliverables, dependencies, prerequisites and stop gates. For each task record ID, input, output, risk, approval, resource estimate (S/M/L or unknown), evidence and rollback. Keep task IDs stable across replans. Use only one authoritative plan.
3. Mark tasks READY only if dependencies and approvals are satisfied; choose highest-value ready task. Parallelize only independent work if supported and authorized; avoid extra agents.
4. Explain the plan to a beginner in terms of outcomes, not internal file complexity. Request scope approval if needed. Do not stop for redundant confirmations within approved work.
5. On new evidence revise affected tasks; preserve completed receipts and identify superseded assumptions. Hand off to workphase with exact task ID and exit test.
Acceptance: no circular dependency, every task has observable completion criteria, no new protected authority inferred, next action executable or named blocker.

Every substantial task includes the pacing tag from core/PACING.md (model, effort, estimated/measured cost, FITS_SESSION, FITS_WEEK, WHEN, evidence). Critical work cannot become READY without verified high-end suitable model/high effort and quota headroom. UNKNOWN is not a pass.
