# Vault メタデータスキーマ

> このファイルが frontmatter schema の**単一の正（single source of truth）**である。各 domain rule と skill は schema を再定義せず、このファイルを参照する。

## 1. 標準ノート

`Daily/`、`Wiki/`、`Maps/`、`Meta/`、`Archive/` などの通常ノートには、次の共通 field を含める。

```yaml
---
title: "ノートタイトル"
type: "note" # note | log | deliverable | paper | experiment | reference | idea | exploration
status: "draft" # draft | in-progress | completed | archived
tags: ["tag1", "tag2"]
created: "2026-05-29"
updated: "2026-05-29"
resource: "..." # optional
---
```

日付は `YYYY-MM-DD` とし、template 内の未展開 placeholder も YAML string として quote する。

### `resource`（任意・OKF 整合）

- 外部に正本（system of record）があるノートだけに付ける。正本がなければ省略する。
- 値は外部 URL、vault 相対 path、SoR identifier のいずれかとする。
  - GitHub blob URL、Slack permalink、Notion URL
  - `Wiki/sources/spec-v2.pdf`
  - `gtasks:task:<id>` / `slack:thread:<id>` / `meeting:<provider>:<id>`
- `repo:`、`paper_url:`、`github_link:` などの type 固有 field と併存してよい。`resource` はその汎用上位概念である。
- `routed_from` / `archived_from` は provenance であり、正本への pointer ではない。`resource` に統合しない。
- 設計の背景を自己言及 project に残す場合は、`Meta/{project-name}/notes.md` などの実在 path を使う。未展開 placeholder を wikilink にしない。

## 2. 標準 type と status

### Wiki type

| 用途 | `type` |
|---|---|
| 学習・読書・技術メモ | `note` |
| 活動記録 | `note` + `#activity` |
| 着想の種 | `idea` |
| 仮説検証・PoC | `exploration` |
| 文献ノート | `paper` |
| 実験ノート | `experiment` |
| 参考資料 | `reference` |

詳細は [[.codex/rules/wiki-management.md]]。

### Status

| Context | `draft` | `in-progress` | `completed` | `archived` |
|---|---|---|---|---|
| **Wiki** | 着想直後・読書開始前 | 検証中・読書中・実験中 | 結論・成果が確定 | 棚卸し・退避 |
| **Daily** | 使用しない | 当日進行中 | その日を終了 | 使用しない |

### Type

| Type | 説明 |
|---|---|
| `note` | 一般ノート。Wiki の学習・活動記録を含む |
| `log` | Daily / Weekly などの進捗ログ |
| `deliverable` | 納品物・最終成果 |
| `paper` | 文献ノート |
| `experiment` | 実験ノート |
| `reference` | 参考資料 |
| `idea` | 着想の種 |
| `exploration` | 仮説検証・PoC |

## 3. type 固有 field

### 論文ノート

`type: paper` では次を追加する。

```yaml
theme: "your-research-theme"
arxiv_id: "2401.12345"
paper_authors: "Author1, Author2"
paper_date: "2024-01-15"
paper_url: "https://arxiv.org/abs/2401.12345"
related_papers: ["2301.xxxxx", "2302.xxxxx"]
key_methods: ["method1", "method2"]
```

### 実験ノート

`type: experiment` では次を追加する。

```yaml
theme: "your-research-theme"
experiment_id: "EXP-2026-001"
objective: "実験の目的"
hypothesis: "仮説"
reproducible: true
resource_consumed: "GPU: 8xA100, Memory: 256GB, Time: 12h"
github_link: ""
```

### Daily

```yaml
---
title: "2026-05-29 デイリー"
type: "log"
status: "in-progress"
tags: []
created: "2026-05-29"
updated: "2026-05-29"
---
```

終了時に `status: completed` へ更新する。

### Weekly / Monthly

```yaml
---
title: "Weekly Review - W22 (2026-05-26 ~ 2026-06-01)"
type: "log"
status: "completed"
period: "week" # week | month
tags: ["weekly-review"]
created: "2026-06-02"
updated: "2026-06-02"
---
```

### Archive

`Archive/` へ退避したノートには `status: archived` と次を追加する。

