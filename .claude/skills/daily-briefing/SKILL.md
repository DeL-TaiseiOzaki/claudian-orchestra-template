---
name: daily-briefing
description: Compose the day's root Daily note (Daily/{YYYY-MM-DD}.md) at morning startup. Reads Hermes-staged raw data from Inbox/{YYYY-MM-DD}/daily/daily.md (Google Calendar events + Google Tasks) and renders the morning briefing (today's schedule, tasks, Genspark join reminders, Today's Focus, job list). If the Inbox stage is missing, prompts the user to run inbox-daily-capture via the Daily-note ジョブリスト rather than fetching directly (external connections are hermes-only per agent-boundaries.md §6). Morning-only — mid-day on-demand aggregation per source is handled by aggregate-* skills, and EOD distill to Main DB by the independent eod-distill skill (2026-06-16 split). Also surfaces MTG prep: it lists today's meetings (with conference URL) and prompts mtg-prep to create 議事録 stubs in the right meetings/ folder and link them from Daily — the briefing offers/guides only; the interactive stub creation (which interviews the user) runs inside mtg-prep. Use for morning briefing or re-running the morning section.
---

# Daily Briefing Skill

## 目的

朝の起動時に **root の Daily ノート（`Daily/{YYYY-MM-DD}.md`）を構成**する。
**Calendar 予定もタスクも、すべて `Inbox/{YYYY-MM-DD}/daily/daily.md`（hermes が capture 済み）から読む**。外部接続（ics fetch・Calendar/Tasks MCP）は Claude 側から行わない（[[.claude/rules/agent-boundaries.md]] §6 — 外部接続は hermes に一元集約）。Inbox 未取得時はジョブリストから取り込みを促す（[[.claude/rules/daily-operations.md]] §0）。

**2026-06-16 スコープ分割**：本スキルは **朝 briefing 専用**。日中の on-demand source 集約は [[.claude/skills/aggregate-slack/SKILL.md]] / [[.claude/skills/aggregate-mtgs/SKILL.md]] / [[.claude/skills/aggregate-code/SKILL.md]] / [[.claude/skills/aggregate-clippings/SKILL.md]] / [[.claude/skills/aggregate-chat-logs/SKILL.md]] が分担。EOD distill（Daily → Main DB）は独立スキル [[.claude/skills/eod-distill/SKILL.md]] が担当。

> **境界**：Hermes の書き込みは `Inbox/` 内に閉じる。root `Daily/` を書くのはこの skill（Claude Code）＋ユーザー＝single-writer。ToDo の正本は **Google Tasks**（[[.claude/rules/agent-boundaries.md]]）。Daily へは**写すだけ**で、競合するタスクリストを Vault に作らない。

## 使用場面

- 朝の起動：`Run daily briefing` / `今日のbriefingを作って`
- 同日に再実行：既存ファイルは保護し、朝セクション（`## 🌅 朝のbriefing`）のみ最新化

## 実行フロー

### Step 1: 当日 Daily ノートを準備

1. `date` で当日（`YYYY-MM-DD`）を取得（推測しない）
2. `Daily/{YYYY-MM-DD}.md` の存在を確認
3. なければ `Templates/daily-note.md` をベースに作成。あれば朝セクションのみ更新（夜セクションは触らない）

### Step 2: 入力源を取得 = `Inbox/{date}/daily/daily.md` を読むだけ

**2026-06-16 アーキ修正**：外部接続は **hermes が一手に引き受ける**原則（[[.claude/rules/agent-boundaries.md]] §6）。Claude 側で直接 ics fetch / Calendar MCP を叩かない。**Calendar・Tasks 共に `Inbox/{date}/daily/daily.md` の単一ソースから読む**。生成は hermes 側 [[.hermes/skills/mymemory/inbox-daily-capture/SKILL.md]] の責務（Private + Research を ics 経由＋secondary を gsk 経由＋Tasks を list_tasks.py 経由で統合）。

