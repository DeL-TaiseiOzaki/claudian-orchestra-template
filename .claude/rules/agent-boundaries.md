# エージェント分担ルール（Hermes / コアエージェント）

この Vault は **Obsidian の中で動く 2 エージェント — Hermes と コアエージェント — の共通制御プレーン**。
**コアエージェント = Codex（既定）または Claude Code**（[[AGENTS.md]] §0。`core-setup` で選択）。
宣言的な設定・契約・自作スキルをここで版管理し、**ランタイム/秘密は git から除外**する（[[.gitignore]]）。
分担の判断軸は「① トリガー（定期/対話）② 状態（共有可変/読み取り）③ 接続面（誰が認証を持つか）」。

> **読み替え規約**：本ファイルを含む rules / skills の文中の「Claude (Code)」は**コアエージェント**を指す（歴史的経緯による表記。Codex コアでも同様に適用）。旧・二頭体制（Claude 指揮 + Codex 実装の委譲モデル）は**廃止**。
>
> 全体アーキテクチャは [[README.md]]、Inbox 取り込みフローは [[.claude/rules/inbox-routing.md]] を参照。

## 1. 役割分担

| エージェント | 役割 | 典型タスク |
|---|---|---|
| **Hermes** | 常時稼働・**全外部接続の所有**・**capture 専用取り込み**・Slack 業務 IF・**`.hermes/**` 配下のデータ／学習ファイル更新のみ** | Slack 双方向 / 予定・タスク・Notion・Web の定期 capture を `Inbox/{date}/{source}/` へ（**auto-route なし**）、`.hermes/**` 配下の **データ／学習 file**（cron/state JSON 等）のみ自律更新、**SKILL.md / references / config の drift / spec 変更も `Inbox/{date}/clippings/` への observation/proposal note** で報告（自己領域でも spec/doc/config は read-only） |
| **コアエージェント**（Codex 既定 / Claude Code 可） | 対話・オーケストレーション・**設計〜実装**・**control-plane を含む全 curated 領域の編集** | `Inbox/{date}/*` の Daily ハブ集約・Main DB への配分蒸留、構造整理、frontmatter 統制、rules / skills / `AGENTS.md` の更新、コード作業（設計・実装・デバッグ・レビュー）、他リポ読解（Hermes 経由） |

### 1.1 コア ⇄ hermes の 2 経路（push / pull）— on-demand 既定

hermes との情報のやり取りは 2 方向ある。**両方とも user-instruction-drivenの on-demand**（2026-06-16 切替・cron は廃止＝既存ジョブのみ過渡期維持・新規登録なし）。

| 経路 | 向き | トリガー | 用途 | 実装 |
|---|---|---|---|---|
| **push**（capture） | hermes → `Inbox/{date}/` | **the user (per the Daily `## 🤖 ジョブリスト`) instructs** → Claude が hermes に CLI 委譲 | 定常取り込み（Calendar / Tasks / Slack / GitHub / Genspark 等） | [[.hermes/skills/vault-capture/]]（capture skills）|
| **pull**（query） | Claude → hermes（CLI `hermes chat -q`） | Claude が必要時に同期呼び出し | ライブ確認・検索（今のタスク？ この件の Slack は？ Notion 参照） | [[.claude/skills/hermes-query/SKILL.md]] |

- **なぜ pull が要るか**：外部接続の認証は hermes が一元所有（§6）。コアエージェントは Slack/GWS/Notion を直接叩けないので、その場の参照は hermes に委譲する。
- **境界**：pull は read/query 既定。durable な結果は hermes に **`Inbox/{date}/` へ書かせる**（curated 直書き禁止）。transient な確認は stdout で受けて会話に統合（永続化しない）。外部への書き込み・破壊操作は §5 の承認ティアに従う。
- **cron は廃止（既定は on-demand）**：既存の cron job（slack-capture・genspark polling/evening・github-eod 等）が稼働中の環境では**触らず過渡期維持**で放置してよいが、**新規登録はしない**。**既定は on-demand**＝Daily ノート `## 🤖 ジョブリスト` から user instruction → Claude が hermes に CLI 委譲。
- **push を pull で置き換えない**：定常 capture は hermes capture skill に通す（push）、pull は「今すぐ・特定の検索」用途に限る。

## 2. system of record（正本の所在）

| コンテンツ | 正本 | 補足 |
|---|---|---|
| 記憶 / 研究 / 作業ノート・evergreen・添付（PDF/Office） | **<your-vault>**（Markdown, Git=正） | local-first・プレーンテキスト永続 |
| 清書・共有する研究 / 会社 KB | **Notion** | <your-vault> から**一方向 publish**（双方向同期は禁止） |
| コード（全リポジトリ） | **GitHub** | GitHub MCP は **hermes が所有**（CC/CX は hermes 経由で読み取り）。<your-vault> 自体は Claude のローカル `git`/`gh` でバックアップ |
| **業務会話** | **Slack** | hermes Slack app が IF。ログとして `Inbox/{date}/slack/` に降ろされる |
| 予定 | **Google Calendar** | 上流：スマホ / Notion Calendar |
| ToDo | **Google Tasks** | 上流：スマホ。Vault に並行 ToDo を作らない |
| Web 壁打ち（ChatGPT / Claude）生ログ | **<your-vault> `Inbox/{date}/chat-logs/`** | 生のまま投入、curate は別工程 |

