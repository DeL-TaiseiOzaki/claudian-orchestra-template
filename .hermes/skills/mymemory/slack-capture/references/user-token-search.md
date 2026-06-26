# Slack user-token search notes

Session learning: Slack `search.messages` is the right path for cross-channel queries such as "today's messages by the user", but it requires a User OAuth Token. A bot token returns `not_allowed_token_type` even when the bot can otherwise read DMs/channels.

## Observed API behavior

- `auth.test` with `SLACK_BOT_TOKEN` can succeed for the Hermes bot.
- `conversations.open` + `conversations.history` works for the bot DM with the user.
- `conversations.list` may return public channels where `is_member=false`; history reads will not work there until the bot is invited or granted access.
- `search.messages` with `SLACK_BOT_TOKEN` returns:

```text
error: not_allowed_token_type
```

## Durable workaround

Add a User OAuth Token to the active Hermes profile env file:

```text
SLACK_USER_TOKEN=<Slack User OAuth Token>
```

The Slack app needs User Token Scopes:

- `search:read`
- `users:read`

Then use `users.info` to resolve `SLACK_ALLOWED_USERS` to username and call `search.messages` with a local-date query such as:

```text
from:{username} after:{YYYY-MM-DD} before:{YYYY-MM-DD+1}
```

Also try the mention form and dedupe results:

```text
from:<@{user_id}> after:{YYYY-MM-DD} before:{YYYY-MM-DD+1}
```

Dedupe by `channel.id + ts`, sort by timestamp ascending, and print only time/channel/text. Never echo token values.
