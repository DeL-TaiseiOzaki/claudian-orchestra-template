"""Check your-vault vault consistency and print Markdown or JSON findings."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    import frontmatter  # type: ignore
except ImportError:  # pragma: no cover
    frontmatter = None

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


HEADING = "## 🔍 整合性チェック"
CHECKED_COUNT = 8
SECTION_RE = re.compile(r"(?ms)^## 🔍 整合性チェック\s*\n.*?(?=^##\s|\Z)")
WIKILINK_RE = re.compile(
    r"""
    \[\[
    (?P<body>
      (?:
        [^\[\]\\|#]
        |\\.
        |\|(?=[^\]])
        |\#(?=[^\]])
      )+
    )
    \]\]
    """,
    re.VERBOSE,
)
HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
CODEMAP_RE = re.compile(r"\[([^\]]+)\]\((https://github\.com/[^)]+)\)")
TASKS_HEADING_RE = re.compile(r"^### ✅ 今日のタスク(?:（Google Tasks）)?\s*$", re.MULTILINE)
TASK_LINE_RE = re.compile(r"^- \[(?P<mark>[ xX])\]\s*(?P<title>.*?)\s*$")
CHECK_NAMES = (
    "Broken wikilinks",
    "Frontmatter schema violation",
    "Inbox stagnation",
    "Today Tasks drift",
    "Code-Map repo health",
    "Work logs project field",
    "Submodule dirty / commit drift",
    "Structure drift",
)
NOTE_ROOTS = (
    "Daily",
    "Inbox",
    "Work",
    "Research",
    "Others",
    "Maps",
    "Meta",
    "Archive",
)
SCAN_EXCLUDED_FILENAMES = {"README.md", "CLAUDE.md", "AGENTS.md"}
SCAN_EXCLUDED_PREFIXES = ("Research/",)
# Wikilink resolution walks the WHOLE vault (broader than the content-scan scope)
# so links to README/CLAUDE/root files/non-md assets are not false-flagged.
RESOLUTION_EXCLUDED_DIRS = {".git", ".trash", ".tmp", ".uv-cache"}
INBOX_ROOT = "Inbox"
INBOX_DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
INBOX_KNOWN_SOURCE_DIRS = frozenset(
    {"daily", "slack", "code", "mtgs", "clippings", "chat-logs", "attachments"}
)
INBOX_STAGNATION_THRESHOLD_DAYS = 7
DEFAULT_SCHEMA_RULES: dict[str, Any] = {
    "common_required": ["title", "type", "status", "tags", "created", "updated"],
    # Optional but recognized fields. `resource` is the OKF-aligned canonical pointer
    # to the system of record (URL / vault path / SoR id). See vault-metadata.md
    # "resource（任意・OKF 整合）" and Meta/{your-meta-project}/proposal.md.
    "optional_known_fields": ["resource"],
    "type_enum": [
        "note",
        "log",
        "deliverable",
        "paper",
        "experiment",
        "reference",
        "idea",
        "exploration",
        "activity",
    ],
    "status_enum": ["draft", "in-progress", "completed", "archived"],
    "work_required": ["project", "client"],
    "work_project_enum": ["PROJ_A", "PROJ_B", "PROJ_X", "PROJ_C", "PROJ_D", "PROJ_E", "PROJ_F"],  # PROJ_X=archived 2026-06-23 (kept valid for Archive/Work/PROJ_X notes)
    "daily_required": {"type": "log"},
    "archive_required": ["archived", "archived_from"],
    "paper_required": ["theme", "arxiv_id", "paper_authors", "paper_date", "paper_url"],
    "experiment_required": ["theme", "experiment_id", "objective", "hypothesis", "reproducible"],
    "work_required_paths": [
        r"^Work/(PROJ_A|PROJ_B|PROJ_X|PROJ_C|PROJ_D|PROJ_E|PROJ_F)/logs/[^/]+\.md$",
        r"^Work/(PROJ_A|PROJ_B|PROJ_X|PROJ_C|PROJ_D|PROJ_E|PROJ_F)/meetings/[^/]+\.md$",
        r"^Work/(PROJ_A|PROJ_B|PROJ_X|PROJ_C|PROJ_D|PROJ_E|PROJ_F)/deliverables/[^/]+\.md$",
        r"^Work/(PROJ_A|PROJ_B|PROJ_X|PROJ_C|PROJ_D|PROJ_E|PROJ_F)/(project|team|status)\.md$",
    ],
    "work_excluded_paths": [
        r"^Work/(PROJ_A|PROJ_B|PROJ_X|PROJ_C|PROJ_D|PROJ_E|PROJ_F)/references/",
        r"^Work/(PROJ_A|PROJ_B|PROJ_X|PROJ_C|PROJ_D|PROJ_E|PROJ_F)/sources/",
        r"^Work/(PROJ_A|PROJ_B|PROJ_X|PROJ_C|PROJ_D|PROJ_E|PROJ_F)/code/",
    ],
    "inbox_source_paths": [r"^Inbox/\d{4}-\d{2}-\d{2}/.*\.md$"],
    "inbox_type_enum": ["capture"],
    "inbox_status_enum": ["inbox"],
    "inbox_common_required": ["title", "type", "status", "tags", "created", "updated"],
    "structure_expected_root_dirs": [
        "Inbox",
        "Daily",
        "Work",
        "Research",
        "Others",
        "Maps",
        "Meta",
        "Archive",
        "Templates",
    ],
    "structure_system_root_prefixes": [
        ".git",
        ".claude",
        ".codex",
        ".hermes",
        ".claudian",
        ".trash",
        ".tmp",
        ".uv-cache",
        ".obsidian*",
    ],
    "structure_required_dirs": [
        "Work/PROJ_A/meetings",
        "Work/PROJ_A/docs",
        "Work/PROJ_A/code",
        "Work/PROJ_A/deliverables",
        "Work/PROJ_A/logs",
        "Work/PROJ_A/sources",
        "Work/PROJ_A/references",
        "Work/PROJ_B/meetings",
        "Work/PROJ_B/docs",
        "Work/PROJ_B/code",
        "Work/PROJ_B/deliverables",
        "Work/PROJ_B/logs",
        "Work/PROJ_B/sources",
        "Work/PROJ_B/references",
        # PROJ_X archived 2026-06-23 -> Archive/Work/PROJ_X/ (removed from required dirs; still valid in work_project_enum)
        "Work/PROJ_C/meetings",
        "Work/PROJ_C/docs",
        "Work/PROJ_C/code",
        "Work/PROJ_C/deliverables",
        "Work/PROJ_C/logs",
        "Work/PROJ_C/sources",
        "Work/PROJ_C/references",
        "Work/PROJ_D/meetings",
        "Work/PROJ_D/docs",
        "Work/PROJ_D/code",
        "Work/PROJ_D/deliverables",
        "Work/PROJ_D/logs",
        "Work/PROJ_D/sources",
        "Work/PROJ_D/references",
        "Work/PROJ_E/meetings",
        "Work/PROJ_E/docs",
        "Work/PROJ_E/code",
        "Work/PROJ_E/deliverables",
        "Work/PROJ_E/logs",
        "Work/PROJ_E/sources",
        "Work/PROJ_E/references",
        "Others/Ideas",
        "Others/Activities",
        "Others/Activities/Ecosystem",
        "Others/Learning",
        "Maps/views",
        "Daily",
        "Meta",
        "Archive",
        "Templates",
    ],
    "structure_scan_roots": [
        "Inbox",
        "Daily",
        "Work",
        "Others",
        "Maps",
        "Meta",
        "Archive",
    ],
    "structure_submodule_excludes": ["Research"],
    "structure_nonmd_allowed": {
        "allowed_path_prefixes": ["Inbox/attachments"],
        "allowed_dir_names": ["_assets", "sources", "attachments"],
        "allowed_filenames": [".gitkeep"],
        "allowed_ext_under_root": [{"ext": ".base", "root": "Maps"}],
        "allowed_ext_anywhere": [".canvas"],
    },
}
SEVERITY_ORDER = {"ERROR": 0, "WARN": 1, "OK": 2}


@dataclass(frozen=True)
class Finding:
    """One consistency check result."""

    tag: str
    check_name: str
    path: str | None
    message: str


@dataclass(frozen=True)
class TaskItem:
    """A checkbox parsed from today's Daily note."""

    title: str
    checked: bool


