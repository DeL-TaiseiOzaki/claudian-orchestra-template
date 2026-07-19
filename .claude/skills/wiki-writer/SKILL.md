---
name: wiki-writer
description: Create and manage Wiki notes — the general-knowledge Main DB for everything durable. Covers quick ideas (type:idea), PoC/検証 notes (type:exploration), learning/reading notes (type:note), literature notes (type:paper, Zotero-linked), experiment notes (type:experiment), and activity records. Use for capturing ideas, exploration/PoC notes, learning/reading notes, literature notes, or community/activity records under Wiki/.
---

# Wiki Writer Skill

## 目的

durable な知識のノートを `Wiki/` に作成・管理する（[[.claude/rules/wiki-management.md]]）。
1 ノート = 1 トピック・wikilink で接続する general wiki。

## できること

### 1. アイデアノート（`type: idea` / `status: draft`）
- 着想を素早く軽量に `Wiki/{slug}.md` へ。`Templates/idea-note.md` から生成

### 2. 検証・PoC ノート（`type: exploration` / `status: in-progress`）
- 仮説・検証方法・結果を記録。シードが育ったらサブフォルダ化（`Wiki/{seed-name}/`）
- `Templates/exploration-note.md` から生成

### 3. 学習・読書・活動ノート（`type: note`）
- 学んだ要点 + 自分の言葉での再構成。書籍は `#book-note`、活動記録は `#activity` `#community`

### 4. 文献・実験ノート（`type: paper` / `type: experiment`）
- 文献ノートは Zotero のメタデータを引いて生成（[[Meta/connections/zotero.md]]・`Templates/research-paper-note.md`）
- 実験ノートは `Templates/research-experiment-note.md`

### 5. 棚卸しの支援
- 破棄は削除せず `status: archived`

## 使用場面

- 着想を書き留める：`Add idea: <タイトル>`
- 検証を始める：`Add exploration note: <タイトル>`
- 学習メモ：`Add learning note: <book/topic>`
- 文献ノート：`この論文の文献ノート作って`

## 関連ルール

- `[[.claude/rules/wiki-management.md]]`
- `[[.claude/rules/vault-metadata.md]]` / `[[.claude/rules/vault-tagging.md]]` / `[[.claude/rules/language.md]]`

## 入口

- `[[Wiki/AGENTS.md]]` / `[[Maps/Home.md]]`
