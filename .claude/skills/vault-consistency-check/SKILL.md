---
name: vault-consistency-check
description: On-demand vault consistency reporting for the your-vault vault that writes or replaces only the `## 🔍 整合性チェック` section in today's root Daily note after running eight scoped checks in light or full mode; run from the Daily job list ('vault 整合性チェック') or manually, in light or full mode.
---

# Vault Consistency Check

## 目的

`vault-consistency-check` は、Daily の `## 🔍 整合性チェック` セクションだけを更新する夜間レポート用 skill である。
single-writer 制約を守るため、対象は **当日 root Daily の 1 section のみ** に限定する。

- `check_vault_consistency.py` は read-only で 8 checks を走らせ、Markdown か JSON を stdout に出す。
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
uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06
```

- JSON が必要なら `--json`
- Hermes を使う remote checks を有効化したいときだけ `--enable-remote`
- `--vault-root` は通常不要。既定では script 位置から vault root を逆算する

### Step 3: Daily に書き戻す

check script の Markdown 出力をそのまま writer に流す。

```powershell
uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-06 `
| uv run python .claude/skills/vault-consistency-check/scripts/write_daily_section.py --date 2026-06-06
```

- Daily が存在すれば `## 🔍 整合性チェック` を完全置換する
- 既存 section が無ければ `## 🌙 夜の振り返り` ブロックの後ろに挿入する
- Daily が無ければ writer は stderr に `WARN [Daily missing] ...` を出して終了する

## モード

| mode | 対象 | remote checks | 目標時間 |
|---|---|---|---|
| `light` | 当日 touched-today の note を中心に 1, 2, 6 を縮小実行。3, 7 は常時。4 は当日 Daily に Tasks 節と内容がある場合のみ。5 は `Maps/Code-Map.md` が touched-today の場合のみ。8 は (a) root registry + (b) required dirs のみ。 | 既定 off。必要時のみ `--enable-remote` | 30 秒以内 |
| `full` | vault 全体の note ドメインを対象に 8 checks 全面実行。8 は (a)–(d) 全サブチェック（(c) 非 md 配置 / (d) 空 dir も走る）。 | 既定 off。必要時のみ `--enable-remote` | 制限なし |

`touched-today` は次の union で決まる。

- `git diff --name-only HEAD@{1.day.ago} HEAD`
- fallback: `git log --since=1.day.ago --name-only --pretty=format:`
- vault root 配下で mtime が直近 24 時間の file

## 出力契約

出力形式の詳細は [[.claude/skills/vault-consistency-check/references/output-format.md]] を参照する。

- 先頭見出しは必ず `## 🔍 整合性チェック`
- summary 行は `WARN: N, ERROR: N, OK: N (checked: 8, mode: M, ran: HH:MM)`
- findings は `ERROR > WARN > OK`、同一 tag 内は `check-name -> path`
- tag と check 名は英語固定（次節の 8 個）、説明と提案は日本語

## 境界

この skill が書いてよいのは **当日 root Daily の `## 🔍 整合性チェック` セクションだけ** である。

- `check_vault_consistency.py` は **絶対に file write しない**
- `write_daily_section.py` は他 file を作らない
- 他 section を触らない
- `Daily/{YYYY-MM-DD}.md` が無い場合は `WARN [Daily missing] ...` を stderr に出して exit する
- findings はすべて「提案のみ・auto-fix なし」で終わる

## 起動方法（the user 確定 2026-06-07：manual trigger model）

Claude harness の `CronCreate(durable: true)` は Obsidian 環境では session-only にしかならず、Claude セッション終了で消える（status.md #33）。よって本 skill は **手動 trigger** を既定とする。Cron による永続自動実行は OS 側で別途組む（オプション、後述）。

### 既定（手動 trigger）

Claude セッション中に明示的に呼び出す：

- skill 呼び出し：`/vault-consistency-check`（あるいは「vault の整合性チェックして」とお願い）
- ターミナル直叩き（vault root で）：

