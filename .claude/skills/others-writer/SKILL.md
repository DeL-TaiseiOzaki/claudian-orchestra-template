---
name: others-writer
description: Create and manage Others notes (Ideas / Ecosystem / Activities / Learning) that belong neither to Work nor to the Research mainline. Ideas covers both quick ideas (type:idea) and separate-seed PoC/検証 notes (type:exploration). Use for capturing ideas, exploration/PoC notes for separate seeds, ecosystem-building activity, community/committee/working-group activities, or learning/reading notes under Others/.
---

# Others Writer Skill

## 目的

Work（受託案件）・Research（研究本流）に属さない活動のノート（Ideas / Ecosystem / Activities / Learning）を効率的に作成・管理します。Ideas は着想（`type: idea`）と別シードの仮説検証・PoC（`type: exploration`）の両方をカバーします。

## できること

### 1. アイデアノートの作成（Ideas）
- 着想を素早く軽量に記録（`type: idea` / `status: draft`）
- `Templates/idea-note.md` から生成

### 2. 検証ノートの作成（Ideas・PoC/検証フレーバー）
- 別シードの仮説検証・PoC を記録（`type: exploration` / `status: in-progress`）。Ideas に内包する flavor
- シード単位でサブフォルダ化：`Others/Ideas/{seed-name}/`
- `Templates/exploration-note.md` から生成

### 3. 活動・学習ノートの作成（Ecosystem / Activities / Learning）
- Ecosystem（組織的エコシステム創発, `type: activity`）、Activities（コミュニティ/委員/WG/コンペ, `type: activity`）、読書・技術メモ（`type: note`）を記録

### 4. 昇格フローの支援
- `Ideas（着想・検証/PoC を含む） → Research / Work` の昇格・移動を補助
- **移動元に wiki-link を残す**（トレーサビリティ確保）
- 破棄は削除せず `status: archived`

## 使用場面

- 着想を書き留める：`Add idea: <タイトル>`
- 検証を始める：`Add exploration note (PoC/検証) under Ideas: <タイトル>`
- 学習メモ：`Add learning note: <book/topic>`

## テンプレート連携

- `Templates/idea-note.md` - アイデア（Ideas）
- `Templates/exploration-note.md` - 検証・PoC（Ideas 内の `type: exploration` flavor）

## 関連ルール

- `[[.claude/rules/others-management.md]]`
- `[[.claude/rules/vault-metadata.md]]`
- `[[.claude/rules/vault-tagging.md]]`
- `[[.claude/rules/language.md]]`

## 入口

- `[[Others/AGENTS.md]]` / `[[Others/README.md]]`
