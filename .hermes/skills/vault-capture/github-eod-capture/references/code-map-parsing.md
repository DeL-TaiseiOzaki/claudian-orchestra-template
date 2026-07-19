# Code-Map.md parser spec

[[.hermes/skills/vault-capture/github-eod-capture/SKILL.md]] §3 で参照される `Maps/Code-Map.md` の parser 契約。

## Goal

`Maps/Code-Map.md` の Markdown link から **GitHub repo + 追跡ブランチ tuple** を deterministic に抽出する。

## URL 判定 regex

```regex
^https://github\.com/([^/\s)#]+)/([^/\s)#]+?)(?:\.git)?$
```

- `owner/repo` ぴったりにマッチ
- 末尾 `.git` は除去
- query string / fragment / trailing slash がついた URL は **不一致**（誤登録防止）

## Branch override 判定 regex（label 末尾のみ）

```regex
^(.+?) \(([^()]+)\)$
```

- `[name (branch)](url)` 形式の label を分解
- 末尾の `(...)` 全体を branch suffix とみなす
- 全角括弧 `（branch）` は override **しない**（半角のみ）

## Branch 解決ルール

| label 表記 | 追跡ブランチ |
|---|---|
| `[repo-name](url)` | 既定 `main` |
| `[repo-name (branch)](url)` | 括弧内のブランチ名 |
| 同じ repo を 2 行で重複 | 各行を別 tuple として保持（複数 branch 追跡） |

`main` 取得失敗時のみ `get repository` → `default_branch` retry（SKILL.md §4 参照）。

## Dedupe ルール

- key：`(owner, repo, branch)` の **完全一致** tuple
- 順序：first-occurrence order を保持（parser が見つけた順）

## 除外対象

- `[[Wiki/...]]` 形式の Wiki-link（Markdown link ではないので URL regex に当たらない）
- `https://github.com/owner/repo/issues/123` のような sub-path
- `https://github.com/orgs/owner` のような organisation URL
- query string / fragment / trailing slash 付き
- 全角括弧 `（...）` の branch suffix

## Fixture 例

例えば [[Maps/Code-Map.md]] に以下の repo が列挙されている場合、parse 結果は次の 6 tuple になるのが期待値：

| # | owner | repo | branch |
|---|---|---|---|
| 1 | your-org | your-tool | main |
| 2 | your-org | your-app-api | main |
| 3 | your-org | your-app-web | main |
| 4 | your-org | your_legacy_lib | main |
| 5 | your-org | your-app-api | develop |
| 6 | your-research-org | your-research-repo | main |

> Code-Map に載っていない repo は巡回対象外。

## E2E parser verification

`scripts/parse_code_map.py`（optional, manual-only）を `uv run` で実行して上記 fixture と一致するか確認できる。cron では使わない（self-contained logic を Hermes 内部で実装）。

## 関連

- [[.hermes/skills/vault-capture/github-eod-capture/SKILL.md]] §3 / §4
- [[Maps/Code-Map.md]] 追跡ブランチ規則
