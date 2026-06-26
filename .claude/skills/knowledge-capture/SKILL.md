---
name: knowledge-capture
description: "Capture durable learnings (root causes, gotchas, recurring patterns, postmortems) discovered during agent work into the structured knowledge base under .claude/docs/knowledges/. Use when a root cause is identified after debugging, when Codex consultation surfaces a non-obvious finding, when a sequence of failed hypotheses leads to insight, or when the user says 'これ knowledge 化して' / '学びをまとめて'."
---

# knowledge-capture

Curates the your-vault vault's **persistent learnings layer** at `.claude/docs/knowledges/`.

This skill exists because the vault accumulates valuable debugging knowledge (`status.md #38` MCP env passthrough, `#33` cron durability, `#15` argparse quirks, etc.) that risks dispersal across status notes, commit messages, and skill SKILL.md headers. Knowledge here is meant to be **re-readable later, when the same symptom recurs**.

## When to invoke

### Explicit invocation (always)
- the user says "これ knowledge 化して" / "学びをまとめて" / "今回の learning を残して"
- Skill name `/knowledge-capture` in chat
- Reference an existing knowledge note → triggers a review/update

### Claude proactive hints (suggest, never force)
When any of these patterns occur in a session, Claude **proposes** capture and waits for the user's approval:

1. **Root cause confirmed after >=2 failed hypotheses** — e.g. #38 ran through PAT scope → SSO authorization → fine-grained owner → Classic PAT regen → finally found `_build_safe_env()` filtering. Hypothesis chain that ends in a non-obvious cause is the strongest signal.
2. **Codex returns a structured response that resolves a previously stuck issue** — the design / Risks section often surfaces a reusable insight beyond the immediate fix.
3. **A specific harness / tool / API quirk is identified** — argparse positional ordering, env passthrough rules, cron expression edge cases.
4. **A policy fails in production** — e.g. #37 markdown callout not enforced. The non-effectiveness itself is the learning.
5. **Repeating the same Codex consultation feels likely** — knowledge note prevents re-spending tokens on the same investigation.

Phrasing for proactive hint (always offer "skip" option):

> 💡 今回の発見（`<one-line summary>`）は knowledge note 化するとよさそうです。`.claude/docs/knowledges/<category>/<slug>.md` に記録しますか？（skip / proceed / template だけ見せて）

### Do NOT invoke for
- Daily journaling (`Daily/`)
- Project-specific notes (`Work/{PROJ_A,PROJ_B,PROJ_C,PROJ_D,PROJ_E,PROJ_F}/`)
- Codex raw consultation results (use `.claude/docs/research/`)
- Decision log entries that belong in `status.md`
- One-off task tracking

## Structure

```
.claude/docs/knowledges/
├── README.md             ← MOC (entry point; categories + recent notes)
├── hermes/               ← hermes 固有の挙動・落とし穴
├── claude-cli/           ← Claude Code harness (CronCreate / TaskCreate / MCP loading)
├── mcp/                  ← MCP 全般 (env passthrough, transport, auth)
├── git/                  ← git workflow / commit / branch patterns
├── vault/                ← Obsidian / vault structure / single-writer
├── architecture/         ← agent orchestration / policy enforcement
├── codex/                ← Codex consultation patterns (when to ask, prompt shape)
└── python/               ← Python / uv / dependency idioms
```

Categories are extensible — add a new dir if a learning doesn't fit. See `references/categories.md` for definitions and examples.

## Note format

Every knowledge note follows the template at `references/template.md`. Required sections:

- **症状 (Symptom)** — concrete observable, 1–3 lines
- **文脈 (Context)** — when / where / what configuration
- **根本原因 (Root cause)** — final cause with code/spec citation
- **修正 (Fix)** — concrete diff / command / setting
- **再発防止チェック (Future-proof check)** — 1-line command or indicator to detect recurrence
- **関連 (Related)** — `status.md` issue#, commits, sibling knowledge notes

Required frontmatter:

```yaml
---
title: "..."
type: "knowledge"
status: "active"       # active | superseded | deprecated
tags: ["category", "subdomain", ...]
created: YYYY-MM-DD
updated: YYYY-MM-DD
source: "incident:#NN" or "session:YYYY-MM-DD" or "codex-consult:<topic>"
applies_to: ["hermes/cron", "mcp/stdio"]
related_commit: "<short-hash>"   # optional
severity: low | medium | high
---
```

## Naming convention

- Path: `.claude/docs/knowledges/{category}/{slug}.md`
- Slug: kebab-case English, descriptive of the cause not the symptom. Examples:
  - ✅ `hermes/mcp-env-passthrough.md` — names the cause
  - ❌ `hermes/github-mcp-404.md` — names a symptom that has many causes
- Avoid date prefixes; recency belongs in `updated:` frontmatter and `git log`

## Lifecycle

| status | Meaning |
|---|---|
| `active` | Current. Reflects today's truth |
| `superseded` | A newer note replaces this one. Add `superseded_by: [[...]]` frontmatter |
| `deprecated` | Cause no longer applies (e.g. hermes upgrade fixed it). Add `deprecated_at: YYYY-MM-DD` and 1-line reason in body |

Never delete a knowledge note. Even deprecated entries help future readers verify "yes, this used to happen, and here's why it doesn't anymore."

## Linking & discoverability

- Each knowledge note should link back to `[[status.md]] #NN` if the source is a tracked issue
- The MOC (`README.md`) lists the 5 most-recently-updated notes per category at the top
- Reference from skills: a hermes / Claude skill's SKILL.md may link to specific knowledges from its "Pitfalls" or "Known issues" section
- `vault-consistency-check` may eventually validate knowledge note frontmatter

## 関連

- 入口: [[.claude/docs/knowledges/README.md]]
- テンプレート: [[.claude/skills/knowledge-capture/references/template.md]]
- カテゴリ定義: [[.claude/skills/knowledge-capture/references/categories.md]]
- 隣接 skill: [[.claude/skills/codex-consult/SKILL.md]]（諮問結果は research/、durable learning は knowledges/）、[[.claude/skills/vault-archive/SKILL.md]]（archived knowledge は deprecated に残し移動しない）
- 親ルール: [[CLAUDE.md]] §4 オーケストレーション契約 / [[.claude/rules/agent-boundaries.md]]
