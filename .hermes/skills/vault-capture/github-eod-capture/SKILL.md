---
name: github-eod-capture
description: "Capture same-day GitHub commits, pull requests, and issues for Code-Map repositories into Inbox for later core-agent distillation."
version: 1.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vault, capture, github, code, vault-capture]
    related_skills: [obsidian]
---

# github-eod-capture

Pipeline Step 5 専用の Hermes capture skill。`Maps/Code-Map.md` の repo の当日 commits / PRs / issues を取得し、`Inbox/{YYYY-MM-DD}/code/code.md` に raw capture として保存する。コアエージェントが Step 6 で distill する。

> [!important] 役割境界
> - このスキルは Step 5 の **raw capture 専用**。LLM による要約・言い換え・タグ推定・本文再構成・auto-route は行わない。
> - 書いてよいのは **`Inbox/{YYYY-MM-DD}/code/code.md` のみ**。`.codex/**`・`Daily/**`・`Wiki/**`・`Templates/**`・`Archive/**`・curated note body は変更しない（agent-boundaries.md §1 + inbox-routing.md §7）。
> - GitHub からの取得は **configured GitHub MCP のみ**。on-demand または既存 legacy cron の実行中に `terminal` / `execute_code` / `gh` / `git` / Python subprocess は使わない。
> - `Maps/Code-Map.md` の読み取りと `Inbox/{YYYY-MM-DD}/code/...` の書き込みは Hermes の通常 file I/O で行う。外部 repo 取得だけを GitHub MCP に限定する。

> [!important] Self-edit boundary (#37, 2026-06-07 確定)
> - このスキルは **自分の SKILL.md / references / config を autonomous に編集しない**。GitHub API / MCP の drift / 仕様変化を発見した場合は、対象 file を直接編集せず `Inbox/{YYYY-MM-DD}/clippings/hermes-obs-github-eod-capture.md` に observation/proposal note を新規作成する。
> - 必須 frontmatter：共通 6 fields（`title`, `type: capture`, `status: inbox`, `tags`, `created`, `updated`）+ `affected_path` / `observed_at` / `evidence` / `proposed_change` / `source: "hermes:observation:github-eod-capture:<ISO8601>"`
> - `.hermes/**` 配下のデータ／学習 file（cron / state JSON 等）の追記は例外（このスキルでは該当なし）。詳細は [[.codex/rules/inbox-routing.md]] §7。

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

`Daily/{date_str}.md` の exact source wikilink と `output_path` の存在を、外部取得より前に確認。

- **Daily に `[[Inbox/{date_str}/code/code.md]]` または拡張子なしの同等 link がある場合**：ownership handoff 済み。raw file が移動済みまたは不在でも、再作成・修復・追記せず `skipped: Daily handoff link preserved` で終了
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

- `[[Wiki/...]]` の wiki-link は無視（Markdown link ではない）
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
title: "GitHub EOD capture - {YYYY-MM-DD}"
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

> `type: capture` / `status: inbox` は [[.codex/rules/vault-metadata.md]] §4 の raw-capture path override。

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

## Cross-territory observation 規約

GitHub API / MCP 仕様 drift を発見しても control-plane を直接編集しない。代わりに `Inbox/{date}/clippings/hermes-obs-github-mcp.md` に observation note を新規作成し、共通 6 fields + `affected_path` / `observed_at` / `evidence` / `proposed_change` / `source` を入れる。

## 起動方法（on-demand）

**既定 = on-demand**：ユーザーが Daily ジョブリストからコアエージェントに指示し、コアが Hermes に委譲する。

### 手動 invoke コマンド

> `hermes chat -q` のスキル指定は `-s <skill>`（`--skill` / `--workdir` というフラグは無い）。vault ルートに cd してから呼ぶ。日本語 Windows では呼び出し前に `PYTHONUTF8=1` を設定する（cp932 デコード起因の出力欠落防止 → [[.codex/skills/hermes-query/SKILL.md]]）。

```bash
cd "<vault root>"
hermes chat -q "Maps/Code-Map.md に載っている GitHub リポジトリについて、当日 00:00 JST から現在までの commits / PRs / issues を GitHub MCP で取得し、Inbox/{YYYY-MM-DD}/code/code.md に raw capture として保存する（日付つき親フォルダがあり、ファイル名は固定 code.md）。外部取得前に Daily の exact source wikilink と既存ファイルを確認し、どちらかがあれば再作成・修復・上書きしない。" -s github-eod-capture -Q --source core-agent
```

> 既存環境の旧 GitHub EOD cron は過渡期ジョブとして現状維持する。新規登録・変更はせず、Daily ジョブリストから on-demand で実行する。

## 関連

- [[.codex/rules/daily-operations.md]] §0 Step 5
- [[.codex/rules/inbox-routing.md]] §2（GitHub MCP source 行）
- [[.codex/rules/agent-boundaries.md]] §1（control-plane boundary）
- [[.codex/rules/vault-metadata.md]]
- [[Maps/Code-Map.md]] 追跡ブランチ規則
- [[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]] / [[.hermes/skills/vault-capture/slack-capture/SKILL.md]]（idiom 参考）
- `references/code-map-parsing.md`
- `references/github-mcp-fallbacks.md`
