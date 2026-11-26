---
name: recovery
description: Detect stalled work, avoid repeated failures and autonomously initiate targeted research.
---

# RECOVERY

Input: task ID, expected/actual, attempts and evidence. Output: revised recovery strategy or bounded blocker report.
Normalize symptom and attempted strategy. Distinct failed strategies >=2 or repeated identical failure or uncertainty/confusion can trigger discovery; research earlier for unknown versions or likely existing solution. Never require two failures to seek documentation. First inspect actual state, preserve work, classify environment/permission/dependency/version/logic/requirements/availability. Reproduce minimally. Record attempt fingerprint to prevent unchanged retries. Form different hypotheses and discriminating tests. Invoke discovery with sanitized context; prefer upstream issue for exact error. Adapt only with safety and license checks. Run isolated test then regression; if validated resume original workphase, record lesson. Default max two research cycles, 12 targeted calls each; stop sooner when budget/approval/context requires. At failure state report what was tried, what is known, what alternatives remain, one recommended next step. Do not invent progress or endlessly try variants.
Acceptance: no unchanged retry loop, no reliance on beginner to find repo, original task and constraints preserved.
