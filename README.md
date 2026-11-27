# CLAUDE-MASTER V3 — Advanced Evolution

A beginner-oriented Claude Code bootstrap kit with expert-level planning, research, verification, persistent memory and adaptive skill development. Advanced Evolution is the default within the user's approved scope. This is a **review candidate**, not a live-tested installer or released version.

> [!IMPORTANT]
> **Model notice.** Run this kit with a **high-end model at high (or higher) thinking/effort** — e.g. the strongest model your plan offers, checked with `/model` and `/effort`. Setup, architecture, persona design and audits are multi-step reasoning tasks; verify the selected model and effort against the task; this repository has no comparative model benchmark. After setup, routine work may drop to a smaller model (see *Quality and budget gate*). The kit never switches models or spends extra on its own.

## Start here

> [!TIP]
> **Using Google Antigravity (`AGY-MASTER`)?** See [AGY-MASTER Start Here](kit/adapters/agy-master/START_HERE.md) and install with `--target antigravity` (EXPERIMENTAL — live CLI smoke-tested on Windows; IDE and Linux/macOS live runs remain unverified).

1. Get the public kit into a separate folder; open Claude Code in your own project, not the reference repository. See [START_HERE](kit/START_HERE.md).
2. Paste: `Read kit/START_HERE.md, kit/CLAUDE_MASTER_BOOTSTRAP_v3.md and kit/PROTOCOL.md from the reference kit. I am a beginner. Start read-only WP00 and explain the next action.` Supply the actual kit location if different.
3. Approve the local workspace and budget after the audit. For optional generic installation, `bash kit/bootstrap.sh --root <project-folder>` previews; add `--apply` only after review. Existing conflicting files are preserved. After manually integrating the kit rules into your root `CLAUDE.md`, add `--preserve-claude-md` to keep that file; other kit-file conflicts still block installation. Claude will interview you, create a WORKPLAN, investigate with ANALYSIS, execute bounded WORKPHASE tasks and verify results.
4. When blocked, Claude researches public documentation and GitHub automatically within the approved budget; it adapts only verified, compatible, licensed solutions. It learns preferences and updates authorized local Markdown and knowledge. Protected instructions, installs, external transfers and publication remain approval-gated.
5. At 80% verified context, Claude saves and verifies BATON before asking you to use `/clear` and then `/baton resume`. Actual command and hook support must be verified. Session/weekly allowance is separate; clearing does not reset it.

## Quality and budget gate

Routine work uses the smallest adequate available model. Architecture, hard debugging, security review, high-risk migration, persona/authority design and release review require the strongest suitable authorized model and high-or-greater verified effort (or documented equivalent). Claude checks `/model` and `/effort` or supported controls, asks before any setting change or additional spend, and holds critical work when quality or budget cannot be verified. See [PACING](kit/core/PACING.md) for the mandatory task tag, headroom estimates and conservative fallback. No plan bypass, silent paid upgrade or fabricated meter.

## Optional enhancements

- [AGY-MASTER (Antigravity Adapter — EXPERIMENTAL, CLI smoke-tested)](kit/adapters/agy-master/START_HERE.md): thin single-source adapter (`--target antigravity`) installing `.agents/claude-master/kit/`, `.agents/skills/`, and `GEMINI.md` without duplicating skills or core rules. See [ADAPTER](kit/adapters/agy-master/ADAPTER.md); live Antigravity CLI smoke test passed on Windows (IDE and Linux/macOS live runs remain unverified).
- [Personas](kit/personas/README.md): four generic profiles, a persona skill and a local validator. They select task behavior and approved shared skills, not new powers or independent agents.
- [Herdr](kit/HERDR_QUICKSTART.md): optional terminal organization with detach/reattach; use plain Claude Code if it is enough. The official terminal upstream is Apache-2.0; no Herdr code or private mods are bundled. Live Herdr integration has not been tested.
- [Protocol](kit/PROTOCOL.md), [acceptance matrix](docs/ACCEPTANCE.md), [workplan](docs/WORKPLAN.md), [test report](docs/LOCAL_TEST_REPORT.txt).

## Provenance

Two private repositories were read **read-only** as design inspiration. Nothing from them — code, schema, names, profiles, paths or data — is included; the public designs here are written independently. They are recorded as **keyed fingerprints** (`HMAC-SHA256(key, lowercase "owner/repo")`). The key is held privately by the maintainer and is not in this repository, so the fingerprints cannot be reversed by guessing names. The maintainer can verify or update a row with:

```sh
printf '%s' 'owner/repo' | openssl dgst -sha256 -hmac "$PROVENANCE_KEY"
```

| Ref | Fingerprint (HMAC-SHA256) | Used for |
|---|---|---|
| R1 | `b06a123f37810e02978d2a58bddc78db37394b20a5c315228728f0b88faab709` | Abstract terminal-workspace and bounded-worker concepts (see `kit/HERDR_QUICKSTART.md`) |
| R2 | `6439bb11daeab93c93d3396ff095cf413a5b88685338d978d186700ea4890103` | Abstract persona schema, shared-skill binding and evidence concepts (see `kit/personas/`) |

## Tests and release

```sh
python3 -I -B -m unittest discover -s tests -v
```

Local deterministic tests and the V3 shell entrypoint smoke tests have been run. Verify actual Claude Code/Herdr runtime integration, real BATON clear/resume, exact branch diff, legacy migration, privacy and license before release. Keep generated user data out of public Git. The previous V2 kit remains available in Git history at commit `8b663cc`.

## Contributing

Improvements are welcome from anyone. Read [CONTRIBUTING](CONTRIBUTING.md), open an issue or a pull request against `main`. For LLM-assisted upstream findings, see [UPSTREAM_POLICY](kit/core/UPSTREAM_POLICY.md) and [the contribute skill](kit/skills/contribute/SKILL.md) (default `SUGGEST`, no automatic pushes). CI runs the tests and the leak scan on every PR; the maintainer reviews and merges (GitHub branch protection is not verified by this repository). Report security problems privately as described in [SECURITY](SECURITY.md).

## License

[MIT](LICENSE). Herdr is a separate project (Apache-2.0) and is not bundled.
