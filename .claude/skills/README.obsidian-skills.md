# Obsidian Skills（vendored）

[kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) から取り込んだ Agent Skills。

| スキル | 用途 | 外部CLI |
|--------|------|---------|
| `obsidian-markdown/` | Obsidian Flavored Markdown（wikilink / embed / callout / properties / tag） | 不要 |
| `obsidian-bases/` | `.base` ファイル（ビュー・フィルタ・数式・サマリ） | 不要 |
| `json-canvas/` | `.canvas` ファイル（ノード・エッジ・グループ） | 不要 |

> [!note] defuddle は Claude 側ミラーなし
> `defuddle/`（Webページから本文markdown抽出・`defuddle` npm CLI が必要）は **`.codex/skills/defuddle/` と `.hermes/skills/vault-capture/defuddle/` のみ**に置く。`.claude/skills/` 配下にミラーは無い。

> [!note] obsidian-cli は除外
> Obsidian アプリ内で作業しているため、外部 `obsidian-cli`（プラグイン/テーマ開発・CLI経由のVault操作）は冗長と判断し導入対象から外した。

## 取り込み構成

- **出典**: `https://github.com/kepano/obsidian-skills`（`main` ブランチ）
- **取得日**: 2026-05-29
- **形式**: 各 `<name>/SKILL.md` + `references/`（正式な Agent Skills フォーマット）
- **本文**: 上流を verbatim で保持。末尾に「## このVaultでの運用（adaptation）」セクションのみ追記。
- **ライセンス**: 上流リポジトリの LICENSE に従う。

## 両エージェントでの有効化（2箇所運用）

| エージェント | 配置 | 検出方法 |
|--------------|------|----------|
| **Claude Code** | `.claude/skills/<name>/` | `<name>/SKILL.md` を自動検出 |
| **Codex CLI** | `.codex/skills/<name>/` | `.codex/config.toml` の `[[skills.config]]` で登録 |

Codex は `.codex/skills/` 配下のスキルのみ拾うため、**両ディレクトリに同一実体を置く**（Windows + Google Drive で symlink が不可のため）。`.claude/skills/` を編集元（正）とし、`.codex/skills/` へ複製する。**例外：`defuddle/` は codex 側＋hermes 側のみ**（`.claude/skills/` にミラーを置かない）。

## adaptation 方針

- frontmatter スキーマ: [[.claude/rules/vault-metadata.md]]
- タグ体系: [[.claude/rules/vault-tagging.md]]
- 言語規約: [[.claude/rules/language.md]]
- パスは Vault ルートからの相対で記述する。

## 更新時

上流の更新を反映する場合：

1. 各 SKILL.md / references を再取得し、`.claude/skills/<name>/` を更新。
2. 末尾の adaptation セクションを再付与。
3. `.codex/skills/<name>/` へ同内容を複製（同期を忘れない）。
