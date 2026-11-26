---
name: workphase
description: Execute a bounded authorized task, validate results, reconcile state and checkpoint.
---

# WORKPHASE

Input: approved plan, READY task ID. Output: task artifacts, evidence, reconciled state.
1. Confirm root, current branch and existing dirty changes. Read scope, requirements, test and rollback. Check context/allowance and approval gates; use baton if required.
2. Change only relevant files. For behavior changes reproduce or write a failing test, implement minimal fix, rerun focused and regression tests. Never weaken a test merely to pass. For noncode deliverables inspect actual output against acceptance criteria.
3. Record relevant commands, exit status and evidence without secrets. If failure persists, invoke recovery; do not mark complete on creation alone. Ask for approval only at protected operations or changed scope.
4. Read back files and actual state; update task status and evidence; reconcile WORKPLAN, WORKPHASE, STATE and decisions. Do not mark VERIFIED until acceptance evidence exists.
5. Extract a relevant lesson, checkpoint next action and report plainly. If interrupted mark IN_PROGRESS or BLOCKED, not complete.
Acceptance: targeted output exists, test evidence supports result, unrelated changes preserved, next task identifiable, no unauthorized push.
