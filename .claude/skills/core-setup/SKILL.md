---
name: core-setup
description: First-run core-agent selection. Use at 使い始め (GETTING-STARTED Level 1), when the user says 「コアを選びたい」「セットアップ」 on a fresh clone, or when .claude/connections.yaml `core:` is unconfigured. Asks which CLI agent the user runs (Codex / Claude Code / both), records it in the registry, then tailors the repo — codex-only: migrate .claude/ → .agents/ (global link rewrite) and remove Claude-specific files; claude-only: remove .codex/; both: keep everything. Migration is destructive, so it always runs commit-first and with user approval.
---

# core-setup — コアエージェントの選択と初期整形

このテンプレートは **コアエージェント 1 体(Codex 既定 / Claude Code 選択可)+ Hermes** で動く([[AGENTS.md]] §0)。
使い始めに「どの CLI を使うか」を確定し、使わない側の前提ファイルを片付けるのがこの skill。

## Step 1: ヒアリング

1 問だけ聞く:

> 「CLI エージェントは何を使っていますか? — **Codex** / **Claude Code** / **両方**」

- 迷っている人には:機能上どちらでも同じ契約([[AGENTS.md]])で動くこと、後から `core-setup` 再実行で変更できること(git 履歴から復元可能)を伝える
- Hermes の有無はここでは聞かない(それは [[GETTING-STARTED.md]] Level 2 / [[.claude/skills/connection-setup/SKILL.md]] の領分)

## Step 2: registry に記録

[[.claude/connections.yaml]] の `core:` を更新する:

```yaml
core: codex   # codex | claude | both
```

## Step 3: リポジトリの整形(承認必須・commit-first)

> **必ず先に clean な git commit を作ってから実行する**(全操作が `git revert` / checkout で戻せる状態を保証する)。実行前に、消すもの・変わるものの一覧を提示して承認を取る。

### 選択 = `codex`(Codex のみ)

`.claude/` という名前を残さない。**中身(rules / skills / registry / docs)はコア運用に必須なので、削除ではなく `.agents/` へのリネーム移行**を行う:

```bash
# 1) clean commit を確認
git status --short   # 空であること

# 2) 全テキストファイル中のパス参照を書き換え(.md / .yaml / .py / .json / .toml)
grep -rlZ '\.claude/' --include='*.md' --include='*.yaml' --include='*.py' \
  --include='*.json' --include='*.toml' . .gitignore | xargs -0 -r sed -i 's|\.claude/|.agents/|g'

# 3) ディレクトリをリネーム
git mv .claude .agents

# 4) Claude 固有物を削除(--ignore-unmatch:存在しない場合はスキップ)
git rm --ignore-unmatch CLAUDE.md                 # Claude コア用アダプタ
git rm --ignore-unmatch .agents/settings.json     # Claude Code 設定
git rm -r --ignore-unmatch .agents/agents         # Claude subagent 定義
find . -name 'CLAUDE.md' -not -path './.git/*'   # ドメイン配下の契約ファイルは AGENTS 用に有用なので残す(名前は歴史的)

# 5) 検証:リンク切れが無いこと・AGENTS.md が .agents/ を指すこと
grep -rn '\.claude/' --include='*.md' . | head   # 0 件であること

# 6) commit
git add -A && git commit -m "core-setup: codex-only (migrate .claude/ -> .agents/)"
```

- 以後、契約は [[AGENTS.md]](パス書き換え後は `.agents/` を参照)のみ。skills はトリガー時に Codex が `SKILL.md` を読んで従う
- ドメイン直下の `CLAUDE.md`(Work/PROJ_A/CLAUDE.md 等)は**ドメイン契約として残す**(ファイル名は歴史的・内容はコア中立)。気になるなら `AGENTS.md` へのリネームも可(リンク書き換えとセットで)

### 選択 = `claude`(Claude Code のみ)

```bash
git rm -r .codex          # Codex 側設定・vendored skills
# AGENTS.md は削除しない(コア契約本体。CLAUDE.md はここを指すアダプタ)
git add -A && git commit -m "core-setup: claude-only (remove .codex/)"
```

### 選択 = `both`(併用)

- 何も消さない。両 CLI が同じ契約([[AGENTS.md]])と同じ制御プレーン(`.claude/`)を読む
- **同じファイルを同時に触らない**(single-writer)。並行セッションのログは `session-log` skill を使う

## Step 4: 次の案内

1. [[GETTING-STARTED.md]] Level 2(Hermes)→ Level 3(接続)へ誘導
2. 続けて外部接続を選ぶなら [[.claude/skills/connection-setup/SKILL.md]](「接続セットアップして」)

## 再実行(コア変更)

- `core:` を書き換え、Step 3 を該当方向に再実行する。codex-only 移行済み vault で Claude を足す場合は、git 履歴から `CLAUDE.md` / settings / subagent 定義を復元し、必要なら `.agents/` → `.claude/` の逆リネームを行う(同じ手順の逆向き)

## 関連

- [[AGENTS.md]] §0 — コア構成と読み替え規約
- [[.claude/connections.yaml]] — `core:` の記録先
- [[.claude/skills/connection-setup/SKILL.md]] — 続く接続セットアップ
