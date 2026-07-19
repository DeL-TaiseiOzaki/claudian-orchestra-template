---
name: aggregate-code
description: Read Hermes-staged GitHub EOD capture at Inbox/{YYYY-MM-DD}/code/code.md and aggregate per-repo commits / PRs / issues into today's root Daily note (Daily/{YYYY-MM-DD}.md). Routes by repo to 🏢 Work (Work project repos) / 🔬 Research (Research and other research repos) / 💡 Others (everything else). Append-only with wikilinks back to the source. Use on-demand when github-eod-capture has just landed (typically late evening or after a coding burst); the full per-repo detail stays in Inbox until EOD distill moves digests to {project}/sources/ or logs/.
---

# aggregate-code

## 目的

Hermes が `Inbox/{date}/code/code.md` に capture した today の GitHub 変化（commits / PRs / issues）を、Daily ノートの該当セクションに **per-repo の 1-2 行サマリ** として append する。

> **位置づけ**：`Inbox/{date}/code/code.md` は **Maps/Code-Map.md 由来の全 repo × today** を含む単一 file の per-repo 区切り構成。本スキルはそれを repo ごとに ばらして Daily の Work / Research / Others セクションへ振り分ける。

## 入力

- 走査: `Inbox/{YYYY-MM-DD}/code/code.md`（**単一ファイル**、per-repo セクション分割）
- frontmatter: `source: "github:eod:..."`, `repos: [...]`, `fetched_at`
- 本文: `## {owner}/{repo}` ごとに `### Commits` `### PRs` `### Issues` がある構造

## 出力（Daily 内の挿入先）

| repo の所属 | Daily section |
|---|---|
| Work 案件 repo（`your-org/proj-a-*` 等） | `### 🏢 Work` の該当案件 |
| Research repo（`your-org/your-research` 等） | `### 🔬 Research` |
| Others / Activities repo（Community-A / Community-B / Kaggle 等） | `### 💡 Others / Insights` |
| 個人 vault・dotfiles 系 | `### 💡 Others / Insights` の `[Meta]` prefix |

### Bullet 形式

```markdown
- **[HH:MM] code / {owner}/{repo}** ({N} commits, {M} PRs, {K} issues)
  - 注目 commit: `{sha7}` {message 1 行}
  - PR: #{number} {title} ({state})
  - Source: [[Inbox/{date}/code/code.md#{owner}-{repo}]]
```

## 実行フロー

### Step 1: 当日 Daily 確定
- `Daily/{date}.md` を Read

### Step 2: Inbox code 走査
- `Inbox/{date}/code/code.md` を Read
- per-repo セクション（`## {owner}/{repo}`）をパース

### Step 3: 未集約チェック
- Daily 全文で `[[Inbox/{date}/code/code.md` を Grep
- 既にあれば（直近セッションで処理済）skip。**ただし**新規 repo が増えていたら差分のみ追加（後述）

### Step 4: per-repo 振り分け
- repo 名から所属を推定（Code-Map のラベルが使えれば使う）
- 不明は `### 💡 Others / Insights`

### Step 5: per-repo summary 作成
- commits: 件数 + 注目 commit（一番大きい diff か、明示的決定 message）
- PRs: open + merged の件数 + 注目 PR
- issues: open の件数 + クリティカル issue
- repo ごとに 1-3 bullet に収める

### Step 6: append
- 該当 section の末尾に repo ごとに 1 ブロック挿入
- **既存 bullet・frontmatter は触らない**

## 差分追加（Step 3 の例外）

`Inbox/{date}/code/code.md` は **単一ファイル** で、github-eod-capture を**再実行**すると上書きされ得る。再 aggregate 時：
- 既に Daily にあった repo の wikilink は skip
- 新規 repo（前回の wikilink リストに無いもの）だけ append
- 増分判定は wikilink 文字列の存在チェックで OK

## 並列セッションへの配慮

- code.md は単一 file 単一 wikilink anchor なので並列は基本 1 セッション想定
- それでも append-only 規則を遵守

## 注意

- **本体コードは GitHub が正本**（[[Maps/Code-Map.md]]）。Daily へは要点のみ
- 大きな PR / 設計変更は別途 `Work/{XXX}/code/` や `.claude/docs/knowledges/` へ別ノート（EOD distill / knowledge-capture 経由）
- Research の進捗は submodule 側にも reflect 推奨（[[.claude/rules/research-management.md]]）

## 他 skill との連携

- [[.claude/skills/eod-distill/SKILL.md]]（per-repo digest を `{project}/sources/` ／ logs/ へ配分）
- [[.hermes/skills/vault-capture/github-eod-capture/SKILL.md]]（capture 側）
- [[.claude/skills/knowledge-capture/SKILL.md]]（コードから得た学び）

## 関連

- [[Maps/Code-Map.md]]（repo インデックス）
- [[.claude/rules/inbox-routing.md]] §3 配分表
- [[.claude/rules/work-management.md]]（Work code/ ルール）
