# .hermes/ — Hermes Agent declarative config (vault-tracked)

This folder holds the **declarative** configuration for [Hermes Agent](https://github.com/NousResearch/Hermes-Agent) so it can be version-controlled alongside this vault.

What's tracked here:

- `config.yaml` — vault-specific deltas from the upstream Hermes defaults (MCP servers, plugins, approval gates). Secrets stay out of this file.
- `SOUL.md` — Hermes' persona / system prompt for this vault.
- `skills/vault-capture/` — the **vault-specific capture skills** Hermes runs (Calendar / Tasks / Slack / GitHub / Genspark / Clippings). Each skill has its own `SKILL.md` describing trigger conditions and the Inbox landing path.

What's NOT tracked (see [`.gitignore`](../.gitignore)):

- Runtime state (`state.db`, `cron/`, `sessions/`, `gateway_state.json`, …)
- Auth tokens & secrets (`.env`, `google_token.json`, `gws_key.json`, `mcp-tokens/`, …)
- Vendored upstream skill library (`skills/*` other than `skills/vault-capture/`)
- Caches & logs

## Setup (quick)

> **Beginner-friendly walkthroughs** (per connection, with verification steps and troubleshooting) live in [`docs/connections/`](../docs/connections/README.md) — start there if this is your first setup. The staged onboarding path is [`GETTING-STARTED.md`](../GETTING-STARTED.md). The steps below are the condensed version.

1. Install Hermes: see [the upstream repo](https://github.com/NousResearch/Hermes-Agent) for the latest install instructions.
2. Copy this `config.yaml` into your `${HERMES_HOME}` (default `~/.hermes/`) and merge with the defaults Hermes creates.
3. Authenticate the integrations you'll use:
   - Slack: `hermes slack add-workspace`
   - Google Workspace (Calendar / Tasks): set up the `gws` CLI (see [`skills/vault-capture/google-auth/`](skills/vault-capture/google-auth/SKILL.md)).
   - Notion MCP: OAuth via the Notion MCP endpoint.
   - GitHub: export `GITHUB_PERSONAL_ACCESS_TOKEN` so the GitHub MCP can use it.
4. Verify with a pull query:
   ```bash
   hermes chat -q "list my Google Tasks"
   ```
5. Try a capture skill — for example: `hermes skill run vault-capture/inbox-daily-capture` should drop `Inbox/{today}/daily/daily.md` into the vault.

## Why Hermes (and not Claude Code) owns the external connections

See [`.claude/rules/agent-boundaries.md`](../.claude/rules/agent-boundaries.md) §6 — every outbound OAuth / PAT / MCP credential is held by exactly one agent (Hermes) to avoid duplication, divergence, and split-brain on token refresh. Claude Code and Codex reach external systems only via Hermes' two paths:

- **push** — Hermes writes raw capture to `Inbox/{date}/{source}/`. Claude curates from there.
- **pull** — Claude runs `hermes chat -q "..."` for live lookups (the [`hermes-query`](../.claude/skills/hermes-query/SKILL.md) skill).

## Optional

If you don't want Hermes at all, you can:

- Remove this folder.
- Strip the corresponding `.claude/skills/hermes-query/` and `.claude/skills/aggregate-*/` references.
- Drop the `Inbox/` capture pipeline (move to fully-manual capture).

Claude Code + Codex still work without Hermes — you just lose the automated Slack / GCal / GTasks / GitHub ingestion.
