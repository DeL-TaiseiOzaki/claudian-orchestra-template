# AGENTS.md — Work（受託案件）

クライアント案件のホーム。詳細ルールは [[.claude/rules/work-management.md]]、frontmatter スキーマは [[.claude/rules/vault-metadata.md]]、入口 MOC は [[Maps/Home.md]]。

## 案件一覧

このテンプレでは **PROJ_A** だけ 4 層構造の雛形を置いている。実案件を始めるときは：

1. `Work/PROJ_A/` を実コードにリネーム（例：`Work/ACME/`）。
2. `.claude/rules/work-management.md` のプロジェクト表を更新。
3. `.claude/rules/vault-tagging.md` のプロジェクトタグ表を更新。
4. 新規案件は [[.claude/skills/work-kickoff/SKILL.md]] が立ち上げをガイドする。

## 4 層標準（フラクタル）

各案件フォルダは vault 全体のアーキテクチャ（Raw → Schema → Compiled → Log）を**フラクタルに再現**する：

```
Work/{CODE}/
├── AGENTS.md        # ② Schema：案件固有の規約・定数
├── project.md       # 入口 MOC（人間向け）
├── status.md        # ④ Log：現況
├── team.md          # ④ Log：チームメンバーのタスク状況
├── sources/         # ① Raw：先方資料 ＋ Inbox curate 着地
├── meetings/        # ③ Compiled：会議メモ
├── docs/            # ③ Compiled：定常ドキュメント
├── code/            # ③ Compiled：コード読解
├── deliverables/    # ③ Compiled：納品物
├── proposals/       # ③ Compiled：受注前の提案成果物
├── references/      # ③ Compiled：自前サーベイ
└── logs/            # ④ Log：案件デイリーログ
```

詳細：[[.claude/rules/work-management.md]]
