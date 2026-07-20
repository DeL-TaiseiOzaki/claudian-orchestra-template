---
title: "接続ガイド: AI 議事録(Genspark / Otter / tl;dv / Notta 等)"
type: "reference"
status: "completed"
tags: ["setup", "connections", "meetings"]
created: 2026-07-19
updated: 2026-07-20
---

# 接続ガイド: AI 議事録(難易度 ★☆☆〜★★☆)

会議の AI 文字起こしを vault に取り込む経路です。**どのサービスを使っていても乗れます** — この vault の議事録パイプラインは「`Inbox/{date}/mtgs/` に transcript の Markdown が置かれること」だけを前提にしているからです。

```
[議事録サービス]
   │ 取り込み(Hermes adapter または export→capture extension)
   ▼
Inbox/{capture-date}/mtgs/{provider}-{slug}.md
   │ 「MTG 集約やって」(inbox-aggregate)
   ▼
Daily に要約 bullet → EOD distill で要約が Wiki/meetings/ へ
```

| 経路 | サービス | 難易度 | 自動化度 |
|---|---|---|---|
| **A. Genspark アダプタ(任意・同梱)** | Genspark AI ミーティングノート | ★★☆ | 高(`gsk` CLI で一括取得) |
| **B. エクスポート → Inbox 投入** | Otter / tl;dv / Notta / Zoom AI / Gemini メモ 等**何でも** | ★☆☆ | 手動(1 会議 30 秒) |

## 1. 何ができるようになるか

- 会議ごとの transcript が `Inbox/{date}/mtgs/` に 1 ファイルで溜まる
- 「MTG 集約やって」で Daily に要点 bullet(決定事項・アクションアイテム)が入る
- EOD distill で**要約が** `Wiki/meetings/{date}-{topic}.md` に配置される(raw transcript を Main DB に持ち込まず、commit 済み確認まで Inbox に保持する。話者名は `Maps/People-Map.md` で名寄せ)
- 会議前の叩き台作成(`mtg-prep`)とセットで「会議前→会議後」が閉じる

## 2. 経路 A:Genspark アダプタ(同梱)

`gsk` CLI で完了済み会議を一括取得する自動化経路です。手順・動作確認・躓きは専用ガイドへ:

→ **[genspark.md](./genspark.md)**

## 3. 経路 B:エクスポート → Inbox 投入(サービス不問)

1. 使っているサービス(Otter / tl;dv / Notta / Zoom AI Companion / Google Meet の Gemini メモ等)で transcript を **Markdown またはテキストでエクスポート**
2. Obsidian capture extension / Local REST API、または Hermes への on-demand 指示で `Inbox/{capture-date}/mtgs/{provider}-{会議名スラグ}.md` に**新規 capture**する。ユーザーとコアエージェントは Inbox へ直接書かない
3. capture 側が付ける frontmatter:

   ```yaml
   ---
   title: "会議名"
   type: "capture"
   status: "inbox"
   tags: ["meeting", "otter"]
   created: 2026-07-20
   updated: 2026-07-20
   source: "otter:meeting:<stable-id>"
   meeting_title: "会議名"
   meeting_date: 2026-07-19
   participants: ["Alice", "Bob"]
   provider: "otter"
   transcript_length: 12345
   ---
   ```

   `otter` は実際の provider slug に置き換える。手動 export でも filename、`source`、`provider` に元サービスを残す。

4. あとは共通:「MTG 集約やって」→ EOD distill

> API / webhook adapter を追加する場合は [[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]] をひな形にできます。原則は **capture only・capture-event date・`{provider}-{slug}.md`・source ID 冪等・Daily handoff 後は変更しない**。

## 4. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| 集約されない | 集約は自動で走りません(on-demand 既定)。「MTG 集約やって」と指示 |
| 話者名が微妙に違う | AI 文字起こしの同音異字は仕様。`Maps/People-Map.md` に正しい名前を登録しておくと distill 時に名寄せされます |

## 5. 関連

- [genspark.md](./genspark.md) — 経路 A(Genspark アダプタ)の詳細
- [[.codex/skills/inbox-aggregate/SKILL.md]] — Daily への集約側
- [[.codex/skills/mtg-prep/SKILL.md]] — 会議前の叩き台作成
- [[.codex/rules/inbox-routing.md]] §3.3 — 議事録だけ「要約して meetings/ へ」の例外である理由
