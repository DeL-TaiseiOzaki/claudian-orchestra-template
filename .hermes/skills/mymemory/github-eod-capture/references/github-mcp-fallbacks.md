# GitHub MCP tool fallback table

[[.hermes/skills/mymemory/github-eod-capture/SKILL.md]] §1 で参照される、GitHub MCP の tool 名前提を環境差分許容にするための fallback 表。

## 原則

skill は **「操作 = capability」だけを宣言**し、具体的な MCP tool 名は固定前提にしない。Hermes 実行時に configured MCP surface を `ToolSearch` 相当で確認し、表の左列に合う右列を使う。

## 必要 capability と fallback

| 必要な操作 | 第一候補 tool 名（推定） | Fallback A | Fallback B |
|---|---|---|---|
| List commits | `list_commits` / `repos/list_commits` | `get_commits` | `search_commits`（branch=resolved_branch, since=ISO8601） |
| List pull requests | `list_pull_requests` | `get_pulls` | `search_issues` with `repo:owner/repo is:pr updated:>=...` |
| List issues | `list_issues` | `get_issues` | `search_issues` with `repo:owner/repo is:issue updated:>=...` |
| Get repository | `get_repository` / `get_repo` | `repos/get` | （必要なら `search_repositories` で 1 件絞り） |
| Search issues | `search_issues` | `search` with `q=...` | （fallback の終端） |

## tool ごとに必須引数

- `list commits`：`owner`, `repo`, `ref=branch`, `since=ISO8601_UTC`
- `list pull requests`：`owner`, `repo`, `state="all"`, `sort="updated"`, `direction="desc"`
- `list issues`：`owner`, `repo`, `state="all"`, `since=ISO8601_UTC`, `sort="updated"`, `direction="desc"`
- `get repository`：`owner`, `repo`
- `search issues`：`q="repo:{owner}/{repo} is:{pr|issue} updated:>={today_start_jst}"`

## エラー区分と handle

| エラー応答 | 区分 | Hermes の振る舞い |
|---|---|---|
| 404 (repo not found) | `deleted_or_renamed` | 当該 repo を per-repo 失敗として記録 → 次の repo へ |
| 403 (no access) | `private_inaccessible` | 同上 |
| 403 / `secondary_rate_limit` / `abuse-rate-limit` | rate limit | exponential backoff（1s → 2s → 4s → 8s）、最大 3 retry |
| 5xx / timeout / network | transient | 同上の backoff、最大 3 retry |
| branch not found（`main` だけ） | branch retry | `get repository` → `default_branch` で再試行（SKILL.md §4） |
| その他 | failure | per-repo 失敗、報告に詳細を残す |

## Page size

- 既定：可能なら max（多くは `per_page=100`）
- 11+ repo × 3 種でも最大 36 calls の見込み（11 + 11 + 11 = 33、failure retry 込みで ~50）

## Search fallback の構文例

```
# PR
repo:your-org/proj-a-repo is:pr updated:>=2026-06-06T00:00:00+09:00

# Issue
repo:your-org/proj-a-repo is:issue updated:>=2026-06-06T00:00:00+09:00
```

## 関連

- [[.hermes/skills/mymemory/github-eod-capture/SKILL.md]] §5
- [[.claude/docs/research/github-eod-capture-design.md]] Codex 設計（Risks セクション）