```yaml
archived: "2026-06-02"
archived_from: "Wiki/2026-01-15-old-note.md"
```

詳細は [[.codex/skills/vault-archive/SKILL.md]]。

## 4. raw-capture path override

次の path class は compiled / curated note ではなく、immutable な raw capture である。

- `Inbox/{YYYY-MM-DD}/**/*.md`
- `Wiki/sources/**/*.md`

両方で次の enum と共通 field を使う。

```yaml
---
title: "capture title"
type: "capture"
status: "inbox"
tags: ["capture"]
created: "2026-05-29"
updated: "2026-05-29"
source: "provider:item:<id>"
---
```

- `Inbox/` は未集約の受信域、`Wiki/sources/` は EOD で承認済みの raw archive だが、同一 raw artifact であることを示すため `type: capture` / `status: inbox` を維持する。`Wiki/sources/` の `status: inbox` は作業状態ではなく、raw-capture class の固定 enum として扱う。
- `Wiki/sources/` へ move した raw file は immutable とする。要約や tag 変更は別の compiled Wiki note に行う。
- meeting transcript は raw archive の例外である。provider を問わず要約を `Wiki/meetings/{date}-{topic}.md` に標準 enum で作成し、raw transcript は `Wiki/sources/` に移さない。raw の同一内容が commit 済みと確認できるまで Inbox に保持し、確認後もユーザー承認なしに削除しない。
- capture の共通 field に加え、source 固有 field を保持してよい。

capture writer は Hermes と capture extension である。コアとユーザーは Inbox に直接書かない。Hermes は Daily 集約前に限って同じ capture job を idempotent に再実行できる。Daily に source link が集約された時点で所有権はコア + ユーザーへ移り、Hermes はその file を以後更新しない。

主な capture path：

- [[.hermes/skills/vault-capture/inbox-daily-capture/SKILL.md]] → `Inbox/{date}/daily/daily.md`
- [[.hermes/skills/vault-capture/slack-capture/SKILL.md]] → `Inbox/{date}/slack/{channel}.md`
- meeting provider adapter / capture extension → `Inbox/{date}/mtgs/{provider}-{slug}.md`
- [[.hermes/skills/vault-capture/github-eod-capture/SKILL.md]] → `Inbox/{date}/code/code.md`
- [[.hermes/skills/vault-capture/clippings-capture/SKILL.md]] → `Inbox/{date}/clippings/{slug}.md`
- AI Exporter / Web Clipper → `Inbox/{date}/chat-logs/{provider}-{slug}.md`

## 5. knowledge-note path override

`.codex/docs/knowledges/{category}/{slug}.md` は、agent operation の durable learning 専用 schema を使う。`.codex/docs/knowledges/README.md` は MOC なので標準 `type: note` を使う。

knowledge note の required field：

```yaml
---
title: "学びの名前"
type: "knowledge"
status: "active" # active | superseded | deprecated
tags: ["category", "subdomain"]
created: "2026-05-29"
updated: "2026-05-29"
source: "session:2026-05-29"
applies_to: ["component/area"]
severity: "medium" # low | medium | high
---
```

- `superseded` では `superseded_by` を追加する。
- `deprecated` では `deprecated_at` と理由を本文に追加する。
- 詳細は [[.codex/skills/knowledge-capture/SKILL.md]]。

## 6. curate 時の enum 移行

- raw から**別の compiled note**を作る場合、compiled note は標準 `type` / `status` を使う。
- raw file 自体を `Wiki/sources/` へ move する場合は §4 の path override を適用し、`type: capture` / `status: inbox` を書き換えない。
- meeting transcript は §4 の例外として、compiled meeting note だけを残す。
- `source` / `created` は provenance として保持する。

整合性チェック（[[.codex/skills/vault-consistency-check/SKILL.md]] Check #2）は path-aware validation を行い、標準ノート、raw capture、knowledge note の各 class に対応する schema を適用する。

## 関連

- [[.codex/rules/wiki-management.md]] / [[.codex/rules/daily-operations.md]]
- [[.codex/rules/inbox-routing.md]] / [[.codex/rules/vault-tagging.md]] / [[.codex/rules/language.md]]
