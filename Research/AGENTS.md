# AGENTS.md — Research（オプション・空のプレースホルダ）

研究関連のホーム。詳細ルールは [[.claude/rules/research-management.md]]。

## このテンプレでの扱い

このテンプレでは **`Research/` は空のプレースホルダ**。利用者は次の 2 通りから選んでよい：

### 1. git submodule で別リポをマウントする（推奨）

研究を別レポジトリで進める場合：

```bash
git submodule add https://github.com/your-org/your-research Research
```

サブモジュール側に自前の `AGENTS.md` / rules / `status.md` を置き、研究作業のルールはサブモジュール側が「正」になる。vault 側（本ファイル）はそれに優先しない。

更新フロー：

```bash
# サブモジュール内でコミット & push
cd Research
git add -A && git commit -m "research: <要約>" && git push
cd ..

# 親 vault でポインタを bump
git add Research && git commit -m "research: bump Research"
```

### 2. vault 内に直書きする

submodule の更新オーバーヘッドが要らないなら、ここを普通のフォルダとして使ってよい。`.claude/rules/research-management.md` で推奨されている 4 層構造（sources / notes / reference / datasets / code / applications / phases / archive）をそのまま採用するのが楽。

## 推奨構造

```
Research/
├── research.md     # 入口 MOC（人間向け）
├── AGENTS.md       # ② Schema：研究エージェント契約（本ファイルを上書き）
├── status.md       # ④ Log：現況 SoT
├── sources/        # ① Raw：外部・事務資料（immutable）
├── notes/          # ③ Compiled：研究ノート
├── reference/      # ③ Compiled：論文ライブラリ（PDF + .bib + summary.md の 3 点ルール）
├── datasets/       # ③ Compiled：データセット pointer
├── code/           # ③ Compiled：コード読解・設計メモ
├── applications/   # ③ Compiled：助成金・フェローシップ応募
├── phases/         # ③ Compiled：フェーズ別実装ワークスペース
└── archive/        # ④ 過去の応募・決定・チェックポイント
```

## 関連

- [[.claude/rules/research-management.md]]
- [[Persona/AGENTS.md]] — 著者プロフィールは vault root から参照
- [[.claude/skills/vault-github-sync/SKILL.md]]
