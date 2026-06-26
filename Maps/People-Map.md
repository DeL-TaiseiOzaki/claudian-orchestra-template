---
title: "People Map — name reconciliation"
type: note
status: in-progress
tags:
  - moc
  - reconciliation
created: 2026-01-01
updated: 2026-01-01
---

# 👥 People Map

vault 横断で参照される **人物の名寄せ表**。Genspark などの AI 文字起こしは同音異字を誤記しがち（「ヤマダ」→「山田田」→ 実際は「山田 太郎」など）。`eod-distill` skill が会議録をマージするとき、本ファイルを正準名のソースとして参照する。

> このテンプレートには **エントリは入れていない**。実 vault では運用しながら、ここに正準名と alias を埋めていく。

## エントリのフォーマット

```markdown
### 山田 太郎（Yamada Taro）

- 正準名：山田 太郎
- alias：やまだ / Taro Yamada / @yamada（Slack）
- ロール：Client A の窓口
- 関連：[[Work/PROJ_A/team.md]] / [[Work/PROJ_A/meetings/]]
- 備考：transcript で「ヤマダ」→「山田田」に化けるケースあり。要正準化。
```

## 使い方

1. Daily / Meeting note で初登場した人物名は、`eod-distill` が本ファイルへの追記を提案する。
2. 既存エントリの alias 列に追加するだけで終わるケースが多い（新規 entry は丁寧に書く）。
3. transcript / Slack で AI が誤記したと思われる名前は **alias に集めて**、正準名を 1 つに収束させる。

## 関連

- [[.claude/skills/eod-distill/SKILL.md]] — 話者名の名寄せ機構
- [[.claude/skills/aggregate-mtgs/SKILL.md]] — 会議メモへの aggregate 時にも本ファイルを参照