```bash
# 既に hermes が capture 済みかチェック
ls "Inbox/${TODAY}/daily/daily.md"
```

- 既存 → そのまま読み、朝 briefing の各セクションに反映（Step 3）。
- 未取得 → ジョブリストの「Calendar + Tasks」を the user に走らせてもらう（または Claude が hermes-query 経由で on-demand 起動）。daily-briefing 自身は外部接続しない。

**フォールバック / 取得不可時**：

- `Inbox/{date}/daily/daily.md` が無い場合は該当セクションに `<!-- inbox-daily-capture pending: ジョブリストから取り込みを指示してください -->` を残してスキップ（briefing 全体は止めない）。
- Tasks 個別欠落（OAuth scope 不足等）は `inbox-daily-capture` 側が `<!-- google-tasks unavailable: ... -->` を埋めるので、そのまま転写するだけ。

### Step 3: 朝briefing を構成

`## 🌅 朝のbriefing` 配下に以下を埋める（セクションが無ければ作成）：

**予定**（`### 📅 今日の予定` / `### 📅 明日の予定`）：

```markdown
- HH:MM-HH:MM **{summary}** ({attendees の人数}名)
  - 参加者: {attendees の名前を , 区切り}
```

終日イベントは `終日 **{summary}**`。

**タスク**（`### ✅ 今日のタスク（Google Tasks）`）：Google Tasks の未完了をチェックボックスで列挙（**読み取りのみ・写し**）：

```markdown
- [ ] {タスク名}{ 期日があれば （〜MM-DD）}
```

**Genspark 議事録（join 取捨選択リマインダ）**（`### 🎙️ Genspark 議事録`）：今日の予定のうち **会議URL付き（= Genspark bot が join し得る）** のものを一覧し、「どれを文字起こしさせるかは **Genspark Web UI で取捨選択**」のリマインダを添える。**CLI では join を切り替えられない**ため、ここが人手の確認ポイント（[[.hermes/skills/mymemory/genspark-slide/SKILL.md]] §1A 参照）。取り込み自体は the user が `## 🤖 ジョブリスト` の「Genspark 議事録」を指示したときに [[.hermes/skills/mymemory/genspark-mtg/SKILL.md]] を on-demand 実行する（cron は廃止）。**ここで `gsk` 取得はしない**（Step 2 で得た予定データだけで一覧する）。

```markdown
- HH:MM-HH:MM **{summary}**（会議URL: あり / なし）
```

> 会議URL（Zoom / Meet / Teams 等）が無い予定は bot が参加できないので候補から外してよい。join 対象の絞り込みは Genspark Web UI / アカウント設定で行う。

**MTG 準備への接続（議事録叩き台）**：この会議一覧を使って、準備したい MTG があれば [[.claude/skills/mtg-prep/SKILL.md]] を案内する（ユーザーが望めば起動）。mtg-prep が ① Genspark bot 準備ガイド（Web UI トグル・CLI 不可）② 対応フォルダ `meetings/` への議事録叩き台作成（目的・アジェンダ・参加者・事前資料をユーザーにヒアリング）③ Daily へのリンク を担う。**briefing 自身は叩き台を作らず案内のみ**（叩き台作成はヒアリングを伴う対話なので mtg-prep 側で実施）。

### Step 4: Today's Focus を確認

予定・タスク・Work 進行中項目を踏まえ、ユーザに `Today's Focus`（3項目程度）の入力を促す。未入力なら空チェックボックスのまま残す。

### Step 4.5: 🤖 ジョブリストを動的更新（on-demand 状態反映）

`## 🤖 ジョブリスト（on-demand）` セクションのチェック状態を `Inbox/{date}/{source}/` の中身から判定して機械更新する（template の固定文を維持しつつ checkbox とサフィックスだけ書き換える）。これにより the user は朝の段階で「何が取得済／未取得か」を一目で確認できる。

**判定ロジック**（capture 系のみ・aggregate/check 系は固定）：

