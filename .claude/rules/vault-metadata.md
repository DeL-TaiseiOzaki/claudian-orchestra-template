# Vault メタデータスキーマ

> このファイルが frontmatter スキーマの**単一の正（single source of truth）**。各ドメインルール（wiki / daily-operations 等）はスキーマを再定義せず、ここを参照する。

## 共通 Frontmatter フィールド

すべてのノートに以下を含める：

```yaml
---
title: "ノートタイトル"
type: "note" | "log" | "deliverable" | "paper" | "experiment" | "reference" | "idea" | "exploration"
status: "draft" | "in-progress" | "completed" | "archived"
tags: ["tag1", "tag2"]
created: 2026-05-29
updated: 2026-05-29
resource: "..."  # optional — see "resource（任意・OKF 整合）" below
---
```

### resource（任意・OKF 整合）

- **任意（optional）**：外部の正本（system of record）を持つノートにのみ付す。無いノートには付けない。
- **用途**：このノートが説明 / 蒸留している正本への正規ポインタ（横断クエリ可能にする）。
- **値の形**：
  - 外部 URL（例：GitHub blob URL `https://github.com/<org>/<repo>/blob/main/...`、Slack permalink、Notion URL）
  - vault 相対パス（例：`Wiki/sources/spec_v2.pdf` ＝ `sources/` 一次資料の蒸留ノートで使う）
  - SoR 識別子（例：`gtasks:task:<id>` / `slack:thread:<...>` / `genspark:meeting:<task_id>` ＝ Inbox `source:` 規約と整合）
- **既存の型特化フィールドとの関係**：`repo:`（code ノート）/ `paper_url:`（論文）/ `github_link:`（実験）は併存維持。`resource` はそれらの**汎用上位概念**で、主に新規 curated ノート（Wiki 等）で使う。code ノートは慣例どおり `repo:` を使い続けてよい（OKF emit 時に `repo → resource` とマップ）。
- **provenance とは別概念**：`routed_from` / `archived_from` は来歴（どこから来たか）であり「現在の正本はどこか」ではない。`resource` に統合しない。
- **背景**：[[Meta/{your-meta-project}/notes.md]] / [[Meta/{your-meta-project}/proposal.md]]（2026-06-16 採用）。

## Wiki ノート用の type 値

| 用途 | type |
|---|---|
| 学習・読書・技術メモ | `note` |
| 活動記録（コミュニティ・委員等） | `note`（＋ `#activity` タグ） |
| 着想の種 | `idea` |
| 仮説検証・PoC | `exploration` |
| 文献ノート（Zotero 連携） | `paper` |
| 実験ノート | `experiment` |
| 参考資料 | `reference` |

詳細運用は [[.claude/rules/wiki-management.md]]。

## 文献・実験ノート用の追加フィールド（Wiki）

### 論文ノート
```yaml
---
theme: "your-research-theme"
type: "paper"
arxiv_id: "2401.12345"
paper_authors: "Author1, Author2"
paper_date: "2024-01-15"
paper_url: "https://arxiv.org/abs/2401.12345"
related_papers: ["2301.xxxxx", "2302.xxxxx"]
key_methods: ["method1", "method2"]
---
```

### 実験ノート
```yaml
---
theme: "your-research-theme"
type: "experiment"
experiment_id: "EXP-2026-001"
objective: "実験の目的"
hypothesis: "仮説"
reproducible: true | false
resource_consumed: "GPU: 8xA100, Memory: 256GB, Time: 12h"
github_link: "リンク（あれば）"
---
```

## Daily ノート

```yaml
---
title: "Daily - 2026-05-29"
type: "log"
status: "completed"
---
```

## Weekly/Monthly ノート

```yaml
---
title: "Weekly Review - W22 (2026-05-26 ~ 2026-06-01)"
type: "log"
period: "week" | "month"
---
```

## Archive 用フィールド（退避時のみ）

`status: archived` で `Archive/` へ退避したノートに付す（[[.claude/skills/vault-archive/SKILL.md]]）：

```yaml
status: "archived"
archived: 2026-06-02                              # 退避した日
archived_from: "Wiki/2026-01-15-old-note.md"        # 元パス（provenance）
```

## Status の使い分け

| Context | Draft | In-Progress | Completed | Archived |
|---------|-------|-------------|-----------|----------|
| **Wiki** | 着想直後・読始 | 検証中・読中/実験中 | 結論・成果 | 棚卸し・破棄 |
| **Daily** | N/A | 進行中 | その日終了 | N/A |

## Type の使い分け

| Type | 説明 |
|------|------|
| `note` | 一般的なノート（Wiki の学習・活動記録含む。活動記録は `#activity` タグ） |
| `log` | 進捗ログ、日記（Daily / Weekly） |
| `deliverable` | 納品物、最終成果 |
| `paper` | 文献ノート（Wiki・Zotero 連携） |
| `experiment` | 実験ノート（Wiki） |
| `reference` | 参考資料 |
| `idea` | 着想の種（Wiki） |
| `exploration` | 別シードの仮説検証・PoC（Wiki） |

## Inbox-source 拡張（capture skills 専用）

`Inbox/**` 配下の **raw capture** ファイルは、curated とは別ライフサイクルなので
標準 enum 外の値を使ってよい（path-based override）：

| Field | Inbox-source 値 | 用途 |
|---|---|---|
| `type` | `capture` | raw 取り込み（curated と区別する） |
| `status` | `inbox` | 未 curate（Step 6 の distill 待ち）|

対象 capture skills（Hermes 側、[[.claude/rules/inbox-routing.md]] §2）：

- [[.hermes/skills/vault-capture/inbox-daily-capture/SKILL.md]] → `Inbox/{date}/daily/daily.md`
- [[.hermes/skills/vault-capture/slack-capture/SKILL.md]] → `Inbox/{date}/slack/{channel}.md`（DM は `dm-{counterpart}.md`、複数 workspace は `{workspace}-{channel}.md`）
- [[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]] → `Inbox/{date}/mtgs/genspark-{slug}.md`（割り振りは curate で）
- [[.hermes/skills/vault-capture/github-eod-capture/SKILL.md]] → `Inbox/{date}/code/code.md`
- [[.hermes/skills/vault-capture/clippings-capture/SKILL.md]] → `Inbox/{date}/clippings/{slug}.md`
- AI Exporter / Web Clipper（ブラウザ拡張 + Local REST API） → `Inbox/{date}/chat-logs/{provider}-{slug}.md`（curate 時は `source: chat:<provider>:<id>` に正規化）

**移行ルール**：curated 領域（`Wiki/`・`Daily/`・`Maps/`）へ
move された時点で `type` / `status` は標準 enum に書き換える。これは **Step 6（夜の振り返り＋distill）で
Claude が curate する時の責務**。Hermes は **capture のみ**（auto-route は廃止・[[.claude/rules/inbox-routing.md]]）。`Inbox/{date}/` 内の file を hermes が二度触らず、Claude による curate を待つのが原則。

整合性チェック（[[.claude/skills/vault-consistency-check/SKILL.md]] Check #2）は
**path-aware validation** で `Inbox/**` には Inbox 専用 enum、curated 領域には標準 enum を適用する。

## 関連

- [[.claude/rules/wiki-management.md]] / [[.claude/rules/daily-operations.md]]
- [[.claude/rules/vault-tagging.md]] / [[.claude/rules/language.md]]
