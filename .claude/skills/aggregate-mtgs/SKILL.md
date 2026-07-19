---
name: aggregate-mtgs
description: Read Hermes-staged Genspark meeting transcripts at Inbox/{YYYY-MM-DD}/mtgs/genspark-*.md and aggregate concise meeting bullets (title / key points / decisions / action items) into today's root Daily note (Daily/{YYYY-MM-DD}.md). Routes to 🏢 Work (project meetings) or 🗒️ ミーティング・連絡メモ. Append-only with wikilinks back to the raw transcript. Speaker names are normalized via Maps/People-Map.md (AI transcription mishears 同音異字). Skip transcripts already aggregated (idempotency via wikilink presence in Daily). Use on-demand when new genspark-mtg capture lands; full transcripts stay in Inbox until EOD distill moves them to {project}/meetings/.
---

# aggregate-mtgs

## 目的

Hermes が `Inbox/{date}/mtgs/genspark-{slug}.md` に capture した Genspark 議事録 raw transcript を、Daily ノートの該当セクションに **要約 bullet として** append する。

> **位置づけ**：raw transcript は重い（数千〜数万文字）ので Daily にそのまま入れない。**要点だけ抜き出して Daily の hub 性を保ち、フル原文へは wikilink で辿る**。EOD distill 時に [[.claude/skills/eod-distill/SKILL.md]] が `{project}/meetings/{date}-{topic}.md`（compiled）へ要約版を配分する（[[.claude/rules/inbox-routing.md]] §3 例外）。

## 入力

- 走査: `Inbox/{YYYY-MM-DD}/mtgs/genspark-*.md`
- frontmatter: `source: "genspark:meeting:..."`, `meeting_title`, `meeting_date`, `participants`, `transcript_length`, `genspark_summary_present`, `genspark_user_notes_present`
- 本文: Genspark `summary` / `user_notes`（任意）＋ raw transcript（必須）

## 出力（Daily 内の挿入先）

| meeting_title hint | Daily section |
|---|---|
| `[PROJ_A]` / `[PROJ_B]` / `[PROJ_C]` / `[PROJ_X]` prefix | `### 🏢 Work` の該当案件 bullet 配下 |
| 学会・コミュニティ（Community-A / Community-B / Kaggle 等） | `### 💡 Others / Insights`（Activities） |
| Research 関連 | `### 🔬 Research` |
| 上記以外 | `### 🗒️ ミーティング・連絡メモ` |

### Bullet 形式

```markdown
- **[HH:MM] MTG / {meeting_title}** ({N}名参加, transcript {chars}字)
  - 要点: {3-5 bullet}
  - 決定事項: {あれば}
  - Action: {担当・期限あれば}
  - Source: [[Inbox/{date}/mtgs/genspark-{slug}.md]]
```

## 実行フロー

### Step 1: 当日 Daily 確定
- `Daily/{date}.md` を Read

### Step 2: Inbox mtgs 走査
- `Inbox/{date}/mtgs/genspark-*.md` を一覧
- frontmatter から `meeting_title`, `participants`, `transcript_length` を抽出

### Step 3: 未集約チェック
- Daily 全文を Grep し、`[[Inbox/{date}/mtgs/genspark-{slug}.md]]` wikilink が既にあれば **skip**

### Step 4: 話者名正規化（重要）
- AI 文字起こしは同音異字を誤記する（例：「ヤマダ」→「山田田」→ 実際は「山田 太郎」）
- [[Maps/People-Map.md]] を参照して `participants` と本文中の名前を canonical 表記に正規化
- 不明な人名は raw のまま残し、Daily 上で `?` 注記を付ける

### Step 5: section 振り分け
- `meeting_title` の prefix から project を推定
- 学会／コミュニティ／Research 系判定

### Step 6: 要約作成（重要）
- Genspark の `summary` / `user_notes` があれば**それを優先**（Genspark 側 LLM 整形済み）
- 無ければ transcript から自前抽出：
  - 要点 3-5 bullet（10-30 字/bullet）
  - 決定事項（あれば）
  - Action items（担当・期限あれば）
- **本スキルでは要約を Daily に書く**。raw transcript は Inbox に残す（EOD で配分）

### Step 7: append
- 該当 section の末尾に bullet を挿入
- **既存 bullet・frontmatter は触らない**

## 並列セッションへの配慮

- 並列で同じ transcript を 2 セッションが処理しないよう、Step 3 の wikilink チェック必須
- People-Map.md は read-only（更新は別 skill）

## 注意

- **raw transcript は Daily に貼らない**（hub の hub-ness を保つ）
- **要約は raw を超えない**（hallucination 防止 — 本文に無いことを書かない）
- **割り振り判定は curate 段階**（本 skill は Daily 集約のみ）
- 名前正規化は EOD distill 時にも再度行う（多段防御）

## 他 skill との連携

- [[.claude/skills/eod-distill/SKILL.md]]（要約版を `{project}/meetings/` へ配分）
- [[.hermes/skills/vault-capture/genspark-mtg/SKILL.md]]（capture 側）
- [[.claude/skills/session-log/SKILL.md]]（append-only pattern）

## 関連

- [[Maps/People-Map.md]]（話者名 canonical mapping）
- [[.claude/rules/inbox-routing.md]] §3（mtgs の curate 例外）
- [[.claude/rules/work-management.md]]（Work meetings/ 命名）
