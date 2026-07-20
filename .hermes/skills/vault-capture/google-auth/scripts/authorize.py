#!/usr/bin/env python3
"""Update-resilient Google OAuth authorization for the your-vault.

WHY THIS EXISTS
---------------
The bundled ``google-workspace`` skill
(``${HERMES_HOME}/skills/productivity/...``)
hardcodes its own ``SCOPES`` and is gitignored / re-installable, so any edit
there is lost on reinstall. Google Tasks (and future features) need scopes
beyond those defaults. Editing the bundled ``setup.py`` is therefore NOT an
option.

Instead, this script is a TRACKED, custom authorization entry point. It
consents to the UNION of (bundled base scopes + our extras) in a single
consent screen and writes the SAME shared token file
(``${HERMES_HOME}/google_token.json``) in the SAME ``authorized_user`` JSON shape.
As a result:

  * The bundled calendar/gmail/drive code (``google_api.py``) keeps working,
    because the shared token is a strict SUPERSET of what it needs.
  * Our own ``list_tasks.py`` works too, because the token now also grants
    the Tasks scope.
  * Reinstalling the bundled skill does not break anything — this file lives
    in the tracked ``vault-capture`` area and is never overwritten.

This mirrors the bundled ``setup.py`` OAuth flow EXACTLY (google_auth_oauthlib
``Flow`` with a ``http://localhost:1`` redirect, PKCE auto-generated code
verifier, manual auth-url -> auth-code copy/paste) so the consent experience
and the on-disk token format are identical.

CLI (mirrors the bundled setup.py UX):
  authorize.py --auth-url            # Print the consent URL for the user
  authorize.py --auth-code "<code-or-redirect-url>"  # Exchange + write token
  authorize.py --revoke             # Revoke with Google and delete the token
  authorize.py --check              # Print AUTHENTICATED/NOT + granted scopes

NOTE: This script does NOT store the client secret. Reuse the bundled skill's
``--client-secret`` step once (it writes
``${HERMES_HOME}/google_client_secret.json``), or place that file yourself.
This script only reads it.
"""

from __future__ import annotations  # allow PEP 604 `X | None` on Python 3.9+

import argparse
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths — resolve HERMES_HOME independently (env var, else ~/.hermes) so this
# script does NOT import the bundled skill's private modules. Same files the
# bundled google-workspace skill reads/writes.
# ---------------------------------------------------------------------------
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
TOKEN_PATH = HERMES_HOME / "google_token.json"
CLIENT_SECRET_PATH = HERMES_HOME / "google_client_secret.json"
PENDING_AUTH_PATH = HERMES_HOME / "google_oauth_pending.json"

# ---------------------------------------------------------------------------
# Scope union. (a) BASE_SCOPES mirror the bundled google-workspace SCOPES so
# calendar/gmail/drive keep working. (b) EXTRA_SCOPES are what the vault needs
# on top of the bundle. Keep this list as the single place to extend later.
#
# Optional override: if a ``scopes.txt`` exists next to this script, every
# non-empty, non-``#`` line is treated as an ADDITIONAL scope and merged in.
# ---------------------------------------------------------------------------
BASE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
]

EXTRA_SCOPES = [
    # Google Tasks (read-only) — consumed by vault-capture/google-tasks/list_tasks.py
    "https://www.googleapis.com/auth/tasks.readonly",
]

# OAuth redirect for the manual code-copy flow. Google deprecated OOB, so the
# bundled skill uses a localhost redirect and asks the user to copy the code
# from the browser URL bar. We mirror that EXACTLY.
REDIRECT_URI = "http://localhost:1"

_SCOPES_FILE = Path(__file__).resolve().parent / "scopes.txt"


def _load_extra_scopes_file() -> list[str]:
    """Read optional additional scopes from scopes.txt (one per line)."""
    if not _SCOPES_FILE.exists():
        return []
    extra: list[str] = []
    for line in _SCOPES_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            extra.append(line)
    return extra


def _scopes() -> list[str]:
    """Return the de-duplicated UNION of base + extra (+ scopes.txt) scopes."""
    union: list[str] = []
    for scope in BASE_SCOPES + EXTRA_SCOPES + _load_extra_scopes_file():
        if scope not in union:
            union.append(scope)
    return union


SCOPES = _scopes()


