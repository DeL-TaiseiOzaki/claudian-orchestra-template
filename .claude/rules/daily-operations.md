# Daily Operations ルール

Vault の日次・週次運用ルールを集約。Daily / Weekly / Work logs の関係性を定義する。
**全体像は §0 の 7-step pipeline（2026-06-06 確定）から**。各ステップの実装は本ドキュメントの後続節と各 skill SKILL.md。

## 0. 一日のパイプライン（7-step）

| # | Phase | Time | Trigger | 担い手 | 入出力サマリ |
|---|---|---|---|---|---|
| 1 | Daily 起動 | 朝（e.g. 07:30）manual | event | Claude | →`Daily/{date}.md` 新規作成。skill：`daily-briefing` 朝 |
| 2 | 予定+タスク把握 | step 1 inline | event | Claude | Hermes pre-staged `Inbox/{YYYY-MM-DD}/daily/daily.md`＋ Google Tasks 全リスト → Daily 朝 briefing に予定／Today's Focus／**Google Tasks `Today Task` リストへ機械 move（提案→承認）**／**今日の会議一覧（会議URL付き）を出して「Genspark にどれを join させるか Web UI で取捨選択」リマインダ**（join 切替は Web UI 専用・CLI 不可。取り込み自体は step 3.5 が自動化）／**参加する MTG は `mtg-prep` で議事録の叩き台を準備＋Daily リンク**（[[.claude/skills/mtg-prep/SKILL.md]]・目的等はヒアリング。bot 準備は Web UI ガイドのみ＝CLI 不可） |
| 3 | 作業 | 日中 continuous | event | User+Claude+Codex | Work logs／Daily 追記／`Inbox/{YYYY-MM-DD}/clippings/` 等。skills：`work-project-writer`／`others-writer`／Codex 委譲 |
| 3.5 | **議事録取り込み** | **on-demand**（Daily `## 🤖 ジョブリスト` の「Genspark 議事録」指示） | event | hermes（user instruction） | `gsk meeting list` で今日(+前日)の `COMPLETED` 未取り込みを `Inbox/{date}/mtgs/` へ（filename 冪等）。**単一会議の `--task_id` 指定取得も同 skill** に統合。skill：`genspark-mtg` |
| 4a | Slack 同日 capture | **on-demand**（ジョブリスト「Slack」指示） | event | hermes（user instruction） | Slack API (today) → `Inbox/{date}/slack/{channel}.md`。skill：`slack-capture` |
| 4b | Slack 翌朝 catch-all | on-demand（朝の briefing 後にジョブリスト指示） | event | hermes（user instruction） | Slack API (前日) → 上書き idempotent ("preserve richer existing") |
| 5 | コード変化 capture | **on-demand**（ジョブリスト「GitHub EOD」指示） | event | hermes（user instruction） | **`Maps/Code-Map.md` 由来の全 repo の指定ブランチ × today** → GitHub MCP → `Inbox/{date}/code/code.md`。skill：`github-eod-capture` |
| 6a | **per-source 集約**（aggregate） | 日中 on-demand（ジョブリスト「Slack 集約」「MTG 集約」等） | event | Claude | `Inbox/{date}/{source}/*` → Daily 該当 section に **append-only** で要約 bullet（wikilink 付き）。session-log と同じ並列セッション対応。skills：`aggregate-slack` / `aggregate-mtgs` / `aggregate-code` / `aggregate-clippings` / `aggregate-chat-logs`（朝の Calendar+Tasks は `daily-briefing`） |
| 6b | **EOD distill**（distribute） | 終業後 manual（ジョブリスト「EOD distill」指示・1 日 1 回・直列） | event | Claude + user approval | Daily ログから durable を Work/Others/Research/`.claude/docs/knowledges/` へ蒸留・配分（移動元 Daily にリンクを残す）＋ raw Inbox を `{area}/sources/` へ配分（genspark mtg のみ要約を `{project}/meetings/` へ＝例外）＋**話者名は [[Maps/People-Map.md]] で名寄せ**＋**Google Tasks close/defer 提案→承認→hermes 反映**。skill：`eod-distill`（daily-briefing から独立・2026-06-16 分離） |
| 7 | **整合性チェック** | **on-demand**（ジョブリスト「vault 整合性チェック」指示） | event | Claude | 所定ディレクトリ scan → 問題リスト → Daily 内 `## 🔍 整合性チェック` セクション。**提案のみ・auto-fix なし**。skill：`vault-consistency-check` |

### 設計原則（pipeline 全体）

