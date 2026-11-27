# Release acceptance matrix (unexecuted cases remain open)
| ID | Scenario | Required proof |
|---|---|---|
| A01 | Fresh install/preview/reapply | no writes on preview; existing files preserved; exact readback |
| A02 | V2 migration | non-destructive mapping and personal identity removed from active defaults |
| A03 | Existing custom settings | no blind overwrite; exact merge diff and explicit approval |
| A04 | Root symlink/escape / nested symlink | rejected; no external writes |
| A05 | Partial disk/permission failure | nonzero status; incomplete operation not reported as success; recovery journal |
| A06 | Git absent/unborn/dirty | truthful states and preservation; no blind staging |
| A07 | Public repo/private state | ignored before writes, already-tracked paths flagged, staged diff reviewed |
| A08 | Two distinct failures / repeated identical error | invoke discovery; no repeated unchanged retries |
| A09 | Missing docs/network | bounded fallback, clear blocker |
| A10 | Malicious README / unknown license | ignored as instructions; no execution or unlicensed code copy |
| A11 | Adapt external solution | pinned provenance, license, sandbox test, rollback |
| A12 | Preference correction/conflict | scope-aware supersession; no inferred sensitive traits |
| A13 | Skill regression | sandbox rejection or rollback; no automatic privilege expansion |
| A14 | Missing, stale, other-session, malformed meter | UNAVAILABLE, no fabricated percentage |
| A15 | Context thresholds 60/70/80 | checkpoint, prepare, verified BATON then request clear |
| A16 | Session allowance high / context high | checkpoint and pause; no quota reset claim |
| A17 | Save interrupted or invalid checksum | do not ask clear; prior verified handover survives |
| A18 | Real /clear and /baton resume | actual new context, verified prior task, no user re-explanation |
| A19 | Drift / missing files / dirty branch | reconciliation before work |
| A20 | Early compaction | actual hook behavior; fallback only preserves existing state |
| A21 | Hook disabled / statusline not supported | manual mode documented and tested |
| A22 | Beginner first project | observable end result; one understandable next action |
| A23 | Usage optimization | same three tasks, quality maintained; measured deltas or unknown |
| A24 | Git push / license decision | exact authorization, correct branch and visibility; release only after review |

Local unit tests cover portions of A04, A08, A14–A17 and A19. They do not prove agent behavior, filesystem race resistance, installer safety, external research quality or live runtime integration. All other cases require actual execution evidence.

| ID | Scenario | Required proof |
|---|---|---|
| A25 | Generic persona profiles | Strict shape/ID/authority validation; no permission expansion; unapproved skill rejected |
| A26 | Persona lifecycle and restart | Verified profile/skill revisions, task-bound activation, stop and resume; no invented independent reviewer |
| A27 | High-end/high-effort gate | Verified suitable model and effort; known fit or HOLD; no automatic spending/settings changes |
| A28 | V2 pacing merge | Weekly burn check with actual reset window; task tags, unknown fit and simultaneous context/quota gates |
| A29 | Herdr workflow | Actual install/version, pane, detach/reattach and BATON verification; quota remains independent |
| A30 | Release privacy | Scan exact staged tree including legacy, history exposure and provenance table decision; no private identifiers, secrets or runtime data |
| A31 | Upstream contribution protocol | `UPSTREAM_POLICY.md` and `contribute/SKILL.md` install on fresh project; existing modified install returns `MERGE_REQUIRED`; live LLM suggestion/draft/approval behavior remains manual/untested |
| A32 | AGY-MASTER Antigravity adapter (EXPERIMENTAL) | `--target antigravity` installs `.agents/claude-master/kit/`, `.agents/skills/`, `GEMINI.md` (no `/clear`, `< 24 KB`), preserves `AGENTS.md`, blocks alias collisions and mismatched flags, supports dual install; live Antigravity rules load, skill discovery, and save → new chat → resume remain manual/untested |

A25 and A27–A28 have deterministic helper test evidence only. A26, A29, live A31 model behavior, and live A32 Antigravity runtime behavior remain live/manual. A30 candidate scan is not a scan of the actual target branch.

Fresh-install preview, reapply, differing existing instructions, existing ignore conflict, symlink escape and shell entrypoint now have local temporary-directory tests. This does not verify Git tracking, every partial-failure path, live skill discovery, existing legacy organizer behavior, or migration.