```powershell
# light（既定）
uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode light --date 2026-06-07 `
  | uv run python .claude/skills/vault-consistency-check/scripts/write_daily_section.py --date 2026-06-07

# full（週末などの棚卸し）
uv run python .claude/skills/vault-consistency-check/scripts/check_vault_consistency.py --mode full --date 2026-06-07 `
  | uv run python .claude/skills/vault-consistency-check/scripts/write_daily_section.py --date 2026-06-07
```

Step 6（夜の振り返り）の流れの最後に手動で叩くのを想定。github-eod / aggregate 群を回した後（ジョブリスト順次）に実行するのが推奨。

### オプション：Windows Task Scheduler で恒久自動化

Claude も Hermes も使わず OS 側で永続スケジューリングしたい場合：

```powershell
# 平日 light
schtasks /create /tn "VaultConsistencyCheck_Light" `
  /tr "uv run python `"<vault-root>\.claude\skills\vault-consistency-check\scripts\check_vault_consistency.py`" --mode light | uv run python `"<vault-root>\.claude\skills\vault-consistency-check\scripts\write_daily_section.py`"" `
  /sc weekly /d MON,TUE,WED,THU,FRI /st 21:57 /ru "%USERNAME%"

# 週末 full
schtasks /create /tn "VaultConsistencyCheck_Full" `
  /tr "uv run python `"<vault-root>\.claude\skills\vault-consistency-check\scripts\check_vault_consistency.py`" --mode full | uv run python `"<vault-root>\.claude\skills\vault-consistency-check\scripts\write_daily_section.py`"" `
  /sc weekly /d SAT,SUN /st 21:57 /ru "%USERNAME%"
```

- date 引数を省略すると script は実行日 (JST) を自動採用
- pipe (`|`) を `schtasks /tr` 内で使うため、文字列全体をクオートで囲み内側の引用は backtick で escape
- 確認：`schtasks /query /tn "VaultConsistencyCheck_Light"`
- 削除：`schtasks /delete /tn "VaultConsistencyCheck_Light" /f`

## 関連

- 設計: [[.claude/docs/research/vault-consistency-check-design.md]]
- Hermes live query: [[.claude/skills/hermes-query/SKILL.md]]
- Daily 作成元: [[.claude/skills/daily-briefing/SKILL.md]]
- Archive 運用: [[.claude/skills/vault-archive/SKILL.md]]
- 日次パイプライン: [[.claude/rules/daily-operations.md]]

## 実装メモ

8 checks は次の固定名を使う。

1. `Broken wikilinks`
2. `Frontmatter schema violation`
3. `Inbox stagnation`
4. `Today Tasks drift`
5. `Code-Map repo health`
6. `Work logs project field`
7. `Submodule dirty / commit drift`
8. `Structure drift`

remote checks の既定は off である。

- `Today Tasks drift` は Hermes で live Google Tasks を JSON 取得するときだけ remote
- `Code-Map repo health` は Hermes で GitHub URL health を JSON 取得するときだけ remote
- timeout や malformed JSON は check 単位で `WARN` に倒し、run 全体は継続する

`Structure drift`（Check #8）はディレクトリ構造の drift を検査する（[[Meta/rearchitecture/directory-structure-strategy.md]] §6）。

- (a) root registry 外の dir [WARN] と (b) 必須 dir の物理欠落 [ERROR] は light / full 両方で走る
- (c) 非 md ファイルの配置違反 [WARN] と (d) 空 dir の `.gitkeep` 欠落 [WARN] は full のみ
- 期待 dir / system dir / scan root / 非 md 許容ルールは `references/schema_rules.yaml` の `structure_*` キーが単一の正（submodule 除外は `.gitmodules` を優先し、無ければ `structure_submodule_excludes` に fallback）
- remote 不要・read-only（他 check 同様、auto-fix なし）