def derive_vault_root(script_file: Path) -> Path:
    """Derive the vault root from scripts/."""

    return script_file.resolve().parents[4]


def normalize_rel(path: Path, root: Path) -> str:
    """Return a relative POSIX path."""

    return path.resolve().relative_to(root.resolve()).as_posix()


def note_domain_path(rel_path: str) -> bool:
    """Return whether the path belongs to note-carrying vault domains."""

    return any(rel_path == root or rel_path.startswith(f"{root}/") for root in NOTE_ROOTS)


def scannable_note_path(rel_path: str) -> bool:
    """Return whether a path is an in-scope curated note for consistency scans."""

    if not note_domain_path(rel_path):
        return False
    if rel_path.startswith(SCAN_EXCLUDED_PREFIXES):
        return False
    parts = rel_path.split("/")
    if parts[-1] in SCAN_EXCLUDED_FILENAMES:
        return False
    return not any(part.startswith(".") for part in parts)


def iter_markdown_files(vault_root: Path) -> list[Path]:
    """List markdown files in note-carrying domains."""

    files: list[Path] = []
    for root_name in NOTE_ROOTS:
        root = vault_root / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.md"):
            rel = normalize_rel(path, vault_root)
            if path.is_file() and scannable_note_path(rel):
                files.append(path)
    return sorted(set(files))


def read_text(path: Path) -> str:
    """Read UTF-8 text from a file."""

    return path.read_text(encoding="utf-8")


def load_schema_rules(vault_root: Path) -> dict[str, Any]:
    """Load schema rules from YAML when available, otherwise use defaults."""

    path = vault_root / ".claude/skills/vault-consistency-check/references/schema_rules.yaml"
    if not path.exists() or yaml is None:
        return DEFAULT_SCHEMA_RULES
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data
    return DEFAULT_SCHEMA_RULES


def extract_yaml_block(text: str) -> tuple[str | None, str]:
    """Extract a leading YAML frontmatter block and return the remainder."""

    match = re.match(r"(?s)^---\n(.*?)\n---\n?", text)
    if not match:
        return None, text
    return match.group(1), text[match.end() :]


def parse_minimal_yaml(block: str) -> dict[str, Any]:
    """Parse a minimal YAML subset without external dependencies."""

    data: dict[str, Any] = {}
    current_key: str | None = None
    current_list: list[str] | None = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") and current_key is not None and current_list is not None:
            current_list.append(line[4:].strip().strip('"').strip("'"))
            continue
        current_key = None
        current_list = None
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            data[key] = []
            current_key = key
            current_list = data[key]
            continue
        if value.startswith("[") and value.endswith("]"):
            items = [item.strip().strip('"').strip("'") for item in value[1:-1].split(",") if item.strip()]
            data[key] = items
            continue
        cleaned = value.strip('"').strip("'")
        if cleaned in {"true", "false"}:
            data[key] = cleaned == "true"
        else:
            data[key] = cleaned
    return data


def load_frontmatter_and_body(path: Path) -> tuple[dict[str, Any], str]:
    """Load frontmatter and markdown body with layered fallbacks."""

    text = read_text(path)
    if frontmatter is not None:
        post = frontmatter.loads(text)
        return dict(post.metadata), post.content
    block, body = extract_yaml_block(text)
    if block is None:
        return {}, text
    if yaml is not None:
        loaded = yaml.safe_load(block) or {}
        if isinstance(loaded, dict):
            return loaded, body
    return parse_minimal_yaml(block), body


def run_command(args: list[str], cwd: Path, timeout: int = 15) -> subprocess.CompletedProcess[str]:
    """Run a subprocess with captured UTF-8 output."""

    return subprocess.run(
        args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
        check=False,
    )


