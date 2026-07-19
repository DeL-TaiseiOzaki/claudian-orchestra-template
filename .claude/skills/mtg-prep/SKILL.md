---
name: mtg-prep
description: Pre-meeting preparation. Before a meeting, (1) list today's calendar events via hermes (gsk calendar list) and let the user pick which to prep (multiple), (2) guide enabling the Genspark notetaker bot in the Genspark Web UI — gsk CLI has NO bot-join toggle (verified 2026-06-18), so join selection is Web-UI-only, (3) interview the user for each meeting's 目的 / アジェンダ・論点 / 参加者 / 事前資料・関連リンク, (4) create a meeting-note stub (議事録の叩き台) at Wiki/meetings/{YYYY-MM-DD}-{topic}.md with status:draft, and (5) link it from today's root Daily note. The stub is the reconciliation target for the post-meeting Genspark transcript (aggregate-mtgs / eod-distill fill INTO it, not duplicate). Surfaced by the morning daily-briefing, which lists today's meetings and prompts this skill. Use when the user says MTG準備 / 会議の準備 / 議事録の叩き台を作って before meetings.
---

# mtg-prep — MTG 準備（議事録の叩き台 + bot ガイド + Daily リンク）

## 目的

**会議の前**に、その日の予定を踏まえて以下を一気にやる：

1. **今日の予定を一覧**して、準備する MTG を選ぶ（複数可）
2. **Genspark notetaker bot の準備をガイド**（どの会議に bot を入れるか → Web UI で取捨選択）
3. 各 MTG について**ユーザーにヒアリング**（目的・アジェンダ・参加者・事前資料）
4. `Wiki/meetings/` に**議事録の叩き台**（`status: draft`）を作成
5. その日の **Daily ノートからリンク**する

> **pipeline 上の位置づけ**：これは **MTG 前の prep**。MTG 後の流れ（[[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]] capture → [[.claude/skills/aggregate-mtgs/SKILL.md]] 集約 → [[.claude/skills/eod-distill/SKILL.md]] 配分）と**対**になる。本 skill が作る叩き台が、後から流れてくる Genspark 議事録の**統合先（reconciliation target）**になる（§6）。朝の [[.claude/skills/daily-briefing/SKILL.md]] が今日の MTG を一覧する際に本 skill を案内・起動する（[[.claude/rules/daily-operations.md]] §0 Step 2 / §1）。

## 境界（守ること）

- **外部接続は hermes 一元**（[[.claude/rules/agent-boundaries.md]] §6）。今日の予定取得（`gsk calendar list`）は Claude が直接叩かず **[[.claude/skills/hermes-query/SKILL.md]] 経由**で hermes に委譲する。
- **bot の join 切替は CLI 不可（2026-06-18 実機 help で確認）**。`gsk meeting` は `list/search/get`（会議**後**の取得）のみ、`gsk calendar` / `gsk google_calendar` にも notetaker bot を会議に入れるトグルは無い。**「どの会議に bot を入れるか」は Genspark Web UI 専用**（スクショの「会議に参加」ボタン）。本 skill は**一覧＋ガイド**に徹し、トグルは人手（§2）。詳細は §7。
- **書き込み先は curated（`Wiki/` `Daily/`）**＝ Claude + ユーザー所有（single-writer）。Inbox には書かない。
- **承認前提**：叩き台の作成・Daily への追記の前に、対象・フォルダ・内容を提示して合意を取る。

## 実行フロー

### Step 1: 当日確定 ＋ 今日の予定を一覧

1. `TZ=Asia/Tokyo date +%Y-%m-%d` で当日 `{date}` を取得（推測しない）。
2. **今日の予定を hermes 経由で取得**（[[.claude/skills/hermes-query/SKILL.md]]）。PowerShell ツールで：

```powershell
$env:PYTHONUTF8 = '1'
Set-Location "<vault root>"
hermes chat -q "List today's calendar events via gsk. First run `gsk calendar accounts` to find the account, then `gsk calendar list --time_min '{date}T00:00:00+09:00' --time_max '{date}T23:59:59+09:00' -a '<account-email>'`. For each event return summary / start / end / attendees / conferenceUrl as a compact JSON array on stdout. Do not write any files." -Q --source claude-code
```

- `conferenceUrl`（Zoom / Meet / Teams 等）の有無 = **bot が join し得るか**の判定材料。
- **フォールバック**：hermes / gsk が使えない時は、ユーザーに Genspark の「今後の予定」画面の内容を貼ってもらう／会話で会議名を挙げてもらう。スキルは予定取得が出来なくても Step 3 以降（叩き台作成）は進められる。

3. 取得した予定を一覧で提示し、**準備する MTG をユーザーに選んでもらう**（複数可・「対象範囲＝一覧から選択」確定方針）。

