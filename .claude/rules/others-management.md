# Others 管理ルール

Work（受託案件）・Research（LLM/VLM 研究本流）に属さない活動の運用ルール（詳細）。
入口は [[Others/CLAUDE.md]]、全体像は [[Others/README.md]]。

## フォルダ構造

```
Others/
├── Ideas/        # アイデア帳（着想の種）＋ 別シードの検証・PoC・初期構想（旧 Exploration を統合・2026-06-13）
├── Activities/   # 継続的活動（社内外コミュニティ・学会委員・グループ・コンペ・エコシステム創発）
│   ├── CLAUDE.md # サブエリア共通 Schema（4 層標準の定義）
│   ├── Community-A/ Community-B/ WG-A/ WG-B/ Kaggle/ Conferences/
│   └── Ecosystem/  # 教育→インターン→起業/活躍 の循環を創発する組織活動（2026-06-12 Activities 配下に正式化）
└── Learning/     # 個人学習・読書ノート・技術メモ（1 トピック = 1 フォルダ：`Learning/{Topic}/` 配下に note 等をまとめる）
```

> **2026-06-13：`Exploration/` を `Ideas/` に統合**。別シードの仮説検証・PoC・初期構想は `Ideas/` 配下に置く（シード単位でサブフォルダ化可）。`type: exploration` は PoC/検証フレーバーとして enum に残す（軽い着想は `type: idea`）。

## サブカテゴリ定義

| フォルダ | 用途 | type | status の起点 | 主なタグ |
|---|---|---|---|---|
| Ideas | 着想を素早く記録（粒度は粗くてよい）＋ 別シードの仮説検証・PoC・初期構想 | `idea`（着想）/ `exploration`（PoC・検証） | `draft` | `#idea` `#seed` `#exploration` `#exploring` |
| Activities | 継続的活動（社内外コミュニティ・学会委員・グループ・コンペ） | `activity` | `in-progress` | `#activity` `#community` |
| Activities/Ecosystem | 教育→インターン→起業/活躍の循環を創発する組織活動 | `activity` | `in-progress` | `#ecosystem` |
| Learning | 学習・読書・技術メモ | `note` | `in-progress` | `#learning` `#book-note` `#tutorial` |

## Frontmatter

frontmatter スキーマの**単一の正は [[.claude/rules/vault-metadata.md]]**。タグ体系は [[.claude/rules/vault-tagging.md]]。

Others ノート固有の `type` 値（サブカテゴリに対応、status enum は共通）：

- Ideas → `idea`（軽い着想）/ `exploration`（PoC・検証フレーバー）
- Ecosystem → `activity`
- Activities → `activity`
- Learning → `note`

## 昇格フロー（重要）

```
Ideas（着想・検証/PoC を含む） → Research / Work
```

- 昇格タイミング: 「検証で芽が出た」「案件化した」など。
- **移動元に wiki-link を残す**（どこへ昇格したか追えるようにする）。
- 破棄するアイデアは削除せず `status: archived` にして残す。
- Ecosystem はこの種昇格フローとは別の**継続的な組織活動**（循環づくりそのものが目的）。

## サブカテゴリ別の運用

### Ideas（着想 ＋ 別シード検証/PoC）
- 1ファイル1着想、軽量に。完璧を目指さない（`type: idea`）。
- **別シードの仮説検証・PoC・初期構想**もここ（研究本流とは別）。シード単位でサブフォルダ化可：`Ideas/{seed-name}/`。仮説・検証方法・結果を簡潔に（`type: exploration`）。テンプレ：[[Templates/idea-note.md]]（軽い着想）/ [[Templates/exploration-note.md]]（PoC/検証型）。
- 芽が出たら：研究本流は `Research/` へ、案件化は `Work/` へ昇格（移動元にリンクを残す）。
- 定期的に棚卸し：昇格 / `archived` へ。

### Activities
- 活動（サブエリア）ごとにフォルダ化：`Activities/{NAME}/`。入口は `README.md`（`type: activity`）。
- **標準構造（4 層・2026-06-12 確定）**：[[Others/Activities/CLAUDE.md]] がサブエリア共通 Schema。
  - ① Raw：`sources/`（もらった資料 ＋ **Inbox 由来の生データの curate 着地**・非 md 直置き可・immutable・frontmatter は `type: capture` のまま）
  - ② Schema：`Activities/CLAUDE.md`（共通）。固有規約が育ったら `{NAME}/CLAUDE.md` を新設
  - ③ Compiled：`notes/` + `meetings/{YYYY-MM-DD}-{topic}.md`（**genspark MTG は curate 時に要約してここへ**＝inbox-routing §3 例外。raw は git 履歴に残す）
  - ④ Log：`logs/` + `README.md`（入口 MOC・現況）
- コンペ系は `Kaggle/{competition-name}/`、学会参加は `Conferences/{学会名年度}/`（例 `ConfX2026`）。単位フォルダ内の `sources/` は必要になったら作る（YAGNI）。自作の非 md（スクリプト・生成データ）は従来どおり `_assets/` へ。
- 現在のサブエリア（例）：`Community-A`（学会若手会コミュニティの例）/ `Community-B`（同・例）/ `WG-A`（社内/研究 WG の例）/ `WG-B`（同・例）/ `Kaggle`（コンペ）/ `Conferences`（学会参加）/ `Ecosystem`（下記）。実際の所属活動に合わせてリネームする。
- R&D・検証で芽が出たものは `Ideas/` へ切り出し、さらに育てば Research / Work へ昇格（移動元にリンクを残す）。

### Activities/Ecosystem
- 目的：**教育（講義）→ 共同研究チームのインターン招聘 → 実力者が他社で活躍 / 起業（スタートアップ）で課題解決**、という循環＝エコシステムの創発。
- 配置：`Others/Activities/Ecosystem/`（2026-06-12 に Activities 配下へ正式化。種昇格フローとは別の継続的組織活動）。
- 構造：Activities 標準（4 層）に従う。コホート/人材追跡が要れば `cohorts/` 等を足す。
- 個別の研究/事業シードそのものは `Ideas/` や該当ドメインへ。ここは**仕組み・働きかけ**を扱う。

### Learning
- **1 トピック = 1 フォルダ**（2026-06-22 確定）：新しい学習対象を入れるときは、その対象だけのフォルダ `Learning/{Topic}/` を作り、note・関連資料・図版などをその中にまとめる（単発の `.md` を `Learning/` 直下に散らさない）。複数 note・`_assets/`・`sources/` をトピック単位で同居させられる。
- 命名：フォルダは対象名（`Learning/WebWorld/` 等）、中の note は内容を表す名前（`Learning/{Topic}/{title}.md`）。
- 書籍は `#book-note`、チュートリアルは `#tutorial`。
- 学んだ要点 + 自分の言葉での再構成を残す。

## やってはいけない

- 受託案件を Others に置かない（→ `Work/`）。
- 研究本流を Others に置かない（→ `Research/`。`Ideas/` の検証/PoC は別シード限定）。
- 昇格時にリンクを残さず移動しない。

## 関連

- [[Others/CLAUDE.md]] / [[Others/README.md]]
- [[.claude/rules/vault-metadata.md]] / [[.claude/rules/vault-tagging.md]] / [[.claude/rules/language.md]]
