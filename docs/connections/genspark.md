---
title: "接続ガイド: Genspark AI 議事録"
type: "reference"
status: "completed"
tags: ["setup", "connections", "genspark", "meetings"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: Genspark AI 議事録(難易度 ★★☆・約15–30分)

Genspark の AI ミーティングノート(会議の自動文字起こし)を vault に取り込む経路です。会議が多い人向けの任意接続で、**Genspark を使っていないなら丸ごとスキップして構いません**(他の議事録サービスを使う場合は、エクスポートを `Inbox/{date}/mtgs/` に手動で置けば同じパイプラインに乗ります)。

## 1. 何ができるようになるか

- **push(on-demand capture)**:「Genspark 議事録取り込みやって」で、今日+前日の完了済み(`COMPLETED`)会議の transcript が **1 会議 = 1 ファイル**で `Inbox/{date}/mtgs/genspark-{slug}.md` に落ちる
- EOD distill 時に**要約されて** `Work/{project}/meetings/{date}-{topic}.md` に配置される(生 transcript を Main DB に持ち込まない、この vault で唯一の例外運用)
- 朝の briefing に「今日の会議一覧 + どれに Genspark を join させるか」のリマインダーが出る

## 2. 前提

- Genspark アカウント(AI ミーティングノート機能が使えるプラン)
- `gsk` CLI(Genspark CLI)が Hermes の動く環境にインストール・ログイン済みであること
- **どの会議に bot を参加(join)させるかは Genspark の Web UI でしか操作できません**(CLI 不可)。取り込みの自動化はできても、join の取捨選択は毎回 Web UI での手動操作です — ここは仕様として割り切ってください

## 3. 手順

1. Genspark Web UI で AI ミーティングノートを設定(カレンダー連携 → 会議に bot を join させる)
2. `gsk` CLI をセットアップし、ログイン:

   ```bash
   gsk meeting list   # 会議一覧が返ればログイン OK
   ```

3. Hermes から見える PATH に `gsk` があることを確認(capture skill は `gsk meeting list` / `gsk meeting get` を呼びます)

## 4. 動作確認

会議を 1 件 Genspark に join させて完了させた後、Claude Code に:

```text
Genspark 議事録取り込みやって
```

→ `Inbox/{今日の日付}/mtgs/genspark-{会議名slug}.md` ができれば完了。「MTG 集約やって」で Daily への集約まで確認できます。

特定の会議だけ取りたい場合は task_id 指定もできます(「task_id XXX の議事録取って」)。

## 5. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| `gsk meeting list` に会議が出ない | その会議に bot を join させていない(Web UI で join 選択)。**join した会議しか一覧に出ません** |
| 取り込みが走ったのにファイルが増えない | 会議がまだ `COMPLETED` になっていない(Genspark 側の処理待ち)、または既に同名ファイルがあり skip された(冪等性・正常) |
| 同じ会議を二重取得しそうで不安 | ファイル名ベースの冪等性なので、何度実行しても既存は skip されます。polling 的に叩いても安全 |
| 話者名が微妙に間違っている | AI 文字起こしの同音異字は仕様。EOD distill 時に `Maps/People-Map.md` で名寄せする運用です |

## 6. 深掘り

- [[.hermes/skills/mymemory/genspark-mtg/SKILL.md]] — capture skill 本体(recency 窓・冪等性・task_id 指定)
- [[.claude/skills/mtg-prep/SKILL.md]] — 会議前の叩き台準備(こちらは Claude 側)
- [[.claude/rules/inbox-routing.md]] §3.3 — genspark 議事録だけ「要約して meetings/ へ」の例外である理由
