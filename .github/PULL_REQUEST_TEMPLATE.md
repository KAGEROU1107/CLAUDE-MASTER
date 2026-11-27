## What does this change?

<!-- One or two sentences. Link the issue if there is one: Fixes #123 -->

## Why?

## How was it tested?

- [ ] `python3 -I -B -m unittest discover -s tests -v` passes
- [ ] `python3 -I -B kit/tools/release_scan.py .` reports `NO_PATTERN_HITS`
- [ ] `bash -n kit/bootstrap.sh` passes (if touched)
- [ ] Live Claude Code / Herdr check (describe below, or write "not tested")

<!-- Paste the commands you ran and what happened. -->

## Not tested / known limits

## Safety checklist

- [ ] No network access, installs, `sudo`, telemetry or credential reads added to scripts
- [ ] No secrets, personal data, private paths or private repository content (manually reviewed; not relying on `release_scan.py` alone)
- [ ] Any copied code has a compatible license, cited here
- [ ] I have the right to submit this change under MIT (including any employer or third-party code)
- [ ] AI-assisted drafting disclosed (if used) and a human reviewed the full sanitized diff, commit messages, and trailers before pushing
- [ ] Personas still grant no extra permissions
- [ ] No "verified/automatic" claim without evidence
