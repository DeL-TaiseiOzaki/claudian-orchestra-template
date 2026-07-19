---
name: vault-github-sync
description: Back up and sync the Obsidian vault to GitHub (your-org/your-vault) via one-way local→GitHub push, treating the local copy as the source of truth. Use when committing/pushing vault changes or running the backup sync.
---

# Vault GitHub Sync Skill

## 目的

Obsidian Vault（`<vault root>`）を GitHub `https://github.com/your-org/your-vault` に **Vault → GitHub の一方向 push** で同期する。
ローカルが常に「正」、GitHub はバックアップ + 共有用途。

## 同期方針

| 項目 | 値 |
|------|---|
| 方向 | Vault → GitHub の一方向（基本 pull はしない） |
| 頻度 | 日次 + 重要な節目（納品・論文ノート完成など） |
| ブランチ | `main` |
| Remote | `origin` = `https://github.com/your-org/your-vault.git` |

別マシン・他人の書き込みは想定しない。万が一リモートが進んでいた場合のみ手動で `git pull --rebase` してから再 push。

## 日次運用

### Step 1: 状態確認

```bash
git status --short
```

### Step 2: 内容別にステージ

雑多に `git add .` せず、テーマごとに分けてコミットする（後で履歴が読める）：

| グループ | 対象パス |
|----------|---------|
| Daily / Weekly | `Daily/` |
| Wiki | `Wiki/` |
| メタ（rules/skills/templates） | `.claude/`, `Templates/` |

### Step 3: コミット & push

```bash
git commit -m "<scope>: <要約>"
git push
```

コミットメッセージの prefix：

| prefix | 用途 |
|--------|------|
| `daily:` | Daily / Weekly |
| `wiki:` | 汎用ナレッジ（アイデア / 学習ノート / 文献ノート / 実験ログ / 活動記録） |
| `meta:` | rules / skills / templates / settings |

## 節目push（即時）

以下イベント発生時はすぐ push：

- Wiki の **文献ノート / 実験ノート** が `status: completed` 化
- Vault 構造や rules を変更

```bash
git add Wiki/
git commit -m "wiki: complete experiment note - <概要>"
git push
```

## .gitignore

現状の `.gitignore` で運用する。変更はユーザー確認必須。

主な除外（参考）:
- `.obsidian/plugins/`, `.obsidian/snippets/`, `.obsidian/appearance.json`
- `*.tmp`, `*.bak`, `*.swp`, `.DS_Store`, `Thumbs.db`
- Python キャッシュ、IDE 設定

## トラブルシューティング

### リモートが先に進んでいた場合

```bash
git fetch origin
git log origin/main --oneline -5
git pull --rebase origin main
git push
```

### `.obsidian/workspace.json` / `.claudian/sessions/` が頻繁に dirty になる

Obsidian / Claudian が裏で書き換えるため。コミットしても OK だが、毎セッション dirty になり続けるのは仕様。
気になる場合は `.gitignore` 追加を検討（要ユーザー判断）。

### 認証エラー（403 / 401）

Windows の Git Credential Manager で `your-org` の PAT を再登録：

```bash
git credential-manager erase
# 次回 push 時にブラウザ認証
```

## 関連

- [[.claude/rules/daily-operations.md]]
- [[.claude/rules/wiki-management.md]]
