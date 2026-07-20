---
name: context-loader
description: Always load the root contract, shared vault rules, and relevant prior findings at the start of every task.
---

# Context Loader Skill

## Purpose

Load shared project context before executing any task.
<your-vault> is a **note-first Obsidian vault** operated by a single core agent
(Codex by default — see [[AGENTS.md]] §0) plus Hermes for ingestion.
Load the context that actually exists.

## When to Activate

**ALWAYS** — run at the beginning of every task to load project context.

## Workflow

### Step 1: Load the contract

Read `AGENTS.md` (vault root) — the single core contract:
core configuration & terminology (§0), domains (Wiki / Daily),
note-operation principles, routing, language protocol, repository conventions.

### Step 2: Load vault rules

Read the relevant files in `.codex/rules/` (highest priority). Always load the
cross-cutting four, then domain rules on demand:

```
.codex/rules/
├── vault-metadata.md       # frontmatter schema (type/status/tags/created/updated)  ← always
├── vault-tagging.md        # tag taxonomy                                           ← always
├── language.md             # think in English, respond in Japanese                  ← always
├── agent-boundaries.md     # core / Hermes boundaries, system of record             ← always
├── wiki-management.md      # Wiki (ideas/learning/paper/experiment/activity notes)  ← on demand
├── inbox-routing.md        # Inbox → Daily → Main DB routing                        ← on demand
└── daily-operations.md     # Daily / Weekly operations                              ← on demand
```

### Step 3: Check prior subagent findings (if relevant)

If the task touches a topic that may have been investigated, check:

```
.codex/docs/research/      # research findings
.codex/docs/libraries/     # library investigations
```

These may be empty until a subagent has run.

### Step 4: Execute task

With the loaded context, follow the contract and rules. Key points:

1. **Notes (`.md`) are edited directly** — no extra delegation for note work.
2. **Use `uv`** for Python — never use `pip` directly.
3. **`.codex/rules/` takes highest priority.**
4. Follow the existing style and naming conventions; avoid unnecessary abstractions.

## Language Protocol

- **Thinking / Reasoning**: English
- **Code**: English (variables, functions, comments)
- **User communication**: Japanese

## Output

After loading context, briefly confirm:
- Contract + rules loaded
- Relevant prior findings checked (or none)
- Ready to execute task
