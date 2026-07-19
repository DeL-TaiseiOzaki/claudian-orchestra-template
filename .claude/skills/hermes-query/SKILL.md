---
name: hermes-query
description: Delegate an on-demand, synchronous query to the Hermes agent via its CLI (`hermes chat -q`) when you need LIVE data from a hermes-owned external connection — Google Tasks / Google Calendar, Slack (search a channel / thread / mention), Notion (read), the Web, or GitHub (read other repos' code/PRs/commits via hermes's GitHub MCP). Use this "pull" path when the cron "push" (hermes → Inbox) hasn't already staged what you need. Hermes owns all external auth (incl. the GitHub PAT); Claude Code does not, so live external lookups go through Hermes. Read / query oriented; durable results are written to Inbox by Hermes, transient lookups return inline.
---

# hermes-query — Claude → hermes 同期呼び出し（pull 経路）

<your-vault> には Claude ⇄ hermes の**2 経路**がある：

| 経路 | 向き | トリガー | 用途 | 既定 |
|---|---|---|---|---|
| **push**（capture） | hermes → Inbox | on-demand（ジョブリスト指示）/ 外部イベント | 定常取り込み（Calendar/Tasks/Slack 等を `Inbox/` へ） | 定常取り込みはこちら |
| **pull**（このスキル） | Claude → hermes（CLI） | あなたが必要時に呼ぶ | ライブな確認・検索（今のタスク？ この件の Slack は？） | 補助 |

> **なぜ hermes 経由か**：Slack / Google Workspace / Notion / Web / **GitHub MCP** の**認証はすべて hermes が一元所有**し（GitHub PAT も hermes のみ保持、#38）、
> Claude Code は持たない（[[.claude/rules/agent-boundaries.md]] §6）。だからライブ外部参照は hermes に委譲する。
> Codex に**コード**を委譲する [[.claude/skills/codex-consult/SKILL.md]] と対になる「**外部接続**の委譲」。

## 1. いつ使うか（トリガー）

- **Google Tasks / Calendar をその場で確認**：「今の未完了タスクは？」「明日の予定は？」（Inbox 未生成・最新が欲しい時）
- **Slack を検索させる**：「#proj-a-* で先週の "納期" を含む発言」「@the user への未読 mention」「このスレッドの結論」
- **Notion を読む**：清書版 KB の特定ページ参照（公開は一方向だが read は可）
- **GitHub を読む**：他リポのコード / PR / commit / issue をその場で確認（例「`your-org/proj-a-repo` の最新コミット」「この repo の README」）。GitHub MCP は hermes 所有なので Claude 直読み不可 → pull で委譲。**定常のコード変化取得は on-demand `github-eod-capture`（push → `Inbox/{YYYY-MM-DD}/code/`）に任せ、pull は「今すぐ・特定リポ」用途に限る**
- **Web の軽い確認**を hermes 側で完結させたい時（広域調査は `general-purpose` subagent が原則）

### 使わない場面

- **定常取り込み**で足りる → on-demand capture（push）に任せる。毎回 pull しない。
- **Vault ノートの作成・編集** → Claude が直接（hermes に投げない）。
- **外部システムへの書き込み・破壊的操作** → このスキルの既定スコープ外。必要なら明示的に範囲を切り、ユーザー承認を取る（[[.claude/rules/agent-boundaries.md]] §5 承認ティア）。
- **コード作業** → Codex（[[.claude/skills/codex-consult/SKILL.md]]）。

## 2. 呼び出し方

`hermes chat -q` が非対話ワンショット。

```bash
hermes chat -q "<hermes への指示>" -Q --source claude-code
```

- `-q/--query`：単発クエリ（非対話）
- `-Q/--quiet`：バナー・スピナー抑制（出力をパースしやすく）
- `--source claude-code`：セッション元タグ（追跡用）
- 必要なら `-s <skill>` で hermes 側スキルを事前ロード（例 `-s google-tasks`）

