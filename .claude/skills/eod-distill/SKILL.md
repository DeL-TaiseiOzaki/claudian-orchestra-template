---
name: eod-distill
description: At end-of-day, distill Daily's accumulated log content into the Main DB (Wiki / .claude/docs/knowledges/). For each durable item in Daily's `## 📝 ログ` and `## 🌙 夜の振り返り`, identify the appropriate target note, move/copy with standard-enum frontmatter, and add a back-link in Daily's `### 📤 蒸留・移送先（EOD distill）` section for traceability. Independent from daily-briefing (which handles morning briefing only). Also distributes raw Inbox sources to their final Wiki/sources/ destinations. Use at EOD when the user says "EOD distill" / "今日の振り返り" / "Main DB に蒸留" / "今日のログを整理して"; typically once per day after aggregate-* skills have brought everything into Daily.
---

# eod-distill

## 目的

一日の終わりに、Daily ノートに蓄積された情報のうち **durable（長期保存に値する）** なものを Main DB（Wiki / `.claude/docs/knowledges/`）へ蒸留・配分する。Daily は「その日の完全な記録」として残し、長期記憶は Main DB に蓄積する。

> **設計上の独立性**：本スキルは [[.claude/skills/daily-briefing/SKILL.md]] とは**独立**（旧 daily-briefing Step 6 を分離・2026-06-16）。daily-briefing は朝のみ、本スキルは夜のみ。並列セッションでは走らせない（直列実行を想定）。

## 入力

- `Daily/{YYYY-MM-DD}.md` 全体
  - `## 📝 ログ`（全 sub-section）
  - `## 🌙 夜の振り返り` の `### ✅ 完了したこと`、`### 💭 感想・気付き`
- `Inbox/{YYYY-MM-DD}/*` の raw capture（必要に応じて配分）

## 出力先（Main DB 配分表）

| Daily の項目タイプ | 移送先 | frontmatter |
|---|---|---|
| Wiki 系（アイデア / 学び / 文献 / 実験 / 活動の durable） | `Wiki/{slug}.md`（type で分類・新規 or 既存追記） | `type: note / idea / exploration / paper / experiment` |
| Knowledge / 根本原因 / gotcha | `.claude/docs/knowledges/{category}/{slug}.md`（[[.claude/skills/knowledge-capture/SKILL.md]] に委譲可） | 当該スキルの schema |
| Inbox raw（slack/code/mtgs/clippings/chat-logs/attachments） | `Wiki/sources/` に raw のまま（type: capture 保持） | Inbox-source 拡張のまま |
| Inbox raw（genspark mtg のみ例外） | 要約を `Wiki/meetings/{date}-{topic}.md`（compiled）| 標準 enum |
| 細かい作業ログ（distill 不要） | Daily に残して終了 | — |

## 実行フロー

### Step 1: Daily 確定
- `Daily/{date}.md` 全体を Read

### Step 2: ログ走査と分類
- `## 📝 ログ` の各 sub-section を巡回
- `[HH:MM]` prefix 付き bullet（session-log / aggregate-* 由来）と直接記入された bullet を identify
- 各 bullet について durable 判定：
  - **durable**：決定 / 完了 deliverable / 学び / 設計判断 / 着想
  - **non-durable**：単発の作業メモ / 一時的な気付き / 既に他所に記載済み

### Step 3: 既配分チェック
- `### 📤 蒸留・移送先（EOD distill）` セクションに既に link 有 → skip
- 移送元 bullet に `→ [[...]]` 付き → skip（前回 EOD 済）

### Step 4: 配分候補リスト作成
- 各 durable item について「これは {target} に移すべきか」を判定
- 候補リストを user に提示

### Step 5: ユーザー承認

```markdown
EOD distill 候補：

1. **RAG 評価の設計判断** → [[Wiki/rag-evaluation-design.md]]?
2. **Slack で議論された新仕様** → [[Wiki/{slug}.md]]?
3. **defuddle 移管学び** → [[.claude/docs/knowledges/architecture/...]]?
   ...

承認: [全 yes] / [個別選択] / [編集] / [skip]
```

- **自動移送はしない**（不可逆操作）— [[.claude/rules/agent-boundaries.md]] §5 ティア「承認前提」
- 一括承認 ／ 個別承認のどちらでも可

