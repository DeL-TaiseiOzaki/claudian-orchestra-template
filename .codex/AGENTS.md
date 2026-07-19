# .codex/AGENTS.md — Codex-core supplements

**The operating contract is the root [[AGENTS.md]]** — read that first. Codex is the **default core agent** of this vault (conversation, orchestration, implementation, curated-note editing all in one). This file only holds Codex-side extras.

## 1) Sandbox discipline

- Default `read-only` for analysis / planning; promote to `workspace-write` when the user's request implies edits. Never silently escalate.
- Even in `workspace-write`, the write boundaries of root AGENTS.md §5 apply (Inbox は Hermes 専用、外部リポは read-only 等).

## 2) Skills

Workflow skills live under `.claude/skills/{name}/SKILL.md` (shared control plane — the directory name is historical; read 「Claude (Code)」 in their text as "the core agent" = you). On a trigger phrase (「接続セットアップして」「EOD distill」「接続チェックして」…), read that SKILL.md and follow it.

Vendored Obsidian file-format skills (physical copies under `.codex/skills/`, registered in `.codex/config.toml`):

| Skill | Use when |
|-------|----------|
| `obsidian-markdown` | Editing `.md` notes: wikilinks, embeds, callouts, frontmatter, tags |
| `obsidian-bases` | Creating/editing `.base` files (database-like views, filters, formulas) |
| `json-canvas` | Creating/editing `.canvas` files (nodes, edges, groups) |
| `defuddle` | Extracting clean markdown from web pages (external `defuddle` CLI required) |
| `context-loader` | Loading vault rules/context at session start |

## 3) Response discipline (kept from the legacy contract)

- Lead with the conclusion (TL;DR), then rationale, then next action.
- Show commands run, files changed, verification results. Separate unverified items as TODOs.
- If requirements are ambiguous, state assumptions explicitly before implementing; for large changes, propose incremental introduction with minimal diffs.
- Follow existing style; no unnecessary abstractions; don't swallow exceptions.

## 4) What Codex does NOT do

- Hold external OAuth/PAT or call Slack / Google / Notion / GitHub MCP directly — **all external connections go through Hermes** (pull = `hermes chat -q`, push = capture skills → `Inbox/{date}/`). See [[.claude/rules/agent-boundaries.md]] §6.
- Use claude.ai connectors (Drive read is a Claude-core-only exception — Codex cores use the Hermes path, [[Meta/connections/google-drive.md]] 経路 B).
- Write into `Inbox/{date}/**` (Hermes / extensions only).

## 5) References

- Root [[AGENTS.md]] — the core contract (§0 terminology: one core at a time)
- `.claude/rules/` — vault rules (highest priority)
- [[.claude/skills/core-setup/SKILL.md]] — codex-only にする場合の `.claude/` → `.agents/` 移行
