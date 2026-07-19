---
title: "接続ガイド: Gmail"
type: "reference"
status: "completed"
tags: ["setup", "connections", "gmail", "google"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: Gmail(難易度 ★☆☆・約10分 ※Google OAuth 済みなら)

Gmail を vault の会話から**検索・参照**できるようにする接続です。[Google Calendar + Tasks](./google-calendar-tasks.md) の経路 B(OAuth)と**同じ認可基盤**に乗るため、そちらが済んでいれば追加作業はほぼありません。

> **設計上の注意**:この vault では **Gmail は pull(その場の検索・参照)が既定**で、朝の briefing には入れません(メールをジャーナルに常時流し込むとノイズが勝つため)。定常 capture skill も持ちません。残したいメールがあるときだけ on-demand で `Inbox/{date}/mail/` に取り込みます。
>
> **他のメールサービスを使っている場合(Outlook / 会社メール等)**:カタログ上のメール接続は Gmail だけです。**他メールは Gmail への自動転送を設定して一本化**してください(Outlook:設定 → メール → 転送 / 多くの企業メールも転送ルールで対応可)。Graph API 等の個別接続を増やすより、転送 1 本のほうがセットアップも保守も圧倒的に軽くなります。ニュースレターの受けにも同じ方針が使えます([rss.md](./rss.md))。

## 1. 何ができるようになるか

- **pull(既定)**:「先週の◯◯さんからのメール探して」「この件の最新のやり取り要約して」をコアエージェントから Hermes 経由で実行
- **on-demand capture(任意)**:「このメール vault に残して」で `Inbox/{date}/mail/{slug}.md` に保存 → 通常の Daily 集約 / EOD distill パイプラインに乗る
- **下書き作成(任意・承認制)**:「◯◯への返信を下書きして」— 外部への write なので実行前に必ず承認を求めます([[.claude/rules/agent-boundaries.md]] §5)。**自動送信はしません**

## 2. 前提

- [Google Calendar + Tasks の経路 B](./google-calendar-tasks.md)(GCP プロジェクト + OAuth クライアント)が済んでいること。未了ならそちらを先に(Gmail だけ使う場合も手順は同じです)

## 3. 手順

1. **Gmail API を有効化**:GCP コンソール → 「API とサービス」→ ライブラリ → **Gmail API** を有効化
2. **スコープを確認**:`google-auth` skill の基本スコープに Gmail(readonly / send / modify)は**最初から含まれています**。経路 B の認可を Gmail API 有効化**後**に行っていれば追加作業なし。有効化が後だった場合や同意画面で外した場合は再認可:

   ```bash
   python .hermes/skills/vault-capture/google-auth/scripts/authorize.py --auth-url
   # ブラウザで同意 → リダイレクト URL を --auth-code に渡す → --check で AUTHENTICATED
   ```

3. 読み取りだけにしたい場合は、同意画面で send / modify のチェックを外して readonly のみ許可しても動きます(下書き作成は不可になります)

## 4. 動作確認

```bash
hermes chat -q "Gmail の未読メールを 3 件、件名だけ教えて" -Q
```

件名が返れば完了です。capture も試すなら「いま来ている◯◯のメールを vault に残して」→ `Inbox/{今日の日付}/mail/` にファイルができれば OK。

## 5. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| 認可は済んでいるのに Gmail だけ失敗 | GCP で **Gmail API を有効化していない**(手順 1)。有効化後は数分待ってから再試行 |
| `insufficient scopes` 系エラー | 同意時に Gmail スコープを外している。`authorize.py --check` で付与スコープを確認し、再認可 |
| メールが大量に vault に入ってきそうで不安 | 入ってきません。**定常 capture は設計上存在せず**、明示指示した 1 通ずつだけです |
| 送信された?と不安 | この接続の write は**下書き作成まで**。送信はユーザーが Gmail 上で行います |

## 6. 深掘り

- [[.hermes/skills/vault-capture/google-auth/SKILL.md]] — スコープ設計(Gmail は基本スコープに含まれる)
- [[docs/connections/google-calendar-tasks.md]] — 同じ OAuth 基盤のセットアップ本体
- [[.claude/rules/agent-boundaries.md]] §5 — 外部への write が承認制である理由
- [[.claude/rules/inbox-routing.md]] §2 — `Inbox/{date}/mail/` の着地規約(on-demand のみ)
