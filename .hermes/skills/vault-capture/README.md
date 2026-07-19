# .hermes/skills/vault-capture/ — このVault専用の自作 Hermes スキル（git 追跡）

bundled（同梱）スキルは `.gitignore` で除外しているが、**この `vault-capture/` カテゴリだけは版管理対象**
（制御プレーン＝<your-vault> でコアエージェントと Hermes の宣言的設定を管理する方針）。

Hermes は `~/.hermes/skills/**/SKILL.md` を自動スキャンするので、ここに置けば登録される（manifest 不要）。

## Inbox レイアウト（date-first・capture-only）

hermes の capture はすべて **`Inbox/{YYYY-MM-DD}/{source}/`**（1 日 = 1 つの日付つき親フォルダ、source ごとにサブフォルダ）に着地する。**auto-route も LLM 判定もしない**。サブフォルダはその source が実際にデータを出した日にだけ作る（全 source を毎日強制的に作らない）。ファイル名に日付 prefix は付けない（日付は親フォルダが持つ）。

| source | 着地パス |
|---|---|
| daily | `Inbox/{date}/daily/daily.md`（GCal + GTasks 朝 capture）|
| slack | `Inbox/{date}/slack/{channel}.md`（channel ごと日次ダイジェスト・DM は `dm-{counterpart}.md`）|
| code | `Inbox/{date}/code/code.md`（github-eod-capture）|
| mtgs | `Inbox/{date}/mtgs/genspark-{slug}.md`（genspark 議事録）|
| clippings | `Inbox/{date}/clippings/{slug}.md`（Web クリップ + hermes observation note）|
| chat-logs | `Inbox/{date}/chat-logs/{provider}-{slug}.md` |
| attachments | `Inbox/{date}/attachments/…`（slack 添付は `Inbox/{date}/attachments/slack/{channel}/…`）|

`Daily/{date}.md` が **唯一のハブ**：Claude が `Inbox/{date}/*` を集約し、EOD に Wiki へ蒸留・分配する。hermes は `Daily/` や curated フォルダには書かない。

## 収録スキル

- `inbox-daily-capture/` — 毎朝 Calendar + Google Tasks を `Inbox/{date}/daily/daily.md` に生 capture（on-demand 既定・cron 任意）。
  整理は Claude Code 側 [[.claude/skills/daily-briefing/SKILL.md]] が担当。
- `slack-capture/` — 毎朝、前日分の Slack（the user 発言／@mention、public/private/DM）を
  `Inbox/{date}/slack/{channel}.md` に日次ダイジェスト化（on-demand 既定・cron 任意）。**capture 専用・routing なし**。
- `genspark-mtg/` — Genspark AI 議事録を `Inbox/{date}/mtgs/genspark-{slug}.md` に生 capture（polling + 夕方 safety-net）。
- `github-eod-capture/` — `Maps/Code-Map.md` の全 repo の当日 commits/PRs/issues を `Inbox/{date}/code/code.md` に生 capture（on-demand 既定・cron 任意）。
- `clippings-capture/` — Web の壁打ち／記事を `Inbox/{date}/clippings/{slug}.md` に生 capture（Chrome 拡張 → gateway / 手動）。
- `google-auth/` — Google OAuth 一括認可ヘルパ（Calendar / Tasks の初回セットアップ）。
- `google-tasks/` — Google Tasks 取得スクリプト。
- `defuddle/` — URL→markdown 抽出ヘルパ（clippings-capture 内部・on-demand pull 用）。
- `genspark-slide/` — スライド生成の補助スキル（capture ではない）。

## 方針

- ここに置くスキルは **capture / 同期など Hermes 担当（`Inbox/{date}/{source}/` 内書き込みに限定）**。
- **routing しない**（channel→宛先マップ・DM 振り分け・auto-route は廃止）。curate（蒸留・分配）は Claude Code + ユーザーの仕事。
- curated 領域の編集ロジックは置かない（それは Claude Code 側スキル）。
- 詳細は [[.claude/rules/agent-boundaries.md]] / [[.claude/rules/inbox-routing.md]]。
