---
name: eod-distill
description: Distill durable Daily and Inbox content into Wiki or agent knowledge with user approval and Daily backlinks. Use for EOD distill or 「今日の振り返り」.
---

# eod-distill

## 目的

一日の終わりに、Daily ノートに蓄積された情報のうち **durable（長期保存に値する）** なものを Main DB（Wiki / `.codex/docs/knowledges/`）へ蒸留・配分する。Daily は「その日の完全な記録」として残し、長期記憶は Main DB に蓄積する。

> **設計上の独立性**：本スキルは [[.codex/skills/daily-briefing/SKILL.md]] とは**独立**（旧 daily-briefing Step 6 を分離・2026-06-16）。daily-briefing は朝のみ、本スキルは夜のみ。並列セッションでは走らせない（直列実行を想定）。

## 入力

- `Daily/{YYYY-MM-DD}.md` 全体
  - `## 📝 ログ`（全 sub-section）
  - `## 🌙 夜の振り返り` の `### ✅ 完了したこと`、`### 💭 感想・気付き`
- `Inbox/{YYYY-MM-DD}/*` の raw capture（必要に応じて配分）

## 出力先（Main DB 配分表）

| Daily の項目タイプ | 移送先 | frontmatter |
|---|---|---|
| Wiki 系（アイデア / 学び / 文献 / 実験 / 活動の durable） | `Wiki/{slug}.md`（type で分類・新規 or 既存追記） | `type: note / idea / exploration / paper / experiment` |
| Knowledge / 根本原因 / gotcha | `.codex/docs/knowledges/{category}/{slug}.md`（[[.codex/skills/knowledge-capture/SKILL.md]] に委譲可） | 当該スキルの schema |
| Inbox raw（slack/code/clippings/chat-logs/attachments） | `Wiki/sources/` に raw のまま（Markdown は `type: capture` / `status: inbox` を保持し、非 Markdown は内容を変更しない） | raw-capture path override |
| Inbox raw（meeting transcript。provider 不問） | 要約を `Wiki/meetings/{date}-{topic}.md`（compiled）| 標準 enum |
| 細かい作業ログ（distill 不要） | Daily に残して終了 | — |

## 実行フロー

### Step 1: Daily 確定
- `Daily/{date}.md` 全体を Read

### Step 2: ログ走査と分類
- `## 📝 ログ` の各 sub-section を巡回
- `[HH:MM]` prefix 付き bullet（session-log / inbox-aggregate 由来）と直接記入された bullet を identify
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
3. **defuddle 移管学び** → [[.codex/docs/knowledges/architecture/{slug}.md]]?
   ...

承認: [全 yes] / [個別選択] / [編集] / [skip]
```

- **自動移送はしない**（不可逆操作）— [[.codex/rules/agent-boundaries.md]] §5 ティア「承認前提」
- 一括承認 ／ 個別承認のどちらでも可

### Step 6: 移送実行
承認されたものを Main DB に書く：
- **新規ノート作成**：frontmatter は標準 enum
- **既存ノートに append**：既存の `Wiki/{slug}.md` に追記する場合は append-only
- **compiled note の frontmatter**：raw から別に作る compiled note は標準 `type` / `status` を使う
- **raw archive の frontmatter**：raw file 自体を `Wiki/sources/` へ move する場合は [[.codex/rules/vault-metadata.md]] §4 の path override を適用し、`type: capture` / `status: inbox` を維持する
- `source: ...` / `created` は provenance として保持

### Step 7: Daily の back-link 更新
移送した分の index を `### 📤 蒸留・移送先（EOD distill）` に追加：

```markdown
### 📤 蒸留・移送先（EOD distill）
- [[Wiki/rag-evaluation-design.md]] — RAG 評価の設計判断を集約
- [[.codex/docs/knowledges/architecture/{slug}.md]] — 外部接続=Hermes 原則の学び
- [[Wiki/concept-{slug}.md]] — 新規着想
```

- 移送元の Daily bullet 末尾に `→ [[移送先]]` を追記（再 EOD 時の skip 判定にも使う）

### Step 8: Inbox raw の配分
- 当日の `Inbox/{date}/*` を走査
- §配分表の規則に従い `Wiki/sources/` へ raw のまま移動
- meeting transcript は provider を問わず例外：要約を `Wiki/meetings/`（compiled）に書き、raw は `Wiki/sources/` へ移さない。raw の同一内容が既に git commit に含まれることを確認でき、ユーザーが削除を承認した場合だけ Inbox から削除する。未 commit /変更中なら「未配分」として Inbox に残す
- 移動できなかった item は Daily の `### 📤 蒸留・移送先` の最後に「未配分」section で残す

### Step 9: Google Tasks 反映（必要に応じて）
- 完了タスク・defer 提案を作成
- ユーザー承認 → [[.codex/skills/hermes-query/SKILL.md]] 経由で hermes に反映

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

- **destructive 操作には承認必須**（[[.codex/rules/agent-boundaries.md]] §5 ティア「承認前提」）
- **Daily からの削除はしない**：Daily は「その日の完全な記録」を保つ。Daily にリンクを残すことで traceability 確保
- **Wiki への大量移送**：1 テーマ 1 ノートに集約する（細切れの多数ノートを作らない）
- **mtgs の例外**：raw transcript は `Wiki/sources/` へ archive せず、要約だけ compiled 領域へ置く（[[.codex/rules/inbox-routing.md]] §3.3）。raw が commit 済みであることを `git status` と対象 path の履歴で確認してから、ユーザー承認付きで削除する。確認できなければ削除しない。話者名は [[Maps/People-Map.md]] で名寄せ
- **起動は on-demand が既定**（Daily `## 🤖 ジョブリスト` の「EOD distill」指示で実行）

## 他 skill との連携

| Skill | 関係 |
|---|---|
| [[.codex/skills/daily-briefing/SKILL.md]] | 朝モード（本スキルは夜モード相当） |
| [[.codex/skills/wiki-writer/SKILL.md]] | Wiki ノート（idea / exploration / note / paper / experiment / 活動記録）作成 |
| [[.codex/skills/knowledge-capture/SKILL.md]] | 学び・根本原因の蓄積 |
| [[.codex/skills/inbox-aggregate/SKILL.md]] 等 | 先にこれらが Daily に集約してから本スキル |
| [[.codex/skills/session-log/SKILL.md]] | コアセッションログを Daily に残す |
| [[.codex/skills/weekly-review/SKILL.md]] | 月曜朝に過去 7 日の Daily を rollup（本スキルが日次 distill した結果を集計） |

## 関連

- [[.codex/rules/daily-operations.md]] §0 7-step pipeline（Step 6・分離後）
- [[.codex/rules/inbox-routing.md]] §3 配分表
- [[.codex/rules/vault-metadata.md]] 移行ルール
- [[.codex/rules/agent-boundaries.md]] §5 自律度ティア
- [[Maps/People-Map.md]] 話者名 canonical mapping
