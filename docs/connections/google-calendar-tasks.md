---
title: "接続ガイド: Google Calendar + Tasks"
type: "reference"
status: "completed"
tags: ["setup", "connections", "google"]
created: 2026-07-19
updated: 2026-07-19
---

# 接続ガイド: Google Calendar + Tasks(難易度 ★★☆・約30–60分)

この vault の**一番おいしい部分**である「朝の briefing 自動化」の土台です。繋がると、毎朝「デイリー取り込みやって」の一言で今日+明日の予定と未完了タスクが `Inbox/{date}/daily/daily.md` に落ち、`daily-briefing` skill が Daily ノートの朝 briefing を組み立てます。

**2 つの経路があり、簡単な方(A)から始められます**:

| 経路 | 対象 | 難易度 | OAuth |
|---|---|---|---|
| **A. ics 限定公開 URL** | Calendar のみ(読み取り) | ★☆☆・10分 | **不要** |
| **B. Google OAuth** | Calendar + **Tasks** | ★★☆・30–60分 | 必要(GCP 設定) |

> まず A で Calendar だけ繋いで朝 briefing を体感し、Tasks も欲しくなったら B に進む、が挫折しない順序です。

## 1. 何ができるようになるか

- **push(朝 capture)**:今日+明日の Calendar 予定 + Google Tasks の未完了タスク → `Inbox/{date}/daily/daily.md`。`daily-briefing` が Daily ノートに Today's Focus・会議一覧付きの朝 briefing を構成
- **pull**:「今の未完了タスクは?」「明日の予定は?」を Claude Code からその場で確認

> **ToDo の正本は Google Tasks のまま**です。vault には読み取りの写しを置くだけで、vault 内に競合するタスクリストは作りません([[.claude/rules/agent-boundaries.md]] §2)。

## 2. 経路 A:ics 限定公開 URL(Calendar のみ・OAuth 不要)

### 手順

1. Google Calendar(Web)→ 設定 → 対象カレンダー → 「カレンダーの統合」→ **「iCal 形式の限定公開 URL」** をコピー
   - この URL は**トークン内包の秘密情報**です。共有しないこと
2. `.hermes/skills/vault-capture/inbox-daily-capture/scripts/calendars.local.json` を作成(gitignore 済み):

   ```json
   {
     "calendars": [
       { "name": "Private", "ics_url": "https://calendar.google.com/calendar/ical/.../basic.ics" }
     ]
   }
   ```

   複数カレンダー(仕事用・私用など)を並べれば横断取得+重複排除されます。
3. 動作確認:

   ```bash
   uv run .hermes/skills/vault-capture/inbox-daily-capture/scripts/fetch_calendar_ics.py --format md
   ```

   今日・明日の予定が Markdown で出れば OK。繰り返し予定(RRULE)の展開・タイムゾーン変換も済んだ状態で出ます。

> **組織の Google Workspace は ics の限定公開 URL を無効にしている場合があります**。その場合は経路 B へ。

## 3. 経路 B:Google OAuth(Calendar + Tasks)

GCP(Google Cloud)での OAuth クライアント作成が必要です。ここが一番の山場ですが、一度通せば以降は自動更新です。

### 手順

1. **GCP プロジェクト作成**:[console.cloud.google.com](https://console.cloud.google.com) → 新しいプロジェクト(名前は何でも可)
2. **API を有効化**:「API とサービス」→ ライブラリで以下を有効化
   - **Google Calendar API**
   - **Google Tasks API**(←忘れやすい。無効のままだと**認証は成功するのに Tasks 取得だけ失敗**します)
3. **OAuth 同意画面**:User Type = External、公開ステータスは Testing のままで OK。**「テストユーザー」に自分の Google アカウントを追加**(忘れると認証時に `access_denied`)
4. **OAuth クライアント作成**:「認証情報」→ 認証情報を作成 → OAuth クライアント ID → 種類 = **デスクトップアプリ** → JSON をダウンロード
5. **クライアントシークレットを Hermes に登録**:

   ```bash
   python .hermes/skills/productivity/google-workspace/scripts/setup.py --client-secret /path/to/client_secret.json
   ```

6. **認可(この vault の tracked スクリプトで)**:bundled の setup.py ではなく、**必要スコープ全部を 1 回の同意で取る** `google-auth` skill を使います

   ```bash
   # 1) 同意 URL を表示 → ブラウザで開いて許可
   python .hermes/skills/vault-capture/google-auth/scripts/authorize.py --auth-url

   # 2) リダイレクト先(localhost で開けないページ)の URL 全体をコピーして渡す
   python .hermes/skills/vault-capture/google-auth/scripts/authorize.py --auth-code "<リダイレクト URL 全体>"

   # 3) 確認:AUTHENTICATED と付与スコープ一覧が出れば完了
   python .hermes/skills/vault-capture/google-auth/scripts/authorize.py --check
   ```

   トークンは `~/.hermes/google_token.json` に保存されます(git 対象外)。

## 4. 動作確認

**pull**:

```bash
hermes chat -q "list my Google Tasks" -Q
hermes chat -q "明日の予定を教えて" -Q
```

**push(パイプライン全体)**:Claude Code に

```text
デイリー取り込みやって
```

→ `Inbox/{今日の日付}/daily/daily.md` ができる → 「朝の briefing 作って」で Daily ノートに反映されれば完了です。

## 5. よくある躓き

| 症状 | 原因と対処 |
|---|---|
| 認証時に `access_denied` | OAuth 同意画面のテストユーザーに自分を追加していない |
| 認証は通るが Tasks だけ失敗 | GCP で **Google Tasks API を有効化**していない(手順 B-2) |
| **約 7 日でトークン失効**する | OAuth アプリが Testing 公開ステータスだと refresh token が約 7 日で失効する Google の仕様。対処は 2 択:(a) 同意画面を **Production に公開**(個人利用なら審査不要のまま使えるスコープ構成にする)、(b) 週 1 で `authorize.py --auth-url` から再認証する運用で割り切る |
| ics 取得が失敗する | URL の期限切れ / 組織が限定公開 URL を無効化。カレンダー設定で URL をリセットして貼り直すか、経路 B へ |
| capture がスキップされる | `Inbox/{date}/daily/daily.md` が既にある(冪等性・正常)。再生成したい場合は消してから |

## 6. 深掘り

- [[.hermes/skills/vault-capture/google-auth/SKILL.md]] — OAuth スコープ設計・再認可・スコープ追加の方法
- [[.hermes/skills/vault-capture/inbox-daily-capture/SKILL.md]] — 朝 capture 本体(ics / gws の使い分け・フォールバック)
- [[.hermes/skills/vault-capture/google-tasks/SKILL.md]] — Tasks 取得スクリプト
- 複数 Google アカウント(会社 Workspace など)を扱いたい場合 → [[.hermes/skills/vault-capture/google-auth/references/gws-cli-calendar-tasks.md]](gws CLI の config dir 切り替え)
