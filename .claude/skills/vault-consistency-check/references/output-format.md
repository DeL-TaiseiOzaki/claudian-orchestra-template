# Output Format

`vault-consistency-check` は Daily に次の Markdown をそのまま書く。

## Section Heading

- 1 行目は必ず `## 🔍 整合性チェック`
- 見出しの次は 1 行空ける

## Summary Line

- 2 行目ではなく、見出しの 1 行下を空けた次の行に置く
- 形式は `WARN: N, ERROR: N, OK: N (checked: 7, mode: M, ran: HH:MM)`
- `mode` は `light` か `full`
- `ran` は実行時刻の 24 時間表記

## Finding Line

- 1 finding 1 行
- 基本形は `- TAG [check-name] path :: 説明。提案: ...（提案のみ・auto-fix なし）。`
- `TAG` は `OK` `WARN` `ERROR` の 3 種だけ
- path を省略してよいのは全体状態だけ
- 説明と提案は日本語で書く
- check 名は英語固定で、次の 8 個だけを使う
  - `Broken wikilinks`
  - `Frontmatter schema violation`
  - `Inbox stagnation`
  - `Today Tasks drift`
  - `Code-Map repo health`
  - `Submodule dirty / commit drift`
  - `Structure drift`

## Sort Order

- まず `ERROR > WARN > OK`
- 同じ tag 内では `check-name` の昇順
- 同じ `check-name` 内では `path` の昇順

## Language Notes

- tag と check 名は英語
- 説明・提案・SKILL.md から Daily に出る文面は日本語
- 絵文字付き tag は使わない

## Worked Example

```md
## 🔍 整合性チェック

WARN: 3, ERROR: 1, OK: 3 (checked: 7, mode: full, ran: 21:57)

- ERROR [Broken wikilinks] Wiki/my-topic.md :: `[[Foo#Bar]]` の参照先が解決できません。提案: 対象ノート名または見出し表記を確認してください（提案のみ・auto-fix なし）。
- WARN  [Code-Map repo health] Maps/Code-Map.md :: `https://github.com/owner/repo` は `deleted_or_renamed` と判定されました。提案: private 想定なら注記追加、移転済みなら URL を見直してください（提案のみ・auto-fix なし）。
- WARN  [Structure drift] Inbox/oldsource :: `Inbox/oldsource/` は Inbox 直下の想定外フォルダです（日付ファースト: `Inbox/YYYY-MM-DD/`）。提案: date-first モデルに沿って整理するか、不要なら削除してください（提案のみ・auto-fix なし）。
- WARN  [Today Tasks drift] Daily/2026-06-06.md :: Daily と Google Tasks の状態に 2 件の差分があります。提案: 完了状態とタスク名を見比べて手動で同期してください（提案のみ・auto-fix なし）。
- OK    [Inbox stagnation] Inbox 配下の日付フォルダに 7 日超の滞留はありません。提案: 追加対応は不要です（提案のみ・auto-fix なし）。
```
