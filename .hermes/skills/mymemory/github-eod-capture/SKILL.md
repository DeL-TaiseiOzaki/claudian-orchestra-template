---
name: github-eod-capture
description: "Use to capture same-day GitHub commits, pull requests, and issues for repositories listed in Maps/Code-Map.md into Inbox/{YYYY-MM-DD}/code/code.md as raw input for later Claude distillation (Step 6). Intended to be invoked on-demand when the user issues a 取り込み instruction (typically from the Daily-note ジョブリスト, e.g. after 21:30). May also run from a cron if registered, but on-demand is the primary mode."
version: 1.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vault, capture, github, code, cron, mymemory]
    related_skills: [obsidian]
---

# github-eod-capture

Pipeline Step 5（[[.claude/rules/daily-operations.md]] §0）専用の Hermes capture skill。the user が指示したタイミングで実行（既定）／cron で時間起動も可（任意）。`Maps/Code-Map.md` に列挙された全 repo の **指定ブランチの当日（00:00 JST 〜 now）の commits / PRs / issues** を GitHub MCP で取得し、`Inbox/{YYYY-MM-DD}/code/code.md`（日付つき親フォルダ配下・ファイル名は固定 `code.md`）に raw capture として保存する。Claude は Step 6 で distill する。

> [!important] 役割境界
> - このスキルは Step 5 の **raw capture 専用**。LLM による要約・言い換え・タグ推定・本文再構成・auto-route は行わない。
> - 書いてよいのは **`Inbox/{YYYY-MM-DD}/code/code.md` のみ**。`.claude/**`・`Daily/**`・`Research/**`・`Templates/**`・`Archive/**`・curated note body は変更しない（agent-boundaries.md §1 + inbox-routing.md §7）。
> - GitHub からの取得は **configured GitHub MCP のみ**。cron 実行中に `terminal` / `execute_code` / `gh` / `git` / Python subprocess は使わない（cron context BLOCK と vault path `マ` 文字問題の両方を回避）。
> - `Maps/Code-Map.md` の読み取りと `Inbox/{YYYY-MM-DD}/code/...` の書き込みは Hermes の通常 file I/O で行う。外部 repo 取得だけを GitHub MCP に限定する。