```markdown
今日の予定（{date}）:
1. 13:00-13:30 【External】Client D (livestock)お打ち合わせ（会議URL: あり）
2. 14:00-15:00 partner Xラップアップ（会議URL: あり）
3. 14:30-15:30 [RL WG] 定例MTG（会議URL: あり）
4. 15:00- Physical AI関連相談（会議URL: なし）
→ どれを準備しますか？（番号で複数可）
```

### Step 2: Genspark bot 準備（Web UI ガイド）

選ばれた MTG のうち **会議URL付き**のものを「bot を入れる候補」として提示し、**Genspark Web UI で join を入れる**ようガイドする（**CLI ではトグル不可**）：

```markdown
🎙️ Genspark bot 準備（Web UI で操作してください）:
- [ ] partner Xラップアップ → Genspark「AIミーティングノート > 今後の予定」で「会議に参加」を ON
- [ ] [RL WG] 定例MTG → 同上
（会議URLなしの「Physical AI関連相談」は bot 参加不可のため対象外）
※ すでに「録画中…」表示のものは join 済み。
```

- 取り込み自体（会議後）は別 job（`genspark-mtg`）。ここでは **join の取捨選択を促すだけ**。
- bot を入れない MTG（手書きメモ運用）でも、叩き台（Step 3〜5）は作ってよい。

### Step 3: 配置先の確認

叩き台の配置先は **`Wiki/meetings/{YYYY-MM-DD}-{topic}.md`** の一択（[[Wiki/AGENTS.md]]）。

- `Wiki/meetings/` が無ければ作成（[[Wiki/AGENTS.md]]）。

### Step 4: ヒアリング（各 MTG・ここがコア）

各 MTG について**ユーザーに聞いて叩き台に反映**する。`AskUserQuestion` か会話で、以下を尋ねる（**「目的」は必須**、他は分かる範囲で）：

| 項目 | 反映先（叩き台） |
|---|---|
| **目的・ゴール**（必須） | 冒頭テーブルの「目的」＋ `## 🎯 目的・ゴール` |
| アジェンダ・論点 | `## 🗣️ アジェンダ・論点` |
| 参加者 | 冒頭テーブルの「参加者」（[[Maps/People-Map.md]] で canonical 表記に名寄せ） |
| 事前資料・関連リンク | `## 🔗 事前資料・関連` に wikilink / URL |

- 既に分かっている情報（予定の attendees 等）は埋めて提示し、差分だけ聞くと速い。
- 不明な人名は raw のまま残し `?` 注記（名寄せは後工程でも再実施）。

### Step 5: 叩き台（議事録ノート）を作成

`Wiki/meetings/{YYYY-MM-DD}-{topic}.md` を作成。`{topic}` は短い読みやすいトピック（日本語可。例 `public broadcaster partnerラップアップ`）。既存同名があれば**上書きせず**ユーザーに確認。

**frontmatter** — [[.claude/rules/vault-metadata.md]] 準拠。**pre-meeting なので `status: draft`**（会議後の確定で `completed` 等へ）。活動タグを使う：

```yaml
---
title: "[{活動名}] {topic}"
type: "note"
status: "draft"
tags: ["{activity-tag}", "meeting", "activity"]
created: {date}
updated: {date}
meeting_date: {date}
participants: [{...}]
meeting_title: "{元のカレンダータイトル}"   # ← 会議後の transcript と突合する match key（§6）
---
```

**本文**（[[Templates/meeting-note.md]] をベースに prep 用へ）。**埋めるのは目的・アジェンダ・参加者・事前資料まで**。決定事項・ToDo・メモは会議中/後に埋める空欄で残す：

```markdown
# {date} {topic}

> 🗓️ **MTG 準備の叩き台**（mtg-prep で生成）。会議後に Genspark 議事録が入ったら本ノートへ統合する（§reconciliation）。

| 項目 | 内容 |
|------|------|
| 日時 | {date} HH:MM |
| 参加者 | {...} |
| 目的 | {1 行サマリ} |

## 🎯 目的・ゴール
- {ヒアリング結果}

## 🗣️ アジェンダ・論点
- {ヒアリング結果}

## ✅ 決定事項
<!-- 会議中/後に記入 -->
-

## 📋 ToDo / ネクストアクション
<!-- 自分の担当は Google Tasks に起票。ここは記録 -->
- [ ] 担当: / 期日:

## 📝 メモ
<!-- 会議中に記入。会議後 Genspark transcript の要点をここへ統合 -->
-

## 🔗 事前資料・関連
- {wikilink / URL}
- [[Daily/{date}.md]]
```

> 関連する `Wiki/` ノートも「関連」に足す。

### Step 6: Daily にリンク（append-only）

`Daily/{date}.md` の `## 📝 ログ` 配下、種別に応じた section に**準備マーカー付きで追記**する：

| 種別 | Daily section |
|---|---|
| コミュニティ / 連絡 | `### 🗒️ ミーティング・連絡メモ` |
| Wiki（研究・活動関連） | `### 📚 Wiki` |

