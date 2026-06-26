# CLAUDE.md — Others（Work / Research 以外）

受託案件（Work）・研究本流（Research）に属さない活動のホーム。
ここは**作業の入口（道標）**。詳細ルールは [[.claude/rules/others-management.md]]。
言語はユーザーの裁量（[[.claude/rules/language.md]]）。

## サブカテゴリ（どこに置くか）

| フォルダ | 用途 | type | 主なタグ |
|---|---|---|---|
| `Ideas/` | アイデア帳。着想の種を素早く記録＋研究本流とは別シードの仮説検証・PoC・初期構想 | `idea`（着想）/ `exploration`（PoC/検証） | `#idea` `#seed` `#exploration` `#exploring` |
| `Activities/` | 継続的な活動（社内外コミュニティ・学会委員・グループ・コンペ） | `activity` | `#activity` `#community` |
| `Learning/` | 個人学習・読書ノート・技術メモ（1 トピック = 1 フォルダ） | `note` | `#learning` `#book-note` |

## Activities サブエリア構造（4 層）

```
Activities/{NAME}/
├── README.md       # ④ Log：入口 MOC・現況
├── CLAUDE.md       # ② Schema：固有規約（共通は Others/Activities/CLAUDE.md）
├── sources/        # ① Raw：もらった資料 + Inbox curate 着地
├── notes/          # ③ Compiled：蒸留ノート
├── meetings/       # ③ Compiled：会議メモ（genspark MTG は要約してここへ）
└── logs/           # ④ Log：活動ログ
```

## 昇格フロー

```
Ideas（着想・検証/PoC を含む） → Research / Work（昇格）
```

- 昇格・移動時は**移動元に wiki-link を残す**（トレーサビリティ）
- 破棄するアイデアは消さず `status: archived` にして残す

## やってはいけない

- 受託案件を Others に置かない（→ `Work/`）
- 研究本流を Others に置かない（→ `Research/`。`Ideas/` の検証/PoC は**別シード限定**）
- アイデアを `Ideas/` に溜めっぱなしにしない（定期的に 昇格 / archived を判断）

## 関連

- [[Others/README.md]] / [[.claude/rules/others-management.md]]
- [[.claude/rules/vault-metadata.md]] / [[.claude/rules/vault-tagging.md]] / [[.claude/rules/language.md]]
