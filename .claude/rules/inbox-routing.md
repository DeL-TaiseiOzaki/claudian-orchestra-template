# Inbox ルーティングルール

外部ソース → **hermes** → **`Inbox/{YYYY-MM-DD}/{source}/`** → **Claude が当日分を Daily に集約** → EOD に Main DB（Work / Others / Research）へ配分、という <your-vault> 唯一の取り込み導線を定義する。
このファイルは routing の **single source of truth**。Hermes-side capture skills（[[.hermes/skills/mymemory/]]）はここを実装する。

> 設計原則（2026-06-15 **日付ファースト＋Daily ハブ**へ再アーキ）：
> 1. **必ず Inbox を経由**する（hermes は直接 curated／Main DB に書かない）。
> 2. hermes は **capture only**：`Inbox/{YYYY-MM-DD}/{source}/` に生データを置き、frontmatter 正規化までしか触らない（**auto-route 廃止・本文加工なし・LLM 判断なし**）。
> 3. **Daily ノートが唯一のハブ**：その日の全ソースを Claude が `Daily/{YYYY-MM-DD}.md` に集約し、そこから Main DB へ蒸留・配分する。Daily は常に「その日の完全な記録」を保つ。

---

## 1. ワークフロー全体像

```
[External source]
       │ (1) capture — hermes（auto-route なし）
       ▼
Inbox/{YYYY-MM-DD}/{source}/{file}.md      ← 日付ファースト・ソース別サブフォルダ
       │ (2) aggregate — Claude が当日分を集約
       ▼
Daily/{YYYY-MM-DD}.md                       ← 唯一のハブ＝その日の完全な記録
       │ (3) distribute — EOD に蒸留・配分（Claude + ユーザー）
       ▼
Main DB（Work / Others / Research）          → Evergreen
```

