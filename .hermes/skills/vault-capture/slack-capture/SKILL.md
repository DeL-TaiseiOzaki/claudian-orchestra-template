---
name: slack-capture
description: "Capture Slack messages visible to the user into the your-vault or produce ad-hoc Slack message reports. Covers bot-token channel/DM history capture and user-token search.messages capture for cross-channel my-messages-today queries. Writes RAW per-channel daily digests to Inbox/{YYYY-MM-DD}/slack/{channel}.md — capture only, no routing, no DM-based sorting. Curation happens later in Claude Code. Intended to be invoked on-demand when the user issues a 取り込み instruction (typically from the Daily-note ジョブリスト). May also run from a cron if registered, but on-demand is the primary mode."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [vault, slack, capture, vault-capture]
    related_skills: [obsidian]
---

# slack-capture

Use this when the user asks to retrieve Slack messages, capture daily Slack logs, or answer queries like "今日の私の発言を取得して".

This is a **capture-only** skill: it writes RAW Slack material into `Inbox/{YYYY-MM-DD}/slack/{channel}.md` (one dated parent folder per day, one file per channel) or returns an ad-hoc report. There is **no routing, no channel→project mapping, and no DM-based sorting** — every relevant channel's daily digest lands in `Inbox/{date}/slack/`. Distilling/distributing these into Work/Others/Research is Claude Code's later curate step (via the `Daily/{date}.md` hub). Do not curate or rewrite note bodies here.

## Token modes

### Multi-workspace user-token-only capture

When the user wants to treat extra Slack workspaces as sub-workspace information sources, keep the primary Hermes Slack gateway on the main workspace and add one workspace-specific User OAuth token per source workspace (for example `SLACK_USER_TOKEN_WORKSPACE_B`). Do not require a bot for read-only capture if the user explicitly says bot is not needed.

