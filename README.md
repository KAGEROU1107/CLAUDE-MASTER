# CLAUDE-MASTER

Bootstrap kit that lets Claude Code set up a persistent, modular, low-usage AI workspace by itself.
Authority: KAGEROU. Mode: audit first, ask before anything risky.

## Contents
```
README.md
kit/
  CLAUDE_MASTER_BOOTSTRAP_v2.md   the prompt Claude Code follows (phases P0-P7, rules, pacing)
  PROTOCOL.md                     where every file lives + how Claude must behave
  bootstrap.sh                    creates the workspace skeleton (dry-run by default)
  organizer.sh                    sorts inbox/ into the workspace (preview by default)
```

## Quick start
1. Copy the kit into your project folder:
   ```bash
   git clone https://github.com/KAGEROU1107/CLAUDE-MASTER.git /tmp/claude-master
   cp -r /tmp/claude-master/kit ./kit
   ```
2. Start Claude Code in that folder and enter:
   ```
   Read kit/PROTOCOL.md and @kit/CLAUDE_MASTER_BOOTSTRAP_v2.md. Run P0 only.
   ```
3. Claude reads the kit, audits your environment, then stops and waits for `GO` before each next phase.

Manual run (optional):
```bash
bash kit/bootstrap.sh                           # preview, changes nothing
bash kit/bootstrap.sh --apply --root <folder>   # create the skeleton
bash tools/organizer.sh                         # preview inbox sorting
bash tools/organizer.sh --apply                 # move files (writes recovery/undo-<ts>.sh)
```

## Phases
| Phase | Purpose |
|---|---|
| P0 | Audit environment, usage meter, backup (read-only) |
| P1 | Grill: max 5 questions per round |
| P2 | Architecture proposal + pacing plan |
| P3 | Foundation: run bootstrap.sh |
| P4 | BATON session handover skill |
| P5 | Measure before/after |
| P6 | Open-source research (only on "GO RESEARCH") |
| P7 | Skills + learning loop |

Every phase ends with REPORT, STOP, wait for GO.

## Safety design
- bootstrap.sh and organizer.sh: dry-run by default, never delete, never overwrite, no network, no installs.
- Secret-like files (.env, keys, tokens) are skipped and never read.
- Every organizer run writes an undo script and a log line.
- Created only with KAGEROU approval: settings.json, hooks, statusLine, BATON skill, first commit, push.
- Pacing: every phase carries model, thinking level, session % and weekly % checks. Unknown meter = UNAVAILABLE, never estimated.

## Verified
- Shell syntax check of both scripts: PASS.
- Throwaway-folder test: dry-run changes nothing, re-apply is idempotent, organizer sorts 7 and skips 5 (secret-like, symlink, directory, unknown type), collisions never overwrite, undo restores inbox, secret scan flags a planted fake key without printing it.
- shellcheck: not run (UNVERIFIED).
- Not tested inside a live Claude Code session. Statusline usage fields and `/baton` argument handling depend on your installed version; P0 checks them.

## Status
Version: v2. No license set yet.
