---
title: "外部接続セットアップガイド — index"
type: "reference"
status: "completed"
tags: ["setup", "connections", "hermes"]
created: 2026-07-19
updated: 2026-07-19
---

# 外部接続セットアップガイド

personal knowledge base の**一番の躓きポイントは外部ツールとの繋ぎ込み**です。このディレクトリは、接続を 1 本ずつ・動作確認しながら繋ぐためのガイド集です。

> 前提:Hermes 本体のセットアップ(= [[GETTING-STARTED.md]] Level 2)が済んでいること。まだなら先にそちらを。

## 共通原則(全接続に共通)

1. **認証はすべて Hermes が持つ**。Claude Code / Codex は外部 API を直接叩かない([[.claude/rules/agent-boundaries.md]] §6)。トークンの置き場は Hermes 側(`.hermes/.env` や `~/.hermes/` 配下)で、**git には絶対に commit されない**(`.gitignore` 設定済み)。
2. **接続ごとに独立**。1 本ずつ繋いで、動作確認してから次へ。全部繋がなくても他は動く。
3. **データの流れは 2 経路**:
   - **push(capture)**:Hermes が生データを `Inbox/{YYYY-MM-DD}/{source}/` に書く。Daily ジョブリストから「○○取り込みやって」で発火(on-demand 既定)
   - **pull(query)**:Claude Code が `hermes chat -q "..."` でその場の確認をする([[.claude/skills/hermes-query/SKILL.md]])
4. **困ったら診断**:Claude Code に「**接続チェックして**」と言えば [[.claude/skills/connection-doctor/SKILL.md]] が全接続の状態と次アクションを報告する。

## 接続一覧

| 接続 | 難易度 | 所要 | 得られるもの | Inbox 着地先 | ガイド |
|---|---|---|---|---|---|
| **GitHub** | ★☆☆ | 10分 | 当日の commits / PRs / issues の EOD capture + 他リポの pull 参照 | `Inbox/{date}/code/code.md` | [github.md](./github.md) |
| **Google Calendar + Tasks** | ★★☆ | 30–60分 | 朝の briefing(予定 + タスク)自動 capture | `Inbox/{date}/daily/daily.md` | [google-calendar-tasks.md](./google-calendar-tasks.md) |
| **Slack** | ★★★ | 30–60分 | 自分の発言 / mention の日次ダイジェスト | `Inbox/{date}/slack/{channel}.md` | [slack.md](./slack.md) |
| **Web クリッピング** | ★★☆ | 15–30分 | 記事・AI 壁打ちログの取り込み | `Inbox/{date}/clippings/` `chat-logs/` | [web-clippings.md](./web-clippings.md) |
| **Genspark 議事録** | ★★☆ | 15–30分 | AI 会議文字起こしの取り込み | `Inbox/{date}/mtgs/genspark-{slug}.md` | [genspark.md](./genspark.md) |
| **Notion** | ★☆☆ | 15分 | vault → Notion への一方向 publish | (取り込みなし・出力のみ) | [notion.md](./notion.md) |

**推奨順**:① GitHub(最短でパイプライン全体を体感できる)→ ② Google(価値最大)→ ③ Slack → ④ 以降は必要になったら。

## 各ガイドの構成

すべてのガイドは同じ構成です:

1. **何ができるようになるか** — 繋ぐと日々の運用がどう変わるか
2. **前提** — 必要なアカウント・権限
3. **手順** — 番号付き。コピペで進められる粒度
4. **動作確認** — pull(即時)と push(capture → Inbox)の両方を確認
5. **よくある躓き** — 実運用で踏んだ失敗と対処
6. **深掘り** — 対応する Hermes capture skill(`.hermes/skills/vault-capture/`)へのリンク

## 使わない接続について

- 対応する capture skill(`.hermes/skills/vault-capture/{skill}/`)ごと削除して構いません
- `Daily` のジョブリストからも該当項目が消えるよう、Claude Code に「○○は使わないので外して」と言えば整理してくれます
