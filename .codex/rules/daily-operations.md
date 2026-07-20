# Daily Operations ルール

Vault の日次・週次運用ルールを集約。Daily / Weekly の関係性を定義する。
**全体像は §0 の 7-step pipeline（2026-06-06 確定）から**。各ステップの実装は本ドキュメントの後続節と各 skill SKILL.md。

## 0. 一日のパイプライン（7-step）

| # | Phase | Time | Trigger | 担い手 | 入出力サマリ |
|---|---|---|---|---|---|
| 1 | Daily 起動 | 朝（e.g. 07:30）manual | event | コア | →`Daily/{date}.md` 新規作成。skill：`daily-briefing` 朝 |
| 2 | 予定+タスク把握 | step 1 inline | event | コア | Hermes pre-staged `Inbox/{YYYY-MM-DD}/daily/daily.md` → Daily 朝 briefing に予定／タスク／Today's Focus／会議記録リマインダ。参加する MTG は `mtg-prep` で provider-neutral な叩き台を準備し Daily からリンク |
| 3 | 作業 | 日中 continuous | event | ユーザー + コア | capture extension による `Inbox/{YYYY-MM-DD}/clippings/` への取り込み／コアによる Daily 追記・Wiki ノート作成。skill：`wiki-writer` |
| 3.5 | **議事録取り込み** | **on-demand**（Daily `## 🤖 ジョブリスト` の議事録指示） | event | Hermes / provider capture extension | 選択した meeting-note provider から raw transcript を `Inbox/{date}/mtgs/{provider}-{slug}.md` へ。provider adapter がある場合は Hermes に委譲 |
| 4a | Slack 同日 capture | **on-demand**（ジョブリスト「Slack」指示） | event | Hermes（ユーザー指示） | Slack API (today) → `Inbox/{date}/slack/{channel}.md`。skill：`slack-capture` |
| 4b | Slack 翌朝 catch-all | on-demand（朝の briefing 後にジョブリスト指示） | event | Hermes（ユーザー指示） | Slack API (前日) → 上書き idempotent ("preserve richer existing") |
| 5 | コード変化 capture | **on-demand**（ジョブリスト「GitHub EOD」指示） | event | Hermes（ユーザー指示） | **`Maps/Code-Map.md` 由来の全 repo の指定ブランチ × today** → GitHub MCP → `Inbox/{date}/code/code.md`。skill：`github-eod-capture` |
| 6a | **per-source 集約**（aggregate） | 日中 on-demand（ジョブリスト「Slack 集約」「MTG 集約」等） | event | コア | `inbox-aggregate` が `Inbox/{date}/{source}/*` → Daily 該当 section に **append-only** で要約 bullet（wikilink 付き） |
| 6b | **EOD distill**（distribute） | 終業後 manual（ジョブリスト「EOD distill」指示・1 日 1 回・直列） | event | コア + ユーザー承認 | Daily から durable content を Wiki / `.codex/docs/knowledges/` へ蒸留し、raw Inbox を `Wiki/sources/` へ配分。meeting transcript は要約を `Wiki/meetings/` へ統合 |
| 7 | **整合性チェック** | **on-demand**（ジョブリスト「vault 整合性チェック」指示） | event | コア | 所定ディレクトリ scan → 問題リスト → Daily 内 `## 🔍 整合性チェック` セクション。**提案のみ・auto-fix なし**。skill：`vault-consistency-check` |

### 設計原則（pipeline 全体）

