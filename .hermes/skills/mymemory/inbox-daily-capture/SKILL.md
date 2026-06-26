---
name: inbox-daily-capture
description: Use when capturing the day's Google Calendar (today + tomorrow) and Google Tasks into the <your-vault> Obsidian vault. Writes RAW markdown to Inbox/{YYYY-MM-DD}/daily/daily.md so the Claude Code daily-briefing step can curate it into the root Daily note. Intended to be invoked on-demand when the user issues a 取り込み instruction (typically from the Daily-note ジョブリスト). May also run from a cron if registered, but on-demand is the primary mode.
version: 1.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vault, capture, calendar, google-tasks, cron, mymemory]
    related_skills: [google-workspace, google-tasks, obsidian]
---

# inbox-daily-capture

your-vault の **capture 係**（Hermes 側）。the user が指示したタイミングで実行（既定）／cron で時間起動も可（任意）。今日と明日の Google Calendar 予定と
Google Tasks の未完了タスクを取得し、**生のまま** `Inbox/{YYYY-MM-DD}/daily/daily.md` に書き出す。

> **役割境界（重要）**：このスキルは **`Inbox/` 内にのみ書き込む**。root `Daily/` や
> curated（Work / Research / Others）には**絶対に触れない**。整理（curate）と root Daily への
> 集約は Claude Code 側の `daily-briefing` が行う（single-writer 原則）。
> ToDo の正本は **Google Tasks**。ここは読み取りの写しを置くだけで、タスクを起票しない。

## 前提・パス解決

- 当日の日付は実行時に取得（推測しない）：`date +%Y-%m-%d`
- vault ルートを解決（この順で）：
  1. `OBSIDIAN_VAULT_PATH`（設定されていればそれ）
  2. 無ければカレントディレクトリ、または `HERMES_HOME` の親ディレクトリが <your-vault> Vault に見える場合のみ採用（`HERMES_HOME=.../<your-vault>/.hermes` → vault=`.../<your-vault>`）。`~/.hermes` の親など Vault に見えない場所へは書かない。
- 書き込み先：`{vault}/Inbox/{YYYY-MM-DD}/daily/daily.md`（dated parent folder が日付を持つ。ファイル名は固定 `daily.md`）
- **file tools は環境変数を展開しない**。先にパスを文字列解決してから絶対パスで書く。
- Windows でもパスは forward slash 可（例 `<vault root>/Inbox/2026-06-03/daily/daily.md`）。

## 手順

### 1. 既存チェック（冪等）
- `{vault}/Inbox/{today}/daily/daily.md` が既にあれば**上書きせず終了**（同日多重実行の防止）。
  更新したい場合のみ明示再生成。

### 2. Calendar 取得（Private + Research/Lab を ics 経由）

**2026-06-16 アーキ修正**：旧 Step 2 は `python google_api.py calendar list` → gws (npm CLI) を優先する設計だったが、(a) ics ルートと冗長で、(b) `python` が PATH 先頭の `.local/bin/python.exe` (3.14) に当たって ImportError、(c) gws 自身は OAuth revoked、と 3 重に壊れて死蔵していた。**ics 直 fetch に一本化**（hermes-owned HTTP source として [[.claude/rules/agent-boundaries.md]] §1.1 push 表に整合）。

```bash
uv run "${HERMES_HOME:-$HOME/.hermes}/skills/mymemory/inbox-daily-capture/scripts/fetch_calendar_ics.py" --format md
```

- 設定ファイル `scripts/calendars.local.json`（**`.gitignore` 済み**・限定公開 ics URL を格納）から `Private`（your-email@example.com）／ `Research`（your-gmail@example.com）の 2 アカウントを取得。
- 出力フォーマット：`### 📅 今日の予定` / `### 📅 明日の予定` の md（そのまま Step 4 に流せる）。構造化が要れば `--format json`、別日基準は `--date YYYY-MM-DD`。
- 繰り返し予定 (RRULE) 展開・JST 変換・複数カレンダー横断 dedup 済み。OAuth 不要（ics URL に token 内包）。
- **失敗時**（ネット不通・config 不在等）：`<!-- ics calendar unavailable: {message} -->` を残してスキップ。**briefing 全体は止めない**。

