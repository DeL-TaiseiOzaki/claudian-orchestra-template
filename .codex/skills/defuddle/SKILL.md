---
name: defuddle
description: Extract clean Markdown from a supplied web-page URL with Defuddle CLI. Do not use for URLs that already end in .md.
---

# Defuddle

Use Defuddle CLI to extract clean readable content from web pages. Prefer over WebFetch for standard web pages — it removes navigation, ads, and clutter, reducing token usage.

If not installed: `npm install -g defuddle`

## Usage

Always use `--md` for markdown output:

```bash
defuddle parse <url> --md
```

Save to file:

```bash
defuddle parse <url> --md -o content.md
```

Extract specific metadata:

```bash
defuddle parse <url> -p title
defuddle parse <url> -p description
defuddle parse <url> -p domain
```

## Output formats

| Flag | Format |
|------|--------|
| `--md` | Markdown (default choice) |
| `--json` | JSON with both HTML and markdown |
| (none) | HTML |
| `-p <name>` | Specific metadata property |

---

## このVaultでの運用（adaptation）

このスキルは kepano/obsidian-skills から導入。

> [!warning] 前提: 外部CLI `defuddle`（npm: `defuddle-cli`）が必要
> Web ページから本文 markdown を抽出してトークンを節約する。実行には CLI 導入が必要。

- 抽出した本文・画像は Vault ルートからの相対パスで保存する。
- 現状この環境では Bash が利用できないため、CLI 実行は Bash 有効化後に限る。
