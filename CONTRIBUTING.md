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

## Review

The maintainer reviews every PR. Changes to the core rules (`kit/core/`), the installer, the release scanner, personas' authority model or CI need extra scrutiny and may take longer.

By contributing you agree that your contribution is licensed under the repository's [MIT License](LICENSE).
