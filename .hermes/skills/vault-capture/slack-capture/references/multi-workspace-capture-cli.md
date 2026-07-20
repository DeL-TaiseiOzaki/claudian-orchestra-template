# Multi-workspace Slack capture CLI pattern

Use this when the user wants the primary workspace to remain the interactive Hermes Slack gateway while additional Slack workspaces are treated as read-only information sources.

## Key distinction

- Hermes Slack gateway configuration is primarily single-workspace via `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `SLACK_ALLOWED_USERS`, and home-channel env vars.
- For multiple *information-source* Slack workspaces, prefer a small <your-vault>-specific Slack Web API CLI over trying to use Slack's official CLI as the capture engine.
- Slack's official CLI is mainly for Slack app development and management: app creation, manifests, local/dev deploy flows, triggers, and workspace app connection. It is useful as setup/admin support, not as the main daily message retrieval layer.

## Recommended architecture

1. Keep the primary workspace (key `primary`) as the Hermes gateway workspace for interaction and notifications.
2. Register sub-workspaces as capture sources with workspace-keyed env vars.
3. Implement or use a capture CLI/script that calls Slack Web API directly.
4. Run it on-demand from the Daily job list. Existing legacy cron may remain transitional, but do not create a new job.
5. Save raw output to `Inbox/{YYYY-MM-DD}/slack/<workspace>-{channel}.md` (capture only; no routing); curate later with the core agent.

## Env var naming pattern

```env
SLACK_WORKSPACES=primary,secondary,client_a

# Main workspace may still also have standard Hermes gateway names:
SLACK_BOT_TOKEN=...
SLACK_APP_TOKEN=...
SLACK_USER_TOKEN=...
SLACK_HOME_CHANNEL_NAME=times_yourname

# Multi-workspace capture names:
SLACK_USER_TOKEN_WORKSPACE_A=xoxp-...
SLACK_BOT_TOKEN_WORKSPACE_A=xoxb-...

SLACK_USER_TOKEN_WORKSPACE_B=xoxp-...
SLACK_BOT_TOKEN_WORKSPACE_B=xoxb-...

SLACK_USER_TOKEN_CLIENT_A=xoxp-...
SLACK_BOT_TOKEN_CLIENT_A=xoxb-...
```

The user should not paste token values into chat. Ask only for workspace keys and env var names after they have placed secrets in `.hermes/.env`.

## Workspace config shape

A compact YAML config keeps scripts and on-demand prompts stable:

```yaml
workspaces:
  primary:
    display_name: Primary (gateway)
    user_token_env: SLACK_USER_TOKEN_WORKSPACE_A
    bot_token_env: SLACK_BOT_TOKEN_WORKSPACE_A
    default_channels: [times_yourname]
    capture:
      my_messages: true
      mentions: true
      keywords: []
    # date-first: digests → Inbox/{date}/slack/primary-{channel}.md (workspace key folded into slug)
    channel_prefix: primary

  workspace_b:
    display_name: Workspace B
    user_token_env: SLACK_USER_TOKEN_WORKSPACE_B
    bot_token_env: SLACK_BOT_TOKEN_WORKSPACE_B
    default_channels: []
    capture:
      my_messages: true
      mentions: true
      keywords: [your-name]
    # date-first: digests → Inbox/{date}/slack/workspace_b-{channel}.md (workspace key folded into slug)
    channel_prefix: workspace_b
```

Suggested path: `.hermes/config/slack-workspaces.yaml` or another profile-local config path.

## CLI command shape

Design the capture tool around explicit verbs:

```bash
uv run --no-project python .hermes/scripts/slack_multi_capture.py auth-test --all
uv run --no-project python .hermes/scripts/slack_multi_capture.py auth-test --workspace workspace_b
uv run --no-project python .hermes/scripts/slack_multi_capture.py capture --workspace workspace_b --date today --mode my-messages
uv run --no-project python .hermes/scripts/slack_multi_capture.py capture --workspace workspace_b --date today --mode mentions
uv run --no-project python .hermes/scripts/slack_multi_capture.py capture --all-workspaces --date yesterday --mode daily
uv run --no-project python .hermes/scripts/slack_multi_capture.py search --workspace primary 'in:#times_yourname from:me on:06/13/2026'
```

## API preference

Use user tokens for cross-channel search when possible:

- `search.messages` for authored messages, mentions, and keywords visible to the user.
- `users.info` / `auth.test` to verify identity and team.

Use bot tokens as a supplement for history where the bot has access:

- `conversations.list`
- `conversations.history`
- `conversations.replies`
- file download APIs

Do not retry `search.messages` with bot tokens after `not_allowed_token_type`; that API path needs a user token.

## User setup checklist to present

When explaining the user's work, keep it concise and action-oriented:

1. List sub-workspaces and assign stable keys (`workspace_b`, `client_a`, etc.).
2. Decide capture modes per workspace: my messages, mentions, channels, keywords, attachments.
3. Create or update a Slack App in each workspace.
4. Add User Token scopes first: `search:read`, `users:read`.
5. Add history/file scopes only if needed: `channels:read`, `channels:history`, `groups:read`, `groups:history`, `im:read`, `im:history`, `files:read`.
6. Reinstall the app to the workspace.
7. Store tokens in `.hermes/.env` using workspace-keyed env vars.
8. Share only workspace keys and env var names, not secrets.
9. Run `auth-test` and a one-workspace on-demand capture before enabling all-workspace mode.
10. Keep invocation on-demand from the Daily job list; do not add a new Hermes cron.

## Cron pattern

> Note: on-demand is the default trigger now (kicked from the Daily `## 🤖 ジョブリスト` on the user's instruction). Cron is transitional only — keep existing jobs running but do not register new ones. The job shapes below still describe the capture cadence regardless of how they are invoked.

Good first jobs:

- Evening capture: all workspaces, today, daily mode.
- Morning digest: summarize yesterday's raw captures.
- Lightweight alert: hourly search for mentions/urgent keywords only.

Avoid trying to make every sub-workspace an interactive Hermes Slack gateway unless the user explicitly wants bot conversations there. If they do, consider separate Hermes profiles or a custom multi-workspace gateway implementation.
