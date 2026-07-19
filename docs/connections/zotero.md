---
title: "接続ガイド: Zotero"
type: "reference"
status: "completed"
tags: ["setup", "connections", "zotero", "research"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: Zotero(難易度 ★☆☆・約15分・研究者向け)

文献管理を Zotero でやっている人向けの接続です。**文献メタデータの正本は Zotero のまま**、vault 側(`Research/` ドメイン)には文献ノート・読書メモを置く、という分担にします。

> **設計**:pull(参照)既定です。Zotero ライブラリを vault に同期・複製することはしません(split-brain 防止・[[.claude/rules/agent-boundaries.md]] §4)。`Research/` を git submodule で運用している場合、文献ノートの置き方はサブモジュール側の規約([[.claude/rules/research-management.md]])が優先です。

## 1. 何ができるようになるか

- **pull**:「最近 Zotero に追加した論文リスト出して」「タグ `to-read` の文献一覧」をコアエージェントから確認
- **文献ノートの起票**:「この論文の文献ノート作って」→ Zotero のメタデータ(著者・年・DOI・URL)を引いて `Research/reference/`(または `Others/Learning/`)にノートを作成。`resource:` frontmatter に Zotero アイテムへのポインタを保持
- 読書中のハイライト・PDF 注釈も API で参照可(取り込みは必要な分だけ手動判断)

## 2. 前提

- Zotero アカウント(ライブラリが Zotero サーバに同期されていること — ローカルのみの運用では Web API が使えません)
- 研究ノートの置き場([[.claude/rules/research-management.md]] — `Research/` 直書き or submodule)

## 3. 手順

1. **API キーを発行**:[zotero.org/settings/keys](https://www.zotero.org/settings/keys) → Create new private key → **Read Only** で発行(write は不要)
2. **userID を控える**:同ページ上部の「Your userID for use in API calls is XXXXX」
3. `.hermes/.env`(gitignore 済み)に登録:

   ```bash
   ZOTERO_API_KEY=xxxx
   ZOTERO_USER_ID=xxxxx
   ```

4. Hermes を再起動

## 4. 動作確認

```bash
hermes chat -q "Zotero Web API (https://api.zotero.org/users/$ZOTERO_USER_ID/items?limit=5&sort=dateAdded) で最近追加した文献 5 件のタイトルを教えて" -Q
```

タイトルが返れば完了。「最近の文献から文献ノート作って」まで通せば運用イメージが掴めます。

## 5. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| API が空を返す | ライブラリが Zotero サーバに未同期(Zotero アプリの Sync 設定を確認)。ローカル専用運用なら Web API は使えません |
| 403 エラー | API キーの権限不足 / userID の取り違え(グループライブラリは `groups/{groupID}` が別途必要) |
| vault に文献 PDF を置きたくなる | 原則置かない。PDF の正本は Zotero(または外部ストレージ)、vault はノートとポインタ(`resource:`)。大容量ファイルの扱いは Research 側規約参照 |

## 6. 関連

- [[.claude/rules/research-management.md]] — Research ドメインの構造(reference/ の 3 点ルール等はサブモジュール側)
- [[.claude/rules/vault-metadata.md]] — 論文ノートの frontmatter スキーマ(`arxiv_id` / `paper_url` 等)・`resource:` ポインタ
- [[.claude/rules/agent-boundaries.md]] §2 — 正本の所在を決め切る原則
