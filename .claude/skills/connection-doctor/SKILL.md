---
name: connection-doctor
description: Use when the user asks to check / diagnose external connections (「接続チェックして」「Hermes 繋がってる?」「Slack が取れないんだけど」etc.). Runs READ-ONLY diagnostics over the Hermes-owned connections (Hermes core / GitHub / Google Calendar+Tasks / Slack / Genspark / Notion / clippings) plus the local prerequisites (Codex CLI, vault git), then reports a status table with per-connection next actions linking to docs/connections/. Never fixes anything autonomously — diagnosis and proposals only.
---

# connection-doctor — 外部接続の一括診断

初心者が一番躓く「外部ツールとの繋ぎ込み」の切り分けを 1 コマンド化する skill。
ユーザーが「接続チェックして」「○○が繋がらない」と言ったら発動する。

## 原則

- **read-only**:診断のみ。設定変更・トークン再発行・ファイル削除は**しない**(修復は提案として提示し、対応する [[docs/connections/README.md]] のガイドへ誘導する)
- **graceful degradation**:1 つのチェックが失敗しても全体を続行する。タイムアウトは各チェック 30–180 秒
- **secrets を表示しない**:トークン値・URL 内 token は「設定あり / なし」だけ報告する。**値を echo しない・会話に貼らない**
- 特定の接続だけ聞かれたら(「Slack だけ見て」)、その接続のチェックのみ実行する

## チェック手順

### 0. 前提レイヤー

| # | チェック | コマンド / 方法 | 判定 |
|---|---|---|---|
| 0-1 | vault git | `git -C {vault} status --short` | repo として動くか |
| 0-2 | Codex CLI(任意) | `codex --version` | 無ければ「Level 1 未導入(任意)」として ℹ️ |
| 0-3 | Hermes CLI | `hermes --version` | 無ければ**以降の接続チェックは全部スキップ**し、[[GETTING-STARTED.md]] Level 2 へ誘導 |
| 0-4 | Hermes 応答 | `hermes chat -q "reply with exactly: PONG" -Q`(timeout 180s) | 応答があるか。LLM バックエンド設定の生死がここでわかる |

> Windows 日本語環境では `PYTHONUTF8=1` を設定してから hermes を呼ぶ(cp932 問題 → [[.claude/skills/hermes-query/SKILL.md]])。

### 1. 接続レイヤー(それぞれ独立・失敗しても続行)

| 接続 | 静的チェック(設定の存在) | 動的チェック(実疎通・pull) |
|---|---|---|
| **GitHub** | `.hermes/.env` 等に `GITHUB_PERSONAL_ACCESS_TOKEN` の**キーが存在するか**(`grep -c` で有無のみ) | `hermes chat -q "GitHub MCP で <Code-Map 先頭の repo> の最新コミット 1 件" -Q`。`Maps/Code-Map.md` に repo が列挙されているかも確認 |
| **Google** | `~/.hermes/google_token.json` の存在 | `python .hermes/skills/vault-capture/google-auth/scripts/authorize.py --check`(AUTHENTICATED + スコープ一覧)。ics 経路は `calendars.local.json` の存在 + `fetch_calendar_ics.py --format md` |
| **Slack** | `.hermes/.env` に `SLACK_BOT_TOKEN` / `SLACK_USER_TOKEN` / `SLACK_ALLOWED_USERS` のキー有無 | `hermes chat -q "Slack で自分の user info を users.info で確認して" -Q` |
| **Genspark** | `gsk` が PATH にあるか(`command -v gsk`) | `gsk meeting list`(一覧 or 空リストが返れば OK) |
| **Notion** | `config.yaml` に notion MCP が enabled か | `hermes chat -q "Notion MCP で何か 1 ページ検索して(タイトルだけ)" -Q` |
| **Clippings** | (Hermes 不要経路のため)直近 7 日の `Inbox/*/clippings/` にファイルがあるか | — |

### 2. パイプラインレイヤー(capture 実績)

直近 7 日の `Inbox/{date}/{source}/` を走査し、**source ごとの最終 capture 日**を出す:

```bash
find {vault}/Inbox -mindepth 2 -maxdepth 2 -type d | sort -r | head -30
```

「接続は生きているのに capture が 5 日前で止まっている」のような**運用の切れ目**もここで見つける。

## 報告フォーマット

結論 → 表 → 次アクション の順。例:

```markdown
## 🔍 接続診断結果(2026-07-19)

**結論**:GitHub / Google は正常。Slack は User トークン未設定(検索系のみ不可)。

| 接続 | 状態 | 最終 capture | 次のアクション |
|---|---|---|---|
| Hermes 本体 | ✅ | — | — |
| GitHub | ✅ | 2026-07-18 | — |
| Google Cal+Tasks | ✅ | 2026-07-19 | — |
| Slack | ⚠️ | 2026-07-14 | SLACK_USER_TOKEN を追加 → docs/connections/slack.md §3.2 |
| Genspark | ➖ 未設定 | — | 使うなら docs/connections/genspark.md |
| Notion | ➖ 未設定 | — | 使うなら docs/connections/notion.md |
```

- ✅ 正常 / ⚠️ 一部問題 / ❌ 不通 / ➖ 未設定(未設定は**エラー扱いしない** — 全接続任意が設計)
- 各 ⚠️ / ❌ には**原因の推定 + 該当ガイドの「よくある躓き」該当行**を 1 行で添える
- 修復コマンドは提示するだけで実行しない(ユーザー承認後に実行)

## 関連

- [[GETTING-STARTED.md]] — 段階的セットアップ(Level 0–3)
- [[docs/connections/README.md]] — 接続別ガイド(修復手順の誘導先)
- [[.claude/skills/hermes-query/SKILL.md]] — pull 経路の呼び出し規約
- [[.claude/rules/agent-boundaries.md]] §6 — 接続の所有マップ
