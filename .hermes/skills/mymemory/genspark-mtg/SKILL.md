---
name: genspark-mtg
description: Use to capture Genspark AI meeting transcripts into the vault. Hermes lists recent meetings via `gsk meeting list`, keeps only COMPLETED ones inside a short recency window (today + yesterday JST), fetches each full transcript via `gsk meeting get`, and writes RAW transcript markdown to `Inbox/{YYYY-MM-DD}/mtgs/genspark-{slug}.md` without any summarization, body edits, or destination judgment. Always lands in Inbox; allocation to Work/Others/Research meetings/ etc. is done later by Claude Code + user (curate). Idempotency is filename-only — no sidecar state file, so frequent polling is safe. Intended to be invoked on-demand when the user issues a 取り込み instruction (typically from the Daily-note ジョブリスト). May also run from a cron if registered (daytime polling + evening safety-net), but on-demand is the primary mode. Single-meeting fetch via `--task_id` is handled by the same skill (Claude invokes it via `hermes chat -q`).
version: 3.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vault, capture, genspark, meeting, cron, mymemory]
    related_skills: [obsidian]
---

# genspark-mtg

your-vault の **Genspark 議事録 capture 係**（Hermes 側）。the user が指示したタイミングで実行（既定）／日中 polling・夕方 safety-net の recurring cron で時間起動も可（任意）。
MTG 終了＆Genspark 側の整理が済んだ会議を**できるだけ早く**取得して、
**1 会議 = 1 ファイル**で **`Inbox/{YYYY-MM-DD}/mtgs/`**（日付つき親フォルダ配下）に書き出す。

対象は **直近窓（today + yesterday・JST）の `COMPLETED` 会議**に絞る。
**join 可否（＝文字起こし対象の選択）は Genspark Web UI 側で完結**しており（CLI からは切り替え不可・後述）、
**参加した会議だけが `gsk meeting list` に出る**。本 skill は出てきたものを取り込むだけで、
「どれを文字起こすか」「どこへ置くか」の判定はしない（＝「全部は文字起こさない」は Web UI の join 選択で自動的に満たされる）。

> **on-demand での 2 モード**：本 skill は (a) **直近窓（today + yesterday）の一括取り込み**（既定）と (b) **`--task_id` での単一会議手動取得** の両方を担う。どちらも Claude が hermes-query 経由で kick する。

> **役割境界（重要）**：このスキルは **`Inbox/{YYYY-MM-DD}/mtgs/` にのみ書き込む**。
> `Work/` / `Daily/` / `Research/` / `Templates/` / `Archive/` / 既存 curated ノート本文は触らない（single-writer）。
>
> **no-LLM-judgment**：本 skill は [[.claude/rules/inbox-routing.md]] §7 の
> no-LLM-judgment 原則に完全準拠する。宛先は固定（`Inbox/{YYYY-MM-DD}/mtgs/`）であり、判定そのものが存在しない
> （「宛先判定のみ LLM judgment 可」のような例外も設けない）。
> meetings/ への割り振りは **Step 6（夜の振り返り）等で Claude Code + ユーザーが curate** する。
> 本文の要約・タグ推論・話者整形・編集も従来どおり全面禁止。transcript は必ず取得・保存し、
> Genspark 側から `summary` / `user_notes` が返る場合のみ、その raw summary/notes も保存する
> （Hermes 生成 summary で代替しない）。
>
> **Self-edit boundary**：**自己領域でも** `.hermes/skills/mymemory/genspark-mtg/SKILL.md` / `references/` / `config` を autonomous に編集してはならない。Hermes 自身の運用学習や仕様改訂提案も `Inbox/{YYYY-MM-DD}/clippings/hermes-obs-genspark-mtg.md` に observation/proposal note を作成する（必須 frontmatter は cross-territory と同じ、`source: "hermes:observation:genspark-mtg:<ISO8601>"`）。データ／学習 file 追記は例外（このスキルでは該当なし、`sidecar state file は持たない`方針）。詳細は [[.claude/rules/inbox-routing.md]] §7。
>
> **single-writer / 冪等性**：宛先に **同名ファイルがあれば skip**（上書きしない）。
> 既存ファイルは the user / Claude Code が curate した可能性があるため、Hermes は再書き込みしない。
> sidecar state file（`.hermes/state/genspark-captured.json` 等）は持たない方針。
> **polling 安全性**：冪等性が filename ベースなので、30 分ごとの polling で同じ会議を何度なめても既存は skip され、
> 二重取得・上書きは起きない（durable cursor 不要）。
> 設計の正本：このファイル。

## 前提・パス解決