| ジョブ | 取得済判定 | 表記サフィックス |
|---|---|---|
| `inbox-daily-capture` | `Inbox/{date}/daily/daily.md` が存在 | ` ✅ 取得済（{HH:MM} mtime）` |
| `slack-capture` | `Inbox/{date}/slack/` に 1 件以上 `.md` | ` ✅ 取得済（{N} channels）` |
| `github-eod-capture` | `Inbox/{date}/code/code.md` が存在 | ` ✅ 取得済（{HH:MM} mtime）` |
| `genspark-mtg` | `Inbox/{date}/mtgs/` に 1 件以上 `.md` | ` ✅ 取得済（{N} 件）` |
| `clippings-capture`（拡張経由） | `Inbox/{date}/clippings/` に 1 件以上、または `Inbox/{date}/chat-logs/` に 1 件以上 | ` ✅ 着地済（clippings/{N1}・chat-logs/{N2}）` |

存在しなければ `[ ]` のまま、未取得サフィックスは付けない（簡潔さ優先）。Aggregate / Check 系は実行時刻だけサフィックスしてもよい（任意・実装ヒント）。

**書き換え範囲**：行頭が `- [ ]` または `- [x]` でジョブ名（太字）を含む行のみ。コメント・見出し・他テキストは触らない。

### Step 5: Inbox/{date}/daily の後始末

`Inbox/{YYYY-MM-DD}/daily/daily.md` を取り込んだら、その旨を Daily に反映した状態にする（raw は夜の distill 工程まで Inbox に残してよい）。重複取り込みはしない。

### Step 6（旧夜モード）: 廃止 → `eod-distill` skill へ分離

> **2026-06-16 分割**：旧 Step 6（EOD 集約＋配分）は本スキルから外し、独立スキル [[.claude/skills/eod-distill/SKILL.md]] に移管した。本スキルは朝 briefing 専用となり、夜の Daily → Main DB 蒸留・配分は `eod-distill` を呼ぶ。

EOD 時に Daily → Main DB 蒸留を行いたいとき：

```
EOD distill / 今日の振り返り / Main DB に蒸留
```

→ [[.claude/skills/eod-distill/SKILL.md]] を invoke。aggregate-* も `eod-distill` も独立 skill であり、daily-briefing からは独立して並列・順次に走らせる設計。

## frontmatter

[[.claude/rules/vault-metadata.md]] の Daily スキーマ準拠：

```yaml
---
title: "{YYYY-MM-DD} デイリー"
type: "log"
status: "in-progress"
projects: []   # その日関わる案件コード（PROJ_A/PROJ_B）を入れる
tags: []
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
---
```

## 注意

- Gmail 取り込みは **初期版では行わない**。明示指示があった場合のみ追加取得
- Google Tasks は**読み取りのみ**（正本は Google Tasks）。Daily で新規タスクを起票しない
- 既存ファイルがある場合、夜セクション（`## 🌙 夜の振り返り`）には絶対触らない

## 他 skill との連携

- 月曜朝の実行時は、まず [[.claude/skills/weekly-review/SKILL.md]] を提案
- 今日参加する MTG があれば [[.claude/skills/mtg-prep/SKILL.md]] を案内（議事録の叩き台作成＋Genspark bot 準備ガイド＋Daily リンク。目的等はヒアリング）
- Work 進行中タスクがあれば [[.claude/skills/work-project-writer/SKILL.md]] で `Work/{XXX}/logs/{YYYY-MM-DD}.md` 作成を案内
- 夜/EOD の distill（Daily + Inbox → evergreen）は [[.claude/rules/daily-operations.md]] の集約フローに従う

## 関連ルール

- [[.claude/rules/daily-operations.md]]
- [[.claude/rules/agent-boundaries.md]]
- [[.claude/rules/vault-metadata.md]]
- [[.claude/rules/language.md]]
- [[Inbox/README.md]]
- [[Templates/daily-note.md]]
