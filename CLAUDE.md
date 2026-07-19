# CLAUDE.md — Claude Code as the Core (adapter)

**Read [[AGENTS.md]] first and follow it as your operating contract.** This vault runs a **single core agent + Hermes**; when you (Claude Code) are the core, AGENTS.md §0–§7 define your duties in full — domain layout, note principles, write boundaries, language, approvals, output contract.

This file only adds what is Claude-specific.

## Claude-specific notes

- **You are the core**: conversation, orchestration, design AND implementation are all yours. There is **no delegation to Codex** — the old two-headed model is retired ([[AGENTS.md]] §0). If rules or skills say 「Claude (Code) が…」, that means you as the core; if anything still references `codex-consult`, treat it as obsolete.
- **Skills**: `.claude/skills/*/SKILL.md` are natively discoverable — invoke them on their trigger phrases (「接続セットアップして」→ `connection-setup`、「接続チェックして」→ `connection-doctor`、「EOD distill」→ `eod-distill` など).
- **Sub-work**: large investigations go to your subagents (`general-purpose` — [[.claude/agents/general-purpose.md]]); findings land in `.claude/docs/research/` / `.claude/docs/libraries/`.
- **Claude-core-only exception**: shared-drive Google Docs/Sheets **read** via the claude.ai Drive connector ([[.claude/rules/agent-boundaries.md]] §6). Codex cores use the Hermes path instead.
- **External connections**: never directly — always via Hermes ([[.claude/skills/hermes-query/SKILL.md]]), except vault git (local `git`/`gh`) and web research reads.
- **Domain contracts**: each domain folder ships an `AGENTS.md` ([[Wiki/AGENTS.md]], [[Persona/AGENTS.md]]). Claude Code does NOT auto-load nested AGENTS.md — read the folder's AGENTS.md before working in that domain.
- **Language**: think in English, respond in Japanese ([[.claude/rules/language.md]]).

## Configuration

- Your core registration lives in [[.claude/connections.yaml]] `core:` (`claude` or `both`). If it is `unconfigured`, offer the `core-setup` flow ([[.claude/skills/core-setup/SKILL.md]]).
- If the user chose `codex` only, this file (and Claude-specific assets) are removed by the core-setup migration — you should not be reading it in that configuration.

## Entry points

- Architecture: [[README.md]] / staged setup: [[GETTING-STARTED.md]]
- Rules index: `.claude/rules/` (metadata / tagging / language / daily-operations / inbox-routing / agent-boundaries / work / research / others)
- Connection guides: [[Meta/connections/README.md]]
