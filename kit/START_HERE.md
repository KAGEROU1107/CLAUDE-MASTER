# Start here — beginner onboarding
This V3 candidate is a review package, not a released installer. Preserve your current project. Download or clone the public reference kit into a separate folder. Open Claude Code in the project you actually want to work on. Give Claude the path to this kit and paste the following:

> Read kit/CLAUDE_MASTER_BOOTSTRAP_v3.md and kit/PROTOCOL.md from the provided kit. I am a beginner; do the technical work safely and explain decisions simply. Use Advanced Evolution Mode. Audit first, grill me, propose a workplan, then implement the approved foundation. When blocked, proactively research public GitHub and official sources, adapt verified solutions, and improve my authorized local memory, Markdown and workflows. At 80% measured context, save and verify BATON, ask me to /clear, then resume with /baton resume. Preserve existing files; protect privacy; do not install, spend, push or change protected settings without approval. Begin with read-only WP00.

Do not run a random install command. Claude should inspect versions, permissions, files and the current workspace first. If the kit is not local, ask Claude to retrieve the public files read-only with the available GitHub or web tool. Confirm the correct root and scope before any writes. Actual live setup is not verified by this package.

For difficult architecture, security or recovery tasks Claude will check the available model and high thinking/effort setting and ask before spending more. Routine tasks stay inexpensive. Optional terminal organization: HERDR_QUICKSTART.md. Optional role profiles: personas/README.md. Neither is required to begin.

Optional approved local installer (Bash + Python 3.9 or newer): `bash kit/bootstrap.sh --root <project-folder>` previews; add `--apply` only after review. Existing differing files stop the installer for review; it never writes private state. Before saving private data, verify ignored paths and no already tracked private data using Git. For an existing root `CLAUDE.md`, inspect the kit rules and integrate the relevant instructions manually. Then preview with `--preserve-claude-md`; use the same flag with `--apply` to keep that file byte-for-byte. The result lists it under `preserved`; this is not verification that its instructions are complete. Other conflicting kit files still require exact reconciliation; this flag does not skip them.

Windows without Bash can preview from the reference checkout with:

```powershell
py -3 -I -B kit/tools/install_entry.py --root "C:\path\to\project"
```

Add `--apply` after reviewing the preview, and `--preserve-claude-md` only after reviewing an existing root instruction file. Python must be 3.9 or newer. Windows behavior remains untested.