- 実行日 / ファイル名の日付は **Asia/Tokyo** 基準（`TZ=Asia/Tokyo date +%Y-%m-%d`）。
- vault ルート解決順：
  1. `OBSIDIAN_VAULT_PATH`
  2. 未設定なら `HERMES_HOME` から親へ遡り、`CLAUDE.md` + `.obsidian*` + `Inbox/` を持つディレクトリを vault と認定。見つからなければ停止。
- `gsk` は PATH 上にある前提（CLI 仕様は [[.hermes/skills/mymemory/genspark-slide/SKILL.md]]）。
- Python を使う場合は `uv` を使う（`pip` 直接実行は禁止）。
- Windows / WSL どちらでも forward slash 表記で OK。
- **Windows cron / Git Bash pitfall**: Python `subprocess.run(["gsk", ...])` may not resolve the shell shim, and invoking the POSIX `gsk` shim via `bash -lc` from a non-ASCII vault path can fail before reaching the Node CLI. In Windows-hosted Hermes cron, prefer the Windows command shim when scripting: `C:/Users/<your-user>/AppData/Local/hermes/node/gsk.cmd meeting ...` (or a discovered `gsk.cmd` from PATH), while keeping output parsing unchanged. Also tolerate leading log lines such as `[INFO] Calling /meeting...` by scanning for the first valid JSON object, not the first `[` character.

## GSK の予定取得と会議録取得の切り分け

ユーザーが「Genspark AI Meeting Notes の今後の予定」「会議予定」を求めた場合、`gsk meeting list/search/get` ではなく calendar 統合を使う。

```bash
gsk calendar accounts
gsk calendar list --time_min "YYYY-MM-DDT00:00:00+09:00" --time_max "YYYY-MM-DDT23:59:59+09:00" -a "<calendar-account-email>"
```

- `gsk meeting list/search/get` は作成済み meeting note / transcript 取得用。
- `gsk calendar list` / `gsk google_calendar list` は今後の予定取得用。
- 詳細と確認済みコマンドは `references/gsk-calendar-schedules.md` を参照。

## 手順

### 1. 取得対象列挙（gsk meeting list）

```bash
gsk meeting list --output json --page_size 50
```

- **直近 50 件を毎回なめる**方式（durable cursor は持たない）。polling でも evening でも同じ。
- そこから **取得対象＝「直近窓（today + yesterday・JST）の `COMPLETED` 会議」** に絞る：
  - `status` が `COMPLETED` 以外（処理中・失敗等）→ skip（次回 poll で再評価される）
  - 会議日が直近窓より古い → skip（その日のうちに取得済みのはず。filename 冪等性でも二重取得は防がれる）
  - 直近窓に残った会議だけ §2 で本体取得する
- **窓を 2 日（today + yesterday）にする理由**：当日夜遅くに Genspark の処理が完了した会議を、翌日の最初の poll で取りこぼさず拾うため（filename 冪等性があるので重複は出ない）。1 日に締めたい場合は窓を today のみへ。
- 返却 JSON の各要素から最低限取り出す：
  - `task_id` — 一意 ID（idempotency と source URI の元）
  - `title` — 会議タイトル（slug の元）
  - `created_at` または会議日相当 — 保存ファイル名の日付・窓判定に使う
  - `status` — 上記フィルタに使う
- list が空／窓内に `COMPLETED` が無い → 何も書かずに正常終了。

### 2. 各 meeting の本体取得（gsk meeting get）

```bash
gsk meeting get --task_id "<task_id>" --detail_level full --output json
```

- 取得：
  - `task_id`
  - `title`
  - `created_at`（または会議メタデータ日時）
  - `participants`（名前配列。取れない場合は空）
  - `transcription_text` / `transcript`（raw markdown / text）— **常に取得・保存する**
  - `summary`（Genspark 側の summary。返る場合のみ保存。`null` なら生成しない）
  - `user_notes`（Genspark 側の notes。返る場合のみ保存。`null` なら生成しない）
- `transcription_text` / `transcript` が空 / 取得失敗 → その meeting を skip し、完了報告に理由を残す（処理は続行）。
- 会議日が取れない → 実行日の JST を fallback、完了報告に明記。

### 3. 保存先解決

宛先は**固定**：`Inbox/{YYYY-MM-DD}/mtgs/genspark-{slug}.md`（日付つき親フォルダが日付を持ち、ファイル名に日付 prefix は付けない）。判定は行わない。

- **日付**：会議メタデータを Asia/Tokyo に正規化して `YYYY-MM-DD`（＝親フォルダ名）。
- **slug**（meeting title から生成）：
  1. 元タイトルを取る
  2. 先頭の `[PROJ_A]` / `[PROJ_B]` / `[PROJ_X]` 等の角括弧 prefix は**取り除かない**（後段 curate の割り振りヒントとして filename に残す。slug 化で `proj-a-` 等の先頭要素になる）
  3. 小文字化
  4. 空白・記号（`[]()/\|:;,.!?@#$%^&*+={}<>~`等）を `-` に置換
  5. 連続 `-` を 1 個に畳む
  6. 先頭末尾の `-` を落とす
  7. 50 文字超なら 50 で切る
  8. 空になったら `meeting-{task_id_short}`（`task_id` 先頭 8 文字）

