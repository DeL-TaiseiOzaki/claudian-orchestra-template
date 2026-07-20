---
name: vault-archive
description: Propose stale vault content for archival and, after approval, move it to Archive without deleting it. Use for vault cleanup or archiving.
---

# Vault Archive Skill

## 目的

各領域は時間とともに肥大化する。不要・非活性な情報を **Archive/ へ退避**して現役領域を軽く保つ。
**削除ではなく move**（provenance 保持）。判断を伴う構造操作なので **承認前提**で動く（[[.codex/rules/agent-boundaries.md]]）。

> 既定は **dry-run（候補提示のみ）**。実際の move はユーザー承認後にのみ行う。

## 使用場面

- 月次などの定期整理：`Run vault archive` / `アーカイブ候補を出して`
- 特定領域だけ：`Archive old Daily notes` / `Wiki の非活性ノートをアーカイブ`

## 候補検出の基準（scan）

| 領域 | アーカイブ候補 | 既定閾値（調整可） |
|---|---|---|
| 全般 | frontmatter `status: archived` のもの | 即候補 |
| Daily | distill 済みの古い `Daily/{YYYY-MM-DD}.md` | 90 日以上前 |
| Wiki | 破棄アイデア（`status: archived`）、長期放置の `draft`、完了した活動の古い `meetings/` | draft 放置 180 日以上 |
| Inbox | 処理済みの残骸（`status` が `inbox` でなく古い） | 30 日以上前 |
| 長命ドキュメント | 活動 `README.md` 等の**解決済みセクション**（within-file trim） | ユーザー判断 |

閾値は実行時に提示し、ユーザーが変更できる。

## 実行フロー

### Step 1: スキャン（dry-run）

1. `date` で当日を取得（推測しない）
2. 上表の基準で候補を収集
3. 候補を表で提示：`元パス` / `理由` / `最終更新` / `想定退避先`

### Step 2: 承認

- ユーザーに **全件 / 個別選択 / 中止** を確認する。承認なしに move しない。

### Step 3: move（ファイル丸ごと）

1. 退避先 = `Archive/` ＋ **元のトップレベル相対パス**（例 `Wiki/meetings/x.md` → `Archive/Wiki/meetings/x.md`）
2. `git mv` で移動（Git をシリアライザに）
3. frontmatter を更新：`status: archived` ／ `archived: {当日}` ／ `archived_from: "{元パス}"`

### Step 4: リンク保全

1. 移動対象への被リンク（`[[...]]`）を grep
2. 被リンクがあれば、リンクを Archive 先へ更新するか、元の場所に **tombstone**（`> 🗄️ Archived → [[Archive/...]]`）を残す
3. どちらにしたかを報告

### Step 5: within-file trim（任意・解決済みセクション）

- 長命ノート（活動 `README.md` 等）で解決済み・古いセクションを、`Archive/Wiki/{name}-archive.md` に追記し、本体から削る（見出し＋日付で履歴化）。本体には「過去分は Archive へ」のリンクを残す。

### Step 6: 報告

- 退避件数 / 触れた領域 / 残課題（要判断で保留したもの）を 3–5 行で要約

## 安全策

- **削除しない**（move のみ）。誤判定はユーザー承認で止める。
- 既定 dry-run。閾値・対象領域は実行時パラメータ。
- Git 前提（移動はコミットで確定）。Drive 同期と競合しないよう自動コミッタは 1 つ（[[.codex/rules/agent-boundaries.md]]）。

## 定期実行との関係

- **候補のフラグ立て（リマインド）= on-demand リマインド**（Daily `## 🤖 ジョブリスト` に「アーカイブ候補を出す」を載せ、user instructionで実行。低リスク・読み取りのみ。「今月のアーカイブ候補 N 件」を提示）。過渡期は既存 cron による通知も可（新規登録なし）。
- **実際の move / trim = コアエージェントがこの skill を実行 ＋ ユーザー承認**（不可逆寄り＝承認前提）。
- 推奨頻度：月次。

## frontmatter（退避時に付与）

```yaml
status: "archived"
archived: {YYYY-MM-DD}          # 退避した日
archived_from: "Wiki/meetings/2026-01-15-topic.md"   # 元パス
```

## 関連

- [[Archive/README.md]]
- [[.codex/rules/agent-boundaries.md]]（自律度ティア・single-writer）
- [[.codex/rules/vault-metadata.md]]（status: archived / archive 用フィールド）
- [[.codex/rules/wiki-management.md]]（破棄は削除せず archived）
- [[.codex/rules/daily-operations.md]]（distill 後の Daily）
