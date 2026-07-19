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

> **まずは対話式がおすすめ**:コアエージェントに「**接続セットアップして**」と言うと、[[.claude/skills/connection-setup/SKILL.md]] がユースケースを質問して**あなたの使うツールだけ**を選ばせ、このガイド群を台本に 1 本ずつセットアップしてくれます。選択は [[.claude/connections.yaml]] に記録され、使わないツールはジョブリスト・診断から消えます。以下は手動で進めたい人・個別に調べたい人向けです。
>
> 前提:Hermes 本体のセットアップ(= [[GETTING-STARTED.md]] Level 2)が済んでいること(`web-clippings` の拡張直書き経路のみ Hermes 不要)。

## 共通原則(全接続に共通)

1. **認証はすべて Hermes が持つ**。Claude Code / Codex は外部 API を直接叩かない([[.claude/rules/agent-boundaries.md]] §6)。トークンの置き場は Hermes 側(`.hermes/.env` や `~/.hermes/` 配下)で、**git には絶対に commit されない**(`.gitignore` 設定済み)。
2. **接続ごとに独立**。1 本ずつ繋いで、動作確認してから次へ。全部繋がなくても他は動く。
3. **データの流れは 2 経路**:
   - **push(capture)**:Hermes が生データを `Inbox/{YYYY-MM-DD}/{source}/` に書く。Daily ジョブリストから「○○取り込みやって」で発火(on-demand 既定)
   - **pull(query)**:Claude Code が `hermes chat -q "..."` でその場の確認をする([[.claude/skills/hermes-query/SKILL.md]])
4. **困ったら診断**:コアエージェントに「**接続チェックして**」と言えば [[.claude/skills/connection-doctor/SKILL.md]] が全接続の状態と次アクションを報告する。

## 接続一覧

| 接続 | 難易度 | 所要 | 得られるもの | Inbox 着地先 | ガイド |
|---|---|---|---|---|---|
| **GitHub** | ★☆☆ | 10分 | 当日の commits / PRs / issues の EOD capture + 他リポの pull 参照 | `Inbox/{date}/code/code.md` | [github.md](./github.md) |
| **Google カレンダー + Tasks** | ★★☆ | 30–60分 | 朝の briefing(予定 + タスク)自動 capture。registry 上は `google-calendar` / `google-tasks` で別々に選べる(Calendar のみなら ics 経路 10 分) | `Inbox/{date}/daily/daily.md` | [google-calendar-tasks.md](./google-calendar-tasks.md) |
| **Gmail** | ★☆☆ | 10分 | pull 検索・参照(定常 capture なし)。**他メールは Gmail 転送で一本化** | `Inbox/{date}/mail/`(on-demand のみ) | [gmail.md](./gmail.md) |
| **Google Drive / Docs** | ★☆☆ | 10分 | 共有資料の read(claude.ai コネクタ or Hermes 経由) | (取り込みなし・read のみ) | [google-drive.md](./google-drive.md) |
| **Slack** | ★★★ | 30–60分 | 自分の発言 / mention の日次ダイジェスト | `Inbox/{date}/slack/{channel}.md` | [slack.md](./slack.md) |
| **Discord** | ★★☆ | 30分 | コミュニティ会話のダイジェスト(**bot 方式のみ**・skill は生成) | `Inbox/{date}/discord/{channel}.md` | [discord.md](./discord.md) |
| **RSS / ニュースレター** | ★☆☆ | 10分 | 購読フィードの新着(**認証不要・最も手軽**) | `Inbox/{date}/clippings/` | [rss.md](./rss.md) |
| **Web クリッピング** | ★★☆ | 15–30分 | 記事・AI 壁打ちログの取り込み | `Inbox/{date}/clippings/` `chat-logs/` | [web-clippings.md](./web-clippings.md) |
| **AI 議事録** | ★☆☆〜★★☆ | 15–30分 | 会議文字起こし(Genspark は自動アダプタ同梱、他サービスはエクスポート投入) | `Inbox/{date}/mtgs/{slug}.md` | [meeting-notes.md](./meeting-notes.md) |
| **Zotero** | ★☆☆ | 15分 | 文献管理の pull 参照・Wiki 文献ノート起票(文献管理ユーザー向け) | (取り込みなし・pull のみ) | [zotero.md](./zotero.md) |
| **Notion** | ★☆☆ | 15分 | vault → Notion への一方向 publish | (取り込みなし・出力のみ) | [notion.md](./notion.md) |

**推奨順**:① GitHub(最短でパイプライン全体を体感できる)→ ② Google カレンダー + Tasks(価値最大)→ ③ Gmail / Drive(② の OAuth のついでに)・RSS(認証不要)→ ④ Slack / Discord → ⑤ 残りは必要になったら。

## カタログ外ツールの対応方針

カタログに無いツールは「**類似接続の代替**」として扱います。多くは (a) 手動で `Inbox/{date}/{source}/` に置く、(b) 同梱 skill をひな形に capture skill を自作する、のどちらかで同じパイプラインに乗ります:

| 使っているツール | 対応 |
|---|---|
| Outlook / 会社メール | **Gmail へ自動転送で一本化**([gmail.md](./gmail.md)) — 個別接続は作らない |
| Microsoft Teams | 会話 capture は現実的でない(API・組織制限)。必要な決定事項だけ手動で Daily / Inbox へ |
| Todoist / TickTick 等の ToDo | Google Tasks の位置に相当。`hermes-query` から API を叩く運用 + 必要なら自作 skill(正本はツール側・vault に写しのみ、の原則は同じ) |
| Linear / Jira | GitHub(issues)の位置に相当。[github-eod-capture](../../.hermes/skills/vault-capture/github-eod-capture/SKILL.md) をひな形に自作 |
| Readwise / Kindle ハイライト | エクスポートを `Inbox/{date}/clippings/` へ(手動 or 自作 skill) |
| Otter / tl;dv / Notta / Zoom AI | [meeting-notes.md](./meeting-notes.md) 経路 B(エクスポート投入)でそのまま乗る |

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
- `Daily` のジョブリストからも該当項目が消えるよう、コアエージェントに「○○は使わないので外して」と言えば整理してくれます
