# MAINTAINERS — Push out this template as a new GitHub repo

> このファイルは **テンプレ作者向け**。利用者向けのセットアップは [`GETTING-STARTED.md`](./GETTING-STARTED.md) / [`README.md`](./README.md) 参照。
> （旧ファイル名 `SETUP.md`。利用者が最初に開いて混乱しないよう 2026-07-19 にリネーム）

このディレクトリ `Meta/claudian-orchestra-template/` は MY_MEMORY vault の中で組み立てた **新規 public リポジトリの中身**そのもの。以下の手順で独立リポジトリとして push する。

## 1. テンプレートをコピーして git 化

vault の外（または別ディレクトリ）にコピーしてから git init する。vault 自身が git repo なのでネストを避けるため。

```bash
# vault 外の作業ディレクトリへコピー
cp -r "<vault parent>/MY_MEMORY/Meta/claudian-orchestra-template" "$HOME/work/claudian-orchestra-template"
cd "$HOME/work/claudian-orchestra-template"

# git init + 初期コミット
git init -b main
git add .
git commit -m "Initial Claudian Orchestra template scaffold"
```

## 2. GitHub にリモートリポジトリを作って push

`gh` CLI が手っ取り早い：

```bash
# Public リポジトリとして作成
gh repo create claudian-orchestra-template \
  --public \
  --description "Vault scaffold for the Claudian Orchestra (Claude Code / Codex / Hermes on Obsidian)" \
  --source . \
  --push
```

または手動で GitHub UI から空のリポジトリを作って、

```bash
git remote add origin https://github.com/<your-org>/claudian-orchestra-template.git
git push -u origin main
```

## 3. 公開後にやること

1. **記事の本文に repo URL を埋める**：`Others/zenn_blogs/articles/claudian-orchestra_20260616.md` の closing セクション（"## 8. まとめ" の下、もしくは "## 参考リンク" の最後）に「テンプレリポ：`https://github.com/<your-org>/claudian-orchestra-template`」を追加する。
2. **Topics を設定**：GitHub の Topics に `obsidian`、`claude-code`、`codex`、`hermes-agent`、`pkm`、`second-brain`、`agent-template` あたりを付けると検索性が上がる。
3. **About 欄**：1 行説明＋記事 URL を入れる。

## 4. 以後のメンテナンス

このテンプレは **MY_MEMORY 本家から手動で差分を反映する** スナップショット運用：

- 本家 vault の `.claude/rules/` / `.claude/skills/` / `Templates/` / `Maps/` を更新したら、必要に応じてテンプレ側にも反映する（sanitize 通しが必要）。
- 利用者の改善 PR は `Meta/claudian-orchestra-template/` に直接マージしてよい（vault 本家に取り込むかは別判断）。

## 5. このファイルの扱い

`MAINTAINERS.md` はテンプレ作者専用なので、公開 repo に push **する** と利用者が混乱する可能性がある。判断：

- **残す**：利用者が forkして自分の派生テンプレを作りやすい
- **削除する**：利用者向け UX を優先する

迷ったら残せばよい（利用者向けの入口は `GETTING-STARTED.md` に分離済みなので、名前で混同されることはない）。
