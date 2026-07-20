---
title: "接続ガイド: Google Calendar + Tasks"
type: "reference"
status: "completed"
tags: ["setup", "connections", "google"]
created: 2026-07-19
updated: 2026-07-20
---

# 接続ガイド: Google Calendar + Tasks(難易度 ★★☆・約30–60分)

この vault の**一番おいしい部分**である「朝の briefing 自動化」の土台です。繋がると、毎朝「デイリー取り込みやって」の一言で今日+明日の予定と未完了タスクが `Inbox/{date}/daily/daily.md` に落ち、`daily-briefing` skill が Daily ノートの朝 briefing を組み立てます。

接続面は 3 つに分かれます。Calendar と Tasks は独立して有効化できます:

| 経路 | 対象 | 難易度 | 認証 |
|---|---|---|---|
| **A. ics 限定公開 URL** | Calendar のみ(読み取り) | ★☆☆・10分 | **不要** |
| **B. Hermes 共有 OAuth** | Google Tasks のみ(読み取り) | ★★☆・30–60分 | GCP OAuth |
| **C. `gws` 追加 Calendar** | private ICS を出せない追加アカウント | ★★☆ | account 別 `gws` OAuth |

> まず A で Calendar を繋ぎ、Tasks が必要なら B を追加します。C は組織ポリシーで private ICS を発行できない Calendar にだけ使います。B の共有 token は Calendar capture には使いません。

## 1. 何ができるようになるか

- **push(朝 capture)**:今日+明日の Calendar 予定 + Google Tasks の未完了タスク → `Inbox/{date}/daily/daily.md`。`daily-briefing` が Daily ノートに Today's Focus・会議一覧付きの朝 briefing を構成
- **pull**:「今の未完了タスクは?」「明日の予定は?」をコアエージェントからその場で確認

> **ToDo の正本は Google Tasks のまま**です。vault には読み取りの写しを置くだけで、vault 内に競合するタスクリストは作りません([[.codex/rules/agent-boundaries.md]] §2)。

## 2. 経路 A:ics 限定公開 URL(Calendar のみ・OAuth 不要)

### 手順

1. Google Calendar(Web)→ 設定 → 対象カレンダー → 「カレンダーの統合」→ **「iCal 形式の限定公開 URL」** をコピー
   - この URL は**トークン内包の秘密情報**です。共有しないこと
2. `${HERMES_HOME}/skills/vault-capture/inbox-daily-capture/scripts/calendars.local.json` を作成(gitignore 済み):

   ```json
   {
     "calendars": [
       { "label": "Private", "url": "https://calendar.google.com/calendar/ical/.../basic.ics" }
     ]
   }
   ```

   複数カレンダー(仕事用・私用など)を並べれば横断取得+重複排除されます。
3. 動作確認:

   ```bash
   uv run "$HERMES_HOME/skills/vault-capture/inbox-daily-capture/scripts/fetch_calendar_ics.py" --format md
   ```

   今日・明日の予定が Markdown で出れば OK。繰り返し予定(RRULE)の展開・タイムゾーン変換も済んだ状態で出ます。

> **組織の Google Workspace は ics の限定公開 URL を無効にしている場合があります**。その場合は経路 C へ。

## 3. 経路 B:Hermes 共有 OAuth(Google Tasks)

GCP(Google Cloud)で OAuth クライアントを作り、`list_tasks.py` が読む `${HERMES_HOME}/google_token.json` を認可します。この経路は Tasks 専用で、Calendar は A または C から取得します。

### 手順