def git_changed_paths(vault_root: Path) -> set[str]:
    """Collect recently changed paths from git, with a fallback query."""

    commands = [
        ["git", "diff", "--name-only", "HEAD@{1.day.ago}", "HEAD"],
        ["git", "log", "--since=1.day.ago", "--name-only", "--pretty=format:"],
    ]
    for command in commands:
        try:
            result = run_command(command, vault_root)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
        if result.returncode != 0:
            continue
        paths = {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}
        if paths or command is commands[-1]:
            return paths
    return set()


def recent_mtime_paths(vault_root: Path) -> set[str]:
    """Collect files changed within the last 24 hours by mtime."""

    cutoff = datetime.now(timezone.utc) - timedelta(days=1)
    paths: set[str] = set()
    for path in vault_root.rglob("*"):
        if not path.is_file():
            continue
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
        except OSError:
            continue
        if mtime >= cutoff:
            paths.add(normalize_rel(path, vault_root))
    return paths


def touched_today_paths(vault_root: Path) -> set[str]:
    """Build the touched-today path set."""

    return git_changed_paths(vault_root) | recent_mtime_paths(vault_root)


def finding_message(description: str, suggestion: str) -> str:
    """Format a finding message with the mandated suffix."""

    return f"{description}提案: {suggestion}（提案のみ・auto-fix なし）。"


def markdown_files_for_mode(vault_root: Path, mode: str, touched: set[str]) -> list[Path]:
    """Return markdown files to inspect for note-content checks."""

    all_files = iter_markdown_files(vault_root)
    if mode == "full":
        return all_files
    touched_files = {
        (vault_root / rel)
        for rel in touched
        if rel.endswith(".md") and scannable_note_path(rel) and (vault_root / rel).is_file()
    }
    return sorted(touched_files)


def normalize_obsidian_name(value: str) -> str:
    """Normalize a wikilink target for loose Obsidian matching."""

    normalized = value.replace("\\", "/").strip()
    if normalized.endswith(".md"):
        normalized = normalized[:-3]
    normalized = normalized.strip("/")
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.casefold()


def parse_wikilink_body(body: str) -> tuple[str, str | None, str | None]:
    """Split a wikilink body into target, header, and alias."""

    # Obsidian writes the alias separator as `\|` inside tables; treat it like `|`.
    interim = body.replace(r"\|", "|").replace(r"\#", "\x00HASH")
    target_alias = interim.split("|", 1)
    target_part = target_alias[0]
    alias = target_alias[1].replace("\x00HASH", "#").strip() if len(target_alias) > 1 else None
    target_header = target_part.split("#", 1)
    target = target_header[0].replace("\x00HASH", "#").strip()
    header = target_header[1].replace("\x00HASH", "#").strip() if len(target_header) > 1 else None
    return target, header, alias


def build_resolution_index(vault_root: Path) -> dict[str, list[Path]]:
    """Index every vault file (md and non-md) for wikilink resolution.

    Deliberately broader than the content-scan scope: includes root-level files,
    README/CLAUDE/AGENTS, Meta/, submodule contents, and non-md assets.
    """

    index: dict[str, list[Path]] = {}

    def add(path: Path) -> None:
        rel = normalize_rel(path, vault_root)
        if path.suffix == ".md":
            keys = {normalize_obsidian_name(path.stem), normalize_obsidian_name(rel[:-3])}
        else:
            keys = {normalize_obsidian_name(path.name), normalize_obsidian_name(rel)}
        for key in keys:
            index.setdefault(key, []).append(path)

    for entry in vault_root.iterdir():
        if entry.is_file():
            add(entry)
            continue
        if entry.name in RESOLUTION_EXCLUDED_DIRS or entry.name.startswith(".obsidian"):
            continue
        for path in entry.rglob("*"):
            if path.is_file():
                add(path)
    return index


def resolve_target(target: str, current_file: Path, index: dict[str, list[Path]]) -> tuple[str, Path | None]:
    """Resolve a wikilink target by loose path/stem matching."""

    key = normalize_obsidian_name(target)
    candidates = index.get(key, [])
    if not candidates:
        return "missing", None
    if len(candidates) == 1:
        return "ok", candidates[0]
    nearby = [path for path in candidates if path.parent == current_file.parent]
    if len(nearby) == 1:
        return "ok", nearby[0]
    # Obsidian prefers the shortest path when a bare name is ambiguous
    # (e.g. [[README.md]] resolves to the vault-root README, not domain READMEs).
    min_depth = min(len(path.parts) for path in candidates)
    shallowest = [path for path in candidates if len(path.parts) == min_depth]
    if len(shallowest) == 1:
        return "ok", shallowest[0]
    return "ambiguous", None


def slugify_header(text: str) -> str:
    """Normalize a markdown heading for comparison."""

    return re.sub(r"\s+", " ", text.strip()).casefold()


def header_exists(md_text: str, wanted: str) -> bool:
    """Return whether a heading exists in a markdown document."""

    headers = {slugify_header(match.group(2)) for match in HEADER_RE.finditer(md_text)}
    return slugify_header(wanted) in headers


def check_broken_wikilinks(vault_root: Path, mode: str, touched: set[str]) -> list[Finding]:
    """Check for missing or ambiguous wikilinks in scoped markdown files."""

    candidates = markdown_files_for_mode(vault_root, mode, touched)
    index = build_resolution_index(vault_root)
    findings: list[Finding] = []
    for path in candidates:
        rel = normalize_rel(path, vault_root)
        text = read_text(path)
        for match in WIKILINK_RE.finditer(text):
            raw = match.group(0)
            target, header, _alias = parse_wikilink_body(match.group("body"))
            if not target or target.endswith("/") or target.startswith("."):
                continue
            status, resolved = resolve_target(target, path, index)
            if status == "missing":
                findings.append(
                    Finding(
                        "ERROR",
                        "Broken wikilinks",
                        rel,
                        finding_message(
                            f"`{raw}` の参照先が解決できません。",
                            "対象ノート名または見出し表記を確認してください",
                        ),
                    )
                )
                continue
            if status == "ambiguous":
                findings.append(
                    Finding(
                        "ERROR",
                        "Broken wikilinks",
                        rel,
                        finding_message(
                            f"`{raw}` の参照先が曖昧です。",
                            "より短く一意に解決できるパスか正式なノート名に書き換えてください",
                        ),
                    )
                )
                continue
            if header and resolved is not None and not header_exists(read_text(resolved), header):
                findings.append(
                    Finding(
                        "ERROR",
                        "Broken wikilinks",
                        rel,
                        finding_message(
                            f"`{raw}` の見出しが見つかりません。",
                            "対象ノート内の見出し表記を確認してください",
                        ),
                    )
                )
    if findings:
        return findings
    if mode == "light" and not candidates:
        message = finding_message("対象ノートがないためこの回のリンク確認はスキップしました。", "追加対応は不要です")
    else:
        message = finding_message("対象ノートの wikilink に未解決参照は見つかりませんでした。", "追加対応は不要です")
    return [Finding("OK", "Broken wikilinks", None, message)]


