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
   token at `${HERMES_HOME}/google_token.json` with `tasks.readonly`.
2. **Google Workspace CLI (`gws`)**: the upstream `@googleworkspace/cli` package
   now exposes the Google Tasks Discovery surface directly (`gws tasks ...`).
   Prefer `gws` when the user explicitly asks to use https://github.com/googleworkspace/cli
   or when they already have `~/.config/gws/client_secret.json` / `gws auth` set up.

Default to read-only scopes unless the user explicitly asks to create/update/delete tasks.

## Credentials (no separate auth)

This skill **reuses the google-workspace OAuth token** at
`${HERMES_HOME}/google_token.json`. There is no
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
[[.hermes/skills/vault-capture/google-auth/SKILL.md]] authorizer, which already
includes `tasks.readonly` in its scope union and writes the SAME shared token:

1. In Google Cloud Console, enable the **Google Tasks API** for the OAuth
   client's project (https://console.cloud.google.com/apis/library).
2. Resolve the Hermes runtime Python as shown below. Then, if needed, store the
   client secret via the bundled skill: `"$HERMES_RUNTIME_PY" "$HERMES_HOME/skills/productivity/google-workspace/scripts/setup.py" --client-secret <path>`.
3. Authorize with the full scope union (base + tasks) in one consent:

   ```bash
   GAUTH="$HERMES_RUNTIME_PY ${HERMES_HOME:-$HOME/.hermes}/skills/vault-capture/google-auth/scripts/authorize.py"
   $GAUTH --auth-url      # open URL, authorize, copy the redirect URL (or code)
   $GAUTH --auth-code "<code-or-redirect-url>"
   $GAUTH --check         # AUTHENTICATED + lists granted scopes incl. tasks.readonly
   ```

After this, the bundled calendar/gmail/drive code AND this skill both work off
the one superset token. Future scopes: add them to `google-auth` (its
`EXTRA_SCOPES` or `scopes.txt`) and re-run the three commands.

## Usage

The Google libraries live in the Hermes runtime. Resolve its interpreter
explicitly; do not derive it from `command -v hermes`:

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
if [ -n "${HERMES_PYTHON:-}" ] && [ -x "$HERMES_PYTHON" ]; then
  HERMES_RUNTIME_PY="$HERMES_PYTHON"
elif [ -x "$HERMES_HOME/hermes-agent/venv/bin/python" ]; then
  HERMES_RUNTIME_PY="$HERMES_HOME/hermes-agent/venv/bin/python"
elif [ -x "$HERMES_HOME/hermes-agent/venv/Scripts/python.exe" ]; then
  HERMES_RUNTIME_PY="$HERMES_HOME/hermes-agent/venv/Scripts/python.exe"
else
  echo "Hermes runtime Python not found; set HERMES_PYTHON to its absolute path" >&2
  exit 1
fi
```

This explicit runtime call is the narrow exception to the vault's normal `uv`
rule because these helpers reuse Hermes-installed Google packages and tokens.

### Bundled read-only helper

```bash
GTASKS="$HERMES_RUNTIME_PY ${HERMES_HOME:-$HOME/.hermes}/skills/vault-capture/google-tasks/scripts/list_tasks.py"

# All incomplete tasks across every list
$GTASKS

# Only tasks due strictly before a date
$GTASKS --due-before 2026-06-10

# Only one named task list
$GTASKS --list "Work"

# Combine filters
$GTASKS --list "Work" --due-before 2026-06-10
```

### Optional direct `gws` query

`inbox-daily-capture` uses `list_tasks.py`; `gws` is not its Tasks backend. Use
the direct CLI only when the user explicitly selects it for a live read or
diagnostic and has authenticated the read-only Tasks scope:

```bash
gws auth status
gws tasks tasklists list --params '{"maxResults":10}'
gws tasks tasks list --params '{"tasklist":"@default","showCompleted":false,"maxResults":100}'
```

PowerShell users must escape JSON's inner double quotes when calling `gws.exe`.
Installation, OAuth, multi-account handling, and `--dry-run` probes are kept in
`../google-auth/references/gws-cli-calendar-tasks.md`.


### Arguments

| Flag | Meaning |
|------|---------|
| `--due-before YYYY-MM-DD` | Keep only tasks with a due date strictly before this date. Tasks with no due date are excluded when this filter is set. |
| `--list "<title>"` | Restrict to a single task list matched by its exact title. Default: all lists. |

## Output

A JSON array on stdout:

```json
[
  {"id": "task-1", "title": "Send report", "due": "2026-06-09", "list_id": "list-1", "list": "Work", "status": "needsAction"},
  {"id": "task-2", "title": "Buy groceries", "due": null, "list_id": "list-2", "list": "Personal", "status": "needsAction"}
]
```

- `id` — task ID used for `source: gtasks:task:<id>` provenance
- `title` — task title (string)
- `due` — due date as `YYYY-MM-DD`, or `null` if the task has no due date
- `list_id` — owning task-list ID
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
| `no google-workspace token ...` | Store the client secret, then run [[.hermes/skills/vault-capture/google-auth/SKILL.md]]. |
| `token lacks the tasks.readonly scope ...` | Re-run `vault-capture/google-auth/scripts/authorize.py --auth-url` → `--auth-code` to consent to the full union. |
| `token is invalid ...` | Re-run [[.hermes/skills/vault-capture/google-auth/SKILL.md]]. |
| `failed to query Google Tasks: ... 403 ...` | Enable the Google Tasks API in Cloud Console, or scope/consent still missing. |

## Dependencies

Same libraries as `google-workspace` — `google-api-python-client`,
`google-auth`, `google-auth-oauthlib`. No new dependency classes. If missing,
install them with **uv** in the Hermes Python environment:

```bash
uv pip install --python "$HERMES_RUNTIME_PY" google-api-python-client google-auth-oauthlib google-auth-httplib2
```
