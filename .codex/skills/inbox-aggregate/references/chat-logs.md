# Chat-log source rules

## 目的

ブラウザ拡張が `Inbox/{date}/chat-logs/{provider}-{slug}.md` に capture した ChatGPT / Claude 等の会話ログを、Daily ノートの該当セクションに **議論テーマ + 主要結論 + 残った疑問** として append する。

> **位置づけ**：会話ログは「壁打ち・思考の足跡」。生の対話は重いので Daily にはサマリだけ。EOD distill で durable な insight だけ `Wiki/` ／ `.codex/docs/knowledges/` に蒸留する。

## 入力

- 走査: `Inbox/{YYYY-MM-DD}/chat-logs/*.md`
- ファイル名規則: `{provider}-{slug}.md`
- frontmatter: `source: "chat:{provider}:{thread_id}"`, `created`, `url`（chat URL があれば）
- 本文: 会話 markdown（User / Assistant の往復）

## 出力（Daily 内の挿入先）

| 議論内容 | Daily section |
|---|---|
| 実装相談 / 設計議論 | `### 📚 Wiki` |
| 研究テーマの議論（仮説検証・論文読み込み） | `### 📚 Wiki` |
| 着想・アイデアの壁打ち | `### 📚 Wiki` |
| Meta（vault 整備・skill 設計など） | `### 📚 Wiki` の `[Meta]` prefix |
| 一般の学習・チュートリアル | `### 📚 Wiki` |

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
- 会話冒頭の User メッセージから theme hint を推定
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
- **EOD distill で配分**：durable な insight は `Wiki/` ／ `.codex/docs/knowledges/` へ
- **長すぎる対話**：1 セッションあたり数千トークン超なら、トピック単位で分割要約することも検討
- **個人情報・機密**：会話に含まれる機密情報は要約段階で削る（Daily は GitHub に push されるため）

## 他 skill との連携

- [[.codex/skills/eod-distill/SKILL.md]]（durable insight を Main DB へ配分）
- [[.codex/skills/knowledge-capture/SKILL.md]]（学びとして昇華）
- [[.codex/skills/wiki-writer/SKILL.md]]（Wiki ノート作成）
- [[.hermes/skills/vault-capture/clippings-capture/SKILL.md]]（capture 経路）

## 関連

- [[.codex/rules/inbox-routing.md]] §2 chat-logs 行