- **Daily ＝唯一のハブ**：その日の全ソース（`Inbox/{date}/*`・作業ログ）は `Daily/{date}.md` に集約され、そこから Main DB（Work/Others/Research）へ蒸留・配分される。**例外（直接配置）**：保存先が完全に見えているものは Inbox を経ず直接 Main DB に置いてよいが、**その場合も Daily に「○○を△△へ直接配置」と必ず記載**して Daily を「その日の完全な記録」に保つ
- **single artifact through the day**：Daily ノートが朝 briefing → 日中ログ → 夜振り返り → 整合性チェックまで通しの 1 枚
- **`Inbox/{date}/*` は capture 専用・auto-route なし**：3.5/4a/4b/5 はすべて `Inbox/{date}/{source}/` に着地。集約（Step 2 / 6a の `aggregate-*`）と配分（Step 6b の `eod-distill`）は Claude が担う（2026-06-16：Step 6 を 6a / 6b に分割し独立 skill 化）
- **on-demand 既定（2026-06-16 切替）**：cron による定時実行は**廃止**。代わりに **Daily ノートの `## 🤖 ジョブリスト`** が一覧として機能し、the user がそれを見て「○○やって」と指示 → Claude/hermes が on-demand 実行する。チェック状態は daily-briefing が `Inbox/{date}/{source}/` の存在から自動更新（取得済→`[x]`）。`Daily/` を見れば「何が済んで何が残っているか」が一目でわかる
   - 既存のメインPC 上の hermes cron job は**現状維持**（触らない）。新規登録はしない方針。一斉移行は段階的に
- **destructive 動作には承認必須**：Tasks close/defer・整合性チェックの修正提案 すべて「提案→承認→反映」
- **正本の所在**（[[.claude/rules/agent-boundaries.md]] §2）：ToDo=Google Tasks、業務会話=Slack、予定=Google Calendar、コード=GitHub
- **外部接続は全部 hermes**（pull は Claude → hermes CLI、push は user instruction → on-demand → `Inbox/{date}/`）
- **ordering の推奨**（cron 廃止後は強制ではない）：Step 6b（`eod-distill`）の前に Step 3.5/4a/5 → 6a（`aggregate-*`）をまとめて回しておくと、当日のコード変化・会議・Slack が全部 Daily に集約され、distill で Main DB へ落とせる。順序は by issuing instructions in order自然に保たれる

## 1. Daily ノート

### 運用スタイル：朝briefing + 日中ログ + 夜振り返り（skill 3 分離・2026-06-16）

| 時間帯 | セクション | 内容 | 担当 skill |
|--------|------------|------|------------|
| 朝 | `## 🌅 朝のbriefing` | Calendar 予定（今日+明日）、Google Tasks のタスク、Genspark 議事録 join リマインダ＋**参加 MTG の議事録叩き台準備の案内（`mtg-prep`）**、Today's Focus、注意点 | `daily-briefing`（朝のみ・Step 1+2）＋ `mtg-prep`（pre-meeting 叩き台・案内/起動） |
| 日中 | `## 📝 ログ` | 気付き、ミーティングメモ、Work/Research/Others の概要 ＋ Inbox 由来 source の集約 bullet | `aggregate-slack` / `aggregate-mtgs` / `aggregate-code` / `aggregate-clippings` / `aggregate-chat-logs`（on-demand append-only・Step 6a） |
| 夜 | `## 🌙 夜の振り返り` | 完了タスク、未完了の理由、感想、明日へ ＋ Main DB への蒸留・配分 | `eod-distill`（夜 1 回・直列・daily-briefing から独立・Step 6b） |

> **重要（2026-06-16 切替）**：以前は `daily-briefing` が朝＋夜の二段階を担っていたが、現在は **`daily-briefing` = 朝のみ／日中＝ `aggregate-*` 群／EOD 蒸留＝ `eod-distill`** の 3 つに分離されている。古い「夜に daily-briefing 再実行」フローは使わない。

### 取り込み〜集約フロー（Inbox/{date} → Daily ハブ → Main DB）

捕捉（capture）と整理（curate）を分ける。**Hermes の書き込みは `Inbox/{date}/` 内に閉じ（auto-route なし）、root `Daily/` と各ドメインは Claude Code ＋ ユーザーが所有**（single-writer）。

1. **朝（capture）**：the user issues instructions → Hermes が `inbox-daily-capture` skill で Calendar 予定 ＋ Google Tasks を取得し、生データを `Inbox/{YYYY-MM-DD}/daily/daily.md` に投入する（cron は廃止＝on-demand 既定）。
2. **朝（aggregate）**：`daily-briefing` skill が `Inbox/{YYYY-MM-DD}/daily/daily.md` を読み、root `Daily/{YYYY-MM-DD}.md` に朝 briefing を構成する（Hermes 未実行なら Calendar を直接読むフォールバック）。
3. **日中（aggregate per-source）**：壁打ち・コード・Slack・議事録などの生キャプチャは `Inbox/{date}/{source}/` に溜まる。新しい capture が landed したら `aggregate-slack` / `aggregate-mtgs` / `aggregate-code` / `aggregate-clippings` / `aggregate-chat-logs` で Daily 該当 section に append-only 集約。
4. **夜/EOD（distribute）**：`eod-distill` skill が Daily に集約された durable な知見を Work / Research / Others / `.claude/docs/knowledges/`（Main DB）へ蒸留・配分し、raw Inbox を `{area}/sources/` へ配分する（移動元 Daily にリンクを残す）。`Inbox/{date}/` は空に近づける（1 日 1 回・直列）。
   - **例外（直接配置）**：保存先が完全に見えているものは Inbox を経ず直接 Main DB に置いてよい。**その場合も Daily に「○○を△△へ直接配置」と必ず記載**する（Daily ＝その日の完全な記録）。

