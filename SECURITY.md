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
