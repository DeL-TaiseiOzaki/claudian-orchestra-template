---
title: "接続ガイド: Slack"
type: "reference"
status: "completed"
tags: ["setup", "connections", "slack"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: Slack(難易度 ★★★・約30–60分)

業務会話が Slack で進む人向けの本命接続です。繋がると、自分が**発言した / @mention された**メッセージの日次ダイジェストが `Inbox/{date}/slack/{channel}.md` に落ち、Daily → Work ログへと流れます。

難易度が高めなのは **Slack app を自分で作り、2 種類のトークン(Bot + User)を発行する**必要があるためです。順番にやれば 30 分程度です。

## 1. 何ができるようになるか

- **push(日次 capture)**:「Slack 取り込みやって」で、当日(または前日)の自分の発言・mention をチャンネルごとにダイジェスト化 → `Inbox/{date}/slack/{channel}.md`(DM は `dm-{相手}.md`)
- **pull(検索)**:「#proj-a で先週の『納期』を含む発言探して」のようなその場の検索
- (任意)Hermes の Slack app を通じて **Slack から Hermes に話しかける**双方向 IF

> **正本は Slack のまま**です。vault に落ちるのはログの写し。会話の続きは Slack でやります([[.claude/rules/agent-boundaries.md]] §2)。

## 2. 前提

- 対象 workspace に **Slack app をインストールできる権限**(管理者に承認を依頼できれば可)
- リアクションや編集履歴は取り込みません(ノイズ削減のための仕様)

## 3. 手順

### 3.1 Slack app を作る

1. [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → From scratch → 名前(例:`hermes-assistant`)と workspace を選択
2. **OAuth & Permissions** を開き、2 種類のスコープを設定:

   **Bot Token Scopes**(チャンネル / DM の履歴取得用):

   ```
   chat:write, app_mentions:read, channels:history, groups:history,
   im:history, im:read, im:write, users:read, files:read
   ```

   **User Token Scopes**(横断検索 = 「今日の自分の発言」用):

   ```
   search:read, users:read
   ```

3. **Install to Workspace** でインストール → 2 つのトークンをコピー
   - Bot User OAuth Token(`xoxb-...`)
   - User OAuth Token(`xoxp-...`)

### 3.2 Hermes に登録

`.hermes/.env`(gitignore 済み)に追記:

```bash
SLACK_BOT_TOKEN=xoxb-...
SLACK_USER_TOKEN=xoxp-...
SLACK_ALLOWED_USERS=U0XXXXXXX   # 自分の Slack user ID(プロフィール → メンバー ID)
```

Hermes を再起動し、双方向 IF を使う場合は `hermes slack add-workspace` で gateway を設定します。

### 3.3 Bot をチャンネルに入れる

Bot トークンで履歴を読めるのは **bot が参加しているチャンネルだけ**です。capture したいチャンネルで `/invite @hermes-assistant` を実行してください(横断検索の方は User トークンなので招待不要)。

## 4. 動作確認

**pull**:

```bash
hermes chat -q "Slack で今日の自分の発言を探して" -Q
```

**push(パイプライン全体)**:コアエージェントに

```text
Slack 取り込みやって
```

→ `Inbox/{今日の日付}/slack/` にチャンネルごとの md ができる → 「Slack 集約やって」で Daily に反映されれば完了です。

## 5. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| `not_allowed_token_type` | 検索(`search.messages`)を **Bot トークンで叩いている**。検索は User トークン(`xoxp-`)専用。`SLACK_USER_TOKEN` を設定する |
| `not_in_channel` | bot がそのチャンネルに未参加。`/invite` する。なお public チャンネルは一覧には出るが、参加するまで履歴は読めない(仕様) |
| スコープを追加したのに反映されない | スコープ変更後は **Reinstall to Workspace** が必要。さらにトークンが再発行される場合があるので `.env` を貼り直し、**Hermes を再起動** |
| DM が取れない | Bot Token Scopes に `im:history` / `im:read` が無い、または User トークン検索のみで運用している(DM 本文は bot 経路) |
| 前日分を取り直したい | 「昨日の Slack 取り込みやって」(翌朝 catch-all)。既存ファイルはより情報量の多い方を保持するマージ仕様 |

## 6. 深掘り

- [[.hermes/skills/vault-capture/slack-capture/SKILL.md]] — capture skill 本体(Bot / User トークンの使い分け・検索クエリの組み方)
- 複数 workspace を情報源にしたい → [[.hermes/skills/vault-capture/slack-capture/references/multi-workspace-user-token-capture.md]]
- [[.claude/rules/inbox-routing.md]] §5 — Slack capture の設計(なぜ channel→project の自動振り分けをしないか)
