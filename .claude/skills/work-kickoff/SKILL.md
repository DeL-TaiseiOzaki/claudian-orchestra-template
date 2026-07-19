---
name: work-kickoff
description: Bootstrap a new Work client engagement or transition a won proposal into delivery. Interviews the user (client, code, phase, Slack / repos / 納期 / 予算 / team / initial sources), then proposes and — on approval — creates the Work/{CODE}/ 4-layer folder with seed files AND registers the new project code across the taxonomy (work-management / vault-tagging / vault-metadata / README / Work/CLAUDE.md / work-project-writer). Use when starting a new proposal or new client (新規案件の立ち上げ / 新規提案を始める / 新しいクライアント), assigning a new project code, or moving a won deal from proposal to delivery (提案→デリバリ / 受注したので案件化する).
---

# Work Kickoff Skill

## 目的

受託案件の**立ち上げ準備**を 1 本で回す。**聞き込み → 確認（dry-run）→ 承認 → フォルダ作成＋初期ファイル seed＋taxonomy 登録**まで。
構造の新設・規約の改変を伴うため **承認前提**で動く（[[.claude/rules/agent-boundaries.md]] §5 不可逆・要判断ティア）。フォルダ新設は対応する rules / README / ドメイン契約の更新と**同一 commit**（[[AGENTS.md]] §2）。

> ノート作成の実務は [[.claude/skills/work-project-writer/SKILL.md]]、構造の正は [[.claude/rules/work-management.md]]。本 skill はその**上位の立ち上げワークフロー**。

## 2 モード

| モード | いつ | 何をするか | フォルダ新設 |
|---|---|---|---|
| **A. 新規案件立ち上げ** | 新クライアント / 新テーマ（コード未採番） | 聞き込み → コード採番 → taxonomy フル登録 → `Work/{CODE}/` 作成＋seed | ✅ する |
| **B. 提案 → デリバリ移行** | 受注した既存案件をデリバリ化 | 聞き込み → `status.md` フェーズ更新＋受注後レイヤー（`docs/` 等）を整える | ❌ しない（既存内で更新） |

## 使用場面

- A：`新規案件を立ち上げて` / `新しいクライアントの提案を始める` / `PROJ_A みたいに案件フォルダ作って`
- B：`{CODE} 受注したのでデリバリに移行` / `提案通ったので案件化して`

## 共通原則

- **当日取得**：`date` で当日を取得（推測しない）。`created` / `updated` / 立ち上げ日に使う。
- **既定 dry-run**：作成・編集の前に必ず差分（作るフォルダ / seed ファイル / taxonomy 追記）を提示し、**承認を得てから適用**。
- **Daily に必ず記録**：立ち上げ／移行を `Daily/{当日}.md` の `## 📝 ログ > 🏢 Work` に 1 行残す（[[.claude/rules/daily-operations.md]]「Daily＝その日の完全な記録」）。
- **機密分離**：他案件フォルダと情報を混在させない（[[Work/CLAUDE.md]]）。
- **言語**：クライアント文脈なので seed 本文は日本語、frontmatter キー / enum / コード / タグは英語（[[.claude/rules/language.md]]）。

---

## Mode A: 新規案件立ち上げ

### Step 1: 聞き込み（フル）

`AskUserQuestion` ＋対話で集める。**必須**が揃えば残りは TBD で雛形化してよいが、フル聞き込みなので任意項目も一通り尋ねる。

| 区分 | 項目 | 備考 |
|---|---|---|
| 必須 | クライアント正式名称 | frontmatter `client` |
| 必須 | 案件コード | 未定なら Step 2 で採番案を出す |
| 必須 | 開始フェーズ | `提案` / `デリバリ` |
| 必須 | 概要・目的（1〜2 行） | `project.md` |
| 任意 | Slack channel | `CLAUDE.md` 定数 |
| 任意 | GitHub repos | `code/README.md` ＋ [[Maps/Code-Map.md]] |
| 任意 | 納期 `delivery_date` / 予算 `budget` | deliverable / 開始時のみ |
| 任意 | チーム（メンバー・役割） | `team.md` |
| 任意 | マイルストーン / 健全性 | `status.md` |
| 任意 | 既に資料をもらっているか | あれば `sources/` への置き方を案内（immutable） |

