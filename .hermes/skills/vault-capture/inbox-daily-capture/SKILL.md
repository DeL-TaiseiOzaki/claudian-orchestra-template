---
name: inbox-daily-capture
description: Use when capturing the day's Google Calendar (today + tomorrow) and Google Tasks into the vault. Writes RAW markdown to Inbox/{YYYY-MM-DD}/daily/daily.md so the Claude Code daily-briefing step can curate it into the root Daily note. Intended to be invoked on-demand when the user issues a 取り込み instruction (typically from the Daily-note ジョブリスト). May also run from a cron if registered, but on-demand is the primary mode.
version: 1.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vault, capture, calendar, google-tasks, cron, vault-capture]
    related_skills: [google-workspace, google-tasks, obsidian]
---

# inbox-daily-capture

vault の **capture 係**(Hermes 側)。ユーザーが指示したタイミングで実行(既定)/cron で時間起動も可(任意)。今日と明日の Google Calendar 予定と
Google Tasks の未完了タスクを取得し、**生のまま** `Inbox/{YYYY-MM-DD}/daily/daily.md` に書き出す。

> **役割境界(重要)**:このスキルは **`Inbox/` 内にのみ書き込む**。root `Daily/` や
> curated(Work / Research / Others)には**絶対に触れない**。整理(curate)と root Daily への
> 集約は Claude Code 側の `daily-briefing` が行う(single-writer 原則)。
> ToDo の正本は **Google Tasks**。ここは読み取りの写しを置くだけで、タスクを起票しない。

## 前提・パス解決

- 当日の日付は実行時に取得(推測しない):`date +%Y-%m-%d`
- vault ルートを解決(この順で):
  1. `OBSIDIAN_VAULT_PATH`(設定されていればそれ)
  2. 無ければカレントディレクトリ、または `HERMES_HOME` の親ディレクトリが vault に見える場合のみ採用(`HERMES_HOME=.../<vault>/.hermes` → vault=`.../<vault>`)。`~/.hermes` の親など vault に見えない場所へは書かない。
- 書き込み先:`{vault}/Inbox/{YYYY-MM-DD}/daily/daily.md`(dated parent folder が日付を持つ。ファイル名は固定 `daily.md`)
- **file tools は環境変数を展開しない**。先にパスを文字列解決してから絶対パスで書く。
- Windows でもパスは forward slash 可(例 `<vault root>/Inbox/2026-06-03/daily/daily.md`)。

## 手順

### 1. 既存チェック(冪等)
- `{vault}/Inbox/{today}/daily/daily.md` が既にあれば**上書きせず終了**(同日多重実行の防止)。
  更新したい場合のみ明示再生成。

### 2. Calendar 取得(ics 直 fetch・OAuth 不要)

Calendar の基本経路は **限定公開 ics URL の直 fetch** に一本化している(OAuth 不要・依存が少なく壊れにくい。hermes-owned HTTP source として [[.claude/rules/agent-boundaries.md]] §1.1 push 表に整合)。

```bash
uv run "${HERMES_HOME:-$HOME/.hermes}/skills/vault-capture/inbox-daily-capture/scripts/fetch_calendar_ics.py" --format md
```

- 設定ファイル `scripts/calendars.local.json`(**`.gitignore` 済み**・限定公開 ics URL を格納)に取得したいカレンダーを列挙する(複数可。書式は [[docs/connections/google-calendar-tasks.md]] 経路 A 参照)。
- 出力フォーマット:`### 📅 今日の予定` / `### 📅 明日の予定` の md(そのまま Step 4 に流せる)。構造化が要れば `--format json`、別日基準は `--date YYYY-MM-DD`。
- 繰り返し予定 (RRULE) 展開・ローカルタイムゾーン変換・複数カレンダー横断 dedup 済み。OAuth 不要(ics URL に token 内包)。
- **失敗時**(ネット不通・config 不在等):`<!-- ics calendar unavailable: {message} -->` を残してスキップ。**briefing 全体は止めない**。

### 2.5. 追加アカウントの Calendar 取得(任意・gws CLI)

