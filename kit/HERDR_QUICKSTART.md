# Optional Herdr terminal workspace (beginner guide)

Herdr keeps multiple terminals organized. A workspace is a project; a pane is a terminal within it. It can display an agent's status and preserve live processes while you disconnect from the terminal UI. It is optional: ordinary Claude Code and BATON work without Herdr. Use one Claude session first. Do not launch additional paid agents just to fill panes.

## 1. Choose the correct product

This guide targets the Herdr terminal multiplexer from [official upstream](https://github.com/herdrdev/herdr), not the separate desktop app or a private workplace/chat extension. The upstream terminal project's LICENSE is Apache-2.0 (checked against the official repository). Each extension or different product has its own license; verify exact release and provenance before integrating.

## 2. Install only after approval

Read the [official installation guide](https://herdr.dev/tui/docs/install/) and [release downloads](https://github.com/herdrdev/herdr/releases). Claude should first inspect your OS, architecture, existing install, supported version and official checksums/signatures if published. Use a supported package manager if already installed, e.g. on a system with Homebrew, after user approval:

```sh
brew install herdr
```

For Windows choose the matching release archive and keep its complete extracted directory together; for Linux/macOS choose the correct binary and follow official instructions. Do not blindly pipe downloaded installers to a shell, disable endpoint protection or bypass execution policy. If the official install requires privileges or new dependencies, explain and ask first. If verification is unavailable, report it; offer plain Claude Code as a fallback. No installation is attempted by this kit.

## 3. First session

Open a terminal in your approved project directory. Verify `herdr --version` and `claude --version` if supported. Start:

```sh
herdr
```

Inside a pane start Claude Code:

```sh
claude
```

Follow START_HERE.md. Use the mouse menu to split a pane for ordinary shell tests or a terminal editor. Default key bindings from upstream (your configuration may override): press Ctrl+B, release, then V for a right split; Ctrl+B then C for a new tab; Ctrl+B then Q detaches. Run `herdr` again from the terminal to reattach. Confirm actual supported controls using the active version/help. Herdr's sidebar status is a convenience, not a proof of task completion. Use actual tests and WORKPHASE receipts.

## 4. Persistence and quota

Detaching normally leaves the existing Herdr server and its processes running; stopping the server kills pane processes, and restarting restores layout rather than arbitrary live processes. Supported agent session restore depends on integration version and native resume identity. Save and verify BATON before stopping, rebooting or clearing context. Reconcile actual project state after reconnecting. A terminal running in another pane does not provide a new Claude quota or context reset; stop when the real provider allowance is exhausted. Do not send additional agent work while paused or claim unattended work unless a verified runtime and explicit scope permit it.

## 5. Optional multi-pane workflow (not default)

One primary Claude pane owns the approved task and state. Use a separate shell for tests/read-only inspection. Only if a real need and permission exist, use an additional verified worker in an isolated worktree with one task ID, bounded inputs, allowed paths, measured resource headroom, acceptance criteria, expiry and a return receipt. Never have two workers edit the same branch/files concurrently. Missing worker quota or identity blocks autonomous dispatch; a reviewer must be actually separate if independent review is required. Terminal presence is not availability or approval. No private chat bridge, mods, worker scheduler, socket automation, token sharing or external transfer is bundled. If you want those later, request a separate design and security review. Keep pane history/session files private; do not upload them with the kit.

## 6. Recovery

If the command isn't found, recheck PATH and install status. If the agent is not detected, it can still run as a terminal process; inspect upstream supported-agent docs before enabling integrations. If panes are lost, restore the project using BATON and native Claude resume if verified, not a guessed transcript. Do not stop a server just to test recovery while work is running. Report actual test evidence; no live Herdr session was executed to produce this guide.

Official references checked 2026-11-27: [quick start](https://herdr.dev/tui/docs/quick-start/), [installation](https://herdr.dev/tui/docs/install/), [persistence](https://herdr.dev/tui/docs/session-state/), [upstream license](https://github.com/herdrdev/herdr/blob/master/LICENSE). Versioned source documentation inspected: upstream 0.9.5 quick-start, install and session-state pages. These are documentation checks, not installed-version certification.
