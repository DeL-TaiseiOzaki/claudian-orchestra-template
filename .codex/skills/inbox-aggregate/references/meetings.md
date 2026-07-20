# Meeting source rules

## 目的

`Inbox/{date}/mtgs/*.md` に capture された provider-neutral な会議記録を、Daily ノートへ **要約 bullet として** append する。

> raw transcript は数千〜数万文字になり得るため Daily に貼らない。要点と原文への wikilink だけを残し、EOD distill で `Wiki/meetings/{date}-{topic}.md` へ統合する。

## 入力

- 走査: `Inbox/{YYYY-MM-DD}/mtgs/*.md`
- 共通 frontmatter: `source`, `meeting_title`, `meeting_date`, `participants`
- 任意 frontmatter: `provider`, `transcript_length`, `summary_present`, `user_notes_present`
- 本文: raw transcript（必須）と、provider summary / user notes（存在する場合）

provider 固有フィールドは読み取りに使ってよいが、集約処理の必須条件にしない。

## 出力（Daily 内の挿入先）

| meeting_title hint | Daily section |
|---|---|
| 学会・コミュニティ・研究関連 | `### 📚 Wiki` |
| 上記以外 | `### 🗒️ ミーティング・連絡メモ` |

### Bullet 形式

```markdown
- **[HH:MM] MTG / {meeting_title}** ({N}名参加, transcript {chars}字)
  - 要点: {3-5 bullet}
  - 決定事項: {あれば}
  - Action: {担当・期限あれば}
  - Source: [[Inbox/{date}/mtgs/{filename}.md]]
```

## 実行フロー

1. `Daily/{date}.md` と `Inbox/{date}/mtgs/*.md` を読む。
2. 各 capture の完全な source wikilink を Daily で検索し、既存なら skip する。
3. [[Maps/People-Map.md]] を参照し、参加者と本文中の話者名を canonical 表記へ正規化する。不明な名前は変更せず `?` を添える。
4. `meeting_title` から挿入先を選ぶ。判定不能なら `### 🗒️ ミーティング・連絡メモ` を使う。
5. user notes があれば最優先し、次に provider summary、どちらも無ければ transcript から要点・決定事項・action items を抽出する。
6. source wikilink付き bullet を append し、直後に再読して重複とリンクを確認する。

## 注意

- raw transcript や長い provider summary は Daily に貼らない。
- 本文にない事実、決定、担当、期限を補わない。
- `inbox-aggregate` は Daily 集約まで。Main DB への配分は `eod-distill` が担う。
- 既存の `mtg-prep` draft がある場合も上書きせず、Daily から両方へ辿れる状態を保つ。

## 関連

- [[Maps/People-Map.md]]
- [[.codex/skills/mtg-prep/SKILL.md]]
- [[.codex/skills/eod-distill/SKILL.md]]
- [[.codex/rules/inbox-routing.md]] §3
- [[.codex/rules/wiki-management.md]]
- [[Meta/connections/meeting-notes.md]]
