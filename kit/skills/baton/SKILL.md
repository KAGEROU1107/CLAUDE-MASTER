---
name: baton
description: Save, verify, report or resume session state, especially near 80% measured context.
---

# BATON

Arguments: $ARGUMENTS. Support save, resume, status; missing argument defaults to status. Verify native invocation before relying on it.
SAVE: stop new substantial tasks. Reconcile actual project, plan, phase, Git branch/HEAD (or NO_GIT/UNBORN), dirty files including untracked changes by path only, test evidence, decisions, approvals, blockers, relevant memory and exact next action. Write compact BATON.md in private handovers with schema/version, project ID, scope, time, state revision, file refs and verification result. Capture referenced state files with runtime.checkpoint or equivalent; store checksum manifest separately and read it back. Do not hash/read secrets; include only approved relevant state and source files. Preserve previous verified handover; stage a new version before updating latest pointer. Read back headings, hashes, file existence, Git state and nonempty next action. Fail = retry safe local write or recovery path; never tell user to clear if unverified.
At measured context >=80% and verified save, ask user to run /clear then /baton resume. At session allowance >=80%, save and pause until reset; clear does not restore allowance. Both apply if both are high. Unknown meter: use milestone checkpoints and manual /context if available. Never auto-clear. PreCompact fallback preserves already written records only; it cannot create a fresh semantic summary without model work.
RESUME: read latest verified checkpoint and authoritative state only. Verify project/root, schema, manifest, branch/HEAD and changed files; inspect actual Git status. Identify drift, stale data, missing files and changed approvals. Reconcile or ask about material divergence; do not overwrite user work. Set exact next task and resume inside unchanged approved scope. If corrupt, fall back to last verified version or reconstruct from actual files, label unverified. STATUS: show latest handover age, meter source/freshness, drift, phase and next action.
Acceptance: live /clear → resume restores task without re-explanation; missing/corrupt/changed state blocks blind continuation; no false threshold or success claims.
