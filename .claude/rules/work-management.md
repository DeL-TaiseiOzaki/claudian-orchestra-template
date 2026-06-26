# Work プロジェクト管理ルール

## プロジェクト一覧（例）

| コード | クライアント | 概要 |
|--------|------------|------|
| **PROJ_A** | Client A | 例：AI 受託案件（デリバリ中） |
| **PROJ_B** | Client B | 例：AI 受託案件（要件定義） |
| **PROJ_C** | Client C | 例：AI 受託案件（提案フェーズ） |
| ~~PROJ_X~~ | Client X | 🗄️ **アーカイブ例（失注）** — `Archive/Work/PROJ_X/` |

> このテンプレートでは **PROJ_A** だけ 4 層構造の雛形を `Work/PROJ_A/` に置いている。実案件を立ち上げるときは `Work/PROJ_A/` を案件コード（例：`Work/ACME/`）にリネームし、本表を更新する。新規案件は [[.claude/skills/work-kickoff/SKILL.md]] で立ち上げると frontmatter / フォルダ / タグが揃う。

## プロジェクトフォルダ構造（4 層標準）

各案件フォルダは vault 全体のアーキテクチャ（Raw Sources → Schema → Compiled Wiki → Index & Log）を**フラクタルに再現**する。

```
Work/{CODE}/
├── CLAUDE.md        # ② Schema：案件固有の規約・定数（エージェント向け・自動読込）
├── project.md       # 入口 MOC（人間向け：概要・主要リンク）
├── status.md        # ④ Log：非定常な全体ステータス（随時更新）
├── team.md          # ④ Log：チームメンバーのタスク状況
├── sources/         # ① Raw：先方資料 ＋ Inbox 由来の生データ（slack/code 等）の curate 着地（非 md 可・immutable・frontmatter は capture のまま）
├── meetings/        # ③ Compiled：会議メモ（{YYYY-MM-DD}-{topic}.md）。genspark 生録は curate 時に要約してここへ
├── docs/            # ③ Compiled：定常ドキュメント（要件・仕様・設計・運用）。sources/ の蒸留先
├── code/            # ③ Compiled：コードベース知識（本体は GitHub）
├── deliverables/    # ③ Compiled：納品物・アウトプット（受注後）
├── proposals/       # ③ Compiled：受注前の提案成果物（提案書・スライド・見積・スコープ・体制案）。受注後は docs/・deliverables/ へ
├── references/      # ③ Compiled：自分たちでサーベイした結果・外部調査資料（先方由来ではない）
└── logs/            # ④ Log：案件デイリーログ（Daily からの詳細）
```

> **資料の置き分け**：
> - 先方からもらった顧客資料・重要資料 → `sources/`（生・immutable・非 md 可）
> - **Inbox 由来の生データ（slack digest・code・添付＝hermes capture）→ curate 時に `sources/` へ raw のまま（frontmatter は `type: capture`）**
> - 自分たちでサーベイした結果・それに準ずる資料 → `references/`
> - 自分たちが書く定常ドキュメント（要件・仕様・設計） → `docs/`
> - **提案フェーズの成果物（提案書・スライド・見積・スコープ・体制案）→ `proposals/`（受注前。受注後の定常ドキュメントは `docs/`、納品物は `deliverables/`）**
> - **例外：genspark MTG（`Inbox/{date}/mtgs/`）は curate 時に要約して `meetings/{YYYY-MM-DD}-{topic}.md`（compiled）へ。raw transcript は git 履歴に残す**

### CLAUDE.md / project.md / status.md の役割分担（重複禁止）

| ファイル | 役割 | 中身 |
|---|---|---|
| `CLAUDE.md` | **エージェント向け契約**（How / 定数） | クライアント・Slack channel・repos・命名・sources/ 運用規約（[[Templates/work-claude.md]]） |
| `project.md` | **人間向け入口 MOC**（What） | 概要・目的・主要成果物・サブフォルダへのリンク |
| `status.md` | **現在の状態**（Now） | フェーズ・健全性・課題・次ステップ（随時更新） |

### sources/（① Raw 層）の運用

- 先方からもらったファイル（データ・資料・PDF・Excel 等）は**とりあえず `sources/` にぶち込む**。
- **非 md 直置き可**：`_assets/` 規約（自作の非 md 作業物）の例外。`sources/` は「外部からもらった一次資料」＋「Inbox 由来の生データ（hermes capture）の curate 着地」。
- **Inbox 由来データはここに raw のまま置く**（`type: capture` を保持）。蒸留は `docs/`・`meetings/`・`references/` 側に別ノートとして書き、元ファイルへ相対リンクを残す（genspark MTG だけは要約を `meetings/` へ＝§資料の置き分け の例外）。
- **immutable**：リネーム・編集・削除しない（provenance 維持）。curate 時は `docs/` に蒸留ノートを作り、元ファイルへ相対リンクを残す。
- 大容量データの正本は外部（GitHub / クラウドストレージ / HuggingFace 等）に置き、ポインタ md を置いてもよい。

### プロジェクト共通コンテンツ

各案件に共通して入る情報と置き場：

