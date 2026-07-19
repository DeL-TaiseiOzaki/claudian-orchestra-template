---
title: "Code Map — repo knowledge cross-index"
type: note
status: in-progress
tags:
  - code
created: 2026-01-01
updated: 2026-01-01
---

# 🗺️ Code Map

コードベース**知識**の単一入口（MOC）。**コード本体の正本は GitHub**。
ここには各リポの「構造・設計判断・読解メモ」への**リンクを集約**する（詳細ノートは各ドメイン側に置く）。
他リポは Hermes 経由の GitHub MCP で**読み取り**し、その理解をドメインのノートに残してここから繋ぐ。

## Wiki / Tools

自作ツール・社内 OSS・コンテスト用リポなどはここに繋ぐ（読解ノートは `Wiki/` に `type: note` で置く）。

- 例：`https://github.com/your-org/your-tool` → `[[Wiki/your-tool-code.md]]`（コード読解ノートの例・未作成）

## 使い方

新規リポを把握対象に加えるとき：

1. `Wiki/` 配下に `{repo-name}.md` の読解ノートを作る（テンプレ：[[Templates/code-note.md]]）。
2. 本ファイル（`Maps/Code-Map.md`）にも繋ぐ。

`github-eod-capture` skill は **本ファイルに載っている repo を巡回する** ので、捕捉対象を増やすときは必ずここに書く。
