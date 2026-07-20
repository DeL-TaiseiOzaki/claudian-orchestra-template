# Knowledge note template

Copy-paste this and fill in. Save as `.codex/docs/knowledges/{category}/{slug}.md`.

```markdown
---
title: "<短い英文 or 日本語、覚えやすい呼び方>"
type: "knowledge"
status: "active"
tags: ["<category>", "<subdomain>", "<tool-name>"]
created: "2026-MM-DD"
updated: "2026-MM-DD"
source: "incident:#NN"            # or "session:YYYY-MM-DD" or "consult:<topic>"
applies_to: ["<component>/<area>"]  # e.g. ["hermes/cron", "mcp/stdio"]
related_commit: "<short-hash>"     # optional
severity: medium                    # low | medium | high
---

# {title}

> TL;DR — 3 行以内で「症状 → 原因 → 修正」。

## 症状 (Symptom)

何が観測されたか。エラーメッセージ・予期せぬ挙動を **コピペできる粒度** で書く。

```
（実際のエラーメッセージや log の抜粋）
```

## 文脈 (Context)

- いつ：YYYY-MM-DD HH:MM
- どこで：tool / skill / cron / 環境
- 構成：関連 versions・config・PAT scope など

## 根本原因 (Root cause)

最終的に判明した原因。可能なら：
- 該当 source code 行を引用（path:line + 抜粋）
- 該当 spec / docs を引用
- 「なぜそう設計されているか」も書く（意図的な制約か、bug か）

```python
# 例：path/to/file.py:296
def _build_safe_env(user_env):
    """..."""
    # whitelist filter
```

## 失敗した仮説 (False leads, optional)

どの仮説で迷走したか、なぜ却下したか。将来同じ症状を見た人が「あ、それは違うよ」と即弾けるように。

1. 仮説 A：... → 却下理由：...
2. 仮説 B：... → 却下理由：...

## 修正 (Fix)

具体的な diff / 設定 / 手順。

```yaml
# 例
mcp_servers:
  github:
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_PERSONAL_ACCESS_TOKEN}"
```

## 検証 (Verification)

修正後にどう動作確認したか。再現できるコマンド／期待値。

```powershell
hermes chat -q "..." -t github -Q
# 期待: OK <sha>
```

## 再発防止チェック (Future-proof check)

このパターンが再発したらすぐ気づくための **1 行コマンドや指標**。

```bash
# 例：MCP に渡されている env を確認する 1 行
grep -E "^\s+env:" .hermes/config.yaml
```

## 関連 (Related)

- 関連 issue: `<実在する issue URL または Meta/{project-name}/status.md#NN>`
- 関連 commit: `<hash>` `<short summary>`
- 関連 knowledge: `<実在する knowledge note への wikilink>`
- 外部 doc: <URL>
```

## カスタマイズ

- TL;DR を必ず書く（読者が 5 秒で要否判定できる）
- 失敗した仮説 (False leads) は optional だが、迷走が長かった件は書く。書くだけで次回の調査時間が大幅に短縮できる。
- 検証コマンドは copy-paste 可能な形で（PowerShell / Bash 区別）
- code 抜粋には絶対 path + line 番号を付ける（hermes 等は version 更新で行番号が動くので、`source` 行の hash で固定すると尚良し）
