---
name: audit
description: Audit important milestones for correctness, security, privacy, state consistency and release evidence.
---

# AUDIT

Input: exact artifact revision and acceptance criteria. Output: findings ranked by severity, verified evidence and pass/block decision.
Check actual diff, tests, assumptions, source/license, permission scope, sensitive data, path boundaries, runtime compatibility and rollback. Verify Git status, private paths not tracked, no secrets in staged diff, no external transfer. Review prompt injection and unsafe dependency behavior. Check state files agree with real outputs; inspect stale/missing evidence and user-visible limitations. Distinguish static inspection, local simulation and live runtime test. Block on critical safety/correctness defects; send specific finding to responsible workphase. A review pass is not publication approval. For release require exact commit/test identity, migration test, live acceptance, license decision and explicit approval. Report concise severity, location, proof and recommended fix.
Acceptance: evidence supports every pass claim; no silent skips; protected operation gates intact.