組織の Google Workspace など **ics の限定公開 URL を出せないアカウント**が別にある場合のみ、`gws`(Google Workspace CLI)の**アカウント別 config dir** で追加取得する。1 アカウント = 1 config dir(例:既定 `~/.config/gws` = 個人、追加分は `GOOGLE_WORKSPACE_CLI_CONFIG_DIR="$HOME/.config/gws-<name>"`)。

```bash
# 追加アカウントを専用 config dir で取得(readonly)
export GOOGLE_WORKSPACE_CLI_CONFIG_DIR="$HOME/.config/gws-<name>"
gws calendar events list --params '{"calendarId":"primary","timeMin":"'"${TODAY}"'T00:00:00+09:00","timeMax":"'"${TOMORROW}"'T23:59:59+09:00","singleEvents":true,"orderBy":"startTime"}'
```

戻り JSON は **Google Calendar API ネイティブ形状**(`items[]`)。各要素から抽出:

- `summary` / `description`
- `start.dateTime` / `end.dateTime`(all-day なら `start.date` / `end.date`、`end.date` は **exclusive**=翌日になっている点に注意)
- `attendees[].displayName`(無ければ `.email`、ただし**domain は剥がさない**)
- `location`
- 会議URL = `hangoutLink`(Meet)または `conferenceData.entryPoints[]` の `entryPointType == "video"` の `uri`

**フィルタ**:

- `status == "cancelled"` の event は drop
- `visibility == "private"` かつ `summary` が空の event は drop(情報無し)
- attendees のうち `resource == true`(会議室)は drop

**複数カレンダー間の重複除去**:同じ予定が複数アカウントに見える構成(同期コピー等)では、Step 2 の ics 予定と `(start, end)` が一致する event を drop する。

**注意**:

- どのアカウントに繋がっているかの確認は各 config dir の `gws auth status` で行う(`gcloud auth list` は GCP CLI のログインアカウントで、capture 対象とは無関係)。
- capture を実行するマシンの**ローカル**に該当 config dir の資格情報が必要。
- OAuth アプリが Testing 公開ステータスのままだと refresh token が**約 7 日で失効**する(Google の仕様)。無人運用するなら Production 公開にするか、定期再認証で割り切る([[docs/connections/google-calendar-tasks.md]] §5)。
- 失敗時(未 provision / 失効 / 401 等)はエラーから secret を mask(`oauth2_token=...` / `access_token=...` / `bearer ...` / `authorization: ...`)した上で `<!-- secondary calendar unavailable: {message} -->` を該当セクションに残してスキップ。**briefing 全体は止めない**。

> **境界**:gws は「外部接続の hermes 経由 capture」として呼ぶ([[.claude/rules/agent-boundaries.md]] §6 に整合)。Claude 側 `daily-briefing` skill は直接叩かない(drift 防止)。CLI 挙動 drift(field rename / null 化など)を検知しても本 SKILL.md を hermes 自身は編集せず、`Inbox/{YYYY-MM-DD}/clippings/hermes-obs-inbox-daily-capture.md` に observation note を残す([[.claude/rules/inbox-routing.md]] §7)。

### 3. Google Tasks 取得(list_tasks.py・library 直叩き)

`list_tasks.py` は必ず **hermes venv の python をフルパスで**呼ぶ(システム側の python に google package が入っているとは限らないため。PATH 先頭の python 任せにしない)。

```bash
HERMES_VENV_PY="$(dirname "$(command -v hermes 2>/dev/null || echo)")/python"
[ -x "$HERMES_VENV_PY" ] || HERMES_VENV_PY="$HOME/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"  # Windows fallback
GTASKS="$HERMES_VENV_PY ${HERMES_HOME:-$HOME/.hermes}/skills/vault-capture/google-tasks/scripts/list_tasks.py"
$GTASKS   # 未完了タスクを JSON [{title, due, list, status}] で取得
```

- `list_tasks.py` は **hermes 共有 OAuth token(`${HERMES_HOME}/google_token.json`)を library で直叩き**する設計(`gws` npm CLI には依存しない)。認可済みアカウントの Tasks(複数リスト横断)を返す。
- 出力 JSON を「✅ Google Tasks」節に写す(**読み取りのみ**・vault で新規起票しない)。
- **非ゼロ終了**(スコープ未付与・未認証等)なら、stderr の 1 行を使って
  `<!-- google-tasks unavailable: {message} -->` を残してスキップ(briefing 全体は止めない)。
