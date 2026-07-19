---
name: session-log
description: After a substantial Claude Code session, append a concise summary of the work done into today's root Daily note (Daily/{YYYY-MM-DD}.md) at the appropriate section (🏢 Work / 🔬 Research / 💡 Others / 🗒️ ミーティング・連絡メモ). Designed for parallel sessions (Claudian fan-out across multiple Claude Code instances) — uses append-only writes with timestamps so concurrent calls do not overwrite each other. Use when the user says 「今のセッションを Daily に残して」 / 「session log」 / 「今やった作業を Daily にまとめて」, or proactively suggest after a conversation has produced concrete output (notes created, files edited, decisions made).
---

# session-log

## 目的

Claudian 経由で **並列に動いている複数の Claude Code セッション** で「ある程度まとまった作業」が終わったとき、その作業内容を **今日の Daily ノートの適切なセクションに append** する。

並列セッションが同じ Daily に書き込むため、**必ず append-only**（既存内容は触らない）で動く。

> **位置づけ**：Daily が「その日の唯一のハブ＝完全な記録」（[[.claude/rules/daily-operations.md]] §0 設計原則）であり続けるための補助スキル。Inbox 由来の capture（slack/code/mtgs 等）は hermes と daily-briefing が拾うが、**Claude Code セッション内で生まれた作業ログは別経路で拾われない**ため、本スキルがその穴を埋める。

## 設計原則

1. **Append-only** — 既存のセクション・bullet は一切変更しない。新しい bullet を末尾に足すだけ。
2. **Timestamped** — 並列セッションを区別するため `[HH:MM]` を頭に付ける。
3. **Concise** — 1 セッション = 1〜3 bullet。長文は別ノートに切り出し、Daily からリンクで参照。
4. **Domain-routed** — 触ったドメインに応じて適切なセクションへ。判らないときは「💡 Others / Insights」。
5. **Linkable artifacts** — 触ったファイル・作成したノートは必ず wikilink で明示。
6. **No frontmatter touch** — `updated` / `projects` は触らない（並列で競合する）。EOD distill か weekly-review でまとめて更新する。

## 使用場面

- ユーザー発話：「今のセッションを Daily に残して」「session log」「今やった作業を Daily にまとめて」「Daily に記録して」
- Claude 自発（提案）：実質的な成果（ノート作成・複数ファイル編集・設計判断など）が出た後に「session-log として Daily に記録しますか？」と提案する

## 実行フロー

### Step 1: 当日 Daily ノートを確定

1. `date +%Y-%m-%d` で当日（`YYYY-MM-DD`）を取得（推測しない）
2. `Daily/{YYYY-MM-DD}.md` の存在を確認
3. **存在しない場合**：先に [[.claude/skills/daily-briefing/SKILL.md]] 朝モードを走らせるか、`Templates/daily-note.md` ベースで最低限の雛形を作る
4. **存在する場合**：そのまま Read（並列セッションの直前書き込みを取り込む）

### Step 2: セッション内容を判定

会話履歴から以下を抽出：

| 抽出項目 | 例 |
|---|---|
| 作業ドメイン | Work（どの案件? PROJ_A / PROJ_B / PROJ_C）/ Research / Others（Ideas / Activities / Learning）/ Meta（vault 整備）|
| トピック | 何をテーマに作業したか（1 行・15 文字以内推奨）|
| 成果物 | 作成・編集したノート（wikilink）|
| 決定事項 | 設計判断・方針決定があれば |
| Follow-up | 未完了 / 次にやるべきこと |

### Step 3: 挿入先セクションを決定

| ドメイン判定 | 挿入先 Daily セクション |
|---|---|
| Work / 案件名あり | `## 📝 ログ` > `### 🏢 Work` の該当案件 bullet 配下 |
| Research | `## 📝 ログ` > `### 🔬 Research` |
| Others / Activities / Ecosystem / Ideas / Learning | `## 📝 ログ` > `### 💡 Others / Insights` |
| 会議・対話メモ・Slack 議論の記録 | `## 📝 ログ` > `### 🗒️ ミーティング・連絡メモ` |
| Vault 整備 / Meta / control-plane / skill 変更 | `## 📝 ログ` > `### 💡 Others / Insights` 配下に `**[Meta]**` prefix |
| 判定不能 | `## 📝 ログ` > `### 💡 Others / Insights` |