```markdown
- 🗓️ **[準備] {HH:MM} {meeting_title}** → 叩き台 [[{folder}/meetings/{date}-{topic}.md]]（目的: {1 行}）
```

- **idempotent**：既に同じ叩き台への wikilink が Daily にあれば skip（並列セッション対応・[[.claude/skills/session-log/SKILL.md]] と同方式）。
- 既存 bullet・frontmatter・他 section は触らない（append-only）。
- Daily が無ければ [[.claude/skills/daily-briefing/SKILL.md]] での作成を先に促す（本 skill では新規作成しない）。

### Step 7: 報告

- 作成した叩き台パス一覧 / bot 準備ガイドの対象 / Daily へのリンク / フォルダ新設の有無 を 3〜5 行で要約。
- bot の Web UI トグルは**ユーザー手作業が残る**ことを明示（リマインド）。

## 6. MTG 後との接続（reconciliation — 重要）

本 skill の叩き台は、会議後に流れてくる Genspark 議事録の**統合先**。**重複ノートを作らない**ための取り決め：

- **match key**：叩き台 frontmatter の `meeting_title` ＋ `meeting_date` を、Genspark capture（`Inbox/{date}/mtgs/genspark-*.md`）の `meeting_title` ／ `meeting_date` と突合する。
- **期待挙動**：[[.claude/skills/aggregate-mtgs/SKILL.md]]（Daily 集約）と [[.claude/skills/eod-distill/SKILL.md]]（`Wiki/meetings/` への配分）は、`Wiki/meetings/` に**同 `meeting_title`+`meeting_date` の draft 叩き台が既にある場合、新規作成せず既存ノートへ追記・統合**する（決定事項・ToDo・要点 + raw transcript への wikilink を埋め、`status: draft → completed`、`source: genspark:meeting:<task_id>` を追記）。
- **ファイル名は一致しない前提**：叩き台は `{date}-{topic}`（読みやすいトピック）、Genspark slug は `genspark-{aggressive-slug}`。だから**ファイル名ではなく frontmatter の match key で突合**する。

> ⚠️ この reconciliation を完全に効かせるには `aggregate-mtgs` / `eod-distill` 側に「既存 draft 叩き台への統合」分岐を足すのが望ましい（本 skill 単体では叩き台作成までを担保）。未対応の間は、EOD distill 時に手動で叩き台へ統合する。

## 7. 不確実な点・将来の自動化余地

- **bot join の自動化は現状不可（検証済）**：`gsk` v 実機 help（2026-06-18）に notetaker bot を既存予定へ入れる/外すサブコマンドは無い。`gsk meeting` は読み取り（list/search/get）のみ。
- **未検証の余地**：`gsk task meeting_notes`（task type）・`gsk zoom create_meeting --auto_recording`（gsk で新規 Zoom を作る場合のみ）は join 制御とは別物に見えるが完全には未検証。将来 bot 準備を自動化したくなったら、まず `hermes chat -q "gsk task meeting_notes --help"` 等で再調査する（[[.claude/skills/hermes-query/SKILL.md]] 経由）。
- gsk のサブコマンドは更新が速い。挙動が変わったら本節と §2 を更新する。

## 安全策

- **当日取得**：日付は `TZ=Asia/Tokyo date` で取得（推測禁止）。
- **承認前提**：対象選択・フォルダ・叩き台内容・Daily 追記を提示してから適用。
- **single-writer / append-only**：Daily は append のみ、既存は触らない。叩き台の同名上書きは確認必須。
- **外部接続は hermes 経由のみ**（予定取得）。Claude が gsk を直接叩かない。

## 他 skill との連携

- [[.claude/skills/hermes-query/SKILL.md]]（今日の予定取得＝pull）
- [[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]]（会議**後**の transcript capture）
- [[.claude/skills/aggregate-mtgs/SKILL.md]]（会議後の Daily 集約・reconciliation 相手）
- [[.claude/skills/eod-distill/SKILL.md]]（会議後の `Wiki/meetings/` 配分・reconciliation 相手）
- [[.claude/skills/daily-briefing/SKILL.md]]（朝 briefing が今日の MTG を一覧 → 本 skill を案内/起動。Genspark join リマインダと整合）
- [[.claude/skills/wiki-writer/SKILL.md]]（ノート作成の実務規約）

## 関連

- [[.claude/rules/daily-operations.md]]（pipeline 全体・Daily ハブ）
- [[.claude/rules/inbox-routing.md]] §3（mtgs の curate 例外＝要約を `meetings/` へ）
- [[Wiki/AGENTS.md]]（Wiki 規約・meetings/ 命名）
- [[.claude/rules/vault-metadata.md]] / [[.claude/rules/vault-tagging.md]] / [[.claude/rules/language.md]]
- [[Maps/People-Map.md]]（話者名 canonical mapping）
- [[Templates/meeting-note.md]]（叩き台のベース）
