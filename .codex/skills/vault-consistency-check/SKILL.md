---
name: vault-consistency-check
description: Run light or full vault consistency checks and update only today's Daily consistency section. Use for 「vault 整合性チェック」.
---

# Vault Consistency Check

## 目的

`vault-consistency-check` は、Daily の `## 🔍 整合性チェック` セクションだけを更新する夜間レポート用 skill である。
single-writer 制約を守るため、対象は **当日 root Daily の 1 section のみ** に限定する。

- `check_vault_consistency.py` は read-only で 7 checks を走らせ、Markdown か JSON を stdout に出す。
- `write_daily_section.py` はその Markdown section を受け取り、当日 Daily の該当 section だけを置換する。
- auto-fix はしない。提案は出すが、変更は人間か別 skill が行う。

## 使用場面

- ジョブリストの「vault 整合性チェック」指示で／EOD レビューを閉じるとき
- `light` で当日差分だけを素早く確認したいとき
- `full` で週末に vault 全体を洗いたいとき
- `Maps/Code-Map.md` や当日 Daily Tasks の整合性を手動で再確認したいとき

## 実行フロー

### Step 1: mode を決める

- 平日夜の定常実行は `light`
- 週末の定常実行は `full`
- 手動実行では、目的が当日差分確認なら `light`、全体棚卸しなら `full`

### Step 2: check script を実行する

vault root で次を実行する。

```powershell
uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06
```

- JSON が必要なら `--json`
- Hermes を使う remote checks を有効化したいときだけ `--enable-remote`
- `--vault-root` は通常不要。既定では script 位置から vault root を逆算する

### Step 3: Daily に書き戻す

check script の Markdown 出力をそのまま writer に流す。

```powershell
uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06 `
| uv run python .codex/skills/vault-consistency-check/scripts/write_daily_section.py --date 2026-06-06
```

- Daily が存在すれば `## 🔍 整合性チェック` を完全置換する
- 既存 section が無ければ `## 🌙 夜の振り返り` ブロックの後ろに挿入する
- Daily が無ければ writer は stderr に `WARN [Daily missing] ...` を出して終了する

## モード

| mode | 対象 | remote checks | 目標時間 |
|---|---|---|---|
| `light` | 当日 touched-today の note を中心に 1, 2 を縮小実行。3, 6 は常時。4 は当日 Daily に Tasks 節と内容がある場合のみ。5 は `Maps/Code-Map.md` が touched-today の場合のみ。7 は (a) root registry + (b) required dirs のみ。 | 既定 off。必要時のみ `--enable-remote` | 30 秒以内 |
| `full` | vault 全体の note ドメインを対象に 7 checks 全面実行。7 は (a)–(d) 全サブチェック（(c) 非 md 配置 / (d) 空 dir も走る）。 | 既定 off。必要時のみ `--enable-remote` | 制限なし |

`touched-today` は次の union で決まる。

- `git diff --name-only HEAD@{1.day.ago} HEAD`
- fallback: `git log --since=1.day.ago --name-only --pretty=format:`
- vault root 配下で mtime が直近 24 時間の file

## 出力契約

出力形式の詳細は [[.codex/skills/vault-consistency-check/references/output-format.md]] を参照する。

- 先頭見出しは必ず `## 🔍 整合性チェック`
- summary 行は `WARN: N, ERROR: N, OK: N (checked: 7, mode: M, ran: HH:MM)`
- findings は `ERROR > WARN > OK`、同一 tag 内は `check-name -> path`
- tag と check 名は英語固定（次節の 7 個）、説明と提案は日本語

## 境界

この skill が書いてよいのは **当日 root Daily の `## 🔍 整合性チェック` セクションだけ** である。

- `check_vault_consistency.py` は **絶対に file write しない**
- `write_daily_section.py` は他 file を作らない
- 他 section を触らない
- `Daily/{YYYY-MM-DD}.md` が無い場合は `WARN [Daily missing] ...` を stderr に出して exit する
- findings はすべて「提案のみ・auto-fix なし」で終わる

## 起動方法（ユーザー確定 2026-06-07：manual trigger model）

コア CLI のセッション内 scheduler は永続性を保証しないため、本 skill は **手動 trigger** を既定とする。この template から Hermes cron や OS scheduled task を新規登録しない。

### 既定（手動 trigger）

コアセッション中に明示的に呼び出す：

- skill 呼び出し：`/vault-consistency-check`（あるいは「vault の整合性チェックして」とお願い）
- ターミナル直叩き（vault root で）：

```powershell
# light（既定）
uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-07 `
  | uv run python .codex/skills/vault-consistency-check/scripts/write_daily_section.py --date 2026-06-07

# full（週末などの棚卸し）
uv run python .codex/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-07 `
  | uv run python .codex/skills/vault-consistency-check/scripts/write_daily_section.py --date 2026-06-07
```

Step 6（夜の振り返り）の流れの最後に手動で叩くのを想定。github-eod / `inbox-aggregate` を回した後（ジョブリスト順次）に実行するのが推奨。

### 既存 scheduled task の扱い

移行前から動いている Hermes cron / Windows Task Scheduler job は過渡期に限って維持できる。新規作成・変更はせず、Daily job list からの on-demand 実行へ移行する。既存 job を削除する場合は destructive operation としてユーザー承認を得る。

## 関連

- Hermes live query: [[.codex/skills/hermes-query/SKILL.md]]
- Daily 作成元: [[.codex/skills/daily-briefing/SKILL.md]]
- Archive 運用: [[.codex/skills/vault-archive/SKILL.md]]
- 日次パイプライン: [[.codex/rules/daily-operations.md]]

## 実装メモ

7 checks は次の固定名を使う。

1. `Broken wikilinks`
2. `Frontmatter schema violation`
3. `Inbox stagnation`
4. `Today Tasks drift`
5. `Code-Map repo health`
6. `Submodule dirty / commit drift`
7. `Structure drift`

remote checks の既定は off である。

- `Today Tasks drift` は Hermes で live Google Tasks を JSON 取得するときだけ remote
- `Code-Map repo health` は Hermes で GitHub URL health を JSON 取得するときだけ remote
- timeout や malformed JSON は check 単位で `WARN` に倒し、run 全体は継続する

`Structure drift`（Check #7）はディレクトリ構造の drift を検査する（正本は [[AGENTS.md]] §1 のドメイン構成と dependency-free な `references/schema_rules.json`）。

- (a) root registry 外の dir [WARN] と (b) 必須 dir の物理欠落 [ERROR] は light / full 両方で走る
- (c) 非 md ファイルの配置違反 [WARN] と (d) 空 dir の `.gitkeep` 欠落 [WARN] は full のみ
- 期待 dir / system dir / scan root / 非 md 許容ルールは `references/schema_rules.json` の `structure_*` キーが単一の正（submodule 除外は `.gitmodules` を優先し、無ければ `structure_submodule_excludes` に fallback）
- frontmatter 検査は curated notes に加えて `Templates/**` と `.codex/docs/knowledges/**` を対象にする（`README.md` / `AGENTS.md` は除外）。
- `Inbox/{YYYY-MM-DD}/**` と `Wiki/sources/**` は raw capture schema、`.codex/docs/knowledges/**` は knowledge schema を適用する。source-first Inbox は許容しない。
- schema と frontmatter の読み込みは Python stdlib のみを使う。JSON schema 欠落・破損時に埋め込み defaults へ fallback しない。

回帰テスト:

```bash
uv run python -m unittest discover -s .codex/skills/vault-consistency-check/tests -v
```
- remote 不要・read-only（他 check 同様、auto-fix なし）