1. **GCP プロジェクト作成**:[console.cloud.google.com](https://console.cloud.google.com) → 新しいプロジェクト(名前は何でも可)
2. **Google Tasks API を有効化**(無効のままだと認証は成功しても Tasks 取得だけ失敗します)
3. **OAuth 同意画面**:User Type = External、公開ステータスは Testing のままで OK。**「テストユーザー」に自分の Google アカウントを追加**(忘れると認証時に `access_denied`)
4. **OAuth クライアント作成**:「認証情報」→ 認証情報を作成 → OAuth クライアント ID → 種類 = **デスクトップアプリ** → JSON をダウンロード
5. **Hermes runtime Python を解決**。Google package/token を再利用する限定例外なので、ここでは通常の `uv` ではなく Hermes runtime を明示します:

   ```bash
   HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
   if [ -n "${HERMES_PYTHON:-}" ] && [ -x "$HERMES_PYTHON" ]; then
     HERMES_RUNTIME_PY="$HERMES_PYTHON"
   elif [ -x "$HERMES_HOME/hermes-agent/venv/bin/python" ]; then
     HERMES_RUNTIME_PY="$HERMES_HOME/hermes-agent/venv/bin/python"
   elif [ -x "$HERMES_HOME/hermes-agent/venv/Scripts/python.exe" ]; then
     HERMES_RUNTIME_PY="$HERMES_HOME/hermes-agent/venv/Scripts/python.exe"
   else
     echo "Hermes runtime Python not found; set HERMES_PYTHON" >&2; exit 1
   fi
   ```

6. **クライアントシークレットを Hermes に登録**:

   ```bash
   "$HERMES_RUNTIME_PY" "$HERMES_HOME/skills/productivity/google-workspace/scripts/setup.py" --client-secret /path/to/client_secret.json
   ```

7. **認可(この vault の tracked スクリプトで)**:

   ```bash
   # 1) 同意 URL を表示 → ブラウザで開いて許可
   "$HERMES_RUNTIME_PY" "$HERMES_HOME/skills/vault-capture/google-auth/scripts/authorize.py" --auth-url

   # 2) リダイレクト先(localhost で開けないページ)の URL 全体をコピーして渡す
   "$HERMES_RUNTIME_PY" "$HERMES_HOME/skills/vault-capture/google-auth/scripts/authorize.py" --auth-code "<リダイレクト URL 全体>"

   # 3) 確認:AUTHENTICATED と付与スコープ一覧が出れば完了
   "$HERMES_RUNTIME_PY" "$HERMES_HOME/skills/vault-capture/google-auth/scripts/authorize.py" --check
   ```

   トークンは `${HERMES_HOME}/google_token.json` に保存されます(git 対象外)。

## 4. 経路 C:`gws` 追加 Calendar(任意)

組織アカウントで private ICS URL が発行できない場合だけ使います。アカウントごとに config dir を分け、Calendar read-only scope でログインします。Tasks はこの経路に依存しません。

```bash
export GOOGLE_WORKSPACE_CLI_CONFIG_DIR="$HOME/.config/gws-work"
gws auth login --scopes 'https://www.googleapis.com/auth/calendar.readonly'
gws auth status
gws calendar events list --params '{"calendarId":"primary","maxResults":3,"singleEvents":true,"orderBy":"startTime"}'
```

詳細は [[.hermes/skills/vault-capture/google-auth/references/gws-cli-calendar-tasks.md]]。capture 実行 PC にこの config dir の資格情報が必要です。

## 5. 動作確認

**pull**:

```bash
hermes chat -q "list my Google Tasks" -Q
hermes chat -q "明日の予定を教えて" -Q
```

**push(パイプライン全体)**:コアエージェントに

```text
デイリー取り込みやって
```

→ `Inbox/{今日の日付}/daily/daily.md` ができる → 「朝の briefing 作って」で Daily ノートに反映されれば完了です。

## 6. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| 認証時に `access_denied` | OAuth 同意画面のテストユーザーに自分を追加していない |
| 認証は通るが Tasks だけ失敗 | GCP で **Google Tasks API を有効化**していない(手順 B-2) |
| **約 7 日でトークン失効**する | OAuth アプリが Testing 公開ステータスだと refresh token が約 7 日で失効する。Production 公開または再認証で対応 |
| ics 取得が失敗する | URL の期限切れ / 組織が限定公開 URL を無効化。カレンダー設定で URL をリセットして貼り直すか、経路 C へ |
| Tasks は取れるが Calendar が空 | 正常な切り分けです。朝 capture の経路 B は shared token を Tasks にだけ使い、Calendar は経路 A または C から取得します。token 自体は bundled Google service と Tasks の scope を持つ superset です |
| `gws` Calendar だけ失敗 | `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` と `gws auth status` の account/scopes を確認 |
| capture がスキップされる | `Inbox/{date}/daily/daily.md` が既にある(冪等性・正常)。Daily handoff 後は変更しない。誤 capture の訂正はコアとユーザーが監査記録付きで扱う |

## 7. 深掘り

- [[.hermes/skills/vault-capture/google-auth/SKILL.md]] — OAuth スコープ設計・再認可・スコープ追加の方法
- [[.hermes/skills/vault-capture/inbox-daily-capture/SKILL.md]] — 朝 capture 本体(ics / gws の使い分け・フォールバック)
- [[.hermes/skills/vault-capture/google-tasks/SKILL.md]] — Tasks 取得スクリプト
- 複数 Google アカウント(会社 Workspace など)を扱いたい場合 → [[.hermes/skills/vault-capture/google-auth/references/gws-cli-calendar-tasks.md]](gws CLI の config dir 切り替え)
