---
title: "接続ガイド: RSS / ニュースレター"
type: "reference"
status: "completed"
tags: ["setup", "connections", "rss"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: RSS / ニュースレター(難易度 ★☆☆・約10分)

購読しているブログ・ニュースサイト・ポッドキャストの新着を vault に取り込む経路です。**認証が一切不要**なので、全接続の中で最も手軽です。定常の情報摂取を `Inbox/{date}/clippings/` に乗せ、既存の集約・distill パイプラインで処理します。

> **設計**:専用の Inbox ソースは作らず **`clippings/` に相乗り**します(RSS 記事は Web クリップと同じ性質のため)。ニュースレターは RSS を出していないものも多いので、その場合は **Gmail 転送 + Gmail 接続の on-demand capture**([gmail.md](./gmail.md))か、Kill the Newsletter 等の「メール → RSS 変換」を使います。

## 1. 何ができるようになるか

- 「RSS 巡回して」で購読フィードの新着が `Inbox/{date}/clippings/{slug}.md` に 1 記事 1 ファイルで落ちる
- 「clippings 集約やって」で Daily に(タイトル + 1 行要約)→ EOD distill で保存価値のあるものだけ `Wiki/sources/` や `Wiki/` へ

## 2. 前提

- Hermes 本体([[GETTING-STARTED.md]] Level 2)
- 購読したいフィードの URL(サイトの `/feed` `/rss.xml` `/atom.xml` 等)

## 3. 手順

1. **フィードリストを作る**:`.hermes/feeds.local.yaml`(**gitignore 済み** — 購読リストは個人情報なので commit しない):

   ```yaml
   feeds:
     - name: "Simon Willison"
       url: https://simonwillison.net/atom/everything/
       tags: [llm]
     - name: "Hacker News (top)"
       url: https://news.ycombinator.com/rss
       tags: [tech-news]
   ```

2. `.gitignore` に `.hermes/feeds.local.yaml` が含まれることを確認(このテンプレでは `*.local.yaml` 系は除外済みのパターンに合わせる。無ければ 1 行追加)
3. 以上です。認証はありません

## 4. 動作確認

コアエージェントに:

```text
RSS 巡回して
```

Hermes が `feeds.local.yaml` の各フィードを fetch し、**前回巡回以降の新着**(初回は直近数件)を `Inbox/{今日の日付}/clippings/` に書き出します(frontmatter `source: "rss:{feed-slug}:{entry-id}"` — 同一 entry は filename 冪等で二重取得しない)。

## 5. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| フィードが見つからない | サイトによって path が違う(`/feed` `/rss` `/atom.xml` `/index.xml`)。ページの HTML 内 `<link rel="alternate">` を見るか、Claude に「このサイトのフィード URL 探して」と頼む |
| ニュースレターを取り込みたい | RSS が無ければ:(a) **Gmail に届くよう購読 → Gmail 接続で on-demand capture**、(b) Kill the Newsletter 等でメール→RSS 変換して本接続に乗せる |
| 新着が多すぎて Inbox が溢れる | フィードを絞る(タグ付きで優先度管理)。全部読む必要はない — 集約時に Claude がタイトル一覧化するので、開くものだけ開く運用で十分 |
| 毎朝自動で巡回したい | on-demand が既定ですが、cron 登録も可(`hermes cron create "0 7 * * *" "RSS 巡回..."`) |

## 6. 関連

- [web-clippings.md](./web-clippings.md) — 同じ `clippings/` 着地の手動クリップ経路
- [gmail.md](./gmail.md) — ニュースレターの Gmail 転送受け
- [[.claude/skills/aggregate-clippings/SKILL.md]] — Daily への集約側