def path_matches_any(rel_path: str, patterns: list[str]) -> bool:
    """Return whether a relative path matches any regex pattern."""

    return any(re.match(pattern, rel_path) for pattern in patterns)


def is_inbox_source(rel_path: str, rules: dict[str, Any]) -> bool:
    """Return True if rel_path matches any pattern in rules['inbox_source_paths']."""

    for pattern in rules.get("inbox_source_paths", []) or []:
        if re.match(pattern, rel_path):
            return True
    return False


def validate_frontmatter(rel_path: str, meta: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    """Validate frontmatter against schema rules."""

    errors: list[str] = []
    if is_inbox_source(rel_path, rules):
        for key in rules.get("inbox_common_required", []):
            if key not in meta:
                errors.append(f"required field missing: {key}")
        if meta.get("type") not in rules.get("inbox_type_enum", []):
            errors.append(f"invalid inbox type: {meta.get('type')}")
        if meta.get("status") not in rules.get("inbox_status_enum", []):
            errors.append(f"invalid inbox status: {meta.get('status')}")
        return errors
    for key in rules["common_required"]:
        if key not in meta:
            errors.append(f"required field missing: {key}")
    if meta.get("type") not in rules["type_enum"]:
        errors.append(f"invalid type: {meta.get('type')}")
    if meta.get("status") not in rules["status_enum"]:
        errors.append(f"invalid status: {meta.get('status')}")
    if rel_path.startswith("Daily/") and meta.get("type") != rules["daily_required"]["type"]:
        errors.append(f"daily note must have type: {rules['daily_required']['type']}")
    if rel_path.startswith("Archive/"):
        for key in rules["archive_required"]:
            if key not in meta:
                errors.append(f"archive field missing: {key}")
    if meta.get("type") == "paper":
        for key in rules["paper_required"]:
            if key not in meta:
                errors.append(f"paper field missing: {key}")
    if meta.get("type") == "experiment":
        for key in rules["experiment_required"]:
            if key not in meta:
                errors.append(f"experiment field missing: {key}")
    if rel_path.startswith("Work/"):
        if path_matches_any(rel_path, rules["work_excluded_paths"]):
            return errors
        if path_matches_any(rel_path, rules["work_required_paths"]):
            for key in rules["work_required"]:
                if key not in meta:
                    errors.append(f"work field missing: {key}")
            if meta.get("project") not in rules["work_project_enum"]:
                errors.append(f"invalid work project: {meta.get('project')}")
    return errors


def check_frontmatter_schema(vault_root: Path, mode: str, touched: set[str], rules: dict[str, Any]) -> list[Finding]:
    """Validate frontmatter presence and schema."""

    candidates = markdown_files_for_mode(vault_root, mode, touched)
    findings: list[Finding] = []
    for path in candidates:
        rel = normalize_rel(path, vault_root)
        meta, _body = load_frontmatter_and_body(path)
        errors = validate_frontmatter(rel, meta, rules)
        if not meta:
            errors.insert(0, "frontmatter missing")
        if not errors:
            continue
        fields = ", ".join(errors)
        findings.append(
            Finding(
                "WARN",
                "Frontmatter schema violation",
                rel,
                finding_message(
                    f"frontmatter に不整合があります: `{fields}`。",
                    "frontmatter に必須項目と想定 enum を追加・修正してください",
                ),
            )
        )
    if findings:
        return findings
    if mode == "light" and not candidates:
        message = finding_message("対象ノートがないためこの回の frontmatter 検証はスキップしました。", "追加対応は不要です")
    else:
        message = finding_message("対象ノートの frontmatter はスキーマに整合しています。", "追加対応は不要です")
    return [Finding("OK", "Frontmatter schema violation", None, message)]


def file_age_days(path: Path, now_utc: datetime) -> int:
    """Return file age in whole days."""

    mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)
    return (now_utc - mtime).days


def check_inbox_stagnation(vault_root: Path) -> list[Finding]:
    """Check for stale Inbox/{YYYY-MM-DD}/ date folders.

    In the date-first model, stagnation is measured per date folder:
    if any file under Inbox/{date}/ is older than the threshold, warn.
    """

    inbox_root = vault_root / INBOX_ROOT
    if not inbox_root.is_dir():
        return [
            Finding(
                "OK",
                "Inbox stagnation",
                None,
                finding_message(
                    f"Inbox 配下に {INBOX_STAGNATION_THRESHOLD_DAYS} 日超の滞留はありません。",
                    "追加対応は不要です",
                ),
            )
        ]
    now_utc = datetime.now(timezone.utc)
    findings: list[Finding] = []
    for date_dir in sorted(inbox_root.iterdir(), key=lambda item: item.name):
        if not date_dir.is_dir():
            continue
        if not INBOX_DATE_DIR_RE.match(date_dir.name):
            continue
        oldest_age: int | None = None
        file_count = 0
        for path in date_dir.rglob("*"):
            if not path.is_file():
                continue
            file_count += 1
            age = file_age_days(path, now_utc)
            if oldest_age is None or age > oldest_age:
                oldest_age = age
        if file_count == 0 or oldest_age is None:
            continue
        if oldest_age <= INBOX_STAGNATION_THRESHOLD_DAYS:
            continue
        rel = normalize_rel(date_dir, vault_root)
        findings.append(
            Finding(
                "WARN",
                "Inbox stagnation",
                rel,
                finding_message(
                    f"`{rel}/` に {oldest_age} 日以上未処理のファイルが {file_count} 件あります。",
                    "Daily ハブへ集約・蒸留するか、不要なら整理してください",
                ),
            )
        )
    if findings:
        return findings
    return [
        Finding(
            "OK",
            "Inbox stagnation",
            None,
            finding_message(
                f"Inbox 配下の日付フォルダに {INBOX_STAGNATION_THRESHOLD_DAYS} 日超の滞留はありません。",
                "追加対応は不要です",
            ),
        )
    ]


