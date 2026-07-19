---
title: "接続ガイド: GitHub"
type: "reference"
status: "completed"
tags: ["setup", "connections", "github"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: GitHub(難易度 ★☆☆・約10分)

**最初に繋ぐ接続としておすすめ**です。必要なのは Personal Access Token(PAT)1 本だけで、これが通れば「Hermes → 外部 API → `Inbox/` → Daily 集約」というパイプライン全体を最短で体感できます。

## 1. 何ができるようになるか

- **push(EOD capture)**:「GitHub 取り込みやって」と言うと、`Maps/Code-Map.md` に列挙した全リポジトリの**当日の commits / PRs / issues** が `Inbox/{date}/code/code.md` に落ちる。夜の EOD distill で「今日コードで何をしたか」が Daily / Work ログに残る
- **pull(その場の参照)**:Claude Code が「`owner/repo` の最新コミットを見て」のような依頼を Hermes 経由で解決できるようになる

> この vault 自体の git バックアップ(`vault-github-sync`)は Claude Code のローカル `git`/`gh` を使う**別経路**です。この接続がなくても vault のバックアップはできます。

## 2. 前提

- GitHub アカウント
- 読み取りたいリポジトリへのアクセス権(private リポを読むなら、その権限を持つアカウントで PAT を作る)

## 3. 手順

1. **PAT を作成**:GitHub → Settings → Developer settings → Personal access tokens
   - **Fine-grained token(推奨)**:対象リポジトリを選び、Repository permissions で `Contents: Read-only` / `Pull requests: Read-only` / `Issues: Read-only` / `Metadata: Read-only` を付与
   - Classic token の場合:`repo` スコープ(private を読むなら必須)
   - 読み取り専用で十分です。write 権限は付けないでください

2. **トークンを Hermes に渡す**:Hermes を起動するシェルの環境変数、または `.hermes/.env`(gitignore 済み)に設定

   ```bash
   # .hermes/.env
   GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_xxxx
   ```

3. **GitHub MCP の設定を確認**:この vault の `.hermes/config.yaml` に GitHub MCP の定義が既にあります(`mcp_servers.github`)。`${HERMES_HOME}` の設定にマージ済みか確認

4. **capture 対象リポジトリを登録**:`Maps/Code-Map.md` に、日々追いたいリポジトリと対象ブランチを列挙する(書式は同ファイル参照)。ここに書いたリポが EOD capture の対象になります

5. **Hermes を再起動**(環境変数を読み直させるため)

## 4. 動作確認

**pull(まずこちら)**:

```bash
hermes chat -q "GitHub MCP で <owner>/<repo> の最新コミットを 3 件教えて" -Q
```

コミットが返れば PAT と MCP は生きています。

**push(パイプライン全体)**:Claude Code に

```text
GitHub EOD 取り込みやって
```

と頼み、`Inbox/{今日の日付}/code/code.md` ができれば完了。続けて「code 集約やって」で Daily への集約まで確認できます。

## 5. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| MCP が認証エラー | `GITHUB_PERSONAL_ACCESS_TOKEN` が Hermes 起動シェルに渡っていない。`.hermes/.env` に書いたら **Hermes を再起動** |
| private リポが 404 | PAT にそのリポの権限がない。Fine-grained token の対象リポ選択を確認 |
| capture が空ファイルに近い | `Maps/Code-Map.md` にリポが列挙されていない、または当日にコミットがない(正常) |
| 同日 2 回目の capture が走らない | 仕様(冪等性)。`Inbox/{date}/code/code.md` が既にあると skip します。再生成したい場合はファイルを消してから |

## 6. 深掘り

- [[.hermes/skills/vault-capture/github-eod-capture/SKILL.md]] — capture skill 本体(取得ロジック・冪等性・MCP tool 名のフォールバック)
- [[.claude/skills/hermes-query/SKILL.md]] — pull 経路の呼び出し方
- [[.claude/rules/agent-boundaries.md]] §6 — なぜ PAT は Hermes だけが持つのか
