# Security policy

## Reporting a problem

Please **do not** open a public issue for a security problem (for example a way for the installer to write outside the chosen folder, a leak-scanner bypass, or a prompt that makes Claude skip an approval gate).

Use GitHub's private reporting instead: **Security tab → Report a vulnerability** on this repository. If that button is not available, open a public issue that only says "security contact requested", with no details, and the maintainer will reach out.

Include what you ran, what happened and what you expected. Never include real secrets in a report.

## Scope

In scope: `kit/tools/*.py`, `kit/bootstrap.sh`, the CI workflow, and instructions in `kit/` that could lead Claude to act without approval, leak private data or run untrusted code.

Out of scope: Claude Code, Herdr and other third-party tools themselves. Report those upstream.

## What this kit promises (and does not)

- The installer previews by default, writes only into the folder you name, never overwrites, and performs no network access.
- The release scanner is a best-effort pattern check. It is **not** proof that a tree or its Git history is free of secrets.
- Nothing here has been certified by a live end-to-end test; see `docs/ACCEPTANCE.md`.

## Threat Model & Operator Guidance

The kit is mostly instructions that a model reads. Instructions can guide behavior, but they cannot enforce a security boundary. You, your host CLI's permission settings and your isolation are the controls.

- **Untrusted content (indirect prompt injection).** Repository files, web pages, issues, pull requests and tool output may contain text written to steer the model. Treat it as data, never as instructions. Prompt rules alone will not reliably stop it: rely primarily on human review of proposed actions plus sandboxing.
- **Untrusted MCP servers and tool-description poisoning.** A connected server can put hostile instructions in its tool descriptions or results. Connect only servers you trust, grant each the least privilege it needs, disable unused ones, and review the connected list and their tools, including after updates.
- **Host CLI authorization drift and experimental status.** Permission modes, defaults, hooks and allowlists belong to the host CLI. They can change between versions or settings, and modes that auto-approve actions reduce your chance to review them. Check the effective permissions rather than assuming the kit's approval gates are enforced. This kit and its adapters are experimental: use a sandbox, VM or container when sensitive credentials are within reach or the repository is untrusted, and keep unneeded credentials out of that environment.
- **Review before running.** Manually read `kit/bootstrap.sh` and `kit/tools/*.py` before you execute them, and again after updating the kit. Preview mode and the scanners do not replace that review.