### 4. 冪等性

- 宛先に同名ファイルが存在 → **skip**（既存ファイルを開かない、本文比較しない、上書きしない）。
- sidecar state file は持たない。
- `source: genspark:meeting:<task_id>` の全体 grep もしない。
- 同 run 内で別 meeting が同じ宛先 filename に衝突 → 先に書けた 1 件のみ残し、後続は skip + 完了報告に記録。

### 5. 書き出し

frontmatter + 本文 = Genspark から取得できた raw summary/user_notes（任意） + raw transcript（必須）。
Hermes は summary を生成しない。Genspark 側の `summary` / `user_notes` が `null` の場合は transcript のみ保存する。

#### Frontmatter テンプレート

宛先は Inbox なので **Inbox-source 拡張**（[[.claude/rules/vault-metadata.md]] "Inbox-source 拡張" セクション）に固定：

```yaml
---
title: "{meeting_title}"
type: "capture"
status: "inbox"
tags: ["meeting", "genspark"]
created: {capture_date_jst}
updated: {capture_date_jst}
source: "genspark:meeting:{task_id}"
genspark_task_id: "{task_id}"
meeting_title: "{meeting_title}"
meeting_date: {meeting_date_jst}
participants: [{participant1}, {participant2}, ...]
transcript_length: {character_count_of_raw_transcript}
genspark_summary_present: {true|false}
genspark_user_notes_present: {true|false}
---
```

- `project` / `client` / project tag は**付けない**（curate 時に Claude + ユーザーが `Work/{X}/meetings/` へ移す際、標準 enum への書き換えと同時に付与する）。
- `created` / `updated` は **capture 実行日**。`meeting_date` は **会議日**（別物）。
- `participants` は表示名の配列。空なら `[]`。

#### 本文

frontmatter の後ろは以下の順序で書く。

1. `summary` が non-empty の場合のみ、Genspark 由来であることが分かる見出しを付けて raw summary を貼る。
2. `user_notes` が non-empty の場合のみ、Genspark 由来であることが分かる見出しを付けて raw user_notes を貼る。
3. **必ず** Genspark から取得した raw transcript markdown/text をそのまま貼る。

Hermes による要約・整形・タグ推論は一切行わない。`summary` / `user_notes` が `null` の場合、transcript から要約を作って補完しない。

### 6. 完了報告

run の最後に短い実行結果を返す（stdout）。

含める内容：
- `processed`: list 件数
- `written`: 新規作成件数
- `skipped_existing`: 既存 filename で skip
- `skipped_out_of_window`: 直近窓（today + yesterday）より古くて skip
- `skipped_empty`: transcript 欠落で skip
- `skipped_status`: `COMPLETED` 以外で skip
- `failed`: 取得 / parse 失敗
- 書き込んだパス一覧

meeting 単位の失敗は集計して続行（partial success OK）。
ただし `vault` 解決失敗 / `gsk meeting list` 失敗 → **run 全体を失敗扱い**で停止。

## あとからの割り振り（curate — Hermes の仕事ではない）

`Inbox/{YYYY-MM-DD}/mtgs/` は未割り振りキュー。Step 6（夜の振り返り）や随時の curate で、
Claude Code + ユーザーが内容を見て `Daily/{YYYY-MM-DD}.md` に集約しつつ `Work/{XXX}/meetings/{YYYY-MM-DD}-{slug}.md` 等へ移動し、
その際に frontmatter を標準 enum（`type: note` / `status: draft` / `project` / `client` / project tag）へ書き換える
（[[.claude/rules/vault-metadata.md]] 移行ルール）。

## 起動方法（on-demand 既定 / cron は任意）

**既定 = on-demand**：ユーザーが Daily ノートの `## 🤖 ジョブリスト` を見て「<該当 job> やって」と Claude に指示 → Claude が hermes に CLI で委譲（[[.claude/skills/hermes-query/SKILL.md]]）。filename 冪等性があるので何度走っても二重取得しない。

### 手動 invoke コマンド

> `hermes chat -q` のスキル指定は `-s <skill>`（`--skill` / `--workdir` というフラグは無い）。vault ルートに cd してから呼ぶ。日本語 Windows では呼び出し前に `PYTHONUTF8=1` を設定する（cp932 デコード起因の出力欠落防止 → [[.claude/skills/hermes-query/SKILL.md]]）。