> 研究ドキュメントは **<your-vault> が正本、Notion は清書版（一方向公開）**。
> **業務会話は Slack が正本**。Vault 側はそのログが残るだけ。

## 3. capture → Daily 集約 → curate の継ぎ目

3 ステージに分離する。Hermes は capture のみ、Claude Code + ユーザーが集約と curate を担う（**route ステージは廃止＝auto-route なし**）。

| Stage | 担い手 | 内容 | 触る範囲 |
|---|---|---|---|
| **capture** | Hermes | 外部ソースから生 md を取得 | `Inbox/{YYYY-MM-DD}/{source}/` に新規ファイル（frontmatter 正規化のみ） |
| **aggregate** | Claude Code | 当日分の `Inbox/{date}/*` を Daily に集約 | `Daily/{date}.md`（ハブ） |
| **curate** | Claude Code + ユーザー | Daily から Main DB へ蒸留・配分・リンク・evergreen 化 | Main DB（Work/Others/Research）の本文編集 |

ルーティング詳細は [[.claude/rules/inbox-routing.md]]。**全ソースが `Inbox/{date}/` に残り、Daily 集約と EOD 配分を待つ**（hermes は判定・移動をしない）。

- **生ログを直接 curated 領域に置かない**（GTD inbox 原則：捕捉と処理は別工程）。**例外**：保存先が完全に見えているものはユーザー／Claude が直接 Main DB に置いてよいが、Daily に「○○を△△へ直接配置」と必ず記載する。
- **Hermes は LLM 由来の要約・タグ付与・auto-route を一切しない**。capture と frontmatter 正規化のみ。

## 4. 単一書き手・一方向（split-brain 防止）

- **Single-writer は file 単位で維持**：Hermes が `Inbox/{date}/` に capture した file も、Claude が Daily へ集約した後は Claude Code + ユーザー所有。Hermes は同じ file に二度触らない。
- **curated パス（Main DB）は Claude Code + ユーザーのみが書く**。Hermes は `Inbox/{date}/` の外に書かない（auto-route 廃止）。
- **自動コミッタは 1 つ**：`Drive 同期 × Git × Obsidian Git × Hermes` が同一 `.md` を奪い合わないようにする。**Git を正、Drive は単なるマウント**と割り切る。
- **Notion ↔ Vault は文書単位で一方向**（Vault → Notion publish のみ）。
- **他リポジトリは hermes の GitHub MCP 経由で読み取り専用**（push: on-demand `github-eod-capture`・ジョブリスト指示 → `Inbox/{date}/code/`。既存 cron は過渡期維持 ／ pull: `hermes chat -q`）。コード変更はそのリポの文脈で PR（共有可変状態を別セッションから触らない）。

## 5. 自律度ティア（リスク × 可逆性で割り当てる）

| ティア | 例 | 担い手 |
|---|---|---|
| **on-demand（既定・2026-06-16 以降）** | 取り込み（`Inbox/{date}/` capture）・同期・バックアップ・ダイジェスト | the user (per the Daily job list) instructs → Claude / Hermes が実行 |
| 提案 → レビュー | Vault へのノート草稿、Notion 公開、Tasks 自動起票 | Hermes / Claude → user approval |
| 承認前提（不可逆・要判断） | 構造改変・削除・スキーマ変更・コード・本文編集・Main DB への配分 | コアエージェント + ユーザー |
| 全自動（**廃止＝過渡期維持のみ**） | 既存の cron job（slack-capture / genspark / github-eod 等） | Hermes cron — 触らない・**新規登録なし** |

## 6. 接続の所有（複製しない）

