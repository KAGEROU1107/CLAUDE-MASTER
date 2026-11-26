# V3 release workplan
Source: existing public CLAUDE-MASTER main V2 bootstrap, protocol, shell scripts, README. Preserve existing V2 source and functionality. This package is additive, a source candidate, not a release.

| ID | Deliverable | Gate | Current status |
|---|---|---|---|
| WP00 | Source audit | V2 contradictions and privacy risks identified | STATIC_REVIEW |
| WP01 | Bootstrap & governance | Universal, Advanced, bounded execution | DRAFTED |
| WP02 | Protocol & templates | Public kit/private data isolation | DRAFTED |
| WP03 | 12 skill procedures | Clear triggers, input/output, acceptance | DRAFTED |
| WP04 | Local helper runtime | Deterministic tests, no network | LOCAL_TESTED |
| WP05 | Installer/organizer hardening | preview, symlink/path, partial failure, rollback, idempotency, migration | OPEN |
| WP06 | Live native integrations | installed Claude version, statusline/hook payloads, actual /clear /baton resume | OPEN |
| WP07 | Adaptive engine validation | research recovery, privacy, license, memory and regression tests | OPEN |
| WP08 | User onboarding and benchmarks | fresh beginner, V2 migration, fixed-task before/after | OPEN |
| WP09 | Release review | exact diff, test evidence, owner license choice and approval | OPEN |

Next: stage candidate on a development branch after explicit push approval, preserve V2 and reconcile naming/install paths; harden installer before claiming a release. No license automatically selected. Keep the original README until migration and live gates pass.

## Continuation slice
| ID | Deliverable | Status |
|---|---|---|
| R01 | Generic optional persona spec, examples, skill and helper | LOCAL_TESTED |
| R02 | Herdr quickstart and official license verification | DOCUMENTED; LIVE_NOT_RUN |
| R03 | High-end model and high effort gate | LOCAL_TESTED; LIVE_NOT_RUN |
| R04 | V2 pacing tag/guide and independent meter gates | LOCAL_TESTED |
| R05 | Proposed MIT text | OWNER_APPROVAL_REQUIRED |
| R06 | README and private-reference fingerprints | DRAFTED; disclosure approval required |
| R07 | Candidate scan, exact target diff, archive scan and public push | CANDIDATE_SCAN_ONLY; HOLD |
| R08 | Isolated unittest discovery | LOCAL_TESTED |

| R09 | Generic installer and offline release scanner | LOCAL_TESTED; archived scripts and live integration remain open |
