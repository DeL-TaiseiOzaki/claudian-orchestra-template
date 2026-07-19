---
name: google-tasks
description: "Use when you need to read the user's incomplete Google Tasks (to-dos) — lists open tasks across all task lists, optionally filtered by due date or list. Read-only; reuses the google-workspace OAuth token."
version: 1.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
required_credential_files:
  - path: google_token.json
    description: Shared Google OAuth2 token created by the google-workspace skill. Must include the tasks.readonly scope.
metadata:
  hermes:
    tags: [Google, Tasks, ToDo, Productivity, OAuth, ReadOnly]
    related_skills: [google-workspace]
---

# Google Tasks (read-only)

Lists the user's **incomplete** Google Tasks across all task lists.

Two backends are supported:

1. **Tracked <your-vault> script**: `scripts/list_tasks.py`, using the shared Hermes
   token at `~/.hermes/google_token.json` with `tasks.readonly`.
2. **Google Workspace CLI (`gws`)**: the upstream `@googleworkspace/cli` package
   now exposes the Google Tasks Discovery surface directly (`gws tasks ...`).
   Prefer `gws` when the user explicitly asks to use https://github.com/googleworkspace/cli
   or when they already have `~/.config/gws/client_secret.json` / `gws auth` set up.

Default to read-only scopes unless the user explicitly asks to create/update/delete tasks.

## Credentials (no separate auth)

This skill **reuses the google-workspace OAuth token** at
`~/.hermes/google_token.json` (resolved via `HERMES_HOME`). There is no
separate setup or token for Tasks. You only need the existing
google-workspace credentials, **plus the `tasks.readonly` scope** granted on
that token.

## Scope / re-consent requirement (IMPORTANT)

The bundled `google-workspace` setup does **not** request any Tasks scope by
default. Its `SCOPES` list (`scripts/setup.py` and `scripts/google_api.py`)
contains only Gmail / Calendar / Drive / Contacts / Sheets / Docs — **not**
`https://www.googleapis.com/auth/tasks` or `.../tasks.readonly`.

So unless the token was already authorized with a Tasks scope, the user must
**re-authorize** google-workspace with `tasks.readonly` added. If the scope is
missing, `list_tasks.py` exits non-zero with
`tasks unavailable: token lacks the tasks.readonly scope ...`.

### How to grant the Tasks scope (update-resilient)

**Do NOT edit the bundled `google-workspace` SCOPES** — that file is gitignored /
re-installable, so the edit is lost on reinstall. Instead use the tracked
[[.hermes/skills/mymemory/google-auth/SKILL.md]] authorizer, which already
includes `tasks.readonly` in its scope union and writes the SAME shared token:

1. In Google Cloud Console, enable the **Google Tasks API** for the OAuth
   client's project (https://console.cloud.google.com/apis/library).
2. (One-time, if not already done) store the client secret via the bundled
   skill: `python .../productivity/google-workspace/scripts/setup.py --client-secret <path>`.
3. Authorize with the full scope union (base + tasks) in one consent:

   ```bash
   GAUTH="python ${HERMES_HOME:-$HOME/.hermes}/skills/mymemory/google-auth/scripts/authorize.py"
   $GAUTH --auth-url      # open URL, authorize, copy the redirect URL (or code)
   $GAUTH --auth-code "<code-or-redirect-url>"
   $GAUTH --check         # AUTHENTICATED + lists granted scopes incl. tasks.readonly
   ```

After this, the bundled calendar/gmail/drive code AND this skill both work off
the one superset token. Future scopes: add them to `google-auth` (its
`EXTRA_SCOPES` or `scopes.txt`) and re-run the three commands.

## Usage

## Usage

### Bundled read-only helper

```bash
GTASKS="python ${HERMES_HOME:-$HOME/.hermes}/skills/mymemory/google-tasks/scripts/list_tasks.py"

# All incomplete tasks across every list
$GTASKS

# Only tasks due strictly before a date
$GTASKS --due-before 2026-06-10

# Only one named task list
$GTASKS --list "Work"

# Combine filters
$GTASKS --list "Work" --due-before 2026-06-10
```

### Direct `gws` CLI usage

When `gws` is authenticated with `https://www.googleapis.com/auth/tasks.readonly`, you can query Tasks directly:

