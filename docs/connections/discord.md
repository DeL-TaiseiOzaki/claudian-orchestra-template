---
title: "接続ガイド: Discord"
type: "reference"
status: "completed"
tags: ["setup", "connections", "discord"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: Discord(難易度 ★★☆・約30分)

コミュニティ・研究グループの会話が Discord で進む人向け。Slack と同じ思想で、自分に関係する会話の日次ダイジェストを `Inbox/{date}/discord/{channel}.md` に落とします。

> ⚠️ **最重要の制約:bot 方式のみ**です。個人アカウントのトークンで会話を取得する行為(self-bot)は **Discord の利用規約違反**で、アカウント停止のリスクがあります。このガイドは「**自分が bot を追加できるサーバ**」だけを対象にします。bot を入れられないサーバの会話は、必要なときに手動コピーで `Inbox/{date}/discord/` に置いてください。

## 1. 何ができるようになるか

- bot が参加しているチャンネルの当日メッセージ(自分の発言・メンション中心)を日次ダイジェスト化 → `Inbox/{date}/discord/{channel}.md`
- 「Discord 集約やって」で Daily へ(集約・distill の扱いは Slack と同じ:コミュニティ系は `Others/Activities/{NAME}/sources/` へ落ちるのが典型)

> **正本は Discord のまま**。vault に落ちるのはログの写しです(Slack と同じ設計・[[.claude/rules/agent-boundaries.md]] §2)。

## 2. 前提

- 対象サーバで **bot を追加できる権限**(自分のサーバ、または管理者に依頼できるコミュニティ)
- **capture skill はテンプレに未同梱**です(Slack ほど利用者が多くないため)。セットアップの最後に、同梱の [[.hermes/skills/vault-capture/slack-capture/SKILL.md]] をひな形に自分用の `discord-capture` skill を生成します(Claude が手伝います)

## 3. 手順

1. **bot を作成**:[discord.com/developers/applications](https://discord.com/developers/applications) → New Application → Bot
2. **Message Content Intent を有効化**:Bot 設定 → Privileged Gateway Intents → **MESSAGE CONTENT INTENT** を ON(これが無いと本文が取れません)
3. **読み取り専用で招待**:OAuth2 → URL Generator → scope `bot`、権限は `View Channels` + `Read Message History` のみ → 生成 URL でサーバに追加
4. **トークンを登録**:`.hermes/.env`(gitignore 済み)に

   ```bash
   DISCORD_BOT_TOKEN=xxxx
   ```

5. **capture skill を生成**:Claude Code に

   ```text
   slack-capture をひな形に discord-capture skill を作って
   ```

   と頼む。原則は Slack と同じ(**capture only・`Inbox/{date}/discord/` にのみ書く・1 日 1 チャンネル 1 ファイル・冪等**)。Discord API は `GET /channels/{id}/messages` で当日分を取得します

## 4. 動作確認

```bash
hermes chat -q "Discord bot で参加サーバとチャンネル一覧を確認して" -Q
```

→ 「Discord 取り込みやって」→ `Inbox/{今日の日付}/discord/` にファイルができれば完了。

## 5. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| 本文が空で取れる | **MESSAGE CONTENT INTENT** が OFF(手順 2)。Developer Portal で ON にして bot を再起動 |
| チャンネルが見えない | bot にそのチャンネルの `View Channels` 権限がない(ロール / チャンネル個別権限を確認) |
| 入れないサーバの会話も取りたい | **やらない**(self-bot は規約違反)。必要な部分だけ手動コピーで `Inbox/{date}/discord/` へ |
| DM を取りたい | bot は自分宛の DM しか見えません。個人 DM の capture は仕様上不可と割り切る |

## 6. 関連

- [[.hermes/skills/vault-capture/slack-capture/SKILL.md]] — 生成時のひな形(設計原則の正本)
- [slack.md](./slack.md) — 同型の接続(ダイジェスト設計の参考)
- [[.claude/rules/inbox-routing.md]] — Inbox 着地の規約