```bash
cd "<vault root>"
hermes chat -q "Load genspark-mtg and run it for the vault. List recent meetings via gsk meeting list, keep only COMPLETED ones whose meeting date is today or yesterday (JST), fetch each full transcript via gsk meeting get, and write each as RAW transcript markdown to Inbox/{YYYY-MM-DD}/mtgs/genspark-{slug}.md (dated parent folder owns the date; no date prefix in the filename). Skip existing filenames (idempotent). No destination judgment, no writes outside Inbox/{date}/mtgs/, no summarization or body edits. Report counts." -s genspark-mtg -Q --source claude-code
```

- 手動・任意タイミングの「**この会議だけ**」取得は本 skill に `--task_id <ID>` を渡して同じく hermes 経由で kick する。本 skill は直近窓の一括取り込みと task_id 指定単一取得の両方を担う。

### Cron 登録（任意）

> cron による定期起動は**任意**（on-demand が既定）。定時運用したい場合の典型は「日中 polling + 夕方 safety-net」の 2 本立て。

**任意で 2 本立てに登録できる**。どちらも同じ skill・同じ today-window catch-up 挙動で、違いは発火頻度と意図だけ。

| cron | schedule（JST） | 役割 |
|---|---|---|
| `genspark-capture-poll` | `*/30 9-20 * * *`（09:00〜20:30 を 30 分間隔） | **near-real-time**。MTG 終了＆Genspark 整理後、最大 30 分で取り込む |
| `genspark-capture-evening` | `0 21 * * *`（21:00） | **safety-net**。今日分の取りこぼしが無いか最終確認。夜の EOD distill の前に `Inbox/{YYYY-MM-DD}/mtgs/` を埋め終える |

**注意：positional `prompt` 引数は schedule の直後に置く必要がある**（`hermes cron create` の argparse 仕様で flag より前に置かないと「unrecognized arguments」エラー）。

```bash
# near-real-time polling（日中 30 分間隔）
hermes cron create "*/30 9-20 * * *" "Load genspark-mtg and run it for the vault. List recent meetings via gsk meeting list, keep only COMPLETED ones whose meeting date is today or yesterday (JST), fetch each full transcript via gsk meeting get, and write each as RAW transcript markdown to Inbox/{YYYY-MM-DD}/mtgs/genspark-{slug}.md (dated parent folder owns the date; no date prefix in the filename). Skip existing filenames (idempotent). No destination judgment, no writes outside Inbox/{date}/mtgs/, no summarization or body edits. Report counts." --name genspark-capture-poll --skill genspark-mtg --workdir "<vault root>"

# evening safety-net（今日分の取りこぼし最終確認）
hermes cron create "0 21 * * *" "Load genspark-mtg and run it for the vault as the evening safety-net: check whether any of today's COMPLETED Genspark meetings are still missing from Inbox/{YYYY-MM-DD}/mtgs/ and capture them. Same behavior as the daytime poll (today+yesterday JST window, RAW transcript only, skip existing filenames, no judgment/summarization). Report counts." --name genspark-capture-evening --skill genspark-mtg --workdir "<vault root>"
```

- **実行機の制約**：cron の**自動発火**には「`gsk` 導入＋認証済み **かつ** hermes **gateway** 常駐」の機が必要（登録自体は gateway 停止中でも通るが、発火しない＝`hermes cron status` が警告）。運用上は **gateway を置くメイン機に登録**する。`gsk` はあっても gateway を持たない機（＝ on-demand 専用機）には**登録しない**。そちらでの逐次取得は本 skill に `--task_id` を渡して on-demand 実行する（hermes-query 経由）。
- **頻度は調整可**：`できるだけすぐ` を強めたいなら `*/20` や `*/15` に。invocation を減らすなら `0,30` のまま hour 範囲を狭める。
- timezone は `.hermes/config.yaml` の `timezone` を使う（global 設定）。

## 関連

- [[.claude/rules/inbox-routing.md]] — Inbox 経路の正本（本 skill は §7 に完全準拠）
- [[.claude/rules/agent-boundaries.md]] — 3 エージェント分担・single-writer 原則
- [[.claude/rules/vault-metadata.md]] — frontmatter schema 単一の正（Inbox-source 拡張・移行ルール）
- [[.claude/rules/vault-tagging.md]] — tag 体系（`genspark` vendor tag は本 skill で初登場）
- [[.claude/rules/work-management.md]] — 割り振り先 `Work/{XXX}/meetings/` の標準命名
- [[.claude/rules/language.md]] — 言語規約
- [[.hermes/skills/mymemory/genspark-slide/SKILL.md]] — `gsk` CLI リファレンス
- [[.hermes/skills/mymemory/slack-capture/SKILL.md]] — capture skill の structural 参照
- [[Inbox/README.md]]