### Step 6: 移送実行
承認されたものを Main DB に書く：
- **新規ノート作成**：frontmatter は標準 enum
- **既存ノートに append**：既存の `Wiki/{slug}.md` に追記する場合は append-only
- **frontmatter の書き換え**：`type: capture` → 標準 type、`status: inbox` → 標準 status（[[.claude/rules/vault-metadata.md]] 移行ルール）
- `source: ...` / `created` は provenance として保持

### Step 7: Daily の back-link 更新
移送した分の index を `### 📤 蒸留・移送先（EOD distill）` に追加：

```markdown
### 📤 蒸留・移送先（EOD distill）
- [[Wiki/rag-evaluation-design.md]] — RAG 評価の設計判断を集約
- [[.claude/docs/knowledges/architecture/external-access-must-go-through-hermes.md]] — 外部接続=hermes 原則の学び
- [[Wiki/concept-{slug}.md]] — 新規着想
```

- 移送元の Daily bullet 末尾に `→ [[移送先]]` を追記（再 EOD 時の skip 判定にも使う）

### Step 8: Inbox raw の配分
- 当日の `Inbox/{date}/*` を走査
- §配分表の規則に従い `Wiki/sources/` へ raw のまま移動
- mtgs のみ例外：要約を `Wiki/meetings/`（compiled）に書き、raw は git 履歴に委ねる
- 移動できなかった item は Daily の `### 📤 蒸留・移送先` の最後に「未配分」section で残す

### Step 9: Google Tasks 反映（必要に応じて）
- 完了タスク・defer 提案を作成
- ユーザー承認 → [[.claude/skills/hermes-query/SKILL.md]] 経由で hermes に反映

### Step 10: Daily ステータス更新
- frontmatter の `updated` を今日に
- 全配分完了で user 確認の上 `status: completed` に
- 並列セッションが終了していることを確認

## 並列セッションへの配慮

- **EOD distill は 1 日 1 回・直列実行**を想定
- もし並列で走った場合：
  - Step 7 の `### 📤 蒸留・移送先` は append-only
  - Step 6 の移送先既存チェックで重複回避（同一 Wiki ノートへは append マージ）

## 注意

- **destructive 操作には承認必須**（[[.claude/rules/agent-boundaries.md]] §5 ティア「承認前提」）
- **Daily からの削除はしない**：Daily は「その日の完全な記録」を保つ。Daily にリンクを残すことで traceability 確保
- **Wiki への大量移送**：1 テーマ 1 ノートに集約する（細切れの多数ノートを作らない）
- **mtgs の例外**：raw transcript は捨て、要約だけ compiled 領域へ（[[.claude/rules/inbox-routing.md]] §3.3）。話者名は [[Maps/People-Map.md]] で名寄せ
- **起動は on-demand が既定**（Daily `## 🤖 ジョブリスト` の「EOD distill」指示で実行）

## 他 skill との連携

| Skill | 関係 |
|---|---|
| [[.claude/skills/daily-briefing/SKILL.md]] | 朝モード（本スキルは夜モード相当） |
| [[.claude/skills/wiki-writer/SKILL.md]] | Wiki ノート（idea / exploration / note / paper / experiment / 活動記録）作成 |
| [[.claude/skills/knowledge-capture/SKILL.md]] | 学び・根本原因の蓄積 |
| [[.claude/skills/aggregate-slack/SKILL.md]] 等 | 先にこれらが Daily に集約してから本スキル |
| [[.claude/skills/session-log/SKILL.md]] | Claude セッションログを Daily に残す |
| [[.claude/skills/weekly-review/SKILL.md]] | 月曜朝に過去 7 日の Daily を rollup（本スキルが日次 distill した結果を集計） |

## 関連

- [[.claude/rules/daily-operations.md]] §0 7-step pipeline（Step 6・分離後）
- [[.claude/rules/inbox-routing.md]] §3 配分表
- [[.claude/rules/vault-metadata.md]] 移行ルール
- [[.claude/rules/agent-boundaries.md]] §5 自律度ティア
- [[Maps/People-Map.md]] 話者名 canonical mapping
