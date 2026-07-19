#!/usr/bin/env python3
"""Fetch today's Slack messages by SLACK_ALLOWED_USERS via Slack search.messages.

Requires SLACK_USER_TOKEN with user scopes search:read and users:read.
Reads env vars from the current process and, if present, ./.hermes/.env under cwd.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def load_local_env() -> None:
    for path in (Path(".hermes/.env"), Path(os.environ.get("HERMES_HOME", "")) / ".env"):
        if not path.exists() or path.is_dir():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = line.strip().strip("\ufeff")
            if not s or s.startswith("#") or "=" not in s:
                continue
            k, v = s.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def slack_api(token: str, method: str, params: dict[str, str] | None = None) -> dict:
    data = urllib.parse.urlencode(params or {}).encode()
    req = urllib.request.Request(
        f"https://slack.com/api/{method}",
        data=data,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"ok": False, "http_status": exc.code, "retry_after": exc.headers.get("Retry-After")}


def main() -> int:
    load_local_env()
    token = os.getenv("SLACK_USER_TOKEN")
    if not token:
        print("SLACK_USER_TOKEN is not set; add a Slack User OAuth Token with search:read and users:read.")
        return 2

    user_id = next((x.strip() for x in os.getenv("SLACK_ALLOWED_USERS", "").replace(";", ",").split(",") if x.strip()), "")
    if not user_id:
        print("SLACK_ALLOWED_USERS is not set; cannot identify the target Slack user.")
        return 2

    info = slack_api(token, "users.info", {"user": user_id})
    if not info.get("ok"):
        print("users.info failed:", json.dumps(info, ensure_ascii=False))
        return 1

    user = info.get("user") or {}
    username = user.get("name") or user.get("profile", {}).get("display_name") or user_id
    today = dt.datetime.now().astimezone().date()
    tomorrow = today + dt.timedelta(days=1)
    queries = [
        f"from:{username} after:{today.isoformat()} before:{tomorrow.isoformat()}",
        f"from:<@{user_id}> after:{today.isoformat()} before:{tomorrow.isoformat()}",
    ]

    seen: set[str] = set()
    matches: list[dict] = []
    last_error: dict | None = None
    for query in queries:
        res = slack_api(token, "search.messages", {"query": query, "sort": "timestamp", "sort_dir": "asc", "count": "100"})
        if not res.get("ok"):
            last_error = res
            continue
        for match in (res.get("messages") or {}).get("matches", []):
            key = f"{(match.get('channel') or {}).get('id')}:{match.get('ts')}"
            if key in seen:
                continue
            seen.add(key)
            matches.append(match)

    if not matches and last_error:
        print("search.messages failed:", json.dumps(last_error, ensure_ascii=False))
        return 1

    print(f"Slack messages by {username} ({user_id}) on {today.isoformat()}: {len(matches)}")
    for match in sorted(matches, key=lambda m: float(m.get("ts") or 0)):
        ts = float(match.get("ts") or 0)
        clock = dt.datetime.fromtimestamp(ts).astimezone().strftime("%H:%M:%S") if ts else "??:??:??"
        channel = (match.get("channel") or {}).get("name") or (match.get("channel") or {}).get("id") or "unknown"
        text = (match.get("text") or "").replace("\n", " ").strip()
        print(f"[{clock}] #{channel}: {text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
