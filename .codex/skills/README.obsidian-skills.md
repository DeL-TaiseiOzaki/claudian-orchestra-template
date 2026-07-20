# Vendored format skills

The Obsidian format skills originated from [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) and are adapted for this vault.

| Skill | Purpose | External CLI |
|---|---|---|
| `obsidian-markdown/` | Wikilinks, embeds, callouts, properties, and tags | None |
| `obsidian-bases/` | `.base` views, filters, formulas, and summaries | None |
| `json-canvas/` | `.canvas` nodes, edges, and groups | None |
| `defuddle/` | Extract clean Markdown from web pages | `defuddle` |

## Canonical location

All skill bodies live under `.codex/skills/`.

- Codex discovers `.codex/skills/{name}/SKILL.md` directly.
- Do not use symlinks; keep skill bodies as plain files, portable on Windows and cloud-synced filesystems.

## Local adaptations

- Follow `.codex/rules/vault-metadata.md`, `.codex/rules/vault-tagging.md`, and `.codex/rules/language.md`.
- Use vault-root-relative paths.
- Keep skill descriptions concise so discovery metadata stays within the initial context budget.
- Keep executable regression tests beside the owning skill. `vault-consistency-check` uses a dependency-free stdlib `unittest` suite.
- `vault-consistency-check/references/schema_rules.json` is the dependency-free schema SSOT; do not duplicate its values in Python.

## Updating upstream

1. Update the canonical `SKILL.md` and references under `.codex/skills/<name>/`.
2. Reapply the vault-specific adaptation section.
3. Run the owning skill's `unittest` suite (e.g. `vault-consistency-check`) to confirm nothing regressed.
