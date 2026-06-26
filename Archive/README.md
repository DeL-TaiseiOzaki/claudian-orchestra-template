---
title: "Archive — inactive content sink"
type: "note"
status: "in-progress"
tags: ["moc", "archive"]
created: 2026-01-01
updated: 2026-01-01
---

# Archive — inactive content sink

非活性情報の退避先。**削除しない方針**。元パスをミラーして残し、frontmatter に `status: archived` を立てる。

## ルール

- 元パスをミラー：例えば `Work/PROJ_X/` を archived するなら `Archive/Work/PROJ_X/` に移す
- frontmatter に以下を追加：
  ```yaml
  status: "archived"
  archived: 2026-XX-XX                  # 退避した日
  archived_from: "Work/PROJ_X/..."      # 元パス（provenance）
  ```
- 履歴は git に任せる（古いコピーを別ファイルで残さない）

## 関連

- [[.claude/skills/vault-archive/SKILL.md]] — 退避判定 + 移動の skill
- [[.claude/rules/vault-metadata.md]] §Archive 用フィールド