For “all messages today” capture, use `search.messages` with `on:MM/DD/YYYY` as the baseline for all messages visible to that user token, then supplement with `conversations.list` + `conversations.history` for richer channel/file metadata. Group by channel and write one raw digest per channel under `Inbox/{YYYY-MM-DD}/slack/{channel}.md` (multi-workspace captures may prefix the workspace into the channel slug, e.g. `{workspace}-{channel}.md`, to keep them distinct within the day's `slack/` folder). See `references/multi-workspace-user-token-capture.md` for the manifest, config pattern, CLI shape, verification commands, and pitfalls.

### Bot token mode: event/channel/DM history

Use `SLACK_BOT_TOKEN` (`xoxb-...`) for Hermes gateway and for channels/DMs where the bot is allowed to read history.

Typical scopes:

- `chat:write`
- `app_mentions:read`
- `channels:history`
- `groups:history`
- `im:history`
- `im:read`
- `im:write`
- `users:read`
- `files:read` / `files:write` if attachments are captured

Pitfall: `conversations.list` may show public channels where the bot is not a member. `conversations.history` can still fail with `not_in_channel`. That is not a capture failure; it means the bot cannot see that channel until invited or granted access.

### User token mode: cross-channel search

Use `SLACK_USER_TOKEN` (`xoxp-...` or `xoxe.xoxp-...`) when the user wants a cross-channel search over messages visible to their own Slack account, especially "my messages today".

Required user scopes:

- `search:read`
- `users:read` for resolving `SLACK_ALLOWED_USERS` to a Slack username

Pitfall: Slack `search.messages` rejects bot tokens with `not_allowed_token_type`. Do not keep retrying with `SLACK_BOT_TOKEN`; ask the user to add a User OAuth Token to `.hermes/.env` as `SLACK_USER_TOKEN`.

## Setup checklist for user-token search

1. Open Slack App management: `https://api.slack.com/apps`.
2. Select the existing Hermes app (the one you created for this vault).
3. Go to OAuth & Permissions.
4. Add User Token Scopes: `search:read`, `users:read`.
5. Reinstall to Workspace.
6. Copy the User OAuth Token and add it to the active Hermes profile env file:

```text
SLACK_USER_TOKEN=xoxp-...
```

7. Restart/reload the Hermes process that needs the new env value.

## Ad-hoc "today's user messages" workflow

1. Load `.hermes/.env` and read:
   - `SLACK_USER_TOKEN`
   - `SLACK_ALLOWED_USERS` (target user id)
2. Call `users.info` with the user token to resolve the username.
3. Build local-date query variants:
   - `from:{username} after:{YYYY-MM-DD} before:{YYYY-MM-DD+1}`
   - `from:<@{user_id}> after:{YYYY-MM-DD} before:{YYYY-MM-DD+1}`
4. Call `search.messages` with `sort=timestamp`, `sort_dir=asc`, and dedupe by `channel.id + ts`.
5. Report channel, local time, and text. Do not print token values.

Reusable script: `scripts/slack_today_my_messages.py`.

## Daily / "run for yesterday" workflow (on-demand or cron)

When this skill is invoked with wording like "run it for yesterday" (either by an on-demand user instruction or by cron), treat it as a capture job for the previous local date (Asia/Tokyo unless the job says otherwise), not as an ad-hoc text-only report.

1. Resolve the target date explicitly from the live clock and record it in output/logs.
2. Use user-token search (`SLACK_USER_TOKEN`) for cross-channel authored messages and @mentions visible to the user.
3. Use bot-token channel/DM history (`SLACK_BOT_TOKEN`) only as a supplement for channels/DMs the bot can read. `not_in_channel` is expected; rate limits are partial-coverage warnings, not a reason to rewrite good captures with poorer data.
4. Dedupe by `channel.id + ts`, then group by channel and write one raw daily digest per channel to `Inbox/{YYYY-MM-DD}/slack/{channel}.md`. No routing, no channel→project lookup — every relevant channel lands in the day's `slack/` folder.
5. If digest files for the target date already exist, verify counts/content before overwriting. Preserve richer existing fields such as attachments, original mention display text, thread permalinks, and valid `mentions: []` frontmatter. Do not replace a richer existing digest with a simplified ad-hoc reconstruction.
6. If existing digest bodies are good but their frontmatter is stale (for example `source: "slack:daily:..."`, timestamp-valued `created`, or missing required fields), perform a **frontmatter-only repair** to the current Output spec. Preserve the message body byte-for-byte except for unavoidable newline normalization; do not re-fetch/rewrite content just to satisfy metadata.
7. Before finalizing, check that no temporary scripts/files remain and that final filesystem changes are either intentional new/updated captures or none.
8. For same-day captures ("today 00:00 to now", whether on-demand or via cron), use the same preservation/merge rules as yesterday re-runs: if today's digest already exists, repair frontmatter or append missing message entries without replacing richer existing bodies. If there are zero qualifying messages and no filesystem changes, report silence only when the invoking job explicitly requested a silent sentinel.
9. When the reusable script is insufficient and a one-off helper is needed, write it under a temporary path such as `.tmp/`, run it, then remove it and verify removal before finalizing. Never print Slack token values in script output or logs.

See `references/yesterday-cron-capture.md` for the preservation safeguards, `references/frontmatter-repair.md` for the frontmatter-only repair pattern, and `references/same-day-cron-capture.md` for same-day digest-writing capture details, bot-supplement rate-limit handling, and cleanup/reporting checks.

## 起動方法（on-demand 既定 / cron は任意）

**既定 = on-demand**：ユーザーが Daily ノートの `## 🤖 ジョブリスト` を見て「<該当 job> やって」と Claude に指示 → Claude が hermes に CLI で委譲（[[.claude/skills/hermes-query/SKILL.md]]）。

### 手動 invoke コマンド

> `hermes chat -q` のスキル指定は `-s <skill>`（`--skill` / `--workdir` というフラグは無い）。vault ルートに cd してから呼ぶ。日本語 Windows では呼び出し前に `PYTHONUTF8=1` を設定する（cp932 デコード起因の出力欠落防止 → [[.claude/skills/hermes-query/SKILL.md]]）。

```bash
cd "<vault root>"

# 当日分の Slack 取り込み（今日 00:00 から now まで）
hermes chat -q "Load the slack-capture skill and run it for today: capture Slack messages visible to the user (authored / mentioned / DM / private), grouped by channel, into Inbox/<today>/slack/{channel}.md. Capture only — no routing, no curated edits." -s slack-capture -Q --source claude-code

# 昨日分の Slack 取り込み（catch-all）
hermes chat -q "Load the slack-capture skill and run it for yesterday: capture Slack messages visible to the user (authored / mentioned / DM / private), grouped by channel, into Inbox/<yesterday>/slack/{channel}.md. Preserve richer existing digests; frontmatter-only repair if needed." -s slack-capture -Q --source claude-code
```

### Cron 登録（任意）

> cron による定期起動は**任意**（on-demand が既定）。定時 capture したい場合の典型は「21:00 same-day capture + 翌朝 07:00 catch-all」の 2 本立て。

```bash
# same-day capture（21:00）
hermes cron create "0 21 * * *" "Load the slack-capture skill and run it for today: capture Slack messages visible to the user (authored / mentioned / DM / private), grouped by channel, into Inbox/<today>/slack/{channel}.md. Capture only — no routing." --name slack-capture-today --skill slack-capture --workdir "<vault root>"

# 翌朝 catch-all（07:00）
hermes cron create "0 7 * * *" "Load the slack-capture skill and run it for yesterday: capture Slack messages visible to the user (authored / mentioned / DM / private), grouped by channel, into Inbox/<yesterday>/slack/{channel}.md. Preserve richer existing digests." --name slack-capture-yesterday --skill slack-capture --workdir "<vault root>"
```

## Self-edit boundary

> このスキルは **自分の SKILL.md / references / config を autonomous に編集しない**。実行中に drift / empirical finding を検知した場合（CLI 挙動変化、Slack API スキーマ drift、cron mode 運用学習など）は、対象 file を直接編集せず `Inbox/{YYYY-MM-DD}/clippings/hermes-obs-slack-capture.md` に observation/proposal note を新規作成する。frontmatter 必須：`affected_path` / `observed_at` / `evidence` / `proposed_change` / `source: "hermes:observation:slack-capture:<ISO8601>"`。詳細は [[.claude/rules/inbox-routing.md]] §7。

## Vault boundaries

- Raw capture target: `Inbox/{YYYY-MM-DD}/slack/` (one dated parent folder per day; create it only on a day Slack actually produces messages).
- One digest file per channel: `Inbox/{YYYY-MM-DD}/slack/{channel}.md`. No routing, no `slack-channel-map.yaml`, no `_unsorted/` — capture only.
- Do not write curated Work/Others/Daily notes from this skill. Distilling/distributing digests is Claude Code's later curate step.
- Do not edit Slack note bodies; this skill only writes/repairs digest files inside `Inbox/{date}/slack/`.

## Output spec (REQUIRED — single source of truth for digest files)

This section is the authoritative format every digest file written by this skill MUST conform to.
Mirrors `.claude/rules/inbox-routing.md` §5.3.

### Digest path & filename

Parent folder: `Inbox/{YYYY-MM-DD}/slack/` (the dated parent folder owns the date; filenames carry NO date prefix).

- Regular / private channel: `Inbox/{YYYY-MM-DD}/slack/{channel}.md` (drop `#`, keep slug as-is)
- DM: `Inbox/{YYYY-MM-DD}/slack/dm-{counterpart}.md` (counterpart = display name, slugified)

### Required frontmatter fields

```yaml
---
source: "slack:digest:{channel}:{YYYY-MM-DD}"     # MUST start with "slack:digest:" (NOT "slack:daily:")
                                                   # Use channel slug (e.g. "times_yourname"), NOT channel_id
channel: "#{channel}"                              # with "#" prefix
channel_id: "{Cxxxx}"                              # Slack channel id
is_dm: true | false
is_private: true | false                           # REQUIRED — true for private channels and DMs
participants: ["display_name_1", "display_name_2"]
user_authored: true | false                       # REQUIRED — did the user author at least one message in this digest
user_mentioned: true | false                      # REQUIRED — was the user @mentioned at least once
message_count: <int>                               # REQUIRED — number of qualifying messages in this digest
fetched_at: <ISO8601 +09:00>                       # REQUIRED — when the capture ran
created: {YYYY-MM-DD}                              # capture run date (Asia/Tokyo)
updated: {YYYY-MM-DD}                              # same as created on first write
---
```

> `source:` is a frontmatter signal string (identifier), NOT a filesystem path — keep it as `slack:digest:{channel-slug}:{date}` regardless of where the file lives.

### Forbidden / deprecated values

| Field | Forbidden | Use instead |
|---|---|---|
| `source` | `"slack:daily:..."` | `"slack:digest:{channel-slug}:{YYYY-MM-DD}"` |
| `source` | `"slack:digest:{channel_id}:..."` | `"slack:digest:{channel-slug}:..."` (slug, not id) |
| `created` | full ISO with time | `YYYY-MM-DD` only (timestamp belongs in `fetched_at`) |

### Thread-parent context (REQUIRED)

When a qualifying the user message is a thread reply (i.e. its Slack envelope has `thread_ts != ts`):

1. ALSO capture the thread parent message (the original post at `thread_ts`).
2. Capture any siblings (other replies in the same thread) that are immediately adjacent in time to the user's message, so the context is readable.
3. Mark each captured non-the user message with `reason: thread_context` (vs `authored` / `mentioned` for primary qualifications).
4. Order by `ts` ascending so the thread reads naturally.

Without thread parent context, a reply like "賛成です" is meaningless to the reader.

### Attachment download (REQUIRED — auth-aware)

Slack file URLs (`https://files.slack.com/...` and per-team file links) **require Slack token authentication** to download the real bytes. A naked `GET` without `Authorization: Bearer <token>` returns the Slack login HTML page (`<!DOCTYPE html>...`), which has been observed saved with a `.png` extension and is useless.

Required behavior:

1. Use `SLACK_BOT_TOKEN` (or `SLACK_USER_TOKEN` if files were shared in a context only the user can see) in the `Authorization: Bearer ...` header for ALL attachment downloads.
2. After download, validate magic bytes match the declared content-type:
   - PNG: `89 50 4E 47 0D 0A 1A 0A`
   - JPEG: `FF D8 FF`
   - GIF: `47 49 46 38`
   - PDF: `25 50 44 46`
3. If validation fails (e.g. the bytes start with `<!DOCTYPE html` or `<html`), DO NOT keep the file — log a one-line warning and write a placeholder pointer in the digest instead:
   ```
   - 📎 {filename} → ⚠️ download failed (auth or permission); permalink: {url}
   ```
4. Save valid attachments to `Inbox/{YYYY-MM-DD}/attachments/slack/{channel}/{ts}-{original-filename}` and link relatively from the digest.

## References

- `references/user-token-search.md` — `SLACK_USER_TOKEN` workaround for cross-channel `search.messages`.
- `references/multi-workspace-capture-cli.md` — pattern for keeping one Slack workspace as the Hermes gateway while using a Slack Web API based <your-vault> capture CLI for additional read-only workspaces.
- `references/yesterday-cron-capture.md` — preservation rules for re-runs (don't overwrite richer existing digests).