最後に**収集内容のサマリを提示して確認**を取る。

### Step 2: コード採番（重複チェック）

- 既存コード（`PROJ_A` / `PROJ_B` / `PROJ_C` / `PROJ_X`（archived））と**衝突しない大文字 3 字**を提案（クライアント名由来。例：Acme Corp→`ACM`）。`Work/` 直下を `Glob` して既存コードと突き合わせ、重複・表記揺れがないことを確認。
- 候補を提示しユーザー確定。タグは小文字化（`#{code}`）。

### Step 3: 差分提示（dry-run）

以下 2 群を**作成前に**まとめて提示：

**(a) 作成するフォルダ＋ seed ファイル**（テンプレの placeholder を埋める）

| 生成物 | テンプレ | 備考 |
|---|---|---|
| `Work/{CODE}/CLAUDE.md` | [[Templates/work-claude.md]] | 案件 Schema（定数） |
| `Work/{CODE}/project.md` | [[Templates/work-project-overview.md]] | 入口 MOC。主要リンクに全レイヤー（`proposals/` 含む） |
| `Work/{CODE}/status.md` | [[Templates/work-status.md]] | 全体フェーズ＝選択フェーズ（`提案（受注前）` / `デリバリ`） |
| `Work/{CODE}/team.md` | [[Templates/work-team.md]] | 任意項目が空なら TBD |
| `Work/{CODE}/code/README.md` | 既存案件の `code/README.md` に倣う | repos があれば記載 |
| フェーズ別 初手ノート | 下記 | — |

- **提案フェーズ開始**：
  - `Work/{CODE}/proposals/{当日}-提案骨子.md` を [[Templates/work-proposal.md]] から seed。
  - **`sources/`（① Raw・先方資料）と `references/`（③ サーベイ）を先に作成**する（提案フェーズは資料受領＋サーベイが即始まるため）。空フォルダは Obsidian / git が保持できないので、各層に**用途を書いた `README.md` を placeholder** として置く（[[Work/PROJ_A/sources/README.md]] / [[Work/PROJ_A/references/README.md]] が参考）。
  - `meetings/` は MTG があれば `{MTG日}-{topic}.md` を作成（無ければ初出時）。`docs/` `logs/` `code/` `deliverables/` は初出時に作成。
- **デリバリフェーズ開始**：`Work/{CODE}/docs/` に要件 starter（[[Templates/work-doc.md]]）を seed。`sources/` `references/` も未作成なら同様に README 付きで用意。

**(b) taxonomy フル登録差分**（新コードを 6 か所へ。Step 4 で承認後に適用＝同一 commit）→ 下記「## taxonomy 登録チェックリスト」。

### Step 4: 承認

- 全件 / 個別調整 / 中止 を確認。承認なしに作成・編集しない。

### Step 5: 適用

1. フォルダ＋ seed ファイル作成（`Write`。frontmatter の `title` / `project` / `client` / `status` / `tags` / `created` / `updated` を当日値で確定）。
2. taxonomy 6 か所を `Edit` で更新。
3. 任意項目で未確定のものは本文に `TBD`／frontmatter は省略 or 確定後記入。

### Step 6: 報告＋ Daily

- 作成パス・登録した taxonomy・TBD 残りを 3〜5 行で要約。
- `Daily/{当日}.md` に「`{CODE}`（{クライアント}）立ち上げ＝{フェーズ}」を追記。
- 任意：`vault-github-sync` で構造変更＋規約更新をまとめて push（ユーザー指示時）。

---

## Mode B: 提案 → デリバリ移行

