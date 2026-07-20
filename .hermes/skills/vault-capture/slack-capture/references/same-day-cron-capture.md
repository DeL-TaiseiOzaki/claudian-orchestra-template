# Same-day cron capture notes

Covers same-day scheduled capture for local-timezone `00:00` to now, collecting user-authored and @mention messages including private/DM where visible.

> Trigger note: on-demand kick (from the Daily `## 🤖 ジョブリスト`) is the primary path now; cron is just one transitional trigger (existing jobs only, no new ones). The capture logic below applies the same way however it is invoked.

## Durable workflow details

- Treat same-day cron as a digest-writing capture, not the ad-hoc text report path. The bundled `scripts/slack_today_my_messages.py` is useful as a user-token search example, but it does not write digest files or preserve existing digest richness.
- Always run user-token `search.messages` first for cross-channel visibility:
  - `from:{username} after:{YYYY-MM-DD} before:{YYYY-MM-DD+1}`
  - `from:<@{user_id}> after:{YYYY-MM-DD} before:{YYYY-MM-DD+1}`
  - mention queries for `<@{user_id}>` / `@{username}` when capturing mentions.
- Then run bot-token `conversations.list` + `conversations.history` only as a supplement for channels/DMs the bot can read. If bot supplement hits `http_429` / rate limit after user-token search succeeded, report it as partial-coverage warning rather than failing or rewriting existing captures.
- Write new digests directly to `Inbox/{YYYY-MM-DD}/slack/{channel}.md`. Capture only — do not route or infer curated destinations.
- For an existing digest, first search `Daily/{YYYY-MM-DD}.md` for its exact source wikilink. If linked, the core owns it: skip unchanged. Only an unlinked pre-aggregation digest may be repaired and appended with missing entries keyed by `channel_id + ts`; preserve richer content.
- For thread replies, fetch parent and adjacent replies when possible; if unavailable, keep the primary message and log a warning.
- For temporary one-off helpers, place them under `.tmp/`, remove them before finalizing, and verify removal plus scoped git status for `Inbox/{YYYY-MM-DD}/slack`, `Inbox/{YYYY-MM-DD}/attachments/slack`, and `.tmp`.

## Reporting

When the invoking cron request includes a silent sentinel instruction, return exactly `[SILENT]` only if there are zero qualifying messages, zero filesystem changes, and no material warnings. If there are warnings such as bot supplement rate limits, report the capture outcome normally.