def daily_note_path(vault_root: Path, target_date: date) -> Path:
    """Return today's Daily note path."""

    return vault_root / "Daily" / f"{target_date.isoformat()}.md"


def extract_today_tasks(text: str) -> tuple[list[TaskItem], bool]:
    """Extract checkbox tasks from the today's tasks section."""

    match = TASKS_HEADING_RE.search(text)
    if not match:
        return [], False
    next_heading = re.search(r"(?m)^(?:### |## )", text[match.end() :])
    section = text[match.end() : match.end() + next_heading.start()] if next_heading else text[match.end() :]
    tasks: list[TaskItem] = []
    has_content = False
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("<!--"):
            continue
        has_content = True
        task_match = TASK_LINE_RE.match(line)
        if not task_match:
            continue
        title = task_match.group("title").strip()
        if not title:
            continue
        tasks.append(TaskItem(title=title, checked=task_match.group("mark").lower() == "x"))
    return tasks, has_content


def normalize_task(value: str) -> str:
    """Normalize a task title for drift comparison."""

    return re.sub(r"\s+", " ", value.strip()).casefold()


def run_hermes_json(vault_root: Path, prompt: str) -> tuple[dict[str, Any] | None, str | None]:
    """Call Hermes and parse JSON output."""

    try:
        result = run_command(["hermes", "chat", "-q", prompt, "-Q", "--source", "claude-code"], vault_root, timeout=15)
    except FileNotFoundError:
        return None, "Hermes CLI が見つかりません。"
    except subprocess.TimeoutExpired:
        return None, "Hermes の応答が 15 秒でタイムアウトしました。"
    if result.returncode != 0:
        stderr = result.stderr.strip() or "Hermes 呼び出しが失敗しました。"
        return None, stderr
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError:
        return None, "Hermes の応答が JSON ではありません。"


def check_today_tasks_drift(vault_root: Path, target_date: date, mode: str, enable_remote: bool) -> list[Finding]:
    """Check drift between Daily tasks and live Google Tasks."""

    rel = f"Daily/{target_date.isoformat()}.md"
    path = daily_note_path(vault_root, target_date)
    if not path.exists():
        return [
            Finding(
                "WARN",
                "Today Tasks drift",
                rel,
                finding_message("当日 Daily が見つからないため比較できません。", "Daily 生成後に再実行してください"),
            )
        ]
    tasks, has_content = extract_today_tasks(read_text(path))
    if mode == "light" and not has_content:
        return [
            Finding(
                "OK",
                "Today Tasks drift",
                rel,
                finding_message("Today Tasks 節に実データがないため比較をスキップしました。", "追加対応は不要です"),
            )
        ]
    if not enable_remote:
        return [
            Finding(
                "OK",
                "Today Tasks drift",
                rel,
                finding_message("リモート照会が無効のため Google Tasks との比較をスキップしました。", "必要時のみ `--enable-remote` で再実行してください"),
            )
        ]
    prompt = (
        "Return JSON only. Fetch live Google Tasks for the default lists relevant to today's daily review. "
        'Schema: {"tasks": [{"title": str, "status": "needsAction|completed"}]}'
    )
    payload, reason = run_hermes_json(vault_root, prompt)
    if payload is None:
        return [Finding("WARN", "Today Tasks drift", rel, finding_message(reason or "Google Tasks の取得に失敗しました。", "Hermes の状態と認証を確認してください"))]
    live_items = payload.get("tasks")
    if not isinstance(live_items, list):
        return [Finding("WARN", "Today Tasks drift", rel, finding_message("Hermes の JSON 形式が期待と異なります。", "Tasks 配列を返すようプロンプトと Hermes 側挙動を確認してください"))]
    daily = {normalize_task(item.title): item.checked for item in tasks}
    live = {
        normalize_task(str(item.get("title", ""))): str(item.get("status", "")) == "completed"
        for item in live_items
        if str(item.get("title", "")).strip()
    }
    only_daily = sorted(daily.keys() - live.keys())
    only_live = sorted(live.keys() - daily.keys())
    mismatch = sorted(key for key in (daily.keys() & live.keys()) if daily[key] != live[key])
    diff_count = len(only_daily) + len(only_live) + len(mismatch)
    if diff_count == 0:
        return [
            Finding(
                "OK",
                "Today Tasks drift",
                rel,
                finding_message("Daily と Google Tasks の状態差分は見つかりませんでした。", "追加対応は不要です"),
            )
        ]
    details = []
    if only_daily:
        details.append(f"Daily のみ: {', '.join(only_daily[:3])}")
    if only_live:
        details.append(f"Google Tasks のみ: {', '.join(only_live[:3])}")
    if mismatch:
        details.append(f"完了状態不一致: {', '.join(mismatch[:3])}")
    return [
        Finding(
            "WARN",
            "Today Tasks drift",
            rel,
            finding_message(
                f"Daily と Google Tasks の状態に {diff_count} 件の差分があります（{' / '.join(details)}）。",
                "完了状態とタスク名を見比べて手動で同期してください",
            ),
        )
    ]


