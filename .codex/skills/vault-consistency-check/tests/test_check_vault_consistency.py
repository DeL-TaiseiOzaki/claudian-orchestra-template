from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "check_vault_consistency.py"
SCHEMA = SKILL_DIR / "references" / "schema_rules.json"
SPEC = importlib.util.spec_from_file_location("check_vault_consistency_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


class VaultConsistencyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        target = self.root / checker.SCHEMA_RULES_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SCHEMA, target)
        self.rules = checker.load_schema_rules(self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        return path

    @staticmethod
    def _common_meta(type_value: str, status: str) -> dict[str, object]:
        return {
            "title": "Fixture",
            "type": type_value,
            "status": status,
            "tags": ["test"],
            "created": "2026-07-20",
            "updated": "2026-07-20",
        }

    def test_json_schema_is_required_without_fallback(self) -> None:
        schema_path = self.root / checker.SCHEMA_RULES_PATH
        schema_path.rename(schema_path.with_suffix(".missing"))
        with self.assertRaisesRegex(RuntimeError, "schema rules file is missing"):
            checker.load_schema_rules(self.root)

    def test_schema_file_is_valid_json(self) -> None:
        data = json.loads(SCHEMA.read_text(encoding="utf-8-sig"))
        self.assertEqual(self.rules, data)

    def test_raw_capture_overrides_only_date_first_inbox_and_wiki_sources(self) -> None:
        capture = self._common_meta("capture", "inbox")
        capture["source"] = "fixture:item:1"
        self.assertEqual(
            [],
            checker.validate_frontmatter(
                "Inbox/2026-07-20/slack/general.md", capture, self.rules
            ),
        )
        self.assertEqual(
            [],
            checker.validate_frontmatter(
                "Wiki/sources/slack/general.md", capture, self.rules
            ),
        )
        source_first_errors = checker.validate_frontmatter(
            "Inbox/slack/2026-07-20/general.md", capture, self.rules
        )
        self.assertIn("invalid type: capture", source_first_errors)
        self.assertIn("invalid status: inbox", source_first_errors)
        direct_date_errors = checker.validate_frontmatter(
            "Inbox/2026-07-20/direct.md", capture, self.rules
        )
        self.assertIn("invalid type: capture", direct_date_errors)
        self.assertIn("invalid status: inbox", direct_date_errors)

        no_source = dict(capture)
        no_source.pop("source")
        self.assertIn(
            "required field missing: source",
            checker.validate_frontmatter(
                "Inbox/2026-07-20/slack/general.md", no_source, self.rules
            ),
        )

    def test_knowledge_note_override(self) -> None:
        knowledge = self._common_meta("knowledge", "active")
        knowledge.update(
            {
                "source": "session:2026-07-20",
                "applies_to": ["codex/skills"],
                "severity": "medium",
            }
        )
        path = ".codex/docs/knowledges/codex/skill-discovery.md"
        self.assertEqual([], checker.validate_frontmatter(path, knowledge, self.rules))
        knowledge["status"] = "in-progress"
        self.assertIn(
            "invalid knowledge status: in-progress",
            checker.validate_frontmatter(path, knowledge, self.rules),
        )
        knowledge["status"] = "superseded"
        self.assertIn(
            "superseded knowledge field missing: superseded_by",
            checker.validate_frontmatter(path, knowledge, self.rules),
        )
        knowledge["superseded_by"] = ".codex/docs/knowledges/codex/replacement.md"
        self.assertEqual([], checker.validate_frontmatter(path, knowledge, self.rules))
        knowledge["status"] = "deprecated"
        self.assertIn(
            "deprecated knowledge field missing: deprecated_at",
            checker.validate_frontmatter(path, knowledge, self.rules),
        )
        knowledge["deprecated_at"] = "2026-07-20"
        self.assertEqual([], checker.validate_frontmatter(path, knowledge, self.rules))

    def test_structure_rejects_file_directly_under_inbox_date(self) -> None:
        self._write("Inbox/2026-07-20/direct.md", "raw\n")
        findings = checker.check_structure_drift(self.root, "light", self.rules)
        self.assertTrue(
            any(item.path == "Inbox/2026-07-20/direct.md" for item in findings),
            findings,
        )

    def test_cli_schema_failure_is_nonzero_and_reports_zero_checks(self) -> None:
        schema_path = self.root / checker.SCHEMA_RULES_PATH
        schema_path.rename(schema_path.with_suffix(".missing"))
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--vault-root",
                str(self.root),
                "--json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)
        payload = json.loads(result.stdout)
        self.assertEqual(0, payload["summary"]["checked"])
        self.assertEqual(1, payload["summary"]["error"])

    def test_scans_templates_and_knowledge_notes_but_not_mocs_or_contracts(self) -> None:
        self._write("Templates/note.md", "---\ntitle: T\n---\n")
        self._write(".codex/docs/knowledges/codex/note.md", "---\ntitle: K\n---\n")
        self._write(".codex/docs/knowledges/README.md", "# MOC\n")
        self._write("Wiki/note.md", "---\ntitle: W\n---\n")
        self._write("Wiki/AGENTS.md", "# Contract\n")
        paths = {
            checker.normalize_rel(path, self.root)
            for path in checker.iter_markdown_files(self.root)
        }
        self.assertIn("Templates/note.md", paths)
        self.assertIn(".codex/docs/knowledges/codex/note.md", paths)
        self.assertIn("Wiki/note.md", paths)
        self.assertNotIn(".codex/docs/knowledges/README.md", paths)
        self.assertNotIn("Wiki/AGENTS.md", paths)

    def test_bom_and_quoted_unquoted_frontmatter_are_deterministic(self) -> None:
        path = self._write(
            "Templates/bom-note.md",
            "\ufeff---\n"
            "title: Unquoted title # comment\n"
            "type: \"note\"\n"
            "status: 'draft'\n"
            "tags: [\"alpha, one\", 'beta, two']\n"
            "created: \"{{date:YYYY-MM-DD}}\"\n"
            "updated: {{date:YYYY-MM-DD}}\n"
            "---\n\n# Body\n",
        )
        meta, body = checker.load_frontmatter_and_body(path)
        self.assertEqual("Unquoted title", meta["title"])
        self.assertEqual(["alpha, one", "beta, two"], meta["tags"])
        self.assertEqual("{{date:YYYY-MM-DD}}", meta["created"])
        self.assertEqual("{{date:YYYY-MM-DD}}", meta["updated"])
        self.assertEqual("# Body\n", body.lstrip())
        findings = checker.check_frontmatter_schema(
            self.root, "full", set(), self.rules
        )
        self.assertEqual("OK", findings[0].tag, findings)

    def test_block_list_frontmatter(self) -> None:
        data = checker.parse_minimal_yaml(
            "title: Test\n"
            "tags:\n"
            "  - alpha\n"
            "  - 'beta' # comment\n"
            "reproducible: true\n"
        )
        self.assertEqual(["alpha", "beta"], data["tags"])
        self.assertIs(data["reproducible"], True)

    def test_meta_assets_are_allowed_by_structure_schema(self) -> None:
        allowed = self.rules["structure_nonmd_allowed"]
        self.assertTrue(checker.nonmd_file_allowed("Meta/assets/architecture.png", allowed))
        self.assertFalse(checker.nonmd_file_allowed("Meta/architecture.png", allowed))


if __name__ == "__main__":
    unittest.main()