**タイムアウト**：LLM セッション + 外部 API 呼び出しで 30–120 秒かかる。Bash ツールの `timeout` を `180000`（3 分）程度に。

**⚠️ 文字コード（日本語 Windows のみ必須）**：`hermes`（Python）は子プロセス出力を既定のロケールエンコーディング（日本語 Windows では **cp932**）でデコードするため、`’`（U+2019）等の非 cp932 文字が混じると `UnicodeDecodeError` でリーダースレッドが死に、**rc=0 なのに stdout が空 / 欠落**する（エラーにならず気づきにくい）。呼び出し前に **`PYTHONUTF8=1`** を必ず設定（UTF-8 モード強制。PowerShell なら `$env:PYTHONUTF8 = '1'`）。恒久化は User 環境変数 `PYTHONUTF8=1`。

```bash
# 日本語 Windows での呼び出し形（PATH に通った hermes を使うのが第一。
# フルパスが要る場合もユーザ名をハードコードせず $USERNAME 等で組む）
PYTHONUTF8=1 hermes chat -q "<指示>" -Q --source claude-code
```

### 指示の書き方（重要）

hermes は自律エージェントなので、**何を・どこから・どう返すか**を明示する：

1. **タスク**：例「Google Tasks の未完了タスクを一覧して」
2. **ソース指定**：どの接続か（Slack の channel 名 / Tasks のリスト / Notion ページ）
3. **戻し方**：
   - **transient（その場参照）**：「結果を簡潔に**標準出力に**返して。ファイルは作らないで」→ Claude が stdout を読む
   - **durable（残す）**：「生のまま `Inbox/{YYYY-MM-DD}/slack/{slug}.md` に書いて、パスだけ返して」→ Inbox 経由（[[.claude/rules/inbox-routing.md]]）。**curated へ直接書かせない**

## 3. 結果の統合（Output Contract）

- **transient**：stdout を読み、結論を会話に統合（CLAUDE.md §4 の出力契約：結論→根拠→次アクション）。
- **durable**：hermes が `Inbox/` に置いたファイルを Claude が curate（move/蒸留は通常フロー。宛先判断は Daily 集約／EOD 配分で Claude が判断）。
- **失敗時**（未認証・接続不可・タイムアウト・**出力空**）：hermes の stderr/末尾メッセージを 1 行で要約し、原因（auth 失効？ **rc=0 で出力空なら cp932（日本語 Windows）** → `PYTHONUTF8=1`）と次アクションを提示。`hermes doctor` / `hermes status` で切り分け可。※`chat -q` は単発スタンドアロンなので gateway 稼働は不要（gateway 停止は pull 失敗の原因ではない）。

## 4. 境界（守ること）

- **push を pull で置き換えない**：定常データは on-demand capture（push）に任せ、pull は「今すぐ・特定の」確認に限る。
- **Inbox 原則を守る**：残すべきデータは hermes に **`Inbox/` へ書かせる**。curated への直接書き込みは禁止（single-writer / [[.claude/rules/agent-boundaries.md]]）。
- **read/query 既定**：外部への書き込み・送信は明示スコープ + 承認。
- **接続は複製しない**：Claude が直接 Slack/GWS/Notion を叩こうとしない。必ず hermes 経由。

## 関連

- [[.claude/rules/agent-boundaries.md]] — 3 エージェント分担・接続所有・push/pull 経路
- [[.claude/rules/inbox-routing.md]] — durable 結果の置き場（Inbox）
- [[.claude/skills/codex-consult/SKILL.md]] — 対になる委譲（コード→Codex）
- [Hermes Agent（upstream）](https://github.com/NousResearch/Hermes-Agent) — hermes CLI リファレンス（`hermes chat -q` 他）
- [[docs/connections/README.md]] — 各接続のセットアップ・トラブルシューティング