- **Daily ＝人間の監査点（audit surface）**：エージェントの全アクションは Daily に痕跡として集約される — `## 🤖 ジョブリスト` のチェック状態（何が取得済か）・集約 bullet の wikilink（何が入ったか）・`### 📤 蒸留・移送先`（どこへ配分されたか）・`## 🔍 整合性チェック`（何が壊れているか）。**ユーザーはその日の Daily を読むだけでシステム全体を監査・承認できる**。だから Daily からは削除せず「その日の完全な記録」を保つ
- **Daily ＝唯一のハブ**：その日の全ソース（`Inbox/{date}/*`・作業ログ）は `Daily/{date}.md` に集約され、そこから Main DB（Wiki）へ蒸留・配分される。**例外（直接配置）**：保存先が完全に見えているものは Inbox を経ず直接 Main DB に置いてよいが、**その場合も Daily に「○○を△△へ直接配置」と必ず記載**して Daily を「その日の完全な記録」に保つ
- **single artifact through the day**：Daily ノートが朝 briefing → 日中ログ → 夜振り返り → 整合性チェックまで通しの 1 枚
- **`Inbox/{date}/*` は capture 専用・auto-route なし**：3.5/4a/4b/5 はすべて `Inbox/{date}/{source}/` に着地。集約（Step 2 / 6a の `inbox-aggregate`）と配分（Step 6b の `eod-distill`）はコアエージェントが担う
- **on-demand 既定（2026-06-16 切替）**：Daily の `## 🤖 ジョブリスト` を見てユーザーが指示し、コア / Hermes が on-demand 実行する。チェック状態は daily-briefing が `Inbox/{date}/{source}/` の存在から更新する
   - 既存の Hermes cron job が稼働中の環境では過渡期に限って維持してよい。新規登録はしない
- **destructive 動作には承認必須**：Tasks close/defer・整合性チェックの修正提案 すべて「提案→承認→反映」
- **正本の所在**（[[.codex/rules/agent-boundaries.md]] §2）：ToDo=Google Tasks、業務会話=Slack、予定=Google Calendar、コード=GitHub
- **認証を伴う外部接続は Hermes が所有**（pull はコア → Hermes CLI、push はユーザー指示 → on-demand → `Inbox/{date}/`）。認証を Hermes と共有しない capture extension も Inbox に新規作成できるが、コアとユーザーは直接書かない
- **capture file の ownership handoff**：Daily 集約前は Hermes が同一 job を idempotent に再実行できる。Daily に source link を集約した後はコア + ユーザー所有となり、Hermes は更新しない
- **ordering の推奨**：`eod-distill` の前に capture → `inbox-aggregate` を実行し、当日の source を Daily に揃える

## 1. Daily ノート

### 運用スタイル：朝briefing + 日中ログ + 夜振り返り（skill 3 分離・2026-06-16）

| 時間帯 | セクション | 内容 | 担当 skill |
|--------|------------|------|------------|
| 朝 | `## 🌅 朝のbriefing` | Calendar 予定（今日+明日）、Google Tasks、会議記録リマインダ、MTG prep 案内、Today's Focus | `daily-briefing` + `mtg-prep` |
| 日中 | `## 📝 ログ` | 気付き、ミーティングメモ、Wiki への蒸留候補、Inbox source の集約 bullet | `inbox-aggregate`（on-demand append-only・Step 6a） |
| 夜 | `## 🌙 夜の振り返り` | 完了タスク、未完了の理由、感想、明日へ ＋ Main DB への蒸留・配分 | `eod-distill`（夜 1 回・直列・daily-briefing から独立・Step 6b） |

> `daily-briefing` = 朝、`inbox-aggregate` = 日中、`eod-distill` = EOD。夜に daily-briefing を再実行しない。

### 取り込み〜集約フロー（Inbox/{date} → Daily ハブ → Main DB）

捕捉（capture）と整理（curate）を分ける。Hermes の書き込みは `Inbox/{date}/` 内に閉じる。capture extension も新規 capture を作成できる。コアとユーザーは Inbox に直接書かず、root `Daily/` と curated domain をコアエージェント + ユーザーが所有する。

