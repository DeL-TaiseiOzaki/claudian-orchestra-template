---
name: aggregate-slack
description: Read Hermes-staged Slack digests at Inbox/{YYYY-MM-DD}/slack/*.md and aggregate them into today's root Daily note (Daily/{YYYY-MM-DD}.md). Per-channel summary as bullets, routed by channel hint to Work section (for project channels) / 🗒️ ミーティング・連絡メモ (DMs / general) / 💡 Others (broader). Append-only with wikilinks back to the Inbox source. Use on-demand mid-day when new Slack capture lands (typically right after the user runs slack-capture via hermes-query); morning sweep is also covered by daily-briefing. Skip channels already aggregated (idempotency via wikilink presence in Daily).
---

# aggregate-slack

## 目的

Hermes が `Inbox/{date}/slack/{channel}.md` に capture した日次 Slack ダイジェストを、Daily ノートの該当セクションに **append** する。

> **位置づけ**：[[.claude/rules/inbox-routing.md]] §1 Step 2「aggregate」を Slack に特化した on-demand スキル。朝の全体さらいは [[.claude/skills/daily-briefing/SKILL.md]]、EOD の Main DB 配分は [[.claude/skills/eod-distill/SKILL.md]] が担う（本スキルは中継のみ）。

## 入力

- 走査: `Inbox/{YYYY-MM-DD}/slack/*.md`
- ファイル名規則: `{channel}.md`（通常 channel） / `dm-{counterpart}.md`（DM）
- frontmatter: `source: "slack:digest:..."`, `channel`, `is_dm`, `participants`, `message_count`, `user_authored`, `user_mentioned`

## 出力（Daily 内の挿入先）

| Inbox file の channel | Daily section |
|---|---|
| Work 系 channel（`proj-a-*` / `proj-b-*` / `proj-c-*` / `proj-d-*` / `proj-e-*` / `proj-f-*`） | `### 🏢 Work` の該当案件 bullet 配下 |
| DM（`dm-*`） | `### 🗒️ ミーティング・連絡メモ` |
| 一般・部署 channel | `### 🗒️ ミーティング・連絡メモ` |
| 知見系 / 雑談から学び | `### 💡 Others / Insights` |

### Bullet 形式

```markdown
- **[HH:MM] Slack / #{channel}** ({message_count} messages, the user authored {N})
  - {the user 発言の要点 1-2 行}
  - {他者の重要 message 抜粋 / 決定事項}
  - Source: [[Inbox/{date}/slack/{channel}.md]]
```

## 実行フロー

### Step 1: 当日 Daily 確定
- `date +%Y-%m-%d` で today
- `Daily/{date}.md` を Read（無ければ daily-briefing 朝モード提案）

### Step 2: Inbox slack 走査
- `Inbox/{date}/slack/*.md` を一覧

### Step 3: 未集約チェック
- 各ファイルについて Daily 全文を Grep し、`[[Inbox/{date}/slack/{channel}.md]]` wikilink が既にあれば **skip**

### Step 4: section 振り分け
- channel 名から project hint を推定（テーブルに従う）
- DM / 一般は ミーティング・連絡メモ
- 不明は `### 💡 Others / Insights`

### Step 5: summary 作成
- frontmatter の `participants` / `message_count` / `user_authored` を読む
- 本文の重要 message を 1-3 bullet で抽出
  - the user 発言（intent / 決定）
  - mention された箇所の context
  - decisions / action items

### Step 6: append
- 該当 section の末尾に bullet を挿入
- **既存 bullet は触らない**（並列セッション競合回避）
- frontmatter `updated` も触らない

## 並列セッションへの配慮

- [[.claude/skills/session-log/SKILL.md]] と同じ append-only 規則
- Edit の `old_string` は一意性を必ず確認
- 同じ channel が複数セッションで処理されるリスク → Step 3 の wikilink チェックで防ぐ

## 注意

- **Daily へは要約のみ**：raw transcript は Inbox に残す（EOD distill 時に `{area}/sources/` へ配分）
- Slack 添付（`Inbox/{date}/attachments/slack/...`）は本スキルでは触らない
- channel→project mapping は heuristic（厳密 mapping は [[.claude/rules/inbox-routing.md]] §5 廃止後の運用）

## 関連

- [[.claude/skills/session-log/SKILL.md]]（append-only pattern の源流）
- [[.claude/skills/daily-briefing/SKILL.md]]（朝の全体さらい）
- [[.claude/skills/eod-distill/SKILL.md]]（EOD で Daily → Main DB）
- [[.hermes/skills/vault-capture/slack-capture/SKILL.md]]（capture 側）
- [[.claude/rules/inbox-routing.md]] §1 / §5
