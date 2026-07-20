# .hermes/ — Hermes Agent declarative config (vault-tracked)

This folder holds the **declarative** configuration for [Hermes Agent](https://github.com/NousResearch/Hermes-Agent) so it can be version-controlled alongside this vault.

What's tracked here:

- `config.yaml` — vault-specific deltas from the upstream Hermes defaults (MCP servers, plugins, approval gates). Secrets stay out of this file.
- `SOUL.md` — Hermes' persona / system prompt for this vault.
- `skills/vault-capture/` — the **vault-specific capture skills** Hermes runs (Calendar / Tasks / Slack / GitHub / Clippings, plus optional Genspark). Each skill has its own `SKILL.md` describing trigger conditions and the Inbox landing path.

What's NOT tracked (see [`.gitignore`](../.gitignore)):

- Runtime state (`state.db`, `cron/`, `sessions/`, `gateway_state.json`, …)
- Auth tokens & secrets (`.env`, `google_token.json`, `gws_key.json`, `mcp-tokens/`, …)
- Vendored upstream skill library (`skills/*` other than `skills/vault-capture/`)
- Caches & logs

## Setup (quick)

> **Beginner-friendly walkthroughs** (per connection, with verification steps and troubleshooting) live in [`Meta/connections/`](../Meta/connections/README.md) — start there if this is your first setup. The staged onboarding path is [`GETTING-STARTED.md`](../GETTING-STARTED.md). The steps below are the condensed version.

1. Install Hermes: see [the upstream repo](https://github.com/NousResearch/Hermes-Agent) for the latest install instructions.
2. From the vault root, use the tracked `.hermes/` directory as the preferred per-vault profile, then initialize Hermes there according to the upstream instructions:
   ```bash
   export HERMES_HOME="$PWD/.hermes"
   ```
   This keeps `config.yaml` and `skills/vault-capture/` inside the active profile. Runtime state, upstream skills, and secrets created there remain gitignored.
   If you must keep an existing global profile, merge `config.yaml` **and** mirror the complete `skills/vault-capture/` directory into that `${HERMES_HOME}`. Copying the config alone leaves these capture skills undiscoverable.
3. Keep the same `HERMES_HOME` exported when running Hermes, and authenticate only the integrations you'll use:
   - Slack: `hermes slack add-workspace`
   - Google Calendar: configure a private ICS URL; use `gws` only for an additional account that cannot expose ICS.
   - Google Tasks: authorize the tracked shared-OAuth helper (see [`skills/vault-capture/google-auth/`](skills/vault-capture/google-auth/SKILL.md)).
   - Notion MCP: OAuth via the Notion MCP endpoint.
   - GitHub: export `GITHUB_PERSONAL_ACCESS_TOKEN` so the GitHub MCP can use it.
4. Verify the active profile and pull path:
   ```bash
   test -f "$HERMES_HOME/skills/vault-capture/inbox-daily-capture/SKILL.md"
   hermes chat -q "list my Google Tasks"
   ```
5. Try a capture skill from the vault root: `hermes chat -q "Load inbox-daily-capture and run it for today" -s inbox-daily-capture -Q --source core-agent` should create `Inbox/{today}/daily/daily.md`.

Capture is on-demand. Do not register new cron jobs from this template; existing
legacy jobs may remain temporarily while migrating to the Daily job list.

Google helper scripts must use the Hermes runtime Python because they reuse its
installed Google packages and shared token. Set `HERMES_PYTHON` to an absolute
interpreter path when `${HERMES_HOME}/hermes-agent/venv/{bin, Scripts}` is not
the install location. Other repository Python commands use `uv`.

## Why Hermes owns the external connections

See [`.codex/rules/agent-boundaries.md`](../.codex/rules/agent-boundaries.md) §6. Every outbound OAuth / PAT / MCP credential is held by Hermes to avoid duplication and token-refresh split brain. The core reaches external systems through two paths:

- **push** — Hermes writes raw capture to `Inbox/{date}/{source}/`. The core curates from there.
- **pull** — The core runs `hermes chat -q "..."` for live lookups (the [`hermes-query`](../.codex/skills/hermes-query/SKILL.md) skill).

## Optional

If you don't want Hermes at all, you can:

- Remove this folder.
- Disable Hermes-backed connections in `.codex/connections.yaml` and remove `hermes-query` if it is not needed.
- Keep the `Inbox/` pipeline: Web Clipper, AI Exporter, or another capture extension writes raw files, and `inbox-aggregate` still moves their summaries into Daily.

The core agent (Codex) still works without Hermes — you just lose the automated Slack / GCal / GTasks / GitHub ingestion.