> ToDo の正本は **Google Tasks**（[[.claude/rules/agent-boundaries.md]]）。Daily へは**読み込んで写すだけ**で、Vault 内に競合するタスクリストを作らない。

### ファイルパス

- `Daily/{YYYY-MM-DD}.md`

### 生成タイミング

| タイミング | アクション | 担当 skill |
|-----------|------------|------------|
| 朝の起動 | Daily ノート新規作成＋朝 briefing 構成 | [[.claude/skills/daily-briefing/SKILL.md]] |
| 朝〜会議前（on-demand） | 参加 MTG の Genspark bot 準備ガイド＋議事録の叩き台作成＋Daily リンク（目的等はヒアリング） | [[.claude/skills/mtg-prep/SKILL.md]] |
| 日中（on-demand） | Inbox `{date}/{source}/*` から Daily へ集約 bullet を append | [[.claude/skills/aggregate-slack/SKILL.md]] / [[.claude/skills/aggregate-mtgs/SKILL.md]] / [[.claude/skills/aggregate-code/SKILL.md]] / [[.claude/skills/aggregate-clippings/SKILL.md]] / [[.claude/skills/aggregate-chat-logs/SKILL.md]] |
| 夜（EOD・1 日 1 回・直列） | Daily ログから durable を Main DB へ蒸留・配分 ＋ raw Inbox を `{area}/sources/` へ | [[.claude/skills/eod-distill/SKILL.md]] |

### テンプレート

- `[[Templates/daily-note.md]]`

## Work 案件ログ

### 運用スタイル：案件フォルダに独立記載

Daily ノートとは別に、案件ごとに `Work/{XXX}/logs/{YYYY-MM-DD}.md` を作る。

### ファイルパス

- `Work/{PROJ_A|PROJ_B|PROJ_C|PROJ_D|PROJ_E|PROJ_F}/logs/{YYYY-MM-DD}.md`（触った案件のみ作成）

### テンプレート

- `[[Templates/work-log-daily.md]]`

### 必須セクション

- `## 今日やったこと / 進捗`

ブロッカー、明日タスク、ミーティングメモは必要に応じて追記。テンプレでは強制しない。

### Daily ノートとの関係

- Daily の `## 📝 ログ > 🏢 Work` セクションは **概要** に留める
- 詳細は `Work/{XXX}/logs/{YYYY-MM-DD}.md` を参照（リンク経由）
- `[[Work/PROJ_A/logs/2026-05-29|PROJ_A 詳細]]` 形式で参照

## Weekly Review

### 運用スタイル：月曜朝に前週月〜日をレビュー

| 項目 | 内容 |
|------|------|
| 生成タイミング | 月曜朝 |
| 対象期間 | 前週月曜〜前週日曜（7日間） |
| 出力ファイル | `Daily/Weekly-{YYYY-W{ISO週番号}}.md` |
| 生成 skill | `[[.claude/skills/weekly-review/SKILL.md]]` |

### 入力データ

- 前週7日分の `Daily/{YYYY-MM-DD}.md`
- 前週分の `Work/*/logs/`
- 前週 `updated` の Research / Others ノート

### テンプレート

- `[[Templates/weekly-review.md]]`

## Calendar 取り込みのスコープ

`daily-briefing` skill が Google Calendar MCP を呼ぶ際の固定スコープ：

| 項目 | 取得内容 |
|------|----------|
| 期間 | 今日 00:00〜23:59 + 明日 00:00〜23:59 |
| カレンダー | primary |
| フィールド | `summary` / `start.dateTime`〜`end.dateTime` / `attendees`（人数+名前） |

Gmail 取り込みは **初期版では行わない**。`daily-briefing` skill は明示指示があった場合のみ Gmail を取得する。

## frontmatter `projects` フィールド

Daily / Weekly ノートの `projects` 配列はその日/週に触る案件コードを入れる：

```yaml
projects: ["PROJ_A", "PROJ_B"]
```

Weekly は触った案件をすべて入れる（`PROJ_A` / `PROJ_B` / `PROJ_C` / `PROJ_D` / `PROJ_E` / `PROJ_F`）。

## 関連

- [[.claude/skills/daily-briefing/SKILL.md]]
- [[.claude/skills/mtg-prep/SKILL.md]]
- [[.claude/skills/weekly-review/SKILL.md]]
- [[.claude/skills/work-project-writer/SKILL.md]]
- [[.claude/rules/work-management.md]]
- [[.claude/rules/vault-metadata.md]]
- [[Templates/daily-note.md]]
- [[Templates/weekly-review.md]]
- [[Templates/work-log-daily.md]]
