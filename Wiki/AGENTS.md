# AGENTS.md — Wiki（汎用ナレッジの Main DB）

**この vault の唯一の Main DB**。durable な知識すべて — アイデア・学習/読書メモ・文献ノート・実験メモ・活動記録・プロジェクトの知見 — をここに蒸留する。
人と AI が同じ Markdown を読み書きする **general wiki**（Karpathy の "LLM wiki" 思想）。詳細ルールは [[.claude/rules/wiki-management.md]]。

## 構造

```
Wiki/
├── AGENTS.md       # ② Schema：本ファイル
├── {slug}.md       # ③ Compiled：1 ノート = 1 トピック（フラット基本・wikilink で接続）
├── {topic}/        # ③ Compiled：ノートが増えたテーマはサブフォルダ化してよい
├── meetings/       # ③ Compiled：非案件の会議メモ（{YYYY-MM-DD}-{topic}.md）
├── sources/        # ① Raw：Inbox 由来 raw の curate 着地（非 md 可・immutable・type: capture のまま）
└── _assets/        # 非 md 作業物
```

## 書き方

- **1 ノート = 1 トピック**。タイトルは内容を表す名詞句、本文は自分の言葉で再構成（コピペの墓場にしない）
- frontmatter は標準 enum（[[.claude/rules/vault-metadata.md]]）。`type` で分類する：
  - `idea`（着想の種）/ `exploration`（PoC・検証） — テンプレ [[Templates/idea-note.md]] / [[Templates/exploration-note.md]]
  - `note`（学習・読書・技術メモ） / `reference`（参考資料ポインタ）
  - `paper`（文献ノート・Zotero 連携 [[Meta/connections/zotero.md]]） / `experiment`（実験ノート） — テンプレ [[Templates/research-paper-note.md]] / [[Templates/research-experiment-note.md]]
- 関連ノートへ **wikilink を張る**（孤立ノートを作らない）。入口 MOC は [[Maps/Home.md]]

## ライフサイクル

- 流入：EOD distill が Daily から蒸留（[[.claude/skills/eod-distill/SKILL.md]]）、または保存先が自明なら直接配置（Daily に記載を残す）
- 破棄：消さず `status: archived`（必要なら `Archive/` へ退避）

## やってはいけない

- 生ログを直置きしない（Inbox → Daily 集約 → distill の導線を通す。例外は保存先自明時の直接配置のみ）
- エージェント運用の学び（gotcha・root cause）は `.claude/docs/knowledges/` へ（Wiki は人間の知識、knowledges はエージェントの運用知）