### Step 1: 対象確認＋聞き込み

- 対象コードを確認（`Work/` から選択）。受注した提案ノート（`proposals/` のどれか）を特定。
- 聞き込み：確定した **納期 / 予算 / 体制 / デリバリのマイルストーン**、最初に着手する `docs/`（要件・仕様）。

### Step 2: 差分提示（dry-run）

| 対象 | 変更 |
|---|---|
| `status.md` | 「全体フェーズ」→ **デリバリ**。`milestone` 更新。確定した `delivery_date` / `budget` を反映 |
| `project.md` | frontmatter `status: in-progress`、`milestone` 更新 |
| 受注した `proposals/{...}.md` | 末尾に「**受注済 → デリバリ移行（{当日}）**。要件は `docs/` へ」を追記（**proposals/ は履歴として残す**・移動しない） |
| `docs/` | 受注後の定常ドキュメント starter を seed（[[Templates/work-doc.md]]） |
| `code/README.md` | repos が新たに割り当たれば記載 |

> **フォルダ新設なし**・**taxonomy 変更なし**（コードは既存）。

### Step 3: 承認 → Step 4: 適用 → Step 5: 報告＋ Daily

- 承認後に適用。`Daily/{当日}.md` に「`{CODE}` 受注・デリバリ移行」を追記。

---

## taxonomy 登録チェックリスト（Mode A・新コード）

新コード `{CODE}` / クライアント `{client}` / タグ `#{code}` を**以下 6 か所すべて**へ：

1. [[.claude/rules/work-management.md]] … ① プロジェクト一覧の表に行追加／② Frontmatter の `project` enum に追記
2. [[.claude/rules/vault-tagging.md]] … 「プロジェクトタグ」ブロックに `#{code}` を追加
3. [[.claude/rules/vault-metadata.md]] … Work 追加フィールドの `project` enum と `client` enum に追記
4. [[README.md]] … ドメインフォルダ図の `Work/{PROJ_A,…}/` 列挙に `{CODE}` 追加
5. [[Work/CLAUDE.md]] … 冒頭の案件列挙＋ frontmatter `project` / `client` enum に追記
6. [[.claude/skills/work-project-writer/SKILL.md]] … 案件コード列挙箇所（description・本文の `PROJ_A / PROJ_B / …`）に追記

> 6 か所一括が「フル登録」。漏らすと整合性チェック（[[.claude/skills/vault-consistency-check/SKILL.md]]）で検出される。

## 安全策

- **コード重複・表記揺れ防止**：大文字 3 字・既存と非衝突を `Glob Work/*` で確認してから採番。
- **承認前提**：作成・規約改変・移行はすべて dry-run → 承認 → 適用。
- **同一 commit**：フォルダ新設と rules / README / ドメイン契約更新は分けない（[[AGENTS.md]] §2）。
- **proposals/ は移さない**：受注後も履歴として残す（受注前の判断の証跡。[[.claude/rules/work-management.md]] §提案 → デリバリのライフサイクル）。
- **Git 前提**：Drive 同期と競合しないよう自動コミッタは 1 つ（[[.claude/rules/agent-boundaries.md]] §4）。

## 関連

- [[.claude/rules/work-management.md]]（4 層標準・提案→デリバリのライフサイクル）/ [[Work/CLAUDE.md]]
- [[.claude/skills/work-project-writer/SKILL.md]]（ノート作成の実務）
- [[.claude/rules/vault-metadata.md]] / [[.claude/rules/vault-tagging.md]] / [[.claude/rules/daily-operations.md]] / [[.claude/rules/agent-boundaries.md]] / [[.claude/rules/language.md]]
- テンプレ：[[Templates/work-claude.md]] / [[Templates/work-project-overview.md]] / [[Templates/work-status.md]] / [[Templates/work-team.md]] / [[Templates/work-proposal.md]] / [[Templates/work-doc.md]]
