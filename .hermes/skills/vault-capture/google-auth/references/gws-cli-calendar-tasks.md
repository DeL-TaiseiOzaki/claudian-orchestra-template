# GWS CLI OAuth for optional Calendar

Use this when a Calendar account cannot expose a private ICS URL and the user
explicitly selects Google Workspace CLI (`gws`,
https://github.com/googleworkspace/cli). `inbox-daily-capture` uses the tracked
Hermes Python helper for Tasks; direct `gws` Tasks commands below are optional
and only for an explicitly requested live read or diagnostic.

## Install / inspect

```bash
npm install -g @googleworkspace/cli
gws --version
gws auth status
gws calendar --help
```

`gws auth status` expects its OAuth Desktop client JSON at:

```text
~/.config/gws/client_secret.json
```

On Windows Git Bash this resolves to:

```text
C:\Users\<your-user>\.config\gws\client_secret.json
```

## Manual OAuth client path

If the user creates a Desktop OAuth client manually in Google Cloud Console:

1. Enable APIs in the target project:
   - Google Calendar API (`calendar-json.googleapis.com`)
   - Google Tasks API (`tasks.googleapis.com`) only if direct Tasks diagnostics
     were explicitly selected
2. Configure OAuth consent screen. If app is Testing, add the user's Google account as a test user.
3. Create OAuth Client ID with Application type = Desktop app.
4. Download the JSON and copy it into place:

```bash
mkdir -p "$HOME/.config/gws"
cp /path/to/client_secret.json "$HOME/.config/gws/client_secret.json"
```

Optional: if Hermes Python wrappers should also share the same client secret, copy it to the active Hermes profile too:

```bash
cp /path/to/client_secret.json "${HERMES_HOME:-$PWD/.hermes}/google_client_secret.json"
```

## Authenticate Calendar with a minimal read-only scope

```bash
gws auth login --scopes 'https://www.googleapis.com/auth/calendar.readonly'
```

This prints a browser URL and waits on a localhost callback. Send the exact URL to the user if running from an agent/CLI environment and ask them to authenticate in the browser. Keep the process alive until callback completes.

For an explicitly requested direct Tasks diagnostic, re-authenticate with the
additional read-only scope and inspect the Tasks command surface:

```bash
gws auth login --scopes 'https://www.googleapis.com/auth/calendar.readonly,https://www.googleapis.com/auth/tasks.readonly'
gws tasks --help
```

Do not request Calendar or Tasks write scopes in this read-only flow.

## Multi-account checks

When the user asks whether the GWS Calendar target accounts are set up, do
**not** inspect `gcloud auth list` — that reports Google Cloud CLI identities,
not the accounts that `gws` uses for Calendar capture.

For `@googleworkspace/cli` 0.22.x, account selection is config-directory based:

```bash
# personal Calendar target
unset GOOGLE_WORKSPACE_CLI_CONFIG_DIR
gws auth status

# additional (e.g. work) Calendar target
GOOGLE_WORKSPACE_CLI_CONFIG_DIR="$HOME/.config/gws-work" gws auth status
```

Convention:

- default `~/.config/gws` → personal account (e.g. `your-personal@gmail.com`)
- `~/.config/gws-<name>` via `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` → each additional account (e.g. `you@your-org.example.com`)

If an additional config dir is absent, create it and copy the same Desktop OAuth client JSON used by default gws:

```bash
mkdir -p "$HOME/.config/gws-work"
cp -f /path/to/client_secret.json "$HOME/.config/gws-work/client_secret.json"
GOOGLE_WORKSPACE_CLI_CONFIG_DIR="$HOME/.config/gws-work" \
  gws auth login --scopes 'https://www.googleapis.com/auth/calendar.readonly'
```

If default gws says `Token has been expired or revoked`, re-run `gws auth login --scopes ...` without overriding `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` and choose the personal account.

## Verification commands

Run the verification once per config dir, with the relevant `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` exported/omitted:

```bash
gws auth status
gws calendar +agenda --today --timezone Asia/Tokyo
```

Only when direct Tasks diagnostics were explicitly selected:

```bash
gws tasks tasklists list --params '{"maxResults":10}'
gws tasks tasks list --params '{"tasklist":"@default","showCompleted":false}'
```

Dry-run probes that do not require auth completion:

```bash
gws calendar events list --dry-run --params '{"calendarId":"primary","timeMin":"2026-06-06T00:00:00+09:00","timeMax":"2026-06-07T00:00:00+09:00","singleEvents":true,"orderBy":"startTime"}'
```

Optional Tasks diagnostic dry runs:

```bash
gws tasks tasklists list --dry-run --params '{"maxResults":10}'
gws tasks tasks list --dry-run --params '{"tasklist":"@default","showCompleted":false}'
```

Expected dry-run endpoints:

- Calendar events: `https://www.googleapis.com/calendar/v3/calendars/primary/events`
- Optional Tasks tasklists: `https://tasks.googleapis.com/tasks/v1/users/@me/lists`
- Optional default task list tasks: `https://tasks.googleapis.com/tasks/v1/lists/%40default/tasks`
