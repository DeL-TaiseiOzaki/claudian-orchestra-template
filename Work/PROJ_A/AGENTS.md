# AGENTS.md — Work/PROJ_A（Client A）

PROJ_A 案件固有の **Schema 層**（規約・定数）。ドメイン共通ルールは [[Work/AGENTS.md]]・[[.claude/rules/work-management.md]]。
**役割分担**：人間向けの入口（概要・主要リンク）は `project.md`、現在の状態は `status.md`。本ファイルには**規約と定数のみ**を書き、概要・状態を重複させない。

## 案件コンテキスト（定数）

| 項目 | 内容 |
|---|---|
| クライアント | Client A |
| 案件コード / タグ | `PROJ_A` / `#proj-a` |
| 関連 Slack channel | TBD |
| GitHub repos | `Work/PROJ_A/code/README.md` 参照 |
| 納期 / マイルストーン | `status.md` 参照 |

## フォルダの 4 層構造

| 層 | 場所 | 書き手 | 内容 |
|---|---|---|---|
| ① Raw | `sources/`（手動投入＋Inbox 由来の生データの curate 着地・非 md 可・immutable・frontmatter は `type: capture` のまま） | ユーザー / コアエージェント | 先方からもらったデータ・資料 ＋ Slack/コード/添付などの curate 着地 |
| ② Schema | `AGENTS.md`（本ファイル） | コアエージェント + ユーザー | 案件固有の規約・定数 |
| ③ Compiled | `docs/` `meetings/` `code/` `deliverables/` `proposals/` `references/` | コアエージェント + ユーザー | 蒸留済みドキュメント・成果物・サーベイ資料 ＋ **受注前の提案成果物（`proposals/`）** |
| ④ Log | `logs/` + `status.md` `team.md` | コアエージェント + ユーザー | 時系列ログ・現在状態 |

## sources/ の運用（Raw 層）

- 先方からもらったファイル（データ・資料・PDF・Excel 等）は**とりあえず `sources/` へ**（非 md 直置き可 — `_assets/` 規約の案件内例外）
- **sources/ は先方由来の資料 ＋ Inbox 由来の生データ（hermes capture）の curate 着地**（frontmatter は `type: capture` のまま）。サーベイ結果は `references/` へ
- **immutable 扱い**：リネーム・編集・削除しない（provenance 維持）
- genspark MTG は curate 時に要約して `meetings/{YYYY-MM-DD}-{topic}.md`（compiled）へ（[[.claude/rules/inbox-routing.md]] §3 の唯一の例外）
- 大容量データの正本は外部（GitHub / クラウドストレージ / HuggingFace 等）に置き、ここにはポインタ md でもよい

## 案件固有規約

- frontmatter：`project: "PROJ_A"` / `client: "Client A"` 必須（[[.claude/rules/vault-metadata.md]]）
- クライアント機密の分離：他案件フォルダへの情報の混在・流用は厳禁
- （案件固有の命名・規約が増えたらここに追記する）
