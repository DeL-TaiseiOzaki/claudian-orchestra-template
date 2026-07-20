from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
CAPTURE_ROOT = ROOT / ".hermes" / "skills" / "vault-capture"
WRITE_CLIPPING = CAPTURE_ROOT / "clippings-capture" / "scripts" / "write_clipping.py"
CALENDAR_HELPER = (
    CAPTURE_ROOT / "inbox-daily-capture" / "scripts" / "fetch_calendar_ics.py"
)
CALENDAR_EXAMPLE = CALENDAR_HELPER.with_name("calendars.local.json.example")
COMMON_FIELDS = {"title", "type", "status", "tags", "created", "updated"}


def frontmatter_text(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError("missing frontmatter")
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            return data
        if ":" in line:
            key, value = line.split(":", 1)
            data[key] = value.strip()
    raise AssertionError("unterminated frontmatter")


def load_calendar_helper():
    spec = importlib.util.spec_from_file_location("fetch_calendar_ics", CALENDAR_HELPER)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load calendar helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ClippingRoutingTests(unittest.TestCase):
    def run_capture(self, payload: dict[str, object]) -> tuple[str, dict[str, str]]:
        with tempfile.TemporaryDirectory() as temp_dir:
            vault = Path(temp_dir)
            (vault / "Inbox").mkdir()
            (vault / "AGENTS.md").write_text("test\n", encoding="utf-8")
            env = os.environ.copy()
            env["OBSIDIAN_VAULT_PATH"] = str(vault)
            result = subprocess.run(
                [sys.executable, str(WRITE_CLIPPING)],
                input=json.dumps(payload),
                text=True,
                capture_output=True,
                env=env,
                check=True,
            )
            output = Path(result.stdout.strip())
            relative = output.relative_to(vault)
            metadata = frontmatter_text(output.read_text(encoding="utf-8"))
            return relative.as_posix(), metadata

    def test_chat_routes_to_provider_prefixed_chat_logs(self) -> None:
        output, metadata = self.run_capture(
            {
                "source": "chatgpt",
                "title": "Design review",
                "captured_at": "2026-07-20T16:30:00Z",
                "content": "raw chat",
            }
        )
        self.assertEqual(output, "Inbox/2026-07-21/chat-logs/chatgpt-design-review.md")
        self.assertTrue(COMMON_FIELDS <= metadata.keys())
        self.assertEqual(metadata["type"], '"capture"')
        self.assertEqual(metadata["status"], '"inbox"')
        self.assertEqual(metadata["source"], '"chatgpt"')

    def test_web_routes_to_clippings_with_url_source(self) -> None:
        output, metadata = self.run_capture(
            {
                "source": "web",
                "title": "Reference",
                "url": "https://example.com/article",
                "captured_at": "2026-07-20T09:00:00+09:00",
                "content": "raw page",
                "tags": ["Reference Material", "日本語"],
            }
        )
        self.assertEqual(output, "Inbox/2026-07-20/clippings/reference.md")
        self.assertTrue(COMMON_FIELDS <= metadata.keys())
        self.assertEqual(metadata["source"], '"web:url:https://example.com/article"')
        self.assertIn("fetched_at", metadata)
        self.assertIn('"reference-material"', metadata["tags"])
        self.assertNotIn("日本語", metadata["tags"])


class CalendarContractTests(unittest.TestCase):
    def test_example_uses_helper_keys(self) -> None:
        data = json.loads(CALENDAR_EXAMPLE.read_text(encoding="utf-8"))
        for calendar in data["calendars"]:
            self.assertIn("label", calendar)
            self.assertIn("url", calendar)
            self.assertNotIn("name", calendar)
            self.assertNotIn("ics_url", calendar)

    def test_markdown_keeps_location_conference_and_source(self) -> None:
        helper = load_calendar_helper()
        lines = helper.render_md_event(
            {
                "summary": "Review",
                "all_day": False,
                "start_hm": "10:00",
                "end_hm": "10:30",
                "attendees": ["Alice"],
                "attendees_count": 1,
                "location": "Room A",
                "conference_url": "https://meet.google.com/abc-defg-hij",
                "uid": "event-123",
            }
        )
        rendered = "\n".join(lines)
        self.assertIn("場所: Room A", rendered)
        self.assertIn("会議URL: https://meet.google.com/abc-defg-hij", rendered)
        self.assertIn("Source: gcal:event:event-123", rendered)

    def test_markdown_keeps_partial_and_total_failure_comments(self) -> None:
        helper = load_calendar_helper()
        rendered = helper.render_md(
            {
                "today": [],
                "tomorrow": [],
                "errors": [
                    "Calendar 'work' failed "
                    "(https://calendar.google.com/private-deadbeef/basic.ics)"
                ],
            }
        )
        self.assertIn("### 📅 今日の予定", rendered)
        self.assertIn("ics calendar unavailable", rendered)
        self.assertIn("private-***", rendered)
        self.assertNotIn("private-deadbeef", rendered)

    def test_markdown_cli_stays_markdown_when_no_calendar_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "calendars.json"
            config.write_text(
                json.dumps({"timezone": "Asia/Tokyo", "calendars": []}),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(CALENDAR_HELPER),
                    "--config",
                    str(config),
                    "--date",
                    "2026-07-20",
                    "--format",
                    "md",
                ],
                text=True,
                capture_output=True,
                check=True,
            )
        self.assertTrue(result.stdout.startswith("### 📅 今日の予定"))
        self.assertNotIn('"generated_for"', result.stdout)


class ControlPlaneTextTests(unittest.TestCase):
    def test_no_new_cron_or_removed_aggregate_instructions(self) -> None:
        files = list((ROOT / ".hermes").rglob("*.md")) + list(
            (ROOT / "Meta" / "connections").rglob("*.md")
        )
        text = "\n".join(path.read_text(encoding="utf-8-sig") for path in files)
        self.assertNotIn("hermes cron create", text)
        self.assertIsNone(
            re.search(r"aggregate-(slack|mtgs|code|clippings|chat-logs)", text)
        )

    def test_hermes_model_is_provider_only(self) -> None:
        config = (ROOT / ".hermes" / "config.yaml").read_text(encoding="utf-8")
        model_block = config.split("model:\n", 1)[1].split("\nmcp_servers:", 1)[0]
        self.assertIn("provider: openai-codex", model_block)
        self.assertNotRegex(model_block, r"(?m)^\s+(name|model|id):")

    def test_daily_capture_forbids_recreation_after_handoff(self) -> None:
        skill = (
            CAPTURE_ROOT / "inbox-daily-capture" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Daily/{today}.md", skill)
        self.assertIn("handoff 済み", skill)
        self.assertIn("再作成しない", skill)

    def test_github_capture_checks_handoff_before_external_fetch(self) -> None:
        skill = (
            CAPTURE_ROOT / "github-eod-capture" / "SKILL.md"
        ).read_text(encoding="utf-8")
        idempotency = skill.split("冪等性", 1)[1].split("### 3.", 1)[0]
        self.assertIn("Daily/{date_str}.md", idempotency)
        self.assertIn("ownership handoff 済み", idempotency)
        self.assertIn("外部取得より前", idempotency)


if __name__ == "__main__":
    unittest.main()
