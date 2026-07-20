---
title: "Meta — vault 自身についてのすべて"
type: "note"
status: "in-progress"
tags: ["moc", "meta"]
created: 2026-01-01
updated: 2026-07-20
---

# Meta — vault 自身についてのすべて

vault「について」のものはすべてここに集約する（vault の「中身」= 知識は `Wiki/`、日々の記録は `Daily/`）。

## 構成

| パス | 中身 |
|---|---|
| `Meta/connections/` | **外部接続のセットアップガイド**（接続ごとの手順・動作確認・トラブルシューティング）。入口は [[Meta/connections/README.md]]、全体導線は [[GETTING-STARTED.md]] |
| `Meta/assets/` | リポジトリ用アセット（README のアーキテクチャ図など） |
| `Meta/{project-name}/` | **自己言及プロジェクト**（再アーキテクチャ・pipeline 改修・スキーマ移行など）。1 プロジェクト = 1 サブフォルダ |

## 規約

- 自己言及プロジェクトは **1 プロジェクト = 1 サブフォルダ**（例：`Meta/rearchitecture/`）
- 完了したら `Archive/Meta/{project-name}/` へ退避（`status: archived`）
- ここは Main DB（Wiki）への蒸留対象ではない（EOD distill のスコープ外）

## 関連

- [[GETTING-STARTED.md]] / [[Meta/connections/README.md]]
- [[.codex/skills/vault-archive/SKILL.md]] — 完了プロジェクトの Archive 退避