| 接続 | 所有者 | 経路 | 備考 |
|---|---|---|---|
| Slack（業務 IF） | Hermes | Slack app（双方向） | **仕事の会話はすべて Slack で進む** |
| Discord（コミュニティ・任意） | Hermes | bot token（`DISCORD_BOT_TOKEN`・read 専用） | **bot を追加できるサーバのみ**（self-bot は規約違反）。capture skill は slack-capture をひな形に自作（[[docs/connections/discord.md]]） |
| RSS / ニュースレター（任意） | Hermes | HTTP fetch（認証なし・`feeds.local.yaml`） | 新着 → `Inbox/{date}/clippings/`。ニュースレターは Gmail 転送受けも可 |
| Zotero（研究者・任意） | Hermes | Zotero Web API（`ZOTERO_API_KEY`・read-only） | pull 既定。文献の正本は Zotero、vault は文献ノート + `resource:` ポインタ（[[docs/connections/zotero.md]]） |
| Google Calendar（個人・複数可） | Hermes | **ics 直 fetch**（限定公開 URL、`.hermes/skills/vault-capture/inbox-daily-capture/scripts/fetch_calendar_ics.py`） | OAuth 不要・URL に token 内包。Claude は読まない。セットアップ → [[docs/connections/google-calendar-tasks.md]] |
| Google Calendar（追加アカウント・任意） | Hermes | **gws（GWS CLI）`gws calendar events list`**（アカウント別 config dir `GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-<name>`・readonly） | ics の限定公開 URL を出せない組織アカウント用。要：consent screen の test user 追加。Testing 公開のままだと token 約7日失効。**capture 実行 PC のローカルに該当 config dir の資格情報が必要** |
| Google Tasks | Hermes | `list_tasks.py`（library 直叩き・`${HERMES_HOME}/google_token.json`） | 共有 OAuth トークン。**`gws` には依存しない**（library が自前で OAuth refresh） |
| Gmail | Hermes | bundled `google-workspace`（共有 OAuth token・`gmail.*` scopes） | **pull 既定**（検索・参照）。定常 capture なし。残すときだけ on-demand で `Inbox/{date}/mail/` へ。下書き作成は承認制・自動送信なし（[[docs/connections/gmail.md]]） |
| Notion | Hermes | Notion MCP | 取り込みなし。Vault → Notion publish のみ |
| Web（調査・検証 read） | Claude Code（read）／ Hermes（capture） | Claude: WebFetch / WebSearch・subagent ／ Hermes: 拡張・on-demand（Web Clipper・AI Exporter） | **Web の調査・検証 read は Claude Code から直接可**（[[AGENTS.md]] §4 operating model と整合）。**Inbox へ残すクリッピング capture は hermes** 経由（ブラウザ拡張） |
| **Google Drive / Docs**（共有ドライブ資料の read） | **Claude Code**（特殊対応・2026-06-16 承認） | claude.ai **Google Drive コネクタ** `read_file_content`（fileId 指定） | **hermes 経由不要**の明示的例外。Claude コアの利便経路（コネクタ）。Codex コア / headless は hermes 経由（[[docs/connections/google-drive.md]] 経路 B）。**read 専用** |
| **GitHub MCP**（他リポのコード context） | **Hermes** | **GitHub MCP**（PAT は hermes のみ保持） | CC / CX は hermes 経由で読み取り（push: on-demand `github-eod-capture`→`Inbox/{date}/code/`・既存 cron は過渡期維持 ／ pull: `hermes chat -q`） |
| Git（vault 自身） | Claude Code | ローカル `gh` / `git` CLI | バックアップ + 履歴管理（GitHub MCP とは別経路） |

> 外向き統合の **write / capture**（Slack / Notion / GWS / **GitHub MCP**）は Hermes が OAuth / PAT + MCP を一元保持する（失効も一括）。
> **コアエージェント直接の例外（hermes を経由しない）**：① vault 自身の git（バックアップ・履歴）／② **共有ドライブの Google Docs/Sheets read**（claude.ai Drive コネクタ・**コアが Claude Code の場合のみ**。Codex コアは hermes 経由 [[docs/connections/google-drive.md]] 経路 B）／③ **Web の調査・検証 read**（WebFetch / WebSearch・subagent）。いずれも **read / backup 主体**で、**durable な外部取り込み（capture→Inbox）と外部システムへの write は従来どおり hermes**。
> GitHub MCP は **hermes が所有**する（PAT は `.hermes/config.yaml` の github MCP に passthrough、#38）。CC / CX は他リポのコード context を hermes 経由で読む（pull = `hermes chat -q` ／ push = on-demand `github-eod-capture`・ジョブリスト指示 → `Inbox/{date}/code/`。既存 cron は過渡期維持）。vault 自身の git 操作（バックアップ・履歴）だけは Claude のローカル `gh`/`git`。

## ヒューリスティック（新タスクの振り分け）

> スケジュール / 外部イベントで外部 → `Inbox/{date}/` に capture するだけ（捕捉・同期・通知）→ **Hermes**。
> 当日分を Daily に集約し、判断して蒸留・リンクし、正本（Main DB）を編集する → **コアエージェント + ユーザー**。
> コード設計・実装・デバッグ → **コアエージェント**（Codex 既定 / Claude Code 可）。
> **あらゆるシステム間フローは一方向、あらゆる file は書き手 1 人（時点ごと）。**

## 関連

- [[README.md]]（アーキテクチャ全景）
- [[AGENTS.md]]（コア契約の正本）
- [[.claude/rules/inbox-routing.md]]（Inbox → Daily 集約 → Main DB 配分）
- [[.claude/rules/daily-operations.md]]（capture / Daily / Weekly）
- [[.hermes/config.yaml]] / [[.hermes/SOUL.md]]（Hermes 宣言的設定）
