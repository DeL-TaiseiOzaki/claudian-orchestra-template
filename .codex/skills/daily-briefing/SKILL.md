---
name: daily-briefing
description: Create or refresh today's morning Daily briefing from Hermes-staged calendar and task data. Use for 「今日の Daily」 or morning briefing requests.
---

# Daily Briefing Skill

## 目的

朝の起動時に **root の Daily ノート（`Daily/{YYYY-MM-DD}.md`）を構成**する。
**Calendar 予定もタスクも、すべて `Inbox/{YYYY-MM-DD}/daily/daily.md`（hermes が capture 済み）から読む**。外部接続（ics fetch・Calendar/Tasks MCP）は コア側から行わない（[[.codex/rules/agent-boundaries.md]] §6 — 外部接続は hermes に一元集約）。Inbox 未取得時はジョブリストから取り込みを促す（[[.codex/rules/daily-operations.md]] §0）。

本スキルは **朝 briefing 専用**。日中の source 集約は [[.codex/skills/inbox-aggregate/SKILL.md]]、EOD distill は [[.codex/skills/eod-distill/SKILL.md]] が担当する。

> **境界**：Hermes の書き込みは `Inbox/` 内に閉じる。root `Daily/` を書くのはコアエージェント＋ユーザー。ToDo の正本は **Google Tasks**（[[.codex/rules/agent-boundaries.md]]）。Daily へは写すだけで、競合するタスクリストを作らない。

## 使用場面

- 朝の起動：`Run daily briefing` / `今日のbriefingを作って`
- 同日に再実行：既存ファイルは保護し、朝セクション（`## 🌅 朝のbriefing`）のみ最新化

## 実行フロー

### Step 1: 当日 Daily ノートを準備

1. `date` で当日（`YYYY-MM-DD`）を取得（推測しない）
2. `Daily/{YYYY-MM-DD}.md` の存在を確認
3. なければ `Templates/daily-note.md` をベースに作成。あれば朝セクションのみ更新（夜セクションは触らない）
4. **ジョブリストの registry フィルタ**：新規作成時は [[.codex/connections.yaml]] を読み、テンプレのジョブ行のうち `<!-- connection: {key...} -->` 付きの行を **listed キーのいずれかが `status: enabled` のものだけ残す**（キーはスペース区切りで複数可。例 `google-calendar google-tasks`。どれも enabled でない行は削除。コメント自体も出力からは除去してよい）。キーなしの行（朝 briefing / EOD distill / 整合性チェック / バックアップ等）は常に残す。**全接続が `unconfigured`**（セットアップ未実施）の場合はテンプレのまま全行残し、ジョブリスト末尾に `> 💡 使うツールを選ぶには「接続セットアップして」（connection-setup）` を 1 行追加する

### Step 2: 入力源を取得 = `Inbox/{date}/daily/daily.md` を読むだけ

外部接続は **hermes が一手に引き受ける**原則（[[.codex/rules/agent-boundaries.md]] §6）。コア側で直接 ics fetch / Calendar MCP を叩かない。**Calendar・Tasks 共に `Inbox/{date}/daily/daily.md` の単一ソースから読む**。生成は hermes 側 [[.hermes/skills/vault-capture/inbox-daily-capture/SKILL.md]] の責務（Calendar を ics 経由＋追加アカウントを gws 経由＋Tasks を list_tasks.py 経由で統合）。

```bash
# 既に hermes が capture 済みかチェック
ls "Inbox/${TODAY}/daily/daily.md"
```

- 既存 → そのまま読み、朝 briefing の各セクションに反映（Step 3）。
- 未取得 → ジョブリストの「Calendar + Tasks」をユーザーに指示してもらう（またはコアエージェントが hermes-query 経由で on-demand 起動）。daily-briefing 自身は外部接続しない。

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

**会議記録リマインダ**（`### 🎙️ 会議記録`）：今日の予定のうち会議URL付きのものを一覧する。`meeting-notes` 接続が有効なら、接続ガイドに従って録画・notetaker の残作業を人間向けチェックとして添える。特定 provider や自動 join を前提にせず、この skill から外部サービスを操作しない。

```markdown
- HH:MM-HH:MM **{summary}**（会議URL: あり / なし）
```