1. **朝（capture）**：ユーザー指示 → Hermes が `inbox-daily-capture` skill で Calendar 予定 + Google Tasks を取得し、raw data を `Inbox/{YYYY-MM-DD}/daily/daily.md` に投入する（on-demand 既定。既存 cron は過渡期のみ維持可、新規登録なし）。
2. **朝（aggregate）**：`daily-briefing` が staged file を読み、root Daily を構成する。未取得なら pending として止め、外部サービスを直接読まない。
3. **日中（aggregate per-source）**：新しい capture が着地したら `inbox-aggregate` で Daily 該当 section に append-only 集約。
4. **夜/EOD（distribute）**：`eod-distill` skill が Daily に集約された durable な知見を Wiki / `.codex/docs/knowledges/`（Main DB）へ蒸留・配分し、raw Inbox を `Wiki/sources/` へ配分する（移動元 Daily にリンクを残す）。raw file は `type: capture` / `status: inbox` の path override を維持する。`Inbox/{date}/` は空に近づける（1 日 1 回・直列）。
   - **例外（直接配置）**：保存先が完全に見えているものは Inbox を経ず直接 Main DB に置いてよい。**その場合も Daily に「○○を△△へ直接配置」と必ず記載**する（Daily ＝その日の完全な記録）。

> ToDo の正本は **Google Tasks**（[[.codex/rules/agent-boundaries.md]]）。Daily へは**読み込んで写すだけ**で、Vault 内に競合するタスクリストを作らない。

### ファイルパス

- `Daily/{YYYY-MM-DD}.md`

### 生成タイミング

| タイミング | アクション | 担当 skill |
|-----------|------------|------------|
| 朝の起動 | Daily ノート新規作成＋朝 briefing 構成 | [[.codex/skills/daily-briefing/SKILL.md]] |
| 朝〜会議前（on-demand） | 参加 MTG の provider-neutral な叩き台作成＋Daily リンク | [[.codex/skills/mtg-prep/SKILL.md]] |
| 日中（on-demand） | Inbox `{date}/{source}/*` から Daily へ集約 bullet を append | [[.codex/skills/inbox-aggregate/SKILL.md]] |
| 夜（EOD・1 日 1 回・直列） | Daily ログから durable を Main DB へ蒸留・配分 ＋ raw Inbox を `Wiki/sources/` へ | [[.codex/skills/eod-distill/SKILL.md]] |

### テンプレート

- `[[Templates/daily-note.md]]`

## Weekly Review

### 運用スタイル：月曜朝に前週月〜日をレビュー

| 項目 | 内容 |
|------|------|
| 生成タイミング | 月曜朝 |
| 対象期間 | 前週月曜〜前週日曜（7日間） |
| 出力ファイル | `Daily/Weekly-{YYYY-W{ISO週番号}}.md` |
| 生成 skill | `[[.codex/skills/weekly-review/SKILL.md]]` |

### 入力データ

- 前週7日分の `Daily/{YYYY-MM-DD}.md`
- 前週 `updated` の Wiki ノート

### テンプレート

- `[[Templates/weekly-review.md]]`

## Calendar 取り込みのスコープ

hermes 側 `inbox-daily-capture` が Google Calendar を取得する際の固定スコープ（`daily-briefing` は `Inbox/{date}/daily/daily.md` を読むだけで、Calendar を直接呼ばない）：

| 項目 | 取得内容 |
|------|----------|
| 期間 | 今日 00:00〜23:59 + 明日 00:00〜23:59 |
| カレンダー | primary |
| フィールド | `summary` / `start.dateTime`〜`end.dateTime` / `attendees`（人数+名前） |

Gmail は briefing に入れない（on-demand pull のみ・[[Meta/connections/gmail.md]]）。

## 関連

- [[.codex/skills/daily-briefing/SKILL.md]]
- [[.codex/skills/mtg-prep/SKILL.md]]
- [[.codex/skills/weekly-review/SKILL.md]]
- [[.codex/rules/wiki-management.md]]
- [[.codex/rules/vault-metadata.md]]
- [[Templates/daily-note.md]]
- [[Templates/weekly-review.md]]
