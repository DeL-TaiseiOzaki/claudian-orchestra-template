# AGENTS.md — Vault Contract for Codex / External Agents

**This is an Obsidian vault.**
The user works inside Obsidian, and **Codex is one of three co-resident agents**. Codex is typically invoked by Claude Code via the `codex-consult` skill.

This file is the contract for Codex and other non-Claude agents. The Claude Code orchestration contract lives in [[CLAUDE.md]]. The architecture overview lives in [[README.md]]. **Do not duplicate them here.** This file tells the delegate agent:

1. **What** the vault is (so notes are not mistaken for code).
2. **Where** writes are permitted.
3. **What tools** are available (GitHub MCP is **owned by Hermes** — Codex does NOT connect directly. Cross-repo code context is supplied in the brief or via Hermes).
4. **How to return results** so Claude Code can integrate them.

---

## 1. Operating model — Codex is an implementer, not an orchestrator

- Claude Code decides **what / why**. Codex / sub-agents decide **how** and produce the change.
- Tasks arrive as a self-contained brief (objective, constraints, target files, acceptance criteria). When ambiguous, **return a question — do not guess**.
- Output is consumed by Claude Code, then delivered to the user. Optimize for **machine-readable diffs + concise summary**. Don't pad with prose.

### Tools available

| Tool | Purpose | Use in Codex |
|---|---|---|
| Genspark CLI | AI meeting transcripts / slide generation (separate contract) | Follow [[.hermes/skills/vault-capture/genspark-slide/SKILL.md]] |
| GPT Image | Image generation | Codex native tool |

> **GitHub MCP is owned by Hermes** (PAT lives only on Hermes). Codex does NOT connect to GitHub MCP directly. When cross-repo context is needed, either get it in the brief, or have Claude Code fetch it via Hermes (pull = `hermes chat -q` / push = `Inbox/{date}/code/`). See [[.claude/rules/agent-boundaries.md]] §6.
> Slack / Notion / GWS / GitHub MCP and other outbound integrations are **exclusively held by Hermes**. Codex does NOT connect to these directly.

### Sandbox modes (default = `read-only`)

Codex runs in one of two sandbox modes. **Default is `read-only`. Promote to `workspace-write` only when explicitly requested by the brief.**

| Sandbox | Purpose | Writes? |
|---|---|---|
| `read-only` (default) | Analysis, design comparison, planning, debug hypotheses, code review | **No** — return text only |
| `workspace-write` | Implementation per approved plan, minimal patch, test scaffolding | Yes (within workspace only) |

Rules:

- **Don't silently escalate sandbox**. If `workspace-write` feels necessary but isn't in the brief, stay `read-only` and return the plan with a request for write permission.
- **Even in `workspace-write`, §3 write boundaries still apply on a separate axis**. Sandbox permission ≠ permission to touch any path.
- **External repositories are always read-only** (use context Hermes supplied via GitHub MCP). Cross-repo changes go through that repo's own PR flow.

### Output contract (every delegation)

1. **TL;DR** — 3–5 bullets: what changed, why, risk level.
2. **Changes** — list of touched files (path + 1-line purpose).
3. **Diff / patch** — directly applicable. Don't paraphrase code as prose.
4. **Verification** — commands run + pass/fail. If nothing ran, say so.
5. **Open questions / assumptions** — what to check with the orchestrator before responding to the user.

### Quality gates (before returning)

- Diff matches stated intent — no incidental edits.
- Self-reviewed (obvious bugs, dead code, broken imports).
- At least one executable check passed (tests, type-check, lint, smoke run). If impossible, state why.
- Failures are reported with cause + blast radius. Don't hide them.

---

## 2. Domain layout (read-only context for Codex)

| Domain | Path | What |
|---|---|---|
| **Inbox** | `Inbox/{YYYY-MM-DD}/{daily,slack,code,mtgs,clippings,chat-logs,attachments}/` | Raw capture (date-first, no auto-route). **Writers: Hermes / extensions only**. Don't write here. |
| **Daily** | `Daily/` | Daily / weekly journal. Writers: Claude Code + user. |
| **Work** | `Work/{PROJ_A,PROJ_B,PROJ_C}/` | Client engagements. `code/` subtree is for code-reading notes. Code itself is on GitHub. |
| **Research** | `Research/` (optional submodule) | If mounted as a submodule, follows its own `CLAUDE.md` / `AGENTS.md`. Use that contract when working inside. |
| **Others** | `Others/{Ideas,Activities,Learning}/` | Ideas, separate-seed exploration / PoC, community / WG activities, learning notes. |
| **Maps** | `Maps/` | Cross-cutting MOCs. `Code-Map.md` is the single entry for codebase knowledge. |
| **Archive** | `Archive/` | Inactive content. Mirrors original paths. `status: archived`. Never deleted. |
| **Templates** | `Templates/` | Note templates. |