- 初回は **tasks.readonly スコープ追加+再認証**が必要:手順は [[.hermes/skills/vault-capture/google-tasks/SKILL.md]]。

### 4. 生 markdown を書き出し
- 下記フォーマットで `{vault}/Inbox/{today}/daily/daily.md` を**新規作成**(file tools で絶対パス書き込み)。

```markdown
---
source: hermes-capture
created: {YYYY-MM-DD}
calendar: primary
status: inbox
---

# {YYYY-MM-DD} 取り込み(raw / Hermes capture)

## 📅 今日の予定
- HH:MM-HH:MM **{summary}** ({attendees数}名){ @location }
  - 参加者: {名前を , 区切り}
  - 会議URL: {conferenceUrl があれば(Zoom/Meet 等)。空なら行ごと省略}
<!-- 予定なしなら「- なし」 -->
<!-- Step 2(ics)と Step 2.5(gws 追加アカウント)の event を start 昇順で merge、(start,end) で dedup -->

## 📅 明日の予定
- ...

## ✅ Google Tasks(未完了・写し)
- [ ] {タスク名}{ (〜MM-DD)}
<!-- 未対応時: <!-- google-tasks unavailable ... --> -->
```

### 5. 完了
- 書き込んだファイルパスを 1 行で報告。**他のファイルは触らない。**

## 起動方法(on-demand 既定 / cron は任意)

**既定 = on-demand**:ユーザーが Daily ノートの `## 🤖 ジョブリスト` を見て「<該当 job> やって」と Claude に指示 → Claude が hermes に CLI で委譲([[.claude/skills/hermes-query/SKILL.md]])。

### 手動 invoke コマンド

> `hermes chat -q` のスキル指定は `-s <skill>`(`--skill` / `--workdir` というフラグは無い)。vault ルートに cd してから呼ぶ。日本語 Windows では呼び出し前に `PYTHONUTF8=1` を設定する(cp932 デコード起因の出力欠落防止 → [[.claude/skills/hermes-query/SKILL.md]])。

```bash
cd "<vault root>"
hermes chat -q "Load the inbox-daily-capture skill and run it for today: fetch today's and tomorrow's Google Calendar events and (if available) Google Tasks, then write the raw markdown to Inbox/<today>/daily/daily.md in the vault. Write only inside Inbox/ — never touch root Daily/ or curated notes." -s inbox-daily-capture -Q --source claude-code
```

### Cron 登録(任意)

> cron による定期起動は**任意**(on-demand が既定)。毎朝決まった時刻に自動 capture したい場合のみ登録する。

state.db に保存されるジョブを次のコマンドで作成(ゲートウェイ側で実行):

```bash
hermes cron create "0 7 * * *"
# プロンプト入力(自然言語・このskillを起動):
#   Load the inbox-daily-capture skill and run it for today: fetch today's and
#   tomorrow's Google Calendar events and (if available) Google Tasks, then write
#   the raw markdown to Inbox/<today>/daily/daily.md in the vault. Write
#   only inside Inbox/ — never touch root Daily/ or curated notes.
```

- スケジュール例:平日のみなら `"0 7 * * 1-5"`、時刻は好みで調整。
- タイムゾーンは Hermes 設定(`config.yaml` の `timezone`)に従う。未設定なら TZ を確認。
- 動作確認:`hermes cron run <id>`(次tickで即時実行)→ `Inbox/{today}/daily/daily.md` 生成を確認。

## 関連

- 整理側(Claude Code):`[[.claude/skills/daily-briefing/SKILL.md]]`(Inbox/{date}/daily → root Daily)
- セットアップ:[[docs/connections/google-calendar-tasks.md]](ics 経路 / OAuth 経路の作り方・トラブルシューティング)
- 規約:`[[.claude/rules/agent-boundaries.md]]`(capture/curate 境界・single-writer)/ `[[Inbox/README.md]]`
- 依存:`google-workspace`(Calendar)/ `obsidian`(vault 書き込み)
