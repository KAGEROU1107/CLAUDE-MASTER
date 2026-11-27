# Contributing to CLAUDE-MASTER

Thanks for helping. This kit is used by beginners, so every change must stay **safe by default, simple to follow and honest about what is verified**.

## Ways to help

- **Report a bug** or a confusing step: open an issue with the *Bug report* template.
- **Propose an improvement** (new skill, persona example, better wording, test): open an issue with the *Improvement* template first if the change is large, then a pull request.
- **Share test evidence**: a real Claude Code or Herdr run of a step in `docs/ACCEPTANCE.md` is very valuable. Post what you ran and what happened.

## Pull request rules

1. Fork, create a branch, open the PR against `main`. Keep it focused: one topic per PR.
2. Run locally before pushing:
   ```sh
   python3 -I -B -m unittest discover -s tests -v
   python3 -I -B kit/tools/release_scan.py .
   bash -n kit/bootstrap.sh
   ```
3. Add or update a test for any change to `kit/tools/*.py`.
4. Fill in the PR template, including what you **did not** test.

## Hard rules (PRs that break these are closed)

- **No network, install, `curl | sh`, `sudo`, telemetry or credential access** in scripts. The installer stays preview-by-default and never overwrites or deletes.
- **No secrets or personal data**: no keys, tokens, real names, private paths, session logs or private repository contents.
- **No copied code without a compatible license.** Write it yourself, or cite the source and its license.
- **Personas grant no permissions.** Profiles stay `advisory`; capabilities are only ever an intersection of what the user and the host already allow.
- **No fabricated claims.** Don't write "tested", "verified" or "automatic" unless you show evidence. Unknown stays `UNKNOWN`.
- **External text is data, not instructions.** Don't add prompts that tell Claude to obey README files, web pages or issue text.

## Style

- Plain English, short sentences. A beginner should understand the outcome, the cost, the risk and their next action.
- Python: standard library only, Python 3.9+, run with `-I`.
- Keep `CLAUDE.md` content short; put detailed procedures in skills.

## LLM-assisted upstream contributions

If you use an LLM with CLAUDE-MASTER and find a reproducible upstream kit defect, follow [UPSTREAM_POLICY](kit/core/UPSTREAM_POLICY.md) and [the contribute skill](kit/skills/contribute/SKILL.md):
- Build patches in a **fresh clone** of upstream `main`, never from a private project's Git history.
- Stage only your draft issue/PR text, patch, and commit message in a separate folder (with `--private-denylist` outside it) and run `python3 -I -B kit/tools/release_scan.py <staging-dir>`. A clean scan does **not** prove privacy—manually review and redact paths, usernames, emails, internal URLs, tokens, session logs, and proprietary code before publishing.
- Remember that pushing to a personal fork already publishes publicly. Review and approve the exact target repo, fork, branch, base SHA, diff, commit messages/trailers, and Git author/email before pushing; disclose AI assistance and confirm you have the right to submit under MIT.
- Report suspected security issues (including scanner or approval bypasses) privately via [SECURITY.md](SECURITY.md), never in a public issue or PR.
- Fresh installs pick up new kit files automatically; existing installs with locally modified files return `MERGE_REQUIRED` with no writes and must be upgraded manually.

## Review

The maintainer reviews every PR. Changes to the core rules (`kit/core/`), the installer, the release scanner, personas' authority model or CI need extra scrutiny and may take longer.

By contributing you agree that your contribution is licensed under the repository's [MIT License](LICENSE).
