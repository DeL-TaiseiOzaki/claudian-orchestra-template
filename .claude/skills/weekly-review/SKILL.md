---
name: weekly-review
description: Generate the weekly review note (Daily/Weekly-{YYYY-WXX}.md) on Monday morning, scanning the previous week's Daily notes and Wiki updates to summarize Wiki progress and extract next-week tasks. Use for weekly retrospectives and planning.
---

# Weekly Review Skill

## 目的

毎週月曜朝に **前週（月〜日）** の振り返りノート `Daily/Weekly-{YYYY-WXX}.md` を生成。
Daily ノートと `Wiki/` の期間内更新を走査して進捗をまとめ、今週やるべきタスクを抽出する。

## 使用場面

- 月曜朝：`Generate weekly review` / `先週のreviewを作って`
- 月曜以外で走らせた場合：直近の月曜〜日曜を「前週」とみなす

## 実行フロー

### Step 1: 対象週の決定

1. `date` で当日（`YYYY-MM-DD`）と曜日を取得
2. 当日を含む週の月曜を求め、**前週月〜日**（7日間）を対象期間とする
3. ISO 週番号は前週の木曜が属する週で算出（`date -d "<前週木曜>" +%V`）
4. 出力先: `Daily/Weekly-{YYYY-W{ISO週番号}}.md`

### Step 2: 入力データ収集

| 領域 | 対象 |
|------|------|
| Daily | `Daily/{YYYY-MM-DD}.md`（対象期間7日分） |
| Wiki | `Wiki/` のうち期間内更新ファイル |

存在しないファイルはスキップ（エラーにしない）。

### Step 3: ノート生成

`Templates/weekly-review.md` をベースに以下を埋める：

- **Wiki Summary**: 読んだ論文・完了実験・アイデア・学習・活動記録の主だった追記（完了 / 進行中 / ブロッカーを含む）
- **今週の目標**: 各領域の今週ゴール（ユーザに確認）
- **振り返り**: うまくいったこと / 改善点 / 学び

### Step 4: 月曜 Daily との接続

- 当日（月曜）の `Daily/{YYYY-MM-DD}.md` が無ければ `[[.claude/skills/daily-briefing/SKILL.md]]` 連続実行を提案
- 月曜 Daily の冒頭に `[[Weekly-{YYYY-WXX}]]` リンクを差し込み

## frontmatter

```yaml
---
title: "Weekly Review - W{ISO週番号}"
type: "log"
status: "completed"
period: "week"
tags: ["weekly-review"]
created: {当日YYYY-MM-DD}
updated: {当日YYYY-MM-DD}
---
```

本文冒頭に `**対象期間（前週月〜日）**: {前週月}~{前週日}` を明記。

## 注意

- 対象期間内に Daily / Wiki ファイルが1つも存在しない領域は「記録なし」と明記してスペースは確保
- frontmatter `updated` が無いノートは `created` で代用
- 既存の Weekly ファイルがある場合は上書きせず、ユーザに上書き / 追記 / 別名保存を確認

## 関連ルール

- [[.claude/rules/daily-operations.md]]
- [[.claude/rules/wiki-management.md]]
- [[.claude/rules/vault-metadata.md]]
- [[Templates/weekly-review.md]]
