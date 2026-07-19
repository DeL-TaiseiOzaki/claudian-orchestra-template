---
name: aggregate-chat-logs
description: Read AI chat exports (ChatGPT / Claude conversation transcripts) at Inbox/{YYYY-MM-DD}/chat-logs/{provider}-{slug}.md and aggregate concise discussion bullets (theme / main conclusions / open questions) into today's root Daily note (Daily/{YYYY-MM-DD}.md). Routes to 💡 Others / Insights by default; project-related discussions route to Work / Research. Append-only with wikilinks back to the raw chat. Use on-demand when a new AI Exporter clipping has landed mid-day; EOD distill later moves durable insights to Others/Ideas/ or .claude/docs/knowledges/.
---

# aggregate-chat-logs

## 目的

Hermes（Chrome 拡張 AI Exporter）が `Inbox/{date}/chat-logs/{provider}-{slug}.md` に capture した ChatGPT / Claude の会話ログを、Daily ノートの該当セクションに **議論テーマ + 主要結論 + 残った疑問** として append する。

> **位置づけ**：会話ログは「壁打ち・思考の足跡」。生の対話は重いので Daily にはサマリだけ。EOD distill で durable な insight だけ `Others/Ideas/` ／ `.claude/docs/knowledges/` に蒸留する。

## 入力

- 走査: `Inbox/{YYYY-MM-DD}/chat-logs/*.md`
- ファイル名規則: `chatgpt-{slug}.md` / `claude-{slug}.md`
- frontmatter: `source: "chat:{provider}:{thread_id}"`, `created`, `url`（chat URL があれば）
- 本文: 会話 markdown（User / Assistant の往復）

## 出力（Daily 内の挿入先）

| 議論内容 | Daily section |
|---|---|
| 案件関連の検討（実装相談 / 設計議論） | `### 🏢 Work` の該当案件 |
| 研究テーマの議論（仮説検証・論文読み込み） | `### 🔬 Research` |
| 着想・アイデアの壁打ち | `### 💡 Others / Insights` |
| Meta（vault 整備・skill 設計など） | `### 💡 Others / Insights` の `[Meta]` prefix |
| 一般の学習・チュートリアル | `### 💡 Others / Insights` |

### Bullet 形式

```markdown
- **[HH:MM] chat / {provider} — {テーマ}**
  - 主要な結論: {1-2 bullet}
  - Open questions / Follow-up: {あれば}
  - Source: [[Inbox/{date}/chat-logs/{provider}-{slug}.md]]
```

## 実行フロー

### Step 1: 当日 Daily 確定
- `Daily/{date}.md` を Read

### Step 2: Inbox chat-logs 走査
- `Inbox/{date}/chat-logs/*.md` を一覧

### Step 3: 未集約チェック
- Daily 全文で `[[Inbox/{date}/chat-logs/{provider}-{slug}.md]]` を Grep
- 既にあれば skip

### Step 4: section 振り分け
- 会話冒頭の User メッセージから theme / project hint を推定
- Meta（vault 整備）系は `[Meta]` prefix を付ける

### Step 5: 要約作成
- 会話全体から：
  - テーマ（1 行）
  - 主要な結論 / 合意（1-2 bullet）
  - 残った open question / follow-up（あれば）
- **対話の引用ではなく自分の言葉で要約**（user 視点で「何を得たか」）
- 本文に無いことは書かない

### Step 6: append
- 該当 section の末尾に bullet を挿入
- **既存 bullet・frontmatter は触らない**

## 並列セッションへの配慮

- 個別 chat ログが複数セッションで処理されないよう Step 3 の wikilink チェック必須

## 注意

- **会話本文は Daily に貼らない**（思考の足跡として Inbox に保持）
- **EOD distill で配分**：durable な insight は `Others/Ideas/` ／ `.claude/docs/knowledges/` ／ Work/Research の該当ノートへ
- **長すぎる対話**：1 セッションあたり数千トークン超なら、トピック単位で分割要約することも検討
- **個人情報・機密**：会話に含まれる機密情報は要約段階で削る（Daily は GitHub に push されるため）

## 他 skill との連携

- [[.claude/skills/eod-distill/SKILL.md]]（durable insight を Main DB へ配分）
- [[.claude/skills/knowledge-capture/SKILL.md]]（学びとして昇華）
- [[.claude/skills/others-writer/SKILL.md]]（Ideas / Learning ノート作成）
- [[.hermes/skills/vault-capture/clippings-capture/SKILL.md]]（capture 経路）

## 関連

- [[.claude/rules/inbox-routing.md]] §2 chat-logs 行
- [[Meta/web-clipper-setup/status.md]]（AI Exporter pivot 経緯）
