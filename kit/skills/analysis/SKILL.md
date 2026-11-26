---
name: analysis
description: Investigate complex or uncertain problems; separate evidence, hypotheses and alternatives.
---

# ANALYSIS

Input: task ID, expected versus actual state. Output: ANALYSIS.md with source-grounded decision.
1. Inspect actual files, errors, versions and relevant prior knowledge. Use scoped searches and small reads. Identify facts, assumptions, missing information and constraints separately.
2. Establish minimal reproduction and relevant baseline. Generate distinct hypotheses, rank by evidence and choose cheapest discriminating test. Do not spend repeated calls on an unchanged failing strategy.
3. If information is missing, search official docs/upstream issues via discovery with sanitized queries. Compare plausible alternatives by feasibility, quality, cost, complexity and security. Label source claims versus local verification.
4. Document decision, rejected alternatives, risks, unresolved uncertainty and next test. Use exact paths/version links when available; never manufacture citations.
5. Update affected workplan; if blocked use recovery, otherwise pass selected approach to workphase.
Acceptance: another session can reconstruct why the approach was chosen without a full transcript; each significant claim has evidence or UNVERIFIED label.
