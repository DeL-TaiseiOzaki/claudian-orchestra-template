# .hermes/skills/vault-capture/ — このVault専用の自作 Hermes スキル（git 追跡）

bundled（同梱）スキルは `.gitignore` で除外しているが、**この `vault-capture/` カテゴリだけは版管理対象**
（制御プレーン＝<your-vault> でコアエージェントと Hermes の宣言的設定を管理する方針）。

Hermes は**実行時の `${HERMES_HOME}/skills/**/SKILL.md`** をスキャンする。vault ルートで `export HERMES_HOME="$PWD/.hermes"` とする per-vault profile が推奨で、この追跡済み skill 群をそのまま discovery できる。既存の global profile を使う場合は、`.hermes/config.yaml` だけでなく、この `vault-capture/` 全体も active profile の `skills/` へ mirror する（manifest 不要）。

## Inbox レイアウト（date-first・capture-only）

hermes の capture はすべて **`Inbox/{YYYY-MM-DD}/{source}/`**（1 日 = 1 つの日付つき親フォルダ、source ごとにサブフォルダ）に着地する。**auto-route も LLM 判定もしない**。サブフォルダはその source が実際にデータを出した日にだけ作る（全 source を毎日強制的に作らない）。ファイル名に日付 prefix は付けない（日付は親フォルダが持つ）。

| source | 着地パス |
|---|---|
| daily | `Inbox/{date}/daily/daily.md`（GCal + GTasks 朝 capture）|
| slack | `Inbox/{date}/slack/{channel}.md`（channel ごと日次ダイジェスト・DM は `dm-{counterpart}.md`）|
| code | `Inbox/{date}/code/code.md`（github-eod-capture）|
| mtgs | `Inbox/{capture-date}/mtgs/{provider}-{slug}.md`（Genspark は任意 adapter）|
| clippings | `Inbox/{date}/clippings/{slug}.md`（Web クリップ + hermes observation note）|
| chat-logs | `Inbox/{date}/chat-logs/{provider}-{slug}.md` |
| attachments | `Inbox/{date}/attachments/…`（slack 添付は `Inbox/{date}/attachments/slack/{channel}/…`）|

`Daily/{date}.md` が **唯一のハブ**：コアエージェントが `Inbox/{date}/*` を集約し、EOD に Wiki へ蒸留・分配する。hermes は `Daily/` や curated フォルダには書かない。

## 収録スキル

- `inbox-daily-capture/` — Calendar + Google Tasks を `Inbox/{date}/daily/daily.md` に生 capture（on-demand）。
  整理は コア側 [[.codex/skills/daily-briefing/SKILL.md]] が担当。
- `slack-capture/` — on-demand で指定日（通常は当日または前日）の Slack（ユーザー発言／@mention、public/private/DM）を
  `Inbox/{date}/slack/{channel}.md` に日次ダイジェスト化。**capture 専用・routing なし**。
- `genspark-mtg/` — 任意 Genspark adapter。capture 実行日の `Inbox/{date}/mtgs/genspark-{slug}.md` に raw transcript を置く。
- `github-eod-capture/` — `Maps/Code-Map.md` の全 repo の当日 commits/PRs/issues を `Inbox/{date}/code/code.md` に生 capture（on-demand）。
- `clippings-capture/` — Web 記事を `clippings/`、ChatGPT / Claude を `chat-logs/` に source-aware capture（Chrome 拡張 → gateway）。
- `google-auth/` — Hermes 共有 Google OAuth helper（Tasks と pull services 用。Calendar capture は ICS / optional `gws`）。
- `google-tasks/` — Google Tasks 取得スクリプト。
- `defuddle/` — URL→markdown 抽出ヘルパ（clippings-capture 内部・on-demand pull 用）。
- `genspark-slide/` — スライド生成の補助スキル（capture ではない）。

## 方針

- ここに置くスキルは **capture / 同期など Hermes 担当（`Inbox/{date}/{source}/` 内書き込みに限定）**。
- **routing しない**（channel→宛先マップ・DM 振り分け・auto-route は廃止）。curate（蒸留・分配）は コアエージェント + ユーザーの仕事。
- curated 領域の編集ロジックは置かない（それは コア側スキル）。
- 新規 cron は登録しない。既存環境に残る旧 cron は過渡期ジョブとして現状維持し、on-demand へ移行する。
- Python は原則 `uv`。Google helper だけは Hermes-installed package/token を再利用するため、明示した `HERMES_PYTHON` または conventional Hermes venv の interpreter を使う限定例外。
- 詳細は [[.codex/rules/agent-boundaries.md]] / [[.codex/rules/inbox-routing.md]]。