> 旧 Claude 側 `.claude/skills/daily-briefing/_assets/fetch_calendar_ics.py` は本 commit で hermes 側へ移管（[[.claude/rules/agent-boundaries.md]] §6 接続所有権ルールに整合）。

### 2.5. Secondary Calendar 取得（gws calendar events list・gsk フォールバック）

**2026-06-22 切替**：secondary-workspace account（`your-work-email@example.com`）の予定取得を **gsk → gws（Google Workspace CLI）へ切替**。secondary-workspace を OAuth test user 登録＋プロジェクト `your-gcp-project-id` に `serviceUsageConsumer` IAM 付与することで gws の readonly Calendar が実機で通ることを検証済み（[[.claude/docs/knowledges/hermes/gws-multi-account-secondary.md]]）。**gsk は fallback として残す**（gws 未 provision / 7日失効時）。東大 Workspace は限定公開 ics を出さない（ics 経路は不可）が、外部 OAuth は組織ブロックしていない。

**確認時の注意**：ユーザーが「<your-vault> 内で gws が取る対象アカウントが 2 つか」を聞いている場合、`gcloud auth list` は見ない（これは GCP CLI のログインアカウントで、capture 対象ではない）。確認するのはこの skill の接続設計と GWS config dir：既定 `~/.config/gws` = lab/personal（`your-gmail@example.com`）、Secondary は `GOOGLE_WORKSPACE_CLI_CONFIG_DIR="$HOME/.config/gws-secondary"` = `your-work-email@example.com`。実機 provision 状態は `gws auth status` と `GOOGLE_WORKSPACE_CLI_CONFIG_DIR="$HOME/.config/gws-secondary" gws auth status`、および `find "$HOME/.config" -maxdepth 1 -type d -name 'gws*'` で切り分ける。

> **前提（PC ローカル・重要）**：gws の secondary 資格情報は **capture を実行する PC のローカル** `~/.config/gws-secondary/credentials.enc` に必要。primary host (gateway)で本 skill を回すなら owner PC 上で一度 `gws auth login`（secondary・readonly）して provision する（手順は上記 knowledge note）。未 provision の PC では gws が失敗 → 自動で gsk fallback に落ちる（briefing は止まらない）。
> **7日失効注意**：OAuth app が Testing 公開ステータスの間 refresh token は約7日で失効する。無人 capture を gws 一本化するなら app を Production 公開して失効を解消するか、gsk fallback を保持すること。

```bash
# secondary-workspace を gws 専用 config dir で取得（readonly）
export GOOGLE_WORKSPACE_CLI_CONFIG_DIR="$HOME/.config/gws-secondary"
gws calendar events list --params '{"calendarId":"primary","timeMin":"'"${TODAY}"'T00:00:00+09:00","timeMax":"'"${TOMORROW}"'T23:59:59+09:00","singleEvents":true,"orderBy":"startTime"}'
```

戻り JSON は **Google Calendar API ネイティブ形状**（`items[]`。gsk の `data.events[]` とは別形状）。各要素から抽出：

- `summary` / `description`
- `start.dateTime` / `end.dateTime`（all-day なら `start.date` / `end.date`、`end.date` は **exclusive**＝翌日になっている点に注意）
- `attendees[].displayName`（無ければ `.email`、ただし**domain は剥がさない**）
- `location`
- 会議URL = `hangoutLink`（Meet）または `conferenceData.entryPoints[]` の `entryPointType == "video"` の `uri`

**フィルタ**：

