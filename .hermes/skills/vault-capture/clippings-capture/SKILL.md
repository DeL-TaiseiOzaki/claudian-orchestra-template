---
name: clippings-capture
description: Use when ingesting a captured web LLM chat (ChatGPT / Claude) or a web page into the your-vault. Writes the clip as RAW markdown to Inbox/{YYYY-MM-DD}/clippings/{slug}.md for the Claude Code curate step to distill. Intended to be invoked on-demand — either event-driven via the Chrome extension webhook, or when the user issues a 取り込み instruction (typically from the Daily-note ジョブリスト). May also run from a cron if registered, but on-demand is the primary mode.
version: 1.0.0
author: your-org
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [vault, capture, clippings, chrome-extension, webhook, vault-capture]
    related_skills: [defuddle, obsidian]
---

# clippings-capture

Web の壁打ち（ChatGPT / Claude）や記事を **生のまま** `Inbox/{YYYY-MM-DD}/clippings/`（日付つき親フォルダ配下）に取り込む capture 係。

> **役割境界**：書き込みは **`Inbox/{YYYY-MM-DD}/clippings/` のみ**（single-writer）。root `Daily/` や
> curated（Work / Research / Others）には触れない。整理（蒸留・リンク・昇華）は Claude Code
> 側の別工程（[[Inbox/README.md]] の処理フロー）。

## 取り込み経路（Chrome 拡張 → Hermes）

自作 Chrome 拡張が、開いているチャット/ページを捕捉して **Hermes ゲートウェイの webhook** に
JSON を POST する（webhook 設定は `webhook-subscriptions` skill）。Hermes はそれをこの skill に
ルーティングし、ペイロードを `write_clipping.py` に渡す。

### ペイロード契約（拡張 → Hermes）

```json
{
  "source": "chatgpt" | "claude" | "web" | "manual",
  "url": "https://chat.openai.com/...",
  "title": "会話のタイトル",
  "captured_at": "2026-06-03T09:00:00Z",
  "content": "# 取り込む本文（markdown）...",
  "tags": ["任意"]
}
```

- `content` のみ必須。`source` 既定は `web`、`captured_at` 既定は現在。
- **チャット**：拡張側で会話を markdown 化して `content` に入れる（推奨）。
- **一般 Web ページ**：`content` を作れない場合は `url` だけ送り、Hermes 側で
  [[.hermes/skills/vault-capture/defuddle/SKILL.md]] 等で本文 markdown を抽出してから `content` に詰める。

## 書き込み（決定的・スクリプト）

```bash
# 標準入力に上記 JSON を渡す。書き出したパスを stdout に返す。
echo "$PAYLOAD_JSON" | python "${HERMES_HOME:-$HOME/.hermes}/skills/vault-capture/clippings-capture/scripts/write_clipping.py"
```

- 出力先：`Inbox/{YYYY-MM-DD}/clippings/{slug}.md`（日付つき親フォルダが日付を持ち、ファイル名に日付 prefix は付けない。衝突時は `-2`, `-3` …で**上書きしない**）。
- vault ルートは `OBSIDIAN_VAULT_PATH` を最優先。未設定時はカレントディレクトリまたは `HERMES_HOME` の親が <your-vault> Vault に見える場合のみ採用（`Inbox/` + `CLAUDE.md` / `.obsidian` で検証）。
- 付与する frontmatter：

```yaml
---
title: "..."
source: chatgpt        # chatgpt | claude | web | manual
created: 2026-06-03
url: "https://..."     # あれば
status: "inbox"
tags: ["clipping", "<source>", ...]
---
```

- エラー時（`content` 欠落・vault 解決不可等）は stderr に `clipping failed: ...` を出して
  非ゼロ終了 → 呼び出し側はその旨を通知し、briefing 等の他処理は止めない。

## 起動方法（on-demand 既定 / cron は任意）

**既定 = on-demand**：このスキルは元々 **event-driven**（Chrome 拡張 webhook → Hermes gateway）。それに加えてユーザーが Daily ノートの `## 🤖 ジョブリスト` を見て「clippings の取り込みやって」と Claude に指示 → Claude が hermes に CLI で委譲（[[.claude/skills/hermes-query/SKILL.md]]）するパターンも on-demand 既定として扱う。

### 手動 invoke コマンド

> `hermes chat -q` のスキル指定は `-s <skill>`（`--skill` / `--workdir` というフラグは無い）。vault ルートに cd してから呼ぶ。日本語 Windows では呼び出し前に `PYTHONUTF8=1` を設定する（cp932 デコード起因の出力欠落防止 → [[.claude/skills/hermes-query/SKILL.md]]）。

```bash
cd "<vault root>"

# 既に拡張から POST されている JSON ペイロードを再投入する場合（bash でも動作）
echo "$PAYLOAD_JSON" | python "${HERMES_HOME:-$HOME/.hermes}/skills/vault-capture/clippings-capture/scripts/write_clipping.py"

# または hermes 経由で skill 起動（webhook subscription 経由のリプレイ等）
hermes chat -q "Load the clippings-capture skill and process the pending clipping payload (or the URL the user pastes inline) into Inbox/<today>/clippings/{slug}.md as RAW markdown." -s clippings-capture -Q --source claude-code
```

### Cron 登録（任意）

> 本 skill は元々 event-driven なので cron 登録は通常不要。定期的な webhook backlog 再処理をしたい場合のみ登録する。

```bash
# 参考：定期的に pending webhook queue を flush する場合の cron 例（任意）
# hermes cron create "0 * * * *" "Load the clippings-capture skill and flush any pending clipping payloads received via the Chrome extension webhook into Inbox/{YYYY-MM-DD}/clippings/{slug}.md." --name clippings-capture-hourly --skill clippings-capture --workdir "<vault root>"
```

## curate（この後の工程・Claude Code 側）

- `Inbox/{YYYY-MM-DD}/clippings/` に溜まったものは、判断・蒸留して Work / Research / Others の evergreen へ
  移送・リンク（移動元にリンクを残す）。処理済みは削除し、Inbox を空に近づける。
- 規約：[[.claude/rules/agent-boundaries.md]] / [[Inbox/README.md]]。

## 関連

- 取り込み先規約：[[Inbox/README.md]]
- 境界：[[.claude/rules/agent-boundaries.md]]（capture / curate・single-writer）
- 本文抽出：[[.hermes/skills/vault-capture/defuddle/SKILL.md]]（一般 Web ページ）