| 情報 | 置き場 | 形態 |
|---|---|---|
| 案件固有の規約・定数 | `CLAUDE.md` | 単一（[[Templates/work-claude.md]]） |
| 先方からの生データ・資料 | `sources/` | 都度投入（非 md 可・immutable） |
| 毎回のミーティング情報 | `meetings/{YYYY-MM-DD}-{topic}.md` | 都度追加（[[Templates/work-meeting-note.md]]） |
| さまざまな定常ドキュメント | `docs/` | 標準ドキュメント（要件・仕様・設計・運用、[[Templates/work-doc.md]]） |
| コードベースの情報 | `code/`（本体は GitHub） | 読解メモ・設計判断（[[Templates/code-note.md]]）。[[Maps/Code-Map.md]] から繋ぐ |
| サーベイ結果・外部調査資料 | `references/` | 都度追加（先方由来でないもの） |
| 提案フェーズの成果物（提案書・見積・スコープ・体制） | `proposals/{YYYY-MM-DD}-{topic}.md` | 都度追加（[[Templates/work-proposal.md]]・受注前） |
| チームメンバーのタスク状況 | `team.md` | 単一・随時更新（[[Templates/work-team.md]]） |
| 非定常なプロジェクト全体ステータス | `status.md` | 単一・随時更新（[[Templates/work-status.md]]） |

> コード**本体**の正本は GitHub（他リポは GitHub MCP で読み取り、理解を `code/` に残して [[Maps/Code-Map.md]] から辿れるようにする）。

## 提案 → デリバリのライフサイクル

受託案件は **① 提案フェーズ（サーベイ → 提案 → 見積）→ ② デリバリフェーズ（要件 → 設計 → 実装 → 納品）** の 2 段で進む。両フェーズを**同じ `Work/{案件}/` 内で地続きに**扱う（提案専用の別エリアは作らない＝クライアント単位ライフサイクル）。

### フェーズと層の対応

| フェーズ | 主に使う層 | 補足 |
|---|---|---|
| ① 提案（受注前） | `references/`（サーベイ）・`meetings/`（提案MTG・引き合い）・`proposals/`（提案書・見積・スコープ・体制） | 提案の意思決定はすべて `proposals/` に残す |
| ② デリバリ（受注後） | `sources/`（先方資料）・`docs/`（要件・仕様・設計）・`code/`・`deliverables/`（納品物）・`logs/` | サーベイ(`references/`)・MTG(`meetings/`) は継続利用 |

### proposals/ の運用（③ Compiled・受注前）

- 置くもの：提案書・提案スライド骨子・概算見積・スコープ案・体制案（受注前の成果物）。
- 命名：`proposals/{YYYY-MM-DD}-{topic}.md`（フラット。サブフォルダは作らない）。テンプレ [[Templates/work-proposal.md]]。
- 受注後も `deliverables/` へは移さず `proposals/` に**履歴として残す**（受注前の判断の証跡）。提案で作ったサーベイは `references/`、提案MTG は `meetings/` に置き、`proposals/` から相対リンクする。
- 受注後の定常ドキュメント（要件・仕様・設計）は `docs/` に新規に書く（提案書をそのまま仕様に流用しない＝受注前 / 受注後の境界を保つ）。

### フェーズの可視化と失注

- 案件全体のフェーズ（**提案 / デリバリ / 完了**）は `status.md` の「全体フェーズ」欄で表現する（frontmatter スキーマは変えない）。
- 提案ノートの frontmatter は `type: note`（最終提案書は `deliverable` 可）＋ タグ `#proposal`（[[.claude/rules/vault-tagging.md]]）。
- **失注・見送り**：削除せず `status: archived` にして残す（必要なら [[.claude/skills/vault-archive/SKILL.md]] で `Archive/` へ退避）。

## Frontmatter

frontmatter スキーマの**単一の正は [[.claude/rules/vault-metadata.md]]**（共通フィールド + Work 追加フィールド + status/type の使い分け）．重複定義はそちらに集約する．

Work ノート固有の追加フィールド（詳細は vault-metadata.md）：

- `project`：`PROJ_A` | `PROJ_B` | `PROJ_C` | …（実案件のコードに置き換える）
- `client`：クライアント名
- `delivery_date`：納期（deliverable のみ）
- `budget`：予算（プロジェクト開始時のみ）
- `milestone`：フェーズ

## デイリーログのルール

- 毎日 `Daily/{YYYY-MM-DD}.md` を作成
- 各プロジェクトの進捗を簡潔に記録
- 納期・マイルストーンを記載

## ウィークリーレビューのルール

- 毎週月曜に `Daily/Weekly-{YYYY-WXX}.md` を作成
- 各プロジェクトの進捗まとめ
- 次週のタスク予定

## 関連

- [[.claude/rules/vault-metadata.md]]（frontmatter スキーマの単一の正）
- [[.claude/rules/vault-tagging.md]] / [[.claude/rules/daily-operations.md]] / [[.claude/rules/language.md]]
- [[.claude/skills/work-project-writer/SKILL.md]] / [[.claude/skills/work-kickoff/SKILL.md]] / [[.claude/skills/daily-briefing/SKILL.md]] / [[.claude/skills/weekly-review/SKILL.md]]