def _configure_stdio() -> None:
    """Prefer UTF-8 for OAuth URLs / diagnostics when stdout or stderr is piped on Windows."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


_configure_stdio()


def _normalize_authorized_user_payload(payload: dict) -> dict:
    """Ensure the token JSON declares the authorized_user type (matches bundled)."""
    normalized = dict(payload)
    if not normalized.get("type"):
        normalized["type"] = "authorized_user"
    return normalized


def _ensure_deps() -> None:
    """Fail clearly if the (bundled, shared) Google deps are missing.

    No new dependencies: google-auth, google-auth-oauthlib,
    google-api-python-client — the same set the bundled skill installs.
    """
    try:
        import google_auth_oauthlib  # noqa: F401
        import google.oauth2.credentials  # noqa: F401
    except ImportError:
        print(
            "ERROR: Google auth libraries not installed. Install them via uv "
            "in the Hermes Python environment, e.g. "
            "uv pip install --python \"$HERMES_RUNTIME_PY\" "
            "google-api-python-client google-auth-oauthlib "
            "google-auth-httplib2.",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Pending-session persistence (PKCE) — same shape as the bundled setup.py.
# ---------------------------------------------------------------------------
def _save_pending_auth(*, state: str, code_verifier: str) -> None:
    """Persist the OAuth session bits needed for a later token exchange."""
    PENDING_AUTH_PATH.write_text(
        json.dumps(
            {
                "state": state,
                "code_verifier": code_verifier,
                "redirect_uri": REDIRECT_URI,
            },
            indent=2,
        )
    )


def _load_pending_auth() -> dict:
    """Load the pending OAuth session created by --auth-url."""
    if not PENDING_AUTH_PATH.exists():
        print("ERROR: No pending OAuth session found. Run --auth-url first.", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(PENDING_AUTH_PATH.read_text())
    except Exception as e:
        print(f"ERROR: Could not read pending OAuth session: {e}", file=sys.stderr)
        print("Run --auth-url again to start a fresh OAuth session.", file=sys.stderr)
        sys.exit(1)
    if not data.get("state") or not data.get("code_verifier"):
        print("ERROR: Pending OAuth session is missing PKCE data.", file=sys.stderr)
        print("Run --auth-url again to start a fresh OAuth session.", file=sys.stderr)
        sys.exit(1)
    return data


def _extract_code_and_state(code_or_url: str) -> tuple[str, str | None]:
    """Accept either a raw auth code or the full redirect URL pasted by the user."""
    if not code_or_url.startswith("http"):
        return code_or_url, None

    from urllib.parse import parse_qs, urlparse

    parsed = urlparse(code_or_url)
    params = parse_qs(parsed.query)
    if "code" not in params:
        print("ERROR: No 'code' parameter found in URL.", file=sys.stderr)
        sys.exit(1)
    state = params.get("state", [None])[0]
    return params["code"][0], state


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def get_auth_url() -> None:
    """Print the OAuth authorization URL covering the FULL scope union."""
    if not CLIENT_SECRET_PATH.exists():
        print(
            f"ERROR: No client secret at {CLIENT_SECRET_PATH}. Store it once via the "
            "bundled google-workspace setup.py --client-secret <path>.",
            file=sys.stderr,
        )
        sys.exit(1)

    _ensure_deps()
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRET_PATH),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        autogenerate_code_verifier=True,
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
    )
    _save_pending_auth(state=state, code_verifier=flow.code_verifier)
    # Print just the URL so an agent can extract it cleanly.
    print(auth_url)


def exchange_auth_code(code: str) -> None:
    """Exchange the authorization code for a token and write the shared token file."""
    if not CLIENT_SECRET_PATH.exists():
        print(
            f"ERROR: No client secret at {CLIENT_SECRET_PATH}. Store it once via the "
            "bundled google-workspace setup.py --client-secret <path>.",
            file=sys.stderr,
        )
        sys.exit(1)

    pending_auth = _load_pending_auth()
    raw_callback = code
    code, returned_state = _extract_code_and_state(code)
    if returned_state and returned_state != pending_auth["state"]:
        print("ERROR: OAuth state mismatch. Run --auth-url again to start a fresh session.", file=sys.stderr)
        sys.exit(1)

    _ensure_deps()
    from google_auth_oauthlib.flow import Flow
    from urllib.parse import parse_qs, urlparse

    # If the user pasted the full redirect URL, the granted scopes are in it
    # (user may have deselected some on the consent screen). Otherwise assume
    # the full requested union.
    granted_scopes = list(SCOPES)
    if isinstance(raw_callback, str) and raw_callback.startswith("http"):
        params = parse_qs(urlparse(raw_callback).query)
        scope_val = (params.get("scope") or [""])[0].strip()
        if scope_val:
            granted_scopes = scope_val.split()

    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRET_PATH),
        scopes=granted_scopes,
        redirect_uri=pending_auth.get("redirect_uri", REDIRECT_URI),
        state=pending_auth["state"],
        code_verifier=pending_auth["code_verifier"],
    )

    try:
        # Accept partial scopes — user may deselect some permissions.
        os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
        flow.fetch_token(code=code)
    except Exception as e:
        print(f"ERROR: Token exchange failed: {e}", file=sys.stderr)
        print("The code may have expired. Run --auth-url to get a fresh URL.", file=sys.stderr)
        sys.exit(1)

    creds = flow.credentials
    token_payload = _normalize_authorized_user_payload(json.loads(creds.to_json()))

    # Store only the scopes ACTUALLY granted (mirrors bundled setup.py). Writing
    # the requested scopes when fewer were granted makes later refresh fail with
    # invalid_scope.
    actually_granted = (
        list(creds.granted_scopes)
        if getattr(creds, "granted_scopes", None)
        else []
    )
    if actually_granted:
        token_payload["scopes"] = actually_granted
    elif granted_scopes != SCOPES:
        token_payload["scopes"] = granted_scopes
    else:
        token_payload["scopes"] = list(SCOPES)

    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(json.dumps(token_payload, indent=2))
    PENDING_AUTH_PATH.unlink(missing_ok=True)

    granted = token_payload.get("scopes", [])
    missing = [s for s in SCOPES if s not in granted]
    if missing:
        print("WARNING: token is missing some requested scopes:", file=sys.stderr)
        for s in missing:
            print(f"  - {s}", file=sys.stderr)
    print(f"OK: Authenticated. Token saved to {TOKEN_PATH}")
    print(f"Granted scopes ({len(granted)}):")
    for s in granted:
        print(f"  - {s}")


def check_auth() -> bool:
    """Print AUTHENTICATED/NOT plus granted scopes. Returns True if valid."""
    if not TOKEN_PATH.exists():
        print(f"NOT_AUTHENTICATED: No token at {TOKEN_PATH}")
        return False

    _ensure_deps()
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    try:
        # Don't pass scopes — the token may hold a subset; passing scopes forces
        # validation on refresh and can fail with invalid_scope.
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
    except Exception as e:
        print(f"TOKEN_CORRUPT: {e}")
        return False

    try:
        payload = json.loads(TOKEN_PATH.read_text())
    except Exception:
        payload = {}
    granted = payload.get("scopes") or payload.get("scope") or []
    if isinstance(granted, str):
        granted = granted.split()

    def _report() -> None:
        print(f"Granted scopes ({len(granted)}):")
        for s in granted:
            print(f"  - {s}")
        missing = [s for s in SCOPES if s not in granted]
        if missing:
            print(f"Missing {len(missing)} of the vault's requested scopes:")
            for s in missing:
                print(f"  - {s}")
            print("Re-run --auth-url -> --auth-code to grant the full union.")

    if creds.valid:
        print(f"AUTHENTICATED: Token valid at {TOKEN_PATH}")
        _report()
        return True

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            token_payload = _normalize_authorized_user_payload(json.loads(creds.to_json()))
            if granted:
                token_payload["scopes"] = granted
            TOKEN_PATH.write_text(
                json.dumps(token_payload, indent=2)
            )
            print(f"AUTHENTICATED: Token refreshed at {TOKEN_PATH}")
            _report()
            return True
        except Exception as e:
            print(f"REFRESH_FAILED: {e}")
            print("Re-run --auth-url -> --auth-code to re-authenticate.")
            return False

    print("TOKEN_INVALID: Re-run --auth-url -> --auth-code.")
    return False


def revoke() -> None:
    """Revoke the stored token with Google and delete it locally."""
    if not TOKEN_PATH.exists():
        print("No token to revoke.")
        return

    _ensure_deps()
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        import urllib.request

        urllib.request.urlopen(
            urllib.request.Request(
                f"https://oauth2.googleapis.com/revoke?token={creds.token}",
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            ),
            timeout=15,
        )
        print("Token revoked with Google.")
    except Exception as e:
        print(f"Remote revocation failed (token may already be invalid): {e}")

    TOKEN_PATH.unlink(missing_ok=True)
    PENDING_AUTH_PATH.unlink(missing_ok=True)
    print(f"Deleted {TOKEN_PATH}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update-resilient Google OAuth authorization for the your-vault "
        "(grants base + extra scopes in one consent, writes the shared token).",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--auth-url", action="store_true", help="Print the OAuth consent URL (full scope union)")
    group.add_argument("--auth-code", metavar="CODE", help="Exchange auth code (or pasted redirect URL) for a token")
    group.add_argument("--revoke", action="store_true", help="Revoke with Google and delete the stored token")
    group.add_argument("--check", action="store_true", help="Print AUTHENTICATED/NOT and the granted scopes")
    args = parser.parse_args()

    if args.auth_url:
        get_auth_url()
    elif args.auth_code:
        exchange_auth_code(args.auth_code)
    elif args.revoke:
        revoke()
    elif args.check:
        sys.exit(0 if check_auth() else 1)


if __name__ == "__main__":
    main()