### Step 4: Append 用 bullet を組み立て

**標準フォーマット**：

```markdown
- **[HH:MM] {1行トピック}**
  - {何をしたか・何が決まったか・1〜3 bullet}
  - 触ったファイル: [[path/to/file1]], [[path/to/file2]]
  - Follow-up: {あれば}
```

**Work 案件の場合**（親 bullet の下に sub-bullet として）：

```markdown
### 🏢 Work
- **PROJ_A**: 
  - **[14:30] データ前処理パイプライン修正** — `training_data_loader.py` の None handling 追加. [[Work/PROJ_A/code/data-prep.md]]
- **PROJ_B**: 
```

**Meta（vault 整備）の場合**：

```markdown
### 💡 Others / Insights
- **[Meta][16:00] スキル境界の再整理** — defuddle / genspark-cli を hermes に移管。session-log skill 新設. [[.claude/skills/session-log/SKILL.md]]
```

### Step 5: Edit ツールで append

- セクションのアンカー（例：`### 💡 Others / Insights`）を一意に find
- **次のセクション見出し**（`### 🗒️` / `---` / `## 🌙 夜の振り返り` 等）の **直前** に bullet を挿入
- **既存の bullet は触らない**（並列セッションが書いた直前の bullet を含む）
- frontmatter は触らない（`updated` の競合回避）

### Step 6: 報告

- 挿入結果を 1 行で user に報告
  - 例：「Daily の 💡 Others に [14:30] vault skill 移行 を追記しました」
- 大きすぎる成果物（500 語超など）は Daily に書かず、別ノートに切り出して Daily からリンクするだけにする

## 並列セッションへの配慮

- **必ず Read → Edit の順**：他セッションが直前に書き込んでいる可能性があるため、Edit 直前に最新を取得する
- **Edit の `old_string` は一意性を確認**：section アンカーが他にないか・bullet 末尾が一意か
- **時刻衝突**：同じ分に複数セッションが書く場合、両方とも残す（順序は問わない）
- **frontmatter は触らない**：並列更新の競合を避けるため、`updated` / `projects` は EOD distill かweekly review で一括更新

## 注意

- **Daily は「その日の完全な記録」**：細かい作業も漏らさず残す（[[.claude/rules/daily-operations.md]] §0 設計原則）
- **長文は別ノートに**：500 語超は `Work/` / `Others/` / `.claude/docs/knowledges/` に新規ノートを作り、Daily からは 1 行リンクのみ
- **Inbox 由来は別経路**：Slack / clippings / Genspark などは hermes capture → `aggregate-*`（日中）／`eod-distill`（EOD）で集約。本スキルは **Claude Code セッション内での作業ログ専用**
- **明日まで持ち越したら**：翌日の Daily に追記、または該当ドメインのノートに持ち越し記録
- **コミット / push はしない**：vault-github-sync は別タイミング（ユーザー指示）で

## 他 skill との連携

| Skill | 関係 |
|---|---|
| [[.claude/skills/daily-briefing/SKILL.md]] | 朝の Daily 作成（朝のみ）。session-log の結果は EOD に [[.claude/skills/eod-distill/SKILL.md]] で Main DB に蒸留される |
| [[.claude/skills/knowledge-capture/SKILL.md]] | 根本原因・学びレベルの内容は session-log とは別に knowledge-capture へ |
| [[.claude/skills/work-project-writer/SKILL.md]] | Work 案件で大きめの成果が出たら案件側ノートにも記録（Daily は概要のみ） |
| [[.claude/skills/others-writer/SKILL.md]] | Others 系も同様（Daily は概要、本体は Others 配下） |

## 関連

- [[.claude/rules/daily-operations.md]]（Daily ハブ集約フロー）
- [[.claude/rules/agent-boundaries.md]]（書き込み境界・single-writer 原則）
- [[.claude/rules/vault-metadata.md]]
- [[Templates/daily-note.md]]