> [!important] Self-edit boundary (#37, 2026-06-07 確定)
> - このスキルは **自分の SKILL.md / references / config を autonomous に編集しない**。GitHub API / MCP の drift / 仕様変化を発見した場合は、対象 file を直接編集せず `Inbox/{YYYY-MM-DD}/clippings/hermes-obs-github-eod-capture.md` に observation/proposal note を新規作成する。
> - 必須 frontmatter：`affected_path` / `observed_at` / `evidence` / `proposed_change` / `source: "hermes:observation:github-eod-capture:<ISO8601>"`
> - `.hermes/**` 配下のデータ／学習 file（cron / state JSON 等）の追記は例外（このスキルでは該当なし）。詳細は [[.claude/rules/inbox-routing.md]] §7。

## 前提・パス解決

- `workdir` は Vault root を指している前提
- 入力ファイル：`Maps/Code-Map.md`
- 出力ファイル：`Inbox/{YYYY-MM-DD}/code/code.md`
- 日付境界は必ず **Asia/Tokyo**
  - `today_start_jst = YYYY-MM-DDT00:00:00+09:00`
  - `today_end_jst = now`
  - API param `today_start_utc = today_start_jst - 9h`
- GitHub MCP の tool 名は環境差分を許容（固定名前提にしない）。次の操作ができる tool を使う：
  - `list commits` for `(owner, repo, ref=branch, since=ISO8601_UTC)`
  - `list pull requests` for `(owner, repo, state="all", sort="updated", direction="desc")`
  - `list issues` for `(owner, repo, state="all", since=ISO8601_UTC, sort="updated", direction="desc")`
  - `get repository` for default-branch detection
  - `search issues` fallback for `repo:owner/repo is:pr ...` / `is:issue ...`

> 環境固有の MCP tool 命名 fallback 表は `references/github-mcp-fallbacks.md`。

## 手順

### 1. 日付・出力先決定

- `today_start_jst`, `today_end_jst`, `today_start_utc`, `date_str`, `output_path = Inbox/{date_str}/code/code.md` を決定
- `fetched_at` は ISO8601 `+09:00` で保持

### 2. 既存ファイル検出（冪等性）

`output_path` が既に存在するか確認。

- **存在する場合**：上書きも merge もせず、そのまま終了。報告に `skipped: existing file preserved` を含める
- 存在しない場合：手順 3 以降に進む

### 3. Code-Map.md parse

`Maps/Code-Map.md` を読み、Markdown link だけを走査。

**URL 判定 regex**：

```regex
^https://github\.com/([^/\s)#]+)/([^/\s)#]+?)(?:\.git)?$
```

**Branch override 判定 regex**（label 末尾のみ）：

```regex
^(.+?) \(([^()]+)\)$
```

**抽出規則**：

- `[[Work/...]]` の wiki-link は無視（Markdown link ではない）
- `https://github.com/owner/repo` 以外の path / query / fragment / trailing slash を含む URL は無視
- label に branch suffix が無ければ branch は `main`（[[Maps/Code-Map.md]] の追跡ブランチ規則と整合）
- 全角括弧 `（branch）` は branch override **しない**（半角のみ）
- Dedupe は `(owner, repo, branch)` tuple で first-occurrence order を保持

詳細 fixture / canonical sample は `references/code-map-parsing.md` を参照。

### 4. Branch 解決

各 repo について tracked branch を決定：

1. label override があればそれを優先
2. 無ければ `main`
3. `list commits` が `main` だけ branch-not-found で失敗した場合に限り、`get repository` を呼んで `default_branch` を取得し retry
4. retry 成功後はその branch 名を以後の表示と取得に使う

### 5. GitHub MCP 取得

各 repo の同日データを取得。ページサイズは指定できるなら最大値を使う。

**Commits**：

- resolved branch に対して `since=today_start_utc` を渡して全ページ取得
- ソート：API 既定（後で `committed_at desc` に正規化）

**PRs**：

- `state="all", sort="updated", direction="desc"` で取得
- フィルタ：`base.ref == resolved_branch` かつ `updated_at >= today_start_utc OR created_at >= today_start_utc OR merged_at >= today_start_utc`
- `updated_at < today_start_utc` に到達したら以後のページ取得を打ち切り（early-stop）

**Issues**：

- `state="all", since=today_start_utc, sort="updated", direction="desc"` で取得
- フィルタ：`pull_request == null` のみ（PR を除外）
- `updated_at < today_start_utc` に到達したら early-stop

**Fallback**（repo-local の list 系が無い MCP 構成）：

- PRs：`search issues` で `repo:owner/repo is:pr updated:>=YYYY-MM-DDT00:00:00+09:00`
- Issues：`repo:owner/repo is:issue updated:>=YYYY-MM-DDT00:00:00+09:00`

### 6. Render 正規化

- Commits：`committed_at desc`
- PRs / Issues：`updated_at desc`
- commit message：改行正規化後、最初の空行までを first paragraph として使う
- commit SHA：先頭 7 桁
- timestamp：すべて JST に変換、`YYYY-MM-DD HH:mm JST` で表示
- Issue labels：label 名を `, ` で join、0 件なら `no-labels`
- 長い title は切り詰めない
- 0 件の subsection は `- なし`

### 7. 書き出し

`output_path` に **一度だけ書き込み**。書き込み後は auto-route しない。

報告は簡潔に：少なくとも `created path`、`repo count`、`skipped or created`、`per-repo counts or failures` を含める。

### 8. Rate limit / transient error

- best-effort
- `secondary rate limit` / `abuse-rate-limit` 相当の応答 → exponential backoff で再試行
- 日次件数は通常 5000 req/h を大きく下回る前提（11+ repo × 3 種 ≈ 36 calls）

## Frontmatter template

```yaml
---
source: "github:eod:{YYYY-MM-DD}"
type: "capture"
status: "inbox"
repos: ["owner/repo (branch)", "owner2/repo2 (branch2)"]
fetched_at: "{YYYY-MM-DDTHH:mm:ss+09:00}"
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
tags: ["github", "capture", "code"]
---
```

> `type: capture` / `status: inbox` は [[.claude/rules/vault-metadata.md]] の標準 enum 外。本 skill が `Inbox/{YYYY-MM-DD}/code/` 専用 owner として override する（slack-capture / genspark-mtg と同様の Inbox-source 命名規則）。vault-metadata.md に正式登録するかは Claude 側で判断。

## Body template

```markdown
## owner/repo (branch)

### Commits
- `abc1234` First paragraph of commit message — alice 2026-06-06 20:41 JST https://github.com/owner/repo/commit/abc1234

### PRs
- #123 [merged] Add branch override support — bob 2026-06-06 19:58 JST https://github.com/owner/repo/pull/123

### Issues
- #45 [open] Follow up on parser edge case — carol bug, priority/high 2026-06-06 18:10 JST https://github.com/owner/repo/issues/45
```

空の subsection は次の形に固定：

```markdown
### Commits
- なし

### PRs
- なし

### Issues
- なし
```

## Cross-territory observation 規約（#32 #29 と整合）

GitHub API / MCP 仕様 drift（field rename・新フィールド出現・rate limit ポリシー変化など）を発見しても、**`.claude/skills/` / `.claude/rules/` / `Maps/Code-Map.md` を直接編集してはならない**。代わりに `Inbox/{date}/clippings/hermes-obs-github-mcp.md` に observation/proposal note を新規作成し、必須 frontmatter（`affected_path` / `observed_at` / `evidence` / `proposed_change` / `source: hermes:observation:github-mcp:<ISO8601>`）を入れる。

## 起動方法（on-demand 既定 / cron は任意）

**既定 = on-demand**：the user が Daily ノートの `## 🤖 ジョブリスト` を見て「<該当 job> やって」と Claude に指示 → Claude が hermes に CLI で委譲（[[.claude/skills/hermes-query/SKILL.md]]）。

### 手動 invoke コマンド（PowerShell）

> ⚠️ **2026-06-16 修正**：`--skill` / `--workdir` は無効（`hermes chat -q` の実際のフラグは `-s SKILLS` / cwd）。Set-Location で vault に入ってから呼ぶ。`$env:PYTHONUTF8 = '1'` は cp932 文字化け回避（[[.claude/docs/knowledges/python/windows-cp932-stdout-default.md]]）。

```powershell
# PowerShell（推奨・cp932 落とし穴回避のため $env:PYTHONUTF8 必須）
$env:PYTHONUTF8 = '1'
Set-Location "<vault root>"
hermes chat -q "Maps/Code-Map.md に載っている GitHub リポジトリについて、当日 00:00 JST から現在までの commits / PRs / issues を GitHub MCP で取得し、Inbox/{YYYY-MM-DD}/code/code.md に raw capture として保存する（日付つき親フォルダがあり、ファイル名は固定 code.md）。既存ファイルがあれば上書きしない。" -s github-eod-capture -Q --source claude-code
```

### Cron 登録（任意 / メインPC のみ・現状は維持）

> ⚠️ **2026-06-16 方針変更**：cron による定期起動は **任意**。既存の cron job（21:30 想定）が稼働中なら維持してよいが、新規登録は不要（on-demand が既定）。下記コマンドは参照用に残す。

```bash
hermes cron create "30 21 * * *" "Maps/Code-Map.md に載っている GitHub リポジトリについて、当日 00:00 JST から現在までの commits / PRs / issues を GitHub MCP で取得し、Inbox/{YYYY-MM-DD}/code/code.md に raw capture として保存する（日付つき親フォルダがあり、ファイル名は固定 code.md）。既存ファイルがあれば上書きしない。" --name github-eod-evening --skill github-eod-capture --workdir "<vault root>"
```

> argparse quirk：positional `prompt` は schedule の直後、flag より前に置く（[[Meta/rearchitecture/status.md]] §4.7 参照）。

## 関連

- [[.claude/rules/daily-operations.md]] §0 Step 5
- [[.claude/rules/inbox-routing.md]] §2（GitHub MCP source 行）
- [[.claude/rules/agent-boundaries.md]] §1（control-plane boundary）
- [[.claude/rules/vault-metadata.md]]
- [[Maps/Code-Map.md]] 追跡ブランチ規則
- [[.hermes/skills/mymemory/genspark-mtg/SKILL.md]] / [[.hermes/skills/mymemory/slack-capture/SKILL.md]]（idiom 参考）
- `references/code-map-parsing.md`
- `references/github-mcp-fallbacks.md`
- Codex design 原本：[[.claude/docs/research/github-eod-capture-design.md]]
