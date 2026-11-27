# AGY-MASTER — Start Here (Antigravity Adapter, EXPERIMENTAL)

> [!NOTE]
> **EXPERIMENTAL:** Deterministic installer and unit tests pass; live Antigravity runtime acceptance is still pending.

Use this adapter to run **CLAUDE-MASTER V3** inside **Google Antigravity (AGY)** while sharing one authoritative kit.

## 1. Prompt Antigravity (Read-Only First)

Download or clone the public `CLAUDE-MASTER` repository into a separate folder, open Antigravity in your own project, and paste:

> Read `kit/adapters/agy-master/ADAPTER.md`, `kit/CLAUDE_MASTER_BOOTSTRAP_v3.md`, and `kit/PROTOCOL.md` from the provided kit. I am using Antigravity (AGY-MASTER adapter). Start read-only WP00, inspect my project and any existing `AGENTS.md` or `GEMINI.md`, explain decisions simply, and do not write, install, push, or change settings without my approval.

## 2. Optional Preview-First Installer

Preview first (writes nothing, checks for `GEMINI.md` conflicts, alias skill collisions under `.agent/` / `_agents/` / `_agent/`, and lists existing `AGENTS.md` / `.agents/rules/*.md` for review):

**macOS / Linux / Git Bash:**
```sh
bash kit/bootstrap.sh --target antigravity --root /path/to/your/project
```

**Windows PowerShell:**
```powershell
py -3 -I -B kit/tools/install_entry.py --target antigravity --root "C:\path\to\your\project"
```

After reviewing the preview, add `--apply` to install `.agents/claude-master/kit/`, `.agents/skills/*/SKILL.md`, `GEMINI.md`, and `.gitignore` (`.cm-private/`).

If your project already has a custom `GEMINI.md`, integrate the kit rules manually first, then pass `--preserve-gemini-md` (both in preview and `--apply`) so your `GEMINI.md` is kept byte-for-byte.

## 3. Dual-Host Projects (Claude Code + Antigravity)

You can safely install both `--target claude` and `--target antigravity` in the same project in either order. Both hosts share `.cm-private/` (record `host: antigravity` or `host: claude` in BATON handovers).
