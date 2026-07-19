# Claudian Orchestra — Vault Template

> An Obsidian vault scaffold for running **three AI agents (Claude Code / Codex / Hermes) as a knowledge-base orchestra** on top of your second brain.
>
> プレーン Markdown の知識ベースを「人と AI の共有メモリ」にする — 設計と運用契約一式のテンプレート．

---

## これは何

Zenn 記事「**続：AI 時代のタスク管理を考える．Claudian orchestra**」で紹介した **MY_MEMORY** という個人 vault の **scaffold（骨組み）だけを公開**したものです．

クライアント名・個人情報・実コンテンツはすべて取り除き，**Markdown のフォルダ構造**・**3 エージェントの契約（`CLAUDE.md` / `AGENTS.md` / `.hermes/`）**・**運用ルール（`.claude/rules/`）**・**スキル群（`.claude/skills/`）**・**ノートテンプレ（`Templates/`）** だけを残しています．clone してそのまま Obsidian で開けば，自分版の "Claudian orchestra" を立ち上げられます．

- 記事本文: [続：AI 時代のタスク管理を考える．Claudian orchestra](https://zenn.dev/mkj/articles/claudian-orchestra_20260616)（公開後）
- 設計思想: Karpathy の "LLM wiki"・Google の Open Knowledge Format（OKF）・PKM の Zettelkasten 伝統と整合
- フォーマット: **Just markdown / Just files / Just YAML frontmatter**（OKF 整合）．プラットフォーム非依存．

---

## アーキテクチャ概要

![Claudian Orchestra architecture — Obsidian Workspace (MY_MEMORY Vault) + Claude Code Orchestra (Claude Code / Codex / Hermes) + External Sources](assets/architecture.png)

*Vault そのものを共有メモリに、3 エージェント（Claude Code / Codex / Hermes）がその上で協調する。左＝Obsidian Workspace、中央＝Claude Code Orchestra、右＝External Sources。*

情報の流れは **capture → Daily ハブ → Main DB** の 3 段：

```
External Source
   │ ① capture（Hermes・拡張 only）
   ▼
Inbox/{YYYY-MM-DD}/{source}/{file}.md     ← 日付ファースト・auto-route なし
   │ ② aggregate（Claude が当日中に Daily へ集約）
   ▼
Daily/{YYYY-MM-DD}.md                      ← その日の唯一のハブ
   │ ③ distribute（EOD に Main DB へ蒸留・配分）
   ▼
Work / Research / Others                   → Evergreen
```

詳細は [`CLAUDE.md`](./CLAUDE.md) / [`AGENTS.md`](./AGENTS.md) / [`.claude/rules/`](./.claude/rules/) を参照．

---

## クイックスタート

> **初めての人はまず [`GETTING-STARTED.md`](./GETTING-STARTED.md) を読んでください。** 全部を一度にセットアップする必要はなく、Obsidian + Claude Code だけ(15分)→ Codex → Hermes → 外部接続 1 本ずつ、という段階式で始められます。外部接続(Slack / Google / GitHub 等)の個別手順とトラブルシューティングは [`docs/connections/`](./docs/connections/README.md) にあります。

### 1. clone してリネーム

```bash
git clone https://github.com/your-org/claudian-orchestra.git my-vault
cd my-vault
```

### 2. Obsidian で開く

`Open folder as vault` でこのディレクトリを選ぶ．`.obsidian/` に最小設定が入っているので、そのまま開けば vault として認識される．

### 3. エージェントを接続する

| Agent | 役割 | 必要なもの |
|---|---|---|
| **Claude Code** | orchestrator | [Claude Code CLI](https://docs.claude.com/claude-code) ＋ Anthropic アカウント |
| **Codex** | implementer | [Codex CLI](https://github.com/openai/codex)（ChatGPT サブスクリプション） |
| **Hermes** | ingestion | [Hermes Agent](https://github.com/NousResearch/Hermes-Agent)（Slack / Google / GitHub の認証） |

Hermes は任意です．Slack / Calendar / Tasks の自動取り込みを使わないなら **Claude Code + Codex だけ**で十分動きます．その場合は `Inbox/` への投入を全部手動でやることになります．

外部接続の繋ぎ込みは PKM 最大の躓きポイントなので，接続ごとに**手順・動作確認・よくある失敗**をまとめたガイドを用意しています：

- 段階式セットアップ：[`GETTING-STARTED.md`](./GETTING-STARTED.md)（Level 0〜3）
- 接続別ガイド：[`docs/connections/`](./docs/connections/README.md)（GitHub / Google / Slack / クリッピング / Genspark / Notion）
- 診断：Claude Code に「**接続チェックして**」と言えば [`connection-doctor`](./.claude/skills/connection-doctor/SKILL.md) skill がどこが繋がっていてどこが切れているかを表で報告します

### 4. 自分用に整える

- `Work/PROJ_A/` を実際の案件コード（例：`Work/MYCLIENT/`）にリネーム．`.claude/rules/work-management.md` の対応表も更新．
- `Persona/CLAUDE.md` に自分のプロフィールを書く（vault 全体から参照される identity の単一の正）．
- `Maps/Home.md` に自分の vault の入口を書く．
- 不要な skill は `.claude/skills/` から削除して構わない（特に `.hermes/skills/mymemory/` 配下の外部接続は，使うものだけ残す）．

---

## 何が入っているか

| パス | 中身 |
|---|---|
| [`GETTING-STARTED.md`](./GETTING-STARTED.md) | 段階式セットアップガイド（Level 0〜3・初めての人はここから） |
| [`docs/connections/`](./docs/connections/) | 外部接続の個別セットアップガイド（GitHub / Google / Slack / クリッピング / Genspark / Notion） |
| [`CLAUDE.md`](./CLAUDE.md) | Claude Code 向けオーケストレーション契約（vault の最上位ルール） |
| [`AGENTS.md`](./AGENTS.md) | Codex / 外部エージェント向け契約 |
| [`.claude/rules/`](./.claude/rules/) | 運用ルール（frontmatter / tagging / Daily 運用 / Inbox routing / Work / Others 等） |
| [`.claude/skills/`](./.claude/skills/) | Claude Code skill 群（daily-briefing / aggregate-* / eod-distill / work-project-writer / vault-archive など） |
| [`.claude/agents/`](./.claude/agents/) | サブエージェント定義（general-purpose） |
| [`.claude/hooks/`](./.claude/hooks/) | Codex 委譲を強制する hook |
| [`.claude/docs/knowledges/`](./.claude/docs/knowledges/) | 運用で得た学びの structured knowledge base（テンプレでは README のみ） |
| [`.codex/`](./.codex/) | Codex 側の契約・skill 共有 |
| [`.hermes/`](./.hermes/) | Hermes 宣言的設定の雛形（`config.yaml`） + MY_MEMORY 固有 capture skill（mymemory/） |
| [`Templates/`](./Templates/) | ノートテンプレ（daily / weekly / work / idea / exploration / paper / experiment 等） |
| [`Maps/`](./Maps/) | 横断 MOC（Home / Code-Map / People-Map）＋ 5 ラベル Bases ビュー |
| [`Work/PROJ_A/`](./Work/PROJ_A/) | クライアント案件の 4 層標準構造（sources / docs / meetings / code / deliverables / proposals / references / logs） |
| [`Others/`](./Others/) | Ideas / Activities / Learning |
| [`Persona/`](./Persona/) | 著者プロフィールの単一の正（vault 全体から参照） |
| [`Inbox/`](./Inbox/) | 外部 capture の受け口（日付ファースト） |
| [`Daily/`](./Daily/) | デイリー / ウィークリージャーナル |
| [`Archive/`](./Archive/) | 非活性退避先 |
| [`Meta/`](./Meta/) | vault 自身についての作業（自己言及プロジェクト） |
| [`Research/`](./Research/) | 研究用プレースホルダ（必要なら git submodule で外部リポを mount） |

`.gitignore` は **secret は絶対に commit しない / runtime state は version しない** という方針で組まれています（特に `.hermes/skills/*` 配下は **mymemory/ 以外を除外**するように設定済み）．

---

## 設計の思想（短く）

1. **Vault そのものがインターフェース**：人も AI も同じ Markdown を読み書きする．特定 SaaS にロックインされない．
2. **正本（system of record）の所在を決め切る**：会話=Slack / ToDo=GTasks / 予定=GCal / コード=GitHub / 記憶=この vault．重複保有しない．
3. **capture と curate を分ける**：Hermes は `Inbox/` に投げるだけ．判断と移動は Claude＋人間．
4. **書き手は時点ごとに 1 人**：split-brain を避けるため，同じファイルを 2 体が同時に触らない．
5. **proposal → delivery を地続きに**：案件は `Work/{CODE}/` の中で提案フェーズもデリバリフェーズも 4 層標準で扱う．
6. **on-demand 既定**：Daily の `## 🤖 ジョブリスト` を見て人間が「これやって」と指示する．cron 多用しない．

---

## ライセンス

[MIT](./LICENSE)．scaffold は自由に改変・派生してください．

## 謝辞

- Andrej Karpathy — "LLM wiki / AI second brain"
- Google Cloud — Open Knowledge Format
- Andy Matuschak — Evergreen notes
- Nous Research — Hermes Agent

設計の収斂は [記事](https://zenn.dev/mkj/articles/claudian-orchestra_20260616) に書きました．フィードバック・PR は歓迎です．
