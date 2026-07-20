# Slack source rules

## 目的

Hermes が `Inbox/{date}/slack/{channel}.md` に capture した日次 Slack ダイジェストを、Daily ノートの該当セクションに **append** する。

> **位置づけ**：[[.codex/rules/inbox-routing.md]] §1 Step 2「aggregate」を Slack に特化した on-demand スキル。朝の全体さらいは [[.codex/skills/daily-briefing/SKILL.md]]、EOD の Main DB 配分は [[.codex/skills/eod-distill/SKILL.md]] が担う（本スキルは中継のみ）。

## 入力

- 走査: `Inbox/{YYYY-MM-DD}/slack/*.md`
- ファイル名規則: `{channel}.md`（通常 channel） / `dm-{counterpart}.md`（DM）
- frontmatter: `source: "slack:digest:..."`, `channel`, `is_dm`, `participants`, `message_count`, `user_authored`, `user_mentioned`

## 出力（Daily 内の挿入先）

| Inbox file の channel | Daily section |
|---|---|
| DM（`dm-*`） | `### 🗒️ ミーティング・連絡メモ` |
| 一般・部署 channel | `### 🗒️ ミーティング・連絡メモ` |
| 知見系 / 雑談から学び | `### 📚 Wiki` |

### Bullet 形式

```markdown
- **[HH:MM] Slack / #{channel}** ({message_count} messages, user authored {N})
  - {ユーザー発言の要点 1-2 行}
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
- channel 名から section を推定（テーブルに従う）
- DM / 一般は ミーティング・連絡メモ
- 不明は `### 📚 Wiki`

### Step 5: summary 作成
- frontmatter の `participants` / `message_count` / `user_authored` を読む
- 本文の重要 message を 1-3 bullet で抽出
  - ユーザー発言（intent / 決定）
  - mention された箇所の context
  - decisions / action items

### Step 6: append
- 該当 section の末尾に bullet を挿入
- **既存 bullet は触らない**（並列セッション競合回避）
- frontmatter `updated` も触らない

## 並列セッションへの配慮

- [[.codex/skills/session-log/SKILL.md]] と同じ append-only 規則
- Edit の `old_string` は一意性を必ず確認
- 同じ channel が複数セッションで処理されるリスク → Step 3 の wikilink チェックで防ぐ

## 注意

- **Daily へは要約のみ**：raw transcript は Inbox に残す（EOD distill 時に `Wiki/sources/` へ配分）
- Slack 添付（`Inbox/{date}/attachments/slack/...`）は本スキルでは触らない
- channel→section mapping は heuristic（厳密 mapping は [[.codex/rules/inbox-routing.md]] §5 廃止後の運用）

## 関連

- [[.codex/skills/session-log/SKILL.md]]（append-only pattern の源流）
- [[.codex/skills/daily-briefing/SKILL.md]]（朝の全体さらい）
- [[.codex/skills/eod-distill/SKILL.md]]（EOD で Daily → Main DB）
- [[.hermes/skills/vault-capture/slack-capture/SKILL.md]]（capture 側）
- [[.codex/rules/inbox-routing.md]] §1 / §5
