# Yesterday cron capture safeguards

Covers the "run it for yesterday" invocation of `slack-capture`. The reusable script only handles "today's user messages", so a yesterday capture typically needs an ad-hoc query to verify/write daily digests.

> Trigger note: on-demand kick (from the Daily `## 🤖 ジョブリスト`) is the primary path now; cron is just one transitional trigger (existing jobs only, no new ones). The safeguards below apply the same way however it is invoked.

Useful pattern:

- Resolve the target date from the live clock in the intended local timezone (Asia/Tokyo for this vault).
- Combine `SLACK_USER_TOKEN` `search.messages` (cross-channel authored messages and mentions visible to the user) with `SLACK_BOT_TOKEN` `conversations.history` (bot-visible channel/DM history) when available.
- Dedupe messages by `channel.id + ts`, then group by channel.
- Write one digest per channel to `Inbox/{YYYY-MM-DD}/slack/{channel}.md`. Capture only — no routing, no channel→project map.
- Before changing an existing digest, search `Daily/{YYYY-MM-DD}.md` for its exact source wikilink. If linked, ownership has handed off to the core and Hermes must skip it unchanged.
- Verify resulting digest files by counting `Inbox/{YYYY-MM-DD}/slack/*.md` files and `- Qualifying messages:` lines.

Pitfall found:

- A simplified ad-hoc reconstruction can overwrite richer existing digests and lose attachments or original mention display text. If the target date's `Inbox/{date}/slack/*.md` files already contain richer capture data, an overwrite silently removes attachment links and normalizes mention text. The correct resolution is to restore/keep the existing files and report verified counts instead of leaving downgraded changes.

Checklist before final response:

1. Daily handoff link checked? If present, skip the existing digest unchanged.
2. Existing unlinked target-date files checked? If yes, preserve richer existing content.
3. Any empty frontmatter lists (`mentions:`) accidentally introduced? Prefer valid `mentions: []` or populated list.
4. Temporary scripts removed?
5. `git status --short` (or equivalent) checked for unintended changes?
6. Report partial Slack API rate limits as caveats, not as total failure, if user-token search and existing captures provide adequate coverage.
