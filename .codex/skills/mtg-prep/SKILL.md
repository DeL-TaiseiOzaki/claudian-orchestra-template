---
name: mtg-prep
description: Prepare selected meetings by gathering context, creating draft meeting notes, and linking them from Daily. Use for MTG準備 or 議事録の叩き台 requests.
---

# Meeting preparation

Create a provider-neutral meeting-note draft before a meeting and link it from today's Daily note. A later transcript, regardless of provider, should reconcile into this draft instead of creating a duplicate note.

## Boundaries

- Prefer today's staged schedule in `Inbox/{date}/daily/daily.md` or the existing Daily note.
- If live schedule data is required, use `hermes-query`; the core does not call calendar services directly.
- Recording or notetaker enrollment is provider-specific and usually requires user action. Follow `Meta/connections/meeting-notes.md` only when that connection is enabled.
- Write only to curated `Wiki/` and `Daily/`, never to Inbox.
- Confirm the selected meetings and draft contents before writing.

## Workflow

1. Determine `{date}` with `date +%Y-%m-%d`.
2. List today's meetings from the staged schedule. If unavailable, ask the user for the meeting title and time; preparation can continue without a calendar connection.
3. Let the user select one or more meetings.
4. For each meeting, collect:
   - purpose or desired outcome (required)
   - agenda and open questions
   - participants, normalized through `Maps/People-Map.md`
   - pre-read material and related links
5. Propose `Wiki/meetings/{date}-{topic}.md`. Never overwrite an existing note without confirmation.
6. Create the note with standard frontmatter and `status: draft`:

   ```yaml
   ---
   title: "{meeting title}"
   type: "note"
   status: "draft"
   tags: ["meeting"]
   created: {date}
   updated: {date}
   meeting_date: {date}
   meeting_title: "{calendar title}"
   participants: [{participants}]
   ---
   ```

7. Use `Templates/meeting-note.md` for the body. Fill purpose, agenda, participants, and references; leave decisions, actions, and notes ready for the meeting.
8. Append a preparation link under the appropriate `## 📝 ログ` subsection in `Daily/{date}.md`:

   ```markdown
   - **[準備] {HH:MM} {meeting title}** → [[Wiki/meetings/{date}-{topic}.md]]（目的: {one-line purpose}）
   ```

9. If a meeting-note provider is enabled, remind the user of any remaining provider-specific recording or join action. Do not claim it was completed.

## Reconciliation

Match later files under `Inbox/{date}/mtgs/` to an existing draft by `meeting_date` plus `meeting_title`. `inbox-aggregate` summarizes the capture into Daily, and `eod-distill` merges durable decisions, actions, and source links into the existing draft before changing its status. File names do not need to match.

## Safety

- Daily edits are append-only and idempotent by exact draft wikilink.
- Transcript content must not replace user-authored preparation.
- Unknown participant names remain unchanged with a `?` note.
- Follow `.codex/rules/vault-metadata.md`, `.codex/rules/wiki-management.md`, and `Wiki/AGENTS.md`.

## Related

- `.codex/skills/hermes-query/SKILL.md`
- `.codex/skills/inbox-aggregate/SKILL.md`
- `.codex/skills/eod-distill/SKILL.md`
- `.codex/skills/daily-briefing/SKILL.md`
- `Meta/connections/meeting-notes.md`