| Step | 担い手 | 触る範囲 | 詳細 |
|---|---|---|---|
| (1) capture | hermes（**user instruction**） | `Inbox/{date}/**` への新規作成 | 各 source から生データ取得＋frontmatter 正規化のみ。**auto-route しない**。**on-demand 既定**＝the user (reads the Daily note's `## 🤖 ジョブリスト` を見て指示 → Claude が hermes に CLI 委譲。cron は任意（過渡期維持） |
| (2) aggregate | Claude | `Daily/{date}.md` | **朝の Calendar+Tasks** は [[.claude/skills/daily-briefing/SKILL.md]]（`Inbox/{date}/daily/` のみ）。**日中の per-source on-demand** は [[.claude/skills/aggregate-slack/SKILL.md]] / [[.claude/skills/aggregate-mtgs/SKILL.md]] / [[.claude/skills/aggregate-code/SKILL.md]] / [[.claude/skills/aggregate-clippings/SKILL.md]] / [[.claude/skills/aggregate-chat-logs/SKILL.md]] が分担 |
| (3) distribute | Claude + ユーザー | Main DB | **EOD に [[.claude/skills/eod-distill/SKILL.md]] が**：Daily から durable な知見を Work / Others / Research / `.claude/docs/knowledges/` へ蒸留・配分（移動元にリンク。raw Inbox は `{area}/sources/` へ。承認前提・1 日 1 回・直列） |

> **例外（直接配置）**：Main DB の保存先が**完全に見えている**場合は、ユーザー／Claude が Inbox を経ず**直接 Main DB に置いてよい**。**その際は Daily ノートに「○○を△△へ直接配置」と必ず記載**し、Daily がその日の完全な記録であり続けるようにする。

---

## 2. Source → Inbox サブディレクトリ対応（日付ファースト）

全ソースを `Inbox/{YYYY-MM-DD}/{source}/` 配下のサブフォルダに統一する。**サブフォルダはその日にそのソースが発生したときだけ作る**（毎日 7 個を強制しない）。ファイル名は識別子のみ（日付は親フォルダが持つので prefix 不要）。

| Source | Inbox の落とし先 | hermes が必ずセットする frontmatter |
|---|---|---|
| **Google Calendar**（GWS CLI） | `Inbox/{date}/daily/daily.md` | `source: "gcal:event:<id>"`, `started_at`, `attendees` |
| **Google Tasks**（GWS CLI） | `Inbox/{date}/daily/daily.md` | `source: "gtasks:task:<id>"`, `due` |
| **Slack**（hermes Slack app — **業務 IF**） | `Inbox/{date}/slack/{channel}.md`（DM は `dm-{counterpart}.md`） | `source: "slack:digest:<channel>:<date>"`, `channel`, `channel_id`, `is_dm`, `is_private`, `participants`, `user_authored`, `user_mentioned`, `message_count`, `fetched_at` |
| **Notion** | （取り込みなし — Vault → Notion は一方向） | — |
| **Web クリッピング**（ブラウザ拡張） | `Inbox/{date}/clippings/{slug}.md` | `source: "web:url:<URL>"`, `fetched_at` |
| **AI 壁打ちログ**（ChatGPT / Claude — Obsidian AI Exporter 拡張 + Local REST API・2026-06-15 ピボット） | `Inbox/{date}/chat-logs/{slug}-{hash}.md` | capture 時：`source: <provider>` / curate 時：`source: chat:<provider>:<id>` 等へ正規化（[[Inbox/README.md]] §chat-logs の normalize 表参照） |
| **GitHub MCP**（Step 5 コード変化） | `Inbox/{date}/code/code.md` | `source: "github:eod:<date>"`, `repos: [...]`, `fetched_at` |
| **Genspark AI 議事録**（`gsk` CLI、**on-demand**＝Daily ジョブリストから指示） | `Inbox/{date}/mtgs/genspark-{slug}.md` | `source: "genspark:meeting:<task_id>"`, `meeting_title`, `meeting_date`, `participants`, `transcript_length` |
| **添付ファイル**（手動 import / Slack files） | `Inbox/{date}/attachments/…`（Slack 添付は `attachments/slack/{channel}/…`） | `source: "manual"` 等 |

> `Inbox/notion/` は作らない（一方向 publish [[.claude/rules/agent-boundaries.md]]）。
> 日付フォルダの `{date}` は **capture イベントの発生日**。chat-logs など外部由来でファイル名に日付を持たないものは frontmatter `created` の日付フォルダに置く。

---

## 3. Inbox → Daily 集約 → Main DB 配分

**auto-route は廃止**（hermes は capture only）。代わりに Claude が当日分を Daily に集約し、EOD に Main DB へ配分する。

### 3.1 集約（Step 2 / daily-briefing）

- Claude（`daily-briefing` skill）が `Inbox/{date}/*` の全サブフォルダを走査し、`Daily/{date}.md` に取り込む。
- 朝：`Inbox/{date}/daily/daily.md`（GCal + GTasks）→ 朝 briefing。
- 日中〜EOD：`slack/` `code/` `mtgs/` `clippings/` `chat-logs/` をその日のログ／振り返りに集約。

### 3.2 配分（Step 6 / EOD distill）

Daily に集約した内容から、durable なものを Main DB へ蒸留・配分する。原則と例外：

| Inbox 元（`Inbox/{date}/…`） | EOD の配分先 | 備考 |
|---|---|---|
| `daily/daily.md` | `Daily/{date}.md` | briefing として集約（compose） |
| `slack/{channel}.md` | `Work/*/sources/`・`Others/*/sources/` 等（raw のまま） | 宛先は Claude/ユーザーが判断。蒸留ノートは `docs/`・`notes/` へ別途 |
| `code/code.md` | raw を `Work/*/sources/`、必要分を `logs/{date}.md` へ蒸留 | per-repo セクションで分かれている |
| `mtgs/genspark-*.md` | **要約して `{project}/meetings/{date}-{name}.md`（compiled）へ** | raw transcript は git 履歴に残す（§3.3 例外）。**話者名は [[Maps/People-Map.md]] で名寄せ**（AI 文字起こしは同音異字を誤記する。例：「ヤマダ」→「山田田」→ 実際は「山田 太郎」） |
| `clippings/{slug}.md` | raw を `{area}/sources/`、蒸留は `notes/`・`Others/Ideas/` | 信号なし＝判断は Claude/ユーザー |
| `chat-logs/{provider}-{slug}.md` | raw を `{area}/sources/`、または蒸留して `Others/Ideas/`・`notes/` | 〃 |
| `attachments/…` | `Work/*/sources/`（先方資料）・`references/`（サーベイ資料）等へ raw のまま | 〃 |

### 3.3 curate 着地の原則

> Inbox 由来データは hermes capture（chat-logs のみ手動）の**生データ**。作業ディレクトリへ移すときは原則 **`{area}/sources/`（① Raw・immutable・frontmatter は `type: capture` のまま）**。`meetings/`・`docs/`・`notes/` は sources/ から**蒸留した compiled** を別途書く層。
> **唯一の例外：genspark MTG（`Inbox/{date}/mtgs/`）は curate 時に要約し、`{project}/meetings/{date}-{name}.md`（③ Compiled・標準 enum）として置く**（raw transcript は sources/ に残さず git 履歴に委ねる）。

---

## 4. frontmatter（capture 時 / curate 時）

### capture 時（hermes がセット）

`source` / `created` / source 固有 signal（§2）をセット。`type: capture` / `status: inbox`（Inbox-source enum、[[.claude/rules/vault-metadata.md]]）。

### curate 時（Main DB へ move する Claude の責務）

- `type: capture` → 実体に合う標準 type、`status: inbox` → 標準 status へ書き換え。
- `source` / `created` は provenance として**保持**。
- 移動元（Daily / Inbox）に移動先への wikilink を残す。

> hermes は capture only なので、旧来の `routed_at` / `route_reason` 等の routing frontmatter は**廃止**。

---

## 5. Slack capture 設計（auto-route 廃止後）

**目的**：ユーザー（the user）が関与した Slack 会話を漏れなく Vault に取り込む。

### 5.1 キャプチャ対象

- the user が **発言した** スレッド／メッセージ
- the user が **@mention された** メッセージ
- **DM・private channel も含む**（参加している会話すべて）
- hermes-bot 自身の発言は対象外

### 5.2 粒度・ファイル命名（日次ダイジェスト）

1 日 × 1 チャンネル = 1 ファイル。**全 channel を一律 `Inbox/{date}/slack/{channel}.md` に capture する**（channel→project の振り分けはしない）。

| 種別 | パス |
|---|---|
| 通常 / private channel | `Inbox/{date}/slack/{channel}.md` |
| DM | `Inbox/{date}/slack/dm-{counterpart}.md` |

- hermes（on-demand `slack-capture`）は当日分／前日分をダイジェスト化し、書いたファイルは確定（同一ファイルを二度触らない＝ file 単位 single-writer と整合）。
- スレッドが翌日に継続しても、続きは翌日付フォルダに入る（過去日フォルダは不変）。

### 5.3 保存内容

| 項目 | 扱い |
|---|---|
| 本文 + メタ（author / ts / channel / mentions / permalink） | **必須**。各メッセージを時系列で列挙 |
| 添付（画像・PDF 等） | `Inbox/{date}/attachments/slack/{channel}/` に保存し、ダイジェストから相対リンク |
| メッセージ内 URL | タイトル / 概要を**展開**してインライン記載 |
| リアクション・編集履歴 | **保存しない**（ノイズ削減） |

frontmatter は §2 の slack 行を参照。

> **廃止（2026-06-15）**：channel→project 対応表（`slack-channel-map.yaml`）・DM 振り分け（`slack-route` skill）・`Inbox/slack/_unsorted/`・hermes auto-route。Slack は **全 channel を Inbox に capture するだけ**で、宛先判断は Daily 集約／EOD 配分で Claude + ユーザーが行う。旧 skill / 対応表は `Archive/.hermes/skills/mymemory/` へ退避（provenance 保持）。

---

## 6. Hermes の書き込み境界

| パス | Hermes 書き込み |
|---|---|
| `Inbox/{YYYY-MM-DD}/**` | ✅ capture & frontmatter 正規化（**唯一の書込先**） |
| curated パス（`Work/`・`Others/`・`Daily/`・`Maps/` 等） | ❌ **書かない**（auto-route 廃止。集約・配分は Claude + ユーザー） |
| `Research/**` | ❌（サブモジュール側の AGENTS.md に従う） |
| `Archive/**` / `Templates/**` | ❌ |

**Single-writer**：`Inbox/{date}/` の capture ファイルも、Claude が Daily へ集約した後は Claude + ユーザー所有。hermes は同じ file を二度触らない。

---

## 7. Hermes がしないこと

- **auto-route**（curated／Main DB への move）— **廃止**。capture のみ。
- **control-plane / Claude territory の編集**（`.claude/**`、`CLAUDE.md`、`AGENTS.md`、`README.md`、`Maps/**`、`Templates/**`、`Daily/**` を含む）
- **`.hermes/**` 配下の SKILL.md / references / config の自律編集**（自己領域でも spec / doc / config は read-only、#37 で 2026-06-07 確定）
  - **例外は `.hermes/**` 配下のデータ／学習ファイルのみ**：`cron` / `state` の JSON 更新、capture skill が出力する `Inbox/**` ファイル
  - SKILL.md / references / config の drift / empirical finding（外部 CLI 挙動変化、API スキーマの drift、cron mode の運用学習など）を検知した場合は、対象 file を直接編集せず `Inbox/{date}/clippings/` に observation/proposal note を新規作成する（最低限 `affected_path` / `observed_at` / `evidence` / `proposed_change` / `source` を frontmatter に含める）
- 本文 Markdown の編集（要約・追記・整形すべて NG）／ LLM 由来のタグ・要約付与
- curated file の移動・削除
- Inbox 配下の file 削除（destructive 操作は原則 人 / Claude 経由）
- `type` / `status` の改変

---

## 関連

- [[CLAUDE.md]] §1 ドメイン構成
- [[AGENTS]] §3 書き込み境界
- [[.claude/rules/agent-boundaries.md]] §3 capture → Daily 集約 → curate
- [[.claude/rules/daily-operations.md]] — Daily ハブ集約フロー
- [[.claude/rules/vault-metadata.md]] — frontmatter スキーマ
- [[.hermes/skills/mymemory/]] — Hermes 側 capture skills（[[.hermes/skills/mymemory/inbox-daily-capture/SKILL.md]] 等）
