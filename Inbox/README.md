---
title: "Inbox — capture receiving zone"
type: "note"
status: "in-progress"
tags: ["moc", "inbox"]
created: 2026-01-01
updated: 2026-01-01
---

# Inbox — capture receiving zone

外部ソースの生 capture（未整理）の受け口。書き手は **Hermes と Obsidian ブラウザ拡張のみ**。Claude / Codex / ユーザーは**書かない**。

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
| mtgs | `Inbox/{date}/mtgs/{slug}.md`（AI 議事録。Genspark は `genspark-{slug}.md`） |
| clippings | `Inbox/{date}/clippings/{slug}.md`（Web クリップ） |
| chat-logs | `Inbox/{date}/chat-logs/{provider}-{slug}.md`（ChatGPT / Claude 壁打ち） |
| mail | `Inbox/{date}/mail/{slug}.md`（Gmail・**on-demand のみ**。定常 capture なし） |
| attachments | `Inbox/{date}/attachments/…` |

## ライフサイクル

```
[External source]
   │ (1) capture — Hermes / 拡張
   ▼
Inbox/{date}/{source}/{file}.md      ← ここ
   │ (2) aggregate — Claude が当日中に Daily へ集約
   ▼
Daily/{date}.md                       ← 唯一のハブ
   │ (3) distribute — EOD distill で Main DB へ蒸留・配分
   ▼
Work / Research / Others              → Evergreen
```

詳細は [[.claude/rules/inbox-routing.md]] / [[.claude/rules/daily-operations.md]] / [[.claude/rules/agent-boundaries.md]]。

## 注意

- **auto-route なし**：channel / file content による振り分けは Daily 集約と EOD distill で人＋Claude が行う
- **single-writer**：capture した file は、Claude が Daily へ集約した後は Claude + ユーザー所有。Hermes は二度触らない
- このフォルダの中身は **git に commit しない方針もアリ**（生 capture が肥大化する場合）。`.gitignore` 側で `Inbox/**` を除外する選択肢もある
