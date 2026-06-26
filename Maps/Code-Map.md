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

## Work（受託案件）

各案件のコード知識は `Work/{案件}/code/` に置き、ここから繋ぐ。

- **PROJ_A**（Client A）：[[Work/PROJ_A/code/README.md]]
  - 例：`https://github.com/your-client-org/proj-a-pipeline`
- **PROJ_B**（Client B）：（このテンプレでは未作成）
- **PROJ_C**（Client C）：（このテンプレでは未作成）

## Research

submodule で外部研究リポをマウントしている場合はそちらの code-map を継承する：

- [[Research/CLAUDE.md]]

## Others / Tools

自作ツール・社内 OSS・コンテスト用リポなどはここに繋ぐ。

- 例：`https://github.com/your-org/your-tool` → `[[Others/Activities/{topic}/code/README.md]]`

## 使い方

新規リポを把握対象に加えるとき：

1. 該当ドメインの `code/` 配下に `{repo-name}.md` を作る（テンプレ：[[Templates/code-note.md]]）。
2. `code/README.md` を更新してリポ → 読解メモの索引に追記する。
3. 本ファイル（`Maps/Code-Map.md`）にも繋ぐ。

`github-eod-capture` skill は **本ファイルに載っている repo を巡回する** ので、捕捉対象を増やすときは必ずここに書く。
