# Multi-workspace user-token Slack capture

Session learning: for sub-workspaces where Hermes should not run a Slack bot, use a user-token-only Slack App plus a workspace-aware capture CLI. Keep the main Hermes Slack gateway pinned to the primary workspace, and treat other workspaces as read/search/capture sources.

## Slack App manifest shape

Use user scopes only; no bot scopes, Socket Mode, event subscriptions, slash commands, or app mentions.

```yaml
display_information:
  name: <your-vault> Slack Capture
  description: Capture Slack messages visible to the installing user into <your-vault>.
  background_color: "#2f3437"
oauth_config:
  scopes:
    user:
      - search:read
      - users:read
      - channels:read
      - channels:history
      - groups:read
      - groups:history
      - im:read
      - im:history
      - mpim:read
      - mpim:history
      - files:read
settings:
  org_deploy_enabled: false
  socket_mode_enabled: false
  token_rotation_enabled: false
```

## Config pattern

Store one env var per workspace, e.g. `SLACK_USER_TOKEN_YNLP`, and keep the token value out of prompts. Use a YAML config such as `.hermes/config/slack-workspaces.yaml`:

```yaml
workspaces:
  ynlp:
    display_name: yans-nlp
    team_id: T0A3AQMBL
    user_id: U0A7B205P6Y
    user_name: sg23174y
    user_token_env: SLACK_USER_TOKEN_YNLP
    bot_token_env: null
    # date-first layout: digests → Inbox/{date}/slack/, attachments → Inbox/{date}/attachments/slack/
    # workspace key is folded into the channel slug (e.g. ynlp-{channel}.md) to stay distinct within the day
    channel_prefix: ynlp
    timezone: Asia/Tokyo
    capture:
      all_day: true
      my_messages: true
      mentions: true
      files: true
```

## Retrieval strategy for “all messages today”

1. Run `auth.test` with the workspace token and record only non-secret identity fields: `team`, `team_id`, `user`, `user_id`, `url`.
2. Use `search.messages` with `on:MM/DD/YYYY` as the baseline for all messages visible to the user token that day. This can return channels that `conversations.history` will not cover when the user can search visible content without being in every listed conversation.
3. Supplement with `conversations.list` + `conversations.history` for the same date window (`oldest` / `latest`) to obtain richer metadata, files, and joined-conversation messages.
4. Dedupe by `channel id/name + ts`, group by channel, and write one digest per channel to `Inbox/{YYYY-MM-DD}/slack/<workspace>-{channel}.md` (fold the workspace key into the slug to keep workspaces distinct within the day's `slack/` folder).
5. For files, download with `Authorization: Bearer <user_token>` and validate magic bytes before saving. Reject Slack login HTML masquerading as images/files.

## Verification commands

```bash
python .hermes/scripts/slack_multi_capture.py auth-test --workspace ynlp
python .hermes/scripts/slack_multi_capture.py search --workspace ynlp --query 'on:06/13/2026' --max-pages 1 --print-limit 5
python .hermes/scripts/slack_multi_capture.py capture --workspace ynlp --date today --mode all-day
python -m py_compile .hermes/scripts/slack_multi_capture.py
```

Expected capture summary fields: `search_matches`, `history_channels_with_messages`, `files_written`, `messages_captured`, `attachments_downloaded`, `history_error_count`, and `output_dir`.

## Pitfalls

- Official Slack CLI is mainly for Slack app management/development, not broad message capture. Prefer a <your-vault>-specific Slack Web API CLI for recurring capture.
- Bot tokens are not required for sub-workspace read-only capture and can be omitted entirely when the user-token app has the necessary scopes.
- `search.messages` date filters are safest as `on:MM/DD/YYYY`; avoid relying only on `after:YYYY-MM-DD` / `before:YYYY-MM-DD`.
- `conversations.history` alone may under-capture “all visible messages”; use search as the baseline and history as enrichment.