- `status == "cancelled"` の event は drop
- `visibility == "private"` かつ `summary` が空の event は drop（情報無し）
- attendees のうち `resource == true`（会議室。gsk fallback 時は `@resource.calendar.google.com` 終端で判定）は drop

**Mirror event の重複除去**（重要）：secondary 側に「lab calendar からの自動同期コピー」が `description` に `自動作成された同期予定` または `元の予定: <ORIGINAL TITLE>` を含む形で混ざる。検出ルールは **description 主軸**（marker 文字依存しない）：

- `description` が `自動作成された同期予定` を含む、または `元の予定:\s*(.+)` にマッチする → mirror 判定
- Step 2 で取得した Research/Lab 側 ics 予定と `(start, end)` が一致する mirror → **drop**（重複防止）
- 一致しない mirror → `summary` を `元の予定:` の捕捉文字列に置換して残す（rare case）

**失敗時 → gsk フォールバック**：gws が非ゼロ終了（未 provision / 7日失効 / 401 / command not found）なら、従来の gsk 経路を試みる：

```bash
gsk google_calendar list --time_min "${TODAY}T00:00:00+09:00" --time_max "${TOMORROW}T23:59:59+09:00"
```

（gsk 戻りは `data.events[]`・`event.conferenceUrl`。抽出/フィルタ/mirror-dedup は上と同義だが gsk フィールド名で行う。）gws・gsk 双方失敗時はエラーから secret を mask（`private-*` / `oauth2_token=...` / `access_token=...` / `bearer\s+...` / `authorization:\s*\S+`）した上で `<!-- secondary-workspace calendar unavailable: {message} -->` を該当セクションに残してスキップ。**briefing 全体は止めない**。

> **境界**：gws / gsk いずれも「外部接続の hermes 経由 capture」として呼ぶ（[[.claude/rules/agent-boundaries.md]] §6 に整合）。Claude 側 `daily-briefing` skill は直接叩かない（drift 防止）。CLI 挙動 drift（field rename / null 化など）を検知しても本 SKILL.md を hermes 自身は編集せず、`Inbox/{YYYY-MM-DD}/clippings/hermes-obs-inbox-daily-capture.md` に observation note を残す（cross-territory rule、[[.claude/rules/inbox-routing.md]] §7）。

### 3. Google Tasks 取得（list_tasks.py・library 直叩き）

**2026-06-16 修正**：旧記述は `python list_tasks.py` だったが、PATH 先頭の `.local/bin/python.exe` (3.14) には google package 未インストール → ImportError → 死。hermes venv python を**フルパス明示**で呼ぶ。

```bash
HERMES_VENV_PY="$(dirname "$(command -v hermes 2>/dev/null || echo)")/python.exe"
[ -x "$HERMES_VENV_PY" ] || HERMES_VENV_PY="$HOME/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe"  # Windows fallback
GTASKS="$HERMES_VENV_PY ${HERMES_HOME:-$HOME/.hermes}/skills/mymemory/google-tasks/scripts/list_tasks.py"
$GTASKS   # 未完了タスクを JSON [{title, due, list, status}] で取得
```

- `list_tasks.py` は **hermes 共有 OAuth token（`${HERMES_HOME}/google_token.json`）を library で直叩き**する設計（`gws` npm CLI には依存しない）。your-gmail@example.com の Tasks（複数リスト横断）を返す。
- 出力 JSON を「✅ Google Tasks」節に写す（**読み取りのみ**・Vault で新規起票しない）。
- **非ゼロ終了**（スコープ未付与・未認証等）なら、stderr の 1 行を使って
  `<!-- google-tasks unavailable: {message} -->` を残してスキップ（briefing 全体は止めない）。
- 初回は **tasks.readonly スコープ追加＋再認証**が必要：手順は [[.hermes/skills/mymemory/google-tasks/SKILL.md]]。

### 4. 生 markdown を書き出し
- 下記フォーマットで `{vault}/Inbox/{today}/daily/daily.md` を**新規作成**（file tools で絶対パス書き込み）。

