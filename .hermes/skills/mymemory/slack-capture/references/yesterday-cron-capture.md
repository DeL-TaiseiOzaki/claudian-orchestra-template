# Yesterday cron capture safeguards

Session context: cron invoked `slack-capture` with "run it for yesterday". The reusable script only handled "today's user messages", so an ad-hoc yesterday capture script was used to query Slack and verify/write daily digests.

> Trigger note: on-demand kick (from the Daily `## 🤖 ジョブリスト`) is the primary path now; cron is just one transitional trigger (existing jobs only, no new ones). The safeguards below apply the same way however it is invoked.

Useful pattern:

- Resolve the target date from the live clock in the intended local timezone (Asia/Tokyo for this vault).
- Combine `SLACK_USER_TOKEN` `search.messages` (cross-channel authored messages and mentions visible to the user) with `SLACK_BOT_TOKEN` `conversations.history` (bot-visible channel/DM history) when available.
- Dedupe messages by `channel.id + ts`, then group by channel.
- Write one digest per channel to `Inbox/{YYYY-MM-DD}/slack/{channel}.md`. Capture only — no routing, no channel→project map.
- Verify resulting digest files by counting `Inbox/{YYYY-MM-DD}/slack/*.md` files and `- Qualifying messages:` lines.

Pitfall found:

- A simplified ad-hoc reconstruction can overwrite richer existing digests and lose attachments or original mention display text. In the session, existing `Inbox/2026-06-05/slack/*.md` files already contained richer capture data; the attempted overwrite removed an attachment link and normalized mention text. The correct resolution was to restore the existing files and report verified counts instead of leaving downgraded changes.

Checklist before final response:

1. Existing target-date files checked? If yes, preserve richer existing content.
2. Any empty frontmatter lists (`mentions:`) accidentally introduced? Prefer valid `mentions: []` or populated list.
3. Temporary scripts removed?
4. `git status --short` (or equivalent) checked for unintended changes?
5. Report partial Slack API rate limits as caveats, not as total failure, if user-token search and existing captures provide adequate coverage.
