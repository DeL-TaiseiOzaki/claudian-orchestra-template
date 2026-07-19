---
title: "接続ガイド: Notion(一方向 publish)"
type: "reference"
status: "completed"
tags: ["setup", "connections", "notion"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: Notion(難易度 ★☆☆・約15分)

vault のノートを清書して Notion に公開する**一方向 publish 専用**の接続です。チームや共同研究者と成果を共有する場が Notion にある人向けで、**個人利用だけなら不要**です。

## 1. 何ができるようになるか

- vault で書いた・蒸留したノートを、コアエージェント経由で **Notion ページとして publish**(vault → Notion の一方向)
- **pull(read)**:Notion 上の特定ページを Hermes 経由で読んで会話に取り込む

> **重要な設計判断:双方向同期はしません**。正本は常に vault(Markdown)側で、Notion は清書の公開先です。Notion 側での編集は vault に戻りません([[.claude/rules/agent-boundaries.md]] §4 — split-brain 防止)。`Inbox/notion/` のような取り込み経路も**意図的に存在しません**。

## 2. 前提

- Notion アカウントと、publish 先の workspace / ページへのアクセス権

## 3. 手順

1. `.hermes/config.yaml` の Notion MCP 定義を確認(このテンプレートでは設定済み):

   ```yaml
   mcp_servers:
     notion:
       url: https://mcp.notion.com/mcp
       auth: oauth
       enabled: true
   ```

2. Hermes 起動後、Notion MCP への初回アクセス時に **OAuth フロー**が走ります。ブラウザで Notion にログインし、対象 workspace へのアクセスを許可
3. 許可する範囲(どのページ / データベースに触れるか)は Notion 側の接続設定で絞れます。**publish 先の親ページだけに絞る**のが安全です

## 4. 動作確認

**pull(read)**:

```bash
hermes chat -q "Notion で <ページ名> を検索して内容を要約して" -Q
```

**publish**:Claude Code に

```text
このノートを Notion の <親ページ> に publish して
```

と頼むと、hermes-query 経由で Notion に書き出されます(外部への write なので、実行前に承認を求められます — [[.claude/rules/agent-boundaries.md]] §5 の承認ティア)。

## 5. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| ページが見つからない | OAuth 時に許可した範囲にそのページが入っていない。Notion の「接続」設定でページを追加 |
| OAuth が期限切れ | Hermes 経由で再認証(MCP のトークンは `~/.hermes/` 配下、git 対象外) |
| Notion 側で編集した内容を vault に取り込みたい | **仕様上やりません**(一方向)。必要な内容は手動で vault 側に書き、以降は vault を正本に |

## 6. 深掘り

- [[.claude/rules/agent-boundaries.md]] §2 / §4 — 正本の所在と一方向 publish の設計理由
- [[.claude/skills/hermes-query/SKILL.md]] — Notion read の呼び出し方
