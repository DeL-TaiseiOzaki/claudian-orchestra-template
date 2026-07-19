---
title: "Home — vault entry"
type: "note"
status: "in-progress"
tags: ["moc"]
created: 2026-01-01
updated: 2026-01-01
---

# 🏠 Home — your vault

vault 全体の入口（MOC）。アーキテクチャ全景は [[README.md]]、運用契約は [[CLAUDE.md]]。

## 📅 今日

- Daily: `Daily/{YYYY-MM-DD}.md`（朝 `daily-briefing` で生成）
- 週次: `Daily/Weekly-{YYYY-WXX}.md`（月曜朝 `weekly-review`）

## 🗂️ ドメイン入口

| 領域 | 入口 |
|---|---|
| Inbox（capture） | [[Inbox/README.md]] |
| Daily（ジャーナル） | [[.claude/rules/daily-operations.md]] |
| Wiki（汎用ナレッジ — アイデア / 学習・読書 / 文献・実験 / 活動記録） | [[Wiki/AGENTS.md]] |
| Persona（著者プロフィール・全体共通） | [[Persona/AGENTS.md]] |
| Maps（横断 MOC） | [[Maps/Code-Map.md]]（コード知識） / [[Maps/People-Map.md]]（関わる人・名寄せ） |
| Meta（vault 自己言及） | [[Meta/README.md]] |
| Archive（退避） | [[Archive/README.md]] |

## 👁️ 5 つの顔（Bases ビュー）

Vault を別角度から見るラベル（[[README.md]] §2）。フォルダではなく **frontmatter 駆動のビュー**として実装する。

| ラベル | ビュー | 何が見えるか |
|---|---|---|
| Logs | [[Maps/views/logs.base\|logs.base]] | 時系列の記録（Daily / Weekly） |
| Knowledge | [[Maps/views/knowledge.base\|knowledge.base]] | 蓄積された知識（note / reference / paper） |
| Memories | [[Maps/views/memories.base\|memories.base]] | 経験・出来事（log + meetings の横断タイムライン） |
| SPK | [[Maps/views/spk.base\|spk.base]] | 蒸留済み evergreen（`status: completed`） |
| —（作業台） | [[Maps/views/inbox-queue.base\|inbox-queue.base]] | curation 待ちキュー |

> 5 つ目のラベル **Markdown Notes** は「すべてが md である」という vault 全体の性質そのものなので、ビューは持たない。