def check_codemap_repo_health(vault_root: Path, mode: str, touched: set[str], enable_remote: bool) -> list[Finding]:
    """Check GitHub repo link health from Maps/Code-Map.md."""

    rel = "Maps/Code-Map.md"
    path = vault_root / rel
    if not path.exists():
        return [Finding("WARN", "Code-Map repo health", rel, finding_message("Code-Map が見つかりません。", "Maps/Code-Map.md を復元または作成してください"))]
    if mode == "light" and rel not in touched:
        return [
            Finding(
                "OK",
                "Code-Map repo health",
                rel,
                finding_message("Code-Map は本日未更新のため repo health 確認をスキップしました。", "追加対応は不要です"),
            )
        ]
    if not enable_remote:
        return [
            Finding(
                "OK",
                "Code-Map repo health",
                rel,
                finding_message("リモート照会が無効のため repo health 確認をスキップしました。", "必要時のみ `--enable-remote` で再実行してください"),
            )
        ]
    urls = [match.group(2) for match in CODEMAP_RE.finditer(read_text(path))]
    if not urls:
        return [Finding("OK", "Code-Map repo health", rel, finding_message("Code-Map に GitHub URL は見つかりませんでした。", "追加対応は不要です"))]
    prompt = (
        "Return JSON only. Check GitHub repo health for these URLs and classify each as one of: "
        "live, private_inaccessible, deleted_or_renamed, network_error. "
        f'URLs: {json.dumps(urls, ensure_ascii=False)}. '
        'Output schema: {"repos": [{"url": str, "status": str, "detail": str}]}'
    )
    payload, reason = run_hermes_json(vault_root, prompt)
    if payload is None:
        return [Finding("WARN", "Code-Map repo health", rel, finding_message(reason or "repo health 取得に失敗しました。", "Hermes の状態と認証を確認してください"))]
    repos = payload.get("repos")
    if not isinstance(repos, list):
        return [Finding("WARN", "Code-Map repo health", rel, finding_message("Hermes の JSON 形式が期待と異なります。", "repos 配列を返すようプロンプトと Hermes 側挙動を確認してください"))]
    findings: list[Finding] = []
    for repo in repos:
        url = str(repo.get("url", "")).strip()
        status = str(repo.get("status", "")).strip()
        detail = str(repo.get("detail", "")).strip()
        if status == "live":
            continue
        findings.append(
            Finding(
                "WARN",
                "Code-Map repo health",
                rel,
                finding_message(
                    f"`{url}` は `{status}` と判定されました。{detail}".strip(),
                    "private 想定なら注記追加、移転済みなら URL を見直してください",
                ),
            )
        )
    if findings:
        return findings
    return [
        Finding(
            "OK",
            "Code-Map repo health",
            rel,
            finding_message("Code-Map 内の GitHub URL はすべて live 判定でした。", "追加対応は不要です"),
        )
    ]


def check_work_logs_project(vault_root: Path, mode: str, touched: set[str]) -> list[Finding]:
    """Check that Work log/project notes declare the matching project code."""

    findings: list[Finding] = []
    candidates: list[Path] = []
    if mode == "full":
        for code in ("PROJ_A", "PROJ_B", "PROJ_X"):
            base = vault_root / "Work" / code / "logs"
            if base.exists():
                candidates.extend(sorted(base.glob("*.md")))
    else:
        for rel in touched:
            if re.match(r"^Work/(PROJ_A|PROJ_B|PROJ_X)/logs/[^/]+\.md$", rel):
                path = vault_root / rel
                if path.is_file():
                    candidates.append(path)
    for path in sorted(set(candidates)):
        rel = normalize_rel(path, vault_root)
        expected = rel.split("/")[1]
        meta, _body = load_frontmatter_and_body(path)
        if meta.get("project") == expected:
            continue
        findings.append(
            Finding(
                "WARN",
                "Work logs project field",
                rel,
                finding_message(
                    f"`project` が `{expected}` と一致していません（現在値: `{meta.get('project')}`）。",
                    "frontmatter の `project` を親ディレクトリの案件コードに合わせてください",
                ),
            )
        )
    if findings:
        return findings
    if mode == "light" and not candidates:
        message = finding_message("本日更新された Work logs はないため確認をスキップしました。", "追加対応は不要です")
    else:
        message = finding_message("対象 Work logs の `project` は親案件コードと一致しています。", "追加対応は不要です")
    return [Finding("OK", "Work logs project field", None, message)]


def check_submodule_drift(vault_root: Path) -> list[Finding]:
    """Check submodule dirty state and pending pointer bumps."""

    findings: list[Finding] = []
    try:
        submodule = run_command(["git", "submodule", "status", "--recursive"], vault_root)
        porcelain = run_command(["git", "status", "--porcelain"], vault_root)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return [Finding("WARN", "Submodule dirty / commit drift", None, finding_message("git コマンドを利用できません。", "git 実行環境を確認してから再実行してください"))]
    if submodule.returncode != 0 or porcelain.returncode != 0:
        reason = (submodule.stderr or porcelain.stderr).strip() or "git 状態取得に失敗しました。"
        return [Finding("WARN", "Submodule dirty / commit drift", None, finding_message(reason, "git 状態を確認してから再実行してください"))]
    for line in submodule.stdout.splitlines():
        if not line:
            continue
        prefix = line[0]
        parts = line[1:].strip().split()
        rel = parts[1] if len(parts) >= 2 else None
        if prefix == "+":
            findings.append(Finding("WARN", "Submodule dirty / commit drift", rel, finding_message("submodule 内の HEAD が親 repo 記録とずれています。", "submodule 側 commit と親 repo pointer の関係を確認してください")))
        elif prefix == "-":
            findings.append(Finding("WARN", "Submodule dirty / commit drift", rel, finding_message("submodule が未初期化です。", "submodule を初期化して状態を確認してください")))
        elif prefix == "U":
            findings.append(Finding("ERROR", "Submodule dirty / commit drift", rel, finding_message("submodule で merge conflict が発生しています。", "競合を解消してから再実行してください")))
    for line in porcelain.stdout.splitlines():
        match = re.match(r"^[ MARCUD?!]{2}\s+(Research)$", line)
        if not match:
            continue
        findings.append(Finding("WARN", "Submodule dirty / commit drift", match.group(1), finding_message("親 vault に submodule pointer の未コミット変更があります。", "意図した pointer bump か確認して必要なら commit してください")))
    if findings:
        return findings
    return [Finding("OK", "Submodule dirty / commit drift", None, finding_message("submodule の dirty 状態や pointer drift は検出されませんでした。", "追加対応は不要です"))]


