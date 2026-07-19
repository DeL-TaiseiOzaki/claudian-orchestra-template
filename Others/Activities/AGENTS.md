# Others/Activities — サブエリア共通 Schema

Activities 配下の各サブエリア（`Community-A/` `Community-B/` `WG-A/` `WG-B/` `Kaggle/` `Conferences/` `Ecosystem/` 等）に共通する規約。
詳細運用は [[.claude/rules/others-management.md]] §Activities。

## 4 層標準（vault 全体のフラクタル）

```
Activities/{NAME}/
├── README.md     # ④ Log：入口 MOC・現況
├── sources/      # ① Raw：もらった資料 + Inbox 由来生データの curate 着地（非 md 可・immutable・type: capture のまま）
├── notes/        # ③ Compiled：蒸留ノート
├── meetings/     # ③ Compiled：会議メモ（{YYYY-MM-DD}-{topic}.md）。genspark MTG は要約してここへ
└── logs/         # ④ Log：活動ログ
```

- ② Schema は本ファイル（共通）。固有規約が育ったサブエリアは `{NAME}/AGENTS.md` を新設してよい（そちらが優先）。
- `sources/` は immutable：リネーム・編集・削除しない（provenance 維持）。蒸留は `notes/` / `meetings/` に別ノートを書く。
- 単位フォルダ内の `sources/` は必要になったら作る（YAGNI）。自作の非 md（スクリプト・生成データ）は `_assets/` へ。

## Frontmatter

- スキーマの単一の正は [[.claude/rules/vault-metadata.md]]。`type: activity` / status は標準 enum。
- `sources/` 配下の Inbox 由来ファイルのみ `type: capture` を保持。

## 命名

- 会議メモ：`meetings/{YYYY-MM-DD}-{topic}.md`
- コンペ：`Kaggle/{competition-name}/`、学会参加：`Conferences/{学会名年度}/`（例 `ConfX2026`）

## 関連

- [[Others/AGENTS.md]] / [[.claude/rules/others-management.md]] / [[.claude/rules/vault-metadata.md]]