```markdown
---
source: hermes-capture
created: {YYYY-MM-DD}
calendar: primary
status: inbox
---

# {YYYY-MM-DD} 取り込み（raw / Hermes capture）

## 📅 今日の予定
- HH:MM-HH:MM **{summary}** ({attendees数}名){ @location }
  - 参加者: {名前を , 区切り}
  - 会議URL: {conferenceUrl があれば（Zoom/Meet 等）。空なら行ごと省略}
<!-- 予定なしなら「- なし」 -->
<!-- Step 2（ics）と Step 2.5（gws/gsk secondary）の event を start 昇順で merge、(start,end) で mirror dedup -->

## 📅 明日の予定
- ...

## ✅ Google Tasks（未完了・写し）
- [ ] {タスク名}{ （〜MM-DD）}
<!-- 未対応時: <!-- google-tasks unavailable ... --> -->
```

### 5. 完了
- 書き込んだファイルパスを 1 行で報告。**他のファイルは触らない。**

## 起動方法（on-demand 既定 / cron は任意）

**既定 = on-demand**：the user が Daily ノートの `## 🤖 ジョブリスト` を見て「<該当 job> やって」と Claude に指示 → Claude が hermes に CLI で委譲（[[.claude/skills/hermes-query/SKILL.md]]）。

### 手動 invoke コマンド（PowerShell）

> ⚠️ **2026-06-16 修正**：`--skill` / `--workdir` は無効（`hermes chat -q` の実際のフラグは `-s SKILLS` / cwd）。Set-Location で vault に入ってから呼ぶ。`$env:PYTHONUTF8 = '1'` は cp932 文字化け回避（[[.claude/docs/knowledges/python/windows-cp932-stdout-default.md]]）。

```powershell
# PowerShell（推奨・cp932 落とし穴回避のため $env:PYTHONUTF8 必須）
$env:PYTHONUTF8 = '1'
Set-Location "<vault root>"
hermes chat -q "Load the inbox-daily-capture skill and run it for today: fetch today's and tomorrow's Google Calendar events and (if available) Google Tasks, then write the raw markdown to Inbox/<today>/daily/daily.md in the your-vault. Write only inside Inbox/ — never touch root Daily/ or curated notes." -s inbox-daily-capture -Q --source claude-code
```

### Cron 登録（任意 / メインPC のみ・現状は維持）

> ⚠️ **2026-06-16 方針変更**：cron による定期起動は **任意**。既存の cron job が稼働中なら維持してよいが、新規登録は不要（on-demand が既定）。下記コマンドは参照用に残す。

state.db に保存されるジョブを次のコマンドで作成（ゲートウェイ側で実行）：

```bash
hermes cron create "0 7 * * *"
# プロンプト入力（自然言語・このskillを起動）:
#   Load the inbox-daily-capture skill and run it for today: fetch today's and
#   tomorrow's Google Calendar events and (if available) Google Tasks, then write
#   the raw markdown to Inbox/<today>/daily/daily.md in the your-vault. Write
#   only inside Inbox/ — never touch root Daily/ or curated notes.
```

- スケジュール例：平日のみなら `"0 7 * * 1-5"`、時刻は好みで調整。
- タイムゾーンは Hermes 設定（`config.yaml` の `timezone`）に従う。未設定なら TZ を確認。
- 動作確認：`hermes cron run <id>`（次tickで即時実行）→ `Inbox/{today}/daily/daily.md` 生成を確認。

## 関連

- 整理側（Claude Code）：`[[.claude/skills/daily-briefing/SKILL.md]]`（Inbox/{date}/daily → root Daily）
- 規約：`[[.claude/rules/agent-boundaries.md]]`（capture/curate 境界・single-writer）/ `[[Inbox/README.md]]`
- 依存：`google-workspace`（Calendar）/ `obsidian`（vault 書き込み）
