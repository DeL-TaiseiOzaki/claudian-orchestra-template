---
title: "接続ガイド: Google Drive / Docs"
type: "reference"
status: "completed"
tags: ["setup", "connections", "google-drive"]
created: 2026-07-19
updated: 2026-07-20
---

# 接続ガイド: Google Drive / Docs(難易度 ★☆☆・約10分)

共有ドライブの資料(Docs / Sheets / PDF)を vault の会話から**読める**ようにする接続です。クライアントやチームとの資料共有が Google Drive 中心の人向け。

> **read 専用**です。Drive 側の正本はそのまま(system of record は Drive)、vault には読んだ内容の**蒸留ノート**(`Wiki/sources/` へのポインタ md や `Wiki/` の要約ノート)だけを残します。vault から Drive への書き込み・同期はしません。

> Codex コアは外部サービスを直接叩かないため、Drive read も **Hermes 経由(OAuth)** の一択です([[.codex/rules/agent-boundaries.md]] §6)。Google OAuth 基盤([google-calendar-tasks.md](./google-calendar-tasks.md) 経路 B)に相乗りします。

## 1. 何ができるようになるか

- 「この共有ドライブの提案書を読んで要約して」「スプレッドシートの◯◯シートの数字を拾って」が会話で完結
- 読んだ内容の蒸留は通常フロー(`Wiki/` に コアエージェントがノート化、元ファイルへのリンクを `resource:` frontmatter で保持)

## 2. セットアップ:Hermes 経由(OAuth)

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
| Drive でファイルが見つからない | 認可した Google アカウントが違う/共有ドライブへのアクセス権がない。Drive 側の共有設定を確認 |
| Hermes 経由で Drive だけ失敗 | GCP で Drive API 未有効化、または同意時にスコープを外した(→再認可) |
| 「Drive に書き込んで」と頼みたくなる | 設計上やりません(read 専用・一方向)。内容は vault 側にノート化し、必要なら人が Drive 側を編集します |

## 5. 深掘り

- [[.codex/rules/agent-boundaries.md]] §6 — 外部接続を Hermes に一元化する理由
- [[.codex/rules/vault-metadata.md]] — 外部正本へのポインタ(`resource:` フィールド)
- [[.hermes/skills/vault-capture/google-auth/SKILL.md]] — 経路 B のスコープ設計
