# Knowledge categories

Top-level dirs under `.codex/docs/knowledges/`. Add a new dir if a learning genuinely doesn't fit; don't over-fit existing categories.

| Category | Scope | Examples |
|---|---|---|
| `hermes/` | hermes daemon / cron / skills / MCP integration の固有挙動 | env passthrough, cron argparse, gateway restart, scheduled task quirks |
| `claude-cli/` | Claude Code harness（Obsidian 環境）の挙動 | `CronCreate durable` 不発、deferred tool loading、context window 制約 |
| `mcp/` | MCP プロトコル / server 一般 | stdio transport、env interpolation、tool name 命名規則 |
| `git/` | git workflow / commit / branch | submodule update, LF/CRLF, sed -i on Windows |
| `vault/` | Obsidian / vault 構造の慣習 | single-writer per file、`Inbox/**` lifecycle、frontmatter override |
| `architecture/` | 多エージェント orchestration / policy 設計 | markdown callout の限界、observation-note pattern、carve-out 設計 |
| `codex/` | Codex CLI 固有挙動（sandbox, config.toml, vendored skills） | sandbox 書き込み制約、config.toml 設定、vendored skills 連携の gotcha |
| `python/` | Python / `uv` / dependency 周り | encoding（Windows cp932）、`uv run` パス解決、stdio reconfigure |

## カテゴリの追加ルール

新カテゴリ追加は気軽に。ただし：

1. **対象が広い一般概念**にする — `slack-capture-bug` のような skill 固有 dir は作らない（その学びは `hermes/` か該当 skill SKILL.md の Pitfalls section へ）
2. **3 件以上溜まりそうか** 自問する — 1 件しか入れる予定がないなら既存カテゴリの subdomain で済ます
3. dir 追加と同時に `README.md` MOC のカテゴリ表に行追加

## 推奨タグ

frontmatter `tags:` の粒度（category と重複可）:

- category: 上記の dir 名
- subdomain: `cron` / `gateway` / `mcp` / `auth` / `encoding` etc.
- tool / product: `hermes` / `npx` / `modelcontextprotocol-server-github` / `windows`
- nature: `gotcha` / `quirk` / `design-limit` / `postmortem`

例：`tags: ["hermes", "mcp", "env-passthrough", "gotcha"]`