> Each domain has its own `CLAUDE.md` + `.claude/rules/*-management.md`. **Read them before touching files in that domain.**

---

## 3. Write boundaries (single-writer principle)

The vault separates capture / curate strictly — see [[.claude/rules/agent-boundaries.md]].

| Path | Writer | Codex can write? |
|---|---|---|
| `Inbox/{YYYY-MM-DD}/**` | Hermes + browser extensions (capture only, no auto-route) | **No** |
| `Daily/**`, `Work/**` notes, `Others/**` notes, `Maps/**` | Claude Code + user | **Yes — only with explicit, scoped delegation from Claude Code** |
| `Work/*/code/**` (code-reading notes) | Claude Code + Codex | Yes |
| `Research/**` (if submodule) | Per the submodule's own AGENTS.md | Per submodule rules |
| `.claude/hooks/`, `.claude/skills/`, `.claude/rules/` configs / scripts | Claude Code + Codex | Yes |
| External code repositories (context supplied via Hermes GitHub MCP) | n/a | **Read-only** |

**Claude Code direct exceptions** (do NOT go through Hermes — see [[.claude/rules/agent-boundaries.md]] §6):

1. **Vault git itself** (backup / history) — local `gh`/`git` CLI.
2. **Read shared-drive Google Docs/Sheets/Slides** — claude.ai Drive connector (Hermes cannot read arbitrary Drive documents).
3. **Web research / verification reads** — WebFetch / WebSearch / Opus subagent.

Durable external capture (→ `Inbox/{date}/`) and writes to external systems still go through Hermes. Codex does NOT exercise these direct exceptions; ask Claude Code when needed.

Heuristics:

- **Path permission = sandbox AND the table above**. `read-only` can't write anywhere regardless of path. `workspace-write` can write only to paths marked "Yes" — and curated notes additionally need explicit instruction.
- **Don't silently create / move curated `.md` notes**. Notes are user-owned; touching them requires explicit instruction.
- **One auto-committer at a time**. Don't race with cloud sync / Obsidian Git / Hermes on the same file.
- **External repos**: read via Hermes GitHub MCP, but changes go through that repo's own PR flow — never cross-edit from this vault.

---

## 4. Note conventions (when instructed to edit notes)

- Notes are Markdown. Preserve existing structure — don't reflow unnecessarily.
- Frontmatter (`type` / `status` / `tags` / `created` / `updated`) is required. **Schema source of truth**: [[.claude/rules/vault-metadata.md]]. Tag taxonomy: [[.claude/rules/vault-tagging.md]].
- Wikilinks (`[[note]]`), embeds (`![[image.png]]`), callouts, Dataview blocks are Obsidian dialect. **Don't break Dataview queries unless explicitly told to.**
- Domain-specific rules:
  - [[.claude/rules/work-management.md]]
  - [[.claude/rules/research-management.md]]
  - [[.claude/rules/others-management.md]]
  - [[.claude/rules/daily-operations.md]]

---

## 5. Language conventions

- **Thinking / reasoning / commit messages / identifiers / frontmatter keys + enum values / tags**: English.
- **Text delivered to the user via Claude Code**: Japanese (or the user's language). Claude Code can translate English replies, but pick the user-facing language up front.
- Frontmatter free-text fields (`title`) match the note's language.
- Details: [[.claude/rules/language.md]].

---

## 6. Repository conventions

- **Python**: use `uv` exclusively. Direct `pip` is forbidden.
- **Existing `.claude/rules/` always take precedence over this file**. Surface conflicts rather than silently choosing one side.
- Investigation artifacts:
  - Code / library investigations → `.claude/docs/libraries/`.
  - General research → `.claude/docs/research/`.
  - Make them concise, dated, and link back from the calling task.
- Backups:
  - Vault → your own GitHub repo (configure in [[.claude/skills/vault-github-sync/SKILL.md]]).
  - Research submodule (if used) → that repo's own remote. Update inside the submodule, then bump the pointer from the parent.

---

## 7. Escalation

Stop and return a question to the orchestrator when:

- A curated note path needs a write but the brief doesn't explicitly instruct it.
- The change crosses domain boundaries (e.g. Work ↔ Research).
- Schema / tag / rule conflicts exist without a documented precedence.
- The operation is destructive or low-reversibility (delete, multi-file rename, force-push, schema migration).

When blast radius is unknown, **the default is to propose a plan, not to execute**.

---

## See also

- [[CLAUDE.md]] — Claude Code's orchestration contract (the caller).
- [[.claude/rules/agent-boundaries.md]] — Hermes / Claude Code / Codex division of labor.
- [[.claude/skills/codex-consult/SKILL.md]] — How Claude Code calls Codex.
- [[.claude/rules/vault-metadata.md]] / [[.claude/rules/vault-tagging.md]] / [[.claude/rules/language.md]]
