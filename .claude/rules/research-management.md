# Research 管理ルール

## 配置：オプションの git サブモジュール

研究関連は vault ルート直下の `Research/` で管理する。実態は **任意**：

- **submodule にする**（推奨・vault と分離）：別 GitHub リポジトリ（例：`your-org/your-research`）を `Research/` にマウント。`.gitmodules` に登録。
- **vault 内に直書きする**：研究 vault と作業 vault を分離せず、`Research/` を普通のフォルダとして使う。submodule の更新オーバーヘッドが要らない。

このテンプレでは **`Research/` は空（CLAUDE.md スタブのみ）**で、submodule にするか直書きするかは利用者の判断に委ねている。

このテンプレでは置き場だけ規定する：

- このサブモジュールは**自己完結**を推奨：独自の `CLAUDE.md` / `.claude/rules/` / `.claude/skills/` / `status.md` を持つ。
- **submodule にする場合、研究作業のルールはサブモジュール側が「正」**。vault 側（本ファイル）はそれに優先しない。

## 入口（推奨構造）

- 入口 MOC（人間向け）: `[[Research/research.md]]`
- 全体契約: `[[Research/CLAUDE.md]]`
- 現況の単一の真実: `Research/status.md`
- 主要ルール（`Research/.claude/rules/`）の例：
  - `reference-management.md` … 論文フォルダ（PDF + .bib + summary.md の3点ルールなど）
  - `research-doc-lifecycle.md` … 研究ノートの命名・昇格パス
  - `application-management.md` … 助成金 / フェローシップ応募のライフサイクル
  - `status-lifecycle.md` / `checkpoint-archive.md` / `archive.md` … 状態・履歴管理
  - `heavy-file-management.md` … 大容量ファイルの振り分け（Drive / HuggingFace 等）

## 推奨フォルダ構造

vault の 4 層フラクタル（Raw → Schema → Compiled → Log）に整列させる。全 `.md` に vault frontmatter を付与すれば、Obsidian graph / Bases / タグ検索に乗る。

```
Research/
├── research.md     # 入口 MOC（人間向け）
├── CLAUDE.md       # ② Schema：研究エージェント契約
├── status.md       # ④ Log：現況 SSOT
├── sources/        # ① Raw：外部・事務資料（immutable）
├── notes/          # ③ Compiled：研究ノート（survey/analysis/synthesis/landscape/profile/experiment）
├── reference/      # ③ Compiled：論文ライブラリ（PascalCase + 3点ルール）
├── datasets/       # ③ Compiled：データセット pointer
├── code/           # ③ Compiled：コード読解・設計メモ（本体は GitHub）
├── applications/   # ③ Compiled：助成金・フェローシップ応募（active）
├── phases/phase1/  # ③ Compiled：フェーズ別実装ワークスペース
└── archive/        # ④ 過去の応募・決定・チェックポイント
```

> 著者プロフィールは vault root の `Persona/` に置き、研究応募からは `../Persona/` を参照する。

## サブモジュールの更新フロー

```bash
# 最新を取り込む
git submodule update --remote Research

# 研究内容を編集したとき：サブモジュール内でコミット & push
cd Research
git add -A && git commit -m "research: <要約>" && git push
cd ..

# 親 vault 側でサブモジュールのポインタ更新をコミット
git add Research && git commit -m "research: bump Research"
```

## vault 側の役割

- vault は `Research/` を**ホスト（マウント）するだけ**。研究ノートの実体は vault 直下に置かない。
- Daily / Weekly から研究進捗に触れる場合は `Research/status.md` を参照する。

## 関連

- [[Research/CLAUDE.md]]
- [[.claude/skills/vault-github-sync/SKILL.md]]
- [[.claude/rules/vault-metadata.md]] / [[.claude/rules/language.md]]
