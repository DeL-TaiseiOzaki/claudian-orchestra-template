# Clipping source rules

## 目的

Hermes（Chrome 拡張 → webhook）が `Inbox/{date}/clippings/{slug}.md` に capture した Web ページ・記事を、Daily ノートの該当セクションに **タイトル + 1 行サマリ + tag 候補** として append する。

> **位置づけ**：Web 記事は信号薄め（user の興味で取り込まれただけ）なので、Daily へは小さなリンク bullet として残し、EOD distill で durable なものだけ `Wiki/sources/` / `Wiki/` に蒸留する。

## 入力

- 走査: `Inbox/{YYYY-MM-DD}/clippings/*.md`
- frontmatter: `source: "web:url:..."` / `"chatgpt:..."` / `"claude:..."`, `url`, `fetched_at`, `tags`
- 本文: clean markdown（[[.hermes/skills/vault-capture/defuddle/SKILL.md]] 抽出）

## 出力（Daily 内の挿入先）

| clipping 内容 | Daily section |
|---|---|
| 研究テーマ関連（LLM / VLM / coaching / motion 等） | `### 📚 Wiki` |
| 一般的な技術記事 / 雑学 / 興味記事 | `### 📚 Wiki` |
| 学会・コミュニティ関連 | `### 📚 Wiki` |

### Bullet 形式

```markdown
- **[HH:MM] clip / {title}**
  - {1 行サマリ}（tags: {tag1}, {tag2}）
  - Source: [[Inbox/{date}/clippings/{slug}.md]] / [{domain}]({url})
```

## 実行フロー

### Step 1: 当日 Daily 確定
- `Daily/{date}.md` を Read

### Step 2: Inbox clippings 走査
- `Inbox/{date}/clippings/*.md` を一覧
- frontmatter の `title` / `url` / `tags` を抽出

### Step 3: 未集約チェック
- Daily 全文で `[[Inbox/{date}/clippings/{slug}.md]]` を Grep
- 既にあれば skip

### Step 4: section 振り分け
- title / url / tags / 本文の先頭から theme hint を推定
- 判定不能は `### 📚 Wiki`

### Step 5: 1 行サマリ生成
- 本文の lead paragraph または最初の見出しから 1 行（30-50 字）
- **本文に無いことを書かない**（hallucination 防止）
- tag は frontmatter の tags + 推定 1-2 個

### Step 6: append
- 該当 section の末尾に bullet を挿入
- **既存 bullet・frontmatter は触らない**

## 並列セッションへの配慮

- 個別 clipping が複数セッションで処理されないよう Step 3 の wikilink チェック必須

## 注意

- **本文は Inbox に残す**（重い content を Daily に貼らない）
- **EOD distill で配分**：本当に保存価値ある記事は `Wiki/sources/`（reference）or `Wiki/{slug}.md`（着想の種）へ
- **chat-logs（ChatGPT / Claude 会話）は別 source mode**：`inbox-aggregate` を Chat logs 指定で使う

## 他 skill との連携

- [[.codex/skills/eod-distill/SKILL.md]]（durable なものを配分）
- [[.hermes/skills/vault-capture/clippings-capture/SKILL.md]]（capture 側）
- [[.hermes/skills/vault-capture/defuddle/SKILL.md]]（本文抽出）

## 関連

- [[.codex/rules/inbox-routing.md]] §3 配分表
- [[.codex/rules/vault-tagging.md]]
