# AGY-MASTER — Antigravity Adapter (EXPERIMENTAL)

> [!NOTE]
> **Status: EXPERIMENTAL (CLI smoke-tested).** Deterministic installer/unit tests pass, and a live Antigravity CLI smoke test (`gemini-3.8-flash-low` on Windows) verified auto-loaded `GEMINI.md`, `14/14` `.agents/skills/` discovery, `.cm-private/` gitignore, and manual BATON save → fresh session `"baton resume"`. Antigravity IDE and Linux/macOS live runs remain unverified.

This adapter lets **Google Antigravity (AGY)** use the single-source `CLAUDE-MASTER` V3 kit without forking or duplicating skills, policies, or tools.

## 1. Host Path & File Mapping

| Claude Code (default) | Antigravity (`--target antigravity`) | Notes |
|---|---|---|
| `CLAUDE.md` | `GEMINI.md` | Root instructions (`< 24 KB`, no `/clear` rule). Never edits `AGENTS.md`. |
| `.claude/claude-master/kit/` | `.agents/claude-master/kit/` | Read-only kit reference copy (includes `adapters/agy-master/`). |
| `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` | Single shared copy from `kit/skills/`; progressive disclosure. |
| `.claude/claude-master/kit/tools/release_scan.py` | `.agents/claude-master/kit/tools/release_scan.py` | Used for `UPSTREAM_POLICY.md` staging-folder scans. |
| `.cm-private/` | `.cm-private/` | Shared private state (gitignored). Dual-host projects share one `.cm-private/`. |

- **`.agents/` stays committable:** Do not add `.agents/` to `.gitignore`; keep `.cm-private/` and secret patterns ignored.
- **Always-on rule coexistence:** Antigravity loads **both** `GEMINI.md` and `AGENTS.md` (plus `.agents/rules/*.md`). Preview lists any existing `AGENTS.md` and `.agents/rules/*.md` for manual conflict review; the installer never modifies them.
- **Skill precedence & collisions:** Workspace skills in `.agents/skills/` override same-named global skills under `~/.gemini/config/`. If a same-named skill already exists under `.agent/`, `_agents/`, or `_agent/`, the installer stops with `MERGE_REQUIRED` and writes nothing.

## 2. Honest Capability & Parity Matrix

| Capability | Antigravity Status | Operating Rule |
|---|---|---|
| Workspace rules (`GEMINI.md`, `AGENTS.md`, `.agents/rules/*.md`) | **CLI smoke-tested (Windows)** | Keep `GEMINI.md` compact (`< 24 KB`); review alongside `AGENTS.md`. IDE and Linux/macOS remain unverified. |
| Workspace skills (`.agents/skills/*/SKILL.md`) | **CLI smoke-tested (Windows, 14/14)** | Progressive disclosure (`name` + `description` only until activated). IDE and Linux/macOS remain unverified. |
| Lifecycle hooks (`.agents/hooks.json`) | **Not integrated** | Antigravity supports hooks, but this kit enables zero hooks automatically. |
| Claude slash commands (`/clear`, `/baton resume`, `/model`, `/effort`, `/context`, `/usage`) | **`UNVERIFIED` / Host-specific** | Do not assume these commands exist in Antigravity. |
| Context reset & BATON handover | **Manual / milestone mode** | Save + verify BATON (record `host: antigravity`), open a **new conversation**, then ask for `"baton resume"`. Do **not** equate `/compact` with a clean context reset. |
| Resource meters & `pacing.py` | **Manual / strict** | Keep `pacing.py` strict (`METER_GATE` on missing meters for critical tasks). Accept only user-reported numbers; map Antigravity UI model/effort labels to `high_end`/`high` only when user-confirmed, else `MODEL_GATE`. |
| Global config (`~/.gemini/config/`) | **Never touched** | Installer writes inside the approved project root only. |

## 3. Mapping Shared Kit Documents

Shared files (`kit/skills/*/SKILL.md`, `kit/core/PACING.md`, `kit/core/UPSTREAM_POLICY.md`, `kit/PROTOCOL.md`, `kit/CLAUDE_MASTER_BOOTSTRAP_v3.md`) are kept as one authoritative copy. When running under Antigravity:
- Read `.claude/` paths as `.agents/` (e.g., `.agents/claude-master/kit/` and `.agents/skills/`).
- Read `CLAUDE.md` as `GEMINI.md`.
- Read `/clear` + `/baton resume` as: verify BATON (with `host: antigravity`), open a **new conversation**, and prompt `"baton resume"`.
- Read `/model` + `/effort` as: ask the user to verify the active model and effort in the Antigravity UI.
