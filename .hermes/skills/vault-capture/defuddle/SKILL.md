---
name: defuddle
description: Extract clean markdown content from a URL via the Defuddle CLI (`defuddle parse <url> --md`), stripping navigation/ads/clutter. Used internally by clippings-capture when only a URL is provided (no body), and on-demand when Claude Code requests a clean fetch via `hermes chat -q`. Returns markdown to stdout for the caller; never writes directly to curated paths.
version: 1.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vault, capture, web, defuddle, vault-capture]
    related_skills: [clippings-capture]
---

# defuddle

任意 URL を Defuddle CLI で取得し、clean markdown を返す **外部接続スキル**。

> **境界**：外部接続は hermes に集約する原則（2026-06-16）に従い、URL fetch はこのスキル（Hermes 側）が担う。

## 用途

| 経路 | 呼び出し方 | 説明 |
|---|---|---|
| 内部 | [[.hermes/skills/vault-capture/clippings-capture/SKILL.md]] が `content` 欠落ペイロードを受けたとき | URL → markdown 抽出 → `write_clipping.py` の `content` に詰める |
| Claude → hermes pull | `hermes chat -q "... defuddle ..." -s defuddle` | on-demand で 1 URL を clean fetch して stdout で返す |
| 単独 capture | clippings-capture 経由（本スキルは抽出だけ担う） | `Inbox/{YYYY-MM-DD}/clippings/{slug}.md` に書く |

## 前提

```bash
npm install -g defuddle
defuddle --version
```

## 使い方

### 単純な markdown 抽出

```bash
defuddle parse <url> --md
```

### ファイル出力

```bash
defuddle parse <url> --md -o content.md
```

### 特定メタデータ

```bash
defuddle parse <url> -p title
defuddle parse <url> -p description
defuddle parse <url> -p domain
```

### 出力フォーマット

| Flag | Format |
|------|--------|
| `--md` | Markdown (default choice) |
| `--json` | JSON with both HTML and markdown |
| (none) | HTML |
| `-p <name>` | Specific metadata property |

## Claude Code からの on-demand 呼び出し

```bash
# 日本語 Windows のみ PYTHONUTF8=1 を前置（cp932 デコード起因の出力欠落防止）
cd "<vault root>"

hermes chat -q "Fetch <URL> as clean markdown via 'defuddle parse <URL> --md' and return the markdown on stdout. Do not write to any file." -s defuddle -Q --source claude-code
```

得られた markdown は Claude が直接 vault に書き込む（curated 領域への配置判断は Claude の責務）。Inbox に着地させたい場合は `clippings-capture` 経由を選ぶ。

## 注意

- `.md` 終端の URL は既に markdown なので defuddle 不要 → 呼び出し側で判定して WebFetch 直接。
- SPA / Cloudflare 等で本文抽出に失敗するケースあり → stderr で警告。呼び出し側は raw URL を残してフォールバック。
- 大きな PDF は対象外（別途 PDF 抽出パイプラインへ）。

## 関連

- [[.hermes/skills/vault-capture/clippings-capture/SKILL.md]]（内部呼び出し元）
- [[.claude/rules/agent-boundaries.md]] §6 接続所有
- [[.claude/rules/inbox-routing.md]]（clippings 取り込みの全体像）
