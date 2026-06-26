---
name: google-auth
description: Use when you need to authorize (or re-authorize) Google OAuth for the your-vault with ALL required scopes in one consent — including scopes beyond the bundled google-workspace defaults (e.g. Google Tasks). Run this instead of the bundled setup.py so the shared token survives bundled-skill reinstalls.
version: 1.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [google, oauth, authorization, scopes, tasks, calendar, gmail]
    related_skills: [google-workspace, google-tasks]
---

# google-auth — Update-resilient Google OAuth for <your-vault>

## Why this skill exists

The bundled `google-workspace` skill lives under
`.hermes/skills/productivity/google-workspace/` which is **gitignored and
re-installable** — any edit to its `setup.py` / `google_api.py` is **lost on
reinstall**. Those bundled files **hardcode their `SCOPES`**, and the vault now
needs scopes beyond them (Google Tasks, and more later).

This skill provides a **tracked** authorization entry point
(`scripts/authorize.py`) that:

- Consents to the **UNION** of (bundled base scopes + our extras) in a single
  consent screen.
- Writes the **same** shared token file `~/.hermes/google_token.json` in the
  **same** `authorized_user` JSON shape the bundled skill expects.
- **Survives bundled reinstalls** (it lives in `mymemory/`, which is tracked
  and never overwritten).

Because the shared token becomes a strict **superset**:

- The bundled `google_api.py` (calendar / gmail / drive / sheets / docs /
  contacts) keeps working unchanged.
- `mymemory/google-tasks/list_tasks.py` works because the token also grants the
  Tasks scope.

## Canonical scope set

Base (mirrors bundled `google-workspace`):

```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.modify
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/contacts.readonly
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/documents
```

Extra (vault additions):

```
https://www.googleapis.com/auth/tasks.readonly
```

The union is defined at the top of `scripts/authorize.py` (`BASE_SCOPES` +
`EXTRA_SCOPES`). To add a scope later, edit `EXTRA_SCOPES`, or drop an optional
`scripts/scopes.txt` (one scope per line, `#` comments allowed) next to the
script — those lines are merged in automatically.

## Prerequisites

1. **Cloud Console**: enable the relevant APIs for your OAuth client —
   in particular the **Google Tasks API** (in addition to Gmail / Calendar /
   Drive / Sheets / Docs / People that the bundle already uses). Without the
   Tasks API enabled, consent succeeds but task calls fail.
2. **Client secret**: this skill reads `~/.hermes/google_client_secret.json`
   but does **not** store it. Store it once via the bundled skill:
   `python .hermes/skills/productivity/google-workspace/scripts/setup.py --client-secret /path/to/client_secret.json`
3. **Deps** (shared, no new deps): `google-api-python-client`,
   `google-auth-oauthlib`, `google-auth-httplib2`. If missing, install them
   with **uv** in the Hermes Python environment:
   `uv pip install google-api-python-client google-auth-oauthlib google-auth-httplib2`

## Commands

Run **this** `authorize.py` (not the bundled `setup.py`) to grant every scope
the vault needs in one consent:

```bash
# 1. Print the consent URL (covers base + extra scopes). Open it in a browser.
python .hermes/skills/mymemory/google-auth/scripts/authorize.py --auth-url

# 2. Authorize in the browser. You land on a localhost page that fails to load
#    (expected) — copy the FULL redirect URL from the address bar, or just the
#    `code` value, and exchange it:
python .hermes/skills/mymemory/google-auth/scripts/authorize.py --auth-code "<paste code OR full redirect URL>"

# 3. Verify: prints AUTHENTICATED and the granted scope list.
python .hermes/skills/mymemory/google-auth/scripts/authorize.py --check

# Revoke + delete the shared token if needed:
python .hermes/skills/mymemory/google-auth/scripts/authorize.py --revoke
```

Pasting the **full redirect URL** in step 2 is recommended: it lets the script
record exactly which scopes you granted (in case you deselected any on the
consent screen).

## Notes

- **OAuth flow**: identical to the bundled `setup.py` — `google_auth_oauthlib`
  `Flow` with `redirect_uri=http://localhost:1`, auto-generated PKCE verifier,
  manual auth-url → auth-code copy/paste. Pending session state is stored in
  `~/.hermes/google_oauth_pending.json` between the two steps.
- **Token format**: `authorized_user` JSON at `~/.hermes/google_token.json`,
  with a `scopes` list of the actually-granted scopes — exactly what the
  bundled `google_api.py` and `list_tasks.py` read.
- **After a bundled reinstall**: nothing to redo. The token already on disk
  keeps working. Only re-run the commands above if you add new scopes or the
  token is revoked/expired without a refresh token.
- Re-running `--auth-url` → `--auth-code` is also how you **add a new scope**:
  edit `EXTRA_SCOPES` (or `scopes.txt`), then re-consent.

## GWS CLI direct path

When the user explicitly wants to use `googleworkspace/cli` (`gws`) for Calendar
or Tasks, prefer the direct `gws` setup/login flow instead of only the Hermes
Python wrapper. See `references/gws-cli-calendar-tasks.md` for install,
side-effect-safe setup, narrow Calendar/Tasks scopes, and verified command
shapes.

Key pitfalls:

- `gws auth setup --project <PROJECT_ID>` can enable many Workspace APIs and create OAuth credentials in the selected GCP project. Always run `--dry-run` first and get explicit approval before the non-dry-run setup.
- For <your-vault> Calendar/Tasks account checks, inspect `gws auth status` for each `GOOGLE_WORKSPACE_CLI_CONFIG_DIR`, not `gcloud auth list`. `gcloud` accounts are Cloud CLI identities and do not tell which Google account `gws` will query.
- <your-vault> convention: default `~/.config/gws` is the lab/personal account; Secondary uses `~/.config/gws-secondary` selected with `GOOGLE_WORKSPACE_CLI_CONFIG_DIR`. See `references/gws-cli-calendar-tasks.md` for the exact multi-account verification and setup commands.

## Related
## References

- `references/gws-cli-calendar-tasks.md` — direct `@googleworkspace/cli` setup for Calendar + Tasks: OAuth Desktop client JSON placement, minimal scopes, login flow, and verification commands.

## Related

- `mymemory/google-tasks` — consumes the `tasks.readonly` scope this grants.
- bundled `google-workspace` — calendar/gmail/drive; keeps working off the same
  superset token.
