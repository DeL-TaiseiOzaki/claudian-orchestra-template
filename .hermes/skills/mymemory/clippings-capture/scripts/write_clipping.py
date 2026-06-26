#!/usr/bin/env python3
"""Write a captured web clipping (e.g. a ChatGPT / Claude chat, or any web
page) into the your-vault under ``Inbox/{YYYY-MM-DD}/clippings/`` as raw markdown.

Reads ONE JSON object on stdin:
    {
      "source": "chatgpt" | "claude" | "web" | "manual",  # optional (default web)
      "url": "https://...",                                # optional
      "title": "...",                                       # optional (filename)
      "captured_at": "2026-06-03T09:00:00Z",                # optional (default now)
      "content": "# markdown ...",                          # REQUIRED (clip body)
      "tags": ["..."]                                        # optional
    }

Writes ``Inbox/{YYYY-MM-DD}/clippings/{slug}.md`` with frontmatter (the dated
parent folder owns the date, so the filename carries no date prefix), never
overwriting (adds ``-2``, ``-3`` ... on collision), and prints the path.

Capture single-writer: writes ONLY inside ``Inbox/{YYYY-MM-DD}/clippings/`` — it
never touches root ``Daily/`` or curated notes. Curation is a separate Claude
Code step (see Inbox/README.md).
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

VALID_SOURCES = {"chatgpt", "claude", "web", "manual"}


def _configure_stdio() -> None:
    """Prefer UTF-8 for paths / JSON when stdout or stderr is piped on Windows."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


_configure_stdio()


def _fail(message: str) -> None:
    print(f"clipping failed: {message}", file=sys.stderr)
    sys.exit(1)


def _looks_like_vault(path: Path) -> bool:
    """Return True only for a plausible your-vault root."""
    return (
        (path / "Inbox").is_dir()
        and ((path / "CLAUDE.md").is_file() or (path / ".obsidian").exists())
    )


def _vault_root() -> Path:
    """Resolve the vault root without silently writing outside the vault.

    Prefer an explicit OBSIDIAN_VAULT_PATH. Otherwise, accept the current
    working directory or HERMES_HOME's parent only if it looks like the vault.
    This avoids treating a normal profile-scoped ~/.hermes as if ~/ were the
    vault root.
    """
    env = os.environ.get("OBSIDIAN_VAULT_PATH")
    if env:
        root = Path(env).expanduser().resolve()
        if _looks_like_vault(root):
            return root
        _fail(f"OBSIDIAN_VAULT_PATH does not look like a vault root: {root}")

    cwd = Path.cwd().resolve()
    if _looks_like_vault(cwd):
        return cwd

    home = os.environ.get("HERMES_HOME")
    if home:
        root = Path(home).expanduser().resolve().parent
        if _looks_like_vault(root):
            return root

    _fail("cannot resolve vault root (set OBSIDIAN_VAULT_PATH to <your-vault>)")
    raise SystemExit(1)  # unreachable; for type-checkers


def _slug(title: str) -> str:
    """Filesystem-friendly slug; keeps unicode word chars (incl. Japanese)."""
    s = title.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)        # drop punctuation/symbols
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:60].strip("-") or "clip"


def _parse_date(raw) -> date:
    if not raw:
        return date.today()
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).date()
    except Exception:
        return date.today()


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception as e:
        _fail(f"invalid JSON on stdin: {e}")
    if not isinstance(payload, dict):
        _fail("payload must be a JSON object")

    content = payload.get("content")
    if not content or not str(content).strip():
        _fail("missing required 'content'")

    source = (str(payload.get("source", "")).strip().lower() or "web")
    if source not in VALID_SOURCES:
        source = "web"
    url = str(payload.get("url", "") or "")
    title = str(payload.get("title", "") or "").strip()
    d = _parse_date(payload.get("captured_at"))

    raw_tags = payload.get("tags") or []
    if not isinstance(raw_tags, list):
        raw_tags = [str(raw_tags)]
    tagset = ["clipping", source] + [str(t) for t in raw_tags]
    seen: set[str] = set()
    tags_final = [t for t in tagset if not (t in seen or seen.add(t))]

    # Date-first layout: the dated parent folder owns the date, so the
    # filename carries NO date prefix (Inbox/{YYYY-MM-DD}/clippings/{slug}.md).
    out_dir = _vault_root() / "Inbox" / d.isoformat() / "clippings"
    out_dir.mkdir(parents=True, exist_ok=True)

    base = _slug(title or source)
    fm_title = title or f"{source} clip {d.isoformat()}"
    lines = [
        "---",
        f"title: {json.dumps(fm_title, ensure_ascii=False)}",
        f"source: {json.dumps(source, ensure_ascii=False)}",
        f"created: {d.isoformat()}",
    ]
    if url:
        lines.append(f"url: {json.dumps(url, ensure_ascii=False)}")
    lines.append('status: "inbox"')
    lines.append(
        "tags: [" + ", ".join(json.dumps(t, ensure_ascii=False) for t in tags_final) + "]"
    )
    lines.append("---")

    text = "\n".join(lines) + "\n\n" + str(content).rstrip() + "\n"
    n = 1
    while True:
        suffix = "" if n == 1 else f"-{n}"
        path = out_dir / f"{base}{suffix}.md"
        try:
            with path.open("x", encoding="utf-8", newline="\n") as f:
                f.write(text)
            print(str(path))
            return
        except FileExistsError:
            n += 1


if __name__ == "__main__":
    main()
