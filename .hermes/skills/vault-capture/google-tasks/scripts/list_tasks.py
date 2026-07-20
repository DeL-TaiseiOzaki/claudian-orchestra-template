#!/usr/bin/env python3
"""Google Tasks (read-only) listing CLI for the Hermes Agent.

Reuses the SAME OAuth credentials/token managed by the bundled
``google-workspace`` skill (``${HERMES_HOME}/google_token.json``). No separate
authentication is required — but the existing token must include the
``tasks.readonly`` scope. If it does not, re-run the tracked
``vault-capture/google-auth/scripts/authorize.py`` flow (see SKILL.md).

Read-only: this script never creates, updates, or deletes tasks.

Usage:
  "$HERMES_PYTHON" list_tasks.py [--due-before YYYY-MM-DD] [--list "<tasklist title>"]

Output:
  A JSON array on stdout:
    [{"id": str, "title": str, "due": "YYYY-MM-DD"|null,
      "list_id": str, "list": str, "status": str}, ...]

On any auth/scope/API error, exits non-zero and prints a single clear line
to stderr so callers can show a graceful "tasks unavailable" marker.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

# Share the bundled google-workspace OAuth token (no separate auth). Resolve
# HERMES_HOME independently (env var, else ~/.hermes) so this script does not
# couple to the vendored skill's private modules or its folder depth.
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
TOKEN_PATH = HERMES_HOME / "google_token.json"

# Read-only Tasks scope. The shared google-workspace token must already grant
# this scope (re-consent required otherwise — see SKILL.md).
SCOPES = ["https://www.googleapis.com/auth/tasks.readonly"]


def _configure_stdio() -> None:
    """Prefer UTF-8 for JSON / diagnostics when stdout or stderr is piped on Windows."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


_configure_stdio()


def _fail(message: str) -> None:
    """Print a one-line error to stderr and exit non-zero."""
    print(f"tasks unavailable: {message}", file=sys.stderr)
    sys.exit(1)


def _normalize_authorized_user_payload(payload: dict) -> dict:
    normalized = dict(payload)
    if not normalized.get("type"):
        normalized["type"] = "authorized_user"
    return normalized


def _stored_token_scopes() -> list[str]:
    """Return scopes actually present in the stored token (mirrors google_api.py)."""
    try:
        data = json.loads(TOKEN_PATH.read_text())
    except Exception:
        return list(SCOPES)
    scopes = data.get("scopes")
    if isinstance(scopes, list) and scopes:
        return scopes
    return list(SCOPES)


def get_credentials():
    """Load and refresh credentials from the shared google-workspace token file.

    Mirrors google_api.get_credentials(): refresh on expiry and save back.
    """
    if not TOKEN_PATH.exists():
        _fail(
            f"no google-workspace token at {TOKEN_PATH} — run "
            "vault-capture/google-auth/scripts/authorize.py after storing the client secret"
        )

    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    stored_scopes = _stored_token_scopes()
    if not any("tasks" in s for s in stored_scopes):
        _fail(
            "token lacks the tasks.readonly scope — re-run "
            "vault-capture/google-auth/scripts/authorize.py --auth-url then --auth-code"
        )

    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), stored_scopes)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_payload = _normalize_authorized_user_payload(json.loads(creds.to_json()))
            token_payload["scopes"] = stored_scopes
            TOKEN_PATH.write_text(
                json.dumps(token_payload, indent=2)
            )
    except Exception as e:
        _fail(f"credential load/refresh failed: {e}")

    if not creds.valid:
        _fail("token is invalid — re-run vault-capture/google-auth/scripts/authorize.py")
    return creds


def build_service():
    # Check auth first so a missing token produces the intended actionable
    # message even when Google API client libraries are not installed yet.
    creds = get_credentials()
    try:
        from googleapiclient.discovery import build
    except ImportError:
        _fail(
            "Google API client libraries are not installed — install via uv: "
            "uv pip install --python \"$HERMES_RUNTIME_PY\" "
            "google-api-python-client google-auth-oauthlib "
            "google-auth-httplib2"
        )

    return build("tasks", "v1", credentials=creds)


def _parse_due(raw: str | None) -> str | None:
    """Google Tasks 'due' is an RFC3339 timestamp; return the date portion."""
    if not raw:
        return None
    # e.g. "2026-06-10T00:00:00.000Z" -> "2026-06-10"
    return raw[:10]


def list_tasks(args) -> None:
    try:
        service = build_service()
        tasklists = []
        page_token = None
        while True:
            resp = (
                service.tasklists()
                .list(maxResults=100, pageToken=page_token)
                .execute()
            )
            tasklists.extend(resp.get("items", []))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
    except Exception as e:
        _fail(f"failed to query Google Tasks: {e}")

    due_before: date | None = None
    if args.due_before:
        try:
            due_before = date.fromisoformat(args.due_before)
        except ValueError:
            _fail(f"--due-before must be YYYY-MM-DD, got {args.due_before!r}")

    output: list[dict] = []
    for tl in tasklists:
        list_title = tl.get("title", "")
        if args.list and list_title != args.list:
            continue

        try:
            # showCompleted=False returns only incomplete tasks.
            page_token = None
            while True:
                resp = (
                    service.tasks()
                    .list(
                        tasklist=tl["id"],
                        showCompleted=False,
                        showHidden=False,
                        maxResults=100,
                        pageToken=page_token,
                    )
                    .execute()
                )
                for task in resp.get("items", []):
                    if task.get("status") == "completed":
                        continue
                    due = _parse_due(task.get("due"))
                    if due_before is not None:
                        if due is None or date.fromisoformat(due) >= due_before:
                            continue
                    output.append(
                        {
                            "id": task.get("id", ""),
                            "title": task.get("title", ""),
                            "due": due,
                            "list_id": tl.get("id", ""),
                            "list": list_title,
                            "status": task.get("status", ""),
                        }
                    )
                page_token = resp.get("nextPageToken")
                if not page_token:
                    break
        except Exception as e:
            _fail(f"failed to list tasks in {list_title!r}: {e}")

    print(json.dumps(output, indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List incomplete Google Tasks (read-only) for Hermes."
    )
    parser.add_argument(
        "--due-before",
        default="",
        help="Only include tasks due strictly before this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--list",
        default="",
        help="Restrict to a single task list by its title (default: all lists).",
    )
    args = parser.parse_args()
    list_tasks(args)


if __name__ == "__main__":
    main()
