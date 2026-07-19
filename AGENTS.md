# AGENTS.md — Claudian Orchestra Core Contract

**This is an Obsidian vault** operated as a personal knowledge base by **two agents**:

| Agent | Role | Default |
|---|---|---|
| **Core agent** | Conversation, orchestration, implementation, all curated-note editing | **Codex** (Claude Code selectable — see §0) |
| **Hermes** | Always-on ingestion. Owns ALL external connections (Slack / Google / GitHub MCP / …) | [Hermes Agent](https://github.com/NousResearch/Hermes-Agent) (optional) |

This file is the **single core contract**: whichever CLI you run as the core reads and follows it. Codex loads it natively; Claude Code is pointed here by [[CLAUDE.md]].

---

## 0. Core configurations & terminology

Pick ONE configuration at setup time (the `core-setup` flow — [[.claude/skills/core-setup/SKILL.md]] — asks this and records it in [[.claude/connections.yaml]] `core:`):

| `core:` | Meaning | What stays in the repo |
|---|---|---|
| `codex` (default) | Codex CLI is the only core | `core-setup` migrates `.claude/` → `.agents/` (link rewrite included) and removes Claude-specific files (`CLAUDE.md`, hooks, settings) |
| `claude` | Claude Code is the only core | Remove `.codex/` (this file stays — it is the core contract) |
| `both` | Both CLIs are used interchangeably as the core | Keep everything |

**Terminology rule (important):** the rules and skills under `.claude/` predate this contract and often say 「Claude (Code) が…」. **Read every such mention as "the core agent"** — the content is agent-neutral; only the directory name and wording are historical. Never interpret it as "delegate to a separate Claude".

There is exactly **one core at a time**. The old two-headed model (Claude orchestrates, Codex implements via delegation) is retired; the core agent both decides and implements.

---

## 1. Domain layout

| Domain | Path | Content |
|---|---|---|
| **Inbox** | `Inbox/{YYYY-MM-DD}/{daily,slack,discord,code,mtgs,clippings,chat-logs,mail,attachments}/` | Capture-only receiving area (raw, unsorted, **date-first**). Writers: Hermes / browser extensions only (**no auto-route**). The core agent aggregates same-day content into Daily; curation is a later step. [[Inbox/README.md]] |
| **Daily** | `Daily/` | The single hub per day (journal). Aggregates `Inbox/{date}/*` and distributes to Main DB. |
| **Work** | `Work/{PROJ_A,…}/` | Client engagements, 4-layer standard ([[.claude/rules/work-management.md]]). |
| **Research** | `Research/` (optional submodule) | Research work. A submodule's own contract takes precedence under it. |
| **Others** | `Others/{Ideas,Activities,Learning}/` | Ideas / PoC, continuous activities, learning notes. |
| **Maps** | `Maps/` | Cross-cutting MOCs + Bases views. `Code-Map.md` = codebase-knowledge entry. |
| **Persona** | `Persona/` | Single source of truth for the author's profile. |
| **Meta** | `Meta/` | Self-referential projects about the vault itself. |
| **Archive** | `Archive/` | Inactive-content sink (never deleted). `status: archived`. |
| **Templates** | `Templates/` | Note templates. |
| **docs** | `docs/` | Human-facing setup guides (`connections/`). Not vault content. Entry: [[GETTING-STARTED.md]]. |

> Each domain ships its own `CLAUDE.md` contract file directly under the folder — read it before touching files there (the filename is historical; it applies to whichever core).

## 2. Note operation principles (highest priority)

- Notes are Markdown. Non-md work-products live under `_assets/`; external one-shot resources under `sources/` (immutable).
- Structural changes (new folders / renames / moves) must land in the same commit as the corresponding rules / README updates.
- Always include frontmatter (`type` / `status` / `tags` / `created` / `updated`). Schema: [[.claude/rules/vault-metadata.md]]. Tags: [[.claude/rules/vault-tagging.md]].
- Domain rules: [[.claude/rules/work-management.md]] / [[.claude/rules/research-management.md]] / [[.claude/rules/others-management.md]] / [[.claude/rules/daily-operations.md]].
- Agent boundaries (Hermes / core — capture/curate split, single-writer): [[.claude/rules/agent-boundaries.md]].
- Obsidian dialect (wikilinks, embeds, callouts, Bases) — preserve; don't reflow notes unnecessarily.

## 3. Language conventions

- **Thinking / internal processing / commit messages / identifiers / frontmatter keys + enum values / tags**: English.
- **User responses**: Japanese by default (adjust to the user's language).
- Details: [[.claude/rules/language.md]].

## 4. Operating model — one core, on-demand

The core agent handles conversation, judgment, design AND implementation. There is no implementation delegation to another chat agent.

- **All external connections go through Hermes** (push: capture → `Inbox/{date}/{source}/` / pull: `hermes chat -q` — follow [[.claude/skills/hermes-query/SKILL.md]]). The core never holds external OAuth/PAT. Exceptions listed in [[.claude/rules/agent-boundaries.md]] §6 (vault git via local `git`/`gh`; web research reads; Claude-core-only Drive connector).
- **On-demand by default**: the Daily note's `## 🤖 ジョブリスト` is the operational checklist. The user says 「○○やって」; the core executes or delegates to Hermes. Cron is optional. [[.claude/rules/daily-operations.md]] §0.
- **Skills**: workflows live as `SKILL.md` instruction files under `.claude/skills/{name}/`. When a trigger phrase matches (「接続セットアップして」「EOD distill」…), **read that SKILL.md and follow it**. Claude Code discovers them natively; Codex reads the file on demand — same contract either way.
- **Sub-work**: large research / analysis may use whatever parallel/sub-agent mechanism the core CLI offers. Findings go to `.claude/docs/research/` or `.claude/docs/libraries/`.
- **Approvals**: destructive / low-reversibility operations (delete, multi-file rename, schema migration, external writes, Main DB distribution) require user approval — tiers in [[.claude/rules/agent-boundaries.md]] §5.

### Output contract

- Order: conclusion → rationale → next action. Make uncertainty explicit (guess / unverified / needs-check).
- Always show: commands run, files changed, test results. Failures reported with cause + blast radius — never hidden.

### Quality gates (before final response)

- Intent matches the user's request; diff self-reviewed; at least one executable check ran when feasible.

## 5. Write boundaries (single-writer principle)

| Path | Writer |
|---|---|
| `Inbox/{YYYY-MM-DD}/**` | Hermes + browser extensions only (capture). Core reads, then owns after aggregation |
| `Daily/**`, `Work/**`, `Others/**`, `Maps/**`, `Persona/**`, `Templates/**` | Core agent + user |
| `Research/**` (if submodule) | Per the submodule's own contract |
| `.claude/**` (control plane: rules / skills / registry / docs) | Core agent + user |
| `.hermes/**` SKILL.md / references / config | Read-only for Hermes itself (observation notes go to `Inbox/{date}/clippings/`); core + user may edit |
| External code repositories | **Read-only** (via Hermes GitHub MCP). Changes go through that repo's own PR flow |

- One auto-committer at a time — don't race with cloud sync / Obsidian Git / Hermes on the same file.
- Vault backup: your own GitHub repo via local `git`/`gh` ([[.claude/skills/vault-github-sync/SKILL.md]]).

## 6. Core-specific notes

### When the core is Codex

- Sandbox: default `read-only`; promote to `workspace-write` for edits per the user's request. Never silently escalate. Even in `workspace-write`, §5 boundaries apply.
- `claude.ai` connectors (e.g. Google Drive read) are unavailable — use the Hermes path instead ([[docs/connections/google-drive.md]] 経路 B).
- Codex-side extras (vendored Obsidian skills, config): [[.codex/AGENTS.md]].

### When the core is Claude Code

- `CLAUDE.md` (thin adapter) points here; `.claude/skills/` are natively discoverable; sub-research via its subagents.
- Claude-core-only exception: shared-drive Google Docs/Sheets **read** via the claude.ai Drive connector ([[.claude/rules/agent-boundaries.md]] §6).

## 7. Repository conventions

- **Python**: use `uv` exclusively (direct `pip` is forbidden).
- `.claude/rules/` take precedence over this file — surface conflicts, don't silently pick.
- Investigation artifacts → `.claude/docs/research/` / `.claude/docs/libraries/` (concise, dated, linked back).

## See also

- [[README.md]] — architecture overview / [[GETTING-STARTED.md]] — staged setup (Level 0–3)
- [[.claude/skills/core-setup/SKILL.md]] — core selection & migration / [[.claude/skills/connection-setup/SKILL.md]] — connection wizard
- [[.claude/rules/agent-boundaries.md]] — Hermes / core division of labor