> 会議URLが無い予定も meeting prep の対象にはできる。記録可否は選択した provider のガイドで判断する。

**MTG 準備への接続**：準備したい会議があれば [[.codex/skills/mtg-prep/SKILL.md]] を案内する。mtg-prep が議事録の叩き台作成と Daily リンクを担い、provider 固有の記録準備は接続済みの場合だけ案内する。

### Step 4: Today's Focus を確認

予定・タスク・進行中項目を踏まえ、ユーザに `Today's Focus`（3項目程度）の入力を促す。未入力なら空チェックボックスのまま残す。

### Step 4.5: 🤖 ジョブリストを動的更新（on-demand 状態反映）

`## 🤖 ジョブリスト（on-demand）` セクションのチェック状態を `Inbox/{date}/{source}/` の中身から判定して機械更新する（template の固定文を維持しつつ checkbox とサフィックスだけ書き換える）。これによりユーザーは朝の段階で「何が取得済／未取得か」を一目で確認できる。

**判定ロジック**（capture 系のみ・aggregate/check 系は固定）：

| ジョブ | 取得済判定 | 表記サフィックス |
|---|---|---|
| `inbox-daily-capture` | `Inbox/{date}/daily/daily.md` が存在 | ` ✅ 取得済（{HH:MM} mtime）` |
| `slack-capture` | `Inbox/{date}/slack/` に 1 件以上 `.md` | ` ✅ 取得済（{N} channels）` |
| `github-eod-capture` | `Inbox/{date}/code/code.md` が存在 | ` ✅ 取得済（{HH:MM} mtime）` |
| `AI 議事録` | `Inbox/{date}/mtgs/` に 1 件以上 `.md` | ` ✅ 取得済（{N} 件）` |
| `clippings-capture`（拡張経由） | `Inbox/{date}/clippings/` に 1 件以上、または `Inbox/{date}/chat-logs/` に 1 件以上 | ` ✅ 着地済（clippings/{N1}・chat-logs/{N2}）` |

存在しなければ `[ ]` のまま、未取得サフィックスは付けない（簡潔さ優先）。Aggregate / Check 系は実行時刻だけサフィックスしてもよい（任意・実装ヒント）。

**書き換え範囲**：行頭が `- [ ]` または `- [x]` でジョブ名（太字）を含む行のみ。コメント・見出し・他テキストは触らない。

### Step 5: Inbox/{date}/daily の後始末

`Inbox/{YYYY-MM-DD}/daily/daily.md` を取り込んだら、その旨を Daily に反映した状態にする（raw は夜の distill 工程まで Inbox に残してよい）。重複取り込みはしない。

### Step 6（旧夜モード）: 廃止 → `eod-distill` skill へ分離

> **2026-06-16 分割**：旧 Step 6（EOD 集約＋配分）は本スキルから外し、独立スキル [[.codex/skills/eod-distill/SKILL.md]] に移管した。本スキルは朝 briefing 専用となり、夜の Daily → Main DB 蒸留・配分は `eod-distill` を呼ぶ。

EOD 時に Daily → Main DB 蒸留を行いたいとき：

```
EOD distill / 今日の振り返り / Main DB に蒸留
```

→ [[.codex/skills/eod-distill/SKILL.md]] を invoke。`inbox-aggregate` と `eod-distill` は daily-briefing から独立している。

## frontmatter

[[.codex/rules/vault-metadata.md]] の Daily スキーマ準拠：

```yaml
---
title: "{YYYY-MM-DD} デイリー"
type: "log"
status: "in-progress"
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

- 月曜朝の実行時は、まず [[.codex/skills/weekly-review/SKILL.md]] を提案
- 今日参加する MTG があれば [[.codex/skills/mtg-prep/SKILL.md]] を案内（provider-neutral な叩き台作成＋Daily リンク）
- 夜/EOD の distill（Daily + Inbox → evergreen）は [[.codex/rules/daily-operations.md]] の集約フローに従う

## 関連ルール

- [[.codex/rules/daily-operations.md]]
- [[.codex/rules/agent-boundaries.md]]
- [[.codex/rules/vault-metadata.md]]
- [[.codex/rules/language.md]]
- [[Inbox/README.md]]
- [[Templates/daily-note.md]]