```bash
# List task lists
gws tasks tasklists list --params '{"maxResults":10}'

# List incomplete tasks for a specific list
# Use an id returned by tasklists.list.
gws tasks tasks list --params '{"tasklist":"TASKLIST_ID","showCompleted":false,"maxResults":100}'
```

PowerShell users must escape JSON's inner double quotes when calling native `gws.exe`:

```powershell
gws tasks tasklists list --params '{\"maxResults\":10}'
gws tasks tasks list --params '{\"tasklist\":\"TASKLIST_ID\",\"showCompleted\":false,\"maxResults\":100}'
```

See `../google-auth/references/gws-cli-calendar-tasks.md` for the broader GWS CLI Calendar/Tasks workflow and pitfalls.

### `gws` CLI backend

Install if missing:

```bash
npm install -g @googleworkspace/cli
```

Place a Google OAuth **Desktop app** client JSON at:

```bash
mkdir -p "$HOME/.config/gws"
cp /path/to/client_secret.json "$HOME/.config/gws/client_secret.json"
```

Authenticate read-only Calendar + Tasks together:

```bash
gws auth login --scopes 'https://www.googleapis.com/auth/calendar.readonly,https://www.googleapis.com/auth/tasks.readonly'
```

Read task lists and tasks:

```bash
gws tasks tasklists list --params '{"maxResults":10}'
gws tasks tasks list --params '{"tasklist":"@default","showCompleted":false}'
```

Use `--dry-run` to verify URL/query construction without making API calls:

```bash
gws tasks tasklists list --dry-run --params '{"maxResults":10}'
gws tasks tasks list --dry-run --params '{"tasklist":"@default","showCompleted":false}'
```

### Direct `googleworkspace/cli` (`gws`) path

If the user asks specifically to use GWS CLI, the upstream `gws` command has
native Tasks support:

```bash
npm install -g @googleworkspace/cli
gws auth status

# Prefer narrow auth scopes for Tasks-only read access
gws auth login --scopes 'https://www.googleapis.com/auth/tasks.readonly'

# List task lists
gws tasks tasklists list --params '{"maxResults":10}'

# List incomplete tasks in the default task list
gws tasks tasks list --params '{"tasklist":"@default","showCompleted":false}'
```

For Calendar + Tasks together, see
`mymemory/google-auth/references/gws-cli-calendar-tasks.md`.


### Arguments

| Flag | Meaning |
|------|---------|
| `--due-before YYYY-MM-DD` | Keep only tasks with a due date strictly before this date. Tasks with no due date are excluded when this filter is set. |
| `--list "<title>"` | Restrict to a single task list matched by its exact title. Default: all lists. |

## Output

A JSON array on stdout:

```json
[
  {"title": "Send report", "due": "2026-06-09", "list": "Work", "status": "needsAction"},
  {"title": "Buy groceries", "due": null, "list": "Personal", "status": "needsAction"}
]
```

- `title` — task title (string)
- `due` — due date as `YYYY-MM-DD`, or `null` if the task has no due date
- `list` — title of the task list the task belongs to
- `status` — Google Tasks status (always `needsAction` here, since completed
  tasks are excluded)

## Errors

On auth / scope / API failure, the script prints a single line to **stderr**
prefixed `tasks unavailable: ...` and exits **non-zero**. Callers should treat
a non-zero exit as "Tasks data unavailable" and render a graceful marker rather
than failing the whole briefing.

| stderr message | Fix |
|----------------|-----|
| `no google-workspace token ...` | Store the client secret, then run [[.hermes/skills/mymemory/google-auth/SKILL.md]]. |
| `token lacks the tasks.readonly scope ...` | Re-run `mymemory/google-auth/scripts/authorize.py --auth-url` → `--auth-code` to consent to the full union. |
| `token is invalid ...` | Re-run [[.hermes/skills/mymemory/google-auth/SKILL.md]]. |
| `failed to query Google Tasks: ... 403 ...` | Enable the Google Tasks API in Cloud Console, or scope/consent still missing. |

## Dependencies

Same libraries as `google-workspace` — `google-api-python-client`,
`google-auth`, `google-auth-oauthlib`. No new dependency classes. If missing,
install them with **uv** in the Hermes Python environment:

```bash
uv pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```
