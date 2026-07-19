---
title: "接続ガイド: Google Drive / Docs"
type: "reference"
status: "completed"
tags: ["setup", "connections", "google-drive"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: Google Drive / Docs(難易度 ★☆☆・約10分)

共有ドライブの資料(Docs / Sheets / PDF)を vault の会話から**読める**ようにする接続です。クライアントやチームとの資料共有が Google Drive 中心の人向け。

> **read 専用**です。Drive 側の正本はそのまま(system of record は Drive)、vault には読んだ内容の**蒸留ノート**(`Wiki/sources/` へのポインタ md や `Wiki/` の要約ノート)だけを残します。vault から Drive への書き込み・同期はしません。

## 2 つの経路

| 経路 | 実行者 | 難易度 | 特徴 |
|---|---|---|---|
| **A. claude.ai Drive コネクタ** | Claude Code 直(**コアが Claude Code の場合のみ**) | ★☆☆ | **Hermes 不要**。コアが外部を直接読める唯一の設計上の例外([[.claude/rules/agent-boundaries.md]] §6) |
| **B. Hermes 経由(OAuth)** | Hermes | ★★☆ | Google OAuth 基盤([google-calendar-tasks.md](./google-calendar-tasks.md) 経路 B)に相乗り。headless 運用向け |

## 1. 何ができるようになるか

- 「この共有ドライブの提案書を読んで要約して」「スプレッドシートの◯◯シートの数字を拾って」が会話で完結
- 読んだ内容の蒸留は通常フロー(`Wiki/` に Claude がノート化、元ファイルへのリンクを `resource:` frontmatter で保持)

## 2. 経路 A:claude.ai Drive コネクタ

1. claude.ai の設定 → コネクタ → **Google Drive** を接続(ブラウザで Google ログイン + 許可)
2. Claude Code のセッションから Drive の検索・read ツールが使えるようになります(**Codex コアでは使えません** — 経路 B へ)
3. 動作確認:Claude Code に「Drive で『◯◯』というファイルを探して内容を要約して」と頼む

> read 専用のコネクタとして扱います。ファイルの作成・編集は依頼されても vault 側ノートで代替します(一方向原則)。

## 3. 経路 B:Hermes 経由(OAuth)

1. [google-calendar-tasks.md](./google-calendar-tasks.md) 経路 B の GCP セットアップを済ませる
2. GCP で **Google Drive API** を有効化(Docs / Sheets も読むなら Docs API・Sheets API も)
3. `google-auth` skill の基本スコープに Drive は含まれているため、API 有効化後に認可済みならそのまま動作。未同意なら再認可(`authorize.py --auth-url` → `--auth-code` → `--check`)
4. 動作確認:

   ```bash
   hermes chat -q "Google Drive で『◯◯』というファイルを検索してタイトルを教えて" -Q
   ```

## 4. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| コネクタでファイルが見つからない | コネクタに許可した Google アカウントが違う/共有ドライブへのアクセス権がない。Drive 側の共有設定を確認 |
| Hermes 経由で Drive だけ失敗 | GCP で Drive API 未有効化、または同意時にスコープを外した(→再認可) |
| 「Drive に書き込んで」と頼みたくなる | 設計上やりません(read 専用・一方向)。内容は vault 側にノート化し、必要なら人が Drive 側を編集します |

## 5. 深掘り

- [[.claude/rules/agent-boundaries.md]] §6 — なぜ Drive read だけ Claude 直の例外なのか
- [[.claude/rules/vault-metadata.md]] — 外部正本へのポインタ(`resource:` フィールド)
- [[.hermes/skills/vault-capture/google-auth/SKILL.md]] — 経路 B のスコープ設計
