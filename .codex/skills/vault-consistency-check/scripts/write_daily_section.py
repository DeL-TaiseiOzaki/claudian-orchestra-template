"""Write or replace the consistency-check section in today's Daily note."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


SECTION_RE = re.compile(r"(?ms)^## 🔍 整合性チェック\s*\n.*?(?=^##\s|\Z)")
NIGHT_SECTION_RE = re.compile(r"(?ms)^## 🌙 夜の振り返り\s*\n.*?(?=^##\s|\Z)")


def derive_vault_root(script_file: Path) -> Path:
    """Derive the vault root from scripts/."""

    return script_file.resolve().parents[4]


def normalize_newlines(text: str) -> str:
    """Normalize text to LF newlines and a single trailing newline."""

    return "\n".join(text.replace("\r\n", "\n").replace("\r", "\n").splitlines()).strip("\n") + "\n"


def daily_note_path(vault_root: Path, target_date: date) -> Path:
    """Return the target Daily note path."""

    return vault_root / "Daily" / f"{target_date.isoformat()}.md"


def insert_after_night_section(document: str, section: str) -> str:
    """Insert a section after the night review block or at EOF."""

    match = NIGHT_SECTION_RE.search(document)
    section_block = f"{section.strip()}\n"
    if not match:
        base = document.rstrip("\n")
        return f"{base}\n\n{section_block}"
    before = document[: match.end()].rstrip("\n")
    after = document[match.end() :].lstrip("\n")
    if after:
        return f"{before}\n\n{section_block}\n{after}"
    return f"{before}\n\n{section_block}"


def write_daily_section(vault_root: Path, target_date: date, incoming: str) -> int:
    """Replace or insert the consistency-check section."""

    path = daily_note_path(vault_root, target_date)
    rel = f"Daily/{target_date.isoformat()}.md"
    if not path.exists():
        sys.stderr.write(f"WARN [Daily missing] {rel}\n")
        return 2
    document = path.read_text(encoding="utf-8-sig")
    section = normalize_newlines(incoming)
    if SECTION_RE.search(document):
        replacement = f"{section.strip()}\n\n"
        updated = SECTION_RE.sub(lambda _: replacement, document, count=1)
    else:
        updated = insert_after_night_section(document, section)
    serialized = normalize_newlines(updated)
    path.write_text(serialized, encoding="utf-8", newline="")
    roundtrip = path.read_text(encoding="utf-8-sig")
    if len(SECTION_RE.findall(roundtrip)) != 1:
        raise RuntimeError("consistency section count must be exactly 1 after write")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--vault-root", type=Path, default=derive_vault_root(Path(__file__)))
    return parser


def main() -> int:
    """Read section Markdown from stdin and write it into today's Daily note."""

    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass
    parser = build_parser()
    args = parser.parse_args()
    target_date = date.fromisoformat(args.date)
    incoming = sys.stdin.read()
    return write_daily_section(args.vault_root.resolve(), target_date, incoming)


if __name__ == "__main__":
    raise SystemExit(main())
