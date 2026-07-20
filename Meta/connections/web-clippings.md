---
title: "接続ガイド: Web クリッピング / AI 壁打ちログ"
type: "reference"
status: "completed"
tags: ["setup", "connections", "clippings", "chat-logs"]
created: 2026-07-19
updated: 2026-07-20
---

# 接続ガイド: Web クリッピング / AI 壁打ちログ(難易度 ★★☆・約15–30分)

Web 記事と、ChatGPT / Claude(Web 版)での壁打ちログを vault に取り込む経路です。

**この接続だけは Hermes 必須ではありません**。ブラウザ拡張が直接 vault に書く構成が最も簡単で、初心者にはそちらを推奨します。

| 経路 | 対象 | 難易度 | 必要なもの |
|---|---|---|---|
| **A. Obsidian 公式拡張(推奨)** | Web 記事 + AI チャット | ★☆☆ | ブラウザ拡張のみ |
| **B. 自作拡張 → Hermes webhook** | 同上(自動化度が高い) | ★★★ | 拡張の自作 + Hermes gateway |
| **C. 手動** | 何でも | ☆☆☆ | 手 |

## 1. 何ができるようになるか

- 読んだ記事・調べ物 → `Inbox/{date}/clippings/{slug}.md`
- ChatGPT / Claude での壁打ちログ → `Inbox/{date}/chat-logs/{provider}-{slug}.md`
- どちらも「clippings 集約やって」「chat-logs 集約やって」で Daily に集約 → EOD で `Wiki/` や `Wiki/sources/` へ蒸留

## 2. 経路 A:Obsidian 公式まわりの拡張(推奨)

1. **Web 記事**:[Obsidian Web Clipper](https://obsidian.md/clipper)(公式ブラウザ拡張)をインストール
   - 保存先テンプレートを `Inbox/{{date:YYYY-MM-DD}}/clippings/{{title}}` に設定
   - frontmatter テンプレートに `title` / `type: capture` / `status: inbox` / `tags` / `created` / `updated` / `source: "web:url:{{url}}"` / `fetched_at` を設定する
2. **AI チャットログ**:AI チャットのエクスポート系拡張(例:Obsidian AI Exporter)+ Obsidian の **Local REST API** プラグインで `Inbox/{date}/chat-logs/` に書き込む
   - Obsidian → コミュニティプラグインで Local REST API を導入 → API キーを発行 → 拡張側に設定
   - file 名は `Inbox/{date}/chat-logs/{provider}-{slug}.md`。`provider` は `chatgpt` または `claude`
   - frontmatter は次の contract に合わせる（日付と title は実値へ展開）:

     ```yaml
     ---
     title: "Chat title"
     type: "capture"
     status: "inbox"
     tags: ["capture", "chat-log"]
     created: "2026-07-20"
     updated: "2026-07-20"
     source: "chatgpt"
     fetched_at: "2026-07-20T09:00:00+09:00"
     ---
     ```
3. 動作確認:適当な記事をクリップ → `Inbox/{今日の日付}/clippings/` にファイルができていれば OK

> 拡張の保存先設定が肝です。**日付フォルダ(`Inbox/{date}/`)に入っていれば集約パイプラインに乗ります**。別の場所に落ちた場合は保存先設定を直し、capture extension から新規 capture し直します。ユーザーやコアが Inbox へ直接移動しません。

## 3. 経路 B:自作拡張 → Hermes webhook

自作の Chrome 拡張が開いているページ / チャットを JSON にして Hermes gateway の webhook に POST する経路です。`clippings-capture` は `source` を見て Web を `clippings/`、ChatGPT / Claude を `chat-logs/{provider}-{slug}.md` に分けます。

- **拡張自体はこのテンプレートに含まれていません**(各自実装)。ペイロード契約(JSON スキーマ)は [[.hermes/skills/vault-capture/clippings-capture/SKILL.md]] に定義されています
- 本文抽出が必要な場合は Hermes 側の `defuddle` skill が URL → Markdown 変換を担います
- 自動化度は最も高いですが、まず経路 A で運用を回してから移行するのがおすすめです

## 4. 経路 C:手動

拡張なしでは、本文をコアへ渡して「Hermes 経由で Web capture として残して」と指示します。Hermes が `clippings-capture` を使って Inbox に新規作成します。ユーザーとコアは Inbox へ直接ファイルを書きません。Hermes を使わない構成では Local REST API / Web Clipper など capture extension を入口にします。

## 5. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| クリップが Inbox に入らない | 拡張の保存先テンプレートが日付フォルダ形式になっていない。`Inbox/{{date:YYYY-MM-DD}}/clippings/` を確認 |
| 集約されない | 集約は自動では走りません(on-demand 既定)。「clippings 集約やって」と指示する |
| frontmatter が規約と違う | 拡張側テンプレートを直し、Daily 集約前なら新規 capture し直す。raw は `type: capture` / `status: inbox` のまま保持し、EOD で標準 enum に変換しない。compiled note だけが標準 enum を使う |
| Local REST API に繋がらない | Obsidian が起動していないと API も落ちています。ポート / API キー設定も確認 |

## 6. 深掘り

- [[.hermes/skills/vault-capture/clippings-capture/SKILL.md]] — webhook 経路のペイロード契約
- [[.hermes/skills/vault-capture/defuddle/SKILL.md]] — URL → Markdown 本文抽出
- [[Inbox/README.md]] — chat-logs の frontmatter 正規化ルール
- [[.codex/skills/inbox-aggregate/SKILL.md]] — Daily への集約側
