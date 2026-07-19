---
title: "接続ガイド: AI 議事録(Genspark / Otter / tl;dv / Notta 等)"
type: "reference"
status: "completed"
tags: ["setup", "connections", "meetings"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: AI 議事録(難易度 ★☆☆〜★★☆)

会議の AI 文字起こしを vault に取り込む経路です。**どのサービスを使っていても乗れます** — この vault の議事録パイプラインは「`Inbox/{date}/mtgs/` に transcript の Markdown が置かれること」だけを前提にしているからです。

```
[議事録サービス]
   │ 取り込み(自動 or エクスポート→手動)
   ▼
Inbox/{date}/mtgs/{slug}.md
   │ 「MTG 集約やって」(aggregate-mtgs)
   ▼
Daily に要約 bullet → EOD distill で要約が Work/{project}/meetings/ へ
```

| 経路 | サービス | 難易度 | 自動化度 |
|---|---|---|---|
| **A. Genspark アダプタ(同梱)** | Genspark AI ミーティングノート | ★★☆ | 高(`gsk` CLI で一括取得) |
| **B. エクスポート → Inbox 投入** | Otter / tl;dv / Notta / Zoom AI / Gemini メモ 等**何でも** | ★☆☆ | 手動(1 会議 30 秒) |

## 1. 何ができるようになるか

- 会議ごとの transcript が `Inbox/{date}/mtgs/` に 1 ファイルで溜まる
- 「MTG 集約やって」で Daily に要点 bullet(決定事項・アクションアイテム)が入る
- EOD distill で**要約が** `Work/{project}/meetings/{date}-{topic}.md` に配置される(raw transcript を Main DB に持ち込まない設計・話者名は `Maps/People-Map.md` で名寄せ)
- 会議前の叩き台作成(`mtg-prep`)とセットで「会議前→会議後」が閉じる

## 2. 経路 A:Genspark アダプタ(同梱)

`gsk` CLI で完了済み会議を一括取得する自動化経路です。手順・動作確認・躓きは専用ガイドへ:

→ **[genspark.md](./genspark.md)**

## 3. 経路 B:エクスポート → Inbox 投入(サービス不問)

1. 使っているサービス(Otter / tl;dv / Notta / Zoom AI Companion / Google Meet の Gemini メモ等)で transcript を **Markdown またはテキストでエクスポート**
2. `Inbox/{今日の日付}/mtgs/{会議名スラグ}.md` に置く(Claude Code に「この議事録 mtgs に入れて」と貼り付けても OK。frontmatter は Claude が付けます)
3. 最低限の frontmatter(手で書く場合):

   ```yaml
   ---
   type: "capture"
   status: "inbox"
   meeting_title: "会議名"
   meeting_date: 2026-07-19
   participants: ["Alice", "Bob"]
   source: "manual"
   ---
   ```

4. あとは共通:「MTG 集約やって」→ EOD distill

> **定常運用を自動化したくなったら**:サービスに API / エクスポート webhook があれば、[[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]] をひな形に capture skill を自作できます(Claude に「{サービス名} 用の議事録 capture skill を設計して」)。原則は同じ:**capture only・`Inbox/{date}/mtgs/` にのみ書く・filename 冪等**。

## 4. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| 集約されない | 集約は自動で走りません(on-demand 既定)。「MTG 集約やって」と指示 |
| どのプロジェクトの会議か判定されない | 正常です(capture 段階では判定しない設計)。EOD distill 時に Claude + あなたが宛先を決めます。会議タイトルに `[PROJ_A]` 等の prefix を付けておくとヒントになります |
| 話者名が微妙に違う | AI 文字起こしの同音異字は仕様。`Maps/People-Map.md` に正しい名前を登録しておくと distill 時に名寄せされます |

## 5. 関連

- [genspark.md](./genspark.md) — 経路 A(Genspark アダプタ)の詳細
- [[.claude/skills/aggregate-mtgs/SKILL.md]] — Daily への集約側
- [[.claude/skills/mtg-prep/SKILL.md]] — 会議前の叩き台作成
- [[.claude/rules/inbox-routing.md]] §3.3 — 議事録だけ「要約して meetings/ へ」の例外である理由
