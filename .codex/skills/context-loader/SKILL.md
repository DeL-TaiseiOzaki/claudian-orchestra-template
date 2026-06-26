---
name: context-loader
description: ALWAYS activate this skill at the start of every task. Load shared project context (CLAUDE.md contract, .claude/rules/, prior subagent findings) so Codex has the same knowledge as Claude Code before executing any task.
---

# Context Loader Skill

## Purpose

Load shared project context so Codex CLI has the same knowledge as Claude Code.
<your-vault> is a **note-first Obsidian vault**; Codex is used only for code design /
implementation / debugging consults. Load the context that actually exists.

## When to Activate

**ALWAYS** — run at the beginning of every task to load project context.

## Workflow

### Step 1: Load the contract

Read `CLAUDE.md` (vault root) — the Vault + orchestration contract:
domains (Work / Research / Others / Daily), note-operation principles,
routing, delegation triggers, language protocol, repository conventions.

### Step 2: Load vault rules

Read the relevant files in `.claude/rules/` (highest priority):

```
.claude/rules/
├── vault-metadata.md       # frontmatter schema (type/status/tags/created/updated)
├── vault-tagging.md        # tag taxonomy
├── language.md             # think in English, respond in Japanese
├── work-management.md      # Work projects (PROJ_A/PROJ_B/PROJ_C/...)
├── research-management.md  # Research submodule pointer
├── others-management.md    # Ideas/Exploration/Ecosystem/Activities/Learning
└── daily-operations.md     # Daily / Weekly operations
```

### Step 3: Check prior subagent findings (if relevant)

If the task touches a topic that may have been investigated, check:

```
.claude/docs/research/      # research findings
.claude/docs/libraries/     # library investigations
```

These may be empty until a subagent has run.

### Step 4: Execute task

With the loaded context, follow the contract and rules. Key points:

1. **Notes (`.md`) are edited directly** — no Codex / lint / delegation for note work.
2. **Use `uv`** for Python — never use `pip` directly.
3. **`.claude/rules/` takes highest priority.**
4. Follow the existing style and naming conventions; avoid unnecessary abstractions.

## Language Protocol

- **Thinking / Reasoning**: English
- **Code**: English (variables, functions, comments)
- **User communication**: Japanese (when reporting back through Claude Code)

## Output

After loading context, briefly confirm:
- Contract + rules loaded
- Relevant prior findings checked (or none)
- Ready to execute task
