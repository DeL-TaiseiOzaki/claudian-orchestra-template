---
title: "Inbox — capture receiving zone"
type: "note"
status: "in-progress"
tags: ["moc", "inbox"]
created: 2026-01-01
updated: 2026-07-20
---

# Inbox — capture receiving zone

外部ソースの生 capture（未整理）の受け口。書き手は **Hermes と capture extension のみ**。コアエージェントとユーザーは**直接書かない**。

## レイアウト（date-first）

```
Inbox/{YYYY-MM-DD}/{daily,slack,discord,code,mtgs,clippings,chat-logs,mail,attachments}/
```

| source | 着地パス |
|---|---|
| daily | `Inbox/{date}/daily/daily.md`（GCal + GTasks 朝 capture） |
| slack | `Inbox/{date}/slack/{channel}.md`（DM は `dm-{counterpart}.md`） |
| discord | `Inbox/{date}/discord/{channel}.md`（bot 参加サーバのみ・skill は自作） |
| code | `Inbox/{date}/code/code.md`（github-eod-capture） |
| mtgs | `Inbox/{capture-date}/mtgs/{provider}-{slug}.md`（AI 議事録。Genspark は任意 adapter） |
| clippings | `Inbox/{date}/clippings/{slug}.md`（Web クリップ） |
| chat-logs | `Inbox/{date}/chat-logs/{provider}-{slug}.md`（ChatGPT / Claude 壁打ち） |
| mail | `Inbox/{date}/mail/{slug}.md`（Gmail・**on-demand のみ**。定常 capture なし） |
| attachments | `Inbox/{date}/attachments/…` |

> **chat-logs の normalize**:capture 時の frontmatter は `source: <provider>`（例:`chatgpt` / `claude`）のまま。compiled note を新規作成する場合は `source: chat:<provider>:<id>` 等へ正規化し、標準 enum を使う。
>
> `Wiki/sources/**` へ移した raw file は immutable source なので `type: capture` / `status: inbox` を維持する。標準 enum へ変換するのは raw とは別に作る compiled / curated note だけ。meeting transcript は provider を問わず compiled meeting note を別作成し、raw は `Wiki/sources/` へ移さず git 履歴に残す。

## ライフサイクル

```
[External source]
   │ (1) capture — Hermes / 拡張
   ▼
Inbox/{date}/{source}/{file}.md      ← ここ
   │ (2) aggregate — コアエージェントが当日中に Daily へ集約
   ▼
Daily/{date}.md                       ← 唯一のハブ＝人間の監査点
   │ (3) distribute — EOD distill で Main DB へ蒸留・配分
   ▼
Wiki                                  → Evergreen
```

詳細は [[.codex/rules/inbox-routing.md]] / [[.codex/rules/daily-operations.md]] / [[.codex/rules/agent-boundaries.md]]。

## 注意

- **auto-route なし**：channel / file content による振り分けは Daily 集約と EOD distill で人＋コアエージェントが行う
- **single-writer**：capture file の正確な wikilink が Daily に入った時点でコアエージェント + ユーザーへ handoff。以後 Hermes は修復・追記・再作成しない
- raw capture を git 対象外にする運用は、meeting transcript の commit retention を使わない場合に限る。meeting capture を使う場合は `Inbox/**` 全体を ignore しない。compiled meeting note 作成後に raw と同内容が git 履歴へ commit 済みであることを確認し、ユーザー承認がある場合だけ作業ツリーから削除する
