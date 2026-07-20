# Wiki 管理ルール

durable な知識の運用ルール。入口は [[Wiki/AGENTS.md]]。
Main DB は **Wiki 一本**（エージェント運用知のみ `.codex/docs/knowledges/`）。

## 何を置くか（type 対応）

| 内容 | type | status の起点 | 主なタグ例 | テンプレ |
|---|---|---|---|---|
| アイデア・着想の種 | `idea` | `draft` | `#idea` `#seed` | [[Templates/idea-note.md]] |
| 仮説検証・PoC | `exploration` | `draft` | `#exploration` | [[Templates/exploration-note.md]] |
| 学習・読書・技術メモ | `note` | `in-progress` | `#learning` `#book-note` `#tutorial` | — |
| 文献ノート（論文） | `paper` | `draft` | `#to-read` `#key-paper` | [[Templates/research-paper-note.md]] |
| 実験ノート | `experiment` | `in-progress` | `#reproducible` 等 | [[Templates/research-experiment-note.md]] |
| 活動・プロジェクト記録（コミュニティ・委員・案件） | `note` | `in-progress` | `#community` `#activity` `#meeting` | — |
| 参考資料ポインタ | `reference` | `completed` | — | — |

frontmatter スキーマの単一の正は [[.codex/rules/vault-metadata.md]]、タグ体系は [[.codex/rules/vault-tagging.md]]。

## 配置規則

- **フラット基本**：`Wiki/{slug}.md`（1 ノート = 1 トピック）。同一テーマのノートが 3 枚を超えたら `Wiki/{topic}/` にサブフォルダ化してよい（移動時はリンクを保つ）
- 会議メモ：`Wiki/meetings/{YYYY-MM-DD}-{topic}.md`（AI 議事録の要約着地先。テンプレ [[Templates/meeting-note.md]]。[[.codex/skills/mtg-prep/SKILL.md]] / [[.codex/skills/inbox-aggregate/SKILL.md]]）
- Inbox 由来の raw（clippings / chat-logs / discord digest 等）を残す場合：`Wiki/sources/` に raw のまま（`type: capture` / `status: inbox` を保持・immutable）。これは [[.codex/rules/vault-metadata.md]] §4 の path override であり、compiled note の標準 enum とは別 class。蒸留 note は Wiki 直下に別途書き、raw へ wikilink する
- 文献管理の正本は Zotero（[[Meta/connections/zotero.md]]）。Wiki には文献ノート（`type: paper`）と `resource:` ポインタだけ置く。PDF は置かない

## ライフサイクル

```
Daily（日中ログ・集約）
   │ EOD distill（承認つき）
   ▼
Wiki/{slug}.md          ← durable な知識の終着（evergreen 化）
```

- 破棄するノートは削除せず `status: archived`（肥大化したら [[.codex/skills/vault-archive/SKILL.md]] で `Archive/` へ）
- 定期棚卸し：weekly-review 時に `draft` のまま放置された idea を昇格 / archived に振り分ける

## やってはいけない

- 生ログの直置き（→ `Inbox/` 経由。保存先自明の直接配置時も Daily に記載）
- エージェント運用の学び（gotcha / root cause / 外部 CLI の仕様変化）を Wiki に書かない（→ `.codex/docs/knowledges/`、[[.codex/skills/knowledge-capture/SKILL.md]]）
- 自己紹介・経歴を書かない（→ `Persona/`）

## 関連

- [[Wiki/AGENTS.md]] / [[.codex/skills/wiki-writer/SKILL.md]]
- [[.codex/rules/vault-metadata.md]] / [[.codex/rules/vault-tagging.md]] / [[.codex/rules/daily-operations.md]]
- [[.codex/skills/eod-distill/SKILL.md]]（Daily → Wiki の蒸留）
