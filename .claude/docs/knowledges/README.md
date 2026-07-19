---
title: "Knowledges — durable learnings"
type: "note"
status: "in-progress"
tags: ["meta", "knowledge"]
created: 2026-01-01
updated: 2026-01-01
---

# Knowledges — durable learnings MOC

Entry point for **reusable learnings** (root causes / gotchas / patterns) discovered during agent work in this vault.

> Operating skill: [[.claude/skills/knowledge-capture/SKILL.md]]
> Note format: [[.claude/skills/knowledge-capture/references/template.md]]
> Category definitions: [[.claude/skills/knowledge-capture/references/categories.md]]

## Categories

| Category | Count | Content |
|---|---:|---|
| hermes | 0 | hermes daemon / cron / skills / MCP / CLI specifics |
| claude-cli | 0 | Claude Code harness behaviour |
| mcp | 0 | MCP protocol / server-general |
| git | 0 | git workflow |
| vault | 0 | Obsidian / vault structure |
| architecture | 0 | Multi-agent orchestration / policy |
| codex | 0 | Codex CLI 固有の挙動（sandbox / config / skills 連携の gotcha） |
| python | 0 | Python / uv / encoding |

## Usage

### When you need to look something up
1. Grep / Obsidian-search inside the category dir.
2. If the symptom is unfamiliar, search by tags (`tag:gotcha tag:hermes`).
3. When you find a similar note, **update it** — don't create a duplicate.

### When you want to capture a finding
1. Trigger `/knowledge-capture` or ask Claude "これ knowledge 化して" ("capture this as a knowledge note").
2. Fill in the 5-section template (symptom / context / root cause / fix / prevention).
3. Always link to the related issue / commit hash / sibling knowledge.

### When a note goes stale
- `status: superseded` (newer note replaces it) or `status: deprecated` (root cause has been resolved).
- **Never delete** — "things used to be this way" is itself useful context for future agents.

## What NOT to put here

- Daily content → `Daily/`
- 人間向けの汎用ナレッジ（学習・文献・アイデア）→ `Wiki/`（ここは agent 運用知のみ）
- Raw investigation results → `.claude/docs/research/`
- A learning that only matters to one skill → that skill's `SKILL.md` `## Pitfalls` section

## See also

- [[.claude/skills/knowledge-capture/SKILL.md]] — operating skill
- [[Maps/Code-Map.md]] — codebase knowledge MOC
- [[AGENTS.md]] §4 operating model
