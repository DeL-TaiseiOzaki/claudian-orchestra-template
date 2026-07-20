---
name: clippings-capture
description: Route a web page or exported LLM chat to its raw Inbox source queue for later core-agent curation.
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

Web 記事と AI 壁打ちログを **生のまま** source 別 Inbox queue に取り込む capture 係。

- Web / manual: `Inbox/{YYYY-MM-DD}/clippings/{slug}.md`
- ChatGPT / Claude: `Inbox/{YYYY-MM-DD}/chat-logs/{provider}-{slug}.md`

> **役割境界**：書き込みは上記 2 queue の新規 capture のみ（single-writer）。root `Daily/` や
> curated（Wiki）には触れない。整理（蒸留・リンク・昇華）はコアエージェントが担う。
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
echo "$PAYLOAD_JSON" | uv run --no-project python "${HERMES_HOME:-$HOME/.hermes}/skills/vault-capture/clippings-capture/scripts/write_clipping.py"
```

- 出力先は `source` で決定する。`web` / `manual` は `clippings/{slug}.md`、`chatgpt` / `claude` は `chat-logs/{provider}-{slug}.md`。親の日付は `captured_at` を Asia/Tokyo に正規化した capture-event date。衝突時は `-2`, `-3` …で**上書きしない**。
- vault ルートは `OBSIDIAN_VAULT_PATH` を最優先。未設定時はカレントディレクトリまたは `HERMES_HOME` の親が <your-vault> Vault に見える場合のみ採用（`Inbox/` + `AGENTS.md` / `.obsidian` で検証）。
- 付与する frontmatter：

```yaml
---
title: "..."
type: "capture"
status: "inbox"
tags: ["clipping", "web"]
created: 2026-06-03
updated: 2026-06-03
source: "web:url:https://..."  # chat log は chatgpt | claude
fetched_at: "2026-06-03T18:00:00+09:00"
url: "https://..."     # あれば
---
```

- エラー時（`content` 欠落・vault 解決不可等）は stderr に `clipping failed: ...` を出して
  非ゼロ終了 → 呼び出し側はその旨を通知し、briefing 等の他処理は止めない。

## 起動方法（on-demand）

**既定 = on-demand**：Chrome 拡張 webhook または Daily ジョブリストからの指示で実行する。

### 手動 invoke コマンド

> `hermes chat -q` のスキル指定は `-s <skill>`（`--skill` / `--workdir` というフラグは無い）。vault ルートに cd してから呼ぶ。日本語 Windows では呼び出し前に `PYTHONUTF8=1` を設定する（cp932 デコード起因の出力欠落防止 → [[.codex/skills/hermes-query/SKILL.md]]）。

```bash
cd "<vault root>"

# 既に拡張から POST されている JSON ペイロードを再投入する場合（bash でも動作）
echo "$PAYLOAD_JSON" | uv run --no-project python "${HERMES_HOME:-$HOME/.hermes}/skills/vault-capture/clippings-capture/scripts/write_clipping.py"

# または hermes 経由で skill 起動（webhook subscription 経由のリプレイ等）
hermes chat -q "Load the clippings-capture skill and process the pending payload as RAW markdown. Route web/manual content to Inbox/<today>/clippings/{slug}.md and ChatGPT/Claude content to Inbox/<today>/chat-logs/{provider}-{slug}.md. Create a new file only." -s clippings-capture -Q --source core-agent
```

> 既存環境に旧 cron がある場合は過渡期ジョブとして現状維持し、この template から新規登録・変更しない。event-driven webhook または on-demand を使う。

## curate（この後の工程・コア側）

- `clippings/` と `chat-logs/` に溜まったものは、コアが判断・蒸留して Wiki の evergreen / sources へ移送し、Daily に監査リンクを残す。Hermes は移動・削除しない。
- 規約：[[.codex/rules/agent-boundaries.md]] / [[Inbox/README.md]]。

## 関連

- 取り込み先規約：[[Inbox/README.md]]
- 境界：[[.codex/rules/agent-boundaries.md]]（capture / curate・single-writer）
- 本文抽出：[[.hermes/skills/vault-capture/defuddle/SKILL.md]]（一般 Web ページ）
