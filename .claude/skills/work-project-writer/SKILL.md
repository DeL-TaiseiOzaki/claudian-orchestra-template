---
name: work-project-writer
description: Create and manage Work project notes for the PROJ_A / PROJ_B / PROJ_C client engagements — project overviews, daily logs, deliverables, proposals (pre-sale 提案書 / 見積 / スコープ / 体制), references — following the Work frontmatter schema. Use when writing or organizing client project notes under Work/, including the proposal phase before a deal is won.
---

# Work Project Writer Skill

## 目的

Work プロジェクト（PROJ_A / PROJ_B / PROJ_C）のノートを効率的に作成・管理します。

## できること

### 1. プロジェクトノートの作成
- 新しいプロジェクトノートを生成
- frontmatter を自動入力
- プロジェクトフォルダ構造を確認

### 2. デイリーログの作成
- その日のプロジェクト進捗をまとめる
- 各案件（PROJ_A / PROJ_B / PROJ_C）の進捗を記録
- ブロッカーや懸念点を記載

### 3. ウィークリーレビューの生成
- 週単位でのプロジェクト進捗をまとめる
- 次週の計画を立案
- パフォーマンスメトリクスを集計

## 使用場面

- 新規プロジェクト開始時：`Create new Work project: PROJ_A`
- 毎日の進捗記録：`Add today's work log`
- 週末レビュー：`Generate weekly review`

## プロジェクト構造（共通5種）

各案件 `Work/{PROJ_A,PROJ_B,PROJ_C}/` の共通コンテンツと置き場（詳細は [[.claude/rules/work-management.md]]）：

| 情報 | 置き場 | テンプレート |
|---|---|---|
| プロジェクト概要（入口） | `project.md` | `Templates/work-project-overview.md` |
| 非定常な全体ステータス | `status.md` | `Templates/work-status.md` |
| チームメンバーのタスク状況 | `team.md` | `Templates/work-team.md` |
| 毎回のミーティング情報 | `meetings/{YYYY-MM-DD}-{topic}.md` | `Templates/work-meeting-note.md` |
| 定常ドキュメント | `docs/` | `Templates/work-doc.md` |
| 提案（受注前：提案書・見積・スコープ・体制） | `proposals/{YYYY-MM-DD}-{topic}.md` | `Templates/work-proposal.md` |
| コードベース知識 | `code/`（本体は GitHub） | `Templates/code-note.md`（[[Maps/Code-Map.md]] から繋ぐ） |
| 案件デイリーログ | `logs/{YYYY-MM-DD}.md` | `Templates/work-log-daily.md` |

## テンプレート連携

- `Templates/work-project-overview.md` - プロジェクト概要（`project.md`）
- `Templates/work-status.md` / `Templates/work-team.md` - 全体ステータス / チーム状況
- `Templates/work-meeting-note.md` - ミーティング記録
- `Templates/work-doc.md` - 定常ドキュメント（要件 / 仕様 / 設計 / 運用）
- `Templates/work-proposal.md` - 提案フェーズ成果物（`proposals/`・受注前：提案書 / 見積 / スコープ / 体制）
- `Templates/code-note.md` - コードベース読解メモ（`code/`）
- `Templates/work-log-daily.md` - 案件別デイリーログ（`Work/{XXX}/logs/{YYYY-MM-DD}.md`）
- `Templates/daily-note.md` - root デイリー（`Daily/{YYYY-MM-DD}.md`）
- `Templates/weekly-review.md` - ウィークリーレビュー（前週月〜日対象）

## 他 skill との連携

| Skill | 役割 |
|-------|------|
| `[[.claude/skills/daily-briefing/SKILL.md]]` | 朝の Daily 起動。Calendar 予定取り込み。Work 進行中タスクがあればここから案件ログ作成へ橋渡し |
| `[[.claude/skills/weekly-review/SKILL.md]]` | 月曜朝に `Work/{XXX}/logs/` と Daily を走査して案件横断のまとめを作る |

詳細運用ルールは `[[.claude/rules/daily-operations.md]]` 参照。

## 関連ルール

- `[[.claude/rules/work-management.md]]`
- `[[.claude/rules/daily-operations.md]]`
- `[[.claude/rules/vault-metadata.md]]`
- `[[.claude/rules/vault-tagging.md]]`
