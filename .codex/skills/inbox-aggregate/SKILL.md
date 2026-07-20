---
name: inbox-aggregate
description: Aggregate one or more Inbox sources into today's Daily note with append-only summaries and source wikilinks. Use for Slack, meetings, code, clippings, or chat-log aggregation.
---

# Inbox aggregate

Aggregate captured material from `Inbox/{YYYY-MM-DD}/{source}/` into the matching section of `Daily/{YYYY-MM-DD}.md`. This skill summarizes and links; it does not distribute material to its final Main DB destination.

## Supported sources

| Source | Input | Reference |
|---|---|---|
| Slack | `slack/*.md` | `references/slack.md` |
| Meetings | `mtgs/*.md` | `references/meetings.md` |
| Code | `code/code.md` | `references/code.md` |
| Clippings | `clippings/*.md` | `references/clippings.md` |
| Chat logs | `chat-logs/*.md` | `references/chat-logs.md` |

When the user names a source, load only that reference. When the user asks to aggregate everything, process the sources in the table order and load each reference as needed.

## Workflow

1. Determine today's date with `date +%Y-%m-%d`; do not infer it from conversation context.
2. Read the latest `Daily/{date}.md`. If it does not exist, run or propose `daily-briefing` first.
3. Resolve the requested source or sources and list matching Inbox files.
4. Before summarizing each file, search the Daily note for its exact wikilink. Skip material already linked.
5. Read the source-specific reference, produce its concise bullet format, and route it to the documented Daily section.
6. Append only. Do not rewrite existing bullets or Daily frontmatter.
7. Re-read the edited Daily note and verify every new bullet contains a valid source wikilink.
8. Report processed, skipped, and missing source counts.

## Invariants

- Raw captures stay in Inbox until `eod-distill` handles distribution.
- Never paste full transcripts or long source bodies into Daily.
- Never invent facts absent from the capture.
- Use `Maps/People-Map.md` for participant-name normalization when processing meetings.
- Concurrent runs rely on exact source wikilinks for idempotency; re-read immediately before each append.

## Related

- `.codex/rules/inbox-routing.md`
- `.codex/rules/daily-operations.md`
- `.codex/skills/daily-briefing/SKILL.md`
- `.codex/skills/eod-distill/SKILL.md`
- `.codex/skills/session-log/SKILL.md`
