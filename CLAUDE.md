# CLAUDE.md — Vault Contract

**This vault is an Obsidian Vault optionally mounted on Google Drive / Dropbox / iCloud / etc.**
The user works inside Obsidian, and **three agents — Claude Code / Codex / Hermes — co-reside** in the same vault.
External data sources are **owned by Hermes** (Slack / Google Workspace / Notion / Web / GitHub MCP — the GitHub PAT lives only on Hermes; Claude Code and Codex don't talk to external APIs directly except for vault git backup).
Work-flow conversations happen in **Slack** (via the Hermes Slack app).

★ **All capture / aggregate / consistency checks are on-demand by default** ★
Cron-driven runs are deprecated. The **Daily note's `## 🤖 ジョブリスト` section** is the operational checklist — the user reads it and tells Claude "do X", which Claude either executes directly or delegates to Hermes via [[.claude/skills/hermes-query/SKILL.md]]. State is auto-updated from the existence of files under `Inbox/{date}/{source}/`. See [[.claude/rules/daily-operations.md]] §0.

Primary purpose: **create / organize / reference your work as Markdown notes (`.md`)**.
★ **Use the §4 orchestration contract aggressively for code work**. ★

> Architecture overview: [[README.md]]. Ingestion routing: [[.claude/rules/inbox-routing.md]]. Agent boundaries: [[.claude/rules/agent-boundaries.md]].

---

## 1. Domain layout

| Domain | Path | Content |
|---|---|---|
| **Inbox** | `Inbox/{YYYY-MM-DD}/{daily,slack,code,mtgs,clippings,chat-logs,attachments}/` | Capture-only receiving area (raw, unsorted, **date-first**). Writers: Hermes / browser extensions only (**no auto-route**). Same-day content gets aggregated to Daily; curation is a later step. [[Inbox/README.md]] |
| **Daily** | `Daily/` | The single hub per day (journal). Aggregates `Inbox/{date}/*` and distributes to Main DB. Daily / weekly reviews. |
| **Work** | `Work/{PROJ_A,PROJ_B,PROJ_C}/` | Client engagements. Each project follows the **4-layer standard** (per-project `CLAUDE.md` + `sources/` + curated + `logs/`, [[.claude/rules/work-management.md]]). Add new project codes as needed. |
| **Research** | `Research/` (optional submodule) | Research work. Often hosted as a git submodule with its own `CLAUDE.md` + `.claude/rules/`. The submodule's rules take precedence over vault rules for files under it. |
| **Others** | `Others/{Ideas,Activities,Learning}/` | Ideas (seed-level), separate-seed exploration / PoC (type: idea / exploration), continuous activities (community / committees / WG / Kaggle / ecosystem cultivation), learning / book notes. |
| **Maps** | `Maps/` | Cross-cutting MOCs (entry notes) + search layer. `Home.md` = vault entry; `Code-Map.md` = single entry for codebase knowledge (code itself lives on GitHub); `views/` = 5-label Bases views (Logs / Knowledge / Memories / SPK etc.). |
| **Persona** | `Persona/` | Single source of truth for the author's profile (history / publications / skills). Referenced **across the whole vault** by Work proposals / Others activities / Research applications. [[Persona/CLAUDE.md]] |
| **Meta** | `Meta/` | Self-referential projects about the vault itself (re-architecture, pipeline rebuilds). 1 project = 1 sub-folder. Archive after completion. |
| **Archive** | `Archive/` | Inactive-content sink (never deleted). Mirrors original paths. `status: archived`. [[.claude/skills/vault-archive/SKILL.md]] |
| **Templates** | `Templates/` | Note templates. |

> Each domain ships its own `CLAUDE.md` directly under the folder — always consult it. CLAUDE.md states "what to do + placement / naming / frontmatter / forbidden patterns" concisely; details live in `.claude/rules/*-management.md`.

---

## 2. Note operation principles (highest priority)

- Notes are Markdown. Non-md work-products (scripts / generated data / diagrams) live under `_assets/` next to where they belong (the canonical attachment store is `Inbox/{date}/attachments/`; the canonical code store is GitHub).
- **Exception: `sources/`** (under Work projects and Others/Activities sub-areas) accepts external one-shot resources in non-md form. Treat as **immutable** (don't rename / edit / delete); distill into `docs/` / `notes/` ([[.claude/rules/work-management.md]]).
- Structural changes (new folders / renames / moves) must happen in the same commit as the corresponding rules / README / domain `CLAUDE.md` update.
- Anyone can create / edit notes: you, the user, codex, and subagents.
- Always include frontmatter (`type` / `status` / `tags` / `created` / `updated`). Schema: [[.claude/rules/vault-metadata.md]]. Tag taxonomy: [[.claude/rules/vault-tagging.md]].
- Domain-specific rules: [[.claude/rules/work-management.md]] / [[.claude/rules/research-management.md]] / [[.claude/rules/others-management.md]] / [[.claude/rules/daily-operations.md]].
- Agent boundaries (Hermes / Claude Code / Codex — control plane, sources of truth, capture/curate split): [[.claude/rules/agent-boundaries.md]].
- Note-writing skills: `work-project-writer` / `others-writer` / `daily-briefing` / `weekly-review` / `vault-github-sync` (research uses skills inside `Research/` if mounted as a submodule).
- Maintenance skill: `vault-archive` (anti-bloat: move inactive notes to `Archive/` — approval required).
- Backup target: your own GitHub repo (see [[.claude/skills/vault-github-sync/SKILL.md]]).

---

## 3. Language conventions

- **Thinking / internal processing**: English (search, organization, structuring).
- **User responses**: Japanese by default (descriptions, questions, status updates, warnings). Adjust to the user's language.
- **Code / identifiers / commands / frontmatter keys / enum values / tags**: English.
- Frontmatter free-text fields (`title`) match the note's language.
- Details: [[.claude/rules/language.md]].

---

## 4. Orchestration contract (code work only)

For code work, Claude Code is **orchestrator, not implementer**.
The top priorities are **conversation quality** and **context economy**. **Do not apply this to note operations**.

### Mission
- Organize / prioritize / align on user requests.
- Delegate to appropriate agents (Codex / Opus subagent).
- Integrate results, present judgments and next actions.

### Non-Goals (what Claude does NOT do directly)
- Large implementations (rule of thumb: > 10 LOC).
- Large investigations (cross-cutting analysis / web research) → Opus subagent.
- Reading long logs / many files sequentially.

### Routing
- **Design / planning / complex implementation / debug / root-cause analysis** → Codex (via `general-purpose`, follow [[.claude/skills/codex-consult/SKILL.md]]).
- **External research / broad analysis** → `general-purpose` subagent (Opus).
- **All external connections** (Slack / Google Tasks·Calendar / Notion / Web fetch / Genspark transcripts / GitHub MCP) → **delegate to Hermes** (push: user instruction → on-demand capture → `Inbox/{date}/*` / pull: `hermes chat -q`, follow [[.claude/skills/hermes-query/SKILL.md]]). The only exception is **vault git backup** ([[.claude/skills/vault-github-sync/SKILL.md]] uses Claude's local `git`/`gh` — see [[.claude/rules/agent-boundaries.md]] §6).
- **Multimodal input (PDF / images)** → Claude directly (delegate to subagent for large analysis).
- **Image generation** → [[.claude/skills/image-gen/SKILL.md]] (Codex `$imagegen` generates, Claude copies the file into the target note's `_assets/` and embeds with `![[...]]`. Codex sandbox cannot write to remote-mounted vaults, so Claude handles final placement).
- **Minor fixes (single file / small change)** → Claude directly.
- **Session work → Daily log** → [[.claude/skills/session-log/SKILL.md]] (append-only logging for parallel Claude Code sessions).
- **Inbox → Daily aggregation** (mid-day on-demand) → [[.claude/skills/aggregate-slack/SKILL.md]] / [[.claude/skills/aggregate-mtgs/SKILL.md]] / [[.claude/skills/aggregate-code/SKILL.md]] / [[.claude/skills/aggregate-clippings/SKILL.md]] / [[.claude/skills/aggregate-chat-logs/SKILL.md]] (morning sweep: [[.claude/skills/daily-briefing/SKILL.md]]).
- **EOD distill** (Daily → Main DB / once a day / serial) → [[.claude/skills/eod-distill/SKILL.md]] (independent from daily-briefing).

> Codex consultation triggers / call patterns / templates / result integration: follow **codex-consult** skill. Enforcement via `.claude/hooks/check-codex-*.py`.

### Delegation Trigger (delegate when any apply)
1. Output likely > 10 lines.
2. Editing 2+ files.
3. Reading 3+ files.
4. Design judgment / trade-off comparison required.
5. Web / latest-information verification required.

### Execution Patterns
- **A. Foreground**: when next steps depend on the result. Specify return format (3–5 bullet summary).
- **B. Background**: run independent tasks in parallel, keep the conversation flowing.
- **C. Save-to-file**: 20+ line outputs go to `.claude/docs/`, only summary back to chat.

### Output Contract
- Order: conclusion → rationale → next action.
- Make uncertainty explicit (distinguish guess / unverified / needs-check).
- Always show: commands run, files changed, test results.

### Quality Gates (before final response)
- Intent matches the user's request.
- Self-reviewed the diff.
- Ran at least one executable test / check.
- For failures: state cause and blast radius.

---

## 5. Repository conventions

- Python: use `uv` (direct `pip` use is forbidden).
- The existing rules in `.claude/rules/` take precedence.
- Subagent investigations go to `.claude/docs/research/`; library investigations to `.claude/docs/libraries/` (matches [[.claude/agents/general-purpose.md]]).