def parse_gitmodules_paths(vault_root: Path) -> list[str]:
    """Read submodule paths from .gitmodules, returning POSIX relative paths."""

    path = vault_root / ".gitmodules"
    if not path.exists():
        return []
    paths: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    for match in re.finditer(r"(?m)^\s*path\s*=\s*(.+?)\s*$", text):
        rel = match.group(1).strip().replace("\\", "/").strip("/")
        if rel:
            paths.append(rel)
    return paths


def is_system_root_dir(name: str, prefixes: list[str]) -> bool:
    """Return whether a root-level directory name is an ignored system dir."""

    for prefix in prefixes:
        if prefix.endswith("*"):
            if name.startswith(prefix[:-1]):
                return True
        elif name == prefix:
            return True
    return False


def structure_submodule_excludes(vault_root: Path, rules: dict[str, Any]) -> list[str]:
    """Resolve submodule exclude paths, preferring .gitmodules over config fallback."""

    discovered = parse_gitmodules_paths(vault_root)
    if discovered:
        return discovered
    return list(rules.get("structure_submodule_excludes", []) or [])


def is_under_excluded_prefix(rel_path: str, excludes: list[str]) -> bool:
    """Return whether a relative path is inside any excluded subtree."""

    return any(rel_path == ex or rel_path.startswith(f"{ex}/") for ex in excludes)


def nonmd_file_allowed(rel_path: str, allowed: dict[str, Any]) -> bool:
    """Return whether a non-markdown file is exempt from the placement rule."""

    parts = rel_path.split("/")
    name = parts[-1]
    if name in (allowed.get("allowed_filenames", []) or []):
        return True
    for prefix in allowed.get("allowed_path_prefixes", []) or []:
        if rel_path == prefix or rel_path.startswith(f"{prefix}/"):
            return True
    allowed_dirs = set(allowed.get("allowed_dir_names", []) or [])
    if any(part in allowed_dirs for part in parts[:-1]):
        return True
    suffix = Path(name).suffix
    if suffix in (allowed.get("allowed_ext_anywhere", []) or []):
        return True
    for rule in allowed.get("allowed_ext_under_root", []) or []:
        ext = rule.get("ext")
        root = rule.get("root")
        if ext and root and suffix == ext and (rel_path == root or rel_path.startswith(f"{root}/")):
            return True
    return False


def iter_scan_dirs(vault_root: Path, scan_roots: list[str], excludes: list[str]):
    """Walk content scan roots, skipping submodule subtrees and dotted dirs."""

    for root_name in scan_roots:
        base = vault_root / root_name
        if not base.is_dir():
            continue
        for current, dirnames, filenames in os.walk(base):
            current_path = Path(current)
            rel_dir = normalize_rel(current_path, vault_root)
            dirnames[:] = sorted(
                d
                for d in dirnames
                if not d.startswith(".")
                and not is_under_excluded_prefix(f"{rel_dir}/{d}" if rel_dir != "." else d, excludes)
            )
            yield current_path, rel_dir, sorted(dirnames), sorted(filenames)


def check_structure_drift(vault_root: Path, mode: str, rules: dict[str, Any]) -> list[Finding]:
    """Check vault directory-structure drift (registry, required dirs, placement)."""

    findings: list[Finding] = []
    expected_root = set(rules.get("structure_expected_root_dirs", []) or [])
    system_prefixes = list(rules.get("structure_system_root_prefixes", []) or [])
    required_dirs = list(rules.get("structure_required_dirs", []) or [])
    scan_roots = list(rules.get("structure_scan_roots", []) or [])
    excludes = structure_submodule_excludes(vault_root, rules)
    allowed = rules.get("structure_nonmd_allowed", {}) or {}

    # (a) Root registry [light + full, WARN]
    for entry in sorted(vault_root.iterdir(), key=lambda item: item.name):
        if not entry.is_dir():
            continue
        name = entry.name
        if name in expected_root or is_system_root_dir(name, system_prefixes):
            continue
        findings.append(
            Finding(
                "WARN",
                "Structure drift",
                name,
                finding_message(
                    f"vault root 直下に registry 外のディレクトリ `{name}/` があります。",
                    "想定構造なら schema_rules.yaml の structure_expected_root_dirs に登録、不要なら整理してください",
                ),
            )
        )

    # (b) Required dirs exist [light + full, ERROR]
    for rel in required_dirs:
        if not (vault_root / rel).is_dir():
            findings.append(
                Finding(
                    "ERROR",
                    "Structure drift",
                    rel,
                    finding_message(
                        f"ルールが前提とするディレクトリ `{rel}/` が物理的に存在しません。",
                        ".gitkeep 付きで作成するか、不要なら schema_rules.yaml の structure_required_dirs から外してください",
                    ),
                )
            )

    # (b2) Inbox shape: date-first model [light + full, WARN]
    # - Inbox/ の直下は Inbox/{YYYY-MM-DD}/ のみ
    # - Inbox/{date}/ の直下は INBOX_KNOWN_SOURCE_DIRS のみ
    inbox_root = vault_root / INBOX_ROOT
    if inbox_root.is_dir():
        for entry in sorted(inbox_root.iterdir(), key=lambda item: item.name):
            if entry.name.startswith("."):
                continue
            rel = normalize_rel(entry, vault_root)
            if entry.is_file():
                # README.md / .gitkeep 等のメタファイルは許容
                continue
            if not entry.is_dir():
                continue
            if not INBOX_DATE_DIR_RE.match(entry.name):
                findings.append(
                    Finding(
                        "WARN",
                        "Structure drift",
                        rel,
                        finding_message(
                            f"`{rel}/` は Inbox 直下の想定外フォルダです（日付ファースト: `Inbox/YYYY-MM-DD/`）。",
                            "date-first モデルに沿って整理するか、不要なら削除してください",
                        ),
                    )
                )
                continue
            # date 直下の source サブdirを検査
            for sub in sorted(entry.iterdir(), key=lambda item: item.name):
                if sub.name.startswith("."):
                    continue
                if not sub.is_dir():
                    continue
                if sub.name in INBOX_KNOWN_SOURCE_DIRS:
                    continue
                sub_rel = normalize_rel(sub, vault_root)
                findings.append(
                    Finding(
                        "WARN",
                        "Structure drift",
                        sub_rel,
                        finding_message(
                            f"`{sub_rel}/` は未知の source サブフォルダです（既知: {sorted(INBOX_KNOWN_SOURCE_DIRS)}）。",
                            "想定 source に揃えるか、不要なら削除してください",
                        ),
                    )
                )

    # (c)/(d) full mode only
    if mode == "full":
        for current_path, rel_dir, dirnames, filenames in iter_scan_dirs(vault_root, scan_roots, excludes):
            # (d) Empty dir without .gitkeep [WARN]
            if not dirnames and not filenames and rel_dir != ".":
                findings.append(
                    Finding(
                        "WARN",
                        "Structure drift",
                        rel_dir,
                        finding_message(
                            f"`{rel_dir}/` が空で `.gitkeep` がないため git が追跡できません。",
                            ".gitkeep を置くか、不要なら削除してください",
                        ),
                    )
                )
            # (c) Non-md placement [WARN]
            for filename in filenames:
                if filename.endswith(".md"):
                    continue
                rel_file = filename if rel_dir == "." else f"{rel_dir}/{filename}"
                if nonmd_file_allowed(rel_file, allowed):
                    continue
                findings.append(
                    Finding(
                        "WARN",
                        "Structure drift",
                        rel_file,
                        finding_message(
                            f"`{rel_file}` が想定外の場所にある非 md ファイルです。",
                            "Inbox/attachments/ か対象フォルダ直下の _assets/ に移すか、コード本体は GitHub を正本にしてください",
                        ),
                    )
                )

    if findings:
        return findings
    return [
        Finding(
            "OK",
            "Structure drift",
            None,
            finding_message("ディレクトリ構造の drift は検出されませんでした。", "追加対応は不要です"),
        )
    ]


def sort_findings(findings: list[Finding]) -> list[Finding]:
    """Sort findings by severity, check name, then path."""

    return sorted(findings, key=lambda item: (SEVERITY_ORDER[item.tag], item.check_name, item.path or ""))


def render_markdown(findings: list[Finding], mode: str, ran_at: str) -> str:
    """Render findings in the required Markdown format."""

    warn_count = sum(1 for item in findings if item.tag == "WARN")
    error_count = sum(1 for item in findings if item.tag == "ERROR")
    ok_count = sum(1 for item in findings if item.tag == "OK")
    lines = [
        HEADING,
        "",
        f"WARN: {warn_count}, ERROR: {error_count}, OK: {ok_count} (checked: {CHECKED_COUNT}, mode: {mode}, ran: {ran_at})",
        "",
    ]
    for item in sort_findings(findings):
        tag = f"{item.tag:<4}"
        if item.path:
            lines.append(f"- {tag} [{item.check_name}] {item.path} :: {item.message}")
        else:
            lines.append(f"- {tag} [{item.check_name}] {item.message}")
    return "\n".join(lines)


def render_json(findings: list[Finding], mode: str, ran_at: str) -> str:
    """Render findings as JSON."""

    payload = {
        "summary": {
            "warn": sum(1 for item in findings if item.tag == "WARN"),
            "error": sum(1 for item in findings if item.tag == "ERROR"),
            "ok": sum(1 for item in findings if item.tag == "OK"),
            "checked": CHECKED_COUNT,
            "mode": mode,
            "ran": ran_at,
        },
        "findings": [asdict(item) for item in sort_findings(findings)],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def collect_findings(vault_root: Path, mode: str, target_date: date, enable_remote: bool) -> list[Finding]:
    """Run all eight checks and return findings."""

    touched = touched_today_paths(vault_root)
    rules = load_schema_rules(vault_root)
    findings: list[Finding] = []
    findings.extend(check_broken_wikilinks(vault_root, mode, touched))
    findings.extend(check_frontmatter_schema(vault_root, mode, touched, rules))
    findings.extend(check_inbox_stagnation(vault_root))
    findings.extend(check_today_tasks_drift(vault_root, target_date, mode, enable_remote))
    findings.extend(check_codemap_repo_health(vault_root, mode, touched, enable_remote))
    findings.extend(check_work_logs_project(vault_root, mode, touched))
    findings.extend(check_submodule_drift(vault_root))
    findings.extend(check_structure_drift(vault_root, mode, rules))
    return findings


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("light", "full"), default="light")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--enable-remote", action="store_true")
    parser.add_argument("--vault-root", type=Path, default=derive_vault_root(Path(__file__)))
    return parser


def main() -> int:
    """Run the CLI and always return zero."""

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass
    parser = build_parser()
    args = parser.parse_args()
    try:
        target_date = date.fromisoformat(args.date)
    except ValueError:
        target_date = date.today()
    ran_at = datetime.now().strftime("%H:%M")
    try:
        findings = collect_findings(args.vault_root.resolve(), args.mode, target_date, args.enable_remote)
        output = render_json(findings, args.mode, ran_at) if args.as_json else render_markdown(findings, args.mode, ran_at)
        sys.stdout.buffer.write(output.encode("utf-8"))
        if not output.endswith("\n"):
            sys.stdout.buffer.write(b"\n")
    except Exception as exc:  # pragma: no cover
        fallback = [Finding("WARN", "Submodule dirty / commit drift", None, finding_message(f"実行時例外が発生しました: {exc}", "スクリプト実装を確認してください"))]
        output = render_json(fallback, args.mode, ran_at) if args.as_json else render_markdown(fallback, args.mode, ran_at)
        sys.stdout.buffer.write(output.encode("utf-8"))
        if not output.endswith("\n"):
            sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
